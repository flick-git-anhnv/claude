---
step: "3A.1"
plan: ../PLAN-MASTER.md
agent: github-repo-researcher
status: done
completed_at: 2026-07-29 13:59
---

# STEP 3A.1 — [Mode A / Bước 3b] Viết bảng đề xuất cải tiến KZTEK

## Input nhận
Từ Bước 2.3 — user đã chọn Mode A. Handoff Log sẽ được nhúng vào đây khi giao việc (link báo cáo phân tích, tóm tắt những điểm kỹ thuật nổi bật đã phân tích).

## Nhiệm vụ
Dựa trên phân tích repo graphify (Bước 2.1 + 2.2), viết bảng đề xuất cải tiến chi tiết cho hệ thống KZTEK. Mỗi đề xuất PHẢI nêu rõ: học từ pattern/feature nào trong graphify, áp dụng vào module nào của KZTEK, lợi ích cụ thể, rủi ro và effort ước tính. Trình bảng này cho user xem xét.

## Definition of Done
- [ ] Bảng đề xuất cải tiến có ít nhất 3 đề xuất (hoặc ghi rõ "không có đề xuất phù hợp" nếu repo quá khác biệt)
- [ ] Mỗi đề xuất có đủ 4 trường: nguồn học (repo graphify), điểm áp dụng (KZTEK module), lợi ích, rủi ro/effort
- [ ] Bảng đề xuất được viết vào `docs/research/RESEARCH-graphify-2026-07-29.md` (thêm mục "Đề xuất cải tiến KZTEK") HOẶC file riêng tùy quyết định agent
- [ ] Xuất lại DOCX + PDF sau khi cập nhật file .md
- [ ] `git add` + `git commit` + `git push` trên nhánh `research/graphify-2026-07-29`
- [ ] Cập nhật step file này + PLAN-MASTER.md

## Đã làm
- Đọc step file STEP-3A.1, đọc lại `docs/research/RESEARCH-graphify-2026-07-29.md` và PLAN-MASTER.md.
- Phân tích 5 điểm kỹ thuật nổi bật của Graphify, đối chiếu với hiện trạng KZTEK CODE-GRAPH.md (§17).
- Viết mục "## 11. Đề xuất cải tiến KZTEK (Mode A)" vào cuối file nghiên cứu với 5 đề xuất (P1–P5), mỗi đề xuất đủ 7 trường theo yêu cầu.
- Chạy `python scripts/md_to_docx_kztek.py` — DOCX thành công, PDF thất bại do thiếu converter (không block).

## Artifact
- Cập nhật `docs/research/RESEARCH-graphify-2026-07-29.md` (thêm mục §11 Đề xuất)
- Cập nhật `docs/research/RESEARCH-graphify-2026-07-29.docx` (DOCX xuất thành công)
- PDF thất bại — không block, ghi nhận trong output

## Quyết định quan trọng
- 5 đề xuất được phân thành 2 nhóm: (a) áp dụng ngay không cần dependency ngoài (P2/P3/P4/P5 — effort thấp), (b) phụ thuộc vào C# product codebase (P1 — Graphify CLI integration, effort trung bình). Trình bày rõ sự phân biệt này trong bảng tổng quan nhanh để user quyết định.
- TUYỆT ĐỐI không tự áp dụng đề xuất nào — chỉ viết bảng, chờ user xác nhận ở Bước 3A.2.

## Handoff Log — bước sau cần biết
- Đã làm: Viết 5 đề xuất P1–P5 vào `docs/research/RESEARCH-graphify-2026-07-29.md` mục §11. Commit xong trên nhánh `research/graphify-2026-07-29`.
- File/module đã đọc hoặc đổi: `docs/research/RESEARCH-graphify-2026-07-29.md`, `docs/research/RESEARCH-graphify-2026-07-29.docx`
- Quyết định quan trọng: P4 (PR checklist impact field) và P2 (query-first checklist §17) có effort thấp nhất và không phụ thuộc ngoài — đây là ứng viên "quick win" nếu user muốn chọn ít nhưng có giá trị ngay. P1 (Graphify CLI integration) mạnh nhất về kỹ thuật nhưng chỉ có giá trị khi có C# codebase thực tế.
- Bước sau cần biết: Bước 3A.2 là bước USER chọn đề xuất — agent KHÔNG làm gì thêm đến khi user xác nhận danh sách. Sau khi user xác nhận, Bước 3A.3 thực hiện Edit/Write vào KZTEK (CLAUDE.md §17, §15.3, template, v.v.). Các đề xuất P2/P3/P4/P5 chỉ đụng CLAUDE.md, CORE.md, template files — không đụng auth/payment/DB schema → không cần security-audit-stride. P1 nếu được chọn cần thêm bước test integration nhỏ.

## Commit
- Hash: aeb0f7d
- Đã push: có (research/graphify-2026-07-29)

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
