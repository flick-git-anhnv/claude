---
step: "8.3"
plan: ../PLAN-MASTER.md
agent: senior-developer
status: done
completed_at: 2026-08-07 14:00
deps: ["8.1", "8.2"]
---

# STEP 8.3 — Backend Sprint 5: Usage Service + BUG-004 Fix + FR-004 Dispatcher Node + FR-005 Aggregate API

## Input nhận
- TDD §29 (Usage): `UsageInfo` TypedDict, endpoints `/usage/active` + `/{acc_id}/usage`, cache 60s, httpx Bearer token
- TDD §30 (BUG-004): child session event trong ingest loop (main.py) cần broadcast `chain_updated` với `parent_session_id`
- TDD §31 (FR-004): prepend Dispatcher node `{is_dispatcher:True, role:"__dispatcher__"}` vào đầu roster mỗi `/chain` response
- TDD §32 (FR-005): `GET /api/pipeline/aggregate?project=&window=` — group by `attribution_agent`, sort `call_count DESC`

## Nhiệm vụ
Implement toàn bộ phần backend Sprint 5 — 4 hạng mục:

**A — Usage Service** | **B — BUG-004 Fix** | **C — FR-004 Dispatcher Node** | **D — FR-005 Aggregate API**

## Definition of Done

### A — Usage Service
- [x] `backend/agent_dashboard/usage_service.py` mới:
  - `UsageInfo` TypedDict (total=False): `account_id`, `five_hour_pct`, `seven_day_pct`, `resets_at`, `error`, `fetched_at`
  - `get_usage(account_id, access_token, *, force=False) -> UsageInfo` — httpx Bearer token, timeout 5s
  - `invalidate_cache(account_id=None)` — xóa cache 1 account hoặc toàn bộ
  - `_pct(v)` — ≤1.0 → ×100 (ratio); >1.0 → giữ nguyên (đã là %)
  - In-memory cache 60s TTL per account_id
- [x] `backend/agent_dashboard/routes/accounts.py`: thêm `GET /usage/active` + `GET /{acc_id}/usage`
  - `/usage/active` PHẢI khai báo TRƯỚC `/{acc_id}/usage` (tránh FastAPI routing conflict)
  - oauth-only: api_key accounts trả về `{"error":"api_key"}`

### B — BUG-004 Fix
- [x] `backend/agent_dashboard/main.py` (`_process_file`): sau khi broadcast WS deltas hiện có, thêm:
  ```python
  if parsed.is_subagent and parsed.parent_session_id:
      await _ws_manager.broadcast(make_delta("chain_updated", {
          "session_id": parsed.parent_session_id,
          "child_session_id": parsed.session_id,
          "reason": "child_event",
      }))
  ```
- [x] Frontend giờ nhận `chain_updated` ngay khi child session có event — không cần đợi model/token data

### C — FR-004 Dispatcher Node
- [x] `backend/agent_dashboard/db.py` (`get_session_chain`):
  - Expand SELECT parent row lấy thêm: `agent_type, started_at, last_event_at, title, token_input, token_output, token_cache_creation, token_cache_read`
  - Trước return, prepend `dispatcher_entry`:
    ```python
    {"role": "__dispatcher__", "display_name": "Claude (Dispatcher)", "is_dispatcher": True,
     "status": "active"|"done", "call_count": 1, "latest_model": parent["agent_type"],
     "total_tokens": {input/output/cache_creation/cache_read}, "history": []}
    ```
  - Dispatcher tokens = tokens của session gốc (LLM turns riêng, không cộng dồn children)

### D — FR-005 Aggregate Endpoint
- [x] `backend/agent_dashboard/db.py`: `get_pipeline_aggregate(conn, project=None, window_days=0)`
  - Lọc parent sessions (is_subagent=0) theo `project` và `window_days`
  - GROUP BY `attribution_agent` — SUM token_input/output/cache*, COUNT calls, SUM(CASE state WHEN 'Running')
  - Bind `parent_ids` 2 lần: correlated subquery (latest_model) + main WHERE
  - Early return `[]` khi không có parent session (tránh SQL IN () empty)
- [x] `backend/agent_dashboard/routes/pipeline.py` (NEW): `GET /api/pipeline/aggregate?project=&window=`

### Chung
- [x] `backend/tests/test_sprint5.py` (mới — 22 tests):
  - `TestPct` (6): None→None, ratio→×100, =1.0, >1.0, zero, invalid string
  - `TestGetUsage` (5): success parse, 401 unauthorized, timeout, cache hit, force bypass cache
  - `TestBug004ChainUpdated` (1): assert `chain_updated` broadcast với `parent_session_id`
  - `TestDispatcherNode` (6): first entry, Running→active, Ended→done, parent tokens, no-subagents, chain check
  - `TestPipelineAggregate` (4): empty DB, group+sum tokens, project filter, active_now counts Running
- [x] Regression test fixup — Sprint 3, 4 tests bị ảnh hưởng bởi FR-004:
  - `test_sprint4_token_step.py`: thêm `_non_dispatcher_roster()` helper, fix 16 assertions
  - `test_db_sprint3.py`: thêm `_non_dispatcher_roster()` helper, fix 3 assertions
  - `test_result_summary.py`: thêm `_non_dispatcher_roster()` helper, fix 3 assertions
- [x] `pytest --tb=short -q` → **250 passed, 0 failed**
- [x] `code-graph/CODE-GRAPH.md` cập nhật (v1.7) — thêm `usage_service.py`, `routes/pipeline.py`, mô tả thay đổi `db.py`, `main.py`, `routes/accounts.py`
- [x] `code-graph/CODE-GRAPH.pdf` xuất lại

