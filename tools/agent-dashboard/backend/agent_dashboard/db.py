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
  id                   INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id           TEXT NOT NULL,
  ts                   TEXT NOT NULL,
  type                 TEXT NOT NULL,
  tool_name            TEXT,
  payload_json         TEXT,
  subagent_type        TEXT,
  subagent_description TEXT,
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


async def _migrate_sprint3_columns(conn: aiosqlite.Connection) -> None:
    """Idempotent: add Sprint 3 columns to sessions if missing.

    Columns:
      title             TEXT          — friendly session name (FR-003)
      last_input_tokens INTEGER       — last-lượt snapshot, NOT cumulative (FR-002)
      last_cache_creation INTEGER
      last_cache_read   INTEGER
      last_usage_at     TEXT          — ISO timestamp of the last assistant message with usage

    After all ALTER TABLE calls, run a one-time cleanup for BUG-003:
      UPDATE sessions SET started_at = last_event_at
        WHERE started_at = '' OR started_at IS NULL
    This is idempotent — after the first run there are no '' rows left.
    """
    async with conn.execute("PRAGMA table_info(sessions)") as cur:
        rows = await cur.fetchall()
    existing = {row["name"] for row in rows}

    for col, typedef in (
        ("title",              "TEXT"),
        ("last_input_tokens",  "INTEGER DEFAULT 0"),
        ("last_cache_creation","INTEGER DEFAULT 0"),
        ("last_cache_read",    "INTEGER DEFAULT 0"),
        ("last_usage_at",      "TEXT"),
    ):
        if col not in existing:
            await conn.execute(f"ALTER TABLE sessions ADD COLUMN {col} {typedef}")
            logger.info("DB migration: added column sessions.%s", col)

    await conn.commit()

    # BUG-003 cleanup — one-time fix: replace '' started_at with last_event_at
    await conn.execute(
        """UPDATE sessions
             SET started_at = last_event_at
           WHERE started_at = '' OR started_at IS NULL"""
    )
    await conn.commit()
    logger.info("DB migration: BUG-003 cleanup applied (started_at='' → last_event_at)")


async def _migrate_events_subagent_columns(conn: aiosqlite.Connection) -> None:
    """Idempotent: add subagent_type + description columns to events table.

    Rationale: `payload_json` is truncated at 2000 chars (parser.py), which
    frequently corrupts Agent tool_use lines whose input contains large task
    prompts (>2000 chars). Re-parsing the truncated JSON in get_session_chain
    fails silently → chain steps get null subagent_type/description → FR-001
    pipeline UI shows unhelpful placeholders.

    Fix: persist subagent_type and description as first-class columns at
    ingest time (already parsed by parser.py into ParsedLine) so get_session_chain
    can read them directly instead of re-parsing truncated JSON.
    """
    async with conn.execute("PRAGMA table_info(events)") as cur:
        rows = await cur.fetchall()
    existing = {row["name"] for row in rows}

    for col, typedef in (
        ("subagent_type",        "TEXT"),
        ("subagent_description", "TEXT"),
    ):
        if col not in existing:
            await conn.execute(f"ALTER TABLE events ADD COLUMN {col} {typedef}")
            logger.info("DB migration: added column events.%s", col)

    await conn.commit()


async def _migrate_result_columns(conn: aiosqlite.Connection) -> None:
    """Idempotent: add tool_use_id, result_summary, result_full to events (Sprint 4b).

    tool_use_id    — block["id"] of the Agent tool_use content block; used to
                     match the event to its result (tool_result or queue-operation).
    result_summary — first ≤400 chars of the agent's output text.
    result_full    — complete output text.
    """
    async with conn.execute("PRAGMA table_info(events)") as cur:
        rows = await cur.fetchall()
    existing = {row["name"] for row in rows}

    for col, typedef in (
        ("tool_use_id",    "TEXT"),
        ("result_summary", "TEXT"),
        ("result_full",    "TEXT"),
    ):
        if col not in existing:
            await conn.execute(f"ALTER TABLE events ADD COLUMN {col} {typedef}")
            logger.info("DB migration: added column events.%s", col)

    await conn.commit()


