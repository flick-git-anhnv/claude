"""Sprint 4 tests — parser Sprint 4 fields, DB migration, roster token join."""
from __future__ import annotations

import json
import pathlib

import pytest
import pytest_asyncio
import aiosqlite

from agent_dashboard import db as db_module
from agent_dashboard.parser import parse_line


# ── Async DB fixture (in-memory SQLite, all migrations) ──────────────────────

@pytest_asyncio.fixture
async def conn():
    c = await aiosqlite.connect(":memory:")
    c.row_factory = aiosqlite.Row
    await c.executescript(db_module._SCHEMA_SQL)
    await c.commit()
    await db_module._migrate_subagent_columns(c)
    await db_module._migrate_sprint3_columns(c)
    await db_module._migrate_events_subagent_columns(c)
    await db_module._migrate_subagent_flag_column(c)
    await db_module._migrate_sprint4_columns(c)
    await db_module._migrate_result_columns(c)
    yield c
    await c.close()


# ── Helpers ────────────────────────────────────────────────────────────────────

def _user_line(ts: str = "2026-08-06T10:00:00.000Z") -> str:
    return json.dumps({
        "type": "user",
        "timestamp": ts,
        "isSidechain": True,
        "attributionAgent": "senior-developer",
        "message": {"role": "user", "content": [{"type": "text", "text": "hello"}]},
    }) + "\n"


def _assistant_line(ts: str, attribution: str = "senior-developer") -> str:
    return json.dumps({
        "type": "assistant",
        "timestamp": ts,
        "isSidechain": True,
        "attributionAgent": attribution,
        "message": {
            "role": "assistant",
            "model": "claude-sonnet-4-6",
            "content": [{"type": "text", "text": "done"}],
            "usage": {
                "input_tokens": 1000,
                "output_tokens": 200,
                "cache_creation_input_tokens": 500,
                "cache_read_input_tokens": 300,
            },
        },
    }) + "\n"


# ── Parser: Sprint 4 fields ───────────────────────────────────────────────────

def test_parser_extracts_parent_session_id():
    """Subagent file → parent_session_id = folder above 'subagents/'."""
    path = str(
        pathlib.Path("proj-abc") / "session-parent-uuid" / "subagents" / "agent-xyz.jsonl"
    )
    result = parse_line(_user_line(), path)
    assert result is not None
    assert result.parent_session_id == "session-parent-uuid"


def test_parser_extracts_attribution_agent_from_assistant():
    """attributionAgent field extracted from assistant JSONL line."""
    path = str(
        pathlib.Path("proj-abc") / "session-001" / "subagents" / "agent-xyz.jsonl"
    )
    result = parse_line(_assistant_line("2026-08-06T10:01:00Z", "tech-lead"), path)
    assert result is not None
    assert result.attribution_agent == "tech-lead"


def test_parser_attribution_agent_none_for_main_session():
    """Non-subagent file → attribution_agent is None."""
    path = str(pathlib.Path("proj-abc") / "session-001.jsonl")
    result = parse_line(_user_line(), path)
    assert result is not None
    assert result.attribution_agent is None
    assert result.parent_session_id is None


def test_parser_user_line_attribution_may_be_none():
    """User lines in subagent transcripts may not have attributionAgent set."""
    line = json.dumps({
        "type": "user",
        "timestamp": "2026-08-06T10:00:00Z",
        "isSidechain": True,
        "message": {"role": "user", "content": [{"type": "text", "text": "hello"}]},
    }) + "\n"
    path = str(pathlib.Path("proj") / "sess" / "subagents" / "agent-001.jsonl")
    result = parse_line(line, path)
    assert result is not None
    assert result.attribution_agent is None  # not set in this line
    assert result.parent_session_id == "sess"


# ── DB migration: Sprint 4 columns ───────────────────────────────────────────

@pytest.mark.asyncio
async def test_sprint4_columns_exist(conn):
    async with conn.execute("PRAGMA table_info(sessions)") as cur:
        rows = await cur.fetchall()
    col_names = {r["name"] for r in rows}
    assert "parent_session_id" in col_names
    assert "attribution_agent" in col_names


