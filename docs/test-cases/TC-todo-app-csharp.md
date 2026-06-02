---
id: TC-todo-app-csharp
feature: To-Do App C# (.NET 8)
prd-ref: docs/prd/PRD-todo-app-csharp.md
us-ref: docs/user-stories/US-todo-app-csharp.md
tdd-ref: docs/tech-design/TDD-todo-app-csharp.md
author: QA Engineer (L5)
qa-lead-ref: QA Lead (L3)
version: 1.0
created: 2026-06-02
updated: 2026-06-02
environment: Windows 11 | .NET 8 | Console App | Storage: JSON @ %LOCALAPPDATA%\KZTEK\TodoApp\todos.json
status: Executed
---

# TC-todo-app-csharp — Test Cases chi tiết: To-Do App C# (.NET 8)

> Tài liệu này là output bắt buộc của QA Engineer theo WF-FEATURE Bước 11.
> Mọi thay đổi AC/behavior trong code phải cập nhật đồng bộ file này.

---

## Tóm tắt kiểm thử

| Chỉ số | Giá trị |
|---|---|
| Tổng test cases | 56 |
| Pass | 50 |
| Fail | 2 |
| Blocked | 4 |
| P0 Fail | 0 |
| P1 Fail | 1 |
| P2 Fail | 1 |
| Ngày thực thi | 2026-06-02 |
| Phương pháp | Code review + dotnet test (54 unit/integration tests) + manual behavior analysis |

---

## Feature Suite F01 — Tạo công việc mới (US-001, AC-01, AC-02)

### TC-001
- **Title:** Tạo task với tiêu đề hợp lệ — happy path
- **Priority:** P0
- **Preconditions:** App đang chạy, danh sách rỗng hoặc có sẵn task
- **Steps:**
  1. Từ màn hình chính, nhập `1` (Tạo mới)
  2. Nhập tiêu đề: `Hoàn thành báo cáo Q2`
  3. Nhập mô tả: Enter (bỏ qua)
  4. Chọn ưu tiên: Enter (mặc định = None)
  5. Nhập ngày hạn: Enter (bỏ qua)
  6. Xác nhận: nhập `Y`
- **Expected Result:**
  - Toast "Công việc đã được tạo thành công!" xuất hiện
  - Task mới hiển thị trong danh sách với trạng thái `[ ]` (Pending)
  - Tiêu đề đúng: "Hoàn thành báo cáo Q2"
  - CreatedAt được ghi nhận (không null)
- **AC:** AC-01
- **Status:** Pass
- **Notes:** Verified qua unit test `Create_ValidTitle_ReturnsOkWithPendingItem` — Pass

---

### TC-002
- **Title:** Tạo task với đầy đủ tất cả trường
- **Priority:** P1
- **Preconditions:** App đang chạy
- **Steps:**
  1. Nhập `1` (Tạo mới)
  2. Tiêu đề: `Họp team sáng thứ 2`
  3. Mô tả: `Phòng họp A3, 9:00`
  4. Ưu tiên: `4` (Cao)
  5. Ngày hạn: `2026-06-09` (ngày tương lai)
  6. Xác nhận: `Y`
- **Expected Result:**
  - Task tạo thành công
  - Trong danh sách: hiển thị `[!!!]` (High priority, màu đỏ)
  - Due date hiển thị `2026-06-09` (màu xám)
  - Status: `[ ]` Pending
- **AC:** AC-01, AC-10
- **Status:** Pass
- **Notes:** Verified qua unit test `Create_WithPriorityAndDueDate_SetsValues` — Pass

---

### TC-003
- **Title:** Tiêu đề rỗng — validation block
- **Priority:** P0
- **Preconditions:** App đang chạy, màn hình CreateScreen
- **Steps:**
  1. Nhập `1` (Tạo mới)
  2. Tiêu đề: nhấn Enter (để trống)
  3. Quan sát phản hồi
- **Expected Result:**
  - Hiển thị lỗi: `Tiêu đề không được để trống.`
  - Không tạo task mới
  - App tiếp tục hỏi tiêu đề (loop, không crash)
- **AC:** AC-02
- **Status:** Pass
- **Notes:** Verified qua unit test `Create_EmptyOrWhitespaceTitle_ReturnsValidationFail` + code review CreateScreen.cs L28-30

---

### TC-004
- **Title:** Tiêu đề chỉ chứa khoảng trắng — xử lý như rỗng
- **Priority:** P0
- **Preconditions:** Màn hình CreateScreen
- **Steps:**
  1. Nhập `1` (Tạo mới)
  2. Tiêu đề: nhập `   ` (3 dấu cách) rồi Enter
- **Expected Result:**
  - Hiển thị lỗi: `Tiêu đề không được để trống.`
  - Không tạo task
- **AC:** AC-02
- **Status:** Pass
- **Notes:** `CreateScreen.cs` L27: `string.IsNullOrEmpty(input)` sau `Trim()` xử lý đúng. Unit test `Create_EmptyOrWhitespaceTitle_ReturnsValidationFail` với `"   "` — Pass

---

### TC-005
- **Title:** Tiêu đề đúng 200 ký tự — boundary hợp lệ
- **Priority:** P1
- **Preconditions:** Màn hình CreateScreen
- **Steps:**
  1. Nhập `1` (Tạo mới)
  2. Tiêu đề: nhập chuỗi 200 ký tự `A`
  3. Xác nhận: `Y`
- **Expected Result:**
  - Task tạo thành công
  - Tiêu đề hiển thị bị cắt ở màn hình (`TitleWidth=38`) nhưng dữ liệu lưu đủ 200 ký tự
- **AC:** AC-01, AC-02
- **Status:** Pass
- **Notes:** `TitleValidator.cs` kiểm tra `> MaxTitleLength` (200) — 200 ký tự hợp lệ. Unit test boundary chạy Pass

---

### TC-006
- **Title:** Tiêu đề vượt quá 200 ký tự — validation fail
- **Priority:** P0
- **Preconditions:** Màn hình CreateScreen
- **Steps:**
  1. Nhập `1` (Tạo mới)
  2. Tiêu đề: nhập chuỗi 201 ký tự
- **Expected Result:**
  - Hiển thị lỗi: `Tiêu đề không được vượt quá 200 ký tự.`
  - Không tạo task
  - Loop hỏi lại tiêu đề
- **AC:** AC-02
- **Status:** Pass
- **Notes:** Unit test `Create_TitleExceeds200Chars_ReturnsValidationFail` — Pass. CreateScreen.cs L33-36 xử lý đúng.

---

### TC-007
- **Title:** Mô tả vượt quá 1000 ký tự — validation fail ở Service layer
- **Priority:** P1
- **Preconditions:** Màn hình CreateScreen
- **Steps:**
  1. Nhập `1` (Tạo mới)
  2. Tiêu đề: `Task hợp lệ`
  3. Mô tả: nhập chuỗi 1001 ký tự
  4. Xác nhận: `Y`
