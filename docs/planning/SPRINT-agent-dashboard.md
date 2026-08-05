# SPRINT-1 Plan — Agent Dashboard | Status: Active

**Feature:** Agent Dashboard — Dashboard Web Local Realtime Quản Lý Claude Code Agents
**Sprint:** 1 (duy nhất — project nhỏ, 1 sprint full)
**Thời gian:** 2026-08-06 → 2026-08-29 (~17 ngày lịch / 12 ngày làm việc thực tế sau TDD)
**Sprint Goal:** Hoàn thành toàn bộ TDD → Code Backend ∥ Frontend → Review → UXR → QA → Deploy local
**Tham chiếu Plan:** `docs/plans/PLAN-agent-dashboard-2026-08-05/PLAN-MASTER.md`

---

## Thông tin Sprint

| Thuộc tính | Giá trị |
|-----------|---------|
| Ngày bắt đầu | 2026-08-06 (Thứ Tư) |
| Ngày kết thúc dự kiến | 2026-08-29 (Thứ Sáu) |
| Sprint Goal | Deliver Agent Dashboard chạy được trên local, đủ 4 màn hình chính, WebSocket realtime, account manager |
| Velocity giả định | **47 SP** (ước lượng từ capacity — project mới, không có historical data) |
| Cơ sở velocity | SD 100% × 10nd ≈ 20SP + JD 100% × 9.5nd ≈ 19SP + TL 40% × ~4.5nd ≈ 9SP + QA/DevOps ≈ 4SP/5SP buffer → tổng 47SP phù hợp capacity thực tế |
| Priority | P2 — tool nội bộ, không production user-facing |

---

## Team

| Role | Thành viên | Tỉ lệ | Scope trong sprint |
|------|-----------|-------|-------------------|
| Tech Lead | Tech Lead | 40% | TDD, code review, merge decision |
| Senior Developer | Senior Developer | 100% | Backend toàn bộ |
| Junior Developer | Junior Developer | 100% | Frontend toàn bộ |
| QA Engineer | QA Engineer | 50% | Test execution, bug log |
| QA Lead | QA Lead | 20% | Sign-off P0/P1 |
| DevOps Engineer | DevOps Engineer | 20% | Deploy local |
| DevOps Lead | DevOps Lead | 10% | Smoke test + approve |
| UX/UI Reviewer | UX/UI Reviewer | 20% | Review UI sau code xong |

---

## Sprint Backlog

> **Quy tắc song song (∥):** S1-T002..S1-T007 (SD backend) và S1-T008..S1-T015 (JD frontend) chạy **song song** sau khi S1-T001 (TDD) xong. JD dùng mock server trong giai đoạn parallel, tích hợp thật ở S1-T016 (TL review).

