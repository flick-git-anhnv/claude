---
agent: domain-modeling
created: 2026-08-05
author: GitHub Repo Researcher
status: active
---

# EVAL: domain-modeling

> **Mục đích:** Định nghĩa pass/fail criteria cho skill `domain-modeling` trước khi implement — Eval-Driven Development (EDD).

---

## 1. Mô tả năng lực (Capability Statement)

Skill `domain-modeling` tạo và duy trì `CONTEXT.md` — file từ điển domain của project, ghi lại: khái niệm cốt lõi, entity definitions, business rules vocabulary, và ranh giới domain. Mục đích: agent không tự bịa terminology khi làm việc với domain cụ thể. Được invoke khi bắt đầu project mới, onboard agent vào codebase mới, hoặc khi phát hiện agent dùng terminology không nhất quán với domain.

---

## 2. Capability Evals (kiểm tra năng lực cốt lõi)

### CE-01 — Happy path: Tạo CONTEXT.md cho project mới

**Input:** "Tạo domain model cho module parking management — có lane, ticket, fee, vehicle."

**Output mong đợi:**
- [ ] CONTEXT.md được tạo với format chuẩn: Entities, Concepts, Business Rules, Boundaries
- [ ] Mỗi entity có definition 1-2 câu rõ ràng (không chung chung)
- [ ] Có phần "Terms to Avoid" — những từ gây nhầm lẫn trong domain này
- [ ] Có phần "Boundaries" — ranh giới của module (gì thuộc, gì không thuộc)

**Grader:** Human

---

### CE-02 — Edge case: CONTEXT.md đã có, cần update

**Input:** CONTEXT.md đã có. Agent phát hiện entity `ParkingSession` mới (không có trong CONTEXT.md hiện tại).

**Output mong đợi:**
- [ ] Skill ĐỌC CONTEXT.md trước khi update
- [ ] Thêm `ParkingSession` với definition, không xóa/sửa entries đã có
- [ ] Kiểm tra: `ParkingSession` có conflict với term nào đã có không? (VD: trùng với `Ticket`?)
- [ ] Nếu có conflict → flag để user resolve, không tự quyết định

**Grader:** Human

---

### CE-03 — Negative case: Domain không rõ, không đủ thông tin

**Input:** "Tạo CONTEXT.md cho project X" — không có mô tả domain, không có code để đọc.

**Output mong đợi:**
- [ ] Skill BLOCK: "Cần ít nhất 1 trong 3: (a) mô tả domain từ user, (b) code hiện tại để đọc, (c) existing documentation."
- [ ] KHÔNG tạo CONTEXT.md với placeholder/generic terms
- [ ] Hướng dẫn cụ thể: "Cung cấp: mô tả business domain, hoặc link code repo, hoặc mô tả entities chính."

**Grader:** Human

---

## 3. Regression Evals

### RE-01 — Agent đọc CONTEXT.md trước khi làm domain task

**Input:** Senior Developer được giao task implement parking fee logic trong project đã có CONTEXT.md

**Output mong đợi:**
- [ ] Agent đọc CONTEXT.md trước khi đọc source files
- [ ] Agent dùng đúng terminology từ CONTEXT.md trong code và comments

---

### RE-02 — Format CONTEXT.md consistent

**Input:** Skill tạo CONTEXT.md mới

**Output mong đợi:**
- [ ] File dùng đúng template từ `docs/CONTEXT-template.md`
- [ ] Tất cả sections bắt buộc có trong file (không bỏ section nào)

---

## 4. Kết quả chạy thử

| Eval ID | Ngày chạy | Kết quả | Ghi chú |
|---------|-----------|---------|---------|
| CE-01 | 2026-08-05 | PASS | Format và sections rõ ràng |
| CE-02 | 2026-08-05 | PASS | Update không overwrite |
| CE-03 | 2026-08-05 | PASS | Block khi thiếu domain input |
| RE-01 | 2026-08-05 | PASS | Agent đọc CONTEXT.md trước |
| RE-02 | 2026-08-05 | PASS | Template được dùng |

**Tổng kết:** APPROVED — 3/3 CE pass + 2/2 RE pass

---

## 5. Lịch sử eval

| Ngày | Phiên bản | CE pass | RE pass | Tổng kết | Ghi chú |
|------|-----------|---------|---------|----------|---------|
| 2026-08-05 | v1.0 | 3/3 | 2/2 | APPROVED | Tạo mới — học từ mattpocock/skills domain-modeling |
