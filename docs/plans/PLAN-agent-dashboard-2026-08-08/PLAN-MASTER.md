---
plan_id: PLAN-agent-dashboard-2026-08-08
title: "Agent Dashboard — FR mới phát sinh sau Sprint 6"
created: 2026-08-08
updated: 2026-08-08 15:55
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

---

## Lịch sử cập nhật

| Ngày | Phiên bản | Thay đổi | Agent |
|------|-----------|----------|-------|
| 2026-08-08 | v1.0 | Tạo plan; FR-006-dispatcher Done | senior-developer |
| 2026-08-08 | v1.1 | BUG-1/2/3 Done — 3 bugfixes: regression hasHistory + is_active project roster + shared display helpers | senior-developer |
