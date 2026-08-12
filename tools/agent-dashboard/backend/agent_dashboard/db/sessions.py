"""Session-level CRUD + list/history/detail queries.

Includes the `_row_to_session` shaper used by every endpoint that returns
session data — computes token_total, current_subagent, and Sprint 3
context_pct fields.
"""
from __future__ import annotations

import logging
from typing import Any, Optional

import aiosqlite

logger = logging.getLogger(__name__)


# ── Session upsert ────────────────────────────────────────────────────────────

async def upsert_session(
    conn: aiosqlite.Connection,
    session_id: str,
    project: str,
    file_path: str,
    agent_type: Optional[str],
    timestamp: str,
    input_tokens: int,
    output_tokens: int,
    cache_creation: int,
    cache_read: int,
    # Sprint 3 — snapshot of LAST message usage (FR-002, ghi đè không cộng dồn)
    last_input_tokens: Optional[int] = None,
    last_cache_creation_tokens: Optional[int] = None,
    last_cache_read_tokens: Optional[int] = None,
    last_usage_at: Optional[str] = None,
    # Subagent flag — hide from main list but keep for Sprint 4 token join
    is_subagent: bool = False,
    # Sprint 4 — subagent transcript linking
    parent_session_id: Optional[str] = None,
    attribution_agent: Optional[str] = None,
) -> bool:
    """Insert new session or update existing. Returns True if brand-new session.

    Two UPDATE groups:
      1. Cumulative token totals — always updated (token_* columns).
      2. Last-lượt snapshot — only updated when caller passes last_usage_at
         (i.e. assistant message with usage.input_tokens > 0).
    """
    # Guard: defensive skip if timestamp is empty (BUG-003 double-guard)
    if not timestamp:
        logger.warning("upsert_session called with empty timestamp for %s — skipped", session_id)
        return False

    # Insert only if not already present
    cur = await conn.execute(
        """INSERT OR IGNORE INTO sessions
             (session_id, project, file_path, agent_type, started_at, last_event_at, state,
              is_subagent, parent_session_id, attribution_agent)
           VALUES (?, ?, ?, ?, ?, ?, 'Running', ?, ?, ?)""",
        (session_id, project, file_path, agent_type, timestamp, timestamp,
         1 if is_subagent else 0, parent_session_id, attribution_agent),
    )
    is_new = cur.rowcount > 0

    # Always update last_event_at + cumulative token totals + agent_type (fill in if null)
    await conn.execute(
        """UPDATE sessions SET
             last_event_at         = ?,
             agent_type            = COALESCE(agent_type, ?),
             token_input           = token_input           + ?,
             token_output          = token_output          + ?,
             token_cache_creation  = token_cache_creation  + ?,
             token_cache_read      = token_cache_read      + ?
           WHERE session_id = ?""",
        (timestamp, agent_type, input_tokens, output_tokens, cache_creation, cache_read, session_id),
    )

    # Snapshot last_* columns — only when assistant message with usage (ghi đè)
    if last_usage_at is not None:
        await conn.execute(
            """UPDATE sessions SET
                 last_input_tokens   = ?,
                 last_cache_creation = ?,
                 last_cache_read     = ?,
                 last_usage_at       = ?
               WHERE session_id = ?""",
            (
                last_input_tokens or 0,
                last_cache_creation_tokens or 0,
                last_cache_read_tokens or 0,
                last_usage_at,
                session_id,
            ),
        )

    await conn.commit()
    return is_new


# ── Title helpers (FR-003) ────────────────────────────────────────────────────

async def update_title(
    conn: aiosqlite.Connection,
    session_id: str,
    title: str,
    source: str = "ai_title",
) -> None:
    """Always overwrite title (ai_title source takes priority over user_text)."""
    await conn.execute(
        "UPDATE sessions SET title = ? WHERE session_id = ?",
        (title, session_id),
    )
    await conn.commit()
    logger.debug("Title updated (%s) for session %s: %.40s", source, session_id, title)


async def update_title_if_null(
    conn: aiosqlite.Connection,
    session_id: str,
    title: str,
    source: str = "user_text",
) -> bool:
    """Set title only when currently NULL. Returns True if an update was made."""
    cur = await conn.execute(
        "UPDATE sessions SET title = ? WHERE session_id = ? AND title IS NULL",
        (title, session_id),
    )
    await conn.commit()
    updated = cur.rowcount > 0
    if updated:
        logger.debug("Title set via fallback (%s) for session %s: %.40s", source, session_id, title)
    return updated