@pytest.mark.asyncio
async def test_sprint4_migration_idempotent(conn):
    await db_module._migrate_sprint4_columns(conn)  # second call must not raise
    async with conn.execute("PRAGMA table_info(sessions)") as cur:
        rows = await cur.fetchall()
    assert "parent_session_id" in {r["name"] for r in rows}


@pytest.mark.asyncio
async def test_sprint4_index_exists(conn):
    async with conn.execute("SELECT name FROM sqlite_master WHERE type='index'") as cur:
        rows = await cur.fetchall()
    index_names = {r["name"] for r in rows}
    assert "idx_sessions_parent_id" in index_names


# ── upsert_session: stores Sprint 4 fields ───────────────────────────────────

@pytest.mark.asyncio
async def test_upsert_stores_parent_session_id(conn):
    await db_module.upsert_session(
        conn, "agent-abc", "proj", "/proj/parent-uuid/subagents/agent-abc.jsonl",
        "claude-sonnet-4-6", "2026-08-06T10:00:00Z", 100, 20, 0, 0,
        is_subagent=True,
        parent_session_id="parent-uuid",
        attribution_agent="senior-developer",
    )
    async with conn.execute(
        "SELECT parent_session_id, attribution_agent FROM sessions WHERE session_id = 'agent-abc'"
    ) as cur:
        row = await cur.fetchone()
    assert row["parent_session_id"] == "parent-uuid"
    assert row["attribution_agent"] == "senior-developer"


@pytest.mark.asyncio
async def test_upsert_parent_fields_null_for_main_session(conn):
    await db_module.upsert_session(
        conn, "sess-main", "proj", "/proj/sess-main.jsonl",
        None, "2026-08-06T10:00:00Z", 0, 0, 0, 0,
    )
    async with conn.execute(
        "SELECT parent_session_id, attribution_agent FROM sessions WHERE session_id = 'sess-main'"
    ) as cur:
        row = await cur.fetchone()
    assert row["parent_session_id"] is None
    assert row["attribution_agent"] is None


# ── get_session_chain: roster structure ──────────────────────────────────────

async def _seed_parent(conn, session_id: str = "parent-sess", state: str = "Running") -> str:
    await conn.execute(
        """INSERT INTO sessions
             (session_id, project, file_path, started_at, last_event_at, state)
           VALUES (?, 'proj', 'p', '2026-08-06T10:00:00Z', '2026-08-06T11:00:00Z', ?)""",
        (session_id, state),
    )
    await conn.commit()
    return session_id


async def _add_agent_event(conn, session_id: str, ts: str,
                           subagent_type: str, description: str,
                           result_summary: str | None = None,
                           result_full: str | None = None) -> None:
    await conn.execute(
        """INSERT INTO events (session_id, ts, type, tool_name, subagent_type, subagent_description,
                               payload_json, result_summary, result_full)
           VALUES (?, ?, 'tool_use', 'Agent', ?, ?, '{}', ?, ?)""",
        (session_id, ts, subagent_type, description, result_summary, result_full),
    )
    await conn.commit()


async def _add_child_session(conn, session_id: str, parent_id: str, attribution: str,
                              model: str, state: str, ts: str,
                              inp: int = 0, out: int = 0, cc: int = 0, cr: int = 0) -> None:
    await db_module.upsert_session(
        conn, session_id, "proj",
        f"/proj/{parent_id}/subagents/{session_id}.jsonl",
        model, ts, inp, out, cc, cr,
        is_subagent=True,
        parent_session_id=parent_id,
        attribution_agent=attribution,
    )
    if state != "Running":
        await db_module.update_session_state(conn, session_id, state,
                                              ts if state == "Ended" else None)


