---
task: PLAN-agent-dashboard-autofailover-2026-08-09
created: 2026-08-09
updated: 2026-08-09 22:32
status: planning
workflow: WF-FEATURE
priority: P1
---

# PLAN MASTER: Agent Dashboard v2 — Auto-Failover Anthropic (Xoay Tài Khoản Tự Động)

> File này CHỈ chứa tổng quan + trạng thái. Chi tiết từng bước (mô tả đầy đủ, Handoff Log, artifact chi tiết) nằm ở `steps/STEP-[N.M]-[tên].md` tương ứng — xem cột "Step file" bên dưới.

> **Lịch sử scope:**
> - v2.0 (2026-08-09): hiểu nhầm "Multi-User" là nhiều người khác nhau → thiết kế Auth/RBAC. Đã sửa.
> - v2.1 (2026-08-09): scope correction đúng (1 máy, 1 người, nhiều account AI). Vẫn giả định OpenAI vào Vault.
> - v2.2 (2026-08-09): Sau spike kỹ thuật TL: (1) Loại OpenAI hoàn toàn; (2) Loại Antigravity IDE (không khả thi kỹ thuật — DPAPI/SQLite); (3) Loại Gemini Advanced; (4) Vault thu gọn: "Gemini CLI Vault" — piggyback OAuth đọc `~/.gemini/oauth_creds.json`.
> - **v2.3 (2026-08-09) — FINAL:** Google đã ngừng hỗ trợ OAuth cá nhân cho Gemini CLI (lỗi: "This client is no longer supported for Gemini Code Assist for individuals — migrate to Antigravity suite"). Cả 2 hướng Gemini piggyback đều chết. User quyết định: "Tạm thời xây dựng luồng cho nhiều tài khoản Claude trước". **Scope cuối cùng: CHỈ Auto-Failover Anthropic.** Gemini + OpenAI vào Backlog tương lai (Sprint 8+).

## Mô tả

Mở rộng Agent Dashboard v1 (đã có Account Manager Anthropic) để thêm **Auto-Failover tự động**: khi account Anthropic đang active bị 429/hết quota (5h/7d), tự động hot-swap sang account Anthropic khác trong chuỗi ưu tiên đã cấu hình — Claude Code CLI không bị gián đoạn. Khi hết toàn bộ account: tự động chờ và retry khi quota reset.

**Scope FINAL v2.3 — CHỈ gồm:**
- **Auto-Failover Anthropic-to-Anthropic:** Failover engine + monitoring + hot-swap credential < 100ms + failover chain config + wait-and-retry khi hết toàn bộ quota + log đầy đủ + indicator trực quan.
- **Backward compat với v1:** Mọi tính năng Sprint 1–6 tiếp tục hoạt động sau upgrade.

**Scope KHÔNG bao gồm (đã chốt):**
- Gemini CLI Vault: Google chặn OAuth cá nhân — không thể piggyback. Antigravity IDE cũng không khả thi (DPAPI). Chuyển vào Backlog tương lai.
- OpenAI: chưa nghiên cứu, user quyết định làm sau. Chuyển vào Backlog tương lai.
- Multi-user/multi-tenant/Auth/RBAC — đã xác nhận KHÔNG cần
- Runaway Loop Guard, Ollama, MCP Manager, Chat Playground, Webhook, Export — backlog riêng

## Nguồn yêu cầu

- Yêu cầu gốc: User xác nhận scope v2.3 final: chỉ Auto-Failover Anthropic
- PRD: `docs/prd/PRD-agent-dashboard-autofailover.md` v2.3 (scope cuối cùng)
- Plan Sprint 1–6 hiện tại: `docs/plans/PLAN-agent-dashboard-2026-08-05/` và `docs/plans/PLAN-agent-dashboard-2026-08-08/` (đã Done)
- Workflow: WF-FEATURE
- Agent chain: PM → BA → UX → EM → PJM → TL → SD/JD → TL review → [UXR] → QA → QAL → DOE → DOL

