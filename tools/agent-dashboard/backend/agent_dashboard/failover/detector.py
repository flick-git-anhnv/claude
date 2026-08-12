"""Failover detector — Channel A (usage poll) + Channel B (JSONL signal hook).

Channel A: usage_poll_loop() polls usage_service every 15 s for all OAuth accounts
           in the failover chain.  Triggers on quota >= threshold or http_429.

Channel B: jsonl_rate_limit_signal() is called by the JSONL watcher when it detects
           a rate-limit signal in a parsed transcript line.  Opportunistic — not
           guaranteed to fire for every 429 (depends on CLI transcript format).

Both channels call the same engine callback ``on_trigger(reason, account_id)`` to
avoid two parallel swap-decision paths.

Anti-patterns avoided:
  - NEVER use time.sleep() — asyncio.sleep() only (RT-4)
  - Dedup 30s: same (account_id, trigger_reason) pair fires at most once per window
  - Distinct 429 check: recent_429_events deque over 60s window for api-wide detection
"""
from __future__ import annotations

import asyncio
import collections
import logging
import time
from typing import Any, Callable, Coroutine, Deque, Optional, Tuple

from .. import config as _cfg
from ..usage_service import get_usage

logger = logging.getLogger(__name__)

# ── Tunables (can override via env or engine constructor kwargs) ───────────────

FAILOVER_USAGE_POLL_SEC: int = int(getattr(_cfg, "FAILOVER_USAGE_POLL_SEC", 15))
FAILOVER_THRESHOLD_PCT: float = float(getattr(_cfg, "FAILOVER_THRESHOLD_PCT", 98.0))
FAILOVER_DEDUP_SEC: int = int(getattr(_cfg, "FAILOVER_DEDUP_SEC", 30))
FAILOVER_API_WIDE_DISTINCT_THRESHOLD: int = int(
    getattr(_cfg, "FAILOVER_API_WIDE_DISTINCT_THRESHOLD", 2)
)
FAILOVER_API_WIDE_WINDOW_SEC: int = int(
    getattr(_cfg, "FAILOVER_API_WIDE_WINDOW_SEC", 60)
)

# ── Type alias ────────────────────────────────────────────────────────────────

OnTriggerCallback = Callable[[str, Optional[str]], Coroutine[Any, Any, None]]
# on_trigger(reason: TriggerReason, account_id: str | None) -> coroutine