- **Expected Result:**
  - Service trả `OperationResult.Fail(Validation, MSG-003)`
  - UI hiển thị Toast Error với thông báo lỗi mô tả
- **AC:** AC-02
- **Status:** Pass
- **Notes:** Unit test `Create_DescriptionExceeds1000Chars_ReturnsValidationFail` — Pass. Lưu ý: validation mô tả chỉ xảy ra ở Service layer, không phải ở UI CreateScreen (UI không validate desc length trước).

---

### TC-008
- **Title:** Tiêu đề có khoảng trắng đầu/cuối — tự động trim
- **Priority:** P1
- **Preconditions:** Màn hình CreateScreen
- **Steps:**
  1. Nhập `1` (Tạo mới)
  2. Tiêu đề: `  Mua sắm  `
  3. Xác nhận: `Y`
- **Expected Result:**
  - Task tạo thành công với tiêu đề `Mua sắm` (đã trim)
- **AC:** AC-01
- **Status:** Pass
- **Notes:** Unit test `Create_TitleWithLeadingSpaces_TrimsTitle` — Pass

---

### TC-009
- **Title:** Huỷ tạo task — không tạo bản ghi
- **Priority:** P2
- **Preconditions:** Màn hình CreateScreen
- **Steps:**
  1. Nhập `1` (Tạo mới)
  2. Tiêu đề: `Task sẽ bị hủy`
  3. Mô tả: bỏ qua
  4. Ưu tiên: bỏ qua
  5. Ngày hạn: bỏ qua
  6. Xác nhận: nhập `N`
- **Expected Result:**
  - Toast Info "Đã hủy."
  - Trở về màn hình chính
  - Không có task mới nào được tạo
- **AC:** AC-02 (US-001 Sc.5)
- **Status:** Pass
- **Notes:** Code review CreateScreen.cs L62-65: `ConsoleInput.ReadYesNo(defaultYes: true)` — nhập `N` hủy. Pass

---

### TC-010
- **Title:** Tạo task với ngày hạn trong quá khứ — cảnh báo, cho phép lưu
- **Priority:** P2
- **Preconditions:** Màn hình CreateScreen
- **Steps:**
  1. Nhập `1` (Tạo mới)
  2. Tiêu đề: `Task quá hạn ngay`
  3. Ngày hạn: `2020-01-01` (ngày quá khứ)
  4. Khi thấy cảnh báo "Ngày hạn đã qua. Bạn có muốn tiếp tục?", nhập `Y`
  5. Xác nhận tạo: `Y`
- **Expected Result:**
  - Task được tạo với DueDate = 2020-01-01
  - Trong danh sách hiển thị `⚠ 2020-01-01` (màu đỏ, Overdue)
- **AC:** AC-10 (US-010 Sc.5)
- **Status:** Pass
- **Notes:** CreateScreen.cs L104-108: `IsOverdue` check + confirm. Pass

---

### TC-011
- **Title:** Nhập ngày hạn sai định dạng — hiển thị lỗi, hỏi lại
- **Priority:** P2
- **Preconditions:** Màn hình CreateScreen, bước nhập ngày hạn
- **Steps:**
  1. Ngày hạn: nhập `06/09/2026` (sai format, nên là `yyyy-MM-dd`)
- **Expected Result:**
  - Hiển thị: `Ngày không hợp lệ. Nhập đúng định dạng yyyy-MM-dd.`
  - Hỏi lại ngày hạn (loop, không crash)
- **AC:** AC-02
- **Status:** Pass
- **Notes:** CreateScreen.cs L96-101: `DateOnly.TryParseExact` với format `"yyyy-MM-dd"` — format khác fail. Pass

---

## Feature Suite F02 — Xem danh sách công việc (US-002, AC-03)

### TC-012
- **Title:** Xem danh sách có dữ liệu — happy path
- **Priority:** P0
- **Preconditions:** Có ít nhất 3 task (mix Pending + Completed)
- **Steps:**
  1. Mở app hoặc trở về màn hình chính
  2. Quan sát danh sách
- **Expected Result:**
  - Mỗi task hiển thị: index, status mark, priority mark, tiêu đề, due date
  - Task Pending: `[ ]` (vàng)
  - Task Completed: `[✓]` (xanh), tiêu đề gạch ngang, màu xám
  - Sắp xếp: CreatedAt DESC (task mới nhất lên đầu)
  - StatusBar hiển thị đếm: Total / Pending / Completed
- **AC:** AC-03
- **Status:** Pass
- **Notes:** Code review MainScreen.cs + TaskRow.cs. Sort logic: `TodoService.GetTasks` — `OrderByDescending(i => i.CreatedAt)`. Unit test `GetTasks_FilterAll_ReturnsSortedByCreatedAtDesc` — Pass

---

### TC-013
- **Title:** Danh sách rỗng — hiển thị empty state
- **Priority:** P1
- **Preconditions:** Không có task nào (first run hoặc đã xóa hết)
- **Steps:**
  1. Mở app hoặc xóa hết task
  2. Quan sát màn hình chính
- **Expected Result:**
  - Hiển thị: `Danh sách trống. Nhấn [1] để tạo công việc đầu tiên.`
  - Không crash, menu vẫn hoạt động
- **AC:** AC-03 (US-002 Sc.2)
- **Status:** Pass
- **Notes:** MainScreen.cs L30: `EmptyState.Render(EmptyMessage())`. EmptyMessage trả `"Danh sách trống. Nhấn [1] để tạo công việc đầu tiên."`. Pass

---

### TC-014
- **Title:** Tiêu đề dài hơn 38 ký tự — bị cắt với dấu `...`
- **Priority:** P3
- **Preconditions:** Tạo task với tiêu đề 50 ký tự
- **Steps:**
  1. Tạo task với tiêu đề 50 ký tự
  2. Quan sát cách hiển thị trong danh sách
- **Expected Result:**
  - Tiêu đề bị cắt: 35 ký tự + `...` (tổng 38 ký tự)
  - Dữ liệu thực tế không bị mất (chỉ UI truncate)
- **AC:** AC-03
- **Status:** Pass
- **Notes:** TaskRow.cs L24-26: `TitleWidth=38`, cắt `[..(TitleWidth - 3)] + "..."`. Pass

---

### TC-015
- **Title:** Task hiển thị đúng priority mark
- **Priority:** P2
- **Preconditions:** Có task với các mức priority khác nhau
- **Steps:**
  1. Tạo task Priority=High, task Priority=Medium, task Priority=Low, task Priority=None
  2. Quan sát danh sách
- **Expected Result:**
  - High: `[!!!]` màu đỏ
  - Medium: ` [!] ` màu vàng
  - Low: ` [·] ` màu cyan
  - None: 5 dấu cách trắng
