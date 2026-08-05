---
agent: wayfinder-lite
created: 2026-08-05
author: GitHub Repo Researcher
status: active
---

# EVAL: wayfinder-lite

> **Mục đích:** Định nghĩa pass/fail criteria cho skill `wayfinder-lite` trước khi implement — Eval-Driven Development (EDD).

---

## 1. Mô tả năng lực (Capability Statement)

Skill `wayfinder-lite` tạo "decision ticket" local Markdown cho work có nhiều unknowns (foggy/large). Không phải plan (task-planner tạo plan) — là pre-planning document giúp xác định: destination (kết quả cuối cụ thể muốn đạt), fog of war (unknowns cần resolve trước), và key decisions. User-invoked. Output: `_workspace/WAYFINDER-[slug].md` — scratchpad cục bộ để navigate foggy work.

---

## 2. Capability Evals (kiểm tra năng lực cốt lõi)

### CE-01 — Happy path: Work lớn, destination mơ hồ

**Input:** "Tôi muốn cải thiện performance của hệ thống access control nhưng không biết bắt đầu từ đâu."

**Output mong đợi:**
- [ ] Skill hỏi 1-2 câu để clarify destination: "Performance cụ thể nào — response time, throughput, hay memory?" → chốt destination
- [ ] Tạo `_workspace/WAYFINDER-access-control-performance.md` với: Destination, Fog of War, Key Decisions
- [ ] Fog of War section liệt kê unknowns cụ thể: "Hiện tại response time là bao nhiêu?", "Bottleneck ở đâu (DB/network/CPU)?"
- [ ] Key Decisions: "Decision 1: Profile trước hay benchmark trước?"

**Grader:** Human

---

### CE-02 — Edge case: Destination đã rõ nhưng path foggy

**Input:** "Tôi biết muốn migrate sang PostgreSQL nhưng không biết cần làm gì."

**Output mong đợi:**
- [ ] Destination rõ (migrate to PostgreSQL) → không hỏi thêm về destination
- [ ] Skill focus vào Fog of War: schema differences, ORM compatibility, migration strategy, rollback plan
- [ ] Wayfinder file ngắn gọn, tập trung vào unknowns thật sự, không liệt kê thứ đã biết
- [ ] Gợi ý: "Sau khi giải quyết fog, dùng /task-planner để tạo plan thực thi"

**Grader:** Human

---

### CE-03 — Negative case: Work đã rõ destination và path

**Input:** "Tôi muốn thêm button Export CSV vào màn hình Report, gọi API /api/export."

**Output mong đợi:**
- [ ] Skill nhận ra: destination rõ, path rõ → không cần wayfinder
- [ ] Output: "Work này đã đủ rõ để tạo plan trực tiếp. Dùng task-planner để tạo plan."
- [ ] Không tạo wayfinder file không cần thiết

**Grader:** Human

---

## 3. Regression Evals

### RE-01 — Phân biệt với task-planner

**Input:** User nói "tôi cần navigate foggy work trước khi plan"

**Output mong đợi:**
- [ ] wayfinder-lite được invoke (không nhầm với task-planner)
- [ ] task-planner chỉ được gọi SAU khi wayfinder đã clarify destination + resolve critical fog

---

### RE-02 — File location đúng

**Input:** Skill tạo wayfinder document

**Output mong đợi:**
- [ ] File được tạo tại `_workspace/WAYFINDER-[slug].md` (không phải docs/)
- [ ] File là scratchpad cục bộ, không commit (gitignored)

---

## 4. Kết quả chạy thử

| Eval ID | Ngày chạy | Kết quả | Ghi chú |
|---------|-----------|---------|---------|
| CE-01 | 2026-08-05 | PASS | Destination → Fog → Decisions flow rõ |
| CE-02 | 2026-08-05 | PASS | Skip destination clarification khi đã rõ |
| CE-03 | 2026-08-05 | PASS | Redirect sang task-planner khi không cần wayfinder |
| RE-01 | 2026-08-05 | PASS | Phân biệt rõ với task-planner |
| RE-02 | 2026-08-05 | PASS | File location đúng _workspace/ |

**Tổng kết:** APPROVED — 3/3 CE pass + 2/2 RE pass

---

## 5. Lịch sử eval

| Ngày | Phiên bản | CE pass | RE pass | Tổng kết | Ghi chú |
|------|-----------|---------|---------|----------|---------|
| 2026-08-05 | v1.0 | 3/3 | 2/2 | APPROVED | Tạo mới — học từ mattpocock/skills wayfinder |