## Đã làm

1. Tạo `backend/agent_dashboard/usage_service.py` — `UsageInfo`, `get_usage()`, `_pct()`, `invalidate_cache()`, in-memory cache dict `_cache: dict[str, tuple[float, UsageInfo]]`
2. Cập nhật `backend/agent_dashboard/routes/accounts.py` — thêm route `/usage/active` (TRƯỚC `/{acc_id}/usage`), helper `_fetch_usage()`, kiểm tra `kind=="api_key"` trả về lỗi sớm
3. Cập nhật `backend/agent_dashboard/main.py` — BUG-004: broadcast `chain_updated` WS delta với `parent_session_id` khi `parsed.is_subagent=True`; include `pipeline_router`
4. Cập nhật `backend/agent_dashboard/db.py` — FR-004: expand SELECT + prepend Dispatcher node; FR-005: `get_pipeline_aggregate()` với GROUP BY + correlated subquery
5. Tạo `backend/agent_dashboard/routes/pipeline.py` — `GET /api/pipeline/aggregate`
6. Tạo `backend/tests/test_sprint5.py` — 22 tests toàn Sprint 5
7. Fix regression: thêm `_non_dispatcher_roster()` helper vào 3 test files (test_sprint4_token_step.py, test_db_sprint3.py, test_result_summary.py), sửa tổng 22 assertions
8. Cập nhật `code-graph/CODE-GRAPH.md` v1.7 + xuất PDF

## Artifact
- `backend/agent_dashboard/usage_service.py` (MỚI)
- `backend/agent_dashboard/routes/pipeline.py` (MỚI)
- `backend/agent_dashboard/routes/accounts.py` (sửa — /usage endpoints)
- `backend/agent_dashboard/db.py` (sửa — FR-004 Dispatcher node + FR-005 aggregate)
- `backend/agent_dashboard/main.py` (sửa — BUG-004 chain_updated WS + pipeline router)
- `backend/tests/test_sprint5.py` (MỚI — 22 tests)
- `backend/tests/test_sprint4_token_step.py` (sửa — _non_dispatcher_roster helper + 16 fixes)
- `backend/tests/test_db_sprint3.py` (sửa — _non_dispatcher_roster helper + 3 fixes)
- `backend/tests/test_result_summary.py` (sửa — _non_dispatcher_roster helper + 3 fixes)
- `code-graph/CODE-GRAPH.md` + `.pdf` (v1.7)

## Quyết định quan trọng

1. **BUG-004 fix ở main.py, không phải state_manager**: broadcast `chain_updated` cần ở ingest loop (`_process_file`) — ngay khi parse được child event, không cần đợi DB write hoàn tất.
2. **Route ordering**: `/usage/active` PHẢI khai báo TRƯỚC `/{acc_id}/usage` trong cùng router — FastAPI match theo thứ tự khai báo; nếu đặt sau, literal "usage" bị bắt làm `acc_id`.
3. **Dispatcher tokens = session gốc riêng**: token_input/output của parent row là LLM turns của Dispatcher — không cộng dồn children (mỗi session row độc lập). Không cần phép trừ.
4. **`parent_ids` bind 2 lần trong aggregate query**: correlated subquery `latest_model` dùng 1 lần, main WHERE `IN (...)` dùng lần 2 — phải truyền `(*parent_ids, *parent_ids)` khi execute.
5. **Regression strategy**: thay vì rewrite Sprint 3/4 tests, thêm `_non_dispatcher_roster()` filter helper — giữ nguyên intent test, chỉ lọc Dispatcher entry mới.
6. **`_pct()` defensive**: ≤1.0 → ratio (×100); >1.0 → đã là %; `None`/invalid → return `None`. API trả về ratio, không phải %, nhưng cần xử lý cả 2 để không crash khi API thay đổi.

## Handoff Payload — bước sau đọc phần này (chỉ phần này, không cần đọc "Đã làm")
- **do_not_redo**: usage_service.py, routes/pipeline.py, BUG-004 broadcast trong main.py, Dispatcher node inject trong db.py — tất cả đã implement và test 250/250 pass.
- **watch_out**:
  - `UsageInfo` TypedDict fields: `five_hour_pct`, `seven_day_pct` (float 0–100 sau `_pct()`), `resets_at` (int unix timestamp), `error` (string literal: "api_key"|"no_oauth"|"unauthorized"|"timeout"|"network"|"http_NNN"), `fetched_at` (int unix timestamp).
  - Dispatcher node shape trong roster: `{role: "__dispatcher__", display_name: "Claude (Dispatcher)", is_dispatcher: true, status: "active"|"done", call_count: 1, latest_model: str|null, total_tokens: {input,output,cache_creation,cache_read}, history: []}` — `history` luôn là `[]`.
  - `/api/pipeline/aggregate` response: `{mode:"aggregate", total_sessions:N, total_calls:N, roster:[{role,display_name,call_count,session_count,latest_model,first_called_at,last_called_at,total_tokens,status,active_now}]}` sorted by `call_count DESC`.
  - Frontend cần filter `is_dispatcher=true` hoặc render riêng — không nên render Dispatcher giống subagent vì `history=[]` và không có `latest_description` từ agent event.
- **next_inputs**:
  - Usage endpoints: `GET /api/accounts/usage/active` + `GET /api/accounts/{acc_id}/usage` — response shape là `UsageInfo` JSON trực tiếp.
  - Aggregate endpoint: `GET /api/pipeline/aggregate?project=<slug>&window=<days>`.
  - Commit hash: sẽ điền sau khi commit xong bước này.

## Commit
- Hash: [điền sau git commit]
- Đã push: không (sẽ push sau khi điền hash)

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
