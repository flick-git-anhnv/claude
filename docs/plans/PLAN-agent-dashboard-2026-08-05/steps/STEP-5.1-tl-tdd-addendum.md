---
step: 5.1
name: TDD ADDENDUM Sprint 2
owner: Tech Lead
status: done
completed_at: 2026-08-06 16:00
---

# Bước 5.1 — TDD ADDENDUM Sprint 2

## Nhiệm vụ
Viết addendum (v1.1) vào cuối `docs/tech-design/TDD-agent-dashboard.md` — KHÔNG viết đè v1.0. Bao 2 track độc lập chạy song song ở Sprint 2:
- Track A: OAuth Account Support (SD)
- Track B: Agent Name/Activity + 2 View Modes (JD)

## Đã làm
- Đọc TDD v1.0 (§1–14) + PRD Q4/Q4b + PLAN-MASTER + parser hiện có + inventory `.claude/agents/*.md`.
- Thêm §15 Assumptions, §16 Goals/Non-goals Sprint 2.
- **Track A (§17):** data model v2 với discriminator `kind` (api_key|oauth_session), API bổ sung (`import-current-oauth`, `oauth-status`, activate flow swap), auto-refresh scheduler "swap-and-invoke" (KHÔNG gọi thẳng OAuth endpoint Anthropic — dùng `claude -p "ok" --model claude-haiku-4-5 --max-turns 1` để buộc CLI tự refresh), UI 2-tab dialog + security banner + badge needs_relogin, migration v1→v2 idempotent.
- **Track B (§18):** parser trích `subagent_type` + `description` khi tool_use `name=="Agent"`, DB thêm 3 column (`current_subagent_type/activity/at`), mapping đầy đủ 19 subagent → VN display name + fallback title-case, endpoint `/api/sessions/by-project`, decode project-slug best-effort (`c--Users-...` → `C:\Users-...` + tooltip slug gốc, chấp nhận ambiguity), UI toggle 2 view mode "Theo Agent"/"Theo Dự án" (accordion `<details>` native).
- §19 Rủi ro Sprint 2 (5 mục), §20 Task breakdown (S2-T01..T12, SD 5.5 ngày ∥ JD 4 ngày), §21 Handoff Payload cho SD + JD.
- Cập nhật PLAN-MASTER: Phase 5 với 5 bước, status plan `completed` → `active`.
- Xuất DOCX+PDF cho TDD.

## Quyết định thiết kế chính
- **KHÔNG tự gọi Anthropic OAuth endpoint** — theo hướng safe đã thống nhất, dùng chiến lược "swap-and-invoke" (backup in-memory + swap file + subprocess CLI + compare expiresAt + restore).
- **`refresh_lock` global asyncio.Lock** — tuần tự hoá refresh iteration, tránh race condition swap file.
- **Encryption giữ nguyên XOR+base64** — accepted risk trong PRD Q4b, thêm security banner UI bắt buộc.
- **Token subagent con KHÔNG tách được ở Sprint 2** — ghi rõ gap ở §16 Non-goals + §19 S2-R4 (file `tasks/<agentId>.output` = 0 byte, không có nguồn dữ liệu tin cậy).
- **Decode slug best-effort có ambiguity** — chấp nhận limitation, tooltip slug gốc để user tự nhận ra.

## Artifact
- `docs/tech-design/TDD-agent-dashboard.md` — cập nhật (§15–21 mới, dòng ~477+)
- `docs/tech-design/TDD-agent-dashboard.docx` + `.pdf` — xuất lại
- `docs/plans/PLAN-agent-dashboard-2026-08-05/PLAN-MASTER.md` — Phase 5 mới, status → active

## Handoff Payload — bước sau đọc phần này
- **Đã làm:** TDD addendum v1.1 chốt 2 track (§17 OAuth, §18 Agent view). Handoff riêng cho SD/JD ở §21.1 và §21.2 của TDD.
- **do_not_redo:** KHÔNG cần đọc lại toàn bộ TDD v1.0 để thiết kế; chỉ dùng §21.1 (SD) hoặc §21.2 (JD) làm điểm vào; các quyết định OAuth/parser đã chốt.
- **watch_out:** SD phải verify thực tế lệnh `claude -p ...` có trigger refresh hay không (compare expiresAt); JD phải giữ decode slug tooltip vì ambiguity không thể tránh; TL security-audit-stride (bước 5.4) BẮT BUỘC vì Track A ghi/đọc file credential nhạy cảm.
- **next_inputs:** SD đọc TDD §17, §19, §20 (S2-T01..T06), §21.1. JD đọc TDD §18, §19, §20 (S2-T07..T12), §21.2.
