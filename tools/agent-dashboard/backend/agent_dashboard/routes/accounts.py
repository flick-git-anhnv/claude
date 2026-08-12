"""Account management REST endpoints — CRUD + activate + reveal + OAuth + usage."""
from __future__ import annotations

import asyncio
import time
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query, Request, Response

from ..accounts import mask_key, mask_oauth_token
from ..models import AccountCreate, AccountUpdate, error_response

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


def _store(request: Request):
    return request.app.state.account_store


def _credentials_path(request: Request) -> Path:
    return request.app.state.credentials_path


def _get_refresh_lock(request: Request) -> asyncio.Lock:
    """Return the shared OAuth refresh lock from app state (H-1 fix)."""
    return request.app.state.oauth_refresh_lock


# ── List / Create ─────────────────────────────────────────────────────────────

@router.get("")
def list_accounts(request: Request):
    return _store(request).list_accounts()


@router.post("", status_code=201)
def add_account(request: Request, body: AccountCreate):
    """Create a new account.

    - kind="api_key"  (default): body must include api_key starting with "sk-".
    - kind="oauth_session": imports the current claudeAiOauth snapshot from
      %USERPROFILE%\\.claude\\.credentials.json. No api_key in body.
    """
    try:
        body.validate_for_kind()
    except ValueError as exc:
        raise HTTPException(400, detail=error_response("ACCOUNT_KEY_INVALID", str(exc)))

    store = _store(request)

    if body.kind == "api_key":
        try:
            acc_id = store.add_account(body.name, body.api_key)  # type: ignore[arg-type]
        except ValueError as exc:
            code = str(exc)
            if code.startswith("ACCOUNT_NAME_DUPLICATE"):
                raise HTTPException(409, detail=error_response("ACCOUNT_NAME_DUPLICATE", "Account name already exists"))
            raise HTTPException(400, detail=error_response("ACCOUNT_KEY_INVALID", code))
        acc = store.get_account(acc_id)
        if not acc:
            raise HTTPException(500, detail=error_response("INTERNAL_ERROR", "Account creation failed"))
        return {
            "id": acc["id"],
            "kind": "api_key",
            "name": acc["name"],
            "key_masked": mask_key(acc["api_key"]),
            "is_active": False,
            "created_at": acc["created_at"],
        }

    # kind == "oauth_session": import current credentials from disk
    creds_path = _credentials_path(request)
    if not creds_path.exists():
        raise HTTPException(
            404,
            detail=error_response(
                "CREDENTIALS_FILE_NOT_FOUND",
                "Run 'claude login' first to create a credentials file",
            ),
        )
    try:
        import json
        raw = json.loads(creds_path.read_text(encoding="utf-8"))
        oauth_block = raw.get("claudeAiOauth")
        if not oauth_block:
            raise ValueError("Missing claudeAiOauth block in credentials file")
        acc_id = store.add_oauth_account(body.name, oauth_block, raw.get("organizationUuid"))
    except ValueError as exc:
        code = str(exc)
        if code.startswith("ACCOUNT_NAME_DUPLICATE"):
            raise HTTPException(409, detail=error_response("ACCOUNT_NAME_DUPLICATE", "Account name already exists"))
        raise HTTPException(400, detail=error_response("OAUTH_SNAPSHOT_INVALID", code))
    except Exception as exc:
        raise HTTPException(500, detail=error_response("INTERNAL_ERROR", str(exc)))

    acc = store.get_account(acc_id)
    if not acc:
        raise HTTPException(500, detail=error_response("INTERNAL_ERROR", "Account creation failed"))
    oauth = acc.get("oauth", {})
    return {
        "id": acc["id"],
        "kind": "oauth_session",
        "name": acc["name"],
        "oauth_masked": mask_oauth_token(oauth.get("accessToken", "")),
        "is_active": False,
        "needs_relogin": False,
        "created_at": acc["created_at"],
    }


# ── Usage (Sprint 5 / FR-A) ───────────────────────────────────────────────────
# NOTE: /usage/active MUST be defined before /{acc_id}/usage to avoid FastAPI
# matching the literal string "usage" as acc_id in the parameterised route.

@router.get("/usage/active")
async def get_active_account_usage(
    request: Request,
    force: bool = Query(False, description="Bypass 60-second cache"),
):
    """Return usage quota for the currently active OAuth account.

    Returns 404 when no account is active, or UsageInfo with error field set
    when the active account is an api_key (no Anthropic session quota).
    """
    store = _store(request)
    active = store.get_active()
    if not active:
        raise HTTPException(
            404,
            detail=error_response("NO_ACTIVE_ACCOUNT", "No active account"),
        )
    return await _fetch_usage(store, active["id"], force=force)


