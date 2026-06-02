---
task: todo-app-csharp
workflow: WF-FEATURE
priority: P2
created: 2026-06-02
updated: 2026-06-02T22:30
status: completed
---

# PLAN: Xây dựng ứng dụng To-Do App C#

## Mô tả
Xây dựng ứng dụng To-Do App bằng C# (.NET), có đầy đủ chức năng quản lý công việc (tạo, sửa, xóa, đánh dấu hoàn thành), giao diện người dùng cơ bản, và có thể deploy được.

## Agent chain
PM → BA → UX → EM → PJM → TL → SD → JD → TL (review) → QAE → QAL → DOE → DOL

---

## Phase 1 — Phân tích & Thiết kế Sản phẩm

| # | Bước | Agent | Status | Artifact | Ghi chú |
|---|------|-------|--------|----------|---------|
| 1.1 | Thu thập yêu cầu, viết PRD cho To-Do App C# | Product Manager | ✅ | docs/prd/PRD-todo-app-csharp.md + .docx | |
| 1.2 | Chi tiết hóa user story, viết acceptance criteria | Business Analyst | ✅ | docs/user-stories/US-todo-app-csharp.md + .docx + .pdf | |
| 1.3 | Thiết kế mockup, wireframe, user flow | UI/UX Designer | ✅ | docs/design/DESIGN-todo-app-csharp.md + .docx + .pdf | |

## Phase 2 — Phân bổ Nguồn lực & Kỹ thuật

| # | Bước | Agent | Status | Artifact | Ghi chú |
|---|------|-------|--------|----------|---------|
| 2.1 | Estimate resource, quyết định priority, phân bổ team | Engineering Manager | ✅ | docs/planning/RESOURCE-todo-app-csharp.md + .docx + .pdf | CTO bỏ qua vì quy mô nhỏ |
| 2.2 | Lên sprint, timeline, task board | Project Manager | ✅ | docs/planning/SPRINT-todo-app-csharp-PLAN.md + .docx + .pdf | |
| 2.3 | Viết Technical Design Doc, chia task chi tiết | Tech Lead | ✅ | docs/tech-design/TDD-todo-app-csharp.md + .docx + .pdf | OQ1=Console, OQ2=JSON, OQ4=LocalAppData |

## Phase 3 — Lập trình

| # | Bước | Agent | Status | Artifact | Ghi chú |
|---|------|-------|--------|----------|---------|
| 3.1 | Code phần phức tạp (service layer, data access, architecture) | Senior Developer | ✅ | src/Domain+App+Infra, 39 tests passed | |
| 3.2 | Code phần CRUD/UI đơn giản theo spec | Junior Developer | ✅ | src/ConsoleUI/ (Screens+Components+Rendering, 54 tests pass) | |
| 3.3 | Code review cuối, merge decision | Tech Lead | ✅ | Review comment + APPROVE; code-graph/CODE-GRAPH.md+pdf; fix comment JsonFileRepository | 54 tests pass, Application coverage 93.97% |

## Phase 4 — Kiểm thử & Deploy

| # | Bước | Agent | Status | Artifact | Ghi chú |
|---|------|-------|--------|----------|---------|
| 4.1 | Thực thi test plan, log bug | QA Engineer | ✅ | docs/test-cases/TC-todo-app-csharp.md + .docx | 56 TC: 50P/2F/4B. BUG-001 P3 + BUG-002 P2 — cả 2 đã fix |
| 4.2 | Sign-off chất lượng, veto nếu còn P0/P1 | QA Lead | ✅ | docs/test-plans/TEST-PLAN-todo-app-csharp.md + .docx | CONDITIONAL SIGN-OFF — 0 P0/P1, AC-08 conditional |
| 4.3 | Deploy lên staging | DevOps Engineer | ✅ | src/TodoApp.ConsoleUI/README.md + .docx; publish/win-x64/TodoApp.ConsoleUI.exe (~64.6MB); docs/devops/DEPLOY-todo-app-csharp.md + .docx | Build Release 0 error 0 warning; 54/54 tests pass |
| 4.4 | Approve staging, verify smoke test, deploy production, monitor | DevOps Lead | ✅ | docs/devops/DEPLOY-todo-app-csharp.md (updated+signed), git tag v1.0.0 | 54/54 pass, PE32+ binary valid, APPROVED |

---

## Artifacts dự kiến
- docs/prd/PRD-todo-app-csharp.md + .docx + .pdf
- docs/user-stories/US-todo-app-csharp.md + .docx + .pdf
- docs/design/DESIGN-todo-app-csharp.md + .docx + .pdf
- docs/planning/RESOURCE-todo-app-csharp.md + .docx + .pdf
- docs/planning/SPRINT-todo-app-csharp-PLAN.md + .docx + .pdf
- docs/tech-design/TDD-todo-app-csharp.md + .docx + .pdf
- src/ (C# source code)
- tests/unit/, tests/integration/
- docs/test-plans/TEST-PLAN-todo-app-csharp.md + .docx + .pdf
- docs/test-cases/TC-todo-app-csharp.md + .docx + .pdf
- infra/, docs/devops/DEPLOY-todo-app-csharp.md + .docx + .pdf

---

## Lịch sử cập nhật
| Ngày | Bước | Ghi chú |
|------|------|---------|
| 2026-06-02 | Plan khởi tạo | User xác nhận OK |
| 2026-06-02 | Bước 2.2 hoàn thành | Project Manager tạo SPRINT-todo-app-csharp-PLAN.md — 3 sprints, 14 ngày |
| 2026-06-02 | Bước 2.3 hoàn thành | Tech Lead tạo TDD-todo-app-csharp.md (+docx+pdf). Quyết định OQ1=Console App, OQ2=JSON file, OQ4=%LOCALAPPDATA%. Layered architecture, interface contracts, task breakdown Sprint 1 (SD ~28h / JD ~19h) |
| 2026-06-02 | Bước 3.3 hoàn thành | Tech Lead code review S1-T018: APPROVE. Build 0 warning, 54 tests pass, Application coverage 93.97% (>80%). Fix 1 Suggestion (comment thừa). Tạo code-graph/CODE-GRAPH.md+pdf. Chuyển QA Engineer (4.1) |
| 2026-06-02 | Bước 4.3 hoàn thành | DevOps Engineer: Build Release self-contained exe PASS (64.6MB). Tạo README.md + DEPLOY-todo-app-csharp.md (+docx). Chuyển DevOps Lead (4.4) |
| 2026-06-02 | Bước 4.4 hoàn thành | DevOps Lead: APPROVED. Binary PE32+ valid (67.7MB), 54/54 tests pass, 0 errors. Git tag v1.0.0 tạo thành công. DEPLOY doc signed-off. WF-FEATURE COMPLETED. |
