---
task: todoapp-search-box
created: 2026-07-05
updated: 2026-07-05 17:26
status: in-progress
workflow: WF-FASTTRACK (có UX/UI Reviewer vì đổi UI)
priority: P3
---

# PLAN: Thêm Search Box vào TodoApp

## Mô tả
Thêm ô tìm kiếm (KzTextBox) vào MainForm của TodoApp (WinForms). Khi user gõ, danh sách task lọc theo Title (case-insensitive, real-time qua TextChanged). Bộ lọc search kết hợp được với filter "hiện task đã xong" hiện có.

## Nguồn yêu cầu
- Yêu cầu gốc: "Thêm 1 ô tìm kiếm (search box) vào TodoApp — lọc danh sách task theo tên khi gõ vào ô đó. Dùng KzTextBox cho ô tìm kiếm."
- Workflow: WF-FASTTRACK rút gọn (tính năng UI nhỏ, không đụng logic nghiệp vụ phức tạp) + bắt buộc có UX/UI Reviewer vì có thay đổi UI.
- Agent chain: Junior Developer → Tech Lead → UX/UI Reviewer → QA Engineer

## Files liên quan
- `src/TodoApp/Forms/MainForm.cs`
- `src/TodoApp/Forms/MainForm.Designer.cs`

## Phases & Steps

> **Session isolation (CLAUDE.md §16.5):** Mỗi bước ⬜/🔄 PHẢI chạy tách session — LOCAL dùng `Agent` subagent, WEB dùng `RemoteTrigger`. Agent/trigger tự commit+push+điền cột "Hoàn thành lúc".

### Phase 1: Implement

| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 1.1 | Thêm KzTextBox search box vào MainForm.cs và MainForm.Designer.cs; xử lý sự kiện TextChanged để filter task list theo Title (case-insensitive); đảm bảo search filter kết hợp được với filter "hiện task đã xong" hiện có | Junior Developer | ✅ | `src/TodoApp/Forms/MainForm.cs` | 2026-07-05 17:19 | Dùng KzTextBox, không dùng TextBox gốc |

### Phase 2: Review & UX Check

| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 2.1 | Review nhanh code search box: logic filter đúng không, KzTextBox dùng đúng không, kết hợp filter không bị conflict | Tech Lead | ✅ | Review OK — không cần sửa code | 2026-07-05 17:20 | Build sạch 0 errors; giữ null-conditional làm defensive |
| 2.2 | Chạy app thật (nếu build được) hoặc verify code; đánh giá bố cục ô search có hợp lý không (vị trí, kích thước, label); chụp screenshot nếu chạy được; đánh giá C1–C7 | UX/UI Reviewer | ✅ | `docs/ux-review/UX-REVIEW-todoapp-search-box.md` + `screenshots/2026-07-05/*.png` | 2026-07-05 17:26 | Chạy app thật, chụp 3 screenshot. Search panel PASS. 2 issue High ở toolbar (button text truncated) và header title ẩn — không do search box. |

### Phase 3: QA Smoke Test

| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 3.1 | Smoke test: gõ text tìm kiếm → list lọc đúng; xóa text → list về đủ; kết hợp filter "done" + search → kết quả chính xác; case-insensitive hoạt động | QA Engineer | ⬜ | smoke test log (nhúng trong PR hoặc comment) | - | |

## Handoff Log (BẮT BUỘC — xem CLAUDE.md §16.5 Bước 4)

> Mỗi bước chạy session/subagent riêng nên KHÔNG thấy lịch sử bước trước. Agent hoàn thành bước PHẢI thêm 1 entry dưới đây; task-planner PHẢI nhúng nguyên văn mục này vào prompt của bước kế tiếp — tránh đọc lại/nghiên cứu lại.

<!-- Thêm entry mới ở cuối, KHÔNG xoá entry cũ -->

### Bước 1.1 — Thêm search box
- Đã làm: Thêm KzPanel pnlSearch (height 46, DockStyle.Top) chứa KzLabel lblSearch và KzTextBox txtSearch vào MainForm. Handler TxtSearch_TextChanged gọi RefreshGrid(). RefreshGrid() áp dụng AND: nếu keyword không rỗng thì lọc Title.Contains(keyword, OrdinalIgnoreCase) sau khi đã lọc showDone.
- File/module đã đọc hoặc đổi: `src/TodoApp/Forms/MainForm.cs`, `src/TodoApp/Forms/MainForm.Designer.cs` (chỉ đọc — stub), `KztekComponent/Controls/KzTextBox.cs` (xác minh PlaceholderText), `src/TodoApp/Forms/EditTaskForm.cs` (xác minh cú pháp PlaceholderText đang dùng)
- Quyết định quan trọng: pnlSearch đặt giữa pnlToolbar và grid (Controls.Add theo thứ tự Fill→pnlSearch→pnlToolbar→pnlHeader); label "Tìm kiếm:" + txtSearch width 300 tại Location (82,8); PlaceholderText = "Nhập tên task..."
- Bước sau cần biết: Tech Lead (2.1) kiểm tra logic AND trong RefreshGrid() — `txtSearch?.Text?.Trim()` dùng null-conditional vì txtSearch có thể null lúc form chưa init đủ. UX/UI Reviewer (2.2): pnlSearch nằm ngay dưới pnlToolbar, chiều cao 46px, nhãn "Tìm kiếm:" ở trái, txtSearch width 300 ở giữa-trái — cần đánh giá bố cục tổng thể có cân đối không.