class Detector:
    """Runs usage polling and processes JSONL rate-limit signals.

    Instantiated once by FailoverEngine; engine passes its own ``on_trigger``
    coroutine as the callback so the two components stay decoupled.
    """

    def __init__(
        self,
        on_trigger: OnTriggerCallback,
        *,
        poll_sec: int = FAILOVER_USAGE_POLL_SEC,
        threshold_pct: float = FAILOVER_THRESHOLD_PCT,
        dedup_sec: int = FAILOVER_DEDUP_SEC,
        api_wide_distinct: int = FAILOVER_API_WIDE_DISTINCT_THRESHOLD,
        api_wide_window_sec: int = FAILOVER_API_WIDE_WINDOW_SEC,
    ) -> None:
        self._on_trigger = on_trigger
        self._poll_sec = poll_sec
        self._threshold_pct = threshold_pct
        self._dedup_sec = dedup_sec
        self._api_wide_distinct = api_wide_distinct
        self._api_wide_window_sec = api_wide_window_sec

        # dedup: {(account_id, reason): last_trigger_unix}
        self._dedup: dict[Tuple[str, str], float] = {}

        # recent_429_events: deque of (account_id, timestamp) for api-wide detection
        self._recent_429: Deque[Tuple[str, float]] = collections.deque()

        # Callback for engine to pause the detector (e.g. during api-wide backoff)
        self._paused_until: float = 0.0

        # Reference to account store + credentials path (injected by engine start())
        self._account_store: Any = None

    # ── Pause / resume ────────────────────────────────────────────────────────

    def pause_until(self, unix_ts: float) -> None:
        """Suppress trigger signals until unix_ts (api-wide backoff)."""
        self._paused_until = unix_ts
        logger.info(
            "Detector paused until %.0f (api-wide backoff, %.0f s)",
            unix_ts,
            unix_ts - time.time(),
        )

    def resume(self) -> None:
        self._paused_until = 0.0
        logger.info("Detector resumed")

    @property
    def is_paused(self) -> bool:
        return time.time() < self._paused_until

    # ── Dedup ─────────────────────────────────────────────────────────────────

    def _should_dedup(self, account_id: str, reason: str) -> bool:
        """Return True if this (account_id, reason) was triggered within dedup window."""
        key = (account_id, reason)
        last = self._dedup.get(key)
        if last and (time.time() - last) < self._dedup_sec:
            return True
        self._dedup[key] = time.time()
        return False

    # ── Distinct-429 api-wide check ───────────────────────────────────────────

    def _record_429(self, account_id: str) -> int:
        """Record a 429-type event and return distinct account count in the window."""
        now = time.time()
        self._recent_429.append((account_id, now))
        # Prune old entries
        cutoff = now - self._api_wide_window_sec
        while self._recent_429 and self._recent_429[0][1] < cutoff:
            self._recent_429.popleft()
        distinct = len({acc for acc, _ in self._recent_429})
        return distinct

    # ── Channel A: usage poll loop ────────────────────────────────────────────

    async def usage_poll_loop(self, account_store: Any) -> None:
        """Background coroutine — polls usage every poll_sec for ALL included accounts.

        Must be started as an asyncio Task and cancelled on shutdown.
        Uses asyncio.sleep() only — never time.sleep().
        """
        self._account_store = account_store
        logger.info(
            "Detector: usage_poll_loop started (interval=%ds, threshold=%.1f%%)",
            self._poll_sec,
            self._threshold_pct,
        )
        while True:
            try:
                await asyncio.sleep(self._poll_sec)
                if self.is_paused:
                    logger.debug("Detector: paused, skipping poll cycle")
                    continue
                await self._poll_once(account_store)
            except asyncio.CancelledError:
                logger.info("Detector: usage_poll_loop cancelled")
                break
            except Exception as exc:
                logger.exception("Detector: usage_poll_loop error: %s", exc)

    async def _poll_once(self, account_store: Any) -> None:
        """One poll cycle across all included OAuth accounts."""
        chain = account_store.get_failover_chain()
        active_id = account_store._data.get("active_id")

        # Also poll the active account if it's OAuth (it may not be in get_failover_chain
        # filtered list if it has needs_relogin, but we still want to detect its quota)
        all_poll_ids = {a["id"] for a in chain}
        if active_id:
            active_acc = account_store.get_account(active_id)
            if active_acc and active_acc.get("kind") == "oauth_session":
                all_poll_ids.add(active_id)

        for acc_id in all_poll_ids:
            acc = account_store.get_account(acc_id)
            if not acc:
                continue
            oauth = acc.get("oauth") or {}
            access_token = oauth.get("accessToken", "")
            if not access_token:
                continue

            try:
                info = await get_usage(acc_id, access_token, force=False)
            except Exception as exc:
                logger.warning("Detector: get_usage(%s) raised: %s", acc_id, exc)
                continue

            error = info.get("error")
            if error == "http_429":
                await self._on_429(acc_id, "http_429")
                continue

            if error:
                logger.debug("Detector: usage error for %s: %s", acc_id, error)
                continue

            five_pct = info.get("five_hour_pct")
            seven_pct = info.get("seven_day_pct")

            if five_pct is not None and five_pct >= self._threshold_pct:
                await self._on_quota_threshold(acc_id, "quota_5h_full")
            elif seven_pct is not None and seven_pct >= self._threshold_pct:
                await self._on_quota_threshold(acc_id, "quota_7d_full")

    async def _on_429(self, account_id: str, reason: str) -> None:
        """Handle a 429 signal from the usage endpoint."""
        if self._should_dedup(account_id, reason):
            logger.debug("Detector: dedup suppressed %s for %s", reason, account_id)
            return

        distinct = self._record_429(account_id)
        logger.info(
            "Detector: 429 detected for %s (distinct in window: %d/%d)",
            account_id,
            distinct,
            self._api_wide_distinct,
        )

        if distinct >= self._api_wide_distinct:
            # Possibly api-wide — let engine decide
            await self._on_trigger("api_wide_suspected", account_id)
        else:
            await self._on_trigger(reason, account_id)

    async def _on_quota_threshold(self, account_id: str, reason: str) -> None:
        """Handle a quota threshold breach."""
        if self._should_dedup(account_id, reason):
            logger.debug("Detector: dedup suppressed %s for %s", reason, account_id)
            return
        logger.info("Detector: quota threshold (%s) for %s", reason, account_id)
        # Quota depletion of ONE account only counts as 1 distinct 429 for api-wide logic
        self._record_429(account_id)
        await self._on_trigger(reason, account_id)

    # ── Channel B: JSONL signal hook ──────────────────────────────────────────

    async def jsonl_rate_limit_signal(self, account_id: Optional[str] = None) -> None:
        """Called from JSONL watcher when a rate-limit signal is detected in transcript.

        This is an opportunistic early-trigger — not guaranteed for every 429.
        Uses force=True for the next usage poll to get fresh quota info.

        Channel B signals dedupe against Channel A using the same dedup dict.
        """
        if self.is_paused:
            return

        reason = "jsonl_rate_limit"
        # Use the active account as signal source when account_id unknown
        check_id = account_id or (
            self._account_store._data.get("active_id")
            if self._account_store
            else None
        )
        if not check_id:
            return

        if self._should_dedup(check_id, reason):
            logger.debug("Detector: JSONL signal dedup suppressed for %s", check_id)
            return

        logger.info("Detector: JSONL rate-limit signal for %s (channel B)", check_id)
        distinct = self._record_429(check_id)

        if distinct >= self._api_wide_distinct:
            await self._on_trigger("api_wide_suspected", check_id)
        else:
            await self._on_trigger(reason, check_id)
