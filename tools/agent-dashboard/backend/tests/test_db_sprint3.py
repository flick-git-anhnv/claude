"""Sprint 3 DB tests — migration, title helpers, snapshot last_*, get_session_chain."""
from __future__ import annotations

import json
import pathlib

import pytest
import pytest_asyncio
import aiosqlite

from agent_dashboard import db as db_module


# ── Async DB fixture (in-memory SQLite) ───────────────────────────────────────

@pytest_asyncio.fixture
async def conn():
    """In-memory aiosqlite connection with full schema + migrations applied."""
    c = await aiosqlite.connect(":memory:")
    c.row_factory = aiosqlite.Row
    await c.executescript(db_module._SCHEMA_SQL)
    await c.commit()
    await db_module._migrate_subagent_columns(c)
    await db_module._migrate_sprint3_columns(c)
    yield c
    await c.close()


# ── _migrate_sprint3_columns ──────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_sprint3_columns_exist(conn):
    """After migration, sessions table must have all 5 Sprint 3 columns."""
    async with conn.execute("PRAGMA table_info(sessions)") as cur:
        rows = await cur.fetchall()
    col_names = {row["name"] for row in rows}
    for expected in ("title", "last_input_tokens", "last_cache_creation",
                     "last_cache_read", "last_usage_at"):
        assert expected in col_names, f"Missing column: {expected}"


@pytest.mark.asyncio
async def test_migration_idempotent(conn):
    """Running _migrate_sprint3_columns twice must not raise."""
    await db_module._migrate_sprint3_columns(conn)  # second call
    async with conn.execute("PRAGMA table_info(sessions)") as cur:
        rows = await cur.fetchall()
    col_names = {r["name"] for r in rows}
    assert "title" in col_names


# ── BUG-003: cleanup migration ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_bug003_cleanup_fixes_empty_started_at(conn):
    """Rows with started_at='' must be updated to last_event_at after migration."""
    # Seed 3 sessions with started_at=''
    for i in range(3):
        await conn.execute(
            """INSERT INTO sessions
                 (session_id, project, file_path, started_at, last_event_at, state)
               VALUES (?, 'proj', 'p', '', '2026-08-06T10:00:00Z', 'Ended')""",
            (f"session-bug-{i}",),
        )
    await conn.commit()

    # Run cleanup migration
    await db_module._migrate_sprint3_columns(conn)

    # All 3 must now have non-empty started_at
    async with conn.execute(
        "SELECT COUNT(*) AS cnt FROM sessions WHERE started_at = ''",
    ) as cur:
        row = await cur.fetchone()
    assert row["cnt"] == 0


@pytest.mark.asyncio
async def test_bug003_cleanup_sets_started_at_to_last_event_at(conn):
    """Cleanup must copy last_event_at → started_at for affected rows."""
    await conn.execute(
        """INSERT INTO sessions
             (session_id, project, file_path, started_at, last_event_at, state)
           VALUES ('s-fix', 'p', 'f', '', '2026-08-06T12:30:00Z', 'Ended')""",
    )
    await conn.commit()

    await db_module._migrate_sprint3_columns(conn)

    async with conn.execute(
        "SELECT started_at FROM sessions WHERE session_id = 's-fix'",
    ) as cur:
        row = await cur.fetchone()
    assert row["started_at"] == "2026-08-06T12:30:00Z"


# ── update_title / update_title_if_null ───────────────────────────────────────

@pytest_asyncio.fixture
async def session_row(conn):
    """A seeded session with no title."""
    await conn.execute(
        """INSERT INTO sessions
             (session_id, project, file_path, started_at, last_event_at, state)
           VALUES ('sess-title', 'proj', 'f', '2026-08-06T10:00:00Z',
                   '2026-08-06T10:00:01Z', 'Running')""",
    )
    await conn.commit()
    return "sess-title"


@pytest.mark.asyncio
async def test_update_title_sets_title(conn, session_row):
    await db_module.update_title(conn, session_row, "My session title")
    async with conn.execute(
        "SELECT title FROM sessions WHERE session_id = ?", (session_row,)
    ) as cur:
        row = await cur.fetchone()
    assert row["title"] == "My session title"