@pytest.mark.asyncio
async def test_roster_basic_structure(conn):
    """Two different roles → two roster entries."""
    sid = await _seed_parent(conn, "p-basic")
    await _add_agent_event(conn, sid, "2026-08-06T10:01:00Z", "product-manager", "Viết PRD")
    await _add_agent_event(conn, sid, "2026-08-06T10:05:00Z", "tech-lead", "TDD")
    await _add_child_session(conn, "c-pm", sid, "product-manager", "claude-sonnet-4-6",
                              "Ended", "2026-08-06T10:01:00Z", 500, 100, 0, 0)
    await _add_child_session(conn, "c-tl", sid, "tech-lead", "claude-opus-4-7",
                              "Running", "2026-08-06T10:05:00Z", 2000, 400, 100, 50)

    result = await db_module.get_session_chain(conn, sid)
    assert result is not None
    assert result["session_id"] == sid
    assert result["session_state"] == "Running"
    roster = result["roster"]
    assert len(roster) == 2
    roles = [r["role"] for r in roster]
    assert roles == ["product-manager", "tech-lead"]


@pytest.mark.asyncio
async def test_roster_tokens_populated(conn):
    """tokens_step are populated from child session cumulative totals."""
    sid = await _seed_parent(conn, "p-tokens")
    await _add_agent_event(conn, sid, "2026-08-06T10:01:00Z", "senior-developer", "Code backend")
    await _add_child_session(conn, "c-sd", sid, "senior-developer", "claude-sonnet-4-6",
                              "Ended", "2026-08-06T10:01:00Z", 1000, 200, 300, 50)

    result = await db_module.get_session_chain(conn, sid)
    entry = result["roster"][0]
    assert entry["role"] == "senior-developer"
    assert entry["total_tokens"]["input"] == 1000
    assert entry["total_tokens"]["output"] == 200
    assert entry["total_tokens"]["cache_creation"] == 300
    assert entry["total_tokens"]["cache_read"] == 50
    assert entry["latest_model"] == "claude-sonnet-4-6"


@pytest.mark.asyncio
async def test_roster_tokens_null_when_no_child(conn):
    """Step with no matching child session → history entry tokens=None."""
    sid = await _seed_parent(conn, "p-null-tok")
    await _add_agent_event(conn, sid, "2026-08-06T10:01:00Z", "qa-engineer", "Test")
    # No child session seeded

    result = await db_module.get_session_chain(conn, sid)
    entry = result["roster"][0]
    assert entry["role"] == "qa-engineer"
    assert entry["total_tokens"] == {"input": 0, "output": 0, "cache_creation": 0, "cache_read": 0}
    assert entry["history"][0]["tokens"] is None


@pytest.mark.asyncio
async def test_roster_multiple_calls_same_role_accumulated(conn):
    """Same role called twice → one roster entry, call_count=2, total_tokens summed."""
    sid = await _seed_parent(conn, "p-multi")
    await _add_agent_event(conn, sid, "2026-08-06T10:01:00Z", "tech-lead", "TDD")
    await _add_agent_event(conn, sid, "2026-08-06T10:10:00Z", "tech-lead", "Code review")
    # Two child sessions for tech-lead
    await _add_child_session(conn, "c-tl-1", sid, "tech-lead", "claude-opus-4-7",
                              "Ended", "2026-08-06T10:01:00Z", 1000, 200, 0, 0)
    await _add_child_session(conn, "c-tl-2", sid, "tech-lead", "claude-opus-4-7",
                              "Ended", "2026-08-06T10:10:00Z", 2000, 400, 0, 0)

    result = await db_module.get_session_chain(conn, sid)
    assert len(result["roster"]) == 1  # one entry despite two calls
    entry = result["roster"][0]
    assert entry["call_count"] == 2
    assert len(entry["history"]) == 2
    assert entry["total_tokens"]["input"] == 3000   # 1000 + 2000 accumulated
    assert entry["total_tokens"]["output"] == 600   # 200 + 400 accumulated


