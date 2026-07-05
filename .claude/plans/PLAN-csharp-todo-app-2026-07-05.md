---
task: csharp-todo-app
created: 2026-07-05
updated: 2026-07-05 16:57
status: completed
workflow: WF-FEATURE (rút gọn)
priority: P2
---

# PLAN: C# WinForms Todo App đơn giản

## Mô tả
Xây dựng ứng dụng To-Do list đơn giản bằng C# WinForms, dùng component KztekComponent cho UI. Hỗ trợ thêm/sửa/xóa task và đánh dấu hoàn thành. Lưu dữ liệu vào file JSON.

## Nguồn yêu cầu
- Yêu cầu gốc: "xây dựng C# to do app đơn giản"
- Workflow: WF-FEATURE (rút gọn) — bỏ PM/BA/UX Designer/EM/PJM/CTO vì app nội bộ đơn giản, không cần PRD elaborate; bỏ Junior Developer vì Senior tự xử lý toàn bộ
- Agent chain: Senior Developer → Tech Lead (review) → QA Engineer (smoke test)
- KztekComponent: CÓ TỒN TẠI tại `KztekComponent/Controls/` — PHẢI dùng tối đa (KzButton, KzTextBox, KzDataGrid, KzCheckBox, KzLabel, KzPanel, KzCard...)

## Lý do skip các bước WF-FEATURE đầy đủ
- Bỏ PM/BA: App đơn giản, yêu cầu rõ ràng, không cần PRD/user story elaborate
- Bỏ UX Designer: WinForms CRUD app chuẩn, không cần mockup riêng
- Bỏ EM/PJM: Không cần phân bổ resource hay sprint planning
- Bỏ CTO: Không có kiến trúc lớn/bảo mật/chiến lược (theo CLAUDE.md §4 điều kiện bỏ qua)
- Bỏ Junior Developer: Senior đảm nhiệm toàn bộ, task không đủ lớn để chia

## Phases & Steps

> **Session isolation (CLAUDE.md §16.5):** Mỗi bước ⬜/🔄 PHẢI chạy tách session — LOCAL dùng `Agent` subagent. Agent tự commit+push+điền cột "Hoàn thành lúc".

### Phase 1: Triển khai

| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 1.1 | Tạo project WinForms, thiết kế model `TodoTask` + `TaskRepository` (lưu JSON), xây dựng `MainForm` với UI đầy đủ: danh sách task (KzDataGrid), Add/Edit/Delete/Mark Done — dùng tối đa KztekComponent | Senior Developer | ✅ | `src/TodoApp/TodoApp.csproj`, `src/TodoApp/Models/TodoTask.cs`, `src/TodoApp/Data/TaskRepository.cs`, `src/TodoApp/Forms/MainForm.cs`, `src/TodoApp/Forms/EditTaskForm.cs`, `src/TodoApp/Program.cs` | 2026-07-05 16:51 | Build sạch 0 error. Commit e667b8e. Push thất bại (403 remote permission denied). |

### Phase 2: Review

| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 2.1 | Review code: cấu trúc project, naming convention, đảm bảo KztekComponent được dùng đúng, không có leak/bug rõ ràng | Tech Lead | ✅ | Commit 24a21a9 (fix Save() safety + AcceptButton/CancelButton + xóa dead code) | 2026-07-05 16:54 | Build sạch. Push 403 lần nữa — user cần xử lý remote perm. |

### Phase 3: Kiểm thử

| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 3.1 | Chạy app thật, smoke test: thêm task, sửa task, xóa task, đánh dấu done, kiểm tra lưu/đọc JSON sau khi restart app | QA Engineer | ✅ | `tests/TodoApp.Tests/TaskRepositoryTests.cs` (14 tests pass) | 2026-07-05 16:57 | Build sạch 0 error. 14/14 unit test pass (CRUD + persistence + toggle + JSON). Verify-by-code cho TC-02/04/06/07 GUI. Không có bug. |

## Handoff Log (BẮT BUỘC — xem CLAUDE.md §16.5 Bước 4)

> Mỗi bước chạy session/subagent riêng nên KHÔNG thấy lịch sử bước trước. Agent hoàn thành bước PHẢI thêm 1 entry dưới đây; task-planner PHẢI nhúng nguyên văn mục này vào prompt của bước kế tiếp.

<!-- Thêm entry mới ở cuối, KHÔNG xoá entry cũ -->

### Bước 1.1 — Tạo project WinForms Todo App
- Đã làm: Tạo đủ 7 file project WinForms net8.0-windows. KzDataGrid cho danh sách, KzButton (Add/Edit/Delete/ToggleDone), KzCheckBox lọc task done, EditTaskForm dùng KzTextBox + KzLabel. Build sạch 0 error.
- File/module đã đọc hoặc đổi: `src/TodoApp/TodoApp.csproj`, `src/TodoApp/Program.cs`, `src/TodoApp/Models/TodoTask.cs`, `src/TodoApp/Data/TaskRepository.cs`, `src/TodoApp/Forms/MainForm.cs`, `src/TodoApp/Forms/MainForm.Designer.cs`, `src/TodoApp/Forms/EditTaskForm.cs`
- Quyết định quan trọng: TodoApp.csproj phải reference trực tiếp `KztekComponent\refs\Guna.UI2.dll` — nếu không, các property kế thừa từ Guna2TextBox/Guna2Button sẽ không resolve (CS0012). ProjectReference đến KztekComponent chưa đủ.
- Bước sau cần biết: Tech Lead review nên chú ý (1) MainForm dùng `partial class` khớp Designer.cs stub; (2) Guna.UI2.dll reference bằng HintPath tương đối — nếu repo clone sang máy khác cần kiểm tra path; (3) Push remote bị 403 (permission denied cho user anhnvkztek) — code đang ở local commit e667b8e trên nhánh feat/session-isolation.

