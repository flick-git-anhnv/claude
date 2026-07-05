---
task: todoapp-fix-ui-toolbar-header
created: 2026-07-05
updated: 2026-07-05 17:48
status: in-progress
workflow: WF-FASTTRACK
priority: P2
---

# PLAN: Fix UI-001 & UI-002 — TodoApp MainForm (Toolbar buttons bị cắt chữ + Header title không hiển thị)

## Mô tả
Fix 2 lỗi UI mức High phát hiện trong UX Review ngày 2026-07-05:
- **UI-001**: Nút toolbar "Thêm/Sửa/Xoá" bị cắt text nghiêm trọng do DPI scaling 125-150% trên Windows 11 khiến font render lớn hơn nhưng button width cố định.
- **UI-002**: Header title "Todo App" (KzLabel H3, Location y=14) không hiển thị trong vùng nhìn thấy — có thể bị titlebar Windows che.

Scope: WinForms layout fix, không đụng logic nghiệp vụ. Phù hợp WF-FASTTRACK.

## Nguồn yêu cầu
- UX Review report: `docs/ux-review/UX-REVIEW-todoapp-search-box.md`
- Workflow: WF-FASTTRACK — Sửa lỗi nhỏ không đụng logic nghiệp vụ
- Agent chain: Senior Developer → Tech Lead (review nhanh) → UX/UI Reviewer → QA Engineer

## Phases & Steps

> **Session isolation (CLAUDE.md §16.5):** Mỗi bước ⬜/🔄 PHẢI chạy tách session — LOCAL dùng `Agent` subagent, WEB dùng `RemoteTrigger`. Agent/trigger tự commit+push+điền cột "Hoàn thành lúc".

### Phase 1: Fix Code

| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 1.1 | Fix UI-001: Tăng width btn toolbar (btnAdd→100px, btnEdit→90px, btnDelete→90px, btnMarkDone cần wrap-check); Fix UI-002: Kiểm tra Location.Y của lblAppTitle, tăng thêm 8-10px hoặc dùng ClientRectangle offset để header hiển thị đúng trong client area. Sửa trong `MainForm.Designer.cs` (và `MainForm.cs` nếu có set property runtime). Không đụng search box / CRUD logic. | Senior Developer | ✅ | `src/TodoApp/Forms/MainForm.cs` | 2026-07-05 17:46 | Fix layout DPI scaling — cần hiểu AutoScaleMode/Anchor/AutoSize WinForms |

### Phase 2: Review & Kiểm tra trực quan

| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 2.1 | Review nhanh PR fix UI-001+UI-002: kiểm tra đúng property (Width/Location), không tạo regression cho search panel, không vi phạm DPI auto-scale. Approve hoặc request changes. | Tech Lead | ✅ | `src/TodoApp/Forms/MainForm.cs` (verify) | 2026-07-05 17:48 | Approve — không cần sửa |
| 2.2 | Chạy app thật lại sau fix, chụp screenshot MainForm, xác nhận UI-001 (buttons hiển thị đủ "Thêm", "Sửa", "Xoá") và UI-002 (header "Todo App" hiển thị trong vùng nhìn thấy). Đánh giá lại C1–C7. Tạo report `docs/ux-review/UX-REVIEW-todoapp-fix-ui-toolbar-header.md`. | UX/UI Reviewer | ⬜ | - | - | Chạy app thật bắt buộc — xem CLAUDE.md UXR rules |

### Phase 3: QA Smoke Test

| # | Bước | Agent | Status | Artifact | Hoàn thành lúc | Ghi chú |
|---|------|-------|--------|----------|-----------------|---------|
| 3.1 | Smoke test toàn bộ MainForm: (1) Buttons Thêm/Sửa/Xoá/Đánh-dấu-xong hoạt động đúng và hiển thị text đầy đủ. (2) Search box vẫn filter được task. (3) Header hiển thị đúng. (4) Grid hiển thị đủ 4 cột. Không cần regression test đầy đủ vì fix scope hẹp. | QA Engineer | ⬜ | - | - | Smoke test tối thiểu theo WF-FASTTRACK |

## Handoff Log (BẮT BUỘC — xem CLAUDE.md §16.5 Bước 4)

> Mỗi bước chạy session/subagent riêng nên KHÔNG thấy lịch sử bước trước. Agent hoàn thành bước PHẢI thêm 1 entry dưới đây; task-planner PHẢI nhúng nguyên văn mục này vào prompt của bước kế tiếp — tránh đọc lại/nghiên cứu lại.

<!-- Thêm entry mới ở cuối, KHÔNG xoá entry cũ -->

