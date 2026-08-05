---
agent: business-analyst
created: 2026-08-05
author: senior-developer
status: active
---

# EVAL: Business Analyst

> **Mục đích:** Định nghĩa pass/fail criteria cho `business-analyst` agent — Eval-Driven Development (EDD).
> **Khi chạy:** Sau khi sửa `C:/Users/nguye/.claude/agents/business-analyst.md` hoặc thay đổi quy trình WF-FEATURE/WF-STORY trong CLAUDE.md, chạy lại toàn bộ eval.

---

## 1. Mô tả năng lực (Capability Statement)

`business-analyst` bóc tách PRD thành user story chi tiết, vẽ flow nghiệp vụ bằng mermaid, liệt kê edge case (lỗi mạng, dữ liệu rỗng, quyền hạn, đa timezone), và định nghĩa Acceptance Criteria rõ ràng theo Given/When/Then. Agent PHẢI đặt câu hỏi cho Product Manager khi yêu cầu mơ hồ — KHÔNG tự suy diễn để lấp khoảng trống nghiệp vụ.

---

## 2. Capability Evals (kiểm tra năng lực cốt lõi)

### CE-01 — Viết user story đầy đủ Given/When/Then + business flow (mermaid) từ PRD rõ ràng

**Input:**
```
Đã có: docs/prd/PRD-device-register.md
  Goals: Cho phép Admin đăng ký thiết bị Access Control mới vào hệ thống.
  Scope: Tên thiết bị, IP, Serial number (bắt buộc); Serial format KZ-XXXXXXXX.
  Non-goals: Không hỗ trợ đăng ký hàng loạt (bulk import) ở phase này.
Yêu cầu: Business Analyst viết user story chi tiết cho tính năng này.
```

**Output mong đợi:**
- [ ] File `docs/user-stories/US-001-device-register.md` được tạo đúng path §11 CLAUDE.md
- [ ] Đúng format: "Là [vai trò] / Tôi muốn [hành động] / Để [mục đích]"
- [ ] Có ≥ 2 Scenario theo Given/When/Then: 1 happy path (đăng ký thành công) + 1 edge case (serial number sai format hoặc trùng tên)
- [ ] Có mục Quy tắc nghiệp vụ (BR1, BR2...) — VD: BR1 = serial phải unique trong site, BR2 = format KZ-XXXXXXXX
- [ ] Có business flow vẽ bằng mermaid (sequence hoặc flowchart) mô tả luồng đăng ký thiết bị
- [ ] Non-goals "bulk import" từ PRD KHÔNG bị lẫn vào AC của story này

**Grader:** Human (kiểm tra AC đo được, đủ Given/When/Then, mermaid flow khớp nghiệp vụ)

---

### CE-02 — Liệt kê đủ nhóm edge case bắt buộc (lỗi mạng, dữ liệu rỗng, quyền hạn, đa timezone)

**Input:**
```
Feature: Đặt lịch bảo trì thiết bị Access Control theo khung giờ định kỳ.
Context: Hệ thống có user ở nhiều site khác timezone (Hà Nội, HCM, chi nhánh nước ngoài).
Yêu cầu: Business Analyst liệt kê edge case cho feature này.
```

**Output mong đợi:**
- [ ] Edge case nhóm lỗi mạng: VD "Mất kết nối khi đang lưu lịch bảo trì → dữ liệu không bị mất/trùng"
- [ ] Edge case nhóm dữ liệu rỗng: VD "Chưa có thiết bị nào trong site → không cho đặt lịch, hiển thị empty state"
- [ ] Edge case nhóm quyền hạn: VD "User không có quyền Admin/Technician cố đặt lịch → nhận lỗi 403"
- [ ] Edge case nhóm đa timezone: VD "Lịch đặt theo giờ local site nào, hiển thị thế nào cho user ở site khác xem chung"
- [ ] Mỗi edge case có mã EC-X và mô tả đủ để QA viết test case reproduce được (không mơ hồ)

**Grader:** Human (kiểm tra đủ 4 nhóm edge case, mỗi nhóm cụ thể hóa đúng theo feature, không copy generic)

---

### CE-03 — Đặt câu hỏi cho PM khi yêu cầu mơ hồ, KHÔNG tự suy diễn (negative case)

**Input:**
```
PRD: docs/prd/PRD-device-register.md chỉ ghi "Cho phép đăng ký thiết bị mới", KHÔNG nói rõ:
  - Ai có quyền đăng ký (chỉ Admin? hay cả Technician)?
  - Serial number có bắt buộc unique toàn hệ thống hay chỉ trong 1 site?
Yêu cầu: Business Analyst viết user story + AC cho feature này ngay.
```

**Output mong đợi:**
- [ ] Agent KHÔNG tự suy diễn/tự chọn 1 phương án (VD: tự quyết "chỉ Admin" hoặc "unique toàn hệ thống") mà không hỏi
- [ ] Agent ghi rõ mục "Câu hỏi mở cho PM" trong user story draft, liệt kê đúng 2 điểm mơ hồ trên (Q1, Q2...)
- [ ] Agent vẫn có thể soạn phần AC không phụ thuộc vào câu hỏi mở (nếu có), nhưng phần phụ thuộc câu hỏi mở PHẢI đánh dấu rõ "chờ PM xác nhận", không viết AC chắc chắn cho phần chưa rõ
- [ ] Agent KHÔNG escalate vượt cấp lên EM/CTO cho việc này — đúng chain "Escalate lên PM khi yêu cầu mâu thuẫn/mơ hồ"

**Grader:** Human (kiểm tra agent có hỏi đúng chỗ mơ hồ, không bịa ra quyết định nghiệp vụ)

---

## 3. Regression Evals (kiểm tra không bị regression sau khi sửa)

### RE-01 — Routing đúng: Business Analyst được gọi đúng thời điểm trong workflow

**Input:** Dispatcher chạy WF-FEATURE — Product Manager vừa hoàn thành PRD (Bước 1), cần chuyển bước tiếp theo

**Output mong đợi:**
- [ ] Dispatcher gọi Business Analyst ở Bước 2 (Chi tiết hóa user story, viết acceptance criteria) — đúng thứ tự theo CLAUDE.md §4 WF-FEATURE
- [ ] Trong WF-SPRINT, Business Analyst được gọi song song (`∥`) với Tech Lead ở Bước 2/3 (đảm bảo AC top stories rõ ràng trước họp), không tuần tự sai thứ tự
- [ ] Trong WF-STORY (route riêng cho "User story / AC"), Business Analyst là agent DUY NHẤT trong chain — không kéo thêm agent khác không cần thiết
- [ ] Header format đúng: `╔══...║  🤖 BUSINESS ANALYST  (Business Analyst | Cấp L4)`

---

### RE-02 — Artifact bắt buộc đủ khi hoàn thành user story

**Input:** Business Analyst hoàn thành user story cho 1 feature bất kỳ

**Output mong đợi:**
- [ ] `docs/user-stories/US-[XXX]-[feature-slug].md` tồn tại, đúng theo Template `US-template.md`
- [ ] File có nhúng business flow (mermaid) VÀ câu hỏi mở cho PM (nếu có) ngay trong cùng file — không tách file riêng
- [ ] DOCX + PDF được xuất cho `US-*.md` theo §19 CLAUDE.md

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
