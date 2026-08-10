"""Failover Scheduler — wait-and-retry when all accounts exhausted (Sprint 7).

Runs as an asyncio Task (started by FailoverEngine._start_wait_and_retry).
Uses asyncio.sleep() only — NEVER time.sleep() (RT-4).

Retry logic:
  - waits until T_reset + buffer (30s) using asyncio.sleep()
  - on each wake-up, calls engine.on_retry_attempt(attempt, account_id)
  - if success → done
  - if fail and attempt < max_retries → sleep 5 more minutes, reschedule
  - if attempt == max_retries → call engine.on_all_retries_failed()
"""
from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .engine import FailoverEngine

from ..usage_service import UsageInfo

logger = logging.getLogger(__name__)

# Tunables
from .. import config as _cfg
FAILOVER_RETRY_INTERVAL_SEC: int = int(getattr(_cfg, "FAILOVER_RETRY_INTERVAL_SEC", 300))  # 5 min
FAILOVER_THRESHOLD_PCT: float = float(getattr(_cfg, "FAILOVER_THRESHOLD_PCT", 98.0))
FAILOVER_RETRY_BUFFER_SEC: int = int(getattr(_cfg, "FAILOVER_RETRY_BUFFER_SEC", 30))


class Scheduler:
    """Handles the wait-and-retry phase when all failover accounts are exhausted."""

    def __init__(self, engine: "FailoverEngine") -> None:
        self._engine = engine

    # ── T_reset computation ───────────────────────────────────────────────────

    def compute_next_reset(
        self, usage_infos: list[UsageInfo], threshold_pct: float = FAILOVER_THRESHOLD_PCT
    ) -> Optional[int]:
        """Return the earliest T_reset (unix seconds) among accounts at or above threshold.

        Only considers accounts without errors.  Returns None when no reset time
        can be determined (fallback: caller should use time.time() + 3600).

        Per TDD §3 Q-TL-4:
          candidates = all (account, window) where pct >= threshold AND reset time known.
          T_reset = min(candidates).
        """
        candidates: list[int] = []
        for info in usage_infos:
            if info.get("error"):
                continue
            for pct_key, reset_key in (
                ("five_hour_pct", "resets_at"),
                ("seven_day_pct", "seven_day_resets_at"),
            ):
                pct = info.get(pct_key)
                reset = info.get(reset_key)
                if pct is not None and pct >= threshold_pct and reset:
                    try:
                        candidates.append(int(reset))
                    except (TypeError, ValueError):
                        pass
        return min(candidates) if candidates else None

    # ── Wait-and-retry loop ───────────────────────────────────────────────────

    async def wait_and_retry_loop(
        self,
        retry_unix: float,
        retry_account_id: Optional[str],
        max_retries: int,
    ) -> None:
        """Async task: sleep until retry_unix, attempt activation, repeat up to max_retries.

        Called by engine._start_wait_and_retry().  Should be created as an asyncio.Task
        and cancelled by engine.on_manual_activation() or on_all_retries_failed().
        """
        if not retry_account_id:
            logger.warning("Scheduler: no retry account — wait_and_retry_loop exiting")
            return

        for attempt in range(1, max_retries + 1):
            # Sleep until retry time (asyncio.sleep — never time.sleep)
            sleep_sec = max(0.0, retry_unix - time.time())
            logger.info(
                "Scheduler: attempt %d/%d — sleeping %.0fs until retry at %.0f",
                attempt, max_retries, sleep_sec, retry_unix,
            )
            try:
                await asyncio.sleep(sleep_sec)
            except asyncio.CancelledError:
                logger.info("Scheduler: cancelled during sleep (attempt %d)", attempt)
                return

            # Attempt activation via engine callback
            try:
                success = await self._engine.on_retry_attempt(attempt, retry_account_id)
            except asyncio.CancelledError:
                logger.info("Scheduler: cancelled during retry attempt %d", attempt)
                return
            except Exception as exc:
                logger.error("Scheduler: on_retry_attempt raised: %s", exc)
                success = False

            if success:
                logger.info(
                    "Scheduler: retry attempt %d succeeded for %s",
                    attempt, retry_account_id,
                )
                return

            # Retry failed — schedule next attempt if not last
            if attempt < max_retries:
                retry_unix = time.time() + FAILOVER_RETRY_INTERVAL_SEC
                logger.info(
                    "Scheduler: attempt %d failed — rescheduling in %ds",
                    attempt, FAILOVER_RETRY_INTERVAL_SEC,
                )
                try:
                    await self._engine.on_retry_rescheduled(
                        attempt, retry_unix, retry_account_id
                    )
                except asyncio.CancelledError:
                    return
            # else: fall through to on_all_retries_failed

        # All retries exhausted
        logger.error(
            "Scheduler: all %d retries exhausted for %s",
            max_retries, retry_account_id,
        )
        try:
            await self._engine.on_all_retries_failed(retry_account_id)
        except asyncio.CancelledError:
            pass
