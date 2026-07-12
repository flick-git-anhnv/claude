---
agent: qa-engineer
created: 2026-07-12
author: senior-developer
status: active
---

# EVAL: QA Engineer

> **Mục đích:** Định nghĩa pass/fail criteria cho `qa-engineer` agent — Eval-Driven Development (EDD).
> **Khi chạy:** Sau khi sửa `.claude/agents/qa-engineer.md` hoặc thay đổi quy trình test trong CLAUDE.md, chạy lại toàn bộ eval.

---

## 1. Mô tả năng lực (Capability Statement)

`qa-engineer` viết test case theo format Given/When/Then có thể reproduce được, reproduce bug với bằng chứng (screenshot/log) cụ thể, và LUÔN khởi động app thật + xác nhận HTTP 200 trước khi bắt đầu test — không bao giờ test tĩnh. Agent có quyền VETO release khi còn P0/P1 bug chưa fix.

---

## 2. Capability Evals (kiểm tra năng lực cốt lõi)

### CE-01 — Viết test case theo Given/When/Then đúng format với CRUD coverage đầy đủ

**Input:**
```
Feature: Đăng ký thiết bị KZTEK Access Control
Acceptance Criteria:
  - User có role Admin có thể đăng ký thiết bị mới (tên, IP, serial number bắt buộc)
  - Tên thiết bị phải unique trong cùng site
  - Serial number phải đúng format: KZ-XXXXXXXX (2 chữ KZ, gạch ngang, 8 số)
  - User không có role Admin nhận lỗi 403
Yêu cầu: Viết test case cho feature này
```

**Output mong đợi:**
- [ ] File `docs/test-cases/TC-device-register.md` được tạo
- [ ] Mỗi test case có đủ: ID (TC-XXX), Given (điều kiện đầu), When (hành động), Then (kết quả mong đợi)
- [ ] Bao phủ đủ 4 nhóm CRUD coverage: CREATE valid, CREATE invalid (thiếu field, format sai, tên trùng), READ (tìm thiết bị vừa tạo / 404), không cần UPDATE/DELETE nếu feature không bao gồm
- [ ] Có test case 403 cho user không phải Admin (permission test)
- [ ] Test data sử dụng đúng marker: tài khoản `test_admin@test.internal`, thiết bị có prefix `[TEST]`
- [ ] File `docs/test-cases/TEST-DATA-device-register.md` được tạo kèm theo

**Grader:** Human (kiểm tra Given/When/Then có đủ chi tiết reproduce được không)

---

### CE-02 — Reproduce bug với evidence cụ thể

**Input:**
```
Bug report nhận được (sơ bộ):
  "Màn hình danh sách thiết bị bị trắng khi có hơn 100 thiết bị"
Yêu cầu: QA Engineer reproduce và viết bug report đầy đủ
App đang chạy tại: http://localhost:5000
```

**Output mong đợi:**
- [ ] Agent khởi động quy trình: kiểm tra app chạy (HTTP 200), mở DevTools Console + Network
- [ ] Tạo test data: ≥101 thiết bị với marker `[TEST]` + `created_by = "qa-test-agent"`
- [ ] Thực hiện thao tác reproduce đúng các bước, ghi lại kết quả + bằng chứng (screenshot filename hoặc console error log thực tế)
- [ ] File `docs/bugs/BUG-001-device-list-blank.md` có đủ fields: Severity, Priority, Môi trường (Browser/URL/Account/Build), Các bước reproduce (đánh số), Kết quả thực tế (có screenshot/log), Kết quả mong đợi (AC nào bị vi phạm), Tần suất, Workaround
- [ ] Severity được phân loại đúng (blank screen ảnh hưởng toàn bộ user → High/Critical)
- [ ] KHÔNG chỉ mô tả bug mà không có bằng chứng reproduce

**Grader:** Human (kiểm tra bug report có đủ thông tin để dev reproduce lại không)

---

### CE-03 — Từ chối test khi app chưa chạy / VETO khi còn P0/P1 bug

**Input (Case A — app chưa chạy):**
```
Yêu cầu: "Chạy smoke test cho tính năng đăng ký thiết bị trên môi trường local."
Context: Agent thử kết nối http://localhost:5000 → Connection refused (app không chạy)
```

**Output mong đợi (Case A):**
- [ ] Agent KHÔNG giả định app đang chạy và bắt đầu viết kết quả test
- [ ] Agent DỪNG và báo cáo: "App không chạy tại localhost:5000 — không thể thực hiện smoke test"
- [ ] Agent chỉ rõ cần làm gì trước: khởi động app (`npm run dev` / `docker compose up` / ...) rồi mới tiếp tục

**Input (Case B — vẫn còn P0 bug chưa fix):**
```
Yêu cầu: "QA sign-off release v1.2 — deploy production sáng mai."
Context: BUG-003 (Severity: Critical / P0) — màn hình thanh toán bị lỗi 500 — chưa fix.
```

**Output mong đợi (Case B):**
- [ ] Agent KHÔNG sign-off release
- [ ] Agent hiển thị VETO rõ ràng: "VETO release v1.2 — còn BUG-003 (P0/Critical) chưa được fix"
- [ ] Agent escalate lên QA Lead để xác nhận
- [ ] KHÔNG bị áp lực bỏ qua — ghi chú đây là Red Flag "bị áp lực bỏ qua test"

**Grader:** Human (kiểm tra agent dừng đúng cả 2 case)

---

## 3. Regression Evals (kiểm tra không bị regression sau khi sửa)

### RE-01 — Routing đúng: QA Engineer được gọi đúng thời điểm trong workflow

**Input:** Dispatcher chạy WF-BUGFIX — Senior Developer vừa fix xong bug, tạo PR

**Output mong đợi:**
- [ ] Dispatcher gọi QA Engineer ở Bước 4 (Verify fix trên staging, regression test) — đúng thứ tự
- [ ] QA Engineer KHÔNG bị bỏ qua hoặc gộp vào bước khác
- [ ] Header format đúng: `╔══...║  🤖 QA ENGINEER  (QA Engineer | Cấp L5)`

---

### RE-02 — Artifact bắt buộc đủ khi hoàn thành test session

**Input:** QA Engineer hoàn thành test session cho bất kỳ feature nào

**Output mong đợi:**
- [ ] `docs/test-cases/TC-[feature-slug].md` tồn tại với ≥3 test case có Given/When/Then
- [ ] `docs/test-cases/TEST-DATA-[feature-slug].md` tồn tại, ghi rõ test data đã tạo
- [ ] Verification run được ghi trong handoff: timestamp + môi trường + kết quả Pass/Fail

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
| 2026-07-12 | v1.0 | —/3 | —/2 | PENDING | Tạo mới theo EDD (Bước 2.1 PLAN-optimize-framework) |
