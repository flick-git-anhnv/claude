---
task: agent-dashboard
created: 2026-08-05
updated: 2026-08-06 10:30
status: completed
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
| 3.5 | Fix 2 issue High từ UXR (UI-001 frontend, UI-002 backend) trước khi QA | Senior Developer ∥ Junior Developer | ✅ | `steps/STEP-3.5-fix-uxr-high.md` | 2026-08-06 10:30 |
| 3.6 | TL verify 2 fix + quyết định merge cuối trước QA | Tech Lead | ✅ | `steps/STEP-3.6-tl-verify-fix.md` | 2026-08-06 11:15 |

### Phase 4: Kiểm thử & Deploy
| # | Bước | Agent | Status | Step file | Hoàn thành lúc |
|---|------|-------|--------|-----------|-----------------|
| 4.1 | Thực thi test plan, log bug | QA Engineer | ✅ | `steps/STEP-4.1-qae-test.md` | 2026-08-06 08:52 |
| 4.2 | Sign-off chất lượng (P2 — QAL review nếu còn P0/P1 bug) | QA Lead | ✅ | `steps/STEP-4.2-qal-signoff.md` | 2026-08-06 14:30 |
| 4.3 | Deploy local (npm/uvicorn start, verify chạy được) | DevOps Engineer | ✅ | `steps/STEP-4.3-doe-deploy.md` | 2026-08-06 09:01 |
| 4.4 | Approve + smoke test cuối, verify dashboard live | DevOps Lead | ✅ | `steps/STEP-4.4-dol-approve.md` | 2026-08-06 15:10 |

### Phase 5: Sprint 2 — OAuth Support (Track A) + Agent Name/Activity + 2 View Modes (Track B)
| # | Bước | Agent | Status | Step file | Hoàn thành lúc |
|---|------|-------|--------|-----------|-----------------|
| 5.1 | TDD ADDENDUM Sprint 2 (§15–21 trong TDD v1.1) — data model OAuth, auto-refresh strategy, parser mở rộng, 2 view mode, task breakdown 12 task | Tech Lead | ✅ | `steps/STEP-5.1-tl-tdd-addendum.md` | 2026-08-06 16:00 |
| 5.2 | Track A: OAuth Account Support (migration v1→v2, activate flow swap credentials, auto-refresh scheduler, UI 2-tab, security banner) — S2-T01..T06 | Senior Developer | ✅ | `steps/STEP-5.2-sd-oauth.md` | 2026-08-06 09:53 |
| 5.3 | Track B: Parser mở rộng subagent_type/description, DB 3 column mới, mapping VN, API by-project, UI 2 view mode "Theo Agent"/"Theo Dự án" — S2-T07..T12 | Junior Developer | ✅ | `steps/STEP-5.3-jd-agent-view.md` | 2026-08-06 17:30 |
| 5.4 | security-audit-stride cho Track A (đụng credential nhạy cảm, ghi file `.credentials.json`) — BLOCK merge nếu Fail nhóm rủi ro cao | Tech Lead | ✅ | `steps/STEP-5.4-tl-security-audit.md` | 2026-08-06 10:02 |
| 5.5 | Code review cuối cả 2 track + verify-pr + merge decision | Tech Lead | ✅ | `steps/STEP-5.5-tl-review-sprint2.md` | 2026-08-06 10:30 |

> **Ghi chú Phase 5:** 5.2 ∥ 5.3 (song song). 5.4 chỉ chạy sau 5.2 (Track A). 5.5 chờ cả 5.2, 5.3, 5.4 xong. UXR/QA/Deploy sẽ mở Phase 6 sau khi 5.5 pass.

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
- (Không có blocker đang mở cho Sprint 2 — Sprint đã đóng)