## Phases & Steps

> **Session isolation (CLAUDE.md §16.5):** Mỗi bước ⬜/🔄 PHẢI chạy tách session — LOCAL dùng `Agent` subagent, WEB dùng `RemoteTrigger`. Agent/trigger tự tạo/cập nhật step file riêng, commit+push, rồi cập nhật đúng 1 dòng status ở bảng dưới đây.

### Phase 0: Discovery — Phân tích Yêu cầu & Thiết kế

| # | Bước | Agent | Status | Step file | Hoàn thành lúc |
|---|------|-------|--------|-----------|-----------------|
| 0.1 | Product Manager — PRD v2.3: scope cuối cùng chỉ Auto-Failover Anthropic, Q1–Q7 đã chốt, Gemini+OpenAI vào Backlog tương lai | product-manager | ✅ | `steps/STEP-0.1-pm-prd.md` | 2026-08-09 21:26 |
| 0.2 | Business Analyst — User stories + AC chi tiết cho Auto-Failover Anthropic (FAIL-1..7) | business-analyst | ✅ | `steps/STEP-0.2-ba-user-stories.md` | 2026-08-09 22:15 |
| 0.3 | UI/UX Designer — Wireframe/mockup: failover status indicator, failover chain config UI, wait-and-retry UI, failover log view | ui-ux-designer | ✅ | `steps/STEP-0.3-ux-design.md` | 2026-08-09 22:32 |
| 0.4 | Engineering Manager — Estimate effort (ước tính ~1 sprint), phân bổ team, quyết định priority | engineering-manager | ⬜ | `steps/STEP-0.4-em-estimate.md` | - |

> **Lưu ý:** CTO review không bắt buộc — không đụng auth thật, không đa người dùng. Tech Lead review đủ (đụng credential swap tự động → security audit STRIDE bắt buộc tại bước TL review code).

### Phase 1: Planning — Lên Kế Hoạch Triển Khai

| # | Bước | Agent | Status | Step file | Hoàn thành lúc |
|---|------|-------|--------|-----------|-----------------|
| 1.1 | Project Manager — Lên sprint plan (~1 sprint), backlog ưu tiên, timeline | project-manager | ⬜ | `steps/STEP-1.1-pjm-sprint-plan.md` | - |
| 1.2 | Tech Lead — Technical Design Doc: failover engine architecture, monitoring design, hot-swap mechanism, retry logic, DB schema mở rộng (failover log), API endpoints mới | tech-lead | ⬜ | `steps/STEP-1.2-tl-tdd.md` | - |

### Phase 2: Sprint A — Multi-User Auth & Phân quyền ⏭️ SKIPPED

> **Lý do skip:** Scope correction 2026-08-09 — toàn bộ Phase này bị loại bỏ vì user xác nhận không cần multi-user/auth. Dashboard vẫn là tool cá nhân 1 người. Không có step file cho phase này.

### Phase 3: Sprint A (renumbered) — Gemini CLI Vault ⏭️ SKIPPED

> **Lý do skip (v2.3, 2026-08-09):** Google đã ngừng hỗ trợ OAuth cá nhân cho Gemini CLI — thông báo lỗi khi user thử đăng nhập: "This client is no longer supported for Gemini Code Assist for individuals — migrate to Antigravity suite". Token OAuth mới không thể được tạo, không thể piggyback OAuth file. Antigravity IDE cũng không khả thi (DPAPI/SQLite — đã xác nhận ở spike v2.2). Gemini CLI Vault chuyển vào Backlog tương lai (Sprint 8+). Không có step file cho phase này.

### Phase 4: Sprint B — Auto-Failover (Anthropic Account Rotation)

