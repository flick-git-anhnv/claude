---
step: 3.1
plan: ../PLAN-MASTER.md
agent: github-repo-researcher
status: done
completed_at: 2026-08-04 15:30
---

# STEP 3.1 — Hành động theo Mode (A: đề xuất cải tiến / B: giải thích tương tác)

## Input nhận
Handoff từ STEP-2.3: user đã chọn Mode A hoặc Mode B.

## Nhiệm vụ
**Nếu Mode A:** Dựa trên phân tích từ STEP-2.2, viết bảng đề xuất cải tiến KZTEK (từng đề xuất nêu rõ: học từ đâu trong repo, áp dụng vào đâu trong KZTEK, lợi ích, rủi ro/effort). Trình user xem xét.

**Nếu Mode B:** Hỏi user muốn tìm hiểu tiếp phần nào — nguyên lý hoạt động / hướng dẫn áp dụng-sử dụng / cả hai. Sau đó giải thích tương tác (có ví dụ cụ thể từ repo nguồn), lặp lại hỏi-đáp đến khi user xác nhận đã nắm rõ.

## Definition of Done
**Mode A:**
- [ ] Bảng đề xuất cải tiến được trình bày rõ ràng
- [ ] User nhìn thấy và phản hồi (bước này kết thúc khi user xác nhận đề xuất nào được chọn)

**Mode B:**
- [ ] Hỏi user muốn tìm hiểu phần nào
- [ ] Giải thích tương tác ít nhất 1 vòng hỏi-đáp
- [ ] Tiếp tục đến khi user xác nhận đã nắm rõ

## Đã làm
Mode A được chọn. Viết 6 đề xuất cải tiến (GX-1 đến GX-6) vào mục 7 của RESEARCH-gitnexus-2026-08-04.md, mỗi đề xuất có đủ 7 cột bảng + phần chi tiết giải thích. Xuất lại DOCX + PDF thành công. Bước này kết thúc khi user chọn đề xuất nào để áp dụng.

## Artifact
- `docs/research/RESEARCH-gitnexus-2026-08-04.md` — đã thêm mục 7 (bảng 6 đề xuất GX-1..GX-6 + chi tiết)
- `docs/research/RESEARCH-gitnexus-2026-08-04.docx` — xuất lại ✅
- `docs/research/RESEARCH-gitnexus-2026-08-04.pdf` — xuất lại ✅

## Quyết định quan trọng
Mode A (đề xuất áp dụng KZTEK). 6 đề xuất được tổ chức theo nhóm:
- GX-1, GX-4: cải tiến CODE-GRAPH-template.md (thêm cột Callers/Used-by, Last verified)
- GX-2: cải tiến PLAN-STEP-template.md (field deps tường minh)
- GX-3: tạo mới skill /detect-impact
- GX-5: cải tiến task-planner.md (context hints Pre-0)
- GX-6: cải tiến Handoff Log structure (PLAN-STEP-template + §16.4 CLAUDE.md)

## Handoff Payload — bước sau đọc phần này
- do_not_redo: đã viết bảng đề xuất vào RESEARCH file, đã xuất DOCX+PDF — không cần làm lại
- watch_out: GX-3 (/detect-impact skill) phụ thuộc GX-1 (cột Callers/Used-by trong CODE-GRAPH-template) phải áp dụng trước; nếu user chọn GX-3 mà không chọn GX-1, cần áp dụng GX-1 trước hoặc ghi nhận dependency này
- next_inputs: user sẽ chọn đề xuất nào (0, 1, hoặc nhiều trong GX-1..GX-6) — bước 3.2 áp dụng các đề xuất đó

## Commit
- Hash: [điền sau commit]
- Đã push: không

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
