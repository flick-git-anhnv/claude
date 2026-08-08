"""Pipeline aggregate REST endpoint (Sprint 5 / FR-005 / FR-006)."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Query, Request, HTTPException

router = APIRouter(prefix="/api/pipeline", tags=["pipeline"])


def _get_db(request: Request):
    return request.app.state.db


@router.get("/aggregate")
async def pipeline_aggregate(
    request: Request,
    project: Optional[str] = Query(None, description="Project slug filter (exact match)"),
    window: int = Query(0, ge=0, description="Only sessions with last_event_at in last N days; 0 = all-time"),
    group_by: str = Query("agent", description="Group data by 'agent' or 'project'"),
):
    """Aggregate pipeline stats across all parent sessions.

    Groups child sessions (subagents) by role (attribution_agent) or project slug,
    returning call counts and token totals — sorted by call_count DESC.
    """
    if group_by not in ("agent", "project"):
        raise HTTPException(400, detail="group_by must be 'agent' or 'project'")

    from .. import db as db_module
    conn = _get_db(request)
    return await db_module.get_pipeline_aggregate(
        conn, project=project, window_days=window, group_by=group_by
    )
