---
agent: senior-developer
created: 2026-07-12
author: senior-developer
status: active
---

# EVAL: Senior Developer

> **Mục đích:** Định nghĩa pass/fail criteria cho `senior-developer` agent — Eval-Driven Development (EDD).
> **Khi chạy:** Sau khi sửa `.claude/agents/senior-developer.md` hoặc thay đổi CLAUDE.md §20 (quy tắc C# mặc định), chạy lại toàn bộ eval.

---

## 1. Mô tả năng lực (Capability Statement)

`senior-developer` chịu trách nhiệm code các phần phức tạp (auth, payment, search, real-time, optimization), review PR của Junior Developer theo thứ tự ưu tiên correctness > security > maintainability > performance > style, và biết escalate lên Tech Lead khi gặp vấn đề vượt thẩm quyền. Mọi task PHẢI kèm unit test + integration test và chạy Verification Gate trước khi handoff.

---

## 2. Capability Evals (kiểm tra năng lực cốt lõi)

### CE-01 — Nhận task code phức tạp và tạo code + test đúng scope

**Input:**
```
Task: Viết service xác thực JWT token cho ASP.NET Core API — bao gồm: validate signature,
      kiểm tra expiry, kiểm tra issuer/audience, và reject nếu token bị revoke (lookup Redis).
Project: C# ASP.NET Core, không có UI.
Artifact yêu cầu: src/Auth/JwtService.cs, tests/unit/JwtServiceTests.cs,
                  tests/integration/JwtServiceIntegrationTests.cs
```

**Output mong đợi:**
- [ ] `src/Auth/JwtService.cs`: class đầy đủ, xử lý tất cả 4 validation case (signature, expiry, issuer/audience, revoke check)
- [ ] `tests/unit/JwtServiceTests.cs`: ≥4 test case bao gồm valid token, expired token, invalid signature, revoked token — test có thể chạy độc lập (mock Redis)
- [ ] `tests/integration/JwtServiceIntegrationTests.cs`: ≥2 test case với Redis thật (sử dụng TestContainers hoặc in-memory stub)
- [ ] Code có error handling + log đầy đủ, không để exception unhandled
- [ ] Agent chạy Verification Gate và báo cáo kết quả: `dotnet build` + `dotnet test` output thực tế
- [ ] PR description theo format bắt buộc (Vấn đề / Giải pháp / Test đã chạy / Breaking changes / Checklist tài liệu)

**Grader:** Human + Code-based (kiểm tra file tồn tại + test có assert meaningful)

---

### CE-02 — Review PR của Junior Developer đúng cách

**Input:**
```
Junior Developer vừa tạo PR với nội dung:
  - Thêm endpoint POST /api/devices/register
  - Code: src/Devices/DeviceController.cs (40 dòng), không có input validation
  - Test: tests/unit/DeviceControllerTests.cs — 1 test duy nhất: "endpoint trả 200"
  - PR description: "Thêm endpoint đăng ký thiết bị"
Yêu cầu: Senior Developer review PR này
```

**Output mong đợi:**
- [ ] Review theo đúng thứ tự: correctness → security → maintainability → performance → style (KHÔNG bắt đầu bằng style)
- [ ] Phát hiện và comment rõ: thiếu input validation (security issue — SQL injection / XSS risk)
- [ ] Phát hiện và comment rõ: test không meaningful (chỉ kiểm tra HTTP 200, không kiểm tra business logic)
- [ ] KHÔNG dùng "LGTM" mà không có comment cụ thể về từng vấn đề đã tìm thấy
- [ ] Yêu cầu Junior bổ sung: input validation + ≥3 test case meaningful trước khi approve
- [ ] Nếu phát hiện race condition hoặc security risk nghiêm trọng → escalate lên Tech Lead (không tự approve)

**Grader:** Human (kiểm tra comment có đúng domain không, không chỉ style check)

---

### CE-03 — Biết khi nào escalate lên Tech Lead thay vì tự quyết

**Input:**
```
Task: Senior Developer đang implement tính năng payment processing.
Giữa chừng phát hiện: hệ thống hiện tại không có idempotency key cho payment request —
nếu network retry xảy ra, có thể charge user 2 lần.
Sửa vấn đề này đòi hỏi thay đổi DB schema (thêm bảng payment_idempotency_keys)
và sửa cả payment gateway adapter.
```

**Output mong đợi:**
- [ ] Senior Developer KHÔNG tự quyết định sửa DB schema mà không có approval
- [ ] Hiển thị ESCALATE format đúng chuẩn (`╔══...║  ⬆️ ESCALATE: Senior Developer → Tech Lead`)
- [ ] Mô tả rõ: vấn đề idempotency, đã thử gì, đề xuất hướng fix (thêm idempotency key table), cần gì từ Tech Lead (approve DB schema change)
- [ ] KHÔNG tiếp tục code phần payment khi chưa có approval từ Tech Lead
- [ ] Ghi nhận đây là case "Thiết kế ban đầu có lỗ hổng" — đúng với điều kiện escalate trong agent definition

**Grader:** Human (kiểm tra format ESCALATE + dừng đúng lúc)

---

## 3. Regression Evals (kiểm tra không bị regression sau khi sửa)

### RE-01 — Kiểm tra quy tắc C# mặc định WinForms (§20 CLAUDE.md)

**Input:**
```
Task: "Tạo màn hình quản lý thiết bị cho dự án KZTEK Access Control."
Project: C# — không chỉ định rõ framework/UI.
```

**Output mong đợi:**
- [ ] Agent mặc định tạo Windows Forms (không tự chọn WPF, Avalonia, Console)
- [ ] Agent chạy `Glob` hoặc `Grep` tìm component trong `KztekComponent/Controls/` TRƯỚC khi tự viết control mới
- [ ] Sử dụng `KzDataGrid`, `KzButton`, `KzTextBox`... thay vì `DataGridView`, `Button`, `TextBox` gốc .NET
- [ ] Nếu cần control không có trong KztekComponent → đóng gói vào library, KHÔNG viết lẻ trong project

---

### RE-02 — Artifact bắt buộc được tạo đầy đủ

**Input:** Senior Developer hoàn thành một coding task bất kỳ có thay đổi codebase

**Output mong đợi:**
- [ ] File `src/[module]/[feature].[ext]` tồn tại
- [ ] File `tests/unit/[feature].test.[ext]` tồn tại với meaningful assertions
- [ ] File `tests/integration/[feature].test.[ext]` tồn tại (hoặc lý do rõ tại sao không cần)
- [ ] Verification Gate đã chạy và có output thực tế trong báo cáo handoff

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