@pytest.mark.asyncio
async def test_update_title_overwrites_existing(conn, session_row):
    """update_title (ai_title source) always overwrites — even an existing title."""
    await db_module.update_title(conn, session_row, "First title")
    await db_module.update_title(conn, session_row, "Updated title")
    async with conn.execute(
        "SELECT title FROM sessions WHERE session_id = ?", (session_row,)
    ) as cur:
        row = await cur.fetchone()
    assert row["title"] == "Updated title"


@pytest.mark.asyncio
async def test_update_title_if_null_sets_when_null(conn, session_row):
    """update_title_if_null must set title when it is NULL."""
    updated = await db_module.update_title_if_null(conn, session_row, "Fallback title")
    assert updated is True
    async with conn.execute(
        "SELECT title FROM sessions WHERE session_id = ?", (session_row,)
    ) as cur:
        row = await cur.fetchone()
    assert row["title"] == "Fallback title"


@pytest.mark.asyncio
async def test_update_title_if_null_skips_when_already_set(conn, session_row):
    """update_title_if_null must NOT overwrite existing title."""
    await db_module.update_title(conn, session_row, "ai_title value")
    updated = await db_module.update_title_if_null(conn, session_row, "user fallback")
    assert updated is False
    async with conn.execute(
        "SELECT title FROM sessions WHERE session_id = ?", (session_row,)
    ) as cur:
        row = await cur.fetchone()
    assert row["title"] == "ai_title value"


# ── upsert_session: snapshot last_* columns ───────────────────────────────────

@pytest.mark.asyncio
async def test_upsert_session_snapshot_updates_last_columns(conn):
    """last_input_tokens, last_cache_creation, last_cache_read, last_usage_at
    must be written (ghi đè) when last_usage_at is provided."""
    await db_module.upsert_session(
        conn,
        session_id="snap-sess",
        project="p",
        file_path="f",
        agent_type="claude-sonnet-4-6",
        timestamp="2026-08-06T10:00:00Z",
        input_tokens=1000,
        output_tokens=200,
        cache_creation=50,
        cache_read=500,
        last_input_tokens=1000,
        last_cache_creation_tokens=50,
        last_cache_read_tokens=500,
        last_usage_at="2026-08-06T10:00:00Z",
    )
    async with conn.execute(
        """SELECT last_input_tokens, last_cache_creation, last_cache_read, last_usage_at
             FROM sessions WHERE session_id = 'snap-sess'"""
    ) as cur:
        row = await cur.fetchone()
    assert row["last_input_tokens"] == 1000
    assert row["last_cache_creation"] == 50
    assert row["last_cache_read"] == 500
    assert row["last_usage_at"] == "2026-08-06T10:00:00Z"


@pytest.mark.asyncio
async def test_upsert_session_snapshot_overwrites_not_cumulates(conn):
    """Second call with new usage must OVERWRITE last_*, not add."""
    for i, (inp, at) in enumerate([
        (1000, "2026-08-06T10:00:00Z"),
        (2000, "2026-08-06T10:01:00Z"),
    ]):
        await db_module.upsert_session(
            conn,
            session_id="snap-ow",
            project="p",
            file_path="f",
            agent_type="claude-sonnet-4-6",
            timestamp=at,
            input_tokens=inp,
            output_tokens=100,
            cache_creation=0,
            cache_read=0,
            last_input_tokens=inp,
            last_cache_creation_tokens=0,
            last_cache_read_tokens=0,
            last_usage_at=at,
        )
    async with conn.execute(
        "SELECT last_input_tokens, token_input FROM sessions WHERE session_id = 'snap-ow'"
    ) as cur:
        row = await cur.fetchone()
    # last_input_tokens = last lượt value (overwrite)
    assert row["last_input_tokens"] == 2000
    # token_input = cumulative (1000 + 2000)
    assert row["token_input"] == 3000


