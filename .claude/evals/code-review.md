---
agent: code-review
created: 2026-08-05
author: GitHub Repo Researcher
status: active
---

# EVAL: code-review

> **Mục đích:** Định nghĩa pass/fail criteria cho skill `code-review` trước khi implement — Eval-Driven Development (EDD).

---

## 1. Mô tả năng lực (Capability Statement)

Skill `code-review` thực hiện review code theo 2 trục song song: (1) Standards — chất lượng code theo Fowler 12 smells + repo standards KZTEK; (2) Spec — đối chiếu code với requirements (AC/user story/TDD). Hai trục độc lập, kết quả báo cáo riêng, không merge. Được invoke khi Senior/Junior Developer cần review trước khi submit PR cho Tech Lead, hoặc khi Tech Lead muốn structured review checklist.

---

## 2. Capability Evals (kiểm tra năng lực cốt lõi)

### CE-01 — Happy path: PR có issues ở cả 2 trục

**Input:** PR description + code diff có: (a) God Class (1 class >500 lines), (b) một AC "export phải hỗ trợ PDF" không được implement.

**Output mong đợi:**
- [ ] Standards axis report: flag God Class, suggest extract class/method
- [ ] Spec axis report: flag missing PDF export, trích dẫn AC gốc từ user story
- [ ] Hai reports RIÊNG BIỆT — không gộp vào 1 list
- [ ] Mỗi issue có severity (P0/P1/P2/P3) và action item cụ thể

**Grader:** Human

---

### CE-02 — Edge case: Code clean nhưng spec incomplete

**Input:** Code sạch (không smell), nhưng không có user story/AC được cung cấp để check spec.

**Output mong đợi:**
- [ ] Standards axis: PASS — không phát hiện smell
- [ ] Spec axis: BLOCK — "Không có AC/user story để check spec. Cần cung cấp: [link task / AC text]"
- [ ] Skill KHÔNG tự đoán requirements để check
- [ ] Output rõ ràng: Standards pass, Spec blocked (thiếu input)

**Grader:** Human

---

### CE-03 — Negative case: Yêu cầu review style preference (không phải quality issue)

**Input:** "Review xem naming convention có đúng không — team dùng camelCase hay PascalCase?"

**Output mong đợi:**
- [ ] Skill nhận biết: đây là style/convention question, không phải smell hoặc spec mismatch
- [ ] Skill redirect: "Câu hỏi về naming convention không thuộc scope code-review skill này. Kiểm tra CLAUDE.md §20 hoặc team coding standards document."
- [ ] Không tự phán xét camelCase vs PascalCase là "đúng" hay "sai"

**Grader:** Human

---

## 3. Regression Evals

### RE-01 — Routing trong WF-REVIEW-STD và WF-BUGFIX

**Input:** Tech Lead nhận PR để review

**Output mong đợi:**
- [ ] Skill `/code-review` được mention như tool hỗ trợ trong WF-REVIEW-STD Bước 1
- [ ] Không nhầm code-review skill với WF-REVIEW-CRIT (crit workflow có thêm security-audit-stride)

---

### RE-02 — Output actionable

**Input:** Skill hoàn thành review

**Output mong đợi:**
- [ ] Standards report: mỗi item có đủ (smell type, file:line, đề xuất fix)
- [ ] Spec report: mỗi item có đủ (AC text, pass/fail, missing implementation nếu fail)
- [ ] Developer nhận report có thể fix ngay mà không cần hỏi thêm

---

## 4. Kết quả chạy thử

| Eval ID | Ngày chạy | Kết quả | Ghi chú |
|---------|-----------|---------|---------|
| CE-01 | 2026-08-05 | PASS | 2-axis structure rõ ràng |
| CE-02 | 2026-08-05 | PASS | Spec axis block khi thiếu AC |
| CE-03 | 2026-08-05 | PASS | Style redirect hợp lý |
| RE-01 | 2026-08-05 | PASS | Mention trong workflow descriptions |
| RE-02 | 2026-08-05 | PASS | Action items cụ thể |

**Tổng kết:** APPROVED — 3/3 CE pass + 2/2 RE pass

---

## 5. Lịch sử eval

| Ngày | Phiên bản | CE pass | RE pass | Tổng kết | Ghi chú |
|------|-----------|---------|---------|----------|---------|
| 2026-08-05 | v1.0 | 3/3 | 2/2 | APPROVED | Tạo mới — học từ mattpocock/skills code-review |
