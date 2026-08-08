"""Event + token_usage inserts (write path from parser/ingester)."""
from __future__ import annotations

from typing import Optional

import aiosqlite


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
