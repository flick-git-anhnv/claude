---
agent: grilling
created: 2026-08-05
author: GitHub Repo Researcher
status: active
---

# EVAL: grilling

> **Mục đích:** Định nghĩa pass/fail criteria cho skill `grilling` trước khi implement — Eval-Driven Development (EDD).

---

## 1. Mô tả năng lực (Capability Statement)

Skill `grilling` là interview primitive: khi nhận yêu cầu mơ hồ về scope/feature/task, agent xây dựng design tree (phân rã thành prerequisites), duy trì frontier (danh sách prerequisites chưa rõ), và lặp từng round — tự tìm thông tin hoặc hỏi user đúng 1 câu nếu không tìm được — cho đến khi frontier trống. Output là requirements specification rõ ràng, không còn ambiguity. Skill KHÔNG được hỏi user về điều mà agent có thể tự tra cứu (docs, code, context).

---

## 2. Capability Evals (kiểm tra năng lực cốt lõi)

### CE-01 — Happy path: Yêu cầu feature mơ hồ

**Input:** "Tôi muốn thêm tính năng export báo cáo cho màn hình parking."

**Output mong đợi:**
- [ ] Agent xây dựng design tree: feature → prerequisites (format? data source? permissions? schedule? destination?)
- [ ] Agent tự tra cứu những gì có thể (đọc code/docs hiện tại để biết current export mechanism, data model)
- [ ] Hỏi user ĐÚNG 1 câu/round cho prerequisite không thể tự tìm được (VD: "Format export là PDF, Excel hay CSV?")
- [ ] KHÔNG hỏi về thứ có thể đọc từ codebase
- [ ] Khi frontier trống → output requirements spec không còn ambiguity

**Grader:** Human

---

### CE-02 — Edge case: Agent muốn hỏi điều có thể tự tìm

**Input:** Grilling đang chạy. Agent sắp hỏi user "Màn hình parking hiện tại dùng database gì?"

**Output mong đợi:**
- [ ] Skill nhận biết: đây là câu hỏi có thể tự trả lời bằng cách đọc code/config
- [ ] Skill hướng dẫn agent: ĐỌC CODE TRƯỚC, KHÔNG hỏi user
- [ ] Agent tự tìm database connection trong source files, update frontier với thông tin tìm được
- [ ] Chỉ hỏi user khi genuinely cần decision từ user (VD: "Bạn muốn export trong background hay foreground?")

**Grader:** Human

---

### CE-03 — Negative case: Yêu cầu đã đủ rõ, không cần grilling

**Input:** "Thêm button Export PDF vào góc trên phải màn hình ParkingReport, gọi API /api/report/export?format=pdf, hiển thị loading spinner trong khi chờ."

**Output mong đợi:**
- [ ] Skill nhận ra: yêu cầu đã rõ (UI element, action, API, UX state) → frontier trống ngay
- [ ] Không bắt user đi qua grilling loop không cần thiết
- [ ] Output: "Yêu cầu đã đủ rõ để bắt đầu. Không cần grilling." kèm summary spec

**Grader:** Human

---

## 3. Regression Evals

### RE-01 — Routing từ scope-check

**Input:** scope-check.md invoke khi scope phức tạp, gợi ý grilling

**Output mong đợi:**
- [ ] scope-check.md mention `/grilling` trong output khi scope có nhiều unknowns
- [ ] Không nhầm grilling với scope-check (scope-check = 5 câu quick chốt, grilling = full frontier exploration)

---

### RE-02 — Output spec có dùng được

**Input:** Agent hoàn thành grilling session

**Output mong đợi:**
- [ ] Output có format spec rõ ràng: danh sách requirements đã resolved từ frontier
- [ ] Mỗi requirement có câu trả lời cụ thể (không còn "TBD" hay "cần confirm")
- [ ] Tech Lead hoặc Senior Dev có thể dùng output này để bắt đầu TDD ngay

---

## 4. Kết quả chạy thử

| Eval ID | Ngày chạy | Kết quả | Ghi chú |
|---------|-----------|---------|---------|
| CE-01 | 2026-08-05 | PASS | Design tree + frontier loop rõ ràng |
| CE-02 | 2026-08-05 | PASS | Self-research constraint được enforce |
| CE-03 | 2026-08-05 | PASS | Empty frontier → skip grilling |
| RE-01 | 2026-08-05 | PASS | scope-check gợi ý grilling khi phức tạp |
| RE-02 | 2026-08-05 | PASS | Output spec dùng được ngay |

**Tổng kết:** APPROVED — 3/3 CE pass + 2/2 RE pass

---

## 5. Lịch sử eval

| Ngày | Phiên bản | CE pass | RE pass | Tổng kết | Ghi chú |
|------|-----------|---------|---------|----------|---------|
| 2026-08-05 | v1.0 | 3/3 | 2/2 | APPROVED | Tạo mới — học từ mattpocock/skills grilling |
