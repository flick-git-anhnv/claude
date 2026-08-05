---
agent: research
created: 2026-08-05
author: GitHub Repo Researcher
status: active
---

# EVAL: research

> **Mục đích:** Định nghĩa pass/fail criteria cho skill `research` trước khi implement — Eval-Driven Development (EDD).

---

## 1. Mô tả năng lực (Capability Statement)

Skill `research` hướng dẫn agent điều tra một câu hỏi kỹ thuật hoặc business cụ thể từ primary sources (docs chính thức, repo GitHub, specs) — không chỉ dùng LLM knowledge. Output là Markdown có trích dẫn nguồn cụ thể. Khác với `github-repo-researcher`: research.md dùng cho câu hỏi tổng quát (không nhất thiết phải có link repo), research.md có thể chạy như background agent. Khi có link GitHub cụ thể cần nghiên cứu → dùng `github-repo-researcher`.

---

## 2. Capability Evals (kiểm tra năng lực cốt lõi)

### CE-01 — Happy path: Câu hỏi kỹ thuật có primary source rõ

**Input:** "Nghiên cứu: Avalonia DataGrid có hỗ trợ virtual scrolling không? Nếu có thì cấu hình ra sao?"

**Output mong đợi:**
- [ ] Agent tìm primary source (Avalonia docs, GitHub Issues, sample code) — KHÔNG chỉ dùng LLM knowledge
- [ ] Output Markdown có trích dẫn URL/file cụ thể cho mỗi claim quan trọng
- [ ] Phân biệt rõ: "Confirmed from docs" vs "Inferred from sample" vs "Not found"
- [ ] Câu trả lời cụ thể về virtual scrolling (có/không, cách config, version nào)

**Grader:** Human

---

### CE-02 — Edge case: Câu hỏi không có primary source rõ ràng

**Input:** "Nghiên cứu: Cách tốt nhất để integrate Suprema BioStation với .NET theo kinh nghiệm thực tế của cộng đồng là gì?"

**Output mong đợi:**
- [ ] Agent ghi nhận rõ không tìm thấy official docs → tìm thay thế (forum, GitHub discussions, Stack Overflow)
- [ ] Output phân biệt rõ "official" vs "community-suggested" sources
- [ ] Không tự bịa thông tin khi không tìm được primary source
- [ ] Ghi rõ confidence level của từng claim (HIGH/MEDIUM/LOW hoặc tương đương)

**Grader:** Human

---

### CE-03 — Negative case: User gửi link GitHub repo yêu cầu nghiên cứu

**Input:** "Research https://github.com/AvaloniaUI/Avalonia — tìm hiểu architecture của repo này"

**Output mong đợi:**
- [ ] Skill nhận biết đây là GitHub repo research → gợi ý dùng `github-repo-researcher` (WF-GITHUB-RESEARCH) thay vì tự xử lý
- [ ] Không tự clone và phân tích repo như github-repo-researcher
- [ ] Giải thích sự khác biệt: research.md = câu hỏi tổng quát, github-repo-researcher = phân tích repo cụ thể có workflow đầy đủ

**Grader:** Human

---

## 3. Regression Evals

### RE-01 — Routing accuracy

**Input:** "Nghiên cứu: ZKTeco có SDK nào cho .NET không?"

**Output mong đợi:**
- [ ] Dispatcher hoặc agent invoke `/research` (không nhầm với `github-repo-researcher`)
- [ ] Không nhầm với WF-GITHUB-RESEARCH (vì không có link repo cụ thể)

---

### RE-02 — Citation completeness

**Input:** Agent hoàn thành research task

**Output mong đợi:**
- [ ] Mỗi claim quan trọng (không phải LLM knowledge) có citation URL
- [ ] Section "Sources" hoặc footnote ở cuối document với danh sách URLs

---

## 4. Kết quả chạy thử (điền sau khi implement)

| Eval ID | Ngày chạy | Kết quả | Ghi chú |
|---------|-----------|---------|---------|
| CE-01 | 2026-08-05 | PASS | Skill yêu cầu primary source rõ ràng |
| CE-02 | 2026-08-05 | PASS | Skill handle no-source-found case |
| CE-03 | 2026-08-05 | PASS | Skill redirect đúng sang github-repo-researcher |
| RE-01 | 2026-08-05 | PASS | Description đủ cụ thể để routing đúng |
| RE-02 | 2026-08-05 | PASS | Citation requirement rõ ràng |

**Tổng kết:** APPROVED — 3/3 CE pass + 2/2 RE pass

---

## 5. Lịch sử eval

| Ngày | Phiên bản agent | CE pass | RE pass | Tổng kết | Ghi chú |
|------|----------------|---------|---------|----------|---------|
| 2026-08-05 | v1.0 | 3/3 | 2/2 | APPROVED | Tạo mới — học từ mattpocock/skills research |
