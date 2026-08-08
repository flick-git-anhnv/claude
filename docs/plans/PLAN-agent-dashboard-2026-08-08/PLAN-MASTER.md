---
plan_id: PLAN-agent-dashboard-2026-08-08
title: "Agent Dashboard — FR mới phát sinh sau Sprint 6"
created: 2026-08-08
updated: 2026-08-08 17:00
status: Active
---

# PLAN-agent-dashboard-2026-08-08 — Agent Dashboard FR phát sinh sau Sprint 6

Các feature request / bugfix phát sinh sau khi Sprint 6 (đã QA pass) được tổng kết.
Không có plan cũ — đây là plan theo dõi các thay đổi nhỏ lẻ phát sinh trong cùng session.

---

## Backlog / Phases & Steps

| # | Mô tả | Assignee | Status | Hoàn thành lúc |
|---|-------|----------|--------|----------------|
| FR-006-dispatcher | **Dispatcher card có nút "Xem lịch sử"** — backend build `history[]` từ non-Agent tool events (Read/Write/Bash…) của parent session; frontend bỏ điều kiện `!is_dispatcher` trong `hasHistory`, thêm nút vào `DispatcherNode`. Test: 6 test mới + 266 pytest pass. | senior-developer | ✅ | 2026-08-08 15:25 |
| BUG-1-history-regression | **Bug 1 — Regression hasHistory** (FR-006-dispatcher): khôi phục `hasHistory = is_dispatcher ? history.length>0 : call_count>=1`; HistoryPanel dùng `fmtTokenDisplay` (luôn "— tokens"), model placeholder "—" khi null cho non-dispatcher. Root cause: đổi sang `history.length>0` cho ALL đã ẩn nút của regular roles khi mock data có `history:[], call_count:1`. | senior-developer | ✅ | 2026-08-08 15:55 |
| BUG-2-project-active-role | **Bug 2 — Highlight role đang chạy trong Theo Dự án**: backend `get_pipeline_aggregate` thêm `is_active` vào từng `project_roster` item (backfill từ `active_roles` set sau khi build `active_agents`); `types/index.ts` thêm `is_active?: boolean` vào `ProjectRosterItem`; frontend `ProjectPipelineRow` dùng `sub.is_active` làm tín hiệu chính + fallback `runningInstances.length>0`. | senior-developer | ✅ | 2026-08-08 15:55 |
| BUG-3-display-consistency | **Bug 3 — Đồng bộ hiển thị 3 tab**: thêm `fmtTokenDisplay(n)` + `fmtModelShort(m)` vào `format.ts` (shared helpers); xóa `shortModel()` trùng lặp trong `AgentRosterItem` + `AggregatePipelineView`; tất cả `DoneSubagentNode`/`DoneSubagentPipelineNode`/`DispatcherPipelineNode`/`ActiveSubagentPipelineNode` dùng `fmtTokenDisplay` — luôn hiện "— tokens" khi zero thay vì để trống. | senior-developer | ✅ | 2026-08-08 15:55 |
| REFACTOR-db-split | **Refactor code quality (không phải feature/bugfix)** — tách `backend/agent_dashboard/db.py` (1598 dòng, gộp 6 nhóm trách nhiệm khác nhau) thành package `db/` gồm 6 module theo domain: `schema.py` (DDL+migrations+init), `cursors.py`, `sessions.py` (CRUD+row shaper+list/history/detail/by-project), `events.py` (write path), `chain.py` (`get_session_chain`+`_backfill_chain_results`+dispatcher history — module phức tạp nhất, mới sửa nhiều lần), `aggregate.py` (`get_pipeline_aggregate`+`get_token_summary`). `db/__init__.py` re-export tất cả symbol public — mọi caller `from .. import db as db_module` + test patch `agent_dashboard.db.X` vẫn hoạt động không đổi. Behavior/logic không đổi (pure move). Test: 266/266 pytest pass. Server restart OK, endpoint `/`, `/api/sessions/by-project`, `/api/pipeline/aggregate`, `/api/sessions/{id}/chain` đều 200 với payload đúng. | tech-lead | ✅ | 2026-08-08 16:30 |

---

## Lịch sử cập nhật

| Ngày | Phiên bản | Thay đổi | Agent |
|------|-----------|----------|-------|
| 2026-08-08 | v1.0 | Tạo plan; FR-006-dispatcher Done | senior-developer |
| 2026-08-08 | v1.1 | BUG-1/2/3 Done — 3 bugfixes: regression hasHistory + is_active project roster + shared display helpers | senior-developer |
| 2026-08-08 | v1.3 | REFACTOR-db-split ✅ — tách `db.py` 1598 dòng → package 6 module theo domain; re-export backward compatible; 266/266 pytest pass; server OK. Đây là refactor code quality (SRP), không phải feature/bugfix — không thay đổi behavior, chỉ chia nhỏ file để dễ maintain. Frontend: 3 file lớn (AggregatePipelineView 746 dòng / mockData 581 / AgentRosterItem 440) — mockData không cần tách (data thuần), 2 file kia có sub-component tách được nhưng effort vừa/cao và cấu trúc hiện tại vẫn coherent → ghi backlog, không làm trong session này. | tech-lead |
| 2026-08-08 | v1.2 | Fix 4 vấn đề mới user báo trên app live: (1) OAuth "Imported" bị http_429 khi poll `/api/oauth/usage` → UsageBar hiển thị dòng "⚠ Quá giới hạn lượt gọi..." rõ ràng thay vì 2 bar rỗng "5h --" "7d --" (root cause KHÔNG PHẢI bug code — thực sự Anthropic rate-limit token này; UI giờ thông báo rõ, không im lặng). (2) "Theo Session" hiện 2 dòng RUNNING trùng — root cause: `agent_started` WS delta được broadcast cho MỌI session mới kể cả subagent (is_subagent=True), frontend wsReducer nhét subagent vào state.sessions gốc; fix: `main.py` chỉ broadcast `agent_started` khi `not parsed.is_subagent`. (3) Dispatcher history quá chi tiết từng tool call — fix: `get_session_chain` dựng history từ user turns (parse payload_json events type=user, lọc tool_result), description = văn bản người dùng [:120] thay vì tool_name; test đổi từ tool events sang user event fixtures (6 test rewritten). (4) UI flicker: `wsReducer` giữ nguyên identity `sessions` array khi delta không match/không đổi (helper `mapIfChanged` + top-level short-circuit `nextSessions===state.sessions`); `AggregatePipelineView` cache `lastJsonStr` skip `setData` khi poll trả nội dung không đổi. Test: 266 pytest pass, 23 vitest pass, tsc clean, build OK. Server restart PID mới, `GET /`=200. | senior-developer |
| 2026-08-08 | v1.4 | Fix encoding tiếng Việt (mojibake) trong dispatcher history. Root cause: Python 3.10 trên Windows có locale.getpreferredencoding()='cp1252' → open() không encoding sẽ dùng cp1252, gây lone surrogates (via errors='surrogateescape') trong payload_json. Audit: tất cả file-reads đã dùng encoding="utf-8" tường minh hoặc binary mode. Thêm `_sanitize_text()` trong `db/chain.py` làm sạch surrogate cho dữ liệu cũ; `_extract_user_turn_text()` gọi sanitize trước return. Script re-ingest `scripts/reingest_recent_sessions.py` để fix data cũ. 21 test mới (287 pass total). Server restart PID mới, GET /=200, chain API trả tiếng Việt clean. | senior-developer |