async def _migrate_sprint4_columns(conn: aiosqlite.Connection) -> None:
    """Idempotent: add parent_session_id + attribution_agent columns to sessions (Sprint 4).

    parent_session_id — UUID of the parent session (folder above "subagents/" in file path).
    attribution_agent — from JSONL field "attributionAgent", e.g. "senior-developer".

    Also creates an index on parent_session_id for fast chain JOIN queries.

    Retroactive backfill:
    - parent_session_id: derived from file_path (pure path manipulation, no I/O needed).
    - attribution_agent: requires reading the JSONL file; reads first 10 lines to find field.
    """
    import json as _json

    async with conn.execute("PRAGMA table_info(sessions)") as cur:
        rows = await cur.fetchall()
    existing = {row["name"] for row in rows}

    for col, typedef in (
        ("parent_session_id", "TEXT"),
        ("attribution_agent", "TEXT"),
    ):
        if col not in existing:
            await conn.execute(f"ALTER TABLE sessions ADD COLUMN {col} {typedef}")
            logger.info("DB migration: added column sessions.%s", col)

    await conn.commit()

    # Index for fast JOIN in get_session_chain — CREATE INDEX IF NOT EXISTS is idempotent.
    await conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_sessions_parent_id ON sessions(parent_session_id)"
    )
    await conn.commit()

    # Backfill parent_session_id from file_path for existing subagent rows.
    # Path: <project>/<session-uuid>/subagents/agent-*.jsonl → parent = folder above "subagents"
    async with conn.execute(
        "SELECT session_id, file_path FROM sessions WHERE is_subagent = 1 AND parent_session_id IS NULL"
    ) as cur:
        rows = await cur.fetchall()

    parent_fixed = 0
    for row in rows:
        p = Path(row["file_path"])
        if p.parent.name == "subagents":
            parent_id = p.parent.parent.name
            await conn.execute(
                "UPDATE sessions SET parent_session_id = ? WHERE session_id = ?",
                (parent_id, row["session_id"]),
            )
            parent_fixed += 1
    if parent_fixed:
        await conn.commit()
        logger.info("DB migration Sprint 4: backfilled parent_session_id for %d sessions", parent_fixed)

    # Backfill attribution_agent by reading JSONL files for existing subagent rows.
    async with conn.execute(
        "SELECT session_id, file_path FROM sessions WHERE is_subagent = 1 AND attribution_agent IS NULL"
    ) as cur:
        rows = await cur.fetchall()

    attr_fixed = 0
    for row in rows:
        attr = _read_attribution_from_file(row["file_path"])
        if attr:
            await conn.execute(
                "UPDATE sessions SET attribution_agent = ? WHERE session_id = ?",
                (attr, row["session_id"]),
            )
            attr_fixed += 1
    if attr_fixed:
        await conn.commit()
        logger.info("DB migration Sprint 4: backfilled attribution_agent for %d sessions", attr_fixed)


def _read_attribution_from_file(file_path: str) -> Optional[str]:
    """Read the first few lines of a JSONL file to extract 'attributionAgent' field.

    Only reads up to 10 lines — attributionAgent appears on the first assistant message,
    typically within the first 2–3 lines of a subagent transcript.
    Returns None if field not found or file cannot be read.
    """
    import json as _json
    try:
        with open(file_path, encoding="utf-8", errors="replace") as fh:
            for i, line in enumerate(fh):
                if i >= 10:
                    break
                line = line.strip()
                if not line:
                    continue
                try:
                    data = _json.loads(line)
                    attr = data.get("attributionAgent")
                    if attr:
                        return str(attr)
                except (ValueError, AttributeError):
                    pass
    except (OSError, IOError):
        pass
    return None