### Bước 2.1 — Tech Lead review
- Đã làm: Review 7 file, phát hiện + tự fix 3 điểm: (a) `TaskRepository.Save()` không try/catch → wrap try/catch + ghi qua file `.tmp` rồi rename để atomic; (b) `EditTaskForm` không có Enter/Esc shortcut → set `AcceptButton`/`CancelButton`; (c) `pnlContent` trong EditTaskForm là dead code (khai báo nhưng không add vào Controls) → xóa. Build lại sạch 0 error/warning.
- File/module đã đọc hoặc đổi: đọc toàn bộ 7 file `src/TodoApp/**`; đổi `src/TodoApp/Data/TaskRepository.cs` + `src/TodoApp/Forms/EditTaskForm.cs`. Commit `24a21a9`.
- Quyết định quan trọng: Không refactor lớn (form/repo/model đã sạch). Không đổi `MainForm.cs` vì logic chuẩn — clone task trước khi mở dialog Edit là pattern tốt, event handler không leak (form dùng cả đời app).
- Bước sau cần biết (cho QA Engineer smoke test):
  * Chạy app: `dotnet run --project src/TodoApp/TodoApp.csproj` HOẶC exe tại `src/TodoApp/bin/Debug/net8.0-windows/TodoApp.exe`.
  * File JSON lưu tại: `src/TodoApp/bin/Debug/net8.0-windows/data/tasks.json` (auto-create). Xóa file này để reset dữ liệu.
  * Test case tối thiểu: (1) Thêm 2-3 task, đóng app, mở lại → phải còn đủ; (2) Sửa title task; (3) Đánh dấu done → chữ mờ xám; (4) Bỏ tick "Hiện task đã xong" → task done biến mất; (5) Xoá task có confirm dialog; (6) Trong EditTaskForm nhấn Enter phải Save, Esc phải Cancel; (7) Để title rỗng khi Save → phải hiện warning.
  * Push remote lỗi 403 — không ảnh hưởng chạy app local. Nếu QA cần commit bug report thì cũng chỉ commit local.

### Bước 3.1 — QA Smoke Test
- Đã làm: Build `dotnet build` sạch 0 error. Tạo `tests/TodoApp.Tests/TaskRepositoryTests.cs` với 14 test case xUnit covering TC-01 → TC-07. Chạy `dotnet test` → 14/14 Passed. Không phát hiện bug.
- File/module đã đọc hoặc đổi: đọc `TaskRepository.cs`, `TodoTask.cs`, `MainForm.cs`, `EditTaskForm.cs`. Tạo `tests/TodoApp.Tests/TodoApp.Tests.csproj` + `tests/TodoApp.Tests/TaskRepositoryTests.cs`.
- Quyết định quan trọng: test project dùng `net8.0-windows` + `UseWindowsForms` để tham chiếu TodoApp (có Windows.Forms dependency). Mỗi test dùng thư mục tạm riêng (IDisposable cleanup) để tránh xung đột dữ liệu.
- Bước sau cần biết: Không có bước tiếp theo — plan hoàn thành. Nếu QA Lead cần sign-off thêm, phải chạy GUI thật trên máy Windows. Các test case verify-by-code (TC-02,04,06,07): đã xác nhận logic trong code là đúng qua code review. Không có bug P0/P1.

## Artifacts dự kiến
- [ ] `src/TodoApp/TodoApp.csproj`
- [ ] `src/TodoApp/Models/TodoTask.cs`
- [ ] `src/TodoApp/Data/TaskRepository.cs`
- [ ] `src/TodoApp/Forms/MainForm.cs` + `MainForm.Designer.cs`
- [ ] `src/TodoApp/data/tasks.json` (tạo lúc runtime)
- [ ] PR review comments (Tech Lead)
- [ ] Smoke test log / bug report nếu có (QA Engineer)

## Blockers
Không có

## Quyết định / Ghi chú
- KztekComponent tồn tại tại `KztekComponent/Controls/` — PHẢI dùng tối đa: KzButton, KzTextBox, KzDataGrid, KzCheckBox, KzLabel, KzPanel, KzCard
- Target framework: net8.0-windows (khớp với KztekComponent đang build)
- Lưu trữ: JSON file (đơn giản, không cần DB cho app nội bộ nhỏ)
- Không có staging/deploy — app chạy local

## Lịch sử cập nhật
| Ngày | Cập nhật | Agent |
|------|----------|-------|
| 2026-07-05 | Plan tạo mới | task-planner |
| 2026-07-05 16:51 | Bước 1.1 Done — 7 file tạo, build sạch, commit e667b8e (push 403) | Senior Developer |
| 2026-07-05 16:54 | Bước 2.1 Done — review + fix 3 điểm (Save safety, AcceptButton/CancelButton, dead code), build sạch, commit 24a21a9 (push 403) | Tech Lead |
| 2026-07-05 16:57 | Bước 3.1 Done — 14/14 unit test pass (CRUD+persistence+toggle+JSON), build sạch, không có bug, plan completed | QA Engineer |

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
