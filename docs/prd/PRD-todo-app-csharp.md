# PRD-todo-app-csharp: Ứng dụng Quản lý Công Việc (To-Do App) — C# Desktop/Console

> **Phiên bản:** 1.0
> **Tác giả:** Product Manager
> **Ngày tạo:** 2026-06-02
> **Trạng thái:** Draft — chờ BA review
> **Reviewer:** Business Analyst, Tech Lead

---

## 1. Tổng quan (Executive Summary)

| Trường | Nội dung |
|---|---|
| **Vấn đề** | Người dùng cá nhân thiếu công cụ đơn giản, nhanh chóng để ghi nhớ và theo dõi công việc hàng ngày ngay trên máy tính mà không cần kết nối Internet hay tài khoản đăng nhập |
| **Đối tượng** | Người dùng cá nhân (sinh viên, nhân viên văn phòng) sử dụng máy tính Windows chạy .NET |
| **Giá trị mang lại** | Ứng dụng nhẹ, chạy offline, không phụ thuộc cloud, giúp người dùng tổ chức công việc hiệu quả trong vài giây |
| **Nền tảng** | Console Application hoặc Desktop (WinForms/WPF) — C# .NET 8 |
| **Phạm vi MVP** | CRUD công việc + đánh dấu hoàn thành + lưu trữ local |

---

## 2. Vấn đề cần giải quyết (Problem Statement)

### 2.1 Bối cảnh

Người dùng thường xuyên ghi công việc vào giấy note, file text, hoặc ứng dụng bên thứ ba đòi hỏi đăng nhập tài khoản. Các giải pháp hiện tại có vấn đề:

- **Giấy note / file text:** Không có cấu trúc, không thể đánh dấu hoàn thành, dễ mất.
- **Ứng dụng cloud (Todoist, TickTick):** Đòi hỏi kết nối Internet, tài khoản, quá nhiều tính năng thừa.
- **Excel:** Cồng kềnh, khởi động chậm, không phù hợp cho ghi nhanh.

### 2.2 Pain points cụ thể

| # | Pain Point | Mức độ nghiêm trọng |
|---|---|---|
| P1 | Quên mất việc cần làm trong ngày | Cao |
| P2 | Không biết việc nào đã xong, việc nào chưa | Cao |
| P3 | Phải mở nhiều ứng dụng để tìm lại task cũ | Trung bình |
| P4 | Không thể ưu tiên (việc nào làm trước) | Trung bình |

---

## 3. Mục tiêu sản phẩm (Goals)

| ID | Mục tiêu | Chỉ số đo |
|---|---|---|
| G1 | Cho phép người dùng tạo, xem, sửa, xóa công việc nhanh chóng | Thao tác ≤ 3 bước từ màn hình chính |
| G2 | Cho phép đánh dấu hoàn thành công việc và lọc theo trạng thái | Hoạt động đúng 100% test case AC |
| G3 | Dữ liệu được lưu tự động, không mất khi tắt ứng dụng | Dữ liệu tồn tại sau khi restart |
| G4 | Ứng dụng khởi động nhanh và phản hồi mượt mà | Thời gian khởi động ≤ 2 giây |
| G5 | Giao diện đơn giản, người dùng không cần hướng dẫn | Onboarding ≤ 1 phút |

---

## 4. Non-goals (Những gì KHÔNG làm trong phiên bản này)

| # | Không làm | Lý do |
|---|---|---|
| NG1 | Đồng bộ cloud / multi-device | Ngoài phạm vi MVP, tăng độ phức tạp |
| NG2 | Hệ thống nhắc nhở / notification | Cần background service, để phiên bản sau |
| NG3 | Chia sẻ công việc với người khác (collaboration) | MVP tập trung single-user |
| NG4 | Recurring tasks (công việc lặp lịch) | Logic phức tạp, để v2 |
| NG5 | Sub-tasks (công việc con) | Tăng độ phức tạp data model |
| NG6 | Giao diện đa ngôn ngữ | Chỉ hỗ trợ tiếng Việt + tiếng Anh tùy cấu hình mặc định |
| NG7 | Tích hợp Calendar, Google Tasks | Ngoài phạm vi |
| NG8 | Import/Export từ file bên ngoài | Để v1.1 |

---

## 5. Đối tượng người dùng (Target Users / Personas)

### Persona A — "Minh — Sinh viên bận rộn"
- **Tuổi:** 20–25
- **Thiết bị:** Laptop Windows, dùng nhiều cho học tập
- **Thói quen:** Ghi việc vào điện thoại hoặc giấy, thường quên
- **Nhu cầu:** Tạo task nhanh, thấy danh sách rõ ràng, đánh dấu xong ngay
- **Frustration:** Ứng dụng nhiều quảng cáo, phải đăng nhập, tốn data

