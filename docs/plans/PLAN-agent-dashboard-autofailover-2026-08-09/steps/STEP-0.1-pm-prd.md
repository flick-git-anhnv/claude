---
step: "0.1"
title: "Product Manager — PRD"
agent: product-manager
status: done
completed_at: "2026-08-09 21:26"
---

# STEP 0.1 — Product Manager: Viết PRD

## Nhiệm vụ

Viết PRD đầy đủ cho initiative Agent Dashboard v2 (Multi-User / Multi-AI / Auto-Failover).

## Đã làm

- Đọc PLAN-MASTER.md, PRD v1 gốc (`docs/prd/PRD-agent-dashboard.md`), báo cáo cải tiến (mục #1 và #2), và DB schema hiện tại để hiểu baseline.
- Viết PRD v2.0 tại `docs/prd/PRD-agent-dashboard-multiuser.md` (10 mục đầy đủ):
  - Bối cảnh + business justification (tại sao cần, không chỉ "có thể làm")
  - Scope decision: ghi rõ đây là thay đổi chủ ý 3 non-goal của v1
  - 2 user persona: Admin và User thường (với quyền hạn rõ ràng)
  - 5 goals, danh sách 11 non-goal với lý do từ chối/hoãn
  - Feature requirements (acceptance-level) cho 3 trụ cột: AUTH (8 req), VAULT (7 req), FAIL (7 req)
  - 8 câu hỏi mở Q1–Q8 cần giải quyết trước khi implement
  - 4 rủi ro chính với biện pháp giảm thiểu
  - Ước tính sơ bộ: 3–4 sprint con (~3–6 tuần)
  - Metric đo lường thành công (6 metrics đo được)
- Xuất DOCX + PDF qua `scripts/md_to_docx_kztek.py`.

## Artifact

- `docs/prd/PRD-agent-dashboard-multiuser.md` — source PRD
- `docs/prd/PRD-agent-dashboard-multiuser.docx` — Word document (KZTEK brand)
- `docs/prd/PRD-agent-dashboard-multiuser.pdf` — PDF

## Quyết định quan trọng

- Scope v2 chủ ý đảo ngược 3 non-goal của v1 (multi-user, auth, multi-provider) — ghi rõ trong PRD mục 2 để audit trail.
- Auto-Failover scope giới hạn: chỉ Anthropic-to-Anthropic rotation. Failover sang OpenAI/Gemini là roadmap sau.
- Provider AI trong Vault: giả định hợp lý dựa trên thị trường (OpenAI, Gemini, DeepSeek, OpenRouter, Groq) — PHẢI xác nhận với user (Q3).
- Phân quyền 2 cấp (Admin/User) là giả định mặc định — Q1 hỏi thêm về Operator level.

## Handoff Payload — bước sau đọc phần này

> **QUAN TRỌNG — Cập nhật sau scope FINAL v2.3 (2026-08-09):** PRD v2.2 (Gemini CLI Vault + Auto-Failover) đã bị thay thế bằng PRD v2.3 — scope CHỈ còn Auto-Failover Anthropic. Google đã chặn OAuth cá nhân cho Gemini CLI. File PRD mới: `docs/prd/PRD-agent-dashboard-autofailover.md`. Folder plan đổi tên: `PLAN-agent-dashboard-autofailover-2026-08-09`. Không còn câu hỏi mở nào — BA bắt đầu ngay.

- do_not_redo:
  - KHÔNG thiết kế Auth/login/RBAC/session đa người dùng — loại từ v2.1, giữ nguyên.
  - KHÔNG thêm Gemini CLI Vault vào scope — Google đã chặn OAuth cá nhân cho Gemini CLI (lỗi: "This client is no longer supported for Gemini Code Assist for individuals"). Không khả thi kỹ thuật. Chỉ có thể làm lại nếu có giải pháp kỹ thuật thay thế (ví dụ: Google AI Studio API key — spike riêng).
  - KHÔNG thêm OpenAI vào scope — chưa nghiên cứu, user quyết định làm sau.
  - KHÔNG đề xuất piggyback Google Antigravity IDE — TL đã xác nhận không khả thi (Electron/DPAPI/SQLite). Không reopen nếu không có giải pháp kỹ thuật mới.
  - Mã hoá credential Anthropic: XOR obfuscation — ĐÃ CHỐT, không mở lại.
  - Failover scope: chỉ Anthropic-to-Anthropic. KHÔNG cross-provider sang bất kỳ provider nào khác.
- watch_out:
  - PRD hiện tại là **v2.3** — tên file: `docs/prd/PRD-agent-dashboard-autofailover.md`.
  - Chỉ còn **1 trụ cột FINAL**: Auto-Failover Anthropic (FAIL-1..7). KHÔNG còn Gemini CLI Vault.
  - **Q2 đã chốt:** Khi hết toàn bộ Anthropic quota → tự động chờ và retry khi quota reset (không chỉ cảnh báo, không cross-provider). BA viết AC cho FAIL-6 theo đúng hành vi này.
  - **Q3 đã chốt:** Tối thiểu 2 account Anthropic (`vietanh` + `OAuth Imported`). Failover chain thiết kế hỗ trợ mở rộng.
  - KHÔNG còn câu hỏi mở nào — BA bắt đầu viết User Stories + AC ngay, không cần chờ gì thêm.
- next_inputs:
  - PRD v2.3: `docs/prd/PRD-agent-dashboard-autofailover.md` — BA đọc toàn bộ, đặc biệt mục 5 (FAIL-1..7), mục 7 (tất cả Q đã chốt), mục 8 (Backlog tương lai — không scope vào đây).
  - Account Manager hiện tại (v1): `tools/agent-dashboard/backend/agent_dashboard/db/schema.py` — BA dùng để hiểu data model gốc khi viết AC mở rộng failover chain + failover log.
  - PLAN-MASTER.md: `docs/plans/PLAN-agent-dashboard-autofailover-2026-08-09/PLAN-MASTER.md` — BA xem danh sách step và phase để biết bước tiếp theo.