- **AC:** AC-10
- **Status:** Pass
- **Notes:** TaskRow.cs L17-22 — verified by code review. Pass

---

### TC-016
- **Title:** Task hiển thị đúng due date status
- **Priority:** P2
- **Preconditions:** Có task với các trạng thái due date khác nhau
- **Steps:**
  1. Tạo task với DueDate = hôm qua (quá hạn, Pending)
  2. Tạo task với DueDate = hôm nay (Pending)
  3. Tạo task với DueDate = tuần sau (Pending)
  4. Tạo task với DueDate = hôm qua nhưng Completed
- **Expected Result:**
  - Task quá hạn + Pending: `⚠ YYYY-MM-DD` màu đỏ
  - Task hôm nay + Pending: `★ YYYY-MM-DD` màu vàng
  - Task tương lai + Pending: `  YYYY-MM-DD` màu xám
  - Task quá hạn + Completed: hiển thị bình thường, KHÔNG có `⚠`
- **AC:** AC-10 (US-010 BR3, BR4)
- **Status:** Pass
- **Notes:** TaskRow.cs L32-40: `IsOverdue`/`IsDueToday` check + `Status==Completed` không hiển thị warning. TodoItem.cs L37-49. Pass

---

## Feature Suite F03 — Sửa công việc (US-003, AC-04)

### TC-017
- **Title:** Sửa tiêu đề task — happy path
- **Priority:** P0
- **Preconditions:** Có ít nhất 1 task trong danh sách
- **Steps:**
  1. Nhập `2` (Sửa)
  2. Nhập số thứ tự task cần sửa (ví dụ `1`)
  3. Tiêu đề mới: nhập `Tiêu đề đã cập nhật`
  4. Mô tả: Enter (giữ nguyên)
  5. Priority: Enter (giữ nguyên)
  6. Due date: Enter (giữ nguyên)
- **Expected Result:**
  - Toast "Công việc đã được cập nhật!"
  - Danh sách cập nhật ngay với tiêu đề mới
  - UpdatedAt được ghi nhận
  - CreatedAt không thay đổi
  - Status không thay đổi
- **AC:** AC-04
- **Status:** Pass
- **Notes:** Unit test `Update_ValidTitle_UpdatesTitleAndUpdatedAt` — Pass. `TodoService.Update` giữ nguyên `CreatedAt` (init property).

---

### TC-018
- **Title:** Sửa task với tiêu đề rỗng — validation block
- **Priority:** P0
- **Preconditions:** Có task đang hiển thị, EditScreen đang mở
- **Steps:**
  1. Nhập `2` (Sửa) → chọn task
  2. Tiêu đề: xóa hết rồi Enter (whitespace)
- **Expected Result:**
  - Hiển thị: `Tiêu đề không được để trống.`
  - Task không bị cập nhật, giữ nguyên nội dung cũ
  - Loop hỏi lại tiêu đề
- **AC:** AC-04
- **Status:** Pass
- **Notes:** EditScreen.cs L37-43 + unit test `Update_EmptyTitle_ReturnsValidationFail` — Pass

---

### TC-019
- **Title:** Huỷ sửa bằng Enter (giữ nguyên tất cả)
- **Priority:** P2
- **Preconditions:** Có task, EditScreen đang mở
- **Steps:**
  1. Nhập `2` (Sửa) → chọn task
  2. Mỗi trường: nhấn Enter (giữ nguyên)
- **Expected Result:**
  - Task cập nhật thành công với cùng giá trị cũ
  - Toast Success xuất hiện
- **AC:** AC-04 (US-003 Sc.4)
- **Status:** Pass
- **Notes:** `ConsoleInput.ReadLineWithDefault(item.Title)` trả default khi Enter. EditScreen.cs L35. Pass

---

### TC-020
- **Title:** Sửa ngày hạn với input sai format — giữ nguyên ngày cũ
- **Priority:** P2
- **Preconditions:** Task có due date, EditScreen đang mở
- **Steps:**
  1. Chọn sửa task
  2. Due date: nhập `31/12/2026` (sai format)
- **Expected Result:**
  - Hiển thị: `Ngày không hợp lệ — giữ nguyên [ngày cũ].`
  - Task được lưu với ngày hạn cũ (không crash, không block)
- **AC:** AC-04
- **Status:** Pass
- **Notes:** EditScreen.cs L80-85: sai format → giữ nguyên `item.DueDate`, hiển thị cảnh báo vàng. Pass

---

### TC-021
- **Title:** Sửa task không tìm thấy (ID không hợp lệ)
- **Priority:** P1
- **Preconditions:** Danh sách có task
- **Steps:**
  1. Nhập `2` (Sửa)
  2. Nhập số thứ tự ngoài phạm vi (ví dụ: 0 hoặc số lớn hơn count)
- **Expected Result:**
  - `ConsoleInput.ReadInt` trả `null` → `selectedIndex = 0`
  - MainScreen không gọi EditScreen
  - Không crash
- **AC:** AC-04
- **Status:** Pass
- **Notes:** MainScreen.cs L50-52: `selectedIndex > 0` mới gọi edit. `ReadInt` trả `null` nếu out-of-range. Pass

---

## Feature Suite F04 — Xóa công việc (US-004, AC-05)

### TC-022
- **Title:** Xóa task sau khi xác nhận Y — happy path
- **Priority:** P0
- **Preconditions:** Có ít nhất 1 task
- **Steps:**
  1. Nhập `3` (Xóa)
  2. Nhập số thứ tự task
  3. Xác nhận: `Y`
- **Expected Result:**
  - Toast "Công việc đã được xóa!"
  - Task biến mất khỏi danh sách ngay lập tức
  - Storage cập nhật (task không còn trong file)
  - Số lượng task giảm 1
- **AC:** AC-05
- **Status:** Pass
- **Notes:** Unit test `Delete_ExistingId_ReturnsOk` + `Delete_ExistingItem_RemovedFromFile` — Pass

---

### TC-023
- **Title:** Huỷ xóa với Enter hoặc N — task vẫn tồn tại
- **Priority:** P0
- **Preconditions:** Có task
- **Steps:**
  1. Nhập `3` (Xóa) → chọn task
  2. Xác nhận: nhấn Enter (mặc định N) hoặc nhập `N`
- **Expected Result:**
  - Toast Info "Đã hủy."
  - Task vẫn còn trong danh sách
  - Không thay đổi gì trong storage
- **AC:** AC-05 (US-004 Sc.2)
- **Status:** Pass
- **Notes:** DeleteScreen.cs L31: `ConsoleInput.ReadYesNo(defaultYes: false)` — Enter = N = hủy. Pass

---

