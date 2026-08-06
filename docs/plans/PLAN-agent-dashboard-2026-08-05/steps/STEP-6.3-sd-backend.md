---
step: "6.3"
name: "Track C Backend Sprint 3"
agent: "Senior Developer"
plan: "PLAN-agent-dashboard-2026-08-05"
status: done
started_at: "2026-08-06 14:30"
completed_at: "2026-08-06 15:09"
commit: "de4fbe8"
---

# STEP 6.3 — Track C Backend Sprint 3

## Nhiệm vụ
Implement toàn bộ backend Sprint 3: BUG-003 fix, FR-003 (ai-title), FR-002 (context_pct snapshot), FR-001 (chain endpoint).

## Đã làm

### BUG-003 — Fix "Invalid Date" started_at
- `parser.py`: Early-return `None` cho mọi dòng không có timestamp (ngoài `ai-title`). Fix trực tiếp tại nguồn phát sinh.
- `db.py` `upsert_session()`: Double-guard — skip khi `timestamp == ""`, log warning.
- `db.py` `_migrate_sprint3_columns()`: Cleanup migration idempotent `UPDATE sessions SET started_at = last_event_at WHERE started_at = '' OR started_at IS NULL` — chạy TRONG `init()` SAU tất cả ALTER TABLE.

### FR-003 — Tên session thân thiện
- `models.py` `ParsedLine`: Thêm 3 fields: `ai_title: Optional[str]`, `first_user_text: Optional[str]`, `is_meta: bool = False`.
- `parser.py`: Detect `type="ai-title"` → return `ParsedLine(is_meta=True, ai_title=data["aiTitle"])`. Detect `type="user"` → extract `first_user_text = text[:60]` từ block text đầu tiên (skip whitespace-only, skip non-text blocks).
- `db.py`: `update_title()` (luôn ghi đè, dùng cho ai_title), `update_title_if_null()` (chỉ set khi NULL, dùng cho user_text fallback, trả bool). Migration: cột `title TEXT`.
- `main.py` `_process_file()`: Khi `is_meta=True` → call `update_title()` + broadcast `session_title_changed` WS delta + `continue`. Sau `upsert_session` bình thường: nếu `first_user_text` → call `update_title_if_null()`, broadcast nếu updated=True.
- API: SELECT queries (`get_active_sessions`, `get_session_history`, `get_sessions_by_project`) đã include cột `title` — field flow tự nhiên qua `_row_to_session`.

### FR-002 — % Context window
- `config.py`: `MODEL_CONTEXT_WINDOW` dict (Sonnet5/Opus5/Fable5 = 1M; Haiku4.5/Sonnet4.6/Opus4.7 = 200K) + `DEFAULT_CONTEXT_WINDOW = 200_000` + `resolve_max_context(model: str) -> int` (exact match, không prefix match).
- `db.py` migration: 4 cột mới `last_input_tokens`, `last_cache_creation`, `last_cache_read`, `last_usage_at` (idempotent).
- `db.py` `upsert_session()`: Thêm 4 params optional `last_input_tokens`, `last_cache_creation_tokens`, `last_cache_read_tokens`, `last_usage_at`. Khi `last_usage_at is not None` → UPDATE riêng (ghi đè). Cumulative `token_*` vẫn UPDATE mọi lần như cũ.
- `db.py` `_row_to_session()`: Pop `last_input_tokens/last_cache_creation/last_cache_read`, tính `last_input_total`, `max_context = resolve_max_context(agent_type)`, `context_pct = round(last_total / max_ctx * 100, 1)`. Thêm 3 fields vào dict kết quả.
- `main.py`: Khi `input_tokens > 0` → truyền snapshot kwargs vào `upsert_session`. Token_update WS delta thêm `last_input_total`, `max_context`, `context_pct`.

### FR-001 — Pipeline view / Chain endpoint
- `db.py` `get_session_chain(conn, session_id)`: Query `events WHERE tool_name='Agent' ORDER BY ts ASC`. Parse `payload_json` (raw JSONL) để extract `subagent_type` + `description` từ content block. `_compute_step_status()`: last step + Running → `active`; tất cả khác → `done`. Return `{session_id, session_state, steps: [...]}` hoặc None nếu không tồn tại.
- `routes/sessions.py`: Endpoint `GET /api/sessions/{session_id}/chain` — 404 nếu session không tồn tại. **Route đặt TRƯỚC `/{session_id}` detail route** để tránh shadowing.