@pytest.mark.asyncio
async def test_upsert_session_no_snapshot_when_last_usage_at_none(conn):
    """When last_usage_at is None, last_* columns must remain at default 0."""
    await db_module.upsert_session(
        conn,
        session_id="no-snap",
        project="p",
        file_path="f",
        agent_type=None,
        timestamp="2026-08-06T10:00:00Z",
        input_tokens=0,
        output_tokens=0,
        cache_creation=0,
        cache_read=0,
        # No snapshot kwargs
    )
    async with conn.execute(
        "SELECT last_input_tokens, last_usage_at FROM sessions WHERE session_id = 'no-snap'"
    ) as cur:
        row = await cur.fetchone()
    assert (row["last_input_tokens"] or 0) == 0
    assert row["last_usage_at"] is None


@pytest.mark.asyncio
async def test_upsert_session_empty_timestamp_is_skipped(conn):
    """upsert_session with empty timestamp must return False and not write to DB."""
    result = await db_module.upsert_session(
        conn,
        session_id="empty-ts",
        project="p",
        file_path="f",
        agent_type=None,
        timestamp="",
        input_tokens=0,
        output_tokens=0,
        cache_creation=0,
        cache_read=0,
    )
    assert result is False
    async with conn.execute(
        "SELECT COUNT(*) AS cnt FROM sessions WHERE session_id = 'empty-ts'"
    ) as cur:
        row = await cur.fetchone()
    assert row["cnt"] == 0


# ── get_session_chain ─────────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def chain_session(conn):
    """Session with 2 Agent tool_use events in the events table."""
    await conn.execute(
        """INSERT INTO sessions
             (session_id, project, file_path, started_at, last_event_at, state)
           VALUES ('chain-sess', 'proj', 'f', '2026-08-06T10:00:00Z',
                   '2026-08-06T10:30:00Z', 'Running')""",
    )
    # Two Agent events
    agent_event_1 = json.dumps({
        "type": "assistant",
        "timestamp": "2026-08-06T10:00:00Z",
        "message": {
            "content": [{
                "type": "tool_use", "name": "Agent",
                "input": {"subagent_type": "product-manager", "description": "Viết PRD"},
            }]
        },
    })
    agent_event_2 = json.dumps({
        "type": "assistant",
        "timestamp": "2026-08-06T10:15:00Z",
        "message": {
            "content": [{
                "type": "tool_use", "name": "Agent",
                "input": {"subagent_type": "business-analyst", "description": "Viết user stories"},
            }]
        },
    })
    # Non-Agent event (must be excluded)
    read_event = json.dumps({
        "type": "assistant",
        "timestamp": "2026-08-06T10:05:00Z",
        "message": {"content": [{"type": "tool_use", "name": "Read", "input": {}}]},
    })
    await conn.execute(
        "INSERT INTO events (session_id, ts, type, tool_name, payload_json) VALUES (?, ?, ?, ?, ?)",
        ("chain-sess", "2026-08-06T10:00:00Z", "tool_use", "Agent", agent_event_1),
    )
    await conn.execute(
        "INSERT INTO events (session_id, ts, type, tool_name, payload_json) VALUES (?, ?, ?, ?, ?)",
        ("chain-sess", "2026-08-06T10:05:00Z", "tool_use", "Read", read_event),
    )
    await conn.execute(
        "INSERT INTO events (session_id, ts, type, tool_name, payload_json) VALUES (?, ?, ?, ?, ?)",
        ("chain-sess", "2026-08-06T10:15:00Z", "tool_use", "Agent", agent_event_2),
    )
    await conn.commit()
    return "chain-sess"


@pytest.mark.asyncio
async def test_get_session_chain_returns_correct_steps(conn, chain_session):
    result = await db_module.get_session_chain(conn, chain_session)
    assert result is not None
    assert result["session_id"] == chain_session
    assert result["session_state"] == "Running"
    assert len(result["steps"]) == 2  # only Agent events


@pytest.mark.asyncio
async def test_get_session_chain_step_fields(conn, chain_session):
    result = await db_module.get_session_chain(conn, chain_session)
    steps = result["steps"]
    # First step
    assert steps[0]["step_index"] == 0
    assert steps[0]["subagent_type"] == "product-manager"
    assert steps[0]["subagent_display"] == "Product Manager"
    assert steps[0]["description"] == "Viết PRD"
    assert steps[0]["status"] == "done"  # not last step
    # Second step (last)
    assert steps[1]["step_index"] == 1
    assert steps[1]["subagent_type"] == "business-analyst"
    assert steps[1]["subagent_display"] == "Business Analyst"
    assert steps[1]["status"] == "active"  # last + Running session


