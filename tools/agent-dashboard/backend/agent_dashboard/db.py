"""Database layer — aiosqlite, WAL mode, single writer via asyncio."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

import aiosqlite

logger = logging.getLogger(__name__)

# ── Schema ────────────────────────────────────────────────────────────────────

_SCHEMA_SQL = """
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;

CREATE TABLE IF NOT EXISTS sessions (
  session_id            TEXT PRIMARY KEY,
  project               TEXT NOT NULL,
  file_path             TEXT NOT NULL,
  agent_type            TEXT,
  started_at            TEXT NOT NULL,
  last_event_at         TEXT NOT NULL,
  ended_at              TEXT,
  state                 TEXT NOT NULL DEFAULT 'Running',
  token_input           INTEGER DEFAULT 0,
  token_output          INTEGER DEFAULT 0,
  token_cache_creation  INTEGER DEFAULT 0,
  token_cache_read      INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_sessions_state         ON sessions(state);
CREATE INDEX IF NOT EXISTS idx_sessions_last_event_at ON sessions(last_event_at);

CREATE TABLE IF NOT EXISTS events (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id   TEXT NOT NULL,
  ts           TEXT NOT NULL,
  type         TEXT NOT NULL,
  tool_name    TEXT,
  payload_json TEXT,
  FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
CREATE INDEX IF NOT EXISTS idx_events_session_ts ON events(session_id, ts);

CREATE TABLE IF NOT EXISTS token_usage (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id     TEXT NOT NULL,
  ts             TEXT NOT NULL,
  input          INTEGER DEFAULT 0,
  output         INTEGER DEFAULT 0,
  cache_creation INTEGER DEFAULT 0,
  cache_read     INTEGER DEFAULT 0,
  FOREIGN KEY (session_id) REFERENCES sessions(session_id)
);
CREATE INDEX IF NOT EXISTS idx_token_ts ON token_usage(ts);

CREATE TABLE IF NOT EXISTS file_cursors (
  file_path   TEXT PRIMARY KEY,
  last_offset INTEGER NOT NULL,
  updated_at  TEXT NOT NULL
);
"""


async def _migrate_subagent_columns(conn: aiosqlite.Connection) -> None:
    """Idempotent: add current_subagent_* columns to sessions if missing.

    Uses PRAGMA table_info to check before ALTER TABLE — SQLite does not support
    'ADD COLUMN IF NOT EXISTS', so this guard prevents 'duplicate column' errors
    on repeated server restarts.
    """
    async with conn.execute("PRAGMA table_info(sessions)") as cur:
        rows = await cur.fetchall()
    existing = {row["name"] for row in rows}

    for col, typedef in (
        ("current_subagent_type",     "TEXT"),
        ("current_subagent_activity", "TEXT"),
        ("current_subagent_at",       "TEXT"),
    ):
        if col not in existing:
            await conn.execute(f"ALTER TABLE sessions ADD COLUMN {col} {typedef}")
            logger.info("DB migration: added column sessions.%s", col)

    await conn.commit()


async def init(db_path: Path) -> aiosqlite.Connection:
    """Open DB, enable WAL, create tables, run migrations. Returns open connection."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = await aiosqlite.connect(str(db_path))
    conn.row_factory = aiosqlite.Row
    await conn.executescript(_SCHEMA_SQL)
    await conn.commit()
    await _migrate_subagent_columns(conn)
    logger.info("DB initialised at %s", db_path)
    return conn


# ── Cursor persistence ────────────────────────────────────────────────────────

async def load_cursors(conn: aiosqlite.Connection) -> dict[str, int]:
    async with conn.execute("SELECT file_path, last_offset FROM file_cursors") as cur:
        rows = await cur.fetchall()
    return {row["file_path"]: row["last_offset"] for row in rows}


async def save_cursor(conn: aiosqlite.Connection, file_path: str, offset: int) -> None:
    now = datetime.now(timezone.utc).isoformat()
    await conn.execute(
        """INSERT INTO file_cursors (file_path, last_offset, updated_at) VALUES (?, ?, ?)
           ON CONFLICT(file_path) DO UPDATE SET last_offset=excluded.last_offset, updated_at=excluded.updated_at""",
        (file_path, offset, now),
    )
    await conn.commit()


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
) -> bool:
    """Insert new session or update existing. Returns True if brand-new session."""
    # Insert only if not already present
    cur = await conn.execute(
        """INSERT OR IGNORE INTO sessions
             (session_id, project, file_path, agent_type, started_at, last_event_at, state)
           VALUES (?, ?, ?, ?, ?, ?, 'Running')""",
        (session_id, project, file_path, agent_type, timestamp, timestamp),
    )
    is_new = cur.rowcount > 0

    # Always update last_event_at + token totals + agent_type (fill in if null)
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
    await conn.commit()
    return is_new


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


# ── Events ────────────────────────────────────────────────────────────────────

async def insert_event(
    conn: aiosqlite.Connection,
    session_id: str,
    ts: str,
    msg_type: str,
    tool_name: Optional[str],
    payload_json: str,
) -> None:
    await conn.execute(
        "INSERT INTO events (session_id, ts, type, tool_name, payload_json) VALUES (?, ?, ?, ?, ?)",
        (session_id, ts, msg_type, tool_name, payload_json),
    )
    await conn.commit()


# ── Token usage ───────────────────────────────────────────────────────────────

async def insert_token_usage(
    conn: aiosqlite.Connection,
    session_id: str,
    ts: str,
    input_tokens: int,
    output_tokens: int,
    cache_creation: int,
    cache_read: int,
) -> None:
    await conn.execute(
        "INSERT INTO token_usage (session_id, ts, input, output, cache_creation, cache_read) VALUES (?, ?, ?, ?, ?, ?)",
        (session_id, ts, input_tokens, output_tokens, cache_creation, cache_read),
    )
    await conn.commit()


# ── Queries ───────────────────────────────────────────────────────────────────

def _row_to_session(row: aiosqlite.Row) -> dict[str, Any]:
    """Shape a sessions-table row for API/WS responses: token_total as TokenCounts object.

    Also builds current_subagent dict from the 3 subagent columns (may be None).
    """
    from .models import get_subagent_display_name

    d = dict(row)
    token_total = {
        "input":          d.pop("token_input", 0) or 0,
        "output":         d.pop("token_output", 0) or 0,
        "cache_creation": d.pop("token_cache_creation", 0) or 0,
        "cache_read":     d.pop("token_cache_read", 0) or 0,
    }
    d["token_total"] = token_total

    # Build current_subagent object (Track B)
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

    return d


async def get_active_sessions(conn: aiosqlite.Connection) -> list[dict[str, Any]]:
    async with conn.execute(
        """SELECT session_id, project, agent_type, state, started_at, last_event_at,
                  token_input, token_output, token_cache_creation, token_cache_read,
                  current_subagent_type, current_subagent_activity, current_subagent_at
           FROM sessions WHERE state != 'Ended'
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
    conditions = ["state = 'Ended'"]
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
                   current_subagent_type, current_subagent_activity, current_subagent_at
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
    from .models import decode_project_slug

    conditions: list[str] = []
    params: list[Any] = []
    if from_dt:
        conditions.append("started_at >= ?")
        params.append(from_dt)
    if to_dt:
        conditions.append("started_at <= ?")
        params.append(to_dt)
    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    async with conn.execute(
        f"""SELECT session_id, project, agent_type, state, started_at, last_event_at,
                   token_input, token_output, token_cache_creation, token_cache_read,
                   current_subagent_type, current_subagent_activity, current_subagent_at
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


async def get_token_summary(conn: aiosqlite.Connection, range_str: str) -> dict[str, Any]:
    """Return buckets + totals for the given range (7d | 30d | 12w | 6m)."""
    now = datetime.now(timezone.utc)

    # Determine bucket truncation and period
    if range_str == "7d":
        from_dt = now - timedelta(days=7)
        bucket_expr = "strftime('%Y-%m-%d', ts)"
        label_fmt = "%Y-%m-%d"
        days = 7
        delta = timedelta(days=1)
    elif range_str == "30d":
        from_dt = now - timedelta(days=30)
        bucket_expr = "strftime('%Y-%m-%d', ts)"
        label_fmt = "%Y-%m-%d"
        days = 30
        delta = timedelta(days=1)
    elif range_str == "12w":
        from_dt = now - timedelta(weeks=12)
        # SQLite: week starts Monday, strftime('%W', ...) = week number
        bucket_expr = "strftime('%Y-W%W', ts)"
        label_fmt = None  # use raw bucket
        days = 84
        delta = timedelta(weeks=1)
    else:  # 6m
        from_dt = now - timedelta(days=183)
        bucket_expr = "strftime('%Y-%m', ts)"
        label_fmt = None
        days = 183
        delta = timedelta(days=30)

    from_str = from_dt.isoformat()

    async with conn.execute(
        f"""SELECT {bucket_expr} AS bucket,
                   SUM(input)          AS input,
                   SUM(output)         AS output,
                   SUM(cache_creation) AS cache_creation,
                   SUM(cache_read)     AS cache_read
            FROM token_usage
            WHERE ts >= ?
            GROUP BY bucket
            ORDER BY bucket""",
        (from_str,),
    ) as cur:
        rows = await cur.fetchall()

    buckets = [
        {
            "label": row["bucket"],
            "input": row["input"] or 0,
            "output": row["output"] or 0,
            "cache_creation": row["cache_creation"] or 0,
            "cache_read": row["cache_read"] or 0,
        }
        for row in rows
    ]

    totals: dict[str, int] = {"input": 0, "output": 0, "cache_creation": 0, "cache_read": 0}
    for b in buckets:
        for k in totals:
            totals[k] += b[k]
    totals["grand_total"] = sum(totals.values())

    # Distinct session count within the same window
    async with conn.execute(
        "SELECT COUNT(DISTINCT session_id) AS cnt FROM token_usage WHERE ts >= ?",
        (from_str,),
    ) as cur:
        row = await cur.fetchone()
    totals["sessions"] = row["cnt"] if row else 0

    return {"buckets": buckets, "totals": totals}