### Bước 1.1 — Fix UI-001 + UI-002
- Đã làm: Sửa `MainForm.cs` (layout code-behind duy nhất — Designer.cs chỉ là stub). UI-001: btnAdd 88→110px tại x=12, btnEdit 80→100px tại x=130, btnDelete 80→100px tại x=238, btnToggleDone 140→170px tại x=346, chkShowDone dịch sang x=524 (gap 8px mỗi nút). UI-002: lblAppTitle Location.Y 14→22px, lblSubtitle Location.Y 42→48px.
- File/module đã đọc hoặc đổi: `src/TodoApp/Forms/MainForm.cs` (đổi), `src/TodoApp/Forms/MainForm.Designer.cs` (đọc — chỉ là stub rỗng, không cần sửa), `docs/ux-review/UX-REVIEW-todoapp-search-box.md` (đọc root cause)
- Quyết định quan trọng: Toàn bộ layout trong MainForm.cs (InitializeComponent), Designer.cs là stub không chứa gì. btnToggleDone tăng lên 170px thay vì 140px đề xuất vì text "Đánh dấu chưa xong" dài hơn "Đánh dấu xong". Build sạch 0 error.
- Bước sau cần biết: Tech Lead (2.1) — không có regression với search panel (pnlSearch/txtSearch không đụng đến); chkShowDone x dịch từ 442→524 (đủ khoảng không bị che bởi btnToggleDone 170px). UX/UI Reviewer (2.2) — cần verify trực quan 2 điểm: (1) buttons hiển thị đủ text ở DPI 100% và 125%; (2) header lblAppTitle "Todo App" hiển thị rõ ở top panel. Lưu ý KzPanel padding là `new Padding(20, 0, 20, 0)` (chỉ horizontal) nên y=22 là offset thuần trong panel, không bị padding dọc ảnh hưởng.

### Bước 2.1 — Tech Lead review
- Đã làm: Verify `MainForm.cs` bằng đọc file. Kiểm tra toán học layout toolbar (btnAdd 12→122, btnEdit 130→230, btnDelete 238→338, btnToggleDone 346→516, chkShowDone x=524 — gap 8px giữa btnToggleDone kết thúc x=516 và chkShowDone x=524, KHÔNG overlap). Kiểm tra header (pnlHeader Height=72, lblAppTitle y=22 chiếm ~22-46, lblSubtitle y=48 chiếm ~48-64 — đều nằm trong panel). Form.Width=900 với pnlToolbar padding horizontal 12+12=24 → usable 876px, tổng width control kết thúc ~700px, còn dư. Search panel/grid/CRUD logic không đụng đến. `dotnet build` sạch 0 error (chỉ warning CA1416 platform từ KzKeyboard, không liên quan). APPROVED — không sửa.
- File/module đã đọc hoặc đổi: `src/TodoApp/Forms/MainForm.cs` (đọc)
- Quyết định quan trọng: Approve nguyên trạng. Gap 8px giữa btnToggleDone và chkShowDone chính xác — Senior đã tính đúng.
- Bước sau cần biết: UX/UI Reviewer (2.2) — chạy app bằng `dotnet run --project src/TodoApp/TodoApp.csproj` (target `net8.0-windows`). Số liệu mới cần chụp và so sánh với screenshot cũ trong `docs/ux-review/screenshots/`: (a) toolbar row buttons hiển thị full text "Thêm" / "Sửa" / "Xoá" / "Đánh dấu xong"; (b) header title "Todo App" hiển thị rõ ở y=22 trong panel navy 72px cao; (c) subtitle "Quản lý công việc của bạn" hiển thị ở y=48. Test ở DPI 100% và 125% nếu có thể. Không có regression để verify — search/CRUD nguyên trạng.

## Artifacts dự kiến
- [ ] `src/TodoApp/Forms/MainForm.Designer.cs` — sửa Width btnAdd/btnEdit/btnDelete, Location lblAppTitle
- [ ] `src/TodoApp/Forms/MainForm.cs` — nếu có property set runtime cần điều chỉnh
- [ ] `docs/ux-review/UX-REVIEW-todoapp-fix-ui-toolbar-header.md` — UX review report sau fix
- [ ] `docs/ux-review/screenshots/` — screenshot mới xác nhận 2 lỗi đã hết

## Blockers
Không có

## Quyết định / Ghi chú
- Fix chỉ tập trung UI-001 + UI-002 (High). UI-003 (alignment 4px) và UI-004 (màu panel) để backlog theo khuyến nghị của UX Reviewer.
- Senior Developer được dùng thay Junior vì DPI scaling WinForms cần hiểu AutoScaleMode/Anchor/MinimumSize — không phải fix đơn giản.
- Nguồn chi tiết root cause: `docs/ux-review/UX-REVIEW-todoapp-search-box.md` — bảng issue ID UI-001 và UI-002.

## Lịch sử cập nhật
| Ngày | Cập nhật | Agent |
|------|----------|-------|
| 2026-07-05 | Plan tạo mới | task-planner |
| 2026-07-05 17:46 | Bước 1.1 Done — Fix UI-001 (btn width) + UI-002 (header y offset); commit 8e130fe; push lỗi 403 | Senior Developer |
| 2026-07-05 17:48 | Bước 2.1 Done — Tech Lead review APPROVED, không cần sửa; build 0 error | Tech Lead |

---
**Status icons:** ⬜ Todo | 🔄 In Progress | ✅ Done | 🛑 Blocked | ⏭️ Skipped