async def update_session_state(
    conn: aiosqlite.Connection,
    session_id: str,
    state: str,
    ended_at: Optional[str] = None,
) -> None:
    await conn.execute(
        "UPDATE sessions SET state = ?, ended_at = COALESCE(ended_at, ?) WHERE session_id = ?",
        (state, ended_at, session_id),
    )
    await conn.commit()


async def update_session_subagent(
    conn: aiosqlite.Connection,
    session_id: str,
    subagent_type: str,
    subagent_activity: Optional[str],
    at: str,
) -> None:
    """Update current_subagent_* columns for a session (Track B)."""
    await conn.execute(
        """UPDATE sessions SET
             current_subagent_type     = ?,
             current_subagent_activity = ?,
             current_subagent_at       = ?
           WHERE session_id = ?""",
        (subagent_type, subagent_activity, at, session_id),
    )
    await conn.commit()


# ── Row shaper ────────────────────────────────────────────────────────────────

def _row_to_session(row: aiosqlite.Row) -> dict[str, Any]:
    """Shape a sessions-table row for API/WS responses.

    Computes:
      - token_total (cumulative, all 4 buckets)
      - current_subagent dict (Track B)
      - last_input_total, max_context, context_pct (Sprint 3 FR-002)
      - title (Sprint 3 FR-003, may be None)
    """
    from ..models import get_subagent_display_name
    from ..config import resolve_max_context

    d = dict(row)

    # ── Cumulative token totals (existing) ────────────────────────────────────
    token_total = {
        "input":          d.pop("token_input", 0) or 0,
        "output":         d.pop("token_output", 0) or 0,
        "cache_creation": d.pop("token_cache_creation", 0) or 0,
        "cache_read":     d.pop("token_cache_read", 0) or 0,
    }
    d["token_total"] = token_total

    # ── Current subagent (Track B) ────────────────────────────────────────────
    sub_type     = d.pop("current_subagent_type",     None)
    sub_activity = d.pop("current_subagent_activity", None)
    sub_at       = d.pop("current_subagent_at",       None)
    if sub_type:
        d["current_subagent"] = {
            "type":         sub_type,
            "display_name": get_subagent_display_name(sub_type),
            "activity":     sub_activity,
            "at":           sub_at,
        }
    else:
        d["current_subagent"] = None

    # ── Sprint 3: last-lượt snapshot + context_pct (FR-002) ──────────────────
    last_inp  = d.pop("last_input_tokens",  0) or 0
    last_cc   = d.pop("last_cache_creation", 0) or 0
    last_cr   = d.pop("last_cache_read",    0) or 0
    # last_usage_at stays in d (useful for debugging, small field)

    agent_type_val: Optional[str] = d.get("agent_type")
    max_ctx: int = resolve_max_context(agent_type_val or "")
    last_total: int = last_inp + last_cc + last_cr
    ctx_pct: float = round(last_total / max_ctx * 100, 1) if max_ctx > 0 else 0.0

    d["last_input_total"] = last_total
    d["max_context"]      = max_ctx
    d["context_pct"]      = ctx_pct

    return d


# ── List/history/detail queries ───────────────────────────────────────────────

async def get_active_sessions(
    conn: aiosqlite.Connection, include_subagents: bool = False
) -> list[dict[str, Any]]:
    where_clause = "state != 'Ended'"
    if not include_subagents:
        where_clause += " AND is_subagent = 0"

    async with conn.execute(
        f"""SELECT session_id, project, agent_type, state, started_at, last_event_at,
                   token_input, token_output, token_cache_creation, token_cache_read,
                   current_subagent_type, current_subagent_activity, current_subagent_at,
                   title, last_input_tokens, last_cache_creation, last_cache_read, last_usage_at,
                   is_subagent
            FROM sessions WHERE {where_clause}
            ORDER BY last_event_at DESC"""
    ) as cur:
        rows = await cur.fetchall()
    return [_row_to_session(r) for r in rows]