async def _migrate_subagent_flag_column(conn: aiosqlite.Connection) -> None:
    """Idempotent: add is_subagent column to sessions if missing.

    is_subagent = 1 for transcripts that live under <session>/subagents/.
    These sessions are STORED (Sprint 4 needs them for token join) but HIDDEN
    from all list endpoints (active, by-project, history).
    """
    async with conn.execute("PRAGMA table_info(sessions)") as cur:
        rows = await cur.fetchall()
    existing = {row["name"] for row in rows}

    if "is_subagent" not in existing:
        await conn.execute(
            "ALTER TABLE sessions ADD COLUMN is_subagent INTEGER NOT NULL DEFAULT 0"
        )
        logger.info("DB migration: added column sessions.is_subagent")

    await conn.commit()

    # One-shot retroactive fix: mark existing sessions whose file_path contains
    # a "subagents" directory component.  Covers both Unix (/subagents/) and
    # Windows (\subagents\) path separators.  Idempotent — re-running does
    # nothing when all matching rows already have is_subagent=1.
    cur = await conn.execute(
        """UPDATE sessions
              SET is_subagent = 1
            WHERE is_subagent = 0
              AND (file_path LIKE '%/subagents/%' OR file_path LIKE '%\\subagents\\%')"""
    )
    if cur.rowcount:
        logger.info(
            "DB migration: retroactively marked %d subagent sessions (is_subagent=1)",
            cur.rowcount,
        )
    await conn.commit()


async def _migrate_fix_subagent_project_attribution(conn: aiosqlite.Connection) -> None:
    """One-shot: re-attribute sessions where project='subagents' (bug) to the
    top-level project slug derived from file_path.

    Root cause: watcher is recursive; subagent transcripts live at
      <projects>/<project-slug>/<session-uuid>/subagents/agent-*.jsonl
    Old parser used p.parent.name → yielded "subagents" instead of the real
    project slug. Fixed in parser.py; this migration cleans up stale rows.
    """
    from . import config as _cfg
    try:
        async with conn.execute(
            "SELECT session_id, file_path FROM sessions WHERE project = 'subagents'"
        ) as cur:
            rows = await cur.fetchall()
        if not rows:
            return
        root = _cfg.CLAUDE_PROJECTS_DIR.resolve()
        fixed = 0
        for row in rows:
            fp = row["file_path"]
            try:
                rel = Path(fp).resolve().relative_to(root)
                new_project = rel.parts[0] if rel.parts else None
            except (ValueError, OSError):
                new_project = None
            if new_project and new_project != "subagents":
                await conn.execute(
                    "UPDATE sessions SET project = ? WHERE session_id = ?",
                    (new_project, row["session_id"]),
                )
                fixed += 1
        await conn.commit()
        if fixed:
            logger.info("Migrated %d subagent sessions to correct project slug", fixed)
    except Exception as exc:  # noqa: BLE001
        logger.warning("subagent project migration skipped: %s", exc)


async def init(db_path: Path) -> aiosqlite.Connection:
    """Open DB, enable WAL, create tables, run migrations. Returns open connection."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = await aiosqlite.connect(str(db_path))
    conn.row_factory = aiosqlite.Row
    await conn.executescript(_SCHEMA_SQL)
    await conn.commit()
    await _migrate_subagent_columns(conn)
    await _migrate_sprint3_columns(conn)
    await _migrate_events_subagent_columns(conn)
    await _migrate_fix_subagent_project_attribution(conn)
    await _migrate_subagent_flag_column(conn)
    await _migrate_sprint4_columns(conn)
    await _migrate_result_columns(conn)
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


# ── Events ────────────────────────────────────────────────────────────────────

async def insert_event(
    conn: aiosqlite.Connection,
    session_id: str,
    ts: str,
    msg_type: str,
    tool_name: Optional[str],
    payload_json: str,
    subagent_type: Optional[str] = None,
    subagent_description: Optional[str] = None,
    tool_use_id: Optional[str] = None,
) -> int:
    """Insert one event row. Returns the new row's ROWID (used for lazy backfill)."""
    cur = await conn.execute(
        "INSERT INTO events (session_id, ts, type, tool_name, payload_json, "
        "subagent_type, subagent_description, tool_use_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (session_id, ts, msg_type, tool_name, payload_json,
         subagent_type, subagent_description, tool_use_id),
    )
    await conn.commit()
    return cur.lastrowid


