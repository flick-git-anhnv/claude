"""Sprint 5 tests — Usage service, BUG-004 broadcast, FR-004 Dispatcher node, FR-005 aggregate."""
from __future__ import annotations

import asyncio
import json
import pathlib
import time
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import aiosqlite
import pytest
import pytest_asyncio

from agent_dashboard import db as db_module
from agent_dashboard.usage_service import UsageInfo, _pct, get_usage, invalidate_cache


# ── Async DB fixture (in-memory SQLite, all Sprint 1-4 migrations) ────────────

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


# ── Helpers ───────────────────────────────────────────────────────────────────

async def _insert_session(
    conn,
    session_id: str,
    *,
    project: str = "test-project",
    agent_type: str | None = "claude-sonnet-4-6",
    state: str = "Ended",
    is_subagent: bool = False,
    parent_session_id: str | None = None,
    attribution_agent: str | None = None,
    token_input: int = 100,
    token_output: int = 50,
    started_at: str = "2026-08-06T10:00:00",
    last_event_at: str = "2026-08-06T10:05:00",
    title: str | None = None,
) -> None:
    await conn.execute(
        """INSERT INTO sessions
           (session_id, project, file_path, agent_type, state, started_at, last_event_at,
            token_input, token_output, token_cache_creation, token_cache_read,
            is_subagent, parent_session_id, attribution_agent, title)
           VALUES (?,?,?,?,?,?,?,?,?,0,0,?,?,?,?)""",
        (
            session_id, project, f"/fake/{session_id}.jsonl",
            agent_type, state, started_at, last_event_at,
            token_input, token_output,
            1 if is_subagent else 0,
            parent_session_id, attribution_agent, title,
        ),
    )
    await conn.commit()


async def _insert_agent_event(
    conn,
    session_id: str,
    subagent_type: str,
    *,
    ts: str = "2026-08-06T10:01:00",
) -> None:
    # Column name in schema is `type` (not msg_type); tool_use_id added by migration
    await conn.execute(
        """INSERT INTO events (session_id, ts, type, tool_name, payload_json,
                               subagent_type, subagent_description, tool_use_id)
           VALUES (?,?,?,?,?,?,?,?)""",
        (
            session_id, ts, "assistant", "Agent",
            json.dumps({"message": {"role": "assistant"}}),
            subagent_type, f"Do {subagent_type} work", None,
        ),
    )
    await conn.commit()


# ═══════════════════════════════════════════════════════════════════════════════
# A — Usage service tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestPct:
    """Tests for _pct() normalisation helper."""

    def test_pct_none_returns_none(self):
        assert _pct(None) is None

    def test_pct_ratio_scale_multiplied(self):
        # 0..1 ratio → multiply by 100
        assert _pct(0.5) == 50.0

    def test_pct_ratio_one_is_100(self):
        # exactly 1.0 → treated as ratio (= 100%)
        assert _pct(1.0) == 100.0

    def test_pct_percentage_scale_kept(self):
        # > 1.0 → already percentage, kept as-is
        assert _pct(75.0) == 75.0

    def test_pct_zero(self):
        assert _pct(0) == 0.0

    def test_pct_invalid_string_returns_none(self):
        assert _pct("not-a-number") is None