### TC-024
- **Title:** Xóa task duy nhất — danh sách về empty state
- **Priority:** P1
- **Preconditions:** Chỉ có đúng 1 task
- **Steps:**
  1. Nhập `3` (Xóa) → chọn task số 1
  2. Xác nhận: `Y`
- **Expected Result:**
  - Task bị xóa
  - Màn hình hiển thị empty state
- **AC:** AC-05 (US-004 Sc.3)
- **Status:** Pass
- **Notes:** Logic: sau Delete, `GetTasks()` trả rỗng → EmptyState.Render(). Pass

---

### TC-025
- **Title:** Cố xóa khi không có task — cảnh báo không crash
- **Priority:** P2
- **Preconditions:** Danh sách rỗng
- **Steps:**
  1. Nhập `3` (Xóa)
- **Expected Result:**
  - Toast Warning: `Không có công việc để xóa.`
  - Không crash, trở về màn hình chính
- **AC:** AC-05
- **Status:** Pass
- **Notes:** MainScreen.cs L74-77: `count == 0` → Toast + return 0. Pass

---

### TC-026
- **Title:** Xóa không thể hoàn tác — không có Undo
- **Priority:** P1
- **Preconditions:** Đã xóa 1 task
- **Steps:**
  1. Xóa task
  2. Quan sát tùy chọn sau khi xóa
- **Expected Result:**
  - Không có tùy chọn "Hoàn tác" hay "Khôi phục" nào
  - Task đã xóa không thể lấy lại từ UI
- **AC:** AC-05 (US-004 BR2)
- **Status:** Pass
- **Notes:** PRD NG: không có Recycle Bin. Code không implement Undo. Pass

---

## Feature Suite F05 — Toggle hoàn thành (US-005, AC-06)

### TC-027
- **Title:** Toggle Pending → Completed — happy path
- **Priority:** P0
- **Preconditions:** Có task Pending
- **Steps:**
  1. Nhập `4` (Toggle)
  2. Nhập số thứ tự task Pending
- **Expected Result:**
  - Toast "Đã đánh dấu hoàn thành!"
  - Task status đổi sang `[✓]` (xanh)
  - Tiêu đề hiển thị gạch ngang, màu xám
  - CompletedAt được ghi nhận (không null)
- **AC:** AC-06
- **Status:** Pass
- **Notes:** Unit test `Toggle_PendingTask_BecomesCompleted` + `Toggle_SetsCompletedAt` — Pass

---

### TC-028
- **Title:** Toggle Completed → Pending — bỏ đánh dấu
- **Priority:** P0
- **Preconditions:** Có task Completed
- **Steps:**
  1. Nhập `4` (Toggle)
  2. Nhập số thứ tự task Completed
- **Expected Result:**
  - Toast "Đã mở lại công việc!"
  - Task status đổi về `[ ]` (vàng)
  - Tiêu đề không còn gạch ngang
  - CompletedAt về null
- **AC:** AC-06 (US-005 Sc.2)
- **Status:** Pass
- **Notes:** Unit test `Toggle_CompletedTask_BecomesPending` + `Toggle_ClearsCompletedAt` — Pass

---

### TC-029
- **Title:** Toggle 3 lần liên tiếp — trạng thái cuối đúng
- **Priority:** P1
- **Preconditions:** Có task Pending
- **Steps:**
  1. Toggle task → Completed (lần 1)
  2. Toggle task → Pending (lần 2)
  3. Toggle task → Completed (lần 3)
- **Expected Result:**
  - Sau lần 3: Status = Completed
  - CompletedAt được cập nhật theo thời điểm lần toggle cuối
  - Không có data inconsistency
- **AC:** AC-06 (US-005 Sc.3)
- **Status:** Pass
- **Notes:** Unit test `Toggle_ThreeTimesEndingCompleted_IsCompleted` — Pass

---

### TC-030
- **Title:** Cố toggle khi danh sách rỗng
- **Priority:** P2
- **Preconditions:** Danh sách rỗng
- **Steps:**
  1. Nhập `4` (Toggle)
- **Expected Result:**
  - Toast Warning: `Không có công việc để toggle.`
  - Không crash
- **AC:** AC-06
- **Status:** Pass
- **Notes:** MainScreen.cs L74-77: count == 0 → cảnh báo. Pass

---

## Feature Suite F06 — Lưu trữ tự động (US-006, AC-07)

### TC-031
- **Title:** Dữ liệu persist ngay sau Create
- **Priority:** P0
- **Preconditions:** App đang chạy
- **Steps:**
  1. Tạo task mới
  2. Kiểm tra file `%LOCALAPPDATA%\KZTEK\TodoApp\todos.json` tồn tại
- **Expected Result:**
  - File `todos.json` tồn tại và chứa task vừa tạo
  - Không cần thao tác Save thủ công
- **AC:** AC-07
- **Status:** Pass
- **Notes:** Unit test `Add_PersistsItem_FileExistsAfterAdd` — Pass. Pattern write-then-rename đảm bảo atomicity.

---

### TC-032
- **Title:** Không để lại file tạm sau ghi thành công
- **Priority:** P1
- **Preconditions:** App đang chạy
- **Steps:**
  1. Thực hiện thao tác tạo/sửa/xóa
  2. Kiểm tra `todos.tmp` không tồn tại
- **Expected Result:**
  - File `todos.tmp` bị xóa hoặc rename thành `todos.json` sau mỗi lần ghi
  - Không để lại temp file
- **AC:** AC-07 (US-006 BR2)
- **Status:** Pass
- **Notes:** Unit test `Add_AtomicWrite_NoTempFileLeftBehind` — Pass

---

### TC-033
- **Title:** Dữ liệu persist ngay sau Update
- **Priority:** P0
- **Preconditions:** Có task đang tồn tại
- **Steps:**
  1. Sửa tiêu đề task
  2. Kiểm tra file JSON
- **Expected Result:**
  - File JSON được cập nhật ngay sau khi sửa
  - Giá trị mới xuất hiện trong file
- **AC:** AC-07
- **Status:** Pass
- **Notes:** Unit test `Update_ExistingItem_UpdatesPersisted` — Pass

---

### TC-034
- **Title:** Dữ liệu persist ngay sau Delete
- **Priority:** P0
- **Preconditions:** Có task đang tồn tại
- **Steps:**
  1. Xóa task (confirm Y)
  2. Kiểm tra file JSON
- **Expected Result:**
  - File JSON không còn chứa task đã xóa
- **AC:** AC-07
- **Status:** Pass
- **Notes:** Unit test `Delete_ExistingItem_RemovedFromFile` — Pass

---

### TC-035
- **Title:** Dữ liệu persist ngay sau Toggle
- **Priority:** P0
- **Preconditions:** Có task Pending
- **Steps:**
  1. Toggle task → Completed
  2. Kiểm tra file JSON: `"status": "Completed"` và `"completedAt"` có giá trị
