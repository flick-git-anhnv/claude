"""Database layer — aiosqlite, WAL mode, single writer via asyncio.

Split into sub-modules by responsibility (2026-08-08 refactor):
    schema     — DDL, migrations, init()
    cursors    — file offset persistence
    sessions   — session CRUD + list/history/detail + row shaper
    events     — event/token_usage insert (write path)
    chain      — get_session_chain + dispatcher history + result backfill
    aggregate  — get_pipeline_aggregate + get_token_summary

All public names are re-exported here so callers can continue to use
`from .. import db as db_module; db_module.get_session_chain(...)`
without changes. Tests that patch `agent_dashboard.db.get_session_chain`
also continue to work because the name is bound on this package.
"""
from __future__ import annotations

# ── Schema & init ─────────────────────────────────────────────────────────────
from .schema import (
    init,
    _SCHEMA_SQL,
    _migrate_subagent_columns,
    _migrate_sprint3_columns,
    _migrate_events_subagent_columns,
    _migrate_result_columns,
    _migrate_sprint4_columns,
    _migrate_subagent_flag_column,
    _migrate_fix_subagent_project_attribution,
    _read_attribution_from_file,
)

# ── Cursor persistence ────────────────────────────────────────────────────────
from .cursors import load_cursors, save_cursor

# ── Session CRUD + queries ────────────────────────────────────────────────────
from .sessions import (
    upsert_session,
    update_title,
    update_title_if_null,
    update_session_state,
    update_session_subagent,
    get_active_sessions,
    get_session_totals,
    get_session_history,
    get_session_detail,
    get_sessions_by_project,
    _row_to_session,
)

# ── Event/token writes ────────────────────────────────────────────────────────
from .events import (
    insert_event,
    update_event_result,
    insert_token_usage,
)

# ── Chain (roster + dispatcher) ───────────────────────────────────────────────
from .chain import (
    get_session_chain,
    _backfill_chain_results,
    _extract_user_turn_text,
)

# ── Aggregate + token summary ─────────────────────────────────────────────────
from .aggregate import (
    get_pipeline_aggregate,
    get_token_summary,
)

__all__ = [
    # schema
    "init",
    # cursors
    "load_cursors", "save_cursor",
    # sessions
    "upsert_session", "update_title", "update_title_if_null",
    "update_session_state", "update_session_subagent",
    "get_active_sessions", "get_session_totals", "get_session_history",
    "get_session_detail", "get_sessions_by_project",
    # events
    "insert_event", "update_event_result", "insert_token_usage",
    # chain
    "get_session_chain",
    # aggregate
    "get_pipeline_aggregate", "get_token_summary",
]