### Bước 2.2 — UX/UI Review
- Đã làm: Chạy app thật (`dotnet run`), xác nhận PID 35548, dùng WinAPI lấy window handle → chụp 3 screenshot (mainform-full.png, mainform-search-zoom.png, mainform-header-zoom.png). Đánh giá C1-C7. Search panel PASS toàn bộ. Phát hiện 2 issue High không liên quan search box: (1) toolbar button text bị cắt nghiêm trọng do DPI scaling (UI-001), (2) header title "Todo App" không hiển thị (UI-002). Không sửa code vì issue không thuộc scope search box và cần xác nhận từ Tech Lead trước.
- File/module đã đọc hoặc đổi: `src/TodoApp/Forms/MainForm.cs` (đọc), `docs/ux-review/UX-REVIEW-todoapp-search-box.md` (tạo mới), `docs/ux-review/screenshots/2026-07-05/*.png` (3 file)
- Quyết định quan trọng: Không sửa code trong review lần này — issue nằm ở toolbar button width (pre-existing), không phải search box. Search box layout đạt yêu cầu.
- Bước sau cần biết: QA Engineer (3.1) smoke test search: (1) gõ text → list lọc real-time; (2) xóa → list khôi phục đủ; (3) kết hợp chkShowDone + search → AND filter đúng; (4) case-insensitive. Lưu ý: buttons toolbar bị cắt text (T, S u, X o) là cosmetic issue, không ảnh hưởng functional test nhưng cần note. Build hiện tại 0 errors.

### Bước 2.1 — Tech Lead review
- Đã làm: Review code MainForm.cs (search block dòng 164–192 + RefreshGrid dòng 274–306). Verify: (a) Logic AND filter đúng — showDone continue trước, keyword continue sau, hai filter độc lập AND. (b) Null-conditional `txtSearch?.Text?.Trim()` là defensive coding, thực tế RefreshGrid gọi sau InitializeComponent nên txtSearch không null, nhưng giữ nguyên để defensive — không phải bug. (c) KzTextBox API dùng đúng (PlaceholderText, Width, Height, Location, TextChanged). (d) `string.Contains(string, StringComparison.OrdinalIgnoreCase)` an toàn với Unicode/ký tự đặc biệt; Trim() không throw. Build sạch 0 errors (chỉ có 1901 CA1416 warnings từ KztekComponent, không liên quan). **KHÔNG cần sửa code.**
- File/module đã đọc hoặc đổi: `src/TodoApp/Forms/MainForm.cs` (chỉ đọc), `src/TodoApp/Forms/MainForm.Designer.cs` (chỉ đọc). Không sửa file nào.
- Quyết định quan trọng: Giữ nguyên `txtSearch?.Text?.Trim()` — defensive coding OK cho scope nhỏ, không đáng risk regression khi bỏ. Không tối ưu `Rows.Clear() + rebuild` mỗi keystroke vì dataset in-memory nhỏ.
- Bước sau cần biết: UX/UI Reviewer (2.2) — code đã approved technically. Cách chạy app: `dotnet run --project src/TodoApp/TodoApp.csproj` (Windows). Bố cục cần đánh giá: header (72px, Navy900) → toolbar (56px, BgAlt, 5 controls) → **pnlSearch (46px, BgDefault, label "Tìm kiếm:" @ (12,12) + txtSearch W=300 @ (82,8))** → grid (Fill). Điểm cần chú ý: (i) khoảng cách label→textbox có đủ không (label AutoSize kết thúc ~x=70, textbox bắt đầu x=82 → gap 12px); (ii) chiều cao pnlSearch 46 vs textbox 30 → padding trên/dưới 8px, có cân không; (iii) màu nền pnlSearch (BgDefault) khớp form nhưng khác pnlToolbar (BgAlt) — có tạo cảm giác phân tách rõ không; (iv) placeholder "Nhập tên task..." có rõ nghĩa không.

## Artifacts dự kiến
- [ ] `src/TodoApp/Forms/MainForm.cs` — cập nhật thêm search box + filter logic
- [ ] `src/TodoApp/Forms/MainForm.Designer.cs` — cập nhật layout Designer
- [ ] `docs/ux-review/UX-REVIEW-todoapp-search-box.md` — UX/UI Reviewer report
- [ ] Smoke test log (QA Engineer)

## Blockers
Không có

## Quyết định / Ghi chú
- Dùng KzTextBox (từ KztekComponent) — không dùng TextBox gốc .NET.
- Filter logic: kết hợp AND giữa search text và filter done (cả hai cùng lúc).
- Real-time filter qua sự kiện TextChanged (không cần nút Search riêng).

## Lịch sử cập nhật
| Ngày | Cập nhật | Agent |
|------|----------|-------|
| 2026-07-05 | Plan tạo mới | task-planner |
| 2026-07-05 17:19 | Bước 1.1 Done — thêm KzTextBox search box, build sạch, commit c21e86a | Junior Developer |
| 2026-07-05 17:20 | Bước 2.1 Done — Tech Lead review OK, không cần sửa code, build sạch | Tech Lead |
| 2026-07-05 17:26 | Bước 2.2 Done — UX/UI Review: chạy app thật, chụp 3 screenshot, search panel PASS, phát hiện UI-001/UI-002 ở toolbar/header (không liên quan search) | UX/UI Reviewer |

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
