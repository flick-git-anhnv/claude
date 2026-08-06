# [BUG-002] CREATE /api/accounts không validate tên trùng lặp

**Severity:** Medium | **Priority:** P2
**Môi trường:** Backend FastAPI uvicorn | URL: http://127.0.0.1:7770 | Build: commit ff0bd2e
**Phát hiện:** QA Engineer | Ngày: 2026-08-06

---

## Mô tả

POST `/api/accounts` chấp nhận tạo account mới với tên (name) đã tồn tại trong danh sách.
US-007 EC1 và BR3 yêu cầu không cho phép trùng tên.

## Các bước reproduce

1. GET `/api/accounts` — ghi nhớ tên account đang có, ví dụ "KZTEK Test Account"
2. POST `/api/accounts` với `{"name":"KZTEK Test Account","api_key":"sk-ant-different-key-xyz"}`
3. Kiểm tra HTTP status và response

## Kết quả thực tế

```
HTTP/1.1 201 Created
{"id":"acc-511c02a9","name":"KZTEK Test Account","key_masked":"...","is_active":false}
```

Hai accounts cùng tên "KZTEK Test Account" tồn tại trong hệ thống.

## Kết quả mong đợi (AC US-007 EC1, BR3)

```
HTTP/1.1 400 Bad Request
{"error":{"code":"ACCOUNT_NAME_DUPLICATE","message":"Tên tài khoản đã tồn tại, vui lòng chọn tên khác"}}
```

## Tần suất

100% reproducible.

## Root Cause (phân tích)

File: `tools/agent-dashboard/backend/agent_dashboard/routes/accounts.py`

```python
@router.post("", status_code=201)
def add_account(request: Request, body: AccountCreate):
    try:
        acc_id = _store(request).add_account(body.name, body.api_key)
    except ValueError as exc:
        raise HTTPException(status_code=400, ...)
```

File: `tools/agent-dashboard/backend/agent_dashboard/accounts.py`

`AccountStore.add_account()` không kiểm tra tên trùng lặp trước khi tạo account mới.

## Tác động

- Vi phạm US-007 BR3: "không cho phép trùng tên"
- User có thể tạo nhiều accounts cùng tên → khó phân biệt trong UI
- Severity: Medium (P2) — không crash, không mất data, nhưng vi phạm constraint nghiệp vụ

## Fix đề xuất

Trong `AccountStore.add_account()`, thêm kiểm tra trùng tên trước khi insert:

```python
def add_account(self, name: str, api_key: str) -> str:
    # Validate duplicate name
    existing = [a for a in self._data.get("accounts", []) if a["name"] == name]
    if existing:
        raise ValueError(f"Account name '{name}' already exists")
    ...
```

Và trong route, map ValueError với message "already exists" → HTTP 400 với code "ACCOUNT_NAME_DUPLICATE".

## Workaround

Frontend nên kiểm tra trùng tên client-side trước khi gửi request.
