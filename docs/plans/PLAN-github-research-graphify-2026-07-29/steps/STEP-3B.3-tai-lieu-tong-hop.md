---
step: "3B.3"
plan: ../PLAN-MASTER.md
agent: github-repo-researcher
status: todo
completed_at:
---

# STEP 3B.3 — [Mode B / Bước 3e] Viết tài liệu tổng hợp & merge

## Input nhận
Từ Bước 3B.2 — tóm tắt những điểm chính đã giải thích trong vòng tương tác. Handoff Log sẽ được nhúng vào đây khi giao việc.

## Nhiệm vụ
Viết tài liệu tổng hợp cuối cùng (phân tích repo + nguyên lý hoạt động + hướng dẫn áp dụng theo hướng user đã chọn), xuất DOCX + PDF, sau đó xin xác nhận merge nhánh về main. KHÔNG tự merge — chờ user xác nhận.

## Definition of Done
- [ ] Cập nhật `docs/research/RESEARCH-graphify-2026-07-29.md` — thêm mục tổng hợp (nguyên lý + hướng dẫn theo Mode B)
- [ ] Chạy `python scripts/md_to_docx_kztek.py docs/research/RESEARCH-graphify-2026-07-29.md` thành công
- [ ] `docs/research/RESEARCH-graphify-2026-07-29.docx` + `.pdf` đã cập nhật
- [ ] `git add` + `git commit` + `git push` trên nhánh `research/graphify-2026-07-29`
- [ ] Agent đã xin xác nhận user có muốn merge nhánh về main không
- [ ] Nếu user đồng ý: merge + xóa nhánh nghiên cứu (tương tự quy trình ở STEP-3A.5)
- [ ] Nếu user không đồng ý: ghi chú lý do, để nhánh tồn tại
- [ ] Cập nhật step file này + PLAN-MASTER.md (task hoàn thành toàn bộ)

## Đã làm
[Điền SAU khi hoàn thành]

## Artifact
- `docs/research/RESEARCH-graphify-2026-07-29.md` (cập nhật với mục tổng hợp Mode B)
- `docs/research/RESEARCH-graphify-2026-07-29.docx`
- `docs/research/RESEARCH-graphify-2026-07-29.pdf`

## Quyết định quan trọng
[Điền SAU khi hoàn thành — user có merge hay không, lý do]

## Handoff Log — bước sau cần biết
Không có — đây là bước cuối của Mode B.

## Commit
- Hash: [điền sau khi commit]
- Đã push: [có/không]

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
