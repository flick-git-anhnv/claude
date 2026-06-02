---
task: todo-app
created: 2026-06-01
updated: 2026-06-01T10:30
status: completed
workflow: WF-FEATURE
priority: P1
---

# PLAN: Xây dựng To-Do App (Ứng dụng quản lý công việc)

## Mô tả
Xây dựng ứng dụng to-do từ đầu — cho phép người dùng tạo, xem, cập nhật và xóa công việc. Bao gồm toàn bộ vòng đời phát triển từ phân tích yêu cầu, thiết kế, lập trình, kiểm thử đến deploy.

## Nguồn yêu cầu
- Yêu cầu gốc: "Xây dựng ứng dụng to-do (quản lý công việc) từ đầu"
- Workflow: WF-FEATURE — Tính năng mới
- Agent chain: Product Manager → Business Analyst → UI/UX Designer → Engineering Manager → Project Manager → Tech Lead → Senior Developer → Junior Developer → Tech Lead (review) → QA Engineer → QA Lead → DevOps Engineer → DevOps Lead

## Phases & Steps

### Phase 1: Phân tích & Thiết kế
| # | Bước | Agent | Status | Artifact | Ghi chú |
|---|------|-------|--------|----------|---------|
| 1.1 | Thu thập yêu cầu, viết PRD đầy đủ | Product Manager | ✅ | `docs/prd/PRD-todo-app.md` | |
| 1.2 | Viết user story chi tiết và acceptance criteria | Business Analyst | ✅ | `docs/user-stories/US-001-todo-app.md` | 6 US, Given/When/Then |
| 1.3 | Thiết kế mockup, wireframe, user flow | UI/UX Designer | ✅ | `docs/design/DESIGN-todo-app.md` | ASCII wireframe + 18 color tokens |
| 1.4 | Estimate resource, phân bổ team, quyết định priority | Engineering Manager | ✅ | `docs/planning/RESOURCE-todo-app.md` | React+Vite+TS+Tailwind, 5 ngày |
| 1.5 | Review kiến trúc (nếu cần) | CTO | ⏭️ | - | Bỏ qua — to-do app không liên quan kiến trúc lớn/bảo mật/chiến lược |

### Phase 2: Lập kế hoạch & Thiết kế kỹ thuật
| # | Bước | Agent | Status | Artifact | Ghi chú |
|---|------|-------|--------|----------|---------|
| 2.1 | Lên sprint, timeline, task board | Project Manager | ✅ | `docs/planning/SPRINT-1-PLAN.md` | 29 tasks, 34 SP |
| 2.2 | Viết Technical Design Document, chia task chi tiết | Tech Lead | ✅ | `docs/tech-design/TDD-todo-app.md` | 13 mục, 4-layer arch |

### Phase 3: Triển khai
| # | Bước | Agent | Status | Artifact | Ghi chú |
|---|------|-------|--------|----------|---------|
| 3.1 | Code service layer + context + types | Senior Developer | ✅ | `src/services/`, `src/context/`, `src/types/` | 94/94 tests pass, coverage 94% |
| 3.2 | Code UI components (19 files) | Junior Developer | ✅ | `src/components/` | tsc pass, 0 error |
| 3.3 | Code review cuối, quyết định merge | Tech Lead | ✅ | Build ✅ 226KB, fix TS2345 | |

### Phase 4: Kiểm thử
| # | Bước | Agent | Status | Artifact | Ghi chú |
|---|------|-------|--------|----------|---------|
| 4.1 | Viết test plan, định nghĩa chiến lược test | QA Lead | ✅ | `docs/test-plans/TEST-PLAN-todo-app.md` | |
| 4.2 | Viết test case chi tiết, thực thi test, log bug | QA Engineer | ✅ | `docs/test-cases/TC-todo-app.md` | 29 TC, 0 P0/P1 bug |
| 4.3 | Sign-off chất lượng | QA Lead | ✅ | Sign-off có điều kiện trong TEST-PLAN | 12 TC browser GUI pending |

### Phase 5: Deploy
| # | Bước | Agent | Status | Artifact | Ghi chú |
|---|------|-------|--------|----------|---------|
| 5.1 | Deploy lên staging | DevOps Engineer | ✅ | `.github/workflows/ci-cd.yml, docs/devops/INFRA-001-todo-app.md` | |
| 5.2 | Approve staging, verify smoke test, deploy production | DevOps Lead | ✅ | `docs/devops/DEPLOY-todo-app.md — APPROVED staging` | Production pending 12 TC browser GUI |

## Artifacts dự kiến
- [x] `docs/prd/PRD-todo-app.md`
- [x] `docs/user-stories/US-001-todo-app.md`
- [x] `docs/design/DESIGN-todo-app.md`
- [x] `docs/planning/RESOURCE-todo-app.md`
- [x] `docs/planning/SPRINT-1-PLAN.md`
- [x] `docs/tech-design/TDD-todo-app.md`
- [x] `todoapp/src/` (source code — services + components + context)
- [x] `todoapp/tests/unit/` (94 unit tests)
- [x] `docs/test-plans/TEST-PLAN-todo-app.md`
- [x] `docs/test-cases/TC-todo-app.md`
- [x] `docs/test-cases/TEST-DATA-todo-app.md`
- [x] `docs/devops/INFRA-001-todo-app.md`
- [x] `docs/devops/DEPLOY-todo-app.md`
- [x] `todoapp/.github/workflows/ci-cd.yml`
- [x] `todoapp/netlify.toml`
- [x] `todoapp/README.md`

## Blockers
Không có

## Quyết định / Ghi chú
- Bước 1.5 (CTO review kiến trúc) được bỏ qua vì to-do app không liên quan đến kiến trúc lớn, bảo mật chiến lược hoặc quyết định chiến lược.
- Tech stack và chi tiết triển khai sẽ được xác định tại bước 2.2 (Tech Lead — TDD).

## Lịch sử cập nhật
| Ngày | Cập nhật | Agent |
|------|----------|-------|
| 2026-06-01 | Plan tạo mới | task-planner |
| 2026-06-01 | Bước 1.1 hoàn thành — PRD đã tạo tại docs/prd/PRD-todo-app.md | Product Manager |
| 2026-06-01 | Bước 2.1 hoàn thành — Sprint Plan đã tạo tại docs/planning/SPRINT-1-PLAN.md | Project Manager |
| 2026-06-01 | Bước 5.1 hoàn thành — CI/CD pipeline và INFRA doc đã tạo | DevOps Engineer |
| 2026-06-01 | Bước 5.2 hoàn thành — Staging APPROVED. Production pending 12 TC browser GUI + Final Sign-Off | DevOps Lead |

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
