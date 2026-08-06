"""Session REST endpoints."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request

from ..models import error_response

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


def _get_db(request: Request):
    return request.app.state.db


@router.get("")
async def list_sessions(request: Request):
    """Active sessions (state != Ended)."""
    from .. import db as db_module
    conn = _get_db(request)
    rows = await db_module.get_active_sessions(conn)
    return rows


@router.get("/by-project")
async def sessions_by_project(
    request: Request,
    from_dt: Optional[str] = Query(None, alias="from"),
    to_dt: Optional[str] = Query(None, alias="to"),
):
    """Sessions grouped by project slug for 'Theo Dự án' view (Track B)."""
    from .. import db as db_module
    conn = _get_db(request)
    groups = await db_module.get_sessions_by_project(conn, from_dt, to_dt)
    return groups


@router.get("/history")
async def session_history(
    request: Request,
    from_dt: Optional[str] = Query(None, alias="from"),
    to_dt: Optional[str] = Query(None, alias="to"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    from .. import db as db_module
    conn = _get_db(request)
    items, total = await db_module.get_session_history(conn, from_dt, to_dt, limit, offset)
    return {"items": items, "total": total}


@router.get("/{session_id}")
async def session_detail(request: Request, session_id: str):
    from .. import db as db_module
    conn = _get_db(request)
    result = await db_module.get_session_detail(conn, session_id)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=error_response("SESSION_NOT_FOUND", f"Session '{session_id}' not found"),
        )
    session, events = result
    return {"session": session, "events": events}
