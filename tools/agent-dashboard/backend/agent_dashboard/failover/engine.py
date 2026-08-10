"""FailoverEngine — central state machine for auto-failover (Sprint 7).

States: idle → detecting → swapping → idle (success)
                        ↘ waiting → retrying → idle (retry success/fail)
        idle → detecting → idle (api_wide_suspected, backoff 5 min)

Key invariants:
  - failover_action_lock prevents concurrent swaps / detecting→swapping races.
  - activate_oauth_account() is called DIRECTLY (not _do_swap_and_invoke) to
    avoid blocking the event loop on the 30-second subprocess.
  - Never uses time.sleep() — asyncio.sleep() only (RT-4).
  - chain_snapshot_json is built via db.failover.serialize_chain_snapshot()
    which whitelists safe fields only (RT-6, BR9).
  - Max 3 retry attempts before declaring wait_and_retry_failed (BR18).
  - Manual activation cancels any pending scheduler task (on_manual_activation).
"""
from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..db import failover as db_failover
from .detector import Detector
from .models import ChainSnapshot, FailoverEvent, FailoverResult, FailoverState, TriggerReason
from .scheduler import Scheduler

logger = logging.getLogger(__name__)

# ── Tunables ──────────────────────────────────────────────────────────────────

from .. import config as _cfg

FAILOVER_API_WIDE_BACKOFF_SEC: int = int(
    getattr(_cfg, "FAILOVER_API_WIDE_BACKOFF_SEC", 300)
)
FAILOVER_MAX_RETRIES: int = int(getattr(_cfg, "FAILOVER_MAX_RETRIES", 3))
FAILOVER_RETRY_BUFFER_SEC: int = int(getattr(_cfg, "FAILOVER_RETRY_BUFFER_SEC", 30))
FAILOVER_THRESHOLD_PCT: float = float(getattr(_cfg, "FAILOVER_THRESHOLD_PCT", 98.0))

# Consecutive swap-fail threshold before forcing wait-and-retry (RT-2)
_SWAP_FAIL_STREAK_THRESHOLD = 3