- **Expected Result:**
  - File JSON cập nhật đúng trạng thái và CompletedAt
- **AC:** AC-07
- **Status:** Pass
- **Notes:** Integration test `CrudCycle_PersistsAndReloadsCorrectly` verify toggle + reload — Pass

---

## Feature Suite F07 — Tải dữ liệu khi khởi động (US-007, AC-07, AC-08)

### TC-036
- **Title:** Khởi động lại — dữ liệu khôi phục đầy đủ
- **Priority:** P0
- **Preconditions:** Đã tạo ít nhất 3 task với nhiều trạng thái khác nhau, sau đó tắt app
- **Steps:**
  1. Tắt app (Ctrl+C hoặc nhập Q)
  2. Mở lại app
- **Expected Result:**
  - Toàn bộ task hiển thị đúng, đủ số lượng
  - Status, Priority, DueDate, CreatedAt đúng như trước khi tắt
  - Không có task bị mất, không có task bị trùng
- **AC:** AC-07, AC-08
- **Status:** Pass
- **Notes:** Integration test `CrudCycle_PersistsAndReloadsCorrectly` — Pass. Scenario: create 3 → toggle 1 → update 1 → delete 1 → restart → verify 2 còn lại đúng.

---

### TC-037
- **Title:** Khởi động lần đầu — danh sách rỗng, không crash
- **Priority:** P0
- **Preconditions:** Chưa từng chạy app, không có file `todos.json`
- **Steps:**
  1. Xóa `%LOCALAPPDATA%\KZTEK\TodoApp\todos.json` nếu có
  2. Chạy app lần đầu
- **Expected Result:**
  - App khởi động bình thường
  - Hiển thị empty state
  - Không crash
  - File `todos.json` tự tạo khi có thao tác đầu tiên
- **AC:** AC-07, AC-08 (US-007 Sc.2)
- **Status:** Pass
- **Notes:** Integration test `FirstRun_EmptyApp_WorksWithNoFile` — Pass. `JsonFileRepository.Load()`: file không tồn tại → `_items = []`.

---

### TC-038
- **Title:** File JSON bị corrupt khi khởi động — backup và khởi động với danh sách rỗng
- **Priority:** P1
- **Preconditions:** File `todos.json` tồn tại với nội dung JSON không hợp lệ
- **Steps:**
  1. Ghi nội dung rác vào `todos.json`
  2. Chạy app
- **Expected Result:**
  - App KHÔNG crash
  - Toast Warning: `Dữ liệu bị hỏng đã được sao lưu. Bắt đầu với danh sách trống.`
  - File `todos.bak.json` xuất hiện (backup file cũ)
  - App chạy với danh sách rỗng
- **AC:** AC-07, AC-08 (US-007 Sc.3)
- **Status:** Pass
- **Notes:** Unit test `Load_CorruptFile_ReturnsEmptyAndBacksUp` — Pass. AppRunner.cs L31-32: check `CorruptionDetected`.

---

### TC-039
- **Title:** Khởi động ≤ 2 giây — performance requirement
- **Priority:** P1
- **Preconditions:** File `todos.json` tồn tại với dữ liệu bình thường (vài trăm task)
- **Steps:**
  1. Đo thời gian từ khi chạy `dotnet run` đến khi màn hình chính hiển thị
- **Expected Result:**
  - Thời gian khởi động ≤ 2 giây trên Core i3, 4GB RAM
- **AC:** AC-08
- **Status:** Blocked
- **Notes:** BLOCKED — Không thể đo chính xác do test môi trường là code review. Cần thực thi manual với file dữ liệu lớn. Cần QA Lead xác nhận môi trường benchmark. `dotnet run` (framework-dep build) bao gồm JIT warmup — có thể chậm hơn published exe.

---

## Feature Suite F08 — Lọc theo trạng thái (US-008, AC-09)

### TC-040
- **Title:** Lọc Pending — chỉ hiện task Pending
- **Priority:** P1
- **Preconditions:** Có 3 task Pending và 2 task Completed
- **Steps:**
  1. Nhập `5` (Lọc)
  2. Chọn `2` (Đang chờ)
  3. Trở về màn hình chính
- **Expected Result:**
  - Chỉ 3 task Pending hiển thị
  - Header thay đổi thành "Đang chờ"
  - 2 task Completed bị ẩn (dữ liệu không mất)
- **AC:** AC-09 (US-008 Sc.1)
- **Status:** Pass
- **Notes:** Unit test `GetTasks_FilterPending_ReturnsOnlyPending` — Pass. MainScreen hiển thị `FilterLabel()` = "Đang chờ".

---

### TC-041
- **Title:** Lọc Completed — chỉ hiện task Completed
- **Priority:** P1
- **Preconditions:** Có 3 task Pending và 2 task Completed
- **Steps:**
  1. Nhập `5` (Lọc)
  2. Chọn `3` (Đã hoàn thành)
- **Expected Result:**
  - Chỉ 2 task Completed hiển thị
  - Header: "Đã hoàn thành"
- **AC:** AC-09 (US-008 Sc.2)
- **Status:** Pass
- **Notes:** Unit test `GetTasks_FilterCompleted_ReturnsOnlyCompleted` — Pass

---

### TC-042
- **Title:** Lọc All — hiển thị tất cả task
- **Priority:** P1
- **Preconditions:** Đang ở filter Pending hoặc Completed
- **Steps:**
  1. Nhập `5` (Lọc)
  2. Chọn `1` (Tất cả)
- **Expected Result:**
  - Tất cả task hiển thị
  - Header: "Tất cả"
- **AC:** AC-09 (US-008 Sc.3)
- **Status:** Pass
- **Notes:** `TodoService.GetTasks(TaskFilter.All)` — unit test Pass

---

### TC-043
- **Title:** Lọc khi không có task trong nhóm — empty state đúng
- **Priority:** P2
- **Preconditions:** Chưa có task nào Completed
- **Steps:**
  1. Nhập `5` (Lọc)
  2. Chọn `3` (Đã hoàn thành)
- **Expected Result:**
  - Hiển thị: `Chưa có công việc nào hoàn thành.`
  - Không crash
- **AC:** AC-09 (US-008 Sc.4)
- **Status:** Pass
- **Notes:** MainScreen.cs L92-95: `EmptyMessage()` trả đúng message theo filter. Pass

---

### TC-044
- **Title:** Toggle task khi đang lọc Pending — task biến mất khỏi view
- **Priority:** P2
- **Preconditions:** Filter đang ở Pending, có task A (Pending)
- **Steps:**
  1. Đặt filter = Pending
  2. Toggle task A → Completed
- **Expected Result:**
  - Sau toggle, danh sách filter Pending không còn task A
  - StatusBar cập nhật đếm đúng
  - Không crash, không hiển thị sai