@router.get("/{acc_id}/usage")
async def get_account_usage(
    request: Request,
    acc_id: str,
    force: bool = Query(False, description="Bypass 60-second cache"),
):
    """Return usage quota for any stored account (active or not).

    Does NOT swap .credentials.json — reads the stored OAuth token directly.
    Quota is only available for oauth_session accounts; api_key accounts return
    UsageInfo with ``error="api_key"``.
    """
    store = _store(request)
    if not store.get_account(acc_id):
        raise HTTPException(
            404,
            detail=error_response("ACCOUNT_NOT_FOUND", f"Account '{acc_id}' not found"),
        )
    return await _fetch_usage(store, acc_id, force=force)


async def _fetch_usage(store, acc_id: str, *, force: bool) -> dict:
    """Internal helper: resolve access token and call usage_service."""
    from ..usage_service import get_usage

    acc = store.get_account(acc_id)
    if not acc:
        return {"account_id": acc_id, "error": "not_found", "fetched_at": int(time.time())}

    kind = acc.get("kind", "api_key")
    if kind != "oauth_session":
        return {"account_id": acc_id, "error": "api_key", "fetched_at": int(time.time())}

    oauth = acc.get("oauth") or {}
    access_token = oauth.get("accessToken", "")
    if not access_token:
        return {"account_id": acc_id, "error": "no_oauth", "fetched_at": int(time.time())}

    # If token nearly expired (< 60s), inform caller but still attempt the call.
    # A 401 back from Anthropic will be captured in UsageInfo.error.
    return await get_usage(acc_id, access_token, force=force)


# ── Update / Delete ───────────────────────────────────────────────────────────

@router.patch("/{acc_id}")
def update_account(request: Request, acc_id: str, body: AccountUpdate):
    ok = _store(request).update_account(acc_id, body.name)
    if not ok:
        raise HTTPException(
            404,
            detail=error_response("ACCOUNT_NOT_FOUND", f"Account '{acc_id}' not found"),
        )
    return _store(request).list_accounts()


@router.delete("/{acc_id}", status_code=204)
async def delete_account(request: Request, acc_id: str):
    store = _store(request)
    try:
        store.delete_account(acc_id)
    except ValueError:
        raise HTTPException(
            409,
            detail=error_response("ACCOUNT_ACTIVE_CANNOT_DELETE", "Cannot delete the active account"),
        )
    except KeyError:
        raise HTTPException(
            404,
            detail=error_response("ACCOUNT_NOT_FOUND", f"Account '{acc_id}' not found"),
        )
    active = store.get_active()
    _broadcast_account_change(request, active)
    return Response(status_code=204)


# ── Activate ──────────────────────────────────────────────────────────────────

@router.post("/{acc_id}/activate")
async def activate_account(request: Request, acc_id: str):
    """Activate an account.

    - api_key: sets active_id in the encrypted store (no file I/O).
    - oauth_session: additionally swaps .credentials.json to use this account's
      OAuth tokens; re-snapshots the previously active OAuth account first.
    """
    store = _store(request)
    acc = store.get_account(acc_id)
    if not acc:
        raise HTTPException(
            404,
            detail=error_response("ACCOUNT_NOT_FOUND", f"Account '{acc_id}' not found"),
        )

    if acc.get("kind", "api_key") == "api_key":
        try:
            store.activate(acc_id)
        except KeyError:
            raise HTTPException(
                404,
                detail=error_response("ACCOUNT_NOT_FOUND", f"Account '{acc_id}' not found"),
            )
        active = store.get_active()
        _broadcast_account_change(request, active)
        return {"active_id": acc_id, "prev_snapshot_updated": False}

    # oauth_session: credential file swap via oauth_service
    from ..oauth_service import activate_oauth_account

    creds_path = _credentials_path(request)
    lock = _get_refresh_lock(request)
    try:
        result = await activate_oauth_account(acc_id, store, creds_path, lock)
    except FileNotFoundError:
        raise HTTPException(
            404,
            detail=error_response(
                "CREDENTIALS_FILE_NOT_FOUND",
                "Claude credentials file not found — run 'claude login' first",
            ),
        )
    except KeyError:
        raise HTTPException(
            404,
            detail=error_response("ACCOUNT_NOT_FOUND", f"Account '{acc_id}' not found"),
        )
    except ValueError as exc:
        raise HTTPException(400, detail=error_response("OAUTH_SNAPSHOT_INVALID", str(exc)))
    except RuntimeError as exc:
        raise HTTPException(500, detail=error_response("CREDENTIALS_WRITE_FAILED", str(exc)))

    active = store.get_active()
    _broadcast_account_change(request, active)

    # Sprint 7: notify failover engine so it can cancel pending retry scheduler
    engine = getattr(request.app.state, "failover_engine", None)
    if engine is not None:
        try:
            await engine.on_manual_activation(acc_id)
        except Exception as exc:
            import logging
            logging.getLogger(__name__).warning(
                "activate_account: failover engine hook error: %s", exc
            )

    return result


