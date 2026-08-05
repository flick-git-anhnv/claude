"""Account management REST endpoints — CRUD + activate + reveal."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, Response

from ..accounts import mask_key
from ..models import AccountCreate, AccountUpdate, error_response

router = APIRouter(prefix="/api/accounts", tags=["accounts"])


def _store(request: Request):
    return request.app.state.account_store


@router.get("")
def list_accounts(request: Request):
    return _store(request).list_accounts()


@router.post("", status_code=201)
def add_account(request: Request, body: AccountCreate):
    try:
        acc_id = _store(request).add_account(body.name, body.api_key)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=error_response("ACCOUNT_KEY_INVALID", str(exc)),
        ) from exc
    store = _store(request)
    acc = store.get_account(acc_id)
    if not acc:
        raise HTTPException(500, detail=error_response("INTERNAL_ERROR", "Account creation failed"))
    return {
        "id": acc["id"],
        "name": acc["name"],
        "key_masked": mask_key(acc["api_key"]),
        "is_active": False,
        "created_at": acc["created_at"],
    }


@router.patch("/{acc_id}")
def update_account(request: Request, acc_id: str, body: AccountUpdate):
    ok = _store(request).update_account(acc_id, body.name)
    if not ok:
        raise HTTPException(
            status_code=404,
            detail=error_response("ACCOUNT_NOT_FOUND", f"Account '{acc_id}' not found"),
        )
    return _store(request).list_accounts()


@router.delete("/{acc_id}", status_code=204)
def delete_account(request: Request, acc_id: str):
    store = _store(request)
    try:
        store.delete_account(acc_id)
    except ValueError:
        raise HTTPException(
            status_code=409,
            detail=error_response("ACCOUNT_ACTIVE_CANNOT_DELETE", "Cannot delete the active account"),
        )
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=error_response("ACCOUNT_NOT_FOUND", f"Account '{acc_id}' not found"),
        )
    # Broadcast account_changed delta via WebSocket
    active = store.get_active()
    _broadcast_account_change(request, active)
    return Response(status_code=204)


@router.post("/{acc_id}/activate")
async def activate_account(request: Request, acc_id: str):
    store = _store(request)
    try:
        store.activate(acc_id)
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=error_response("ACCOUNT_NOT_FOUND", f"Account '{acc_id}' not found"),
        )
    active = store.get_active()
    _broadcast_account_change(request, active)
    return {"active_id": acc_id}


@router.get("/{acc_id}/reveal")
def reveal_key(request: Request, acc_id: str):
    store = _store(request)
    try:
        key = store.reveal_key(acc_id)
    except RuntimeError:
        raise HTTPException(
            status_code=429,
            detail=error_response("RATE_LIMIT_EXCEEDED", "Reveal rate limit: 5 times per minute"),
        )
    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=error_response("ACCOUNT_NOT_FOUND", f"Account '{acc_id}' not found"),
        )
    return {"api_key": key}


# ── Internal helper ───────────────────────────────────────────────────────────

def _broadcast_account_change(request: Request, active: dict | None) -> None:
    """Fire-and-forget WebSocket broadcast for account changes."""
    import asyncio
    from ..models import make_delta

    ws_manager = getattr(request.app.state, "ws_manager", None)
    if ws_manager is None:
        return

    payload = make_delta(
        "account_changed",
        {
            "active_id": active["id"] if active else None,
            "name": active["name"] if active else None,
            "key_masked": active["key_masked"] if active else None,
        },
    )

    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.ensure_future(ws_manager.broadcast(payload))