@pytest.mark.asyncio
async def test_get_session_chain_all_done_when_ended(conn):
    """When session is Ended, all steps must be 'done', not 'active'."""
    await conn.execute(
        """INSERT INTO sessions
             (session_id, project, file_path, started_at, last_event_at, state, ended_at)
           VALUES ('ended-sess', 'p', 'f', '2026-08-06T09:00:00Z',
                   '2026-08-06T09:30:00Z', 'Ended', '2026-08-06T09:30:00Z')""",
    )
    payload = json.dumps({
        "type": "assistant",
        "message": {"content": [{"type": "tool_use", "name": "Agent",
                                  "input": {"subagent_type": "senior-developer"}}]},
    })
    await conn.execute(
        "INSERT INTO events (session_id, ts, type, tool_name, payload_json) VALUES (?, ?, ?, ?, ?)",
        ("ended-sess", "2026-08-06T09:00:00Z", "tool_use", "Agent", payload),
    )
    await conn.commit()

    result = await db_module.get_session_chain(conn, "ended-sess")
    assert result is not None
    assert result["steps"][0]["status"] == "done"


@pytest.mark.asyncio
async def test_get_session_chain_empty_steps_for_no_agent_calls(conn):
    """Session with no Agent events → steps=[]."""
    await conn.execute(
        """INSERT INTO sessions
             (session_id, project, file_path, started_at, last_event_at, state)
           VALUES ('no-agent', 'p', 'f', '2026-08-06T10:00:00Z',
                   '2026-08-06T10:00:01Z', 'Running')""",
    )
    await conn.execute(
        "INSERT INTO events (session_id, ts, type, tool_name, payload_json) VALUES (?, ?, ?, ?, ?)",
        ("no-agent", "2026-08-06T10:00:01Z", "tool_use", "Read", "{}"),
    )
    await conn.commit()

    result = await db_module.get_session_chain(conn, "no-agent")
    assert result is not None
    assert result["steps"] == []


@pytest.mark.asyncio
async def test_get_session_chain_returns_none_for_unknown_session(conn):
    """Non-existent session_id → None."""
    result = await db_module.get_session_chain(conn, "does-not-exist")
    assert result is None


# ── _row_to_session: context_pct calculation ─────────────────────────────────

@pytest.mark.asyncio
async def test_row_to_session_context_pct_zero_when_no_usage(conn):
    """Session with no last_* usage → context_pct=0.0."""
    await db_module.upsert_session(
        conn,
        session_id="ctx-zero",
        project="p",
        file_path="f",
        agent_type="claude-sonnet-4-6",
        timestamp="2026-08-06T10:00:00Z",
        input_tokens=0,
        output_tokens=0,
        cache_creation=0,
        cache_read=0,
    )
    sessions = await db_module.get_active_sessions(conn)
    sess = next(s for s in sessions if s["session_id"] == "ctx-zero")
    assert sess["context_pct"] == 0.0
    assert sess["last_input_total"] == 0


@pytest.mark.asyncio
async def test_row_to_session_context_pct_calculated(conn):
    """context_pct = round((last_inp + last_cc + last_cr) / max_context * 100, 1)."""
    # claude-sonnet-4-6 → max_context = 200_000
    # last_total = 1000 + 500 + 100 = 1600
    # context_pct = round(1600 / 200_000 * 100, 1) = 0.8
    await db_module.upsert_session(
        conn,
        session_id="ctx-calc",
        project="p",
        file_path="f",
        agent_type="claude-sonnet-4-6",
        timestamp="2026-08-06T10:00:00Z",
        input_tokens=1000,
        output_tokens=200,
        cache_creation=500,
        cache_read=100,
        last_input_tokens=1000,
        last_cache_creation_tokens=500,
        last_cache_read_tokens=100,
        last_usage_at="2026-08-06T10:00:00Z",
    )
    sessions = await db_module.get_active_sessions(conn)
    sess = next(s for s in sessions if s["session_id"] == "ctx-calc")
    assert sess["last_input_total"] == 1600
    assert sess["max_context"] == 200_000
    assert sess["context_pct"] == 0.8