### Tests
- Cập nhật `test_parser.py`: fix 2 test bị ảnh hưởng bởi BUG-003 early-return (`test_parse_missing_fields_does_not_crash` → expect None; `test_raw_json_truncated_at_2000` → add timestamp).
- Tạo `test_parser_sprint3.py`: 19 tests — BUG-003 early-return, ai-title is_meta, first_user_text extraction.
- Tạo `test_db_sprint3.py`: 22 tests — migration idempotent, BUG-003 cleanup, update_title helpers, upsert_session snapshot, get_session_chain (steps/status/empty/404/active vs done), context_pct calculation.
- Tạo `test_config_sprint3.py`: 10 tests — resolve_max_context exact match, unknown model fallback, no prefix match.
- Tạo `test_sessions_sprint3.py`: 7 tests — /chain endpoint 200/404/empty/route-ordering via FastAPI TestClient + mock patch.
- **Kết quả: 170 tests pass (119 → +51 mới)**.
- Install `pytest-asyncio` (pyproject.toml đã có `asyncio_mode = "auto"` nhưng package chưa được cài).

### CODE-GRAPH
- Updated `code-graph/CODE-GRAPH.md` v1.5: module table backend, config env table, thay đổi gần đây.
- DOCX xuất OK. PDF fail non-blocking (LibreOffice không có sẵn).

## Artifact
- `tools/agent-dashboard/backend/agent_dashboard/config.py` — MODEL_CONTEXT_WINDOW + resolve_max_context
- `tools/agent-dashboard/backend/agent_dashboard/models.py` — ParsedLine + 3 Sprint 3 fields
- `tools/agent-dashboard/backend/agent_dashboard/parser.py` — ai-title, early-return, first_user_text
- `tools/agent-dashboard/backend/agent_dashboard/db.py` — migrations, title helpers, snapshot, chain query, SELECT
- `tools/agent-dashboard/backend/agent_dashboard/routes/sessions.py` — /chain endpoint
- `tools/agent-dashboard/backend/agent_dashboard/main.py` — is_meta handling, snapshot, WS deltas
- `tools/agent-dashboard/backend/tests/test_parser.py` — 2 tests updated
- `tools/agent-dashboard/backend/tests/test_parser_sprint3.py` — NEW (19 tests)
- `tools/agent-dashboard/backend/tests/test_db_sprint3.py` — NEW (22 tests)
- `tools/agent-dashboard/backend/tests/test_config_sprint3.py` — NEW (10 tests)
- `tools/agent-dashboard/backend/tests/test_sessions_sprint3.py` — NEW (7 tests)
- `code-graph/CODE-GRAPH.md` v1.5 + CODE-GRAPH.docx

## Quyết định quan trọng
- `ai-title` dòng: trả ParsedLine với `is_meta=True` thay vì `None` — để ingest loop có thể update title mà không cần read file lại.
- `last_*` snapshot dùng điều kiện `input_tokens > 0` (không check `msg_type == "assistant"`) — vì msg_type có thể là `tool_use` cho assistant message có content block tool_use, nhưng usage vẫn có.
- Route `/chain` đặt trước `/{session_id}` trong `sessions.py` — FastAPI resolve theo thứ tự khai báo.
- `pytest-asyncio` phải install thủ công dù pyproject.toml đã khai báo `asyncio_mode = "auto"`.

## Handoff Payload — bước sau đọc phần này

- **do_not_redo:**
  - Parser, DB migrations, chain endpoint đã hoàn chỉnh và test pass. Không modify lại các module này trong bước 6.5 review trừ khi có bug thật.
  - `_migrate_sprint3_columns` là idempotent — không cần chạy manual.
  - Route `/chain` đã đặt đúng thứ tự trước `/{session_id}` — không reorder.

- **watch_out:**
  1. `pytest-asyncio` phải được cài (`pip install pytest-asyncio`) để chạy test_db_sprint3.py — đã install trong session này nhưng pyproject.toml chưa list dependency test.
  2. `_row_to_session` pop các cột `last_input_tokens`, `last_cache_creation`, `last_cache_read` — nếu SELECT query nào thiếu các cột này sẽ raise KeyError. Đã cập nhật 3 SELECT queries nhưng `get_session_detail` dùng `SELECT *` nên không bị ảnh hưởng.
  3. Chain endpoint chỉ filter `tool_name='Agent'` — KHÔNG dùng `subagent_type IS NOT NULL` (sai vì có Agent call không có subagent_type).
  4. `context_pct` tính ở backend (`round(x, 1)`) — frontend chỉ format string, không tính lại.
  5. Frontend Track D (Bước 6.4 — Junior Developer) chạy song song, đã có các file staging từ session trước. Tech Lead review 6.5 cần verify BOTH tracks.

- **next_inputs:**
  - Commit hash: `de4fbe8`
  - Test output: `170 passed, 1 warning in 1.15s`
  - API mới: `GET /api/sessions/{id}/chain` → `{session_id, session_state, steps: [{step_index, subagent_type, subagent_display, description, started_at, status}]}`
  - WS delta mới: `session_title_changed {session_id, title, source: "ai_title"|"user_text"}`
  - WS delta mở rộng: `token_update` thêm `last_input_total`, `max_context`, `context_pct`
  - Response sessions thêm: `title` (nullable), `last_input_total`, `max_context`, `context_pct`
