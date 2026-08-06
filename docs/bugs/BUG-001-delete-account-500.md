# [BUG-001] DELETE /api/accounts/{id} trả HTTP 500 thay vì 204

**Severity:** High | **Priority:** P2
**Môi trường:** Backend FastAPI uvicorn | URL: http://127.0.0.1:7770 | Build: commit ff0bd2e
**Phát hiện:** QA Engineer | Ngày: 2026-08-06

---

## Mô tả

DELETE non-active account trả về HTTP 500 "Internal Server Error" thay vì HTTP 204 No Content.
Tuy nhiên account ĐƯỢC xóa thành công từ disk (data inconsistency): caller nhận 500 nhưng thực ra operation đã thành công.

## Các bước reproduce

1. GET `/api/accounts` — xác nhận có account không active
2. DELETE `/api/accounts/{acc_id}` với account KHÔNG active
3. Kiểm tra HTTP status response
4. GET `/api/accounts` lại — xác nhận account đã biến mất

## Kết quả thực tế

```
HTTP/1.1 500 Internal Server Error
"Internal Server Error"
```

Nhưng sau đó GET `/api/accounts` → account KHÔNG còn → đã bị xóa.

## Kết quả mong đợi (AC US-007 Scenario 4 / HTTP convention)

```
HTTP/1.1 204 No Content
```

Account bị xóa khỏi danh sách và file `accounts.enc`.

## Tần suất

100% reproducible — mọi DELETE non-active account đều trả 500.

## Root Cause (phân tích)

File: `tools/agent-dashboard/backend/agent_dashboard/routes/accounts.py`

```python
@router.delete("/{acc_id}", status_code=204)
def delete_account(request: Request, acc_id: str):  # sync route
    store = _store(request)
    store.delete_account(acc_id)   # ← succeeds, account deleted from disk
    active = store.get_active()
    _broadcast_account_change(request, active)  # ← raises RuntimeError here
    return Response(status_code=204)             # never reached
```

`_broadcast_account_change()` gọi `asyncio.get_event_loop()` từ một **sync route handler** của FastAPI. FastAPI chạy sync routes trong thread pool — không có event loop trong thread đó. `asyncio.get_event_loop()` trong Python 3.10+ raises `DeprecationWarning` và có thể không tạo event loop mới, dẫn đến `asyncio.ensure_future()` fail.

Kết quả: account bị xóa (IO operation thành công) nhưng broadcast thất bại → FastAPI trả 500.

## Tác động

- UI/caller nhận 500 → có thể retry → thấy 404 (account đã xóa) → confusing UX
- Tuy nhiên data trên disk đúng (account đã xóa) — chỉ HTTP status sai
- Severity: High (P2) vì gây UX confusion và có thể gây retry-loop trong client code

## Fix đề xuất

**Option A (preferred):** Đổi `delete_account` thành `async def` và dùng `await` cho broadcast:

```python
@router.delete("/{acc_id}", status_code=204)
async def delete_account(request: Request, acc_id: str):
    ...
    active = store.get_active()
    ws_manager = getattr(request.app.state, "ws_manager", None)
    if ws_manager:
        await ws_manager.broadcast(make_delta("account_changed", {...}))
    return Response(status_code=204)
```

**Option B:** Wrap trong `asyncio.get_event_loop().run_in_executor()` hoặc dùng `asyncio.run_coroutine_threadsafe()`.

## Workaround

Caller có thể kiểm tra GET `/api/accounts` sau khi nhận 500 — nếu account đã biến mất thì operation thành công.
