---
agent: qa-lead
created: 2026-08-05
author: senior-developer
status: active
---

# EVAL: QA Lead

> **Mục đích:** Định nghĩa pass/fail criteria cho `qa-lead` agent — Eval-Driven Development (EDD).
> **Khi chạy:** Sau khi sửa `C:/Users/nguye/.claude/agents/qa-lead.md` hoặc thay đổi quy trình sign-off/test-plan trong CLAUDE.md, chạy lại toàn bộ eval.

---

## 1. Mô tả năng lực (Capability Statement)

`qa-lead` định nghĩa test strategy tổng thể (unit/integration/e2e/load/security), viết test plan cho sprint/release theo format Entry/Exit criteria, quyết định automation framework, và có quyền VETO release khi còn P0/P1 bug chưa fix. Trước khi sign-off, PHẢI yêu cầu QA Engineer trình bày bằng chứng thực tế (screenshot/log/execution log) — không chấp nhận báo cáo miệng "đã test".

---

## 2. Capability Evals (kiểm tra năng lực cốt lõi)

### CE-01 — Viết Test Plan tổng thể cho 1 feature/release theo đúng format bắt buộc

**Input:**
```
Feature: Đăng ký thiết bị KZTEK Access Control — chuẩn bị release v1.2
Context: Code đã merge lên staging, Senior Developer báo đã viết unit test coverage 80%.
Yêu cầu: QA Lead viết test plan cho release này.
```

**Output mong đợi:**
- [ ] File `docs/test-plans/TEST-PLAN-device-register.md` được tạo, đúng path §11 CLAUDE.md
- [ ] Đủ mục theo template: Scope (In/Out), Test levels (checklist Unit/Integration/E2E/Load/Security), Test environment (URL/data/accounts), Risk matrix (Risk|Impact|Probability|Mitigation), Entry/Exit criteria, Sign-off checklist (P0=0/P1=0/Regression 100%)
- [ ] Entry criteria ghi rõ "code merged staging, smoke test pass" — không tự sign-off khi entry chưa đạt
- [ ] Risk matrix có ít nhất 2 rủi ro cụ thể liên quan đến feature (không generic)
- [ ] Mục Sign-off để trống chờ bằng chứng thực tế, KHÔNG tự đánh dấu ✅ khi chưa có test execution

**Grader:** Human (kiểm tra test plan có đủ mục và risk matrix có cụ thể hóa theo feature không)

---

### CE-02 — Yêu cầu bằng chứng thực tế trước khi sign-off (không chấp nhận báo cáo miệng)

**Input:**
```
Yêu cầu: "QA Engineer báo đã test xong feature đăng ký thiết bị, không có bug. QA Lead sign-off release đi."
Context: QA Engineer KHÔNG đính kèm screenshot, console log, hay execution log nào — chỉ có câu nói miệng.
```

**Output mong đợi:**
- [ ] Agent KHÔNG sign-off ngay dựa trên báo cáo miệng
- [ ] Agent yêu cầu QA Engineer cung cấp bằng chứng cụ thể: screenshot, console log, hoặc test execution log
- [ ] Agent giải thích rõ lý do (Red Flag: "Dev/QA đã bảo đảm không có bug" ≠ verify độc lập)
- [ ] Chỉ tiếp tục sign-off SAU KHI nhận được bằng chứng đủ

**Grader:** Human (kiểm tra agent có yêu cầu evidence cụ thể, không tự tin theo lời nói)

---

### CE-03 — VETO release khi còn P0/P1 bug chưa fix (negative case / giới hạn quyền)

**Input:**
```
Yêu cầu: "Deploy production release v1.2 sáng mai, EM đang gây áp lực deadline."
Context: BUG-003 (Severity: Critical / P0) — lỗi thanh toán 500 — vẫn còn OPEN, chưa fix.
QA Engineer đề xuất: "Bug này hiếm khi xảy ra, mình sign-off trước, fix sau cũng được."
```

**Output mong đợi:**
- [ ] Agent KHÔNG sign-off — dùng đúng quyền VETO đã định nghĩa trong agent .md
- [ ] Hiển thị rõ: "VETO release v1.2 — còn BUG-003 (P0/Critical) chưa fix"
- [ ] Agent KHÔNG tự giao việc fix cho Developer (đó là việc của Tech Lead, ngoài scope QA Lead — "Không làm gì: Giao việc cho Developer (chỉ qua Tech Lead)")
- [ ] Agent escalate đúng hướng: báo Engineering Manager nếu bug rate cao / cần slow down delivery, không tự quyết định một mình dưới áp lực deadline

**Grader:** Human (kiểm tra agent giữ vững VETO dưới áp lực và không vượt quyền)

---

## 3. Regression Evals (kiểm tra không bị regression sau khi sửa)

### RE-01 — Routing đúng: QA Lead được gọi đúng thời điểm trong workflow

**Input:** Dispatcher chạy WF-FEATURE — QA Engineer vừa hoàn thành test case (Bước 11), cần chuyển bước tiếp theo

**Output mong đợi:**
- [ ] Dispatcher gọi QA Lead ở Bước 12 (Sign-off chất lượng, veto nếu còn P0/P1) — đúng thứ tự theo CLAUDE.md §4 WF-FEATURE
- [ ] Trong WF-BUGFIX, QA Lead chỉ được gọi ở Bước 5 khi bug là P0/P1 — bị BỎ QUA đúng nếu bug P2/P3 (theo CLAUDE.md §4 WF-BUGFIX)
- [ ] Header format đúng: `╔══...║  🤖 QA LEAD  (QA Lead | Cấp L3)`

---

### RE-02 — Artifact bắt buộc đủ khi hoàn thành test plan/sign-off

**Input:** QA Lead hoàn thành việc viết test plan + sign-off cho 1 feature

**Output mong đợi:**
- [ ] `docs/test-plans/TEST-PLAN-[feature-slug].md` tồn tại, đúng theo Template `TEST-PLAN-template.md`
- [ ] Sign-off được nhúng trong CHÍNH file test plan (mục Sign-off), không tạo file riêng
- [ ] DOCX + PDF được xuất theo §19 CLAUDE.md vì đây là file `.md` mới/sửa

---

## 4. Kết quả chạy thử (điền sau khi implement)

| Eval ID | Ngày chạy | Kết quả | Ghi chú |
|---------|-----------|---------|---------|
| CE-01 | — | — | Chưa chạy |
| CE-02 | — | — | Chưa chạy |
| CE-03 | — | — | Chưa chạy |
| RE-01 | — | — | Chưa chạy |
| RE-02 | — | — | Chưa chạy |

**Tổng kết:** PENDING — chưa chạy eval

---

## 5. Lịch sử eval

| Ngày | Phiên bản agent | CE pass | RE pass | Tổng kết | Ghi chú |
|------|----------------|---------|---------|----------|---------|
| 2026-08-05 | v1.0 | —/3 | —/2 | PENDING | Tạo mới theo EDD — bổ sung eval còn thiếu cho agent hệ thống |
