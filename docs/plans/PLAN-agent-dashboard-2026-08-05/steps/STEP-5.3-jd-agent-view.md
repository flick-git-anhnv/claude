---
step: "5.3"
title: "Track B: Parser mở rộng subagent_type/description, DB 3 column mới, mapping VN, API by-project, UI 2 view mode"
agent: Junior Developer
status: done
created: 2026-08-06
completed_at: 2026-08-06 17:30
deps: ["5.1"]
---

# STEP 5.3 — Track B: Agent Name/Activity + 2 View Modes

## Nhiệm vụ

Implement S2-T07..T12 theo TDD §18:
- S2-T07: Parser trích `subagent_type` + `subagent_activity` từ `tool_use Agent`
- S2-T08: DB migrate 3 cột mới (idempotent) + UPDATE rule
- S2-T09: API `/api/sessions/by-project` + WS event `subagent_changed` + `current_subagent` trong sessions
- S2-T10: UI badge tên vai trò + activity trong AgentCard
- S2-T11: Toggle 2 view mode + view "Theo Dự án" (accordion `<details>`)
- S2-T12: Unit tests parser + slug decode + mapping

## Đã làm

### Backend

**`agent_dashboard/models.py`**
- Thêm `SUBAGENT_DISPLAY` dict (19 agents KZTEK)
- Thêm `get_subagent_display_name(slug)` — fallback title-case
- Thêm `decode_project_slug(slug)` — best-effort `c--...` → `C:\...`
- Thêm 2 optional field vào `ParsedLine`: `subagent_type`, `subagent_activity`

**`agent_dashboard/parser.py`**
- Trong content block loop: nếu `block.name == "Agent"` → trích `input.subagent_type` + `input.description`
- Các tool_use khác (Read/Bash/Edit/…) KHÔNG set subagent fields

**`agent_dashboard/db.py`**
- `_migrate_subagent_columns()`: check `PRAGMA table_info` → ALTER TABLE idempotent (3 cột)
- `init()`: gọi migration sau `executescript`
- `_row_to_session()`: pop 3 subagent cols → build `current_subagent` object hoặc `null`
- `get_active_sessions()`: SELECT bổ sung 3 cột mới
- `get_session_history()`: SELECT bổ sung 3 cột mới
- `update_session_subagent()`: UPDATE 3 cột cho 1 session
- `get_sessions_by_project()`: group sessions theo project slug, tính token_total, kèm decode

**`agent_dashboard/routes/sessions.py`**
- Thêm `GET /api/sessions/by-project` — đặt TRƯỚC `/{session_id}` để tránh FastAPI match sai

**`agent_dashboard/main.py`**
- Import `get_subagent_display_name`
- Sau `upsert_session`: nếu `parsed.subagent_type` → `update_session_subagent()` + broadcast `subagent_changed` WS delta

### Frontend

**`src/types/index.ts`**
- Thêm `CurrentSubagent` interface, `ProjectGroup`, `ViewMode`
- Update `Session` thêm `current_subagent?: CurrentSubagent | null`
- Thêm `subagent_changed` vào `DeltaEvent` union

**`src/state/wsReducer.ts`**
- `agent_started`: init `current_subagent: null`
- Thêm case `subagent_changed`: map session → update `current_subagent`

**`src/components/agents/AgentCard.tsx`**
- Activity row: nếu `current_subagent != null` → badge navy + activity text + relative time
- Fallback: hiển thị cũ "Hoạt động cuối: Xs trước"

**`src/components/agents/AgentStatusPanel.tsx`**
- View mode state từ `localStorage` (key `agent-dashboard.view-mode`)
- Pill toggle "Theo Agent" / "Theo Dự án" ở header
- `ByAgentView`: tách thành sub-component (giữ layout cũ)
- `ByProjectView`: group sessions → `<details>` accordion native HTML, tooltip slug gốc
- `decodeProjectSlug()`: mirror logic backend

### Tests

**`tests/test_parser.py`** (4 test cases mới):
- `test_parse_agent_tool_use_extracts_subagent` — happy path
- `test_parse_non_agent_tool_use_does_not_set_subagent` — Read/Bash không set
- `test_parse_agent_tool_use_missing_input_fields` — input empty không crash
- `test_parse_agent_tool_use_null_input` — input=null không crash

**`tests/test_models.py`** (12 test cases mới):
- Parametrized 19 agents SUBAGENT_DISPLAY
- Coverage check 19/19
- `get_subagent_display_name` known + fallback
- `decode_project_slug` Windows drive + double-dash + no-prefix + uppercase + empty

## Kết quả build/test

```
python -m pytest tests/ -q  →  85 passed, 1 warning in 0.36s
npx tsc -b                  →  0 errors (TSC_OK)
npx vite build              →  858 modules, built in 5.04s (0 errors)
```

## Artifact

- `tools/agent-dashboard/backend/agent_dashboard/models.py` — SUBAGENT_DISPLAY + helpers
- `tools/agent-dashboard/backend/agent_dashboard/parser.py` — subagent extraction
- `tools/agent-dashboard/backend/agent_dashboard/db.py` — migration + new functions
- `tools/agent-dashboard/backend/agent_dashboard/routes/sessions.py` — /by-project
- `tools/agent-dashboard/backend/agent_dashboard/main.py` — subagent_changed broadcast
- `tools/agent-dashboard/backend/tests/test_parser.py` — +4 tests
- `tools/agent-dashboard/backend/tests/test_models.py` — 12 tests (new file)
- `tools/agent-dashboard/frontend/src/types/index.ts` — extended types
- `tools/agent-dashboard/frontend/src/state/wsReducer.ts` — subagent_changed handler
- `tools/agent-dashboard/frontend/src/components/agents/AgentCard.tsx` — subagent badge
- `tools/agent-dashboard/frontend/src/components/agents/AgentStatusPanel.tsx` — 2 view modes
- Commit: `5c23e75`

## Handoff Payload — bước sau đọc phần này

- **do_not_redo:**
  - Migration idempotent đã xử lý (PRAGMA table_info guard) — KHÔNG chạy lại ALTER TABLE thủ công
  - `decode_project_slug` logic đã verify với slug thực tế `c--Users-nguye-Desktop-Claude-Git-claude` → `C:\Users-nguye-Desktop-Claude-Git-claude`
  - `/api/sessions/by-project` phải đứng TRƯỚC `/{session_id}` trong router — đã đúng thứ tự
  - 85/85 tests pass — KHÔNG sửa test cũ

- **watch_out:**
  - `kz-navy-very-light` KHÔNG tồn tại trong Tailwind config — đã thay bằng `hover:bg-gray-50`
  - `models.py` đã được linter Track A cập nhật thêm `AccountCreate` OAuth fields — KHÔNG revert
  - `current_subagent` là optional (`?: CurrentSubagent | null`) — AgentCard check null trước khi render badge
  - Accordion `<details>` native không có animation — per spec TDD §18.6, không thêm lib

- **next_inputs:**
  - Bước 5.5 (TL review): đọc diff commit `5c23e75`, check 4 watch_out trên
  - Bước 5.4 (security-audit Track A): độc lập với Track B, không cần chờ
  - Track B không đụng credentials/OAuth — KHÔNG cần security audit riêng
