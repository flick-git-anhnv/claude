---
name: research
description: "PHẢI dùng khi: cần điều tra câu hỏi kỹ thuật hoặc business từ primary sources (docs chính thức, specs, GitHub repos, RFCs) — output cần có citation cụ thể, không chỉ dùng LLM knowledge. Trigger: 'nghiên cứu X', 'tìm hiểu Y hoạt động như thế nào', 'so sánh A và B', 'có tài liệu chính thức nào về Z không'. KHÔNG dùng khi: user gửi link GitHub repo cụ thể và yêu cầu phân tích repo đó (→ github-repo-researcher / WF-GITHUB-RESEARCH); yêu cầu là viết code/feature (→ WF-FEATURE); chỉ cần tra cứu nhanh không cần citation (→ trả lời thẳng từ LLM knowledge)."
---

# Skill: research — Điều tra từ Primary Sources

> Học từ `mattpocock/skills` `skills/engineering/research/SKILL.md`.
> Nguyên tắc cốt lõi: **"Bắt đầu từ primary sources. Cite mọi claim quan trọng. Phân biệt rõ 'confirmed' vs 'inferred' vs 'not found'."**

---

## Quy trình 4 bước

### Bước 1 — Xác định câu hỏi cần trả lời

ĐỌC yêu cầu và làm rõ:
- Câu hỏi chính là gì? (1 câu cụ thể)
- Câu trả lời dạng nào là đủ? (yes/no? how-to? comparison? summary?)
- Primary sources khả dĩ ở đâu? (official docs, GitHub repo, spec, RFC?)

Nếu câu hỏi quá rộng → thu hẹp thành 2-3 sub-questions cụ thể. KHÔNG bắt đầu research với câu hỏi mơ hồ.

---

### Bước 2 — Tìm primary sources

**Thứ tự ưu tiên source:**

1. Official documentation (docs.avalonia.net, learn.microsoft.com, developer.mozilla.org...)
2. GitHub repo chính thức (README, source code, Issues, Discussions)
3. RFC / spec chính thức
4. Technical blog của maintainer
5. Community (Stack Overflow, forum — chỉ dùng khi không có primary source)

**Quy tắc tìm source:**
- Dùng `WebSearch` với query hướng vào primary source: `"site:docs.avalonia.net DataGrid virtual scrolling"`
- Dùng `WebFetch` để đọc trang docs tìm được
- Nếu GitH repo: dùng `WebFetch` trực tiếp URL README hoặc specific file
- Tối thiểu 2 sources độc lập cho mỗi claim quan trọng

**KHÔNG làm:**
- Không tự đưa ra claim từ LLM knowledge mà không có source
- Không dùng SEO farm, summary sites (toidicodedao, viblo khi chỉ paraphrase), medium articles không rõ tác giả

---

### Bước 3 — Tổng hợp và phân loại

Với mỗi claim tìm được, phân loại:

| Label | Ý nghĩa |
|-------|---------|
| **CONFIRMED** | Đọc trực tiếp từ primary source (docs/source code) |
| **INFERRED** | Suy luận từ context trong source — không có phát biểu tường minh |
| **COMMUNITY** | Chỉ có ở community source (Stack Overflow, forum), chưa verified từ primary |
| **NOT FOUND** | Tìm kiếm nhưng không tìm được thông tin về điểm này |

---

### Bước 4 — Viết output có citation

Output format chuẩn:

```markdown
## [Tóm tắt câu trả lời — 1-3 câu]

### Phát hiện chính

**[Điểm 1]** [CONFIRMED]
[Giải thích cụ thể]
> Source: [URL hoặc file:line] — [trích đoạn ngắn relevant]

**[Điểm 2]** [INFERRED]
[Giải thích]
> Source: [URL] — [trích đoạn]

**[Điểm 3]** [NOT FOUND]
Không tìm thấy thông tin về [điểm này] trong primary sources đã kiểm tra.

### Không chắc chắn / cần kiểm tra thêm

- [Điểm còn unclear và tại sao]

### Sources

- [URL 1] — [mô tả ngắn]
- [URL 2] — [mô tả ngắn]
```

---

## Red Flags

| Thought | Reality |
|---------|---------|
| "Tôi biết câu trả lời rồi, không cần search" | LLM knowledge có thể outdated hoặc sai. Primary source check mất < 5 phút |
| "Community source đủ rồi" | Community claim có thể sai hoặc outdated. Cần primary source để verify |
| "Không tìm thấy nghĩa là không có" | Có thể search query sai. Thử 2-3 query khác trước khi kết luận NOT FOUND |

---

## Verification (done gate)

- [ ] Mỗi claim CONFIRMED có URL source cụ thể
- [ ] Claims INFERRED và COMMUNITY được đánh label rõ ràng
- [ ] Có mục "NOT FOUND" cho những gì tìm không thấy (thay vì im lặng bỏ qua)
- [ ] Có section "Sources" hoặc footnotes với danh sách URLs ở cuối
- [ ] Không có claim quan trọng nào không có source

---

## Phân biệt với github-repo-researcher

| Skill | Khi nào dùng |
|-------|-------------|
| `/research` | Câu hỏi kỹ thuật tổng quát, không có link repo cụ thể; hoặc cần citation từ nhiều sources khác nhau |
| `github-repo-researcher` + WF-GITHUB-RESEARCH | User gửi link GitHub repo cụ thể và yêu cầu phân tích/nghiên cứu repo đó — có workflow đầy đủ (tạo nhánh, clone, RESEARCH-*.md, DOCX/PDF export) |
