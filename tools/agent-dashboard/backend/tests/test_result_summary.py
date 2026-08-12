"""Tests for Sprint 4b: _extract_agent_result + result_summary in /chain response."""
from __future__ import annotations

import json
import pathlib
import tempfile

import pytest
import pytest_asyncio
import aiosqlite

from agent_dashboard import db as db_module
from agent_dashboard.parser import _extract_agent_result


# ── Sprint 5 compatibility helper ─────────────────────────────────────────────

def _non_dispatcher_roster(result: dict) -> list:
    """Filter out the Dispatcher node (FR-004, Sprint 5) from roster."""
    return [r for r in result["roster"] if not r.get("is_dispatcher")]


# ── Helpers to build fake JSONL lines ─────────────────────────────────────────

def _agent_tool_use_line(ts: str, tool_use_id: str, subagent_type: str,
                          run_in_background: bool = False) -> str:
    return json.dumps({
        "type": "assistant",
        "timestamp": ts,
        "message": {
            "role": "assistant",
            "model": "claude-sonnet-4-6",
            "content": [{
                "type": "tool_use",
                "id": tool_use_id,
                "name": "Agent",
                "input": {
                    "subagent_type": subagent_type,
                    "description": f"Run {subagent_type}",
                    "run_in_background": run_in_background,
                },
            }],
            "usage": {"input_tokens": 100, "output_tokens": 20,
                      "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0},
        },
    })


def _sync_tool_result_line(ts: str, tool_use_id: str, result_text: str) -> str:
    return json.dumps({
        "type": "user",
        "timestamp": ts,
        "message": {
            "role": "user",
            "content": [{
                "type": "tool_result",
                "tool_use_id": tool_use_id,
                "content": result_text,
            }],
        },
    })


def _sync_tool_result_list_content_line(ts: str, tool_use_id: str, result_text: str) -> str:
    """Variant where content is a list of text blocks instead of a plain string."""
    return json.dumps({
        "type": "user",
        "timestamp": ts,
        "message": {
            "role": "user",
            "content": [{
                "type": "tool_result",
                "tool_use_id": tool_use_id,
                "content": [{"type": "text", "text": result_text}],
            }],
        },
    })


def _async_tool_result_placeholder_line(ts: str, tool_use_id: str, agent_id: str) -> str:
    """The initial tool_result for an async agent — contains the 'Async agent launched' placeholder."""
    placeholder = (
        f"Async agent launched successfully. "
        f"agentId: {agent_id} (internal ID)"
    )
    return json.dumps({
        "type": "user",
        "timestamp": ts,
        "message": {
            "role": "user",
            "content": [{
                "type": "tool_result",
                "tool_use_id": tool_use_id,
                "content": placeholder,
            }],
        },
    })


def _queue_operation_line(ts: str, tool_use_id: str, agent_id: str, result_text: str) -> str:
    """queue-operation with task-notification XML — delivers the async result."""
    xml = (
        "<task-notification>\n"
        f"<task-id>{agent_id}</task-id>\n"
        f"<tool-use-id>{tool_use_id}</tool-use-id>\n"
        "<status>completed</status>\n"
        f"<result>{result_text}</result>\n"
        "</task-notification>"
    )
    return json.dumps({
        "type": "queue-operation",
        "operation": "enqueue",
        "timestamp": ts,
        "content": xml,
    })


# ── _extract_agent_result tests ───────────────────────────────────────────────

class TestExtractAgentResultSync:
    """SYNC case: tool_result with plain result text."""

    def test_sync_string_content(self):
        """Plain string tool_result content → result_summary set."""
        tool_use_id = "toolu_sync_001"
        result_text = "Backend đã hoàn thành. 47 tests pass."
        lines = [
            _agent_tool_use_line("2026-08-06T10:00:00Z", tool_use_id, "senior-developer"),
            _sync_tool_result_line("2026-08-06T10:05:00Z", tool_use_id, result_text),
        ]
        result = _extract_agent_result(lines, tool_use_id)

        assert result is not None
        assert result["result_summary"] == result_text
        assert result["result_full"] == result_text
        assert result["duration_ms"] is None

    def test_sync_list_content(self):
        """List-of-text-blocks content also works."""
        tool_use_id = "toolu_sync_002"
        result_text = "Frontend hoàn thành. tsc 0 errors."
        lines = [
            _agent_tool_use_line("2026-08-06T10:00:00Z", tool_use_id, "junior-developer"),
            _sync_tool_result_list_content_line("2026-08-06T10:05:00Z", tool_use_id, result_text),
        ]
        result = _extract_agent_result(lines, tool_use_id)

        assert result is not None
        assert result["result_full"] == result_text

    def test_sync_result_truncated_to_400_chars(self):
        """result_summary is at most 400 chars; result_full keeps the full text."""
        tool_use_id = "toolu_sync_003"
        result_text = "x" * 600
        lines = [_sync_tool_result_line("2026-08-06T10:00:00Z", tool_use_id, result_text)]
        result = _extract_agent_result(lines, tool_use_id)

        assert result is not None
        assert len(result["result_summary"]) == 400
        assert len(result["result_full"]) == 600

    def test_sync_wrong_tool_use_id_returns_none(self):
        """If the tool_use_id in the line doesn't match, return None."""
        lines = [
            _sync_tool_result_line("2026-08-06T10:00:00Z", "toolu_other", "some result"),
        ]
        result = _extract_agent_result(lines, "toolu_target")
        assert result is None

    def test_sync_empty_lines_returns_none(self):
        result = _extract_agent_result([], "toolu_any")
        assert result is None

    def test_sync_corrupted_json_skipped(self):
        """Corrupted lines are skipped gracefully."""
        tool_use_id = "toolu_sync_004"
        lines = [
            "not valid json",
            "{}",
            _sync_tool_result_line("2026-08-06T10:00:00Z", tool_use_id, "OK result"),
        ]
        result = _extract_agent_result(lines, tool_use_id)
        assert result is not None
        assert result["result_full"] == "OK result"


class TestExtractAgentResultAsync:
    """ASYNC case: placeholder tool_result + queue-operation with task-notification."""

    def test_async_result_extracted_from_queue_operation(self):
        """Async case: real result comes from queue-operation XML."""
        tool_use_id = "toolu_async_001"
        agent_id = "abc123"
        result_text = "Agent selesai. Semua tests pass. Commit f1a2b3c."
        lines = [
            _agent_tool_use_line(
                "2026-08-06T10:00:00Z", tool_use_id, "senior-developer",
                run_in_background=True
            ),
            _async_tool_result_placeholder_line(
                "2026-08-06T10:00:01Z", tool_use_id, agent_id
            ),
            # Some other lines in between
            json.dumps({"type": "assistant", "timestamp": "2026-08-06T10:01:00Z",
                        "message": {"role": "assistant", "content": [], "usage": {}}}),
            _queue_operation_line(
                "2026-08-06T10:05:00Z", tool_use_id, agent_id, result_text
            ),
        ]
        result = _extract_agent_result(lines, tool_use_id)

        assert result is not None
        assert result["result_summary"] == result_text[:400]
        assert result["result_full"] == result_text
        assert result["duration_ms"] is None

    def test_async_long_result_truncated(self):
        """result_summary truncated at 400 chars for async results too."""
        tool_use_id = "toolu_async_002"
        agent_id = "def456"
        result_text = "y" * 800
        lines = [
            _async_tool_result_placeholder_line("2026-08-06T10:00:00Z", tool_use_id, agent_id),
            _queue_operation_line("2026-08-06T10:05:00Z", tool_use_id, agent_id, result_text),
        ]
        result = _extract_agent_result(lines, tool_use_id)

        assert result is not None
        assert len(result["result_summary"]) == 400
        assert len(result["result_full"]) == 800

    def test_async_placeholder_but_no_notification_returns_none(self):
        """Agent launched async but no queue-operation yet (still running)."""
        tool_use_id = "toolu_async_003"
        lines = [
            _async_tool_result_placeholder_line("2026-08-06T10:00:00Z", tool_use_id, "xyz"),
        ]
        result = _extract_agent_result(lines, tool_use_id)
        assert result is None

    def test_async_wrong_tool_use_id_in_notification_returns_none(self):
        """queue-operation contains a different tool_use_id → no match."""
        tool_use_id = "toolu_async_004"
        lines = [
            _async_tool_result_placeholder_line("2026-08-06T10:00:00Z", tool_use_id, "abc"),
            _queue_operation_line("2026-08-06T10:05:00Z", "toolu_other", "abc", "result"),
        ]
        result = _extract_agent_result(lines, tool_use_id)
        assert result is None


class TestExtractAgentResultNotFound:
    """No tool_result in lines for the given tool_use_id."""

    def test_no_user_messages_returns_none(self):
        lines = [
            json.dumps({"type": "assistant", "timestamp": "2026-08-06T10:00:00Z",
                        "message": {"role": "assistant", "content": []}}),
        ]
        assert _extract_agent_result(lines, "toolu_x") is None

    def test_only_unrelated_tool_results(self):
        lines = [
            _sync_tool_result_line("2026-08-06T10:00:00Z", "toolu_other", "some result"),
        ]
        assert _extract_agent_result(lines, "toolu_target") is None


# ── Async DB fixture ──────────────────────────────────────────────────────────

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


# ── DB migration tests ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_result_columns_exist(conn):
    """events table must have tool_use_id, result_summary, result_full after migration."""
    async with conn.execute("PRAGMA table_info(events)") as cur:
        rows = await cur.fetchall()
    col_names = {r["name"] for r in rows}
    assert "tool_use_id" in col_names
    assert "result_summary" in col_names
    assert "result_full" in col_names


@pytest.mark.asyncio
async def test_result_migration_idempotent(conn):
    """Running migration twice must not raise."""
    await db_module._migrate_result_columns(conn)  # second call
    async with conn.execute("PRAGMA table_info(events)") as cur:
        rows = await cur.fetchall()
    assert "tool_use_id" in {r["name"] for r in rows}


@pytest.mark.asyncio
async def test_insert_event_stores_tool_use_id(conn):
    """insert_event accepts tool_use_id and persists it."""
    await conn.execute(
        """INSERT INTO sessions (session_id, project, file_path, started_at, last_event_at, state)
           VALUES ('sess-r1', 'proj', '/p', '2026-08-06T10:00:00Z', '2026-08-06T10:00:00Z', 'Running')"""
    )
    await conn.commit()

    event_id = await db_module.insert_event(
        conn, "sess-r1", "2026-08-06T10:00:00Z", "tool_use", "Agent",
        '{"msg":"test"}',
        subagent_type="senior-developer",
        tool_use_id="toolu_test_001",
    )

    async with conn.execute(
        "SELECT tool_use_id FROM events WHERE id = ?", (event_id,)
    ) as cur:
        row = await cur.fetchone()
    assert row["tool_use_id"] == "toolu_test_001"


@pytest.mark.asyncio
async def test_update_event_result_persists(conn):
    """update_event_result stores result_summary and result_full."""
    await conn.execute(
        """INSERT INTO sessions (session_id, project, file_path, started_at, last_event_at, state)
           VALUES ('sess-r2', 'proj', '/p', '2026-08-06T10:00:00Z', '2026-08-06T10:00:00Z', 'Running')"""
    )
    await conn.commit()

    event_id = await db_module.insert_event(
        conn, "sess-r2", "2026-08-06T10:00:00Z", "tool_use", "Agent",
        '{}', tool_use_id="toolu_002",
    )

    await db_module.update_event_result(conn, event_id, "short summary", "full text here")

    async with conn.execute(
        "SELECT result_summary, result_full FROM events WHERE id = ?", (event_id,)
    ) as cur:
        row = await cur.fetchone()
    assert row["result_summary"] == "short summary"
    assert row["result_full"] == "full text here"


# ── get_session_chain lazy backfill test ──────────────────────────────────────

@pytest.mark.asyncio
async def test_chain_result_summary_via_backfill(conn, tmp_path):
    """get_session_chain triggers lazy backfill when result_summary is NULL.

    Writes a real JSONL file so _backfill_chain_results can read it.
    """
    tool_use_id = "toolu_backfill_001"
    result_text = "Bước 3.1 hoàn thành. 47 tests pass. Commit abc123."

    # Build a minimal JSONL file with agent tool_use + sync tool_result
    jsonl_lines = [
        _agent_tool_use_line("2026-08-06T10:01:00Z", tool_use_id, "senior-developer"),
        _sync_tool_result_line("2026-08-06T10:05:00Z", tool_use_id, result_text),
    ]
    jsonl_file = tmp_path / "test-session.jsonl"
    jsonl_file.write_text("\n".join(jsonl_lines) + "\n", encoding="utf-8")

    # Seed parent session pointing to the JSONL file
    session_id = "sess-backfill-001"
    await conn.execute(
        """INSERT INTO sessions (session_id, project, file_path, started_at, last_event_at, state)
           VALUES (?, 'proj', ?, '2026-08-06T10:00:00Z', '2026-08-06T10:05:00Z', 'Ended')""",
        (session_id, str(jsonl_file)),
    )
    await conn.commit()

    # Insert Agent event WITHOUT tool_use_id (simulates old event pre-Sprint 4b)
    await conn.execute(
        """INSERT INTO events (session_id, ts, type, tool_name, payload_json,
                               subagent_type, subagent_description)
           VALUES (?, '2026-08-06T10:01:00Z', 'tool_use', 'Agent', '{}',
                   'senior-developer', 'Run senior-developer')""",
        (session_id,),
    )
    await conn.commit()

    # get_session_chain should trigger backfill and return result_summary
    result = await db_module.get_session_chain(conn, session_id)

    assert result is not None
    roster = _non_dispatcher_roster(result)
    assert len(roster) == 1
    history = roster[0]["history"]
    assert len(history) == 1

    h = history[0]
    assert h["result_summary"] is not None
    assert h["result_summary"] == result_text[:400]
    assert h["result_full"] == result_text
    assert h["duration_ms"] is None


@pytest.mark.asyncio
async def test_chain_result_summary_async_via_backfill(conn, tmp_path):
    """Async agent result extracted from queue-operation via backfill."""
    tool_use_id = "toolu_async_backfill_001"
    agent_id = "aaa111bbb"
    result_text = "Async task done. Frontend deployed. tsc 0 errors."

    jsonl_lines = [
        _agent_tool_use_line("2026-08-06T10:01:00Z", tool_use_id, "junior-developer",
                             run_in_background=True),
        _async_tool_result_placeholder_line("2026-08-06T10:01:01Z", tool_use_id, agent_id),
        _queue_operation_line("2026-08-06T10:10:00Z", tool_use_id, agent_id, result_text),
    ]
    jsonl_file = tmp_path / "async-session.jsonl"
    jsonl_file.write_text("\n".join(jsonl_lines) + "\n", encoding="utf-8")

    session_id = "sess-async-backfill"
    await conn.execute(
        """INSERT INTO sessions (session_id, project, file_path, started_at, last_event_at, state)
           VALUES (?, 'proj', ?, '2026-08-06T10:00:00Z', '2026-08-06T10:10:00Z', 'Ended')""",
        (session_id, str(jsonl_file)),
    )
    await conn.commit()

    await conn.execute(
        """INSERT INTO events (session_id, ts, type, tool_name, payload_json,
                               subagent_type, subagent_description)
           VALUES (?, '2026-08-06T10:01:00Z', 'tool_use', 'Agent', '{}',
                   'junior-developer', 'Run junior-developer')""",
        (session_id,),
    )
    await conn.commit()

    result = await db_module.get_session_chain(conn, session_id)
    assert result is not None
    h = _non_dispatcher_roster(result)[0]["history"][0]
    assert h["result_summary"] == result_text[:400]
    assert h["result_full"] == result_text


@pytest.mark.asyncio
async def test_chain_result_none_when_no_tool_result(conn, tmp_path):
    """Agent event with no matching tool_result → result_summary=None (not bịa)."""
    tool_use_id = "toolu_no_result_001"

    # File has the tool_use but no matching tool_result
    jsonl_lines = [
        _agent_tool_use_line("2026-08-06T10:01:00Z", tool_use_id, "qa-engineer"),
    ]
    jsonl_file = tmp_path / "no-result-session.jsonl"
    jsonl_file.write_text("\n".join(jsonl_lines) + "\n", encoding="utf-8")

    session_id = "sess-no-result"
    await conn.execute(
        """INSERT INTO sessions (session_id, project, file_path, started_at, last_event_at, state)
           VALUES (?, 'proj', ?, '2026-08-06T10:00:00Z', '2026-08-06T10:01:00Z', 'Running')""",
        (session_id, str(jsonl_file)),
    )
    await conn.commit()
    await conn.execute(
        """INSERT INTO events (session_id, ts, type, tool_name, payload_json,
                               subagent_type, subagent_description)
           VALUES (?, '2026-08-06T10:01:00Z', 'tool_use', 'Agent', '{}',
                   'qa-engineer', 'Run qa-engineer')""",
        (session_id,),
    )
    await conn.commit()

    result = await db_module.get_session_chain(conn, session_id)
    assert result is not None
    h = _non_dispatcher_roster(result)[0]["history"][0]
    assert h["result_summary"] is None
    assert h["result_full"] is None
    assert h["duration_ms"] is None
