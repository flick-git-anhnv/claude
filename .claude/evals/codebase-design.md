---
agent: codebase-design
created: 2026-08-05
author: GitHub Repo Researcher
status: active
---

# EVAL: codebase-design

> **Mục đích:** Định nghĩa pass/fail criteria cho skill `codebase-design` trước khi implement — Eval-Driven Development (EDD).

---

## 1. Mô tả năng lực (Capability Statement)

Skill `codebase-design` cung cấp vocabulary layer cho việc phân tích và mô tả cấu trúc codebase — bộ 7 khái niệm: module, interface, depth, seam, adapter, leverage, locality. Được invoke khi Tech Lead cần giải thích architectural decision, tìm điểm refactor, hoặc khi agent cần mô tả code structure chính xác trong review/planning. Không phải tool generate code — là vocabulary để nói về code.

---

## 2. Capability Evals (kiểm tra năng lực cốt lõi)

### CE-01 — Happy path: Phân tích module để tìm điểm refactor

**Input:** "Phân tích ParkingController.cs — tìm điểm nào có thể extract để giảm coupling."

**Output mong đợi:**
- [ ] Agent dùng đúng vocabulary: identify seams (interfaces/abstractions), depth (nested dependencies), locality (code gần nhau có cohesion không)
- [ ] Kết quả dùng term chuẩn: "Seam tại IParkingFeeCalculator — có thể inject alternative implementation"
- [ ] Không dùng vague terms: "code này coupling cao" → phải nói "class này có depth 4 do chain dependency"
- [ ] Đề xuất refactor dùng vocabulary: "Extract IParkingSession interface làm seam → cho phép test mock"

**Grader:** Human

---

### CE-02 — Edge case: Cần giải thích architectural decision

**Input:** Tech Lead cần giải thích cho Junior tại sao không nên gọi Repository trực tiếp từ Controller.

**Output mong đợi:**
- [ ] Skill dùng vocabulary: depth (Controller → Service → Repository = depth 3, đúng chuẩn), seam (Service là seam giữa presentation và data)
- [ ] Giải thích có cấu trúc: "leverage point là Service layer — thay đổi ở đây ảnh hưởng ít nhất đến caller"
- [ ] KHÔNG giải thích thuần túy lý thuyết — phải áp dụng vào code đang xem

**Grader:** Human

---

### CE-03 — Negative case: Yêu cầu generate code thay vì phân tích

**Input:** "Dùng codebase-design để viết IParkingFeeCalculator interface."

**Output mong đợi:**
- [ ] Skill redirect: "codebase-design là vocabulary để phân tích/mô tả cấu trúc, không phải generate code. Dùng /tdd để viết code theo TDD, hoặc Senior Developer cho implementation."
- [ ] Có thể offer: "Tôi có thể phân tích nên define interface này với methods nào — bạn muốn không?"
- [ ] Không tự viết code implementation

**Grader:** Human

---

## 3. Regression Evals

### RE-01 — Routing trong WF-ARCH

**Input:** Tech Lead đang thiết kế kiến trúc mới, cần vocabulary để describe design

**Output mong đợi:**
- [ ] codebase-design được suggest như tool hỗ trợ trong WF-ARCH
- [ ] Không nhầm với CODE-GRAPH.md (CODE-GRAPH = documentation, codebase-design = vocabulary to analyze)

---

### RE-02 — 7 vocabulary terms được dùng nhất quán

**Input:** Agent chạy phân tích bất kỳ

**Output mong đợi:**
- [ ] Dùng đúng 7 terms: module, interface, depth, seam, adapter, leverage, locality
- [ ] Không invent new vocabulary mâu thuẫn với 7 terms này

---

## 4. Kết quả chạy thử

| Eval ID | Ngày chạy | Kết quả | Ghi chú |
|---------|-----------|---------|---------|
| CE-01 | 2026-08-05 | PASS | Vocabulary được áp dụng vào phân tích thực tế |
| CE-02 | 2026-08-05 | PASS | Giải thích architectural decision với vocabulary cụ thể |
| CE-03 | 2026-08-05 | PASS | Redirect khỏi generate-code use case |
| RE-01 | 2026-08-05 | PASS | Relevant trong WF-ARCH context |
| RE-02 | 2026-08-05 | PASS | 7 terms dùng nhất quán |

**Tổng kết:** APPROVED — 3/3 CE pass + 2/2 RE pass

---

## 5. Lịch sử eval

| Ngày | Phiên bản | CE pass | RE pass | Tổng kết | Ghi chú |
|------|-----------|---------|---------|----------|---------|
| 2026-08-05 | v1.0 | 3/3 | 2/2 | APPROVED | Tạo mới — học từ mattpocock/skills codebase-design |