### Persona B — "Lan — Nhân viên văn phòng"
- **Tuổi:** 27–40
- **Thiết bị:** PC Windows tại văn phòng
- **Thói quen:** Dùng giấy sticky note trên màn hình
- **Nhu cầu:** Quản lý việc cá nhân song song công việc, muốn ưu tiên rõ ràng
- **Frustration:** Ghi giấy dễ mất, không biết hôm nay đã xong bao nhiêu việc

---

## 6. Tính năng cốt lõi (Features — Phân loại MoSCoW)

### Must Have (M) — MVP bắt buộc

| ID | Tính năng | Mô tả |
|---|---|---|
| F01 | Tạo công việc mới | Nhập tiêu đề, mô tả tùy chọn, lưu vào danh sách |
| F02 | Xem danh sách công việc | Hiển thị tất cả task, phân biệt rõ done/pending |
| F03 | Sửa công việc | Chỉnh sửa tiêu đề, mô tả của task đã tạo |
| F04 | Xóa công việc | Xóa vĩnh viễn task khỏi danh sách |
| F05 | Đánh dấu hoàn thành | Toggle trạng thái Pending ↔ Completed |
| F06 | Lưu trữ local (persistence) | Tự động lưu vào file JSON hoặc SQLite khi thay đổi |
| F07 | Tải dữ liệu khi khởi động | Load đúng dữ liệu đã lưu từ lần trước |

### Should Have (S) — Ưu tiên cao, làm nếu đủ thời gian

| ID | Tính năng | Mô tả |
|---|---|---|
| F08 | Lọc theo trạng thái | Xem All / Pending / Completed |
| F09 | Mức độ ưu tiên (Priority) | Gán Low / Medium / High cho từng task |
| F10 | Ngày hạn hoàn thành (Due Date) | Gán deadline, hiển thị task quá hạn rõ |

### Could Have (C) — Làm nếu còn sprint capacity

| ID | Tính năng | Mô tả |
|---|---|---|
| F11 | Tìm kiếm task theo từ khóa | Search trong tiêu đề / mô tả |
| F12 | Sắp xếp danh sách | Sort theo tên / ngày tạo / ưu tiên / due date |
| F13 | Đếm số task hoàn thành / còn lại | Summary ở cuối danh sách |

### Won't Have (W) — Không làm trong phiên bản này

| ID | Tính năng |
|---|---|
| F14 | Cloud sync |
| F15 | Reminder / Notification |
| F16 | Collaboration |

---

## 7. Acceptance Criteria cấp cao

> Chi tiết Given/When/Then sẽ do Business Analyst viết trong `docs/user-stories/US-*.md`.

- [ ] **AC-01 — Tạo task:** Khi user nhập tiêu đề (≥ 1 ký tự) và xác nhận, task mới xuất hiện trong danh sách với trạng thái "Pending".
- [ ] **AC-02 — Validation tạo task:** Khi tiêu đề rỗng, hệ thống hiển thị thông báo lỗi, không tạo task.
- [ ] **AC-03 — Xem danh sách:** Danh sách hiển thị đúng tất cả task đã tạo với thông tin: tiêu đề, trạng thái, ngày tạo.
- [ ] **AC-04 — Sửa task:** Khi user thay đổi tiêu đề/mô tả và lưu, nội dung cập nhật ngay trong danh sách.
- [ ] **AC-05 — Xóa task:** Sau khi xác nhận xóa, task biến mất hoàn toàn khỏi danh sách và không khôi phục được.
- [ ] **AC-06 — Đánh dấu hoàn thành:** Khi toggle sang Completed, task hiển thị khác biệt rõ (gạch ngang / màu mờ). Khi toggle lại thành Pending, task trở về trạng thái ban đầu.
- [ ] **AC-07 — Persistence (lưu tự động):** Mọi thay đổi được lưu vào file local ngay sau thao tác. Sau khi tắt và mở lại, dữ liệu nguyên vẹn.
- [ ] **AC-08 — Khởi động:** Ứng dụng load xong và sẵn sàng dùng trong vòng 2 giây trên máy cấu hình tối thiểu (Core i3, 4GB RAM).
- [ ] **AC-09 — Lọc trạng thái (F08):** User có thể chọn xem All / Pending / Completed, danh sách cập nhật đúng ngay lập tức.
- [ ] **AC-10 — Priority (F09):** User có thể gán Priority khi tạo hoặc sửa task; task hiển thị nhãn priority tương ứng.

---

