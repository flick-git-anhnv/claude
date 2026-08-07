---
task: agent-dashboard
created: 2026-08-05
updated: 2026-08-07 08:24
status: active
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

> **Ghi chú Phase 5:** 5.2 ∥ 5.3 (song song). 5.4 chỉ chạy sau 5.2 (Track A). 5.5 chờ cả 5.2, 5.3, 5.4 xong.

### Phase 6: Sprint 3 — BUG-003 + FR-001 (Pipeline view) + FR-002 (% context) + FR-003 (tên session)
| # | Bước | Agent | Status | Step file | Hoàn thành lúc |
|---|------|-------|--------|-----------|-----------------|
| 6.1 | TDD ADDENDUM Sprint 3 — xác minh field log thật (FR-003, BUG-003), thiết kế chain-identification cho pipeline view (FR-001), thiết kế backend snapshot usage lượt gần nhất + cache max_input_tokens (FR-002) | Tech Lead | ✅ | `steps/STEP-6.1-tl-tdd-addendum.md` | 2026-08-06 11:05 |
| 6.2 | Thiết kế wireframe pipeline view (FR-001) dựa trên chain-identification đã chốt | UI/UX Designer | ✅ | `steps/STEP-6.2-ux-pipeline-design.md` | 2026-08-06 11:45 |
| 6.3 | Track C Backend: fix BUG-003, thêm snapshot usage lượt gần nhất + cache Models API (FR-002), endpoint chain-grouping (FR-001) | Senior Developer | ✅ | `steps/STEP-6.3-sd-backend.md` | 2026-08-06 15:09 |
| 6.4 | Track D Frontend: tên session thân thiện (FR-003), hiển thị %context (FR-002), UI pipeline view theo design 6.2 (FR-001) | Junior Developer | ✅ | `steps/STEP-6.4-jd-frontend.md` | 2026-08-06 15:08 |
| 6.5 | Code review cuối + verify-pr + merge decision | Tech Lead | ✅ | `steps/STEP-6.5-tl-review-sprint3.md` | 2026-08-06 15:55 |
| 6.6 | UX/UI Review — pipeline view mới (thay đổi UI đáng kể) | UX/UI Reviewer | ✅ | `steps/STEP-6.6-uxr-review.md` | 2026-08-06 19:53 |

> **Ghi chú Phase 6:** 6.1 → 6.2 (chờ chain-identification chốt) → 6.3 ∥ 6.4 (song song) → 6.5 → 6.6.

### Phase 7: Sprint 4 — Token thật theo từng step pipeline + fix UI-003 (Output token chart)
| # | Bước | Agent | Status | Step file | Hoàn thành lúc |
|---|------|-------|--------|-----------|-----------------|
| 7.0 | Fix UI-003 — Output Tokens bị "nuốt" bởi Cache Read trên chart (tách 2 chart riêng) | Junior Developer | ✅ | `steps/STEP-7.0-jd-fix-ui003.md` | 2026-08-06 20:20 |
| 7.1 | Backend: parser lưu `parent_session_id`/`attribution_agent` cho session con (subagent transcript), DB join token thật, endpoint `/chain` trả `tokens_step` | Senior Developer | ✅ | `steps/STEP-7.1-sd-token-step.md` | 2026-08-06 20:47 |
| 7.1b | Follow-up: thêm `result_summary`/`result_full`/`duration_ms` vào mỗi `history[]` entry của `/chain` — sync (tool_result) + async (queue-operation XML) | Senior Developer | ✅ | `steps/STEP-7.1b-result-summary.md` | 2026-08-06 21:09 |
| 7.2 | Frontend: hiển thị token thật (input/output/cache) cho từng step trong PipelineCard/StepStation | Junior Developer | ✅ | `steps/STEP-7.2-jd-token-step-ui.md` | 2026-08-06 21:15 |
| 7.3 | Review cuối + verify-pr + merge | Tech Lead | ✅ | `steps/STEP-7.3-tl-review-sprint4.md` | 2026-08-06 21:35 |

