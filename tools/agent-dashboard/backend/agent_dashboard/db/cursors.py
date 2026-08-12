"""File cursor persistence — tracks last-read offset for each JSONL file."""
from __future__ import annotations

from datetime import datetime, timezone

import aiosqlite


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