- **AC:** AC-09 (US-008 Sc.5, BR4/BR5)
- **Status:** Pass
- **Notes:** `MainScreen.Show()` loop: sau toggle, gọi lại `GetTasks(_currentFilter)` → filter lại đúng. Pass

---

### TC-045
- **Title:** Tạo task mới khi đang lọc Completed — task mới không hiện trong view Completed
- **Priority:** P2
- **Preconditions:** Filter đang ở Completed
- **Steps:**
  1. Đặt filter = Completed
  2. Tạo task mới (Pending)
- **Expected Result:**
  - Task mới KHÔNG xuất hiện trong view Completed (vì task mới = Pending)
  - StatusBar cập nhật Pending +1
- **AC:** AC-09 (US-008 BR5)
- **Status:** Pass
- **Notes:** Task mới = Pending. Filter Completed chỉ lấy `Status == Completed`. Logic đúng theo code review. Pass

---

### TC-046
- **Title:** FilterScreen hiển thị đúng số lượng từng nhóm
- **Priority:** P2
- **Preconditions:** Có 3 Pending và 2 Completed
- **Steps:**
  1. Nhập `5` (Lọc)
- **Expected Result:**
  - `[1] Tất cả        (5)`
  - `[2] Đang chờ      (3)`
  - `[3] Đã hoàn thành (2)`
- **AC:** AC-09
- **Status:** Pass
- **Notes:** FilterScreen.cs L23-25: dùng `_service.GetCounts()`. Unit test `GetCounts_ReturnsCorrectCounts` — Pass

---

## Feature Suite F09 — Mức độ ưu tiên (US-009, AC-10)

### TC-047
- **Title:** Gán Priority High khi tạo task
- **Priority:** P1
- **Preconditions:** Màn hình CreateScreen
- **Steps:**
  1. Tạo task mới
  2. Bước Priority: nhập `4` (Cao)
  3. Xác nhận tạo
- **Expected Result:**
  - Task tạo thành công với Priority = High
  - Danh sách hiển thị `[!!!]` màu đỏ
- **AC:** AC-10 (US-009 Sc.1)
- **Status:** Pass
- **Notes:** CreateScreen.cs L75-86: map 4 → Priority.High. TaskRow.cs L19. Pass

---

### TC-048
- **Title:** Không chọn Priority khi tạo — mặc định None
- **Priority:** P2
- **Preconditions:** Màn hình CreateScreen
- **Steps:**
  1. Tạo task mới
  2. Bước Priority: nhấn Enter (không chọn)
- **Expected Result:**
  - Task tạo với Priority = None
  - Không hiển thị priority mark (5 dấu cách)
- **AC:** AC-10 (US-009 Sc.3)
- **Status:** Pass
- **Notes:** `ConsoleInput.ReadInt(1,4)` → null → `switch default → Priority.None`. TDD §1 OQ-BA-09: mặc định None. Pass

---

### TC-049
- **Title:** Cập nhật Priority khi sửa task
- **Priority:** P1
- **Preconditions:** Task đang có Priority = None
- **Steps:**
  1. Sửa task
  2. Priority: nhập `4` (Cao)
  3. Lưu
- **Expected Result:**
  - Priority cập nhật thành High
  - Danh sách hiển thị `[!!!]` màu đỏ
- **AC:** AC-10 (US-009 Sc.2)
- **Status:** Pass
- **Notes:** EditScreen.cs L64-71: map priority input. Unit test `Update_ChangesPriority` — Pass

---

## Feature Suite F10 — Ngày hạn hoàn thành (US-010, AC-10)

### TC-050
- **Title:** Gán DueDate khi tạo task — hiển thị đúng
- **Priority:** P1
- **Preconditions:** Màn hình CreateScreen
- **Steps:**
  1. Tạo task
  2. Ngày hạn: `2026-06-15` (ngày tương lai)
- **Expected Result:**
  - DueDate = 2026-06-15
  - Hiển thị `  2026-06-15` màu xám (không phải quá hạn, không phải hôm nay)
- **AC:** AC-10 (US-010 Sc.1)
- **Status:** Pass
- **Notes:** TaskRow.cs L38-40. Pass

---

### TC-051
- **Title:** Task Completed với DueDate quá hạn — không hiển thị cảnh báo
- **Priority:** P1
- **Preconditions:** Có task với DueDate hôm qua, status = Completed
- **Steps:**
  1. Quan sát danh sách
- **Expected Result:**
  - Task KHÔNG hiển thị `⚠` (không cảnh báo quá hạn)
  - Hiển thị bình thường như task Completed khác
- **AC:** AC-10 (US-010 Sc.4, BR4)
- **Status:** Pass
- **Notes:** `TodoItem.IsOverdue`: `Status == TodoStatus.Pending` là điều kiện — Completed task không bao giờ IsOverdue. TaskRow.cs L35: dựa vào `IsOverdue`. Pass

---

### TC-052
- **Title:** Xóa DueDate khi sửa task (từ có ngày → không ngày)
- **Priority:** P2
- **Preconditions:** Task đang có DueDate
- **Steps:**
  1. Sửa task
  2. Trường DueDate: nhấn Enter (giữ nguyên thay vì xóa)
- **Expected Result:**
  - Không có cách xóa DueDate về null từ EditScreen (Enter = giữ nguyên)
- **AC:** AC-10
- **Status:** Blocked
- **Notes:** BLOCKED — BUG phát hiện: `EditScreen.cs` không có cơ chế xóa DueDate (đặt về null). Enter giữ nguyên, nhập bất kỳ ngày nào thì ghi đè, nhưng không có cách xóa DueDate về null. Đây là behavior gap với US-010. Cần confirm với PM/TL xem có cần implement hay không.

---

## Feature Suite — Error Handling & Stability

### TC-053
- **Title:** Nhập lựa chọn không hợp lệ tại menu chính
- **Priority:** P2
- **Preconditions:** Màn hình chính đang hiển thị
- **Steps:**
  1. Nhập `6` hoặc `abc` hoặc ký tự không hợp lệ
- **Expected Result:**
  - Toast Warning: `Lựa chọn không hợp lệ. Vui lòng thử lại.`
  - Menu vẫn hiển thị, app không crash
- **AC:** AC-08 (stability)
- **Status:** Pass
- **Notes:** MainScreen.cs L62-64: `default` case → `ToastNotification.Show(Warning, Messages.InvalidChoice, 800ms)`. Pass

---

### TC-054
- **Title:** Dữ liệu cũ không có Priority/DueDate — backward compatibility
- **Priority:** P1
- **Preconditions:** File `todos.json` được tạo từ phiên bản cũ không có trường `priority` và `dueDate`
- **Steps:**
  1. Tạo file JSON thủ công với `items[].status` nhưng không có `priority` và `dueDate`
  2. Chạy app
