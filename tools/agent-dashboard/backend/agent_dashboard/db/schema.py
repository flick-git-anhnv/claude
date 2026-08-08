"""Database schema, migrations, and initialisation.

All DDL and idempotent ALTER TABLE migrations live here so the rest of the
`db` package can assume the schema is already up to date.
"""
from __future__ import annotations

import json as _json
import logging
from pathlib import Path
from typing import Optional

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
    from .. import config as _cfg
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
