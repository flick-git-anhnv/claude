---
title: "asyncio.Lock không tự động chia sẻ — coroutine khác nhau phải nhận cùng 1 Lock instance"
category: python-tkinter
tags: [asyncio, concurrency, race-condition, fastapi]
created: 2026-08-06
updated: 2026-08-06
severity: HIGH
project: agent-dashboard
---

# asyncio.Lock không tự động chia sẻ — coroutine khác nhau phải nhận cùng 1 Lock instance

## Vấn đề gặp phải

**Triệu chứng (H-1 race condition):** Hàm `activate_oauth_account()` và background scheduler (`_do_swap_and_invoke()`) đều đọc/ghi cùng 1 file `.credentials.json`, nhưng chúng dùng 2 code path khác nhau và KHÔNG chia sẻ lock. Kết quả: scheduler's `finally` block restore file backup của nó, **overwrite** credential vừa được activate — user thấy "Activate thành công" trên UI nhưng file trên disk vẫn là account cũ.

**Root cause:** `_do_swap_and_invoke` đã có `async with refresh_lock:` nhưng `activate_oauth_account` KHÔNG nhận lock này vì không có trong signature. Developer thêm background scheduler sau khi viết activate function, quên cập nhật để chúng chia sẻ lock.

## Giải pháp đúng

**Quy tắc:** Mọi coroutine cần exclusive access vào cùng 1 resource (file, socket, shared state) PHẢI dùng cùng 1 `asyncio.Lock` instance. Lock phải được:
1. Tạo ở 1 nơi (module-level hoặc app state)
2. Inject vào TẤT CẢ function cần nó qua parameter
3. KHÔNG tạo `asyncio.Lock()` mới trong mỗi function (lock mới = không có mutual exclusion)

```python
# ❌ SAI — mỗi function tạo lock riêng, không có mutual exclusion
async def activate_oauth_account(acc_id, store, path):
    lock = asyncio.Lock()   # Lock mới → không liên quan gì với scheduler lock
    async with lock:
        ...

async def _do_swap_and_invoke(acc_id, store, path, refresh_lock):
    async with refresh_lock:   # Lock khác hoàn toàn
        ...
```

```python
# ✅ ĐÚNG — cùng 1 lock instance inject vào cả 2 function
async def activate_oauth_account(acc_id, store, path, refresh_lock: asyncio.Lock):
    async with refresh_lock:   # Chặn nếu _do_swap_and_invoke đang giữ lock
        ...

async def _do_swap_and_invoke(acc_id, store, path, refresh_lock: asyncio.Lock):
    async with refresh_lock:   # Chặn nếu activate đang giữ lock
        ...
```

**Expose lock qua app state (FastAPI):**

```python
# main.py — tạo lock 1 lần
_oauth_refresh_lock = asyncio.Lock()

async def lifespan(app):
    app.state.oauth_refresh_lock = _oauth_refresh_lock  # expose cho routes
    ...

# routes/accounts.py — lấy lock từ app state
def _get_refresh_lock(request: Request) -> asyncio.Lock:
    return request.app.state.oauth_refresh_lock

async def activate_account(request: Request, acc_id: str):
    lock = _get_refresh_lock(request)
    result = await activate_oauth_account(acc_id, store, creds_path, lock)
```

## Phân tích deadlock

Trước khi thêm lock vào function, PHẢI kiểm tra deadlock:
- `_do_swap_and_invoke` giữ lock → có gọi `activate_oauth_account` không? **Không** → an toàn
- `activate_oauth_account` giữ lock → có gọi `_do_swap_and_invoke` không? **Không** → an toàn
- Deadlock chỉ xảy ra khi: A giữ lock X, chờ lock Y; B giữ lock Y, chờ lock X

## Test pattern cho concurrent lock

```python
def test_activate_and_scheduler_serialized_by_lock(tmp_path):
    """Verify hai coroutine chạy concurrent nhưng serialize qua shared lock."""
    lock = asyncio.Lock()
    execution_order = []

    async def _run():
        async def holder():
            async with lock:
                execution_order.append("holder_start")
                await asyncio.sleep(0.05)  # giữ lock 50ms
                execution_order.append("holder_end")

        async def waiter():
            await asyncio.sleep(0.01)  # delay nhỏ để holder lấy lock trước
            await func_that_uses_lock(lock)
            execution_order.append("waiter_done")

        await asyncio.gather(holder(), waiter())

    asyncio.get_event_loop().run_until_complete(_run())
    
    # holder_end phải trước waiter_done — waiter bị chặn đến khi holder release
    assert execution_order.index("holder_end") < execution_order.index("waiter_done")
```

## Khi nào cần shared Lock?

| Tình huống | Cần shared Lock? |
|---|---|
| 2+ coroutine đọc/ghi cùng 1 file | ✅ Bắt buộc |
| 2+ coroutine update cùng 1 dict/list không phải `asyncio.Queue` | ✅ Bắt buộc |
| Background scheduler + HTTP handler cùng modify shared state | ✅ Bắt buộc |
| Mỗi coroutine dùng resource riêng biệt | ❌ Không cần |
| Read-only concurrent (không write) | ❌ Không cần (thường) |

## Bài học rút ra

1. Khi thêm background scheduler sau function đã viết sẵn: **ngay lập tức kiểm tra** xem scheduler và function có cùng đụng resource không — nếu có, inject lock vào cả 2.
2. `asyncio.Lock()` **mỗi lần tạo là 1 lock mới, độc lập** — tạo trong function là sai hoàn toàn.
3. Security audit STRIDE theo "Tampering" category sẽ bắt được pattern này: "2 path ghi cùng resource không có synchronization".