| # | Bước | Agent | Status | Step file | Hoàn thành lúc |
|---|------|-------|--------|-----------|-----------------|
| 4.1 | Senior Developer — Failover engine backend: giám sát 429/quota, hot-swap credentials < 100ms, failover chain config, wait-and-retry khi hết toàn bộ quota, failover log | senior-developer | ⬜ | `steps/STEP-4.1-sd-failover-engine.md` | - |
| 4.2 | Junior Developer — Frontend: failover status realtime UI, failover chain config UI, failover log view, cảnh báo hết toàn bộ quota + countdown reset | junior-developer | ⬜ | `steps/STEP-4.2-jd-failover-frontend.md` | - |
| 4.3 | Tech Lead — Code review (security audit STRIDE bắt buộc vì đụng credential swap tự động) | tech-lead | ⬜ | `steps/STEP-4.3-tl-review.md` | - |
| 4.4 | UX/UI Reviewer — Kiểm tra failover status UI: indicator rõ ràng, cảnh báo quota, config chain | ux-ui-reviewer | ⬜ | `steps/STEP-4.4-uxr.md` | - |
| 4.5 | QA Engineer — Test failover: simulate 429, simulate quota 100%, verify auto-rotation, verify CLI không bị gián đoạn, verify wait-and-retry | qa-engineer | ⬜ | `steps/STEP-4.5-qa.md` | - |
| 4.6 | QA Lead — Sign-off final | qa-lead | ⬜ | `steps/STEP-4.6-qal-signoff.md` | - |

### Phase 5: Deploy

| # | Bước | Agent | Status | Step file | Hoàn thành lúc |
|---|------|-------|--------|-----------|-----------------|
| 5.1 | DevOps Engineer — Chuẩn bị deploy: migration script DB (thêm bảng failover log), env vars mới nếu cần, backward compat check với Sprint 6 | devops-engineer | ⬜ | `steps/STEP-5.1-doe-deploy-prep.md` | - |
| 5.2 | DevOps Lead — Approve và deploy production, monitor | devops-lead | ⬜ | `steps/STEP-5.2-dol-deploy-prod.md` | - |

## Artifacts dự kiến (tổng)

- [x] `docs/prd/PRD-agent-dashboard-autofailover.md` (v2.3 — scope cuối cùng) — Product Manager ✅
- [x] `docs/prd/PRD-agent-dashboard-autofailover.docx` — xuất KZTEK brand ✅
- [x] `docs/prd/PRD-agent-dashboard-autofailover.pdf` — xuất KZTEK brand ✅
- [x] `docs/user-stories/US-agent-dashboard-autofailover.md` — Business Analyst ✅
- [x] `docs/user-stories/US-agent-dashboard-autofailover.docx` — xuất KZTEK brand ✅
- [ ] `docs/user-stories/US-agent-dashboard-autofailover.pdf` — ⚠️ PDF thất bại (RPC Windows) — DOCX đủ dùng
- [x] `docs/design/DESIGN-agent-dashboard-autofailover.md` — UI/UX Designer ✅
- [x] `docs/design/DESIGN-agent-dashboard-autofailover.docx` — xuất KZTEK brand ✅
- [ ] `docs/design/DESIGN-agent-dashboard-autofailover.pdf` — ⚠️ PDF thất bại (RPC Windows) — DOCX đủ dùng
- [ ] `docs/planning/RESOURCE-agent-dashboard-autofailover.md` — Engineering Manager
- [ ] `docs/planning/SPRINT-agent-dashboard-autofailover.md` — Project Manager
- [ ] `docs/tech-design/TDD-agent-dashboard-autofailover.md` — Tech Lead
- [ ] `src/` — failover engine, failover chain config, failover log
- [ ] `tests/` — unit + integration tests cho Auto-Failover
- [ ] `docs/ux-review/UX-REVIEW-agent-dashboard-autofailover.md` — UX/UI Reviewer
- [ ] `docs/devops/DEPLOY-agent-dashboard-autofailover.md` — DevOps Lead

## Blockers

Không có. Tất cả câu hỏi mở đã được chốt — BA có thể bắt đầu ngay.