## 8. Metric đo lường thành công

| Metric | Mục tiêu | Cách đo |
|---|---|---|
| Tỷ lệ hoàn thành AC MVP | 100% AC-01 đến AC-08 pass | QA sign-off report |
| Thời gian khởi động ứng dụng | ≤ 2 giây | Benchmark trên máy tối thiểu |
| Thời gian tạo task (từ click đến save) | ≤ 5 giây | Manual test với user persona |
| Tỷ lệ crash khi dùng bình thường | 0 crash trong 30 phút sử dụng liên tục | Stress test QA |
| Dữ liệu không bị mất khi restart | 100% dữ liệu khôi phục | Regression test |
| Test coverage (unit test) | ≥ 80% cho business logic | Coverage report từ dotnet test |

---

## 9. Timeline sơ bộ

> Timeline chi tiết theo sprint sẽ do Project Manager xác nhận sau khi EM estimate resource.

| Giai đoạn | Nội dung | Ước tính |
|---|---|---|
| **Phase 0 — Analysis** | BA viết User Story + AC, Tech Lead viết TDD | 2–3 ngày |
| **Phase 1 — Development MVP** | Implement F01–F07 (Must Have) | 5–7 ngày |
| **Phase 2 — Should Have** | Implement F08–F10 | 2–3 ngày |
| **Phase 3 — QA & Polish** | Testing, bug fix, code review | 2–3 ngày |
| **Phase 4 — Release** | Package, deploy, documentation | 1 ngày |
| **Tổng ước tính** | | **12–17 ngày làm việc** |

---

## 10. Phụ thuộc & Rủi ro

### 10.1 Phụ thuộc

| # | Phụ thuộc | Ghi chú |
|---|---|---|
| D1 | Quyết định nền tảng: Console App hay WinForms/WPF | Tech Lead quyết định trong TDD |
| D2 | Quyết định storage: JSON file hay SQLite | Tech Lead quyết định — ảnh hưởng F06/F07 |
| D3 | .NET 8 SDK cài đặt trên máy dev | DevOps Engineer xác nhận |

### 10.2 Rủi ro

| # | Rủi ro | Xác suất | Mức ảnh hưởng | Mitigation |
|---|---|---|---|---|
| R1 | Chọn WinForms/WPF tăng thời gian dev do phải thiết kế UI | Trung bình | Cao | Tech Lead chọn Console App cho MVP; UI nâng cấp ở v2 nếu cần |
| R2 | File JSON bị corrupt khi app crash giữa chừng khi ghi | Thấp | Cao | Dùng write-then-rename hoặc SQLite transaction để đảm bảo atomicity |
| R3 | Scope creep — user yêu cầu thêm tính năng Should/Could trong sprint | Cao | Trung bình | PM lock scope MoSCoW trước sprint; mọi thay đổi phải qua PM |
| R4 | Thiếu test coverage dẫn đến regression | Trung bình | Cao | Tech Lead yêu cầu ≥ 80% coverage trước khi merge |

### 10.3 Câu hỏi mở (Open Questions)

| # | Câu hỏi | Cần ai trả lời | Deadline |
|---|---|---|---|
| OQ1 | Console App hay WinForms/WPF cho MVP? | Tech Lead | Trước Phase 0 kết thúc |
| OQ2 | Storage: JSON file hay SQLite? | Tech Lead | Trước Phase 0 kết thúc |
| OQ3 | Có cần hỗ trợ Windows 10 trở xuống không? | EM | Trước Phase 1 bắt đầu |
| OQ4 | Tên file lưu trữ và vị trí mặc định (AppData hay cùng thư mục exe)? | Tech Lead | Trước Phase 1 bắt đầu |

---

## 11. Định nghĩa DONE (Definition of Done — cấp sản phẩm)

Sản phẩm được coi là DONE khi:

- [ ] 100% Acceptance Criteria từ AC-01 đến AC-08 pass QA
- [ ] Test coverage unit test ≥ 80% cho business logic layer
- [ ] Không còn bug P0 / P1 nào open
- [ ] Code đã được Tech Lead review và merge vào nhánh main
- [ ] File lưu trữ local hoạt động đúng sau 5 lần restart liên tiếp
- [ ] Documentation Writer hoặc Dev tạo README cơ bản hướng dẫn chạy ứng dụng
- [ ] DevOps Lead đã verify build ra file `.exe` chạy được trên máy sạch (không cần cài VS)

---

*Tài liệu này là đầu vào chính thức cho Business Analyst (US + AC chi tiết), UI/UX Designer (nếu chọn WinForms/WPF), và Tech Lead (TDD + Technical Design).*