| Task ID | Mô tả | Assignee | Estimate | SP | Priority | Status | Phụ thuộc |
|---------|-------|----------|----------|----|----------|--------|-----------|
| S1-T001 | Viết Technical Design Doc — stack, kiến trúc, API contract, DB schema, file-watcher design | Tech Lead | 2nd | 4 | P1 | Todo | — |
| S1-T002 | Backend: project setup + cấu trúc (FastAPI/Python, virtual env, folder structure) | Senior Dev | 0.5nd | 1 | P1 | Todo | S1-T001 |
| S1-T003 | Backend: File-watcher + JSONL parser (watchdog, defensive parse, realtime ingest) | Senior Dev | 2nd | 4 | P1 | Todo | S1-T002 |
| S1-T004 | Backend: SQLite schema + ingestion layer (sessions, token_events, ORM, index) | Senior Dev | 1.5nd | 3 | P1 | Todo | S1-T002 |
| S1-T005 | Backend: WebSocket server — endpoint `/ws`, delta push, reconnect grace | Senior Dev | 1nd | 2 | P1 | Todo | S1-T003, S1-T004 |
| S1-T006 | Backend: Account Management API — CRUD `/accounts`, accounts.enc mã hóa nhẹ | Senior Dev | 1.5nd | 3 | P1 | Todo | S1-T002 |
| S1-T007 | Backend: Unit + integration tests (parser, SQLite, account CRUD, WS message format) | Senior Dev | 0.5nd | 1 | P2 | Todo | S1-T003, S1-T004, S1-T005, S1-T006 |
| S1-T008 | Frontend: project setup + routing (Vite + React, CSS variables từ design tokens) | Junior Dev | 0.5nd | 1 | P1 | Todo | S1-T001 |
| S1-T009 | Frontend: Layout toàn cục — AppHeader, SidebarNav, WebSocketStatus | Junior Dev | 1.5nd | 3 | P1 | Todo | S1-T008 |
| S1-T010 | Frontend: Màn hình Agent Status — AgentCard, AgentStatusPanel, auto-refresh | Junior Dev | 1.5nd | 3 | P1 | Todo | S1-T008 |
| S1-T011 | Frontend: Màn hình Token Analytics — TokenBarChart, SummaryCard (3 card), filter bar | Junior Dev | 2nd | 4 | P1 | Todo | S1-T008 |
| S1-T012 | Frontend: Màn hình Session History — SessionTable, sort + pagination, date filter | Junior Dev | 1nd | 2 | P2 | Todo | S1-T008 |
| S1-T013 | Frontend: Màn hình Account Manager — AccountCard, AddAccountPanel, ConfirmDialog | Junior Dev | 2nd | 4 | P1 | Todo | S1-T008 |
| S1-T014 | Frontend: Global utility components — ToastNotification, BannerAlert | Junior Dev | 0.5nd | 1 | P2 | Todo | S1-T008 |
| S1-T015 | Frontend: WebSocket client integration — connect `/ws`, delta state update realtime | Junior Dev | 0.5nd | 1 | P1 | Todo | S1-T009, S1-T010 |
| S1-T016 | Code review toàn bộ SD + JD — verify-pr checklist, approve + merge decision | Tech Lead | 1.5nd | 3 | P1 | Todo | S1-T007, S1-T015 |
| S1-T017 | UX/UI Review — chạy app thật, chụp screenshot, đánh giá C1–C7 | UX/UI Reviewer | 0.5nd | 1 | P1 | Todo | S1-T016 |
| S1-T018 | QA: Thực thi test plan, log bug | QA Engineer | 1.5nd | 3 | P1 | Todo | S1-T017 |
| S1-T019 | QA Lead: Sign-off (review nếu còn P0/P1 bug) | QA Lead | 0.5nd | 1 | P1 | Todo | S1-T018 |
| S1-T020 | Deploy local — start script uvicorn + vite build, verify chạy được | DevOps Engineer | 0.5nd | 1 | P1 | Todo | S1-T019 |
| S1-T021 | Smoke test cuối + approve — DevOps Lead verify dashboard live | DevOps Lead | 0.5nd | 1 | P1 | Todo | S1-T020 |

**Tổng SP sprint: 47 SP** | P1: 38 SP | P2: 9 SP

---

## Timeline dự kiến

```
Tuần 1 (08-06 ~ 08-07):
  S1-T001 — TDD (Tech Lead, 2nd) → done 08-07

Tuần 1-2 song song (08-08 ~ 08-21):
  S1-T002..T007 — Backend (Senior Dev, 7nd) → done ~08-18
  S1-T008..T015 — Frontend (Junior Dev, 9.5nd) → done ~08-21

Tuần 3 (08-22 ~ 08-25):
  S1-T016 — TL Code Review (1.5nd) → done ~08-25
  S1-T017 — UXR (0.5nd, song song hoặc ngay sau T016) → done ~08-25

Tuần 3-4 (08-26 ~ 08-29):
  S1-T018 — QA (1.5nd) → done ~08-27
  S1-T019 — QAL sign-off (0.5nd) → done ~08-28
  S1-T020..T021 — Deploy + Smoke (1nd) → done ~08-29
```

**Mốc hoàn thành dự kiến: 2026-08-29**

---

## Dependencies quan trọng

| Dependency | Mô tả | Rủi ro |
|-----------|-------|--------|
| S1-T001 → T002..T008 | SD và JD PHẢI chờ TDD được duyệt — KHÔNG bắt đầu code khi chưa có TDD | Cao — blocker toàn sprint nếu TDD kéo dài |
| S1-T003 trước T005 | File-watcher và JSONL parser phải xong trước khi viết WebSocket push | Trung |
| S1-T007 + T015 trước T016 | TL chỉ review khi cả backend và frontend đã xong + verify-pr pass | Trung |
| JD dùng mock data | Trong giai đoạn parallel, JD dùng MSW hoặc json-server mock — KHÔNG đợi SD xong | Thấp — được thiết kế sẵn |

