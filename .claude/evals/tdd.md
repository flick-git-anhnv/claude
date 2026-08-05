---
agent: tdd
created: 2026-08-05
author: GitHub Repo Researcher
status: active
---

# EVAL: tdd

> **Mục đích:** Định nghĩa pass/fail criteria cho skill `tdd` trước khi implement — Eval-Driven Development (EDD).

---

## 1. Mô tả năng lực (Capability Statement)

Skill `tdd` hướng dẫn agent viết code theo Red-Green-Refactor cycle với seam-based approach: xác định seams (điểm extension trong code hiện tại) trước khi viết test, viết failing test (RED) trước khi viết code, implement tối thiểu để test pass (GREEN), rồi refactor. Tránh 3 anti-pattern: implementation-coupled (test gắn vào implementation detail), tautological (test không verify gì thực sự), horizontal slicing (test theo layer thay vì theo user story). Được invoke khi viết feature mới hoặc fix bug có test.

---

## 2. Capability Evals (kiểm tra năng lực cốt lõi)

### CE-01 — Happy path: Viết feature mới với TDD

**Input:** "Viết function `calculateParkingFee(entry: DateTime, exit: DateTime): decimal` — phí 5,000 VND/30 phút, tối thiểu 1 chu kỳ."

**Output mong đợi:**
- [ ] Agent bắt đầu bằng failing test (RED) trước khi viết implementation
- [ ] Test scenarios theo user story: 30 phút → 5000, 31 phút → 10000, 0 phút → 5000
- [ ] KHÔNG viết test theo implementation detail (không test `TimeSpan.TotalMinutes / 30`)
- [ ] Sau khi test pass (GREEN): code tối thiểu để pass, sau đó refactor

**Grader:** Human

---

### CE-02 — Edge case: Agent muốn viết implementation trước

**Input:** Agent sắp viết `calculateParkingFee` implementation trước rồi mới viết test.

**Output mong đợi:**
- [ ] Skill nhận ra và block: "Viết test trước — RED trước GREEN"
- [ ] Skill hướng dẫn agent xác định seam và viết failing test ngay cả khi "function chưa tồn tại" (compile fail = RED state)
- [ ] KHÔNG cho phép "viết implementation tối thiểu trước để test có thể compile"

**Grader:** Human

---

### CE-03 — Negative case: 3 anti-patterns bị phát hiện

**Input:** Agent viết test: `Assert.Equal(TimeSpan.FromMinutes(35).TotalMinutes / 30, Math.Ceiling(...))`

**Output mong đợi:**
- [ ] Skill nhận ra anti-pattern: test đang test implementation detail (TimeSpan.TotalMinutes / 30) — implementation-coupled
- [ ] Skill hướng dẫn viết lại: test behavior, không test implementation. VD: "calculateParkingFee(entry, entry.AddMinutes(35)) == 10000"
- [ ] Không chấp nhận test chỉ assert cùng logic mà code sẽ dùng (tautological)

**Grader:** Human

---

## 3. Regression Evals

### RE-01 — Routing accuracy

**Input:** Senior Developer được giao task "viết feature mới có test"

**Output mong đợi:**
- [ ] Agent mention `/tdd` trong workflow
- [ ] Không nhầm với `/diagnosing-bugs` (tdd = viết code mới, diagnosing = debug code cũ)

---

### RE-02 — Seam identification

**Input:** Agent nhận task thêm tính năng vào code hiện tại đang chạy

**Output mong đợi:**
- [ ] Agent xác định seam (interface/abstraction point) trước khi viết test
- [ ] Không viết test đòi hỏi sửa code có sẵn để test được (coupling cao)

---

## 4. Kết quả chạy thử

| Eval ID | Ngày chạy | Kết quả | Ghi chú |
|---------|-----------|---------|---------|
| CE-01 | 2026-08-05 | PASS | RED trước GREEN constraint rõ |
| CE-02 | 2026-08-05 | PASS | Block implementation-first |
| CE-03 | 2026-08-05 | PASS | 3 anti-patterns được đặt tên cụ thể |
| RE-01 | 2026-08-05 | PASS | Description phân biệt với diagnosing-bugs |
| RE-02 | 2026-08-05 | PASS | Seam identification là bước đầu |

**Tổng kết:** APPROVED — 3/3 CE pass + 2/2 RE pass

---

## 5. Lịch sử eval

| Ngày | Phiên bản | CE pass | RE pass | Tổng kết | Ghi chú |
|------|-----------|---------|---------|----------|---------|
| 2026-08-05 | v1.0 | 3/3 | 2/2 | APPROVED | Tạo mới — học từ mattpocock/skills tdd |