async def update_event_result(
    conn: aiosqlite.Connection,
    event_id: int,
    result_summary: Optional[str],
    result_full: Optional[str],
) -> None:
    """Store result fields on an existing Agent event row (identified by PK)."""
    await conn.execute(
        "UPDATE events SET result_summary = ?, result_full = ? WHERE id = ?",
        (result_summary, result_full, event_id),
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
    """Shape a sessions-table row for API/WS responses.

    Computes:
      - token_total (cumulative, all 4 buckets)
      - current_subagent dict (Track B)
      - last_input_total, max_context, context_pct (Sprint 3 FR-002)
      - title (Sprint 3 FR-003, may be None)
    """
    from .models import get_subagent_display_name
    from .config import resolve_max_context

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


async def get_active_sessions(conn: aiosqlite.Connection) -> list[dict[str, Any]]:
    async with conn.execute(
        """SELECT session_id, project, agent_type, state, started_at, last_event_at,
                  token_input, token_output, token_cache_creation, token_cache_read,
                  current_subagent_type, current_subagent_activity, current_subagent_at,
                  title, last_input_tokens, last_cache_creation, last_cache_read, last_usage_at
           FROM sessions WHERE state != 'Ended' AND is_subagent = 0
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


async def _backfill_chain_results(
    conn: aiosqlite.Connection,
    session_id: str,
    event_rows: list,
) -> None:
    """One-shot lazy backfill: read the session JSONL and populate tool_use_id +
    result_summary/full on Agent events that are still missing those fields.

    Strategy:
    1. Get file_path from sessions table.
    2. Read all lines from the JSONL file.
    3. Build {ts: [tool_use_id, ...]} for every Agent tool_use line in the file.
    4. For each event_row with result_summary=NULL:
       a. If tool_use_id is NULL: resolve it from the ts-based mapping.
       b. Call _extract_agent_result(lines, tool_use_id).
       c. Persist both tool_use_id and result fields to the events row.
    """
    import json as _json
    from collections import defaultdict
    from .parser import _extract_agent_result

    # 1. Get file_path
    async with conn.execute(
        "SELECT file_path FROM sessions WHERE session_id = ?", (session_id,)
    ) as cur:
        row = await cur.fetchone()
    if not row:
        return
    file_path: str = row["file_path"]

    # 2. Read JSONL lines (best-effort; skip on IO error)
    try:
        from pathlib import Path
        session_lines: list[str] = Path(file_path).read_text(
            encoding="utf-8", errors="replace"
        ).splitlines()
    except (OSError, IOError) as exc:
        logger.warning("_backfill_chain_results: cannot read %s — %s", file_path, exc)
        return

    # 3. Build ts → [tool_use_id, ...] from Agent tool_use lines in the file
    ts_to_ids: dict[str, list[str]] = defaultdict(list)
    for raw in session_lines:
        raw = raw.strip()
        if not raw:
            continue
        try:
            data = _json.loads(raw)
        except _json.JSONDecodeError:
            continue
        if data.get("type") != "assistant":
            continue
        for block in (data.get("message") or {}).get("content") or []:
            if (
                isinstance(block, dict)
                and block.get("type") == "tool_use"
                and block.get("name") == "Agent"
                and block.get("id")
            ):
                ts = data.get("timestamp") or ""
                ts_to_ids[ts].append(block["id"])

    # Occurrence counters per ts (to handle rare duplicate-ts events in order)
    ts_occurrence: dict[str, int] = defaultdict(int)

    # 4. Process each missing event row
    for ev in event_rows:
        if ev["result_summary"] is not None:
            continue  # already filled

        event_id: int = ev["id"]
        ts: str = ev["ts"]

        # Resolve tool_use_id: prefer DB value; fall back to ts-based mapping
        tool_use_id: Optional[str] = ev["tool_use_id"]
        if not tool_use_id:
            candidates = ts_to_ids.get(ts, [])
            occ = ts_occurrence[ts]
            if occ < len(candidates):
                tool_use_id = candidates[occ]
            ts_occurrence[ts] += 1

        if not tool_use_id:
            logger.debug(
                "_backfill_chain_results: no tool_use_id for event %d (ts=%s)", event_id, ts
            )
            continue

        result = _extract_agent_result(session_lines, tool_use_id)
        r_summary = result["result_summary"] if result else None
        r_full = result["result_full"] if result else None

        # Persist — always write tool_use_id (even if result is None) so we
        # don't re-scan the same event on the next /chain call.
        await conn.execute(
            """UPDATE events
                  SET tool_use_id    = ?,
                      result_summary = ?,
                      result_full    = ?
                WHERE id = ?""",
            (tool_use_id, r_summary, r_full, event_id),
        )

    await conn.commit()
    logger.debug(
        "_backfill_chain_results: backfill done for session %s (%d Agent events)",
        session_id,
        len(event_rows),
    )


async def get_session_chain(
    conn: aiosqlite.Connection,
    session_id: str,
) -> Optional[dict[str, Any]]:
    """Return pipeline chain for a session as a **roster** (Sprint 4 / FR-001 redesign).

    Roster = one entry per unique subagent role, ordered by first appearance.
    Each entry accumulates token totals across all calls and keeps a per-call history.

    Response shape:
    {
      "session_id": "...",
      "session_state": "Running|Idle|Ended",
      "roster": [
        {
          "role": "senior-developer",
          "display_name": "Senior Developer",
          "status": "active|done",
          "call_count": N,
          "latest_description": "...",
          "latest_model": "claude-sonnet-4-6" | null,
          "first_called_at": "...",
          "last_called_at": "...",
          "total_tokens": {"input": N, "output": N, "cache_creation": N, "cache_read": N},
          "history": [
            {"call_index": 1, "started_at": "...", "description": "...",
             "model": "...", "status": "done", "tokens": {...} | null}
          ]
        }
      ]
    }

    Token data is joined from child sessions via parent_session_id / attribution_agent.
    status = "active" when the latest child session for this role is still Running;
             "done" otherwise (including when no child session found).
    Returns None if the session does not exist.
    """
    import json as _json
    from collections import defaultdict, OrderedDict
    from .models import get_subagent_display_name

    # Verify session exists + get its state
    async with conn.execute(
        "SELECT state FROM sessions WHERE session_id = ?", (session_id,)
    ) as cur:
        row = await cur.fetchone()
    if not row:
        return None
    session_state: str = row["state"]

    # ── Step 1: Fetch all Agent tool_use events ordered chronologically ──────
    async with conn.execute(
        """SELECT id, ts, payload_json, subagent_type, subagent_description,
                  tool_use_id, result_summary, result_full
             FROM events
            WHERE session_id = ? AND tool_name = 'Agent'
            ORDER BY ts ASC""",
        (session_id,),
    ) as cur:
        event_rows = await cur.fetchall()

    # ── Step 1b: Lazy backfill result fields from JSONL if any event is missing them ──
    # This handles both old events (tool_use_id=NULL, ingested before Sprint 4b)
    # and new events where the result arrived after ingest.
    need_backfill = any(
        row["result_summary"] is None for row in event_rows
    )
    if need_backfill and event_rows:
        await _backfill_chain_results(conn, session_id, event_rows)
        # Re-fetch so we have the persisted result_summary/full values
        async with conn.execute(
            """SELECT id, ts, payload_json, subagent_type, subagent_description,
                      tool_use_id, result_summary, result_full
                 FROM events
                WHERE session_id = ? AND tool_name = 'Agent'
                ORDER BY ts ASC""",
            (session_id,),
        ) as cur:
            event_rows = await cur.fetchall()

    # ── Step 2: Build per-call list (resolve subagent_type from stored col / fallback JSON) ──
    raw_calls: list[dict[str, Any]] = []
    for ev in event_rows:
        subagent_type: Optional[str] = ev["subagent_type"] if "subagent_type" in ev.keys() else None
        description: Optional[str] = ev["subagent_description"] if "subagent_description" in ev.keys() else None
        if not subagent_type:
            try:
                data = _json.loads(ev["payload_json"] or "{}")
                message = data.get("message") or {}
                content = message.get("content")
                if isinstance(content, list):
                    for block in content:
                        if (
                            isinstance(block, dict)
                            and block.get("type") == "tool_use"
                            and block.get("name") == "Agent"
                        ):
                            tool_input = block.get("input") or {}
                            subagent_type = tool_input.get("subagent_type") or None
                            description = tool_input.get("description") or None
                            break
            except (ValueError, AttributeError):
                pass
        result_summary: Optional[str] = ev["result_summary"] if "result_summary" in ev.keys() else None
        result_full: Optional[str] = ev["result_full"] if "result_full" in ev.keys() else None
        raw_calls.append({
            "subagent_type":  subagent_type,
            "description":    description,
            "started_at":     ev["ts"],
            "result_summary": result_summary,
            "result_full":    result_full,
        })

    # ── Step 3: Load child sessions grouped by attribution_agent ─────────────
    # IMPORTANT: do NOT filter by is_subagent=0 here — child sessions ARE subagents.
    async with conn.execute(
        """SELECT session_id, attribution_agent, agent_type, state, started_at,
                  token_input, token_output, token_cache_creation, token_cache_read
             FROM sessions
            WHERE parent_session_id = ?
            ORDER BY attribution_agent ASC, started_at ASC""",
        (session_id,),
    ) as cur:
        child_rows = await cur.fetchall()

    # {attribution_agent -> [child dicts sorted by started_at]}
    children_by_role: dict[str, list[dict]] = defaultdict(list)
    for r in child_rows:
        children_by_role[r["attribution_agent"]].append(dict(r))

    # ── Step 4: Match each call to its child session (Nth call of role X → Nth child of role X) ──
    occurrence_counter: dict[str, int] = defaultdict(int)
    matched_calls: list[dict[str, Any]] = []
    for call in raw_calls:
        role = call["subagent_type"]
        if role:
            idx = occurrence_counter[role]
            occurrence_counter[role] += 1
            matches = children_by_role.get(role, [])
            child = matches[idx] if idx < len(matches) else None
        else:
            child = None

        tokens_step: Optional[dict] = None
        model: Optional[str] = None
        child_state: Optional[str] = None
        if child:
            tokens_step = {
                "input":          child["token_input"] or 0,
                "output":         child["token_output"] or 0,
                "cache_creation": child["token_cache_creation"] or 0,
                "cache_read":     child["token_cache_read"] or 0,
            }
            model = child["agent_type"]
            child_state = child["state"]

        matched_calls.append({
            "subagent_type":  role,
            "description":    call["description"],
            "started_at":     call["started_at"],
            "tokens":         tokens_step,
            "model":          model,
            "child_state":    child_state,
            "result_summary": call.get("result_summary"),
            "result_full":    call.get("result_full"),
        })

    # ── Step 5: Build roster — one entry per unique role, ordered by first appearance ──
    # Use OrderedDict to preserve insertion order (Python 3.7+ guarantees it, but explicit is clearer)
    roster_map: dict[str, dict[str, Any]] = OrderedDict()
    for i, call in enumerate(matched_calls):
        role = call["subagent_type"] or "__unknown__"
        if role not in roster_map:
            roster_map[role] = {
                "role":               role if role != "__unknown__" else None,
                "display_name":       get_subagent_display_name(role) if role != "__unknown__" else None,
                "call_count":         0,
                "latest_description": None,
                "latest_model":       None,
                "first_called_at":    call["started_at"],
                "last_called_at":     call["started_at"],
                "total_tokens":       {"input": 0, "output": 0, "cache_creation": 0, "cache_read": 0},
                "history":            [],
            }
        entry = roster_map[role]
        entry["call_count"] += 1
        entry["last_called_at"] = call["started_at"]
        entry["latest_description"] = call["description"]
        if call["model"]:
            entry["latest_model"] = call["model"]

        # Accumulate tokens
        if call["tokens"]:
            for k in ("input", "output", "cache_creation", "cache_read"):
                entry["total_tokens"][k] += call["tokens"][k]

        # Per-call history item
        history_item: dict[str, Any] = {
            "call_index":     entry["call_count"],
            "started_at":     call["started_at"],
            "description":    call["description"],
            "model":          call["model"],
            "tokens":         call["tokens"],
            "result_summary": call.get("result_summary"),
            "result_full":    call.get("result_full"),
            "duration_ms":    None,
        }
        entry["history"].append(history_item)

    # ── Step 6: Compute status for each roster entry ─────────────────────────
    # PRIMARY SIGNAL — result_summary / result_full on the Agent event:
    #   If the parent session has already received a tool_result for this Agent call,
    #   both fields are populated (via backfill or real-time ingest).
    #   result_summary set → agent definitively finished, regardless of child_state.
    #   result_summary None → no result received yet → agent possibly still running.
    #
    # SECONDARY SIGNAL — child session state (only Ended is trusted):
    #   "Ended" is a reliable termination signal.
    #   "Idle" / "Running" are ambiguous (cannot distinguish "waiting for LLM" from
    #   "finished long ago but not yet timed out to Ended") — intentionally ignored.
    #
    # PARENT GATE — session_state == "Running" only:
    #   "Idle" parent = ambiguous (parent stopped writing events while child works).
    #   "Ended" parent = all roles are done.
    #   Only a "Running" parent can have an actively-executing child.
    #
    # Decision table (for the LAST call of each role):
    #   result set           → "done"  (primary, unconditional)
    #   child Ended          → "done"  (secondary, reliable)
    #   parent Ended/Idle    → "done"  (parent gate)
    #   parent Running + no result + child not Ended → "active"
    roster: list[dict[str, Any]] = []
    for role_key, entry in roster_map.items():
        # Find the last matched_call for this role
        last_matched = next(
            (c for c in reversed(matched_calls) if (c["subagent_type"] or "__unknown__") == role_key),
            None,
        )
        last_child_state = last_matched["child_state"] if last_matched else None
        last_result_summary = last_matched.get("result_summary") if last_matched else None
        last_result_full = last_matched.get("result_full") if last_matched else None

        is_active = (
            session_state == "Running"                          # parent still alive
            and last_matched is not None                        # at least one call exists
            and last_result_summary is None                     # no result received yet (primary)
            and last_result_full is None
            and last_child_state != "Ended"                    # Ended child = definitively done
        )
        entry["status"] = "active" if is_active else "done"

        # Annotate each history item's status
        for hist_item in entry["history"]:
            pass  # status per-call is implicitly "done" for all except possibly the last one
        # Last history item is "active" if role is active
        if entry["history"]:
            entry["history"][-1]["status"] = "active" if is_active else "done"
            for h in entry["history"][:-1]:
                h["status"] = "done"

        roster.append(entry)

    return {
        "session_id":    session_id,
        "session_state": session_state,
        "roster":        roster,
    }


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