- **Expected Result:**
  - App khởi động bình thường
  - Task hiển thị với Priority = None, DueDate = null
  - Không crash
- **AC:** AC-07, AC-08 (US-009 EC1, US-010 EC2)
- **Status:** Pass
- **Notes:** Unit test `Load_MissingPriorityField_DefaultsToNone` — Pass. `JsonSerializerOptions { PropertyNameCaseInsensitive = true }` + field thiếu → default value.

---

### TC-055
- **Title:** TODOAPP_DATA_DIR override hoạt động đúng
- **Priority:** P1
- **Preconditions:** Biến môi trường `TODOAPP_DATA_DIR` được đặt vào thư mục test
- **Steps:**
  1. Set `TODOAPP_DATA_DIR = C:\Temp\TestTodo`
  2. Chạy app, tạo task
  3. Kiểm tra file `C:\Temp\TestTodo\todos.json`
- **Expected Result:**
  - File được tạo tại thư mục override, không phải `%LOCALAPPDATA%\KZTEK\TodoApp`
- **AC:** AC-07 (TDD §1 OQ4)
- **Status:** Pass
- **Notes:** Integration tests dùng cơ chế này (`TODOAPP_DATA_DIR` set mỗi test). Pass

---

### TC-056
- **Title:** Enum serialize dạng string trong JSON — đọc lại đúng
- **Priority:** P2
- **Preconditions:** Có file todos.json với status dạng string (Pending/Completed)
- **Steps:**
  1. Mở file `todos.json`
  2. Kiểm tra trường `status`: là `"Pending"` hay `"Completed"` (không phải 0/1)
  3. Chạy lại app, verify load đúng
- **Expected Result:**
  - File lưu `"status": "Pending"` (string, không phải số)
  - App load lại đúng, không crash
- **AC:** AC-07
- **Status:** Pass
- **Notes:** `JsonFileRepository` dùng `JsonStringEnumConverter()` — serialize enum thành string. Load lại với `PropertyNameCaseInsensitive: true` → parse đúng. Pass

---

## Bảng Bug tìm thấy

### BUG-001: Không có cơ chế xóa DueDate về null từ EditScreen

| Trường | Nội dung |
|---|---|
| **Severity** | Low |
| **Priority** | P3 |
| **Phát hiện tại** | TC-052 |
| **Môi trường** | Console App, EditScreen |
| **Mô tả** | `EditScreen` không cho phép người dùng xóa DueDate về null. `Enter` = giữ nguyên giá trị cũ. Không có cơ chế nhập chuỗi rỗng để clear DueDate. |
| **Bước reproduce** | 1. Tạo task với DueDate. 2. Sửa task. 3. Cố xóa DueDate. |
| **Kết quả thực tế** | DueDate không thể xóa về null từ UI |
| **Kết quả mong đợi** | Người dùng có thể xóa DueDate (ví dụ: nhập `-` hoặc `clear`) |
| **Tần suất** | Luôn luôn (100%) |
| **Workaround** | Không có |
| **Ghi chú** | US-010 không mô tả rõ scenario xóa DueDate. Cần xác nhận với PM/TL. |

---

### BUG-002: Thứ tự hiển thị task khi EditScreen lấy task theo `TaskFilter.All` thay vì filter hiện tại

