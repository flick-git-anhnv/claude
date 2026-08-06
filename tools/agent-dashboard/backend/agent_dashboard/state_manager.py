"""Session state machine — Running / Idle / Ended.

Thresholds (from config, not hardcoded):
  Running  : last event ≤ IDLE_THRESHOLD_SEC ago
  Idle     : last event > IDLE_THRESHOLD_SEC and ≤ ENDED_THRESHOLD_SEC ago
  Ended    : last event > ENDED_THRESHOLD_SEC ago
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional

from .models import SessionInfo, StateChange

logger = logging.getLogger(__name__)

_ISO_FMT = "%Y-%m-%dT%H:%M:%S.%f"  # with microseconds
_ISO_FMT_SHORT = "%Y-%m-%dT%H:%M:%S"  # without microseconds


def _parse_ts(ts_str: str) -> datetime:
    """Parse ISO-8601 string → timezone-aware datetime (UTC)."""
    if not ts_str:
        return datetime.now(timezone.utc)
    # Strip trailing 'Z' and try both formats
    s = ts_str.rstrip("Z").split("+")[0]
    for fmt in (_ISO_FMT, _ISO_FMT_SHORT):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    # Fallback: best-effort with fromisoformat (Python 3.11+)
    try:
        return datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except ValueError:
        logger.debug("Cannot parse timestamp '%s', using now", ts_str)
        return datetime.now(timezone.utc)


class SessionStateManager:
    """In-memory state machine; survives restart via DB-seeded initialization."""

    def __init__(self, idle_threshold: int = 0, ended_threshold: int = 0) -> None:
        """
        idle_threshold / ended_threshold override config values (used in tests).
        Pass 0 to use values from config at call time.
        """
        self._idle_override = idle_threshold
        self._ended_override = ended_threshold
        self._sessions: Dict[str, SessionInfo] = {}

    # ── Initialization ────────────────────────────────────────────────────────

    def initialize_from_db(
        self,
        sessions: list[dict],
        idle_threshold: Optional[int] = None,
        ended_threshold: Optional[int] = None,
    ) -> List[StateChange]:
        """Seed in-memory state from DB rows at startup.

        Re-evaluates each session's state based on ``last_event_at`` vs current
        time instead of blindly restoring the stored state.  This prevents stale
        "Running" sessions (that have been idle for hours/days) from appearing
        active after a backend restart.

        Returns a list of StateChange objects for every session whose computed
        state differs from the stored state — callers should persist these
        corrections to the DB immediately so both layers are consistent before
        the first periodic ticker fires.
        """
        from . import config  # late import avoids circular at module level

        idle_sec = idle_threshold if idle_threshold is not None else (
            self._idle_override or config.IDLE_THRESHOLD_SEC
        )
        ended_sec = ended_threshold if ended_threshold is not None else (
            self._ended_override or config.ENDED_THRESHOLD_SEC
        )

        now = datetime.now(timezone.utc)
        changes: List[StateChange] = []

        for row in sessions:
            sid = row["session_id"]
            last_event_ts = _parse_ts(row.get("last_event_at", ""))
            stored_state = row.get("state", "Running")

            # Re-evaluate based on elapsed time — never trust the stored state
            elapsed = (now - last_event_ts).total_seconds()
            if elapsed > ended_sec:
                new_state = "Ended"
            elif elapsed > idle_sec:
                new_state = "Idle"
            else:
                new_state = "Running"

            self._sessions[sid] = SessionInfo(
                session_id=sid,
                state=new_state,
                last_event_at=last_event_ts,
            )

            if new_state != stored_state:
                changes.append(
                    StateChange(
                        session_id=sid,
                        old_state=stored_state,
                        new_state=new_state,
                        changed_at=now.isoformat(),
                    )
                )

        return changes

    # ── Activity update ───────────────────────────────────────────────────────

    def update_activity(self, session_id: str, timestamp_str: str) -> Optional[StateChange]:
        """
        Called each time a new parsed line arrives for a session.
        Returns a StateChange if the state actually changed, else None.
        """
        ts = _parse_ts(timestamp_str)

        if session_id not in self._sessions:
            self._sessions[session_id] = SessionInfo(
                session_id=session_id,
                state="Running",
                last_event_at=ts,
            )
            return StateChange(
                session_id=session_id,
                old_state="",
                new_state="Running",
                changed_at=timestamp_str,
            )

        session = self._sessions[session_id]
        session.last_event_at = ts

        if session.state != "Running":
            old = session.state
            session.state = "Running"
            return StateChange(
                session_id=session_id,
                old_state=old,
                new_state="Running",
                changed_at=timestamp_str,
            )
        return None

    def get_state(self, session_id: str) -> str:
        s = self._sessions.get(session_id)
        return s.state if s else "Unknown"

    # ── Periodic evaluation ───────────────────────────────────────────────────

    def evaluate_all(
        self,
        idle_threshold: Optional[int] = None,
        ended_threshold: Optional[int] = None,
    ) -> List[StateChange]:
        """
        Evaluate every active session; return list of state transitions.
        Called by the asyncio ticker every STATE_TICKER_INTERVAL_SEC seconds.
        """
        from . import config  # late import avoids circular at module level

        idle_sec = idle_threshold or self._idle_override or config.IDLE_THRESHOLD_SEC
        ended_sec = ended_threshold or self._ended_override or config.ENDED_THRESHOLD_SEC

        now = datetime.now(timezone.utc)
        changes: List[StateChange] = []

        for session_id, session in self._sessions.items():
            if session.state == "Ended":
                continue

            elapsed = (now - session.last_event_at).total_seconds()
            changed_at = now.isoformat()

            if elapsed > ended_sec:
                old = session.state
                session.state = "Ended"
                changes.append(StateChange(session_id, old, "Ended", changed_at))
            elif elapsed > idle_sec and session.state == "Running":
                session.state = "Idle"
                changes.append(StateChange(session_id, "Running", "Idle", changed_at))

        return changes
