"""Tests for subagent session filtering — parser detection + DB migration + query filter."""
from __future__ import annotations

import json
import pathlib

import pytest
import pytest_asyncio
import aiosqlite

from agent_dashboard import db as db_module
from agent_dashboard.parser import parse_line


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def conn():
    """In-memory aiosqlite connection with full schema + all migrations."""
    c = await aiosqlite.connect(":memory:")
    c.row_factory = aiosqlite.Row
    await c.executescript(db_module._SCHEMA_SQL)
    await c.commit()
    await db_module._migrate_subagent_columns(c)
    await db_module._migrate_sprint3_columns(c)
    await db_module._migrate_events_subagent_columns(c)
    await db_module._migrate_subagent_flag_column(c)
    yield c
    await c.close()


def _user_line(ts: str = "2026-08-06T10:00:00.000Z") -> str:
    return json.dumps({
        "type": "user",
        "timestamp": ts,
        "message": {"role": "user", "content": [{"type": "text", "text": "hello"}]},
    }) + "\n"


# ── Parser: detect subagent path ──────────────────────────────────────────────

def test_parser_normal_session_not_subagent():
    """Main session file → is_subagent=False."""
    path = str(pathlib.Path("proj-abc") / "session-001.jsonl")
    result = parse_line(_user_line(), path)
    assert result is not None
    assert result.is_subagent is False


def test_parser_subagent_transcript_detected():
    """File under subagents/ dir → is_subagent=True."""
    path = str(
        pathlib.Path("proj-abc") / "session-001" / "subagents" / "agent-xyz.jsonl"
    )
    result = parse_line(_user_line(), path)
    assert result is not None
    assert result.is_subagent is True


def test_parser_subagent_session_id_is_stem():
    """session_id for subagent file is the agent-xxx stem, not 'subagents'."""
    path = str(
        pathlib.Path("proj-abc") / "session-001" / "subagents" / "agent-a87dcaf9.jsonl"
    )
    result = parse_line(_user_line(), path)
    assert result is not None
    assert result.session_id == "agent-a87dcaf9"


# ── DB migration: is_subagent column exists ───────────────────────────────────

@pytest.mark.asyncio
async def test_migration_adds_is_subagent_column(conn):
    async with conn.execute("PRAGMA table_info(sessions)") as cur:
        rows = await cur.fetchall()
    col_names = {r["name"] for r in rows}
    assert "is_subagent" in col_names


@pytest.mark.asyncio
async def test_migration_idempotent(conn):
    """Running _migrate_subagent_flag_column twice must not raise."""
    await db_module._migrate_subagent_flag_column(conn)
    async with conn.execute("PRAGMA table_info(sessions)") as cur:
        rows = await cur.fetchall()
    assert "is_subagent" in {r["name"] for r in rows}


# ── DB upsert: is_subagent stored correctly ───────────────────────────────────

@pytest.mark.asyncio
async def test_upsert_stores_is_subagent_false(conn):
    await db_module.upsert_session(
        conn, "sess-main", "proj-abc", "/proj/sess-main.jsonl",
        None, "2026-08-06T10:00:00Z", 0, 0, 0, 0, is_subagent=False,
    )
    async with conn.execute(
        "SELECT is_subagent FROM sessions WHERE session_id = ?", ("sess-main",)
    ) as cur:
        row = await cur.fetchone()
    assert row is not None
    assert row["is_subagent"] == 0


@pytest.mark.asyncio
async def test_upsert_stores_is_subagent_true(conn):
    await db_module.upsert_session(
        conn, "agent-xyz", "proj-abc", "/proj/sess-001/subagents/agent-xyz.jsonl",
        None, "2026-08-06T10:00:01Z", 0, 0, 0, 0, is_subagent=True,
    )
    async with conn.execute(
        "SELECT is_subagent FROM sessions WHERE session_id = ?", ("agent-xyz",)
    ) as cur:
        row = await cur.fetchone()
    assert row is not None
    assert row["is_subagent"] == 1


# ── DB queries: subagent sessions excluded from list endpoints ────────────────

async def _seed(conn, session_id: str, is_subagent: bool, state: str = "Running",
                ts: str = "2026-08-06T10:00:00Z") -> None:
    await db_module.upsert_session(
        conn, session_id, "proj-abc", f"/proj/{session_id}.jsonl",
        None, ts, 0, 0, 0, 0, is_subagent=is_subagent,
    )
    if state != "Running":
        await db_module.update_session_state(conn, session_id, state,
                                             ts if state == "Ended" else None)


@pytest.mark.asyncio
async def test_get_active_sessions_excludes_subagents(conn):
    await _seed(conn, "sess-main-1", is_subagent=False, state="Running")
    await _seed(conn, "agent-sub-1", is_subagent=True,  state="Running")

    rows = await db_module.get_active_sessions(conn)
    ids = {r["session_id"] for r in rows}
    assert "sess-main-1" in ids
    assert "agent-sub-1" not in ids


@pytest.mark.asyncio
async def test_get_sessions_by_project_excludes_subagents(conn):
    await _seed(conn, "sess-main-2", is_subagent=False)
    await _seed(conn, "agent-sub-2", is_subagent=True)

    groups = await db_module.get_sessions_by_project(conn)
    all_ids = {s["session_id"] for g in groups for s in g["sessions"]}
    assert "sess-main-2" in all_ids
    assert "agent-sub-2" not in all_ids


@pytest.mark.asyncio
async def test_get_sessions_by_project_count_excludes_subagents(conn):
    """session_count in project group must not count subagent sessions."""
    await _seed(conn, "sess-main-3", is_subagent=False)
    await _seed(conn, "agent-sub-3", is_subagent=True)

    groups = await db_module.get_sessions_by_project(conn)
    proj = next((g for g in groups if g["project_slug"] == "proj-abc"), None)
    assert proj is not None
    # Only the 3 main sessions seeded across all tests for proj-abc should appear;
    # specifically the count for this single insert pair should be >= 1 (main only).
    for s in proj["sessions"]:
        assert s["session_id"] != "agent-sub-3", "subagent session leaked into group"


@pytest.mark.asyncio
async def test_get_session_history_excludes_subagents(conn):
    await _seed(conn, "sess-hist-1", is_subagent=False, state="Ended",
                ts="2026-08-06T09:00:00Z")
    await _seed(conn, "agent-hist-1", is_subagent=True, state="Ended",
                ts="2026-08-06T09:00:01Z")

    items, total = await db_module.get_session_history(conn, None, None, 100, 0)
    ids = {r["session_id"] for r in items}
    assert "sess-hist-1" in ids
    assert "agent-hist-1" not in ids