async def get_session_totals(conn: aiosqlite.Connection, session_id: str) -> dict[str, int]:
    """Return cumulative token totals for a session as TokenCounts object."""
    async with conn.execute(
        """SELECT token_input, token_output, token_cache_creation, token_cache_read
           FROM sessions WHERE session_id = ?""",
        (session_id,),
    ) as cur:
        row = await cur.fetchone()
    if not row:
        return {"input": 0, "output": 0, "cache_creation": 0, "cache_read": 0}
    return {
        "input":          row["token_input"] or 0,
        "output":         row["token_output"] or 0,
        "cache_creation": row["token_cache_creation"] or 0,
        "cache_read":     row["token_cache_read"] or 0,
    }


async def get_session_history(
    conn: aiosqlite.Connection,
    from_dt: Optional[str],
    to_dt: Optional[str],
    limit: int,
    offset: int,
) -> tuple[list[dict[str, Any]], int]:
    conditions = ["state = 'Ended'", "is_subagent = 0"]
    params: list[Any] = []
    if from_dt:
        conditions.append("started_at >= ?")
        params.append(from_dt)
    if to_dt:
        conditions.append("started_at <= ?")
        params.append(to_dt)
    where = " AND ".join(conditions)

    async with conn.execute(f"SELECT COUNT(*) AS cnt FROM sessions WHERE {where}", params) as cur:
        row = await cur.fetchone()
    total = row["cnt"] if row else 0

    async with conn.execute(
        f"""SELECT session_id, project, agent_type, state, started_at, last_event_at, ended_at,
                   token_input, token_output, token_cache_creation, token_cache_read,
                   current_subagent_type, current_subagent_activity, current_subagent_at,
                   title, last_input_tokens, last_cache_creation, last_cache_read, last_usage_at
            FROM sessions WHERE {where}
            ORDER BY started_at DESC LIMIT ? OFFSET ?""",
        params + [limit, offset],
    ) as cur:
        rows = await cur.fetchall()

    return [_row_to_session(r) for r in rows], total


async def get_session_detail(
    conn: aiosqlite.Connection, session_id: str
) -> Optional[tuple[dict, list]]:
    async with conn.execute(
        "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
    ) as cur:
        row = await cur.fetchone()
    if not row:
        return None

    async with conn.execute(
        "SELECT id, ts, type, tool_name, payload_json FROM events WHERE session_id = ? ORDER BY ts",
        (session_id,),
    ) as cur:
        events = await cur.fetchall()

    return dict(row), [dict(e) for e in events]


async def get_sessions_by_project(
    conn: aiosqlite.Connection,
    from_dt: Optional[str] = None,
    to_dt: Optional[str] = None,
) -> list[dict[str, Any]]:
    """Return all sessions grouped by project slug (Track B — 'Theo Dự án' view).

    Reuses the same filter pattern as get_session_history but returns all states
    and groups by project. Does NOT duplicate filter/pagination logic.
    """
    from collections import defaultdict
    from ..models import decode_project_slug

    conditions: list[str] = ["is_subagent = 0"]
    params: list[Any] = []
    if from_dt:
        conditions.append("started_at >= ?")
        params.append(from_dt)
    if to_dt:
        conditions.append("started_at <= ?")
        params.append(to_dt)
    where = "WHERE " + " AND ".join(conditions)

    async with conn.execute(
        f"""SELECT session_id, project, agent_type, state, started_at, last_event_at,
                   token_input, token_output, token_cache_creation, token_cache_read,
                   current_subagent_type, current_subagent_activity, current_subagent_at,
                   title, last_input_tokens, last_cache_creation, last_cache_read, last_usage_at
            FROM sessions {where}
            ORDER BY project ASC, last_event_at DESC""",
        params,
    ) as cur:
        rows = await cur.fetchall()

    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[row["project"]].append(_row_to_session(row))

    result = []
    for slug, sessions in groups.items():
        token_total = sum(
            s["token_total"]["input"] + s["token_total"]["output"]
            + s["token_total"]["cache_creation"] + s["token_total"]["cache_read"]
            for s in sessions
        )
        result.append({
            "project_slug":    slug,
            "project_display": decode_project_slug(slug),
            "session_count":   len(sessions),
            "token_total":     token_total,
            "sessions":        sessions,
        })

    return result
