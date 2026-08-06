---
task: agent-dashboard
created: 2026-08-05
updated: 2026-08-06 08:40
status: in-progress
workflow: WF-FEATURE
priority: P2
---

# PLAN MASTER: Agent Dashboard — Dashboard Web Local Realtime Quản Lý Claude Code Agents

> File này CHỈ chứa tổng quan + trạng thái. Chi tiết từng bước (mô tả đầy đủ, Handoff Log, artifact chi tiết) nằm ở `steps/STEP-[N.M]-[tên].md` tương ứng — xem cột "Step file" bên dưới.

## Mô tả
Xây dựng dashboard web local, realtime, để quản lý hệ thống Claude Code Agents của KZTEK. Dashboard hiển thị agent nào đang chạy/đã chạy làm gì, token usage theo agent/session (lưu lịch sử dài hạn để phân tích xu hướng), và cho phép chuyển đổi tài khoản/API key linh hoạt (bảo mật đơn giản, dùng cá nhân trên 1 máy).

## Nguồn yêu cầu
- Yêu cầu gốc: "Xây dựng dashboard web local, realtime, để quản lý hệ thống Claude Code Agents của KZTEK — hiển thị agent nào đang chạy/đã chạy làm gì, token usage theo agent/session (có lưu lịch sử dài hạn để phân tích xu hướng), và cho phép chuyển đổi tài khoản/API key linh hoạt (mức bảo mật đơn giản, dùng cá nhân trên máy này, không cần multi-user)."
- Workflow: WF-FEATURE — Tính năng mới
- Agent chain: PM → BA → UX → EM → [CTO ⏭️ P2/internal] → PJM → TL → SD ∥ JD → TL (review) → UXR → QAE → QAL → DOE → DOL

## Scope đã chốt
- Môi trường: local only (`c:\Users\nguye\Desktop\Claude-Git\claude`)
- Realtime: file-watch trên `~/.claude/projects/*/*.jsonl`, đẩy qua WebSocket (~1-2s độ trễ)
- Lưu trữ: SQLite local để lưu lịch sử dài hạn và phân tích xu hướng
- Bảo mật account: lưu danh sách account/API key trong file local có mã hoá nhẹ, không cần OS keychain hay multi-user
- CTO step: ⏭️ Skipped — P2, tool nội bộ, không đụng auth/payment/production DB schema

## Phases & Steps

> **Session isolation (CLAUDE.md §16.5):** Mỗi bước ⬜/🔄 PHẢI chạy tách session — LOCAL dùng `Agent` subagent, WEB dùng `RemoteTrigger`. Agent/trigger tự tạo/cập nhật step file riêng, commit+push, rồi cập nhật đúng 1 dòng status ở bảng dưới đây.

### Phase 1: Phân tích & Thiết kế Sản phẩm — ✅ HOÀN THÀNH TOÀN BỘ — Sẵn sàng chuyển Phase 2
| # | Bước | Agent | Status | Step file | Hoàn thành lúc |
|---|------|-------|--------|-----------|-----------------|
| 1.1 | Viết PRD — mục tiêu, user persona, feature list, non-goals | Product Manager | ✅ | `steps/STEP-1.1-pm-prd.md` | 2026-08-05 22:52 |
| 1.2 | Viết User Stories + Acceptance Criteria chi tiết | Business Analyst | ✅ | `steps/STEP-1.2-ba-user-stories.md` | 2026-08-05 23:30 |
| 1.3 | Thiết kế wireframe/design spec — layout dashboard, màn hình account | UI/UX Designer | ✅ | `steps/STEP-1.3-ux-design.md` | 2026-08-05 23:05 |
| 1.4 | Estimate resource, confirm priority P2, phân bổ team | Engineering Manager | ✅ | `steps/STEP-1.4-em-resource.md` | 2026-08-05 23:50 |
| 1.5 | CTO review kiến trúc | CTO | ⏭️ | `steps/STEP-1.5-cto-skip.md` | - |
| 1.6 | Lên sprint plan + task board | Project Manager | ✅ | `steps/STEP-1.6-pjm-sprint.md` | 2026-08-05 23:59 |