@pytest.mark.asyncio
async def test_roster_mixed_roles_with_repeat(conn):
    """TL → SD → TL pattern → TL appears once in roster with call_count=2, history=[2]."""
    sid = await _seed_parent(conn, "p-mixed")
    await _add_agent_event(conn, sid, "2026-08-06T10:01:00Z", "tech-lead", "Design")
    await _add_agent_event(conn, sid, "2026-08-06T10:05:00Z", "senior-developer", "Code")
    await _add_agent_event(conn, sid, "2026-08-06T10:10:00Z", "tech-lead", "Review")
    await _add_child_session(conn, "c-tl-a", sid, "tech-lead", "claude-opus-4-7",
                              "Ended", "2026-08-06T10:01:00Z", 500, 100, 0, 0)
    await _add_child_session(conn, "c-sd-a", sid, "senior-developer", "claude-sonnet-4-6",
                              "Ended", "2026-08-06T10:05:00Z", 800, 150, 0, 0)
    await _add_child_session(conn, "c-tl-b", sid, "tech-lead", "claude-opus-4-7",
                              "Ended", "2026-08-06T10:10:00Z", 600, 120, 0, 0)

    result = await db_module.get_session_chain(conn, sid)
    roles = [r["role"] for r in result["roster"]]
    assert roles == ["tech-lead", "senior-developer"]  # ordered by FIRST appearance
    tl_entry = next(r for r in result["roster"] if r["role"] == "tech-lead")
    assert tl_entry["call_count"] == 2
    assert len(tl_entry["history"]) == 2
    assert tl_entry["total_tokens"]["input"] == 1100  # 500 + 600
    assert tl_entry["history"][0]["tokens"]["input"] == 500
    assert tl_entry["history"][1]["tokens"]["input"] == 600


@pytest.mark.asyncio
async def test_roster_status_active_when_last_child_running(conn):
    """latest call of a role has Running child → status='active'."""
    sid = await _seed_parent(conn, "p-active-status", state="Running")
    await _add_agent_event(conn, sid, "2026-08-06T10:05:00Z", "senior-developer", "Code")
    await _add_child_session(conn, "c-sd-run", sid, "senior-developer", "claude-sonnet-4-6",
                              "Running", "2026-08-06T10:05:00Z", 100, 20, 0, 0)

    result = await db_module.get_session_chain(conn, sid)
    entry = result["roster"][0]
    assert entry["status"] == "active"
    assert entry["history"][-1]["status"] == "active"


@pytest.mark.asyncio
async def test_roster_status_active_when_last_child_idle(conn):
    """BUG-FIX: latest call has Idle child (agent between LLM rounds) → status='active'.

    An agent waiting for LLM inference doesn't write JSONL events; after
    IDLE_THRESHOLD_SEC the state machine marks its child session 'Idle'.
    The roster should still show 'active', not 'done'.
    """
    sid = await _seed_parent(conn, "p-idle-child", state="Running")
    await _add_agent_event(conn, sid, "2026-08-06T10:05:00Z", "junior-developer", "Code feature")
    await _add_child_session(conn, "c-jd-idle", sid, "junior-developer", "claude-sonnet-4-6",
                              "Idle", "2026-08-06T10:05:00Z", 300, 60, 0, 0)

    result = await db_module.get_session_chain(conn, sid)
    entry = result["roster"][0]
    assert entry["status"] == "active", (
        "Idle child session should show 'active' — agent is between LLM rounds, not done"
    )
    assert entry["history"][-1]["status"] == "active"


@pytest.mark.asyncio
async def test_roster_status_done_when_parent_idle(conn):
    """Parent Idle → all roles status='done' (Idle is ambiguous, not a reliable 'active' signal).

    New logic only trusts session_state=='Running' as the parent-alive gate.
    Idle parent → conservatively 'done' to prevent 3+ roles showing 'active' simultaneously.
    """
    sid = await _seed_parent(conn, "p-idle-parent-idle-child", state="Idle")
    await _add_agent_event(conn, sid, "2026-08-06T10:05:00Z", "junior-developer", "Code feature")
    await _add_child_session(conn, "c-jd-idle2", sid, "junior-developer", "claude-sonnet-4-6",
                              "Idle", "2026-08-06T10:05:00Z", 300, 60, 0, 0)

    result = await db_module.get_session_chain(conn, sid)
    entry = result["roster"][0]
    assert entry["status"] == "done", (
        "Idle parent should show 'done' — Idle is ambiguous, use Running as active gate"
    )
    assert entry["history"][-1]["status"] == "done"