def _now_iso() -> str:
    """Current UTC time as ISO 8601 with milliseconds and +00:00 offset."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "+00:00"


class FailoverEngine:
    """Coordinates failover detection, account swapping, and wait-and-retry scheduling."""

    def __init__(
        self,
        account_store: Any,
        credentials_path: Path,
        refresh_lock: asyncio.Lock,
        db_conn: Any,
        ws_manager: Any,
    ) -> None:
        self._store = account_store
        self._credentials_path = credentials_path
        self._refresh_lock = refresh_lock
        self._db = db_conn
        self._ws = ws_manager

        # State machine
        self._state: FailoverState = "idle"

        # Lock protecting all state transitions
        self._failover_action_lock = asyncio.Lock()

        # Detector (Channel A + B)
        self._detector = Detector(on_trigger=self._maybe_trigger_failover)

        # Scheduler (wait-and-retry)
        self._scheduler = Scheduler(engine=self)

        # Background tasks (started in start())
        self._poll_task: Optional[asyncio.Task] = None
        self._scheduler_task: Optional[asyncio.Task] = None

        # Consecutive swap-fail streak counter (RT-2 infinite loop guard)
        self._swap_fail_streak: int = 0

        # API-wide backoff end time
        self._api_wide_backoff_until: float = 0.0

        # Current retry attempt counter (0 = not in retry cycle)
        self._retry_attempt: int = 0

        # Account earmarked for the next retry
        self._retry_account_id: Optional[str] = None
        self._retry_at: Optional[float] = None  # unix seconds

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    async def start(self) -> None:
        """Start background tasks.  Call from app lifespan startup."""
        self._poll_task = asyncio.create_task(
            self._detector.usage_poll_loop(self._store),
            name="failover_poll",
        )
        logger.info("FailoverEngine started")

    async def stop(self) -> None:
        """Cancel all background tasks.  Call from app lifespan shutdown."""
        if self._poll_task and not self._poll_task.done():
            self._poll_task.cancel()
            try:
                await self._poll_task
            except asyncio.CancelledError:
                pass

        if self._scheduler_task and not self._scheduler_task.done():
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass

        logger.info("FailoverEngine stopped")

    # ── Public: JSONL hook ────────────────────────────────────────────────────

    async def on_jsonl_rate_limit_signal(
        self, account_id: Optional[str] = None
    ) -> None:
        """Called from watcher when JSONL transcript contains a rate-limit signal."""
        await self._detector.jsonl_rate_limit_signal(account_id)

    # ── Public: manual activation hook ───────────────────────────────────────

    async def on_manual_activation(self, acc_id: str) -> None:
        """Called after a manual account activation via POST /api/accounts/{id}/activate.

        Cancels any pending retry scheduler task and logs/broadcasts
        retry_cancelled_by_manual event if in waiting/retrying state.
        """
        async with self._failover_action_lock:
            was_waiting = self._state in ("waiting", "retrying")
            old_retry_account = self._retry_account_id

            # Cancel scheduler task
            if self._scheduler_task and not self._scheduler_task.done():
                self._scheduler_task.cancel()
                self._scheduler_task = None
                logger.info("FailoverEngine: scheduler task cancelled by manual activation")

            self._state = "idle"
            self._retry_attempt = 0
            self._retry_account_id = None
            self._retry_at = None
            self._swap_fail_streak = 0

            if was_waiting:
                await self._log_event(
                    trigger_reason="manual_override",
                    result="retry_cancelled_by_manual",
                    from_account_id=old_retry_account,
                    to_account_id=acc_id,
                    to_account_name=self._account_name(acc_id),
                )
                await self._broadcast({
                    "type": "retry_cancelled_by_manual",
                    "activated": {
                        "id": acc_id,
                        "name": self._account_name(acc_id),
                    },
                })

    # ── Core: trigger entry point ─────────────────────────────────────────────

    async def _maybe_trigger_failover(
        self, reason: str, account_id: Optional[str]
    ) -> None:
        """Called by Detector when a failover trigger condition is detected.

        This is the ONLY entry point for failover decisions — both channels
        funnel through here to avoid parallel swap logic.
        """
        # Quick check outside lock to avoid unnecessary locking
        if self._state not in ("idle", "detecting"):
            logger.debug(
                "FailoverEngine: trigger %s ignored (state=%s)", reason, self._state
            )
            return

        async with self._failover_action_lock:
            if self._state not in ("idle", "detecting"):
                return

            self._state = "detecting"
            logger.info(
                "FailoverEngine: trigger received reason=%s account=%s",
                reason, account_id,
            )

            try:
                if reason == "api_wide_suspected":
                    await self._handle_api_wide_suspected(account_id)
                else:
                    await self._handle_normal_trigger(reason, account_id)
            except Exception as exc:
                logger.exception("FailoverEngine: unhandled error in trigger: %s", exc)
                self._state = "idle"

    async def _handle_api_wide_suspected(self, account_id: Optional[str]) -> None:
        """API-wide outage suspected — do NOT swap, backoff and log."""
        backoff_until = time.time() + FAILOVER_API_WIDE_BACKOFF_SEC
        self._api_wide_backoff_until = backoff_until
        self._detector.pause_until(backoff_until)
        self._state = "idle"

        backoff_iso = datetime.fromtimestamp(backoff_until, tz=timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.000+00:00"
        )

        await self._log_event(
            trigger_reason="api_wide_suspected",
            result="api_wide_suspected",
            from_account_id=account_id,
            from_account_name=self._account_name(account_id) if account_id else None,
            error_message="API-wide outage suspected: 2+ accounts with 429 in 60s window",
        )
        await self._broadcast({
            "type": "failover_paused",
            "reason": "api_wide_suspected",
            "backoff_until": backoff_iso,
        })
        logger.warning(
            "FailoverEngine: api_wide_suspected — pausing failover for %ds",
            FAILOVER_API_WIDE_BACKOFF_SEC,
        )

        # Schedule resume after backoff (using asyncio.sleep — no time.sleep)
        asyncio.create_task(
            self._resume_after_backoff(FAILOVER_API_WIDE_BACKOFF_SEC),
            name="failover_api_backoff_resume",
        )

    async def _resume_after_backoff(self, seconds: int) -> None:
        await asyncio.sleep(seconds)
        self._detector.resume()
        logger.info("FailoverEngine: api-wide backoff expired, detector resumed")

    async def _handle_normal_trigger(self, reason: str, account_id: Optional[str]) -> None:
        """Normal (single-account) trigger — try to find next account and swap."""
        active_id = self._store._data.get("active_id")

        # Only act if the triggered account is the currently active account
        # (or we don't know which account triggered — treat as active)
        if account_id and account_id != active_id:
            logger.debug(
                "FailoverEngine: trigger for non-active account %s (active=%s) — ignoring",
                account_id, active_id,
            )
            self._state = "idle"
            return

        # RT-2 guard: if swap failures streaking ≥ threshold, force wait-and-retry
        if self._swap_fail_streak >= _SWAP_FAIL_STREAK_THRESHOLD:
            logger.warning(
                "FailoverEngine: %d consecutive swap failures — forcing wait-and-retry",
                self._swap_fail_streak,
            )
            self._swap_fail_streak = 0
            await self._start_wait_and_retry(reason)
            return

        # Get candidate accounts (sorted by priority, excluding active)
        chain = self._store.get_failover_chain()
        candidates = [a for a in chain if a["id"] != active_id]

        if not candidates:
            logger.warning("FailoverEngine: no candidate accounts — starting wait-and-retry")
            await self._start_wait_and_retry(reason)
            return

        # Find first candidate with quota < threshold
        next_acc = await self._find_viable_candidate(candidates)

        if next_acc is None:
            logger.warning(
                "FailoverEngine: all %d candidates exhausted — starting wait-and-retry",
                len(candidates),
            )
            await self._start_wait_and_retry(reason)
            return

        # Perform swap
        await self._do_swap(reason, active_id, next_acc)

    async def _find_viable_candidate(self, candidates: list) -> Optional[Dict[str, Any]]:
        """Return first candidate with quota < threshold, or None if all are full.

        Checks usage for each candidate in priority order.  Stops at first viable one.
        Uses the stored OAuth token without swapping credentials.
        """
        from ..usage_service import get_usage
        threshold = FAILOVER_THRESHOLD_PCT

        for acc in candidates:
            oauth = acc.get("oauth") or {}
            access_token = oauth.get("accessToken", "")
            if not access_token:
                continue
            try:
                info = await get_usage(acc["id"], access_token, force=False)
            except Exception:
                continue
            if info.get("error"):
                continue
            five_pct = info.get("five_hour_pct") or 0.0
            seven_pct = info.get("seven_day_pct") or 0.0
            if five_pct < threshold and seven_pct < threshold:
                return acc
        return None

    async def _do_swap(
        self, reason: str, from_acc_id: Optional[str], to_acc: Dict[str, Any]
    ) -> None:
        """Execute the credential swap by calling activate_oauth_account directly."""
        from ..oauth_service import activate_oauth_account

        self._state = "swapping"
        to_acc_id = to_acc["id"]
        to_acc_name = to_acc.get("name", "")
        from_acc_name = self._account_name(from_acc_id) if from_acc_id else None

        chain_snapshot = self._build_chain_snapshot()

        await self._broadcast({
            "type": "failover_started",
            "from": {"id": from_acc_id, "name": from_acc_name},
            "to": {"id": to_acc_id, "name": to_acc_name},
            "reason": reason,
            "at": _now_iso(),
        })

        t_start = time.monotonic()
        failover_id = uuid.uuid4().hex
        try:
            await activate_oauth_account(
                to_acc_id,
                self._store,
                self._credentials_path,
                self._refresh_lock,
            )
            latency_ms = int((time.monotonic() - t_start) * 1000)
            self._swap_fail_streak = 0
            self._state = "idle"

            await self._log_event(
                failover_id=failover_id,
                trigger_reason=reason,
                result="success",
                from_account_id=from_acc_id,
                from_account_name=from_acc_name,
                to_account_id=to_acc_id,
                to_account_name=to_acc_name,
                swap_latency_ms=latency_ms,
                chain_snapshot_json=db_failover.serialize_chain_snapshot(chain_snapshot),
            )
            await self._broadcast({
                "type": "failover_completed",
                "failover_id": failover_id,
                "to": {"id": to_acc_id, "name": to_acc_name},
                "swap_latency_ms": latency_ms,
            })
            logger.info(
                "FailoverEngine: swap SUCCESS %s → %s (%dms)",
                from_acc_id, to_acc_id, latency_ms,
            )

        except Exception as exc:
            self._swap_fail_streak += 1
            self._state = "idle"
            error_msg = str(exc)[:500]
            logger.error(
                "FailoverEngine: swap FAILED (%s → %s): %s",
                from_acc_id, to_acc_id, error_msg,
            )
            await self._log_event(
                failover_id=failover_id,
                trigger_reason=reason,
                result="swap_failed",
                from_account_id=from_acc_id,
                from_account_name=from_acc_name,
                to_account_id=to_acc_id,
                to_account_name=to_acc_name,
                error_message=error_msg,
                chain_snapshot_json=db_failover.serialize_chain_snapshot(chain_snapshot),
            )
            await self._broadcast({
                "type": "failover_failed",
                "failover_id": failover_id,
                "reason": error_msg,
            })

    # ── Wait-and-retry ────────────────────────────────────────────────────────

    async def _start_wait_and_retry(self, reason: str) -> None:
        """Chain exhausted — schedule a retry when quota resets."""
        self._state = "waiting"
        self._swap_fail_streak = 0

        # Pick the first included account as retry target (highest priority)
        chain = self._store.get_failover_chain()
        retry_acc = chain[0] if chain else None
        self._retry_account_id = retry_acc["id"] if retry_acc else None

        # Compute T_reset from all chain accounts' usage info
        from ..usage_service import get_usage
        usage_infos = []
        for acc in chain:
            oauth = acc.get("oauth") or {}
            token = oauth.get("accessToken", "")
            if token:
                try:
                    info = await get_usage(acc["id"], token, force=False)
                    usage_infos.append(info)
                except Exception:
                    pass

        t_reset = self._scheduler.compute_next_reset(usage_infos)
        if t_reset is None:
            # Fallback: 1 hour from now
            t_reset = int(time.time()) + 3600
            logger.warning("FailoverEngine: could not compute T_reset, using +1h fallback")

        retry_unix = t_reset + FAILOVER_RETRY_BUFFER_SEC
        self._retry_at = float(retry_unix)
        retry_iso = datetime.fromtimestamp(retry_unix, tz=timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.000+00:00"
        )

        chain_snapshot = self._build_chain_snapshot()
        await self._log_event(
            trigger_reason=reason,
            result="wait_and_retry_scheduled",
            from_account_id=self._store._data.get("active_id"),
            next_retry_at=retry_iso,
            chain_snapshot_json=db_failover.serialize_chain_snapshot(chain_snapshot),
        )
        await self._broadcast({
            "type": "all_accounts_exhausted",
            "next_retry_at": retry_iso,
            "retry_account": {
                "id": self._retry_account_id,
                "name": retry_acc["name"] if retry_acc else None,
            },
            "retry_attempt": self._retry_attempt + 1,
            "max_retries": FAILOVER_MAX_RETRIES,
        })

        # Start the scheduler task
        if self._scheduler_task and not self._scheduler_task.done():
            self._scheduler_task.cancel()

        self._scheduler_task = asyncio.create_task(
            self._scheduler.wait_and_retry_loop(
                retry_unix=retry_unix,
                retry_account_id=self._retry_account_id,
                max_retries=FAILOVER_MAX_RETRIES,
            ),
            name="failover_scheduler",
        )

    # ── Retry hooks (called back from Scheduler) ──────────────────────────────

    async def on_retry_attempt(self, attempt: int, retry_account_id: str) -> bool:
        """Try to activate retry_account_id.  Returns True on success."""
        async with self._failover_action_lock:
            if self._state not in ("waiting", "retrying"):
                return False

            self._state = "retrying"
            self._retry_attempt = attempt
            logger.info(
                "FailoverEngine: retry attempt %d/%d for %s",
                attempt, FAILOVER_MAX_RETRIES, retry_account_id,
            )

            from ..oauth_service import activate_oauth_account
            try:
                await activate_oauth_account(
                    retry_account_id,
                    self._store,
                    self._credentials_path,
                    self._refresh_lock,
                )
                self._state = "idle"
                self._retry_attempt = 0
                self._retry_account_id = None
                self._retry_at = None
                self._swap_fail_streak = 0

                await self._log_event(
                    trigger_reason="manual_override",
                    result="wait_and_retry_success",
                    to_account_id=retry_account_id,
                    to_account_name=self._account_name(retry_account_id),
                    retry_attempt=attempt,
                )
                await self._broadcast({
                    "type": "retry_success",
                    "account": {
                        "id": retry_account_id,
                        "name": self._account_name(retry_account_id),
                    },
                })
                return True

            except Exception as exc:
                logger.error(
                    "FailoverEngine: retry attempt %d failed for %s: %s",
                    attempt, retry_account_id, exc,
                )
                self._state = "waiting"  # back to waiting for next attempt
                return False

    async def on_all_retries_failed(self, retry_account_id: str) -> None:
        """Called by scheduler when max retries exhausted without success."""
        async with self._failover_action_lock:
            self._state = "idle"
            self._retry_attempt = 0
            self._scheduler_task = None

            await self._log_event(
                trigger_reason="manual_override",
                result="wait_and_retry_failed",
                to_account_id=retry_account_id,
                retry_attempt=FAILOVER_MAX_RETRIES,
                error_message=f"All {FAILOVER_MAX_RETRIES} retry attempts exhausted",
            )
            await self._broadcast({
                "type": "failover_failed",
                "failover_id": "",
                "reason": f"wait_and_retry_failed: all {FAILOVER_MAX_RETRIES} retries exhausted",
            })
            logger.error(
                "FailoverEngine: all %d retries exhausted for %s — manual intervention required",
                FAILOVER_MAX_RETRIES, retry_account_id,
            )

    async def on_retry_rescheduled(
        self, attempt: int, next_retry_unix: float, retry_account_id: str
    ) -> None:
        """Called by scheduler when a retry failed and another retry is scheduled."""
        self._retry_at = next_retry_unix
        next_retry_iso = datetime.fromtimestamp(next_retry_unix, tz=timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%S.000+00:00"
        )
        await self._broadcast({
            "type": "all_accounts_exhausted",
            "next_retry_at": next_retry_iso,
            "retry_account": {
                "id": retry_account_id,
                "name": self._account_name(retry_account_id),
            },
            "retry_attempt": attempt + 1,
            "max_retries": FAILOVER_MAX_RETRIES,
        })

    # ── Status snapshot (for /api/failover/status) ────────────────────────────

    def get_status(self) -> Dict[str, Any]:
        """Return current engine status for the REST status endpoint."""
        from .. import db as db_module  # avoid circular at import time
        active_id = self._store._data.get("active_id")
        active_acc = self._store.get_account(active_id) if active_id else None
        retry_acc = (
            self._store.get_account(self._retry_account_id)
            if self._retry_account_id
            else None
        )
        api_wide_backoff_iso: Optional[str] = None
        if self._api_wide_backoff_until > time.time():
            api_wide_backoff_iso = datetime.fromtimestamp(
                self._api_wide_backoff_until, tz=timezone.utc
            ).strftime("%Y-%m-%dT%H:%M:%S.000+00:00")

        retry_at_iso: Optional[str] = None
        if self._retry_at:
            retry_at_iso = datetime.fromtimestamp(
                self._retry_at, tz=timezone.utc
            ).strftime("%Y-%m-%dT%H:%M:%S.000+00:00")

        return {
            "state": self._state,
            "active_account": (
                {"id": active_id, "name": active_acc["name"]}
                if active_id and active_acc
                else None
            ),
            "next_retry_at": retry_at_iso,
            "retry_account": (
                {"id": self._retry_account_id, "name": retry_acc["name"]}
                if retry_acc
                else None
            ),
            "retry_attempt": self._retry_attempt,
            "max_retries": FAILOVER_MAX_RETRIES,
            "count_24h": 0,  # filled by route handler via db query
            "api_wide_backoff_until": api_wide_backoff_iso,
        }

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _account_name(self, acc_id: Optional[str]) -> Optional[str]:
        if not acc_id:
            return None
        acc = self._store.get_account(acc_id)
        return acc["name"] if acc else None

    def _build_chain_snapshot(self) -> List[Dict[str, Any]]:
        """Build a safe chain snapshot list for DB serialization.

        Only whitelisted fields (no credentials).  pct values will be
        None at this point — engine doesn't hold live usage info but the
        chain structure + priority is captured.
        """
        chain = self._store.get_failover_chain()
        snapshots = []
        for acc in chain:
            snapshots.append({
                "id": acc["id"],
                "name": acc.get("name", ""),
                "priority": acc.get("priority", 999),
                "include_in_chain": acc.get("include_in_chain", True),
                "five_hour_pct": None,
                "seven_day_pct": None,
            })
        return snapshots

    async def _log_event(
        self,
        *,
        trigger_reason: str,
        result: str,
        failover_id: Optional[str] = None,
        from_account_id: Optional[str] = None,
        from_account_name: Optional[str] = None,
        to_account_id: Optional[str] = None,
        to_account_name: Optional[str] = None,
        swap_latency_ms: Optional[int] = None,
        next_retry_at: Optional[str] = None,
        retry_attempt: Optional[int] = None,
        error_message: Optional[str] = None,
        chain_snapshot_json: Optional[str] = None,
    ) -> None:
        """Persist a failover event to the DB.  Silently logs errors."""
        fid = failover_id or uuid.uuid4().hex
        try:
            await db_failover.insert_failover_event(
                self._db,
                failover_id=fid,
                occurred_at=_now_iso(),
                from_account_id=from_account_id,
                from_account_name=from_account_name,
                to_account_id=to_account_id,
                to_account_name=to_account_name,
                trigger_reason=trigger_reason,
                result=result,
                swap_latency_ms=swap_latency_ms,
                next_retry_at=next_retry_at,
                retry_attempt=retry_attempt,
                error_message=error_message,
                chain_snapshot_json=chain_snapshot_json,
            )
        except Exception as exc:
            logger.error("FailoverEngine: failed to log event to DB: %s", exc)

    async def _broadcast(self, payload: Dict[str, Any]) -> None:
        """Fan-out a WebSocket message to all connected clients."""
        if self._ws is None:
            return
        try:
            await self._ws.broadcast(payload)
        except Exception as exc:
            logger.debug("FailoverEngine: WS broadcast error: %s", exc)
