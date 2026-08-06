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


def test_initialize_from_db_recent_sessions_keep_correct_state():
    """Sessions with recent activity are evaluated correctly from last_event_at."""
    sm = SessionStateManager(idle_threshold=300, ended_threshold=1800)
    now = datetime.now(timezone.utc)

    # 1-minute-old → Running
    running_ts = (now - timedelta(minutes=1)).isoformat()
    # 10-minute-old → Idle (> 300 s, < 1800 s)
    idle_ts = (now - timedelta(minutes=10)).isoformat()

    changes = sm.initialize_from_db(
        [
            {"session_id": "s_running", "state": "Running", "last_event_at": running_ts},
            {"session_id": "s_idle",    "state": "Running", "last_event_at": idle_ts},
        ],
        idle_threshold=300,
        ended_threshold=1800,
    )

    assert sm.get_state("s_running") == "Running"
    assert sm.get_state("s_idle")    == "Idle"

    # s_running stored as "Running" → matches → no change emitted
    # s_idle stored as "Running" but re-evaluated to "Idle" → change emitted
    change_ids = {c.session_id: c.new_state for c in changes}
    assert "s_running" not in change_ids
    assert change_ids["s_idle"] == "Idle"


def test_initialize_from_db_stale_running_becomes_ended():
    """Sessions stored as Running with last_event_at hours ago must be re-evaluated to Ended."""
    sm = SessionStateManager(idle_threshold=300, ended_threshold=1800)
    now = datetime.now(timezone.utc)

    stale_ts = (now - timedelta(hours=5)).isoformat()   # 18 000 s >> ended(1800 s)

    changes = sm.initialize_from_db(
        [{"session_id": "stale", "state": "Running", "last_event_at": stale_ts}],
        idle_threshold=300,
        ended_threshold=1800,
    )

    assert sm.get_state("stale") == "Ended"
    assert len(changes) == 1
    assert changes[0].old_state == "Running"
    assert changes[0].new_state == "Ended"


def test_initialize_from_db_returns_no_changes_when_states_already_correct():
    """No StateChange emitted when stored state already matches re-evaluated state."""
    sm = SessionStateManager(idle_threshold=300, ended_threshold=1800)
    now = datetime.now(timezone.utc)

    recent_ts = (now - timedelta(seconds=30)).isoformat()

    changes = sm.initialize_from_db(
        [{"session_id": "fresh", "state": "Running", "last_event_at": recent_ts}],
        idle_threshold=300,
        ended_threshold=1800,
    )

    assert sm.get_state("fresh") == "Running"
    assert changes == []


def test_initialize_from_db_multiple_stale_sessions_all_corrected():
    """Multiple stale sessions (hundreds of hours old) all become Ended, not Running."""
    sm = SessionStateManager(idle_threshold=300, ended_threshold=1800)
    now = datetime.now(timezone.utc)

    rows = [
        {"session_id": f"old_{i}", "state": "Running",
         "last_event_at": (now - timedelta(hours=200 + i)).isoformat()}
        for i in range(5)
    ]

    changes = sm.initialize_from_db(rows, idle_threshold=300, ended_threshold=1800)

    for i in range(5):
        assert sm.get_state(f"old_{i}") == "Ended", f"old_{i} should be Ended"

    assert len(changes) == 5
    assert all(c.new_state == "Ended" for c in changes)


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
