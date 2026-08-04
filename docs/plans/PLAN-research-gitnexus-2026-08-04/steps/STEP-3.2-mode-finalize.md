---
step: 3.2
plan: ../PLAN-MASTER.md
agent: github-repo-researcher
status: todo
completed_at:
---

# STEP 3.2 — Hoàn thiện theo Mode (A: áp dụng đề xuất / B: tài liệu tổng hợp)

## Input nhận
Handoff từ STEP-3.1: [Mode A] danh sách đề xuất user đã chọn / [Mode B] xác nhận user đã nắm rõ nguyên lý.

## Nhiệm vụ
**Nếu Mode A:** Áp dụng các đề xuất đã được user chọn vào code/tài liệu KZTEK. Commit lên nhánh `research/gitnexus-2026-08-04`. Nếu đề xuất đụng auth/payment/DB schema → chạy `security-audit-stride` trước khi tiếp tục.

**Nếu Mode B:** Viết tài liệu tổng hợp cuối cùng (phân tích + nguyên lý + hướng dẫn áp dụng) vào `docs/research/RESEARCH-gitnexus-2026-08-04-guide.md`. Xuất DOCX+PDF. Xin xác nhận merge nhánh về main.

## Definition of Done
**Mode A:**
- [ ] Các đề xuất đã chọn được áp dụng vào KZTEK
- [ ] Commit + push lên nhánh research
- [ ] Báo user danh sách thay đổi đã áp dụng

**Mode B:**
- [ ] `docs/research/RESEARCH-gitnexus-2026-08-04-guide.md` được tạo
- [ ] DOCX + PDF xuất thành công
- [ ] Commit + push lên nhánh research

## Đã làm
[Điền sau khi hoàn thành]

## Artifact
- [Mode A] File/code đã sửa trong KZTEK
- [Mode B] `docs/research/RESEARCH-gitnexus-2026-08-04-guide.md` + `.docx` + `.pdf`

## Quyết định quan trọng
[Điền những thay đổi quan trọng đã áp dụng hoặc quyết định về nội dung tài liệu]

## Handoff Log — bước sau cần biết
[Mode A: danh sách file đã thay đổi, commit hash / Mode B: đường dẫn tài liệu tổng hợp]

## Commit
- Hash: [điền sau khi commit]
- Đã push: [có/không]

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
