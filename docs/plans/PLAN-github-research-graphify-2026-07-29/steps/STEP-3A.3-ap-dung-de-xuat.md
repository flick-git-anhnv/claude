---
step: "3A.3"
plan: ../PLAN-MASTER.md
agent: github-repo-researcher
status: todo
completed_at:
---

# STEP 3A.3 — [Mode A / Bước 4b] Áp dụng đề xuất đã được user chọn

## Input nhận
Từ Bước 3A.2 — danh sách đề xuất được user duyệt. Handoff Log sẽ được nhúng vào đây khi giao việc (danh sách cụ thể đề xuất nào được chọn, module KZTEK liên quan).

## Nhiệm vụ
Áp dụng các đề xuất đã được user chọn vào code/tài liệu KZTEK. Commit toàn bộ thay đổi lên nhánh `research/graphify-2026-07-29`. Nếu đề xuất đụng auth/payment/DB schema/dữ liệu nhạy cảm → chạy `security-audit-stride` trước khi coi là hoàn thành.

## Definition of Done
- [ ] Từng đề xuất được chọn đã được áp dụng vào đúng module/file KZTEK
- [ ] [Nếu áp dụng] Đề xuất đụng auth/payment/DB schema → đã chạy `security-audit-stride`, không có Fail nhóm rủi ro cao
- [ ] Tài liệu liên quan cập nhật theo §15 CLAUDE.md (PRD/TDD/DESIGN nếu thay đổi code/schema/UI)
- [ ] `git add` + `git commit` + `git push` trên nhánh `research/graphify-2026-07-29`
- [ ] Cập nhật step file này + PLAN-MASTER.md

## Đã làm
[Điền SAU khi hoàn thành]

## Artifact
[Điền SAU khi hoàn thành — danh sách file đã thay đổi]

## Quyết định quan trọng
[Điền SAU khi hoàn thành — ghi nếu có đề xuất nào gặp trở ngại khi áp dụng]

## Handoff Log — bước sau cần biết
[Điền SAU khi hoàn thành — tóm tắt những gì đã được áp dụng, file nào đã thay đổi, để user review trước khi quyết định merge]

## Commit
- Hash: [điền sau khi commit]
- Đã push: [có/không]

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