# ── OAuth-specific endpoints ──────────────────────────────────────────────────

@router.post("/{acc_id}/import-current-oauth")
def import_current_oauth(request: Request, acc_id: str):
    """Re-import the current .credentials.json snapshot into an existing OAuth account.

    Useful when the user has re-run 'claude login' and wants to refresh the
    stored snapshot without deleting and re-adding the account.
    """
    store = _store(request)
    acc = store.get_account(acc_id)
    if not acc:
        raise HTTPException(
            404,
            detail=error_response("ACCOUNT_NOT_FOUND", f"Account '{acc_id}' not found"),
        )
    if acc.get("kind") != "oauth_session":
        raise HTTPException(
            400,
            detail=error_response("ACCOUNT_KIND_MISMATCH", "Account is not an OAuth session"),
        )

    creds_path = _credentials_path(request)
    if not creds_path.exists():
        raise HTTPException(
            404,
            detail=error_response(
                "CREDENTIALS_FILE_NOT_FOUND",
                "Run 'claude login' first to create a credentials file",
            ),
        )

    try:
        import json
        raw = json.loads(creds_path.read_text(encoding="utf-8"))
        oauth_block = raw.get("claudeAiOauth")
        if not oauth_block:
            raise ValueError("Missing claudeAiOauth block")
        ok = store.update_oauth_snapshot(acc_id, oauth_block, raw.get("organizationUuid"))
        if not ok:
            raise HTTPException(500, detail=error_response("INTERNAL_ERROR", "Snapshot update failed"))
    except ValueError as exc:
        raise HTTPException(400, detail=error_response("OAUTH_SNAPSHOT_INVALID", str(exc)))

    from datetime import datetime, timezone
    return {"ok": True, "imported_at": datetime.now(timezone.utc).isoformat()}


@router.get("/{acc_id}/oauth-status")
def oauth_status(request: Request, acc_id: str):
    """Return OAuth token status for a single OAuth account."""
    store = _store(request)
    status = store.get_oauth_status(acc_id)
    if status is None:
        acc = store.get_account(acc_id)
        if not acc:
            raise HTTPException(
                404,
                detail=error_response("ACCOUNT_NOT_FOUND", f"Account '{acc_id}' not found"),
            )
        raise HTTPException(
            400,
            detail=error_response("ACCOUNT_KIND_MISMATCH", "Account is not an OAuth session"),
        )
    return status


# ── Reveal (api_key only) ─────────────────────────────────────────────────────

@router.get("/{acc_id}/reveal")
def reveal_key(request: Request, acc_id: str):
    store = _store(request)
    try:
        key = store.reveal_key(acc_id)
    except RuntimeError:
        raise HTTPException(
            429,
            detail=error_response("RATE_LIMIT_EXCEEDED", "Reveal rate limit: 5 times per minute"),
        )
    except ValueError as exc:
        raise HTTPException(
            400,
            detail=error_response("REVEAL_NOT_SUPPORTED_FOR_OAUTH", str(exc)),
        )
    except KeyError:
        raise HTTPException(
            404,
            detail=error_response("ACCOUNT_NOT_FOUND", f"Account '{acc_id}' not found"),
        )
    return {"api_key": key}


# ── Internal helper ───────────────────────────────────────────────────────────

def _broadcast_account_change(request: Request, active: dict | None) -> None:
    """Fire-and-forget WebSocket broadcast for account changes."""
    import asyncio
    from ..models import make_delta

    ws_manager = getattr(request.app.state, "ws_manager", None)
    if ws_manager is None:
        return

    payload = make_delta(
        "account_changed",
        {
            "active_id": active["id"] if active else None,
            "name": active["name"] if active else None,
            "kind": active["kind"] if active else None,
            "key_masked": active.get("key_masked") if active and active.get("kind") == "api_key" else None,
            "oauth_masked": active.get("oauth_masked") if active and active.get("kind") == "oauth_session" else None,
        },
    )

    try:
        loop = asyncio.get_running_loop()
        loop.create_task(ws_manager.broadcast(payload))
    except RuntimeError:
        try:
            # Running in a worker thread (non-async route context)
            asyncio.run(ws_manager.broadcast(payload))
        except Exception:
            pass
