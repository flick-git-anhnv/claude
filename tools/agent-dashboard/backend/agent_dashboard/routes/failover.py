"""Failover REST endpoints (Sprint 7).

Endpoints:
  GET  /api/failover/status          — engine state + active account + retry info
  GET  /api/failover/log             — paginated failover event log with date filter
  GET  /api/failover/chain           — ordered failover chain with live status
  PUT  /api/failover/chain           — reorder / include/exclude accounts
  POST /api/failover/cancel-retry    — cancel pending wait-and-retry scheduler
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from ..models import error_response

router = APIRouter(prefix="/api/failover", tags=["failover"])


def _engine(request: Request):
    """Return the FailoverEngine from app state (injected at startup)."""
    engine = getattr(request.app.state, "failover_engine", None)
    if engine is None:
        raise HTTPException(503, detail=error_response("ENGINE_NOT_READY", "Failover engine not started"))
    return engine


def _store(request: Request):
    return request.app.state.account_store


def _db(request: Request):
    return request.app.state.db


# ── GET /api/failover/status ──────────────────────────────────────────────────

@router.get("/status")
async def get_failover_status(request: Request):
    """Return current failover engine state and 24-hour event count."""
    from .. import db as db_module

    engine = _engine(request)
    status = engine.get_status()

    # Fill count_24h from DB
    try:
        status["count_24h"] = await db_module.count_24h(_db(request))
    except Exception:
        status["count_24h"] = 0

    return status


# ── GET /api/failover/log ─────────────────────────────────────────────────────

@router.get("/log")
async def get_failover_log(
    request: Request,
    from_dt: Optional[str] = Query(None, alias="from", description="ISO 8601 start datetime"),
    to_dt: Optional[str] = Query(None, alias="to", description="ISO 8601 end datetime"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """Return paginated failover event log.

    Optional date range filter via ``from`` and ``to`` query params (ISO 8601).
    Returns ``{items, total, count_24h}``.
    """
    from .. import db as db_module

    # Validate date params
    if from_dt:
        try:
            _validate_iso_dt(from_dt)
        except ValueError:
            raise HTTPException(400, detail=error_response("INVALID_DATE", f"'from' is not a valid ISO date: {from_dt}"))
    if to_dt:
        try:
            _validate_iso_dt(to_dt)
        except ValueError:
            raise HTTPException(400, detail=error_response("INVALID_DATE", f"'to' is not a valid ISO date: {to_dt}"))

    try:
        result = await db_module.list_failover_events(
            _db(request),
            from_dt=from_dt,
            to_dt=to_dt,
            limit=limit,
            offset=offset,
        )
    except Exception as exc:
        raise HTTPException(500, detail=error_response("DB_ERROR", str(exc)))

    return result


# ── GET /api/failover/chain ───────────────────────────────────────────────────

@router.get("/chain")
async def get_failover_chain(request: Request):
    """Return all OAuth accounts with failover chain status.

    Each item includes live status: active/standby/exhausted/needs_relogin.
    Uses cached usage data (no fresh API call here).
    """
    from ..usage_service import get_usage

    store = _store(request)
    active_id = store._data.get("active_id")
    accounts = store._data.get("accounts", [])

    items = []
    for acc in accounts:
        if acc.get("kind") != "oauth_session":
            continue

        acc_id = acc["id"]
        priority = acc.get("priority", 999)
        include_in_chain = acc.get("include_in_chain", True)
        needs_relogin = acc.get("needs_relogin", False)

        # Determine status
        if needs_relogin:
            status = "needs_relogin"
        elif acc_id == active_id:
            status = "active"
        elif not include_in_chain:
            status = "standby"  # disabled from chain — treat as standby
        else:
            status = "standby"

        # Get usage if possible (from cache — no extra API calls)
        five_hour_pct: Optional[float] = None
        seven_day_pct: Optional[float] = None
        resets_at: Optional[int] = None
        oauth = acc.get("oauth") or {}
        access_token = oauth.get("accessToken", "")
        if access_token and not needs_relogin:
            try:
                info = await get_usage(acc_id, access_token, force=False)
                if not info.get("error"):
                    five_hour_pct = info.get("five_hour_pct")
                    seven_day_pct = info.get("seven_day_pct")
                    resets_at = info.get("resets_at")

                    # If usage is near/above threshold and it's a standby, mark exhausted
                    from ..failover.detector import FAILOVER_THRESHOLD_PCT
                    if (
                        status == "standby"
                        and (
                            (five_hour_pct is not None and five_hour_pct >= FAILOVER_THRESHOLD_PCT)
                            or (seven_day_pct is not None and seven_day_pct >= FAILOVER_THRESHOLD_PCT)
                        )
                    ):
                        status = "exhausted"
            except Exception:
                pass

        items.append({
            "acc_id": acc_id,
            "name": acc.get("name", ""),
            "priority": priority,
            "include_in_chain": include_in_chain,
            "status": status,
            "five_hour_pct": five_hour_pct,
            "seven_day_pct": seven_day_pct,
            "resets_at": resets_at,
        })

    # Sort by priority
    items.sort(key=lambda x: x["priority"])
    return items


# ── PUT /api/failover/chain ───────────────────────────────────────────────────

class ChainItem(BaseModel):
    acc_id: str
    priority: int
    include_in_chain: bool


class PutChainBody(BaseModel):
    items: List[ChainItem]


@router.put("/chain")
async def update_failover_chain(request: Request, body: PutChainBody):
    """Reorder and include/exclude accounts in the failover chain.

    Validates:
      - All acc_ids must exist in the store
      - Priorities must be unique
      - At least one account must remain included
    """
    store = _store(request)

    if not body.items:
        raise HTTPException(400, detail=error_response("EMPTY_CHAIN", "Chain items cannot be empty"))

    # Validate acc_ids exist
    for item in body.items:
        if not store.get_account(item.acc_id):
            raise HTTPException(
                400,
                detail=error_response("UNKNOWN_ACCOUNT", f"Account '{item.acc_id}' not found"),
            )

    # Validate priorities unique
    priorities = [item.priority for item in body.items]
    if len(set(priorities)) != len(priorities):
        raise HTTPException(
            400,
            detail=error_response("DUPLICATE_PRIORITY", "Priority values must be unique"),
        )

    # Validate at least 1 included
    included_count = sum(1 for item in body.items if item.include_in_chain)
    if included_count == 0:
        raise HTTPException(
            400,
            detail=error_response(
                "CHAIN_MUST_HAVE_ONE_INCLUDED",
                "At least one account must be included in the failover chain",
            ),
        )

    # Apply updates
    for item in body.items:
        try:
            store.set_priority(item.acc_id, item.priority)
        except ValueError as exc:
            raise HTTPException(400, detail=error_response("INVALID_PRIORITY", str(exc)))
        try:
            store.set_include_in_chain(item.acc_id, item.include_in_chain)
        except ValueError as exc:
            raise HTTPException(400, detail=error_response("CHAIN_CONSTRAINT", str(exc)))

    return {"ok": True}


# ── POST /api/failover/cancel-retry ──────────────────────────────────────────

@router.post("/cancel-retry")
async def cancel_retry(request: Request):
    """Cancel any pending wait-and-retry scheduler task.

    Returns ``{"ok": true, "cancelled": bool}`` where ``cancelled`` is True only
    if there was an active retry task that was cancelled.
    """
    engine = _engine(request)
    was_waiting = engine._state in ("waiting", "retrying")

    if was_waiting and engine._scheduler_task and not engine._scheduler_task.done():
        engine._scheduler_task.cancel()
        engine._scheduler_task = None
        engine._state = "idle"
        engine._retry_attempt = 0
        engine._retry_account_id = None
        engine._retry_at = None
        return {"ok": True, "cancelled": True}

    return {"ok": True, "cancelled": False}


# ── Internal helpers ──────────────────────────────────────────────────────────

def _validate_iso_dt(value: str) -> None:
    """Raise ValueError if value is not a plausible ISO 8601 datetime string."""
    from datetime import datetime
    # Try standard ISO formats
    for fmt in (
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%d",
    ):
        try:
            datetime.strptime(value[:len(fmt)], fmt)
            return
        except ValueError:
            pass
    raise ValueError(f"Not a valid ISO date: {value}")
