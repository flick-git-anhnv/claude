"""Unit tests for state_manager.py — Running / Idle / Ended transitions."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from agent_dashboard.state_manager import SessionStateManager, _parse_ts


# ── _parse_ts ─────────────────────────────────────────────────────────────────

def test_parse_ts_with_z():
    dt = _parse_ts("2026-08-05T10:00:00Z")
    assert dt.tzinfo is not None
    assert dt.year == 2026


def test_parse_ts_with_microseconds():
    dt = _parse_ts("2026-08-05T10:00:00.123456Z")
    assert dt.microsecond == 123456


def test_parse_ts_empty_returns_now():
    dt = _parse_ts("")
    diff = abs((datetime.now(timezone.utc) - dt).total_seconds())
    assert diff < 5


# ── SessionStateManager ───────────────────────────────────────────────────────

def test_new_session_starts_as_running():
    sm = SessionStateManager()
    change = sm.update_activity("s1", "2026-08-05T10:00:00Z")
    assert change is not None
    assert change.new_state == "Running"
    assert sm.get_state("s1") == "Running"


def test_activity_on_running_session_no_state_change():
    sm = SessionStateManager()
    sm.update_activity("s1", "2026-08-05T10:00:00Z")
    change = sm.update_activity("s1", "2026-08-05T10:00:01Z")
    # Still Running, no change event
    assert change is None
    assert sm.get_state("s1") == "Running"


def test_transition_to_idle():
    # idle=300s (5min), ended=1800s (30min); activity was 6min=360s ago → Idle, not Ended
    sm = SessionStateManager(idle_threshold=300, ended_threshold=1800)
    ts = (datetime.now(timezone.utc) - timedelta(minutes=6)).isoformat()
    sm.update_activity("s1", ts)

    changes = sm.evaluate_all(idle_threshold=300, ended_threshold=1800)
    assert any(c.session_id == "s1" and c.new_state == "Idle" for c in changes)
    assert sm.get_state("s1") == "Idle"


def test_transition_to_ended():
    # activity 31 min = 1860s ago → > ended_threshold(1800s)
    sm = SessionStateManager(idle_threshold=300, ended_threshold=1800)
    ts = (datetime.now(timezone.utc) - timedelta(minutes=31)).isoformat()
    sm.update_activity("s1", ts)

    changes = sm.evaluate_all(idle_threshold=300, ended_threshold=1800)
    assert any(c.session_id == "s1" and c.new_state == "Ended" for c in changes)
    assert sm.get_state("s1") == "Ended"


def test_ended_session_not_re_evaluated():
    sm = SessionStateManager(idle_threshold=300, ended_threshold=1800)
    ts = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    sm.update_activity("s1", ts)
    sm.evaluate_all(idle_threshold=300, ended_threshold=1800)
    assert sm.get_state("s1") == "Ended"

    # Evaluate again — should not emit another change
    changes = sm.evaluate_all(idle_threshold=300, ended_threshold=1800)
    assert not any(c.session_id == "s1" for c in changes)


def test_activity_resets_idle_to_running():
    # 10min = 600s > idle(300s) but < ended(1800s) → Idle
    sm = SessionStateManager(idle_threshold=300, ended_threshold=1800)
    old_ts = (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
    sm.update_activity("s1", old_ts)
    sm.evaluate_all(idle_threshold=300, ended_threshold=1800)
    assert sm.get_state("s1") == "Idle"

    # New event arrives → back to Running
    change = sm.update_activity("s1", datetime.now(timezone.utc).isoformat())
    assert change is not None
    assert change.new_state == "Running"
    assert sm.get_state("s1") == "Running"


def test_initialize_from_db():
    sm = SessionStateManager()
    sm.initialize_from_db([
        {"session_id": "s1", "state": "Idle",
         "last_event_at": "2026-08-05T09:00:00Z"},
        {"session_id": "s2", "state": "Running",
         "last_event_at": "2026-08-05T10:00:00Z"},
    ])
    assert sm.get_state("s1") == "Idle"
    assert sm.get_state("s2") == "Running"


def test_multiple_sessions_evaluate_independently():
    # idle=300s, ended=1800s
    # active: now → Running (no change)
    # idle_s: 10min=600s ago → Idle
    # ended_s: 1h=3600s ago → Ended
    sm = SessionStateManager(idle_threshold=300, ended_threshold=1800)
    now = datetime.now(timezone.utc)

    sm.update_activity("active", now.isoformat())
    sm.update_activity("idle_s", (now - timedelta(minutes=10)).isoformat())
    sm.update_activity("ended_s", (now - timedelta(hours=1)).isoformat())

    changes = sm.evaluate_all(idle_threshold=300, ended_threshold=1800)
    states = {c.session_id: c.new_state for c in changes}

    assert states.get("active") is None  # no change
    assert states["idle_s"] == "Idle"
    assert states["ended_s"] == "Ended"
    assert sm.get_state("active") == "Running"
