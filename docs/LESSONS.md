---
created: 2026-07-29
updated: 2026-07-29
description: Bài học workflow và business decisions đã học — KHÁC với GOTCHAS.md (lỗi kỹ thuật ngầm)
---

# LESSONS.md — Bài học Workflow & Business Decisions

> **Mục đích:** Ghi lại bài học về quy trình làm việc, quyết định nghiệp vụ/kiến trúc, và pattern thành công/thất bại — để tránh lặp lại sai lầm quy trình và kế thừa cách xử lý đã hoạt động tốt.
>
> **KHÁC với `.claude/shared/GOTCHAS.md`:** GOTCHAS.md = lỗi kỹ thuật ngầm (tool behavior, path quirks, env issues). LESSONS.md = bài học workflow, business logic, quy trình xử lý tình huống.
>
> **Khi nào thêm entry:** Sau mỗi workflow hoàn thành (xem CLAUDE.md §3.3), nếu có bài học đáng ghi. Không cần thêm nếu workflow chạy hoàn toàn theo template không có gì bất thường.
>
> **Đọc khi nào:** Đầu mỗi session mới (Pre-0b trong CLAUDE.md §3.0) — đọc lướt 5–10 entry gần nhất.

---

## Template mỗi entry

```
### L[NNN] — [Tiêu đề ngắn mô tả bài học]
- **Ngày:** YYYY-MM-DD
- **Workflow/Task liên quan:** [WF-ID hoặc tên task]
- **Bài học rút ra:** [Mô tả rõ ràng — đã xảy ra gì, tại sao đáng ghi]
- **Áp dụng cho lần sau:** [Hành động cụ thể cần làm khác đi, hoặc pattern cần giữ lại]
```

---

## Danh sách bài học

### L001 — Xác định Research Mode trước khi tạo nhánh, không đợi đến Bước 3
- **Ngày:** 2026-07-29
- **Workflow/Task liên quan:** WF-GITHUB-RESEARCH (nghiên cứu Graphify-Labs/graphify)
- **Bài học rút ra:** User thường nêu rõ mục đích (Mode A: cải tiến KZTEK / Mode B: học tập) ngay trong yêu cầu ban đầu. Nếu đã rõ ở Bước 1 → ghi nhận và skip Bước 2.3 (hỏi lại mode), tiết kiệm 1 vòng tương tác không cần thiết.
- **Áp dụng cho lần sau:** Khi user gửi link GitHub kèm từ khóa "cải tiến", "áp dụng", "đề xuất" → mặc định Mode A và bỏ qua bước hỏi mode. Khi có từ khóa "học", "tìm hiểu", "cho biết" → Mode B. Chỉ hỏi khi thực sự không rõ.

### L002 — Đề xuất cải tiến tài liệu/workflow không cần security-audit-stride
- **Ngày:** 2026-07-29
- **Workflow/Task liên quan:** WF-GITHUB-RESEARCH Mode A (graphify — 5 đề xuất P1–P5)
- **Bài học rút ra:** Các đề xuất chỉ thay đổi tài liệu nội bộ (CLAUDE.md, templates, docs/) và không đụng auth/payment/DB schema/dữ liệu nhạy cảm → không cần chạy security-audit-stride (theo CLAUDE.md rule chỉ bắt buộc khi đụng các nhóm đó). Tiết kiệm thời gian bằng cách đánh giá ngay tại bước lập đề xuất, không đợi đến lúc apply.
- **Áp dụng cho lần sau:** Khi lập bảng đề xuất Mode A, ngay lập tức đánh dấu "không cần security-audit" cho các đề xuất thuần tài liệu — ghi rõ lý do trong cột Rủi ro/Effort để user yên tâm approve nhanh.