## Quyết định / Ghi chú tổng

- **Scope v2.3 FINAL (2026-08-09):** CHỈ Auto-Failover Anthropic. Gemini + OpenAI vào Backlog tương lai.
- **Lý do loại Gemini (v2.3):** Google đã chặn OAuth cá nhân cho Gemini CLI. Piggyback OAuth file không còn hoạt động. Antigravity IDE cũng không khả thi (DPAPI/SQLite). Hướng khả thi nếu làm sau: Google AI Studio API key (không piggyback quota cá nhân).
- **Q2 đã chốt:** Khi hết toàn bộ Anthropic quota → tự động chờ và retry khi quota reset (không chỉ cảnh báo, không cross-provider).
- **Q3 đã chốt:** Tối thiểu 2 account Anthropic hiện có (`vietanh` + `OAuth Imported`), failover chain thiết kế mở rộng được.
- **Mã hoá credential:** Giữ XOR obfuscation (đã chốt với user, không nâng AES-256).
- **Storage:** Giữ SQLite (không còn vấn đề concurrent multi-user).
- **Security audit STRIDE:** Bắt buộc tại bước TL review code (Phase 4.3) vì đụng credential swap tự động.
- **CTO review:** Không còn bắt buộc — không đụng auth thật, không đa người dùng.
- **Sprint 6 hiện tại KHÔNG bị ảnh hưởng:** Initiative này là branch/feature mới, không rollback Sprint 6.

## Lịch sử cập nhật

| Ngày | Cập nhật | Agent |
|------|----------|-------|
| 2026-08-09 | Plan tạo mới (tên folder `PLAN-agent-dashboard-multiuser-2026-08-09`) — khung MASTER, chờ user xác nhận | task-planner |
| 2026-08-09 21:26 | Bước 0.1 ✅ — PRD v2.0 viết xong (scope sai — hiểu nhầm multi-user là nhiều người). PRD + .docx + .pdf | product-manager |
| 2026-08-09 | Scope correction v2.1 — "Multi-User" = 1 máy, 1 người, nhiều account AI. Bỏ Auth/RBAC. Phase 2 skip. Q4 chốt: XOR | product-manager |
| 2026-08-09 | Scope final v2.2 — Sau spike TL: OpenAI loại (user quyết định), Antigravity loại (DPAPI/SQLite), Gemini Advanced loại. Vault thu gọn: Gemini CLI piggyback OAuth. PRD đổi tên → `PRD-agent-dashboard-autofailover-gemini.md` | product-manager |
| 2026-08-09 22:15 | Bước 0.2 ✅ — US + AC viết xong: 7 US, 27 scenarios, 21 BR, 11 EC, 4 câu hỏi TL. DOCX xuất thành công. | business-analyst |
| 2026-08-09 22:32 | Bước 0.3 ✅ — Design spec 4 component UI: FailoverStatusBadge, FailoverChainConfig, FailoverLogTable, WaitRetryBanner. Mermaid 2 diagram. DOCX xuất thành công. | ui-ux-designer |
| 2026-08-09 | **Scope FINAL v2.3** — Google chặn OAuth cá nhân cho Gemini CLI (lỗi: "This client is no longer supported..."). Gemini CLI Vault KHÔNG KHẢ THI. User quyết định: ưu tiên Anthropic failover trước. (1) Loại hoàn toàn Phase 3 (Gemini CLI Vault → SKIPPED); (2) Đổi tên PRD → `PRD-agent-dashboard-autofailover.md`; (3) Đổi tên folder plan → `PLAN-agent-dashboard-autofailover-2026-08-09`; (4) Q2 chốt: wait-and-retry; (5) Q3 chốt: 2 account. Không còn câu hỏi mở nào chặn BA. | product-manager |

---

**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
**Cách đọc nhanh:** đọc MASTER trước → nếu cần chi tiết bước cụ thể mới mở step file tương ứng.