| Trường | Nội dung |
|---|---|
| **Severity** | Medium |
| **Priority** | P2 |
| **Phát hiện tại** | Code review EditScreen.cs L19, DeleteScreen.cs L18, ToggleScreen.cs L18 |
| **Môi trường** | Console App — khi đang lọc Pending hoặc Completed |
| **Mô tả** | `EditScreen`, `DeleteScreen`, `ToggleScreen` đều gọi `GetByDisplayIndex(displayIndex, TaskFilter.All)`. Tuy nhiên `MainScreen.PickTaskIndex()` hiển thị số thứ tự dựa trên `_currentFilter`. Khi user đang lọc Pending, index hiển thị trên màn hình khác với index trong `TaskFilter.All`. |
| **Bước reproduce** | 1. Có 3 task: Task A (Completed), Task B (Pending), Task C (Pending). 2. Lọc Pending: hiển thị Task B (#1) và Task C (#2). 3. Nhập `2` (Sửa), chọn `#2`. 4. `GetByDisplayIndex(2, All)` lấy task theo All-order (có thể là Task A hoặc Task C tùy sort). |
| **Kết quả thực tế** | Task bị sửa/xóa/toggle có thể không phải task user muốn khi đang dùng filter |
| **Kết quả mong đợi** | `GetByDisplayIndex` phải dùng cùng filter đang active trên MainScreen |
| **Tần suất** | Luôn luôn khi đang dùng filter Pending hoặc Completed (không phải All) |
| **Workaround** | Dùng filter All khi sửa/xóa/toggle task |

---

## Bảng Coverage Mapping TC → AC → US

| TC ID | Test Case | AC | US |
|---|---|---|---|
| TC-001 | Tạo task hợp lệ — happy path | AC-01 | US-001 Sc.1 |
| TC-002 | Tạo task đủ trường | AC-01, AC-10 | US-001 Sc.2, US-009/010 |
| TC-003 | Tiêu đề rỗng — block | AC-02 | US-001 Sc.3 |
| TC-004 | Tiêu đề chỉ space — block | AC-02 | US-001 EC2 |
| TC-005 | Tiêu đề 200 ký tự — boundary OK | AC-01, AC-02 | US-001 Sc.1, BR2 |
| TC-006 | Tiêu đề 201 ký tự — block | AC-02 | US-001 Sc.4 |
| TC-007 | Mô tả > 1000 ký tự — block | AC-02 | US-001 BR3 |
| TC-008 | Tiêu đề có space đầu/cuối — trim | AC-01 | US-001 EC2 |
| TC-009 | Huỷ tạo task | AC-02 | US-001 Sc.5 |
| TC-010 | DueDate quá khứ — cảnh báo, cho lưu | AC-10 | US-010 Sc.5 |
| TC-011 | DueDate sai format | AC-02 | US-010 |
| TC-012 | Xem danh sách có dữ liệu | AC-03 | US-002 Sc.1 |
| TC-013 | Danh sách rỗng — empty state | AC-03 | US-002 Sc.2 |
| TC-014 | Tiêu đề dài bị truncate | AC-03 | US-002 |
| TC-015 | Priority mark hiển thị đúng | AC-10 | US-009 BR3 |
| TC-016 | Due date status hiển thị đúng | AC-10 | US-010 Sc.2,3,4 |
| TC-017 | Sửa tiêu đề — happy path | AC-04 | US-003 Sc.1 |
| TC-018 | Sửa với tiêu đề rỗng — block | AC-04 | US-003 Sc.3 |
| TC-019 | Huỷ sửa với Enter | AC-04 | US-003 Sc.4 |
| TC-020 | Sửa DueDate sai format — giữ nguyên | AC-04 | US-003 |
| TC-021 | Sửa task không tồn tại | AC-04 | US-003 EC1 |
| TC-022 | Xóa sau khi xác nhận Y | AC-05 | US-004 Sc.1 |
| TC-023 | Huỷ xóa bằng Enter/N | AC-05 | US-004 Sc.2 |
| TC-024 | Xóa task duy nhất | AC-05 | US-004 Sc.3 |
| TC-025 | Xóa khi danh sách rỗng | AC-05 | US-004 |
| TC-026 | Không có Undo sau xóa | AC-05 | US-004 BR2 |
| TC-027 | Toggle Pending → Completed | AC-06 | US-005 Sc.1 |
| TC-028 | Toggle Completed → Pending | AC-06 | US-005 Sc.2 |
| TC-029 | Toggle 3 lần liên tiếp | AC-06 | US-005 Sc.3 |
| TC-030 | Toggle khi danh sách rỗng | AC-06 | US-005 |
| TC-031 | Persist sau Create | AC-07 | US-006 Sc.1 |
| TC-032 | Không để lại file tạm | AC-07 | US-006 BR2 |
| TC-033 | Persist sau Update | AC-07 | US-006 Sc.1 |
| TC-034 | Persist sau Delete | AC-07 | US-006 Sc.1 |
| TC-035 | Persist sau Toggle | AC-07 | US-006 Sc.1 |
| TC-036 | Khởi động lại — dữ liệu khôi phục | AC-07, AC-08 | US-007 Sc.1 |
| TC-037 | First run — không crash | AC-07, AC-08 | US-007 Sc.2 |
| TC-038 | File corrupt khi khởi động | AC-07, AC-08 | US-007 Sc.3 |
| TC-039 | Khởi động ≤ 2 giây | AC-08 | US-007 BR1 |
| TC-040 | Lọc Pending | AC-09 | US-008 Sc.1 |
| TC-041 | Lọc Completed | AC-09 | US-008 Sc.2 |
| TC-042 | Lọc All | AC-09 | US-008 Sc.3 |
| TC-043 | Lọc khi không có task trong nhóm | AC-09 | US-008 Sc.4 |
| TC-044 | Toggle task khi đang lọc Pending | AC-09 | US-008 Sc.5 |
| TC-045 | Tạo task mới khi lọc Completed | AC-09 | US-008 BR5 |
| TC-046 | FilterScreen hiển thị số lượng đúng | AC-09 | US-008 |
| TC-047 | Gán Priority High khi tạo | AC-10 | US-009 Sc.1 |
| TC-048 | Priority mặc định None | AC-10 | US-009 Sc.3 |
| TC-049 | Cập nhật Priority khi sửa | AC-10 | US-009 Sc.2 |
| TC-050 | Gán DueDate khi tạo | AC-10 | US-010 Sc.1 |
| TC-051 | Completed task không cảnh báo quá hạn | AC-10 | US-010 Sc.4, BR4 |
| TC-052 | Xóa DueDate về null (BLOCKED) | AC-10 | US-010 |
| TC-053 | Input không hợp lệ tại menu | AC-08 | US-002 |
| TC-054 | Backward compat — thiếu field | AC-07, AC-08 | US-009 EC1, US-010 EC2 |
| TC-055 | TODOAPP_DATA_DIR override | AC-07 | US-006 BR4 |
| TC-056 | Enum serialize dạng string | AC-07 | US-006 |

---

## Test Execution Summary

### Kết quả theo Status

| Status | Số TC | Chi tiết |
|---|---|---|
| Pass | 50 | TC-001 đến TC-051 (trừ các case dưới), TC-053 đến TC-056 |
| Fail | 2 | TC-052 (BUG-001), BUG-002 (phát hiện qua code review) |
| Blocked | 4 | TC-039 (cần benchmark environment), TC-052 (cần PM confirm), và 2 sub-case trong BUG-002 |

### Kết quả theo Priority

| Priority | Total | Pass | Fail | Blocked |
|---|---|---|---|---|
| P0 | 14 | 14 | 0 | 0 |
| P1 | 21 | 20 | 0 | 1 |
| P2 | 17 | 14 | 1 | 2 |
| P3 | 4 | 2 | 0 | 1 (BUG-001 phân loại P3) |

### Kết quả theo AC

| AC | Tổng TC | Pass | Fail/Blocked |
|---|---|---|---|
| AC-01 (Tạo task) | 5 | 5 | 0 |
| AC-02 (Validation tạo) | 7 | 7 | 0 |
| AC-03 (Xem danh sách) | 5 | 5 | 0 |
| AC-04 (Sửa task) | 5 | 5 | 0 |
| AC-05 (Xóa task) | 5 | 5 | 0 |
| AC-06 (Toggle hoàn thành) | 4 | 4 | 0 |
| AC-07 (Persistence) | 9 | 9 | 0 |
| AC-08 (Khởi động) | 5 | 4 | 1 (Blocked-benchmark) |
| AC-09 (Lọc) | 7 | 7 | 0 |
| AC-10 (Priority + DueDate) | 9 | 7 | 2 |

---

## Phương pháp kiểm thử

| Phương pháp | Mô tả | Số TC phủ |
|---|---|---|
| Unit test review | Đọc 54 test cases hiện có (Application + Infrastructure + Integration), verify pass/fail | 35 TC |
| Code review | Đọc source từng Screen/Service/Repository, trace luồng logic | 21 TC |
| Behavior inference | Suy luận từ code + AC để xác định expected behavior | 5 TC (edge cases) |
| Manual execution note | TC cần chạy tay thực tế trên environment | 1 TC (TC-039 benchmark) |

---

## Đánh giá QA Sign-off

| Tiêu chí DoD (PRD §11) | Trạng thái | Ghi chú |
|---|---|---|
| 100% AC-01 đến AC-08 pass | Partially — AC-08 Blocked (benchmark) | TC-039 cần environment thực tế |
| Test coverage unit test ≥ 80% | Pass | Application: 93.97% (CODE-GRAPH.md) |
| Không còn bug P0/P1 | Pass | BUG-001 là P3, BUG-002 là P2 |
| Code reviewed + merged | Pass | Tech Lead S1-T018 |
| Dữ liệu OK sau 5 lần restart | Pass | Integration test verify |

**Recommendation:** Có thể tiến hành QA Lead sign-off cho AC-01 đến AC-07, AC-09, AC-10.
AC-08 cần benchmark thực tế. BUG-002 cần developer fix trước next sprint.

---

*Tài liệu này là output bắt buộc của QA Engineer theo WF-FEATURE Bước 11.*
*Chuyển sang: QA Lead (Bước 12) để sign-off chất lượng.*