---

## Scope bị đẩy ra ngoài sprint

| Item | Lý do |
|------|-------|
| Multi-user support | Scope đã loại từ PRD — tool cá nhân 1 máy |
| OS keychain integration | Chấp nhận mã hóa nhẹ (accounts.enc) — đủ cho local personal tool |
| Dark mode | Không có trong design spec hiện tại |
| Export CSV/report | Out of scope MVP |

---

## Rủi ro sprint

| Rủi ro | Mức độ | Mitigation |
|--------|--------|-----------|
| TDD kéo dài > 2nd, unblock SD/JD muộn | Trung | TL ưu tiên TDD là P1 đầu sprint |
| File-watcher Windows performance (watchdog) | Thấp–Trung | SD test sớm ở T003, fallback polling 2s |
| TokenBarChart (Recharts) phức tạp hơn dự kiến | Thấp | JD làm T011 sớm, escalate TL nếu blocked |
| Sprint miss deadline > 20% | Thấp | JD có thể drop T012 (Session History) và T014 (Toast/Banner) vì là P2 |

---

## Definition of Done

### P0/P1 Done:
- [ ] TDD được Tech Lead duyệt trước khi SD/JD code
- [ ] Backend chạy được: file-watcher nhận event, WebSocket push delta, account CRUD hoạt động
- [ ] Frontend load được 4 màn hình chính, WebSocket connect realtime
- [ ] Code review pass verify-pr checklist
- [ ] UXR đánh giá C1–C7 không có blocking issue
- [ ] QA thực thi test plan, không còn P0/P1 bug
- [ ] QA Lead sign-off

### QA sign-off:
- [ ] Smoke test pass toàn bộ happy path (agent status, token chart, session history, account switch)
- [ ] Không có P0/P1 bug còn mở

### Deploy:
- [ ] `uvicorn` + `vite build` start thành công trên local
- [ ] Dashboard accessible tại `http://localhost:PORT`

### Demo xong:
- [ ] Demo ngắn cho user: realtime agent card update, token chart render, account switch

---

## Task Board

### TODO
- S1-T001 Tech Lead: Viết TDD
- S1-T002 Senior Dev: Backend setup
- S1-T003 Senior Dev: File-watcher + JSONL parser
- S1-T004 Senior Dev: SQLite schema + ingestion
- S1-T005 Senior Dev: WebSocket server
- S1-T006 Senior Dev: Account API
- S1-T007 Senior Dev: Backend tests
- S1-T008 Junior Dev: Frontend setup
- S1-T009 Junior Dev: Layout toàn cục
- S1-T010 Junior Dev: Màn hình Agent Status
- S1-T011 Junior Dev: Màn hình Token Analytics
- S1-T012 Junior Dev: Màn hình Session History
- S1-T013 Junior Dev: Màn hình Account Manager
- S1-T014 Junior Dev: Global utility components
- S1-T015 Junior Dev: WebSocket client integration
- S1-T016 Tech Lead: Code Review + merge
- S1-T017 UX/UI Reviewer: UXR review
- S1-T018 QA Engineer: Test execution
- S1-T019 QA Lead: Sign-off
- S1-T020 DevOps Engineer: Deploy local
- S1-T021 DevOps Lead: Smoke test + approve

### IN PROGRESS
_(trống)_

### REVIEW
_(trống)_

### DONE
_(trống)_

---

## Phê duyệt

| Role | Người | Trạng thái |
|------|-------|-----------|
| Product Manager | Product Manager | ✅ Đã duyệt (PRD/US đã confirm) |
| Tech Lead | Tech Lead | ⬜ Cần duyệt TDD trước khi code bắt đầu |
| QA Lead | QA Lead | ⬜ Confirm testability sau khi có TDD |
| Project Manager | Project Manager | ✅ Sprint plan được chốt — 2026-08-05 |

---

## Lịch sử cập nhật

| Ngày | Phiên bản | Thay đổi | Agent |
|------|-----------|---------|-------|
| 2026-08-05 | v1.0 | Sprint plan khởi tạo — 21 task, 47 SP, mốc 2026-08-29 | Project Manager |
