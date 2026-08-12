"""DB access layer for failover_events table (Sprint 7).

Functions:
    insert_failover_event  — write one event row
    list_failover_events   — paginated query with optional date filter
    count_24h              — count events in the last 24 hours
    purge_old              — delete rows older than N days (called by migration too)

All functions receive an open aiosqlite.Connection that has row_factory=aiosqlite.Row.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

import aiosqlite

logger = logging.getLogger(__name__)

# Whitelist of account fields allowed in chain_snapshot_json — NEVER include tokens
_CHAIN_SNAPSHOT_FIELDS = frozenset({
    "id", "name", "priority", "include_in_chain",
    "five_hour_pct", "seven_day_pct",
})


def serialize_chain_snapshot(accounts: List[Dict[str, Any]]) -> str:
    """Serialize account chain state to JSON, whitelisting safe fields only.

    SECURITY (RT-6): NEVER include accessToken / refreshToken / api_key or any
    credential field. Only the fields in _CHAIN_SNAPSHOT_FIELDS are included.
    A unit test in test_sprint7_failover.py verifies this grep-style.
    """
    safe = []
    for acc in accounts:
        entry = {k: acc.get(k) for k in _CHAIN_SNAPSHOT_FIELDS}
        # Normalise: pct values come from UsageInfo snapshots passed alongside account dicts
        safe.append(entry)
    return json.dumps(safe, ensure_ascii=False)


async def insert_failover_event(
    conn: aiosqlite.Connection,
    *,
    failover_id: str,
    occurred_at: str,
    from_account_id: Optional[str],
    from_account_name: Optional[str],
    to_account_id: Optional[str],
    to_account_name: Optional[str],
    trigger_reason: str,
    result: str,
    swap_latency_ms: Optional[int],
    next_retry_at: Optional[str],
    retry_attempt: Optional[int],
    error_message: Optional[str],
    chain_snapshot_json: Optional[str],
) -> None:
    """Insert one failover event row.  All nullable fields can be None.

    ``chain_snapshot_json`` MUST be produced by :func:`serialize_chain_snapshot`
    to guarantee no credential data leaks into the DB.
    """
    await conn.execute(
        """
        INSERT INTO failover_events (
            failover_id, occurred_at,
            from_account_id, from_account_name,
            to_account_id, to_account_name,
            trigger_reason, result,
            swap_latency_ms, next_retry_at,
            retry_attempt, error_message,
            chain_snapshot_json
        ) VALUES (
            ?, ?,
            ?, ?,
            ?, ?,
            ?, ?,
            ?, ?,
            ?, ?,
            ?
        )
        """,
        (
            failover_id, occurred_at,
            from_account_id, from_account_name,
            to_account_id, to_account_name,
            trigger_reason, result,
            swap_latency_ms, next_retry_at,
            retry_attempt, error_message,
            chain_snapshot_json,
        ),
    )
    await conn.commit()


async def list_failover_events(
    conn: aiosqlite.Connection,
    *,
    from_dt: Optional[str] = None,
    to_dt: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> Dict[str, Any]:
    """Return paginated failover events with optional ISO-date range filter.

    Returns:
        {
            "items": [row_dict, ...],
            "total": int,          -- total rows matching the filter
            "count_24h": int,      -- last-24h count (always computed, not filtered)
        }
    """
    where_clauses: list[str] = []
    params: list[Any] = []

    if from_dt:
        where_clauses.append("occurred_at >= ?")
        params.append(from_dt)
    if to_dt:
        where_clauses.append("occurred_at <= ?")
        params.append(to_dt)

    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

    # Total count
    async with conn.execute(
        f"SELECT COUNT(*) FROM failover_events {where_sql}", params
    ) as cur:
        row = await cur.fetchone()
        total = row[0] if row else 0

    # Paginated items
    async with conn.execute(
        f"""
        SELECT * FROM failover_events
        {where_sql}
        ORDER BY occurred_at DESC
        LIMIT ? OFFSET ?
        """,
        [*params, limit, offset],
    ) as cur:
        rows = await cur.fetchall()

    items = [dict(r) for r in rows]

    c24 = await count_24h(conn)
    return {"items": items, "total": total, "count_24h": c24}


async def count_24h(conn: aiosqlite.Connection) -> int:
    """Count failover events in the last 24 hours."""
    async with conn.execute(
        "SELECT COUNT(*) FROM failover_events WHERE occurred_at >= datetime('now', '-1 day')"
    ) as cur:
        row = await cur.fetchone()
        return row[0] if row else 0


async def purge_old(conn: aiosqlite.Connection, days: int = 30) -> int:
    """Delete rows older than *days* days. Returns number of rows deleted."""
    cur = await conn.execute(
        f"DELETE FROM failover_events WHERE occurred_at < datetime('now', '-{days} days')"
    )
    await conn.commit()
    return cur.rowcount