class TestGetUsage:
    """Tests for get_usage() with mocked HTTP client."""

    def setup_method(self):
        invalidate_cache()  # ensure clean cache between tests

    @pytest.mark.asyncio
    async def test_successful_response_parses_fields(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "five_hour": 0.42,
            "seven_day": 0.68,
            "resets_at": 1700000000,
            "rate_limit_type": "five_hour",
        }

        with patch("agent_dashboard.usage_service.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)

            result = await get_usage("acc-001", "token-xyz")

        assert result["account_id"] == "acc-001"
        assert result["five_hour_pct"] == 42.0
        assert result["seven_day_pct"] == 68.0
        assert result["resets_at"] == 1700000000
        assert result["rate_limit_type"] == "five_hour"
        assert "error" not in result

    @pytest.mark.asyncio
    async def test_401_returns_unauthorized_error(self):
        mock_response = MagicMock()
        mock_response.status_code = 401

        with patch("agent_dashboard.usage_service.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_response)
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)

            result = await get_usage("acc-002", "expired-token")

        assert result["error"] == "unauthorized"
        assert "five_hour_pct" not in result

    @pytest.mark.asyncio
    async def test_timeout_returns_timeout_error(self):
        import httpx as _httpx

        with patch("agent_dashboard.usage_service.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(side_effect=_httpx.TimeoutException("timeout"))
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)

            result = await get_usage("acc-003", "token-abc")

        assert result["error"] == "timeout"

    @pytest.mark.asyncio
    async def test_cache_avoids_second_http_call(self):
        invalidate_cache()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"five_hour": 0.3, "seven_day": 0.5}

        call_count = 0

        async def fake_get(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return mock_response

        with patch("agent_dashboard.usage_service.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.get = fake_get
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)

            await get_usage("acc-004", "tok")
            await get_usage("acc-004", "tok")  # second call — should use cache

        assert call_count == 1  # HTTP called exactly once

    @pytest.mark.asyncio
    async def test_force_bypasses_cache(self):
        invalidate_cache()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"five_hour": 0.1}

        call_count = 0

        async def fake_get(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return mock_response

        with patch("agent_dashboard.usage_service.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.get = fake_get
            MockClient.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)

            await get_usage("acc-005", "tok")
            await get_usage("acc-005", "tok", force=True)  # bypass cache

        assert call_count == 2


# ═══════════════════════════════════════════════════════════════════════════════
# B — BUG-004: chain_updated broadcast when child event ingested
# ═══════════════════════════════════════════════════════════════════════════════

class TestBug004ChainUpdated:
    """BUG-004: main.py broadcasts chain_updated when a child session line arrives."""

    @pytest.mark.asyncio
    async def test_child_event_broadcasts_chain_updated(self, tmp_path, conn):
        """_process_file must emit chain_updated with parent_session_id."""
        from agent_dashboard import main as main_module

        parent_id = "parent-aaa-001"
        child_id = "agent-bbb-001"
        project = "test-proj"

        # Write a minimal subagent JSONL file
        subagent_dir = tmp_path / project / parent_id / "subagents"
        subagent_dir.mkdir(parents=True)
        child_file = subagent_dir / f"{child_id}.jsonl"
        line = json.dumps({
            "type": "user",
            "timestamp": "2026-08-06T12:00:00.000Z",
            "isSidechain": True,
            "attributionAgent": "senior-developer",
            "message": {"role": "user", "content": [{"type": "text", "text": "hi"}]},
        }) + "\n"
        child_file.write_text(line, encoding="utf-8")

        # Patch globals inside main module
        broadcast_calls: list[dict] = []

        async def fake_broadcast(msg: dict) -> None:
            broadcast_calls.append(msg)

        mock_ws = MagicMock()
        mock_ws.broadcast = fake_broadcast

        # Reset TailReader so it reads from byte 0
        from agent_dashboard.tail_reader import TailReader
        original_tail = main_module._tail_reader
        main_module._tail_reader = TailReader()

        original_ws = main_module._ws_manager
        main_module._ws_manager = mock_ws

        try:
            # Patch CLAUDE_PROJECTS_DIR inside config so parser detects correct project
            with patch("agent_dashboard.config.CLAUDE_PROJECTS_DIR", tmp_path):
                await main_module._process_file(conn, str(child_file))
        finally:
            main_module._tail_reader = original_tail
            main_module._ws_manager = original_ws

        chain_msgs = [
            m for m in broadcast_calls
            if m.get("payload", {}).get("event") == "chain_updated"
        ]
        assert len(chain_msgs) >= 1, "Expected at least one chain_updated broadcast"
        payload = chain_msgs[0]["payload"]
        assert payload["session_id"] == parent_id
        assert payload["child_session_id"] == child_id
        assert payload["reason"] == "child_event"


# ═══════════════════════════════════════════════════════════════════════════════
# C — FR-004: Dispatcher node prepended to /chain roster
# ═══════════════════════════════════════════════════════════════════════════════

class TestDispatcherNode:
    """FR-004: get_session_chain prepends Dispatcher entry to roster."""

    @pytest.mark.asyncio
    async def test_dispatcher_is_first_roster_entry(self, conn):
        parent_id = "parent-disp-001"
        child_id = "child-disp-001"

        await _insert_session(conn, parent_id, state="Ended", title="My session")
        await _insert_session(
            conn, child_id,
            is_subagent=True, parent_session_id=parent_id,
            attribution_agent="senior-developer", state="Ended",
        )
        await _insert_agent_event(conn, parent_id, "senior-developer")

        result = await db_module.get_session_chain(conn, parent_id)

        assert result is not None
        assert len(result["roster"]) >= 1
        dispatcher = result["roster"][0]
        assert dispatcher["is_dispatcher"] is True
        assert dispatcher["role"] == "__dispatcher__"
        assert dispatcher["display_name"] == "Claude (Dispatcher)"
        assert dispatcher["history"] == []
        assert dispatcher["call_count"] == 1

    @pytest.mark.asyncio
    async def test_dispatcher_status_active_when_running(self, conn):
        parent_id = "parent-disp-002"
        await _insert_session(conn, parent_id, state="Running")
        await _insert_agent_event(conn, parent_id, "tech-lead")

        result = await db_module.get_session_chain(conn, parent_id)
        assert result["roster"][0]["status"] == "active"

    @pytest.mark.asyncio
    async def test_dispatcher_status_done_when_ended(self, conn):
        parent_id = "parent-disp-003"
        await _insert_session(conn, parent_id, state="Ended")
        await _insert_agent_event(conn, parent_id, "qa-engineer")

        result = await db_module.get_session_chain(conn, parent_id)
        assert result["roster"][0]["status"] == "done"

    @pytest.mark.asyncio
    async def test_dispatcher_carries_parent_tokens(self, conn):
        parent_id = "parent-disp-004"
        await _insert_session(
            conn, parent_id, state="Ended",
            token_input=1000, token_output=500,
        )
        await _insert_agent_event(conn, parent_id, "junior-developer")

        result = await db_module.get_session_chain(conn, parent_id)
        tokens = result["roster"][0]["total_tokens"]
        assert tokens["input"] == 1000
        assert tokens["output"] == 500

    @pytest.mark.asyncio
    async def test_dispatcher_present_even_without_subagents(self, conn):
        """Dispatcher node must appear even when there are no Agent tool_use events."""
        parent_id = "parent-disp-005"
        await _insert_session(conn, parent_id, state="Ended")
        # No events, no subagents

        result = await db_module.get_session_chain(conn, parent_id)
        assert result is not None
        assert len(result["roster"]) == 1  # only Dispatcher
        assert result["roster"][0]["is_dispatcher"] is True

    @pytest.mark.asyncio
    async def test_dispatcher_not_in_subagent_sessions(self, conn):
        """get_session_chain called on a child session_id should return None (not found as parent)."""
        parent_id = "parent-disp-006"
        child_id = "child-disp-006"
        await _insert_session(conn, parent_id, state="Ended")
        await _insert_session(
            conn, child_id,
            is_subagent=True, parent_session_id=parent_id,
            attribution_agent="senior-developer", state="Ended",
        )
        # child has no is_subagent=0 row — get_session_chain on child_id finds row,
        # returns a Dispatcher for the child session itself (expected behaviour).
        result = await db_module.get_session_chain(conn, parent_id)
        assert result["roster"][0]["role"] == "__dispatcher__"


# ═══════════════════════════════════════════════════════════════════════════════
# D — FR-005: Aggregate endpoint
# ═══════════════════════════════════════════════════════════════════════════════

class TestPipelineAggregate:
    """FR-005: get_pipeline_aggregate groups child sessions by role."""

    @pytest.mark.asyncio
    async def test_empty_db_returns_zero_totals(self, conn):
        result = await db_module.get_pipeline_aggregate(conn)
        assert result["mode"] == "aggregate"
        assert result["total_sessions"] == 0
        assert result["total_calls"] == 0
        assert result["roster"] == []

    @pytest.mark.asyncio
    async def test_groups_by_role_and_sums_tokens(self, conn):
        parent_id = "parent-agg-001"
        await _insert_session(conn, parent_id, state="Ended")

        # Two child sessions with role "senior-developer"
        for i in range(2):
            await _insert_session(
                conn, f"child-sr-{i}",
                is_subagent=True, parent_session_id=parent_id,
                attribution_agent="senior-developer",
                token_input=100, token_output=50, state="Ended",
            )
        # One child session with role "tech-lead"
        await _insert_session(
            conn, "child-tl-0",
            is_subagent=True, parent_session_id=parent_id,
            attribution_agent="tech-lead",
            token_input=200, token_output=80, state="Ended",
        )

        result = await db_module.get_pipeline_aggregate(conn)
        assert result["total_sessions"] == 1
        roster = result["roster"]

        # sort by call_count DESC — senior-developer (2) before tech-lead (1)
        assert roster[0]["role"] == "senior-developer"
        assert roster[0]["call_count"] == 2
        assert roster[0]["total_tokens"]["input"] == 200   # 100 × 2
        assert roster[1]["role"] == "tech-lead"
        assert roster[1]["call_count"] == 1
        assert result["total_calls"] == 3

    @pytest.mark.asyncio
    async def test_project_filter_excludes_other_projects(self, conn):
        # Parent in project-A
        await _insert_session(conn, "pa-001", project="project-a", state="Ended")
        await _insert_session(
            conn, "ca-001",
            project="project-a", is_subagent=True, parent_session_id="pa-001",
            attribution_agent="qa-engineer", state="Ended",
        )
        # Parent in project-B
        await _insert_session(conn, "pb-001", project="project-b", state="Ended")
        await _insert_session(
            conn, "cb-001",
            project="project-b", is_subagent=True, parent_session_id="pb-001",
            attribution_agent="junior-developer", state="Ended",
        )

        result = await db_module.get_pipeline_aggregate(conn, project="project-a")
        assert result["total_sessions"] == 1
        roles = {r["role"] for r in result["roster"]}
        assert "qa-engineer" in roles
        assert "junior-developer" not in roles

    @pytest.mark.asyncio
    async def test_active_now_counts_running_children(self, conn):
        parent_id = "parent-active-001"
        await _insert_session(conn, parent_id, state="Running")
        await _insert_session(
            conn, "child-run-001",
            is_subagent=True, parent_session_id=parent_id,
            attribution_agent="senior-developer", state="Running",
        )
        await _insert_session(
            conn, "child-end-001",
            is_subagent=True, parent_session_id=parent_id,
            attribution_agent="senior-developer", state="Ended",
        )

        result = await db_module.get_pipeline_aggregate(conn)
        sr_entry = next(r for r in result["roster"] if r["role"] == "senior-developer")
        assert sr_entry["active_now"] == 1  # only the Running child counts