## Backlog Sprint 3 (mở từ Bước 5.5)
- **BUG-003 (P2):** Session hiển thị "Bắt đầu: Invalid Date" — `started_at: ""` trả về từ `/api/sessions/by-project` + WS `agent_started`. Root cause: `parser.py:55` fallback `""` + state_manager snapshot cho legacy sessions. Fix pattern giống UI-001 (frontend safe-guard) HOẶC chuẩn hóa backend không trả `""`. Reproduce: `curl /api/sessions/by-project | jq '.[0].sessions[0].started_at'` → `""`.
- **FR-001 (feature request):** Redesign `AgentStatusPanel` thành pipeline view — chain PM→BA→…→SD/JD→TL→QA→Deploy xếp hàng, agent đang hoạt động highlight sáng (tên + việc + token), agent khác trong chain mờ. Cần UX design lại + xác định cách nhận diện "chain" (session_id gốc? parent-task marker trong JSONL?). Câu hỏi mở cho PM/UX ở kick-off Sprint 3.
- **DEBT-001 (Sprint 3):** Thắt lại `kind: AccountKind` thành required trong `Account`/`ActiveAccount` sau khi backend gửi `kind` trong WS delta `account_changed` + snapshot. Hiện đang optional (hotfix 5.5).
- **H-1 (đã fix Sprint 2, ghi để tra cứu):** OAuth race activate↔refresh — fix `b1866cc` bằng `refresh_lock` shared trong `activate_oauth_account`.
- ~~Bước 3.6 🛑 REQUEST CHANGES~~ — RESOLVED lần verify #2 (2026-08-06 11:15): `_parse_ts('')`→epoch, 52/52 tests, Running 244→3. Merge APPROVED → Bước 4.1 QAE.

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
| 2026-08-06 08:35 | Bước 3.6 🛑 REQUEST CHANGES — UI-001 APPROVED, UI-002 fix chưa xử lý edge case `last_event_at=''` (242/245 sessions Running sai sau restart). SD cần sửa `_parse_ts('')` → epoch + thêm test + optional cleanup migration. Chưa chuyển QA. | Tech Lead |
| 2026-08-06 11:15 | Bước 3.6 ✅ verify #2 PASS — `_parse_ts('')`→epoch OK, 52/52 tests, Running 244→3 sau restart uvicorn 7770, 347 Ended trong history. APPROVED merge → Bước 4.1 QAE. | Tech Lead |
| 2026-08-06 08:52 | Bước 4.1 ✅ — QAE thực thi 44 TC (39 Pass, 2 Fail, 2 Skip); UI-001/UI-002 regression PASS; BUG-001 DELETE 500 (P2), BUG-002 Duplicate name (P2); TC+BUG DOCX/PDF tạo xong | QA Engineer |
| 2026-08-06 14:30 | Bước 4.2 ✅ — QAL SIGN-OFF PASS: P0=0, P1=0, exit criteria met. 2 bug P2 tồn đọng (BUG-001, BUG-002) ghi known issues — deploy được phép. TC file cập nhật sign-off section. | QA Lead |
| 2026-08-06 09:01 | Bước 4.3 ✅ — start.bat tạo xong; server verify HTTP 200 + watcher_alive:true tại port 7770; DEPLOY-agent-dashboard.md + .docx tạo xong (PDF RPC fail non-blocking) | DevOps Engineer |
| 2026-08-06 16:00 | Bước 5.1 ✅ — TDD ADDENDUM v1.1 Sprint 2 viết xong (§15–21): Track A OAuth (data model v2, swap-and-invoke refresh, 12 task), Track B agent name+2 view mode; status plan → active để mở Sprint 2 | Tech Lead |
| 2026-08-06 17:30 | Bước 5.3 ✅ — Track B hoàn thành: parser subagent, DB 3 cột mới (idempotent), SUBAGENT_DISPLAY 19 agents, /by-project endpoint, WS subagent_changed, AgentCard badge, toggle 2 view mode + accordion; 85/85 tests, tsc+vite 0 errors; commit 5c23e75 | Junior Developer |
| 2026-08-06 15:10 | Bước 4.4 ✅ — DOL smoke test PASS (health/frontend/sessions/accounts 4/4); isolation OK; DEPLOY doc reviewed; **WF-FEATURE HOÀN THÀNH** — status → completed | DevOps Lead |
| 2026-08-06 09:53 | Bước 5.2 ✅ — Track A OAuth: migration v2, oauth_service.py (activate+scheduler+subprocess), routes, main scheduler wired, frontend 2-tab+badge+banner, 33 tests (118 total pass), claude -p verified exit 0; CODE-GRAPH v1.2 cập nhật | Senior Developer |
| 2026-08-06 10:30 | Bước 5.5 ✅ — TL review Sprint 2 PASS: 119/119 backend tests, tsc+vite build 0 lỗi (sau hotfix nới `kind?: AccountKind`), tích hợp thật 3/3 endpoint OK. Phát hiện BUG-003 (Invalid Date started_at, P2) + FR-001 (pipeline view) → Backlog Sprint 3. **Sprint 2 APPROVED merge, status plan → completed.** | Tech Lead |
| 2026-08-06 10:02 | Bước 5.4 ✅ — Security audit PASS có điều kiện: 1 High (H-1 race activate↔refresh, không share `refresh_lock`, mở BUG P1 Sprint 3), 3 Medium (auth endpoint, backup cleanup, XOR obfuscation), 2 Low (log không lộ token ✅, migration v1→v2 safe ✅); verified mid-swap restore bằng chạy thử thật. Không BLOCK merge Sprint 2 → sẵn sàng Bước 5.5. | Tech Lead |

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
**Cách đọc nhanh:** đọc MASTER trước → nếu cần chi tiết bước cụ thể mới mở step file tương ứng.
