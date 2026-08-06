---
step: 7.1
plan: ../PLAN-MASTER.md
agent: Senior Developer
status: done
completed_at: 2026-08-06 20:47
deps: []
---

# STEP 7.1 — Backend: token thật theo từng bước pipeline (roster)

## Input nhận
- Thiết kế từ Tech Lead (lịch sử chat): subagent transcript tại `<project>/<session-uuid>/subagents/agent-*.jsonl`, field `isSidechain: true`, `attributionAgent` (= subagent_type slug), `message.usage` là token thật của agent con.
- Endpoint `/chain` cần trả thêm `tokens_step` và roster structure thay cho flat steps.
- Commit trước: `0b2f132` (fix TokenAnalytics chart UI-003).

## Nhiệm vụ
1. Parser: trích `parent_session_id` và `attribution_agent` từ JSONL subagent.
2. DB: migration Sprint 4, update upsert_session, redesign get_session_chain → roster.
3. Endpoint `/chain` trả roster với total_tokens cộng dồn + history[] chi tiết từng lần.
4. 201 tests pass.

## Definition of Done
- [x] Parser trích đúng `parent_session_id` (folder trên `subagents/`) + `attribution_agent` (từ `attributionAgent` field)
- [x] DB migration idempotent, PRAGMA table_info guard, index `idx_sessions_parent_id`
- [x] Backfill retroactive: `parent_session_id` từ file_path, `attribution_agent` từ đọc JSONL
- [x] `get_session_chain` trả `roster[]`: 1 entry/vai trò, `total_tokens` cộng dồn, `history[]`, `call_count`, `latest_model`, `status` dựa trên child session state
- [x] 201 tests pass
- [x] Verify thật `/chain` session `973154ca` → 14 vai trò, token hợp lý

## Đã làm
- `models.py`: thêm `parent_session_id`, `attribution_agent` vào `ParsedLine`.
- `parser.py`: khi `is_subagent=True`, trích `parent_session_id = p.parent.parent.name`, `attribution_agent = data.get("attributionAgent")`.
- `db.py`:
  - `_migrate_sprint4_columns()`: ADD COLUMN idempotent, index, backfill path-based + đọc JSONL.
  - `_read_attribution_from_file()`: đọc tối đa 10 dòng đầu để lấy attributionAgent.
  - `upsert_session()`: nhận và lưu 2 trường mới vào INSERT.
  - `get_session_chain()`: thiết kế lại hoàn toàn → roster (OrderedDict gộp theo vai trò, match Nth child session theo thứ tự started_at ASC cho từng attribution_agent, SUM token từ sessions table).
  - Xóa `_compute_step_status()` không còn dùng.
  - `init()`: gọi `_migrate_sprint4_columns`.
- `main.py`:
  - `upsert_session()` call: truyền `parent_session_id`, `attribution_agent`.
  - `_startup_scan()`: đổi `glob("*/*.jsonl")` → `rglob("*.jsonl")` để pick up subagent transcripts.
- Tests:
  - `test_sprint4_token_step.py`: 15 test mới (parser, migration, roster, token join, status, multi-call).
  - `test_db_sprint3.py`: cập nhật 5 test chain từ `steps[]` → `roster[]` + thêm `_migrate_sprint4_columns` vào fixture.
  - `test_subagent_filter.py`: thêm migration vào fixture.

## Quyết định quan trọng
1. **Roster thay vì flat steps**: 1 entry/vai trò gộp mọi lần gọi (kể cả không liền kề như TL→SD→TL), total_tokens cộng dồn, history[] chi tiết. Ordered by first appearance.
2. **Token từ sessions table không từ token_usage**: `sessions.token_input/output/cache_*` đã là cumulative — không cần JOIN token_usage riêng, đơn giản và nhất quán hơn.
3. **status logic mới**: "active" = session Running + child session cuối của vai trò đó là Running (không chỉ dựa vào vị trí trong danh sách như cũ).
4. **result_summary defer**: Tech Lead yêu cầu thêm `result_summary` (từ tool_result của Agent call, xử lý sync/async). Tách thành follow-up commit ngay sau — commit hiện tại ổn định trước.
5. **Backfill attribution_agent = đọc file**: migration đọc tối đa 10 dòng JSONL/file, tìm `attributionAgent` — 40/53 subagent sessions backfilled thành công (13 còn None là sessions cũ từ trước khi transcript feature ổn định).

## Artifact
- `tools/agent-dashboard/backend/agent_dashboard/models.py`
- `tools/agent-dashboard/backend/agent_dashboard/parser.py`
- `tools/agent-dashboard/backend/agent_dashboard/db.py`
- `tools/agent-dashboard/backend/agent_dashboard/main.py`
- `tools/agent-dashboard/backend/tests/test_sprint4_token_step.py` (mới)
- `tools/agent-dashboard/backend/tests/test_db_sprint3.py` (cập nhật)
- `tools/agent-dashboard/backend/tests/test_subagent_filter.py` (cập nhật)

## Handoff Payload — bước sau đọc phần này
- do_not_redo: Migration Sprint 4 đã chạy, columns đã có trong DB, backfill đã xong. Không chạy lại migration hay re-parse JSONL.
- watch_out:
  - `/chain` endpoint trả `roster[]` (KHÔNG còn `steps[]` — cập nhật TypeScript types trước khi dùng).
  - 13/53 subagent sessions có `attribution_agent=None` (early sessions) → `tokens_step=null` trong history → UI phải handle null gracefully (không hiển thị 0, ẩn token row).
  - `total_tokens` trong roster = cộng dồn từ tất cả child sessions; nếu child session không match → không cộng vào (giữ 0 cho field đó).
  - `status: "active"` chỉ khi CÙNG lúc: session đang Running + child session cuối của vai trò đó là Running. Với session đang Running nhưng role cuối không có child → status="done".
  - `result_summary` chưa có trong response (defer) — JD Bước 7.2 không cần đợi field này.
- next_inputs:
  - API contract mới `/chain` response: `{session_id, session_state, roster: [{role, display_name, status, call_count, latest_description, latest_model, first_called_at, last_called_at, total_tokens: {input, output, cache_creation, cache_read}, history: [{call_index, started_at, description, model, tokens: {…}|null, status}]}]}`
  - Backend đang chạy port 7770: `curl http://localhost:7770/api/sessions/973154ca-dd2a-4b42-ae24-6bc8a2930a27/chain` để verify response thật
  - Commit hash: `0ae3bed`

## Commit
- Hash: 0ae3bed
- Đã push: không (branch research/skills-2026-08-05, ahead of origin by 6 commits)

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