### Phase 2: Thiết kế Kỹ thuật
| # | Bước | Agent | Status | Step file | Hoàn thành lúc |
|---|------|-------|--------|-----------|-----------------|
| 2.1 | Technical Design Doc — stack, kiến trúc, API contract, DB schema, file-watcher design | Tech Lead | ✅ | `steps/STEP-2.1-tl-tdd.md` | 2026-08-06 00:15 |

### Phase 3: Triển khai
| # | Bước | Agent | Status | Step file | Hoàn thành lúc |
|---|------|-------|--------|-----------|-----------------|
| 3.1 | Code backend: file-watcher, WebSocket server, SQLite ingestion, account mgmt API | Senior Developer | ✅ | `steps/STEP-3.1-sd-backend.md` | 2026-08-05 23:37 |
| 3.2 | Code frontend: dashboard UI (agent list, token chart, account switcher), WebSocket client | Junior Developer | ✅ | `steps/STEP-3.2-jd-frontend.md` | 2026-08-05 23:59 |
| 3.3 | Code review + verify-pr + merge decision (SD + JD) | Tech Lead | ✅ | `steps/STEP-3.3-tl-code-review.md` | 2026-08-06 00:45 |
| 3.4 | UX/UI Review — chạy app thật, screenshot, đánh giá C1–C7 | UX/UI Reviewer | ✅ | `steps/STEP-3.4-uxr-review.md` | 2026-08-06 08:30 |
| 3.5 | Fix 2 issue High từ UXR (UI-001 frontend, UI-002 backend) trước khi QA | Senior Developer ∥ Junior Developer | 🔄 | `steps/STEP-3.5-fix-uxr-high.md` | - |

### Phase 4: Kiểm thử & Deploy
| # | Bước | Agent | Status | Step file | Hoàn thành lúc |
|---|------|-------|--------|-----------|-----------------|
| 4.1 | Thực thi test plan, log bug | QA Engineer | ⬜ | `steps/STEP-4.1-qae-test.md` | - |
| 4.2 | Sign-off chất lượng (P2 — QAL review nếu còn P0/P1 bug) | QA Lead | ⬜ | `steps/STEP-4.2-qal-signoff.md` | - |
| 4.3 | Deploy local (npm/uvicorn start, verify chạy được) | DevOps Engineer | ⬜ | `steps/STEP-4.3-doe-deploy.md` | - |
| 4.4 | Approve + smoke test cuối, verify dashboard live | DevOps Lead | ⬜ | `steps/STEP-4.4-dol-approve.md` | - |

## Artifacts dự kiến (tổng)
- [ ] `docs/prd/PRD-agent-dashboard.md` — Product Requirements Document
- [ ] `docs/prd/PRD-agent-dashboard.docx` + `.pdf`
- [ ] `docs/user-stories/US-agent-dashboard.md` — User Stories + AC
- [ ] `docs/design/DESIGN-agent-dashboard.md` — Wireframe + Design Spec
- [ ] `docs/planning/RESOURCE-agent-dashboard.md` — Resource estimate
- [ ] `docs/planning/SPRINT-agent-dashboard-01-PLAN.md` — Sprint plan
- [ ] `docs/tech-design/TDD-agent-dashboard.md` — Technical Design Doc
- [ ] `src/agent-dashboard/` — Source code (backend + frontend)
- [ ] `docs/test-cases/TC-agent-dashboard.md` — Test cases
- [ ] `docs/devops/DEPLOY-agent-dashboard.md` — Deploy checklist

## Blockers
Không có