@pytest.mark.asyncio
async def test_roster_status_active_fallback_when_no_child_yet(conn):
    """BUG-FIX: latest call has no child session yet (file not indexed) → status='active' fallback.

    When a parent session is Running and has an Agent call for a role but the
    child transcript file hasn't been scanned yet (watcher lag or file not yet
    created), child_state is None.  We should conservatively show 'active'.
    """
    sid = await _seed_parent(conn, "p-no-child-yet", state="Running")
    # Agent event exists in parent but no child session row in DB yet
    await _add_agent_event(conn, sid, "2026-08-06T10:05:00Z", "junior-developer", "Code feature")
    # No _add_child_session call — simulates watcher lag

    result = await db_module.get_session_chain(conn, sid)
    entry = result["roster"][0]
    assert entry["status"] == "active", (
        "Missing child session on Running parent should fallback to 'active'"
    )


@pytest.mark.asyncio
async def test_roster_status_done_when_child_ended_parent_running(conn):
    """Latest call's child is Ended even though parent is Running → status='done'."""
    sid = await _seed_parent(conn, "p-child-ended", state="Running")
    await _add_agent_event(conn, sid, "2026-08-06T10:05:00Z", "senior-developer", "Code")
    await _add_child_session(conn, "c-sd-ended", sid, "senior-developer", "claude-sonnet-4-6",
                              "Ended", "2026-08-06T10:05:00Z", 100, 20, 0, 0)

    result = await db_module.get_session_chain(conn, sid)
    entry = result["roster"][0]
    assert entry["status"] == "done"


@pytest.mark.asyncio
async def test_roster_status_done_when_session_ended(conn):
    """Ended session → all roles status='done'."""
    sid = await _seed_parent(conn, "p-ended-status", state="Ended")
    await _add_agent_event(conn, sid, "2026-08-06T10:05:00Z", "senior-developer", "Code")
    await _add_child_session(conn, "c-sd-end", sid, "senior-developer", "claude-sonnet-4-6",
                              "Ended", "2026-08-06T10:05:00Z", 100, 20, 0, 0)

    result = await db_module.get_session_chain(conn, sid)
    entry = result["roster"][0]
    assert entry["status"] == "done"


@pytest.mark.asyncio
async def test_roster_empty_when_no_agent_calls(conn):
    """Session with no Agent events → roster=[]."""
    sid = await _seed_parent(conn, "p-no-agents")
    result = await db_module.get_session_chain(conn, sid)
    assert result is not None
    assert result["roster"] == []


@pytest.mark.asyncio
async def test_roster_returns_none_for_unknown_session(conn):
    result = await db_module.get_session_chain(conn, "does-not-exist")
    assert result is None


@pytest.mark.asyncio
async def test_history_call_index_increments_per_role(conn):
    """history[].call_index starts at 1 and increments for each repeat call of same role."""
    sid = await _seed_parent(conn, "p-call-idx")
    await _add_agent_event(conn, sid, "2026-08-06T10:01:00Z", "tech-lead", "First")
    await _add_agent_event(conn, sid, "2026-08-06T10:05:00Z", "tech-lead", "Second")

    result = await db_module.get_session_chain(conn, sid)
    entry = result["roster"][0]
    assert entry["history"][0]["call_index"] == 1
    assert entry["history"][1]["call_index"] == 2


# ── New tests: result_summary-based active logic (over-correct fix) ──────────

@pytest.mark.asyncio
async def test_roster_status_done_when_result_present_child_idle(conn):
    """result_summary set on event → 'done' even if child is Idle and parent is Running.

    Primary signal: tool_result received in parent = agent definitively finished.
    Child state (Idle/Running) is irrelevant when result_summary is set.
    """
    sid = await _seed_parent(conn, "p-result-idle-child", state="Running")
    await _add_agent_event(conn, sid, "2026-08-06T10:05:00Z", "senior-developer", "Code",
                           result_summary="Backend hoàn thành. 47 tests pass.",
                           result_full="Backend hoàn thành. 47 tests pass. Commit abc123.")
    await _add_child_session(conn, "c-sd-result-idle", sid, "senior-developer",
                              "claude-sonnet-4-6", "Idle",
                              "2026-08-06T10:05:00Z", 1000, 200, 0, 0)

    result = await db_module.get_session_chain(conn, sid)
    entry = result["roster"][0]
    assert entry["status"] == "done", (
        "result_summary present → agent done, regardless of child Idle state"
    )
    assert entry["history"][-1]["status"] == "done"


