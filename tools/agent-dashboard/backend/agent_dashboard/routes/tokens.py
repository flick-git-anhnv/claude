"""Token analytics endpoint."""
from __future__ import annotations

from fastapi import APIRouter, Query, Request

router = APIRouter(prefix="/api/tokens", tags=["tokens"])

_VALID_RANGES = {"7d", "30d", "12w", "6m"}


@router.get("/summary")
async def token_summary(
    request: Request,
    range: str = Query("7d", pattern="^(7d|30d|12w|6m)$"),
):
    from .. import db as db_module
    conn = request.app.state.db
    result = await db_module.get_token_summary(conn, range)
    return result
