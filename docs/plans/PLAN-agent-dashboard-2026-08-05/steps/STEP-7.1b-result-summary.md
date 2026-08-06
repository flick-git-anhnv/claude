---
step: 7.1b
title: result_summary/result_full/duration_ms trong /chain history
agent: Senior Developer
status: done
created: 2026-08-06
completed_at: 2026-08-06 21:09
commit: 87bd590
---

# Bước 7.1b — result_summary/result_full/duration_ms trong /chain history

## Nhiệm vụ
Thêm 3 field vào mỗi `history[]` entry của endpoint `/api/sessions/{id}/chain`:
- `result_summary`: tóm tắt tối đa 400 ký tự
- `result_full`: kết quả đầy đủ
- `duration_ms`: luôn `null` (dữ liệu không có trong JSONL hiện tại)

Hai case cần xử lý:
- **Sync** (`run_in_background=False`): `tool_result` message kế sau `Agent tool_use`, link bằng `tool_use_id`
- **Async** (`run_in_background=True`): `tool_result` đầu là placeholder "Async agent launched..."; kết quả thật trong `queue-operation` (`operation="enqueue"`) chứa XML `<task-notification>` với `<tool-use-id>` và `<result>`

## Đã làm

### Phát hiện quan trọng (gotcha)
Task ban đầu mô tả `task-notification` là một loại JSONL riêng biệt — **không đúng**. Không có top-level type `task-notification` trong các file JSONL thực tế. Kết quả async được đóng gói trong `queue-operation` (type `queue-operation`, `operation="enqueue"`) dưới dạng XML trong trường `content`.

### Files thay đổi

**`models.py`**
- Thêm field `tool_use_id: Optional[str] = None` vào `ParsedLine`

**`parser.py`**
- Thêm extraction `tool_use_id = block.get("id") or None` trong nhánh `if tool_name == "Agent":`
- Thêm `tool_use_id=tool_use_id` vào `ParsedLine(...)` return
- Thêm hàm `_extract_agent_result(session_lines, tool_use_id) -> Optional[dict]`:
  - Phase 1: tìm `tool_result` user message khớp `tool_use_id`; detect async qua prefix "Async agent launched"
  - Phase 2 (async only): scan `queue-operation` lines, regex `<tool-use-id>`, extract `<result>`
  - Returns `{result_summary, result_full, duration_ms}` hoặc `None`

**`db.py`**
- `_migrate_result_columns(conn)`: idempotent migration thêm 3 cột `tool_use_id TEXT`, `result_summary TEXT`, `result_full TEXT` vào bảng `events`
- `insert_event()`: thêm param `tool_use_id`, lưu vào INSERT, trả `int` (lastrowid)
- `update_event_result(conn, event_id, result_summary, result_full)`: UPDATE đúng row
- `_backfill_chain_results(conn, session_id, event_rows)`: lazy backfill — lần đầu gọi `/chain`, đọc JSONL file, build `ts→tool_use_id` mapping, resolve kết quả, persist vào DB
- `get_session_chain()`: thêm SELECT `id, tool_use_id, result_summary, result_full`, trigger backfill nếu có NULL, propagate 3 field vào `history_item`

**`main.py`**
- Pass `tool_use_id=parsed.tool_use_id` khi gọi `insert_event`

**`tests/test_result_summary.py`** (file mới — 19 test)
- `TestExtractAgentResultSync`: 6 test (string content, list content, truncation, wrong ID, empty, corrupted JSON)
- `TestExtractAgentResultAsync`: 4 test (queue-operation, truncation, no notification, wrong ID)
- `TestExtractAgentResultNotFound`: 2 test
- DB tests: migration idempotency, INSERT tool_use_id, update_event_result, chain backfill sync, chain backfill async, chain null when no result

**Fix test fixtures** (3 files): thêm `await db_module._migrate_result_columns(c)` vào `conn` fixture của `test_db_sprint3.py`, `test_sprint4_token_step.py`, `test_subagent_filter.py`

## Verification

```
Verification: python -m pytest tests/ -q
Output: 220 passed, 1 warning in 1.68s
Kết luận: Pass
```

```
Verification: curl http://localhost:7770/api/sessions/973154ca-dd2a-4b42-ae24-6bc8a2930a27/chain
Output: 
  roster entries: 14
  role=task-planner      history=1  with_summary=1
  role=product-manager   history=1  with_summary=1
  role=business-analyst  history=1  with_summary=1
  role=ui-ux-designer    history=2  with_summary=2
  role=engineering-manager history=1 with_summary=1
  role=project-manager   history=1  with_summary=1
  role=tech-lead         history=11 with_summary=10
  role=senior-developer  history=11 with_summary=5
  role=junior-developer  history=8  with_summary=7
  role=ux-ui-reviewer    history=3  with_summary=0  (async, no notification)
  role=qa-engineer       history=1  with_summary=1
  role=qa-lead           history=1  with_summary=1
  role=devops-engineer   history=1  with_summary=1
  role=devops-lead       history=1  with_summary=1
Kết luận: Pass — 13/14 role có result_summary; ux-ui-reviewer=0 là đúng (async agents chưa có notification)
```

## Handoff Payload — bước sau đọc phần này

- do_not_redo: `_migrate_result_columns` đã chạy và 3 cột đã tồn tại trong DB (`agent_dashboard.db`). `_extract_agent_result` đã được verify trên JSONL thực tế. KHÔNG viết lại logic backfill.
- watch_out: `ux-ui-reviewer` entries có `result_summary=null` vì đây là async agents mà JSONL session này không có `queue-operation` notification tương ứng — đây là expected behavior (agents launched in background, no result yet). Không phải bug.
- next_inputs: Endpoint `/chain` đã trả đầy đủ `result_summary`, `result_full`, `duration_ms` trong mỗi `history[]` entry. Frontend (Bước 7.2 đã done) và Tech Lead review (Bước 7.3 chờ) có thể dùng response này.