## Quyết định / Ghi chú tổng
- CTO step (1.5) ⏭️ Skipped: P2, tool nội bộ, không đụng production auth/payment/DB schema — không đủ điều kiện WF-FEATURE Bước 5.
- Bước 3.1 và 3.2 chạy song song (∥) sau khi TDD được duyệt — SD phụ trách backend phức tạp (file-watcher, WebSocket, SQLite), JD phụ trách frontend (dashboard UI, WebSocket client).
- Stack kỹ thuật sẽ do TL quyết định ở Bước 2.1 — gợi ý ban đầu: Python/FastAPI (backend) + React hoặc vanilla HTML/JS (frontend), SQLite (storage).
- UXR (Bước 3.4) bắt buộc vì có UI dashboard.

## Lịch sử cập nhật
| Ngày | Cập nhật | Agent |
|------|----------|-------|
| 2026-08-05 | Plan tạo mới | task-planner |
| 2026-08-05 22:52 | Bước 1.1 ✅ — PRD viết xong, DOCX+PDF xuất tại `docs/prd/` | Product Manager |
| 2026-08-05 23:30 | Bước 1.2 ✅ — 8 User Stories F-01..F-08, DOCX tại `docs/user-stories/` | Business Analyst |
| 2026-08-05 23:05 | Bước 1.3 ✅ — Design spec 5 màn hình, 13 components, DOCX tại `docs/design/` | UI/UX Designer |
| 2026-08-05 23:50 | Bước 1.4 ✅ — Resource estimate: SD 7nd backend, JD 9.5nd frontend, Priority P2, DOCX tại `docs/planning/` | Engineering Manager |
| 2026-08-05 23:59 | Bước 1.6 ✅ — Sprint plan 1 sprint, 21 task, 47 SP, mốc 2026-08-29, DOCX tại `docs/planning/`; Phase 1 hoàn thành toàn bộ | Project Manager |
| 2026-08-06 00:15 | Bước 2.1 ✅ — TDD viết xong, chốt Python/FastAPI + Vite/React/TS, API contract + DB schema + task breakdown 21 task; DOCX tại `docs/tech-design/` (PDF fail RPC — DOCX OK) | Tech Lead |
| 2026-08-05 23:37 | Bước 3.1 ✅ — Backend implement đầy đủ: 12 modules, 47 tests pass, commit fecd37d | Senior Developer |
| 2026-08-05 23:59 | Bước 3.2 ✅ — Frontend implement đầy đủ: 44 files, 13 components, 4 pages, mock mode, build verified (tsc 0 errors, vite 858 modules), commit b868513 | Junior Developer |
| 2026-08-06 00:45 | Bước 3.3 ✅ — TL review PASS, fix 5 lệch schema mock↔backend + refactor mask_key, tích hợp thật port 7770 verify OK, commit b1c148f+affb0c6 | Tech Lead |
| 2026-08-06 08:30 | Bước 3.4 ✅ — UXR review xong (2 lần bị dừng giữa chừng, resume qua SendMessage + hoàn tất sổ sách thủ công): 6 issue (0 Critical, 2 High, 2 Medium, 2 Low). Thêm Bước 3.5 (fix High) trước khi vào QA | UX/UI Reviewer / Dispatcher |
| 2026-08-06 08:19 | Bước 3.5 🔄 — Backend UI-002 fix xong (commit ed84b69): initialize_from_db() re-evaluate stale state; 50/50 tests pass. Frontend UI-001 đang chạy song song (JD) | Senior Developer |
| 2026-08-06 08:40 | Bước 3.5 🔄 JD phần UI-001 xong — normalizeIso()+fmtDateShort() fix NaN bug Python microseconds; vitest setup, 20 tests pass; tsc+build 0 lỗi; lesson ghi vào react-web/; CODE-GRAPH cập nhật | Junior Developer |

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
**Cách đọc nhanh:** đọc MASTER trước → nếu cần chi tiết bước cụ thể mới mở step file tương ứng.