@pytest.mark.asyncio
async def test_roster_status_done_when_result_present_child_running(conn):
    """result_summary set → 'done' even if child session is still Running.

    Stale child session (state machine lag) must not override tool_result signal.
    """
    sid = await _seed_parent(conn, "p-result-running-child", state="Running")
    await _add_agent_event(conn, sid, "2026-08-06T10:05:00Z", "tech-lead", "TDD",
                           result_summary="TDD xong. Design approved.",
                           result_full="TDD xong. Design approved. Commit def456.")
    await _add_child_session(conn, "c-tl-result-run", sid, "tech-lead",
                              "claude-opus-4-7", "Running",
                              "2026-08-06T10:05:00Z", 2000, 400, 0, 0)

    result = await db_module.get_session_chain(conn, sid)
    entry = result["roster"][0]
    assert entry["status"] == "done", (
        "result_summary present → done, child Running state is stale/irrelevant"
    )


@pytest.mark.asyncio
async def test_roster_only_one_active_among_multiple_roles(conn):
    """Only 1 role shows 'active' when only 1 has no result; others have result_summary.

    This is the core regression test: prevents 3+ roles showing 'active' simultaneously
    when only 1 agent is actually executing.
    """
    sid = await _seed_parent(conn, "p-one-active", state="Running")
    # PM called and returned result
    await _add_agent_event(conn, sid, "2026-08-06T10:01:00Z", "product-manager", "PRD",
                           result_summary="PRD xong.", result_full="PRD xong. Commit aaa.")
    # TL called and returned result
    await _add_agent_event(conn, sid, "2026-08-06T10:05:00Z", "tech-lead", "TDD",
                           result_summary="TDD xong.", result_full="TDD xong. Commit bbb.")
    # SD currently running — no result yet
    await _add_agent_event(conn, sid, "2026-08-06T10:10:00Z", "senior-developer", "Code")
    await _add_child_session(conn, "c-pm", sid, "product-manager", "claude-sonnet-4-6",
                              "Ended", "2026-08-06T10:01:00Z", 500, 100, 0, 0)
    await _add_child_session(conn, "c-tl", sid, "tech-lead", "claude-opus-4-7",
                              "Ended", "2026-08-06T10:05:00Z", 2000, 400, 0, 0)
    await _add_child_session(conn, "c-sd", sid, "senior-developer", "claude-sonnet-4-6",
                              "Running", "2026-08-06T10:10:00Z", 300, 60, 0, 0)

    result = await db_module.get_session_chain(conn, sid)
    active_roles = [e["role"] for e in result["roster"] if e["status"] == "active"]
    done_roles = [e["role"] for e in result["roster"] if e["status"] == "done"]

    assert active_roles == ["senior-developer"], (
        "Only the role without a result should be 'active'"
    )
    assert set(done_roles) == {"product-manager", "tech-lead"}


@pytest.mark.asyncio
async def test_roster_status_done_when_no_result_parent_ended(conn):
    """No result_summary + parent Ended → 'done' (parent gate blocks active).

    Even if result was never captured (e.g. agent crashed), Ended parent means
    all work is complete — nothing can be 'active'.
    """
    sid = await _seed_parent(conn, "p-ended-no-result", state="Ended")
    await _add_agent_event(conn, sid, "2026-08-06T10:05:00Z", "qa-engineer", "Test")
    # No result_summary, no child session

    result = await db_module.get_session_chain(conn, sid)
    entry = result["roster"][0]
    assert entry["status"] == "done", (
        "Ended parent with missing result should show 'done', not hang as 'active'"
    )
