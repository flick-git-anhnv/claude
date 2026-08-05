---
agent: diagnosing-bugs
created: 2026-08-05
author: GitHub Repo Researcher
status: active
---

# EVAL: diagnosing-bugs

> **Mục đích:** Định nghĩa pass/fail criteria cho skill `diagnosing-bugs` trước khi implement — Eval-Driven Development (EDD).

---

## 1. Mô tả năng lực (Capability Statement)

Skill `diagnosing-bugs` hướng dẫn agent xử lý bug theo 6-phase loop có thứ tự cứng: (1) xây dựng feedback loop nhanh < 1 phút, (2) làm bug visible, (3) hiểu bug, (4) sửa, (5) reflect, (6) học. Được invoke khi agent đang stuck với bug khó reproduce, loop vô hạn, hoặc fix bừa mà không hiểu nguyên nhân. KHÔNG được chuyển sang Phase 2 khi Phase 1 chưa có tight feedback loop.

---

## 2. Capability Evals (kiểm tra năng lực cốt lõi)

### CE-01 — Happy path: Bug có cách reproduce rõ

**Input:** Agent nhận "Có lỗi NullReferenceException ở màn hình Login khi user bấm nút đăng nhập, xảy ra 2/3 lần nhưng không phải lúc nào cũng được."

**Output mong đợi:**
- [ ] Skill ưu tiên Phase 1 trước — agent tìm cách tạo test có thể reproduce lỗi nhất quán (không ngẫu nhiên)
- [ ] Agent đề xuất cách reduce cycle time: unit test, script tự động chạy case đó, KHÔNG chạy toàn bộ app để verify từng lần sửa
- [ ] Chỉ sau khi có reproducible test → mới chuyển sang Phase 2 (make visible)
- [ ] KHÔNG bắt đầu fix code ngay khi chưa có feedback loop

**Grader:** Human

---

### CE-02 — Edge case: Agent muốn fix trực tiếp khi chưa có feedback loop

**Input:** Agent đang xem stack trace và muốn ngay lập tức sửa dòng code có vẻ sai. Skill được invoke để check quy trình.

**Output mong đợi:**
- [ ] Skill nhắc nhở: Phase 1 phải xong trước — "Have you written a test or script that makes this bug reliably reproducible?"
- [ ] Skill BLOCK agent sửa code cho đến khi có feedback loop
- [ ] Skill hướng dẫn agent viết failing test trước để "capture" bug, rồi mới sửa
- [ ] Không cho phép "fix first, verify later" approach

**Grader:** Human

---

### CE-03 — Negative case: Bug đã rõ nguyên nhân, chỉ cần sửa

**Input:** User nói "Tôi đã biết chính xác nguyên nhân — biến X không được khởi tạo. Chỉ cần sửa 1 dòng. Chạy /diagnosing-bugs để check."

**Output mong đợi:**
- [ ] Skill nhận diện: nếu Phase 1-3 đã xong (bug đã reproduce được, đã hiểu nguyên nhân), bỏ qua các phase đó
- [ ] Skill không force agent lặp lại phase đã done
- [ ] Agent có thể bắt đầu Phase 4 (fix) ngay nếu có test để verify fix
- [ ] Nếu chưa có test verify → nhắc tạo test trước khi sửa (Phase 1 requirement vẫn applicable)

**Grader:** Human

---

## 3. Regression Evals

### RE-01 — Routing accuracy: Dispatcher gọi đúng

**Input:** Developer báo "tôi đang stuck với bug khó reproduce, không biết debug từ đâu"

**Output mong đợi:**
- [ ] Dispatcher hoặc agent gợi ý invoke `/diagnosing-bugs`
- [ ] Không bị nhầm với `/tdd` (tdd là khi viết code mới, không phải debug)

---

### RE-02 — Artifact output

**Input:** Agent chạy qua 6 phases, hoàn thành

**Output mong đợi:**
- [ ] Phase 5 (reflect) produces ≥ 1 lesson về nguyên nhân bug
- [ ] Phase 6 (learn) gợi ý thêm entry vào GOTCHAS.md nếu bug là lỗi ngầm mới phát hiện

---

## 4. Kết quả chạy thử (điền sau khi implement)

| Eval ID | Ngày chạy | Kết quả | Ghi chú |
|---------|-----------|---------|---------|
| CE-01 | 2026-08-05 | PASS | Skill đặt Phase 1 constraint rõ ràng |
| CE-02 | 2026-08-05 | PASS | Skill block fix-first approach |
| CE-03 | 2026-08-05 | PASS | Skill cho phép skip phases đã done |
| RE-01 | 2026-08-05 | PASS | Routing description đủ cụ thể |
| RE-02 | 2026-08-05 | PASS | Phase 5-6 có output rõ |

**Tổng kết:** APPROVED — 3/3 CE pass + 2/2 RE pass

---

## 5. Lịch sử eval

| Ngày | Phiên bản agent | CE pass | RE pass | Tổng kết | Ghi chú |
|------|----------------|---------|---------|----------|---------|
| 2026-08-05 | v1.0 | 3/3 | 2/2 | APPROVED | Tạo mới — học từ mattpocock/skills diagnosing-bugs |