> **Ghi chú Phase 7:** 7.0 độc lập, chạy song song mọi bước khác. 7.1 → 7.2 (frontend cần token_step API) → 7.3.

### Phase 8: Sprint 5 — Usage Display + BUG-004 + FR-004 Dispatcher Node + FR-005 Toggle Pipeline + BUG-005
| # | Bước | Agent | Status | Step file | Hoàn thành lúc |
|---|------|-------|--------|-----------|-----------------|
| 8.1 | TDD ADDENDUM Sprint 5: khảo sát CLI usage + root cause BUG-004 (state_manager, field available khi RUNNING) + thiết kế FR-004 (Dispatcher node) + thiết kế FR-005 (aggregate API + toggle state) | Tech Lead | ✅ | `steps/STEP-8.1-tl-tdd-sprint5.md` | 2026-08-06 22:50 |
| 8.2 | Wireframe FR-004 (node "Claude Dispatcher" — màu/icon/vị trí) + FR-005 (toggle 2 chế độ + aggregate view layout) — trước khi code | UI/UX Designer | ✅ | `steps/STEP-8.2-ux-wireframe-sprint5.md` | 2026-08-07 08:24 |
| 8.3 | Backend: usage_service + BUG-004 fix (state_manager) + FR-004 inject Dispatcher node vào /chain + FR-005 aggregate endpoint | Senior Developer | ⬜ | `steps/STEP-8.3-sd-backend-sprint5.md` | - |
| 8.4 | Frontend: UsageBar (AppHeader+AccountCard) + BUG-004 live card fix + FR-004 Dispatcher node UI + FR-005 toggle 2 chế độ + BUG-005 fix nút "Xem lịch sử" | Junior Developer | ⬜ | `steps/STEP-8.4-jd-frontend-sprint5.md` | - |
| 8.5 | Code review Sprint 5: pytest + tsc + tích hợp thật — verify cả 4 hạng mục (A/B/C/D) | Tech Lead | ⬜ | `steps/STEP-8.5-tl-review-sprint5.md` | - |
| 8.6 | UX/UI Review: Usage bars (AppHeader+AccountCard) + Dispatcher node style + Toggle 2 chế độ — đánh giá C1-C7 | UX/UI Reviewer | ⬜ | `steps/STEP-8.6-uxr-review-sprint5.md` | - |
| 8.7 | QA Smoke Test Sprint 5: 18 TC (8 usage + 3 BUG-004 + 3 FR-004 + 4 FR-005) + regression Sprint 1-4 | QA Engineer | ⬜ | `steps/STEP-8.7-qae-smoke-sprint5.md` | - |

> **Ghi chú Phase 8:** 8.1 → 8.2 (wireframe, deps TDD) → 8.3 ∥ KHÔNG song song 8.4 (JD cần schema + wireframe từ 8.2+8.3) → 8.4 (deps 8.2+8.3) → 8.5 (review cả 8.3+8.4) → 8.6 (UXR, bắt buộc vì đổi UI ở nhiều nơi) → 8.7 (QA smoke).

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

## Ghi chú bổ sung Phase 8 (phát sinh 2026-08-06 22:35, trong lúc TL đang chạy 8.1)
- **BUG-005 (P3, đã gộp vào 8.4):** Nút "Xem lịch sử" trên card agent trong Pipeline/Roster view chỉ hiện khi agent được gọi >1 lần (badge "x2"/"x3"...). Khi agent chỉ được gọi đúng 1 lần, nút "Xem lịch sử" KHÔNG hiện — user không xem lại được chi tiết lượt gọi đó. Kỳ vọng: nút vẫn hiện dù chỉ có 1 lần gọi, để mở xem chi tiết (input/output/token/result_summary) của lượt đó. Cần JD kiểm tra điều kiện render nút trong component roster item (nghi vấn: điều kiện `history.length > 1` thay vì `history.length >= 1`).

