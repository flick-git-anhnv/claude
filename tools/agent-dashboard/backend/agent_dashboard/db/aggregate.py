"""Aggregate pipeline stats + token summary (dashboard-wide queries)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import aiosqlite


async def get_pipeline_aggregate(
    conn: aiosqlite.Connection,
    project: Optional[str] = None,
    window_days: int = 0,
    group_by: str = "agent",
) -> dict[str, Any]:
    """Aggregate pipeline stats across all parent sessions (FR-005 / FR-006).

    Groups child sessions by ``attribution_agent`` (if group_by == "agent")
    or by ``project`` (if group_by == "project").

    Args:
        conn:        Open aiosqlite connection.
        project:     Optional project slug filter (exact match, decoded slug).
        window_days: When > 0, only include sessions with ``last_event_at``
                     within the last N days. Default 0 = all-time.
        group_by:    "agent" (default) or "project".

    Returns:
        Dict with keys: ``mode``, ``total_sessions``, ``total_calls``, ``roster``.
    """
    from ..models import get_subagent_display_name

    # ── Step 1: Collect parent session IDs in scope ──────────────────────────
    filters: list[str] = ["is_subagent = 0"]
    params: list[Any] = []
    if project:
        filters.append("project = ?")
        params.append(project)
    if window_days > 0:
        filters.append("last_event_at >= datetime('now', ?)")
        params.append(f"-{window_days} days")

    parents_sql = f"SELECT session_id FROM sessions WHERE {' AND '.join(filters)}"
    async with conn.execute(parents_sql, params) as cur:
        parent_ids = [r["session_id"] for r in await cur.fetchall()]

    if not parent_ids:
        return {"mode": "aggregate", "total_sessions": 0, "total_calls": 0, "roster": []}

    placeholders = ",".join("?" * len(parent_ids))

    # ── Step 2: Aggregate child/parent sessions ──────────────────────────────
    if group_by == "project":
        # Group by project slug. Sum tokens of ALL sessions (dispatcher + subagents)
        # belonging to the projects of the parent sessions in scope.
        sql = f"""SELECT s.project                                    AS role,
                       (SELECT COUNT(*) FROM sessions s_sub
                          WHERE s_sub.project = s.project
                            AND s_sub.is_subagent = 1
                            AND s_sub.parent_session_id IN ({placeholders})) AS call_count,
                       COUNT(DISTINCT CASE WHEN s.is_subagent = 0 THEN s.session_id ELSE NULL END) AS session_count,
                       SUM(s.token_input)                              AS ti,
                       SUM(s.token_output)                             AS to_,
                       SUM(s.token_cache_creation)                     AS tcc,
                       SUM(s.token_cache_read)                         AS tcr,
                       MIN(s.started_at)                               AS first_at,
                       MAX(s.last_event_at)                            AS last_at,
                       (SELECT COUNT(*) FROM sessions s3 WHERE s3.project = s.project AND s3.state = 'Running') AS active_now,
                       (SELECT agent_type FROM sessions s2
                          WHERE s2.project = s.project
                            AND s2.is_subagent = 0
                            AND s2.session_id IN ({placeholders})
                          ORDER BY last_event_at DESC LIMIT 1)        AS latest_model
                  FROM sessions s
                 WHERE s.project IN (SELECT DISTINCT project FROM sessions WHERE session_id IN ({placeholders}))
                 GROUP BY s.project
                 ORDER BY call_count DESC"""
        async with conn.execute(sql, parent_ids + parent_ids + parent_ids) as cur:
            rows = await cur.fetchall()
    else:
        group_col = "attribution_agent"
        where_clause = f"parent_session_id IN ({placeholders}) AND attribution_agent IS NOT NULL"
        sql = f"""SELECT {group_col}                                AS role,
                       COUNT(*)                                    AS call_count,
                       COUNT(DISTINCT parent_session_id)           AS session_count,
                       SUM(token_input)                            AS ti,
                       SUM(token_output)                           AS to_,
                       SUM(token_cache_creation)                   AS tcc,
                       SUM(token_cache_read)                       AS tcr,
                       MIN(started_at)                             AS first_at,
                       MAX(last_event_at)                          AS last_at,
                       SUM(CASE state WHEN 'Running' THEN 1 ELSE 0 END) AS active_now,
                       (SELECT agent_type FROM sessions s2
                          WHERE s2.{group_col} = sessions.{group_col}
                            AND s2.parent_session_id IN ({placeholders})
                          ORDER BY last_event_at DESC LIMIT 1)    AS latest_model
                  FROM sessions
                 WHERE {where_clause}
                 GROUP BY {group_col}
                 ORDER BY call_count DESC"""
        async with conn.execute(sql, parent_ids + parent_ids) as cur:
            rows = await cur.fetchall()

    roster: list[dict[str, Any]] = []
    for r in rows:
        entry = {
            "role":            r["role"],
            "display_name":    r["role"] if group_by == "project" else get_subagent_display_name(r["role"]),
            "call_count":      r["call_count"],
            "session_count":   r["session_count"],
            "latest_model":    r["latest_model"],
            "first_called_at": r["first_at"],
            "last_called_at":  r["last_at"],
            "total_tokens": {
                "input":          r["ti"]  or 0,
                "output":         r["to_"] or 0,
                "cache_creation": r["tcc"] or 0,
                "cache_read":     r["tcr"] or 0,
            },
            "status":     "done",
            "active_now": r["active_now"] or 0,
        }

        if group_by == "project":
            async with conn.execute(
                """SELECT attribution_agent, COUNT(*) AS call_count,
                          SUM(token_input) AS ti, SUM(token_output) AS to_
                     FROM sessions
                    WHERE project = ? AND is_subagent = 1 AND attribution_agent IS NOT NULL
                    GROUP BY attribution_agent
                    ORDER BY call_count DESC""",
                (r["role"],),
            ) as sub_cur:
                sub_rows = await sub_cur.fetchall()
            entry["project_roster"] = [
                {
                    "role": sr["attribution_agent"],
                    "display_name": get_subagent_display_name(sr["attribution_agent"]),
                    "call_count": sr["call_count"],
                    "total_tokens": {
                        "input": sr["ti"] or 0,
                        "output": sr["to_"] or 0,
                    }
                }
                for sr in sub_rows
            ]

            # Active agents: sessions currently Running in this project (subagents + dispatcher)
            # Use LEFT JOIN to fetch current_subagent_activity from parent dispatcher session
            # if this is a subagent session itself (where is_subagent = 1).
            async with conn.execute(
                """SELECT s.session_id, s.attribution_agent, s.agent_type,
                          s.current_subagent_type,
                          COALESCE(s.current_subagent_activity, p.current_subagent_activity) AS current_activity,
                          s.token_input, s.token_output,
                          s.token_cache_creation, s.token_cache_read,
                          s.is_subagent
                     FROM sessions s
                     LEFT JOIN sessions p ON s.parent_session_id = p.session_id
                    WHERE s.project = ? AND s.state = 'Running'
                    ORDER BY s.is_subagent ASC, s.started_at ASC""",
                (r["role"],),
            ) as act_cur:
                act_rows = await act_cur.fetchall()
            entry["active_agents"] = [
                {
                    "session_id":   ar["session_id"],
                    "role":         ar["attribution_agent"],
                    "display_name": (
                        "Claude (Dispatcher)"
                        if not ar["attribution_agent"]
                        else get_subagent_display_name(ar["attribution_agent"])
                    ),
                    "is_dispatcher": not ar["attribution_agent"],
                    "model":         ar["agent_type"],
                    "current_activity": ar["current_activity"],
                    "tokens": {
                        "input":          ar["token_input"] or 0,
                        "output":         ar["token_output"] or 0,
                        "cache_creation": ar["token_cache_creation"] or 0,
                        "cache_read":     ar["token_cache_read"] or 0,
                    },
                }
                for ar in act_rows
            ]

            # Bug 2: back-fill is_active into project_roster items.
            # active_agents is built above; derive the set of currently-running roles
            # (excluding dispatcher) and stamp each roster item explicitly.
            active_roles: set[str] = {
                a["role"]
                for a in entry["active_agents"]
                if not a["is_dispatcher"] and a["role"]
            }
            for item in entry["project_roster"]:
                item["is_active"] = item["role"] in active_roles

        roster.append(entry)


    return {
        "mode":           "aggregate",
        "total_sessions": len(parent_ids),
        "total_calls":    sum(e["call_count"] for e in roster),
        "roster":         roster,
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
