"""Pipeline aggregate REST endpoint (Sprint 5 / FR-005)."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query, Request

router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])


def _get_db(request: Request):
    return request.app.state.db


@router.get("/aggregate")
async def pipeline_aggregate(
    request: Request,
    project: Optional[str] = Query(None, description="Project slug filter (exact match)"),
    window: int = Query(0, ge=0, description="Only sessions with last_event_at in last N days; 0 = all-time"),
):
    """Aggregate pipeline stats across all parent sessions.

    Groups child sessions (subagents) by role (attribution_agent), returning
    per-role call counts and token totals — sorted by call_count DESC.

    Response shape:
    ```json
    {
      "mode": "aggregate",
      "total_sessions": 42,
      "total_calls": 156,
      "roster": [
        {
          "role": "senior-developer",
          "display_name": "Senior Developer",
          "call_count": 47,
          "session_count": 12,
          "latest_model": "claude-sonnet-4-6",
          "first_called_at": "2026-08-05T...",
          "last_called_at": "2026-08-06T...",
          "total_tokens": {"input": N, "output": N, "cache_creation": N, "cache_read": N},
          "status": "done",
          "active_now": 2
        }
      ]
    }
    ```
    """
    from .. import db as db_module
    conn = _get_db(request)
    return await db_module.get_pipeline_aggregate(conn, project=project, window_days=window)