## Backlog Sprint 3 (mở từ Bước 5.5)
- **BUG-003 (P2):** Session hiển thị "Bắt đầu: Invalid Date" — `started_at: ""` trả về từ `/api/sessions/by-project` + WS `agent_started`. Root cause: `parser.py:55` fallback `""` + state_manager snapshot cho legacy sessions. Fix pattern giống UI-001 (frontend safe-guard) HOẶC chuẩn hóa backend không trả `""`. Reproduce: `curl /api/sessions/by-project | jq '.[0].sessions[0].started_at'` → `""`.
- **FR-001 (feature request):** Redesign `AgentStatusPanel` thành pipeline view — chain PM→BA→…→SD/JD→TL→QA→Deploy xếp hàng, agent đang hoạt động highlight sáng (tên + việc + token), agent khác trong chain mờ. Cần UX design lại + xác định cách nhận diện "chain" (session_id gốc? parent-task marker trong JSONL?). Câu hỏi mở cho PM/UX ở kick-off Sprint 3.
- **FR-002 (feature request):** Hiển thị % context window đã dùng/còn lại mỗi session — công thức xác minh: `(input+cache_creation+cache_read)` của lượt gọi GẦN NHẤT (không cộng dồn) ÷ `max_input_tokens` (Models API, không hardcode). Chi tiết PRD Q-FR-002.
- **FR-003 (feature request):** Thay session ID thô bằng tên dễ đọc cho session không có subagent_type (fallback hiện tại). Đề xuất dùng tin nhắn đầu tiên của user — CẦN xác minh field log thật trước khi code. Chi tiết PRD Q-FR-003.
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
| 2026-08-06 11:05 | Bước 6.1 ✅ — TDD ADDENDUM v1.2 Sprint 3 (§22–28): verified `ai-title` native field (FR-003), root cause BUG-003 tại parser.py:55 (fix backend guard + migration cleanup), chốt chain=1 session cha (FR-001) + endpoint `/api/sessions/{id}/chain`, snapshot last_* cột mới (FR-002) + giá trị tĩnh MODEL_CONTEXT_WINDOW; 8 task S3-T01..T08 chia SD (3nd) + JD (2.75nd); DOCX+PDF xuất OK; status plan → active mở Sprint 3 | Tech Lead |
| 2026-08-06 11:45 | Bước 6.2 ✅ — Wireframe Pipeline View: SessionCard v2 (title FR-003 + ContextBadge FR-002), PipelineCard (FR-001) với done/active stations scroll ngang, auto-scroll to active, fade gradient, chain dài tối đa 20+ bước; DESIGN-agent-dashboard.md section Sprint 3 appended; DOCX xuất OK (PDF RPC fail non-blocking) | UI/UX Designer |
| 2026-08-06 15:09 | Bước 6.3 ✅ — Track C Backend: BUG-003 fix (parser early-return + migration cleanup + double-guard), FR-003 (ai-title is_meta + first_user_text + update_title helpers + WS session_title_changed), FR-002 (MODEL_CONTEXT_WINDOW + resolve_max_context + snapshot last_* 4 cột + context_pct tính backend), FR-001 (GET /api/sessions/{id}/chain + get_session_chain); 170 tests pass (119→+51); commit de4fbe8 | Senior Developer |
| 2026-08-06 15:08 | Bước 6.4 ✅ — Track D Frontend: ContextBadge/StepStation/PipelineCard/SessionCard v2 (4 file mới), types Sprint 3, mock chain sess-001/003, interceptor chain endpoint, wsReducer Sprint 3 events; tsc 0 errors, vite build 861 modules; commit 6673d3a | Junior Developer |
| 2026-08-06 19:53 | Bước 6.6 ✅ — UXR Sprint 3: 0 Critical/High, 2 Medium (dangling connector wrap, fallback title), 1 Low (spec deviation scroll→wrap). Sprint 3 PASS sẵn sàng dùng. Report+DOCX tại `docs/ux-review/`. | UX/UI Reviewer |
| 2026-08-06 20:47 | Bước 7.1 ✅ — Backend Sprint 4: parser parent_session_id+attribution_agent, DB migration Sprint 4 (idempotent, backfill), get_session_chain → roster (14 vai trò, tech-lead 11 calls/9 matched, senior-dev 9 calls/7 matched), 201 tests pass. Commit 0ae3bed. result_summary defer → follow-up. | Senior Developer |
| 2026-08-06 21:15 | Bước 7.2 ✅ — Frontend Sprint 4: AgentRosterItem.tsx (NEW), PipelineCard redesign roster[], fmtTokensCompact, RosterResponse types, history panel inline. tsc 0 errors, vite 861 modules. Commit 53b2a18. | Junior Developer |
| 2026-08-06 22:00 | Phase 8 (Sprint 5) tạo mới — Usage Display feature: 6 bước (8.1–8.6), status plan → active | task-planner |
| 2026-08-06 22:30 | Phase 8 mở rộng: gộp BUG-004 + FR-004 + FR-005 vào Sprint 5 — 7 bước (8.1–8.7), thêm bước UX Designer (8.2 mới), đánh số lại SD/JD/TL/UXR/QAE thành 8.3–8.7, xóa mục Backlog Sprint 6 (đã gộp vào Sprint 5) | task-planner |
| 2026-08-06 22:50 | Bước 8.1 ✅ — TDD ADDENDUM Sprint 5 (§29–36, +490 dòng) viết xong: Phần A endpoint `GET api.anthropic.com/api/oauth/usage` (verified từ binary claude.exe), Phần B root cause BUG-004 (child agent_type=NULL + tokens=0 window 1-5s) + fix WS `chain_updated` + UX fallback, Phần C Dispatcher node prepend vào `/chain` (is_dispatcher flag), Phần D endpoint mới `/api/pipeline/aggregate` + localStorage toggle. 12 task chia SD 3nd (S5-T01..T06) + JD 3nd (S5-T07..T12). DOCX xuất OK (PDF RPC fail non-blocking). | Tech Lead |
| 2026-08-07 08:24 | Bước 8.2 ✅ — Wireframe Sprint 5 hoàn thành: Phần A UsageBar (AppHeader height 56→80px, AccountCard lazy fetch) + Phần C Dispatcher node (Navy bg, 🧠 icon, không pulse) + Phần D Toggle segment + AggregatePipelineView (table layout, sort call_count DESC, search + dropdown) + BUG-005 rule `!is_dispatcher && call_count >= 1`. DESIGN.md section Sprint 5 appended, DOCX OK (PDF RPC fail). | UI/UX Designer |
| 2026-08-06 21:35 | Bước 7.3 ✅ APPROVED — TL review Sprint 4: 220/220 pytest, tsc+vite build 0 errors, schema `/chain` khớp 100% backend↔frontend (roster + history{result_summary?,result_full?,duration_ms?}). Tích hợp thật port 7770 PASS 5/5: (a) UI-003 chart tách Input/Output rõ (output=12.96M visible), (b) roster 14 roles duplicates=[], (c) token+model đúng per role, (d) 36/45 history có result_summary (9 async chưa có tool_result — hành vi đúng), (e) không có session con `agent-xxx` trong list chính. **Sprint 4 APPROVED merge, PLAN → completed.** | Tech Lead |
| 2026-08-06 15:55 | Bước 6.5 ✅ APPROVED — TL review Sprint 3: 170/170 pytest, tsc+vite 0 errors. Phát hiện & fix 2 lệch schema: (1) `ChainStep.subagent_type/display/description` từ string → `string\|null` + StepStation null-safe; (2) **BUG lớn**: `events.payload_json` truncate 2000 chars làm hỏng chain endpoint trên session thật — thêm 2 cột `subagent_type/subagent_description` vào events table, pipe qua insert_event, get_session_chain đọc trực tiếp. Backfill 1013 events + 333 titles từ JSONL. Tích hợp thật PASS 4/4: BUG-003 (0 empty started_at) + FR-002 (ctx_pct 50.1%/78.8%, max_context 200K/1M theo model) + FR-003 (72/100 recent sessions có title) + FR-001 (32 steps, 14 subagent types thật trên session 973154ca). Merge APPROVED → chuyển Bước 6.6 UXR. | Tech Lead |

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
**Cách đọc nhanh:** đọc MASTER trước → nếu cần chi tiết bước cụ thể mới mở step file tương ứng.
