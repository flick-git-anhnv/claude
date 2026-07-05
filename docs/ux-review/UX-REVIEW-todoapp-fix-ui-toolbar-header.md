# UX/UI Review Report — 2026-07-05 (Fix Verification: UI-001 & UI-002)

**App / Module:** TodoApp — MainForm  
**Reviewer:** UX/UI Reviewer Agent  
**Môi trường:** Local | Build: Debug net8.0-windows  
**Tổng số màn hình review:** 1 (MainForm — focus xác nhận 2 fix)  
**Kết quả tổng quan:** PASS — UI-001 và UI-002 đã RESOLVED sau 2 lần sửa

---

## Bối cảnh

Report này xác nhận việc fix 2 issue phát hiện trong report trước (`UX-REVIEW-todoapp-search-box.md`):

- **UI-001** (High): Nút toolbar "Thêm/Sửa/Xoá/Đánh dấu xong" bị cắt text
- **UI-002** (High): Header title "Todo App" không hiển thị trong vùng nhìn thấy

---

## Quá trình sửa (ghi nhận trong session này)

### Lần sửa 1 (Senior Dev trước đó, Bước 1.1)
- Tăng width buttons (btnAdd 88→110px, btnEdit 80→100px, ...)
- Tăng y offset lblAppTitle (14→22px), lblSubtitle (42→48px)

**Kết quả sau lần sửa 1:**
- UI-001: "Thêm" vẫn bị cắt thành "Thê", "Đánh dấu xong" wrap 2 dòng — CHƯA HẾT
- UI-002: Header vẫn chỉ thấy subtitle, title "Todo App" invisible — CHƯA HẾT

**Screenshot:** `screenshots/2026-07-05/mainform-window-after-fix.png`

### Root cause phát hiện trong session này

**UI-001:** Width tăng không đủ — KzButton có padding nội bộ khiến text area nhỏ hơn tổng width.

**UI-002 (root cause thực sự):** `KzPanel.OnPaint()` hardcode `new SolidBrush(KzTokens.White)` để fill background, bỏ qua `BackColor` property hoàn toàn. Vì vậy dù set `BackColor = KzTokens.Navy900`, panel vẫn render nền trắng. Label "Todo App" với `ForeColor = White` trên nền trắng → invisible.

### Lần sửa 2 (UX/UI Reviewer — session này)

**File sửa 1:** `KztekComponent/Controls/KzPanel.cs`
- Sửa `OnPaint`: thay `new SolidBrush(KzTokens.White)` bằng `new SolidBrush(fillColor)` với `fillColor = BackColor == Transparent ? KzTokens.White : BackColor`
- Cho phép KzPanel render đúng màu BackColor được set từ bên ngoài

**File sửa 2:** `src/TodoApp/Forms/MainForm.cs`
- pnlHeader Height: 72 → 90px (đủ chỗ cho 2 dòng label)
- lblAppTitle Location.Y: 22 → 12px
- lblSubtitle Location.Y: 48 → 52px
- btnAdd Width: 110 → 130px
- btnEdit Width: 100 → 110px, Location.X: 130 → 150
- btnDelete Width: 100 → 110px, Location.X: 238 → 268
- btnToggleDone Width: 170 → 200px, Location.X: 346 → 386
- chkShowDone Location.X: 524 → 594

**Kết quả sau lần sửa 2:** RESOLVED — xem screenshots bên dưới.

---

## Chi tiết màn hình: MainForm (sau fix hoàn chỉnh)

**Screenshot:** `screenshots/2026-07-05/mainform-v3-final.png`
**Header zoom:** `screenshots/2026-07-05/mainform-v3-header-zoom.png`

| Tiêu chí | Kết quả | Ghi chú |
|---|---|---|
| C1 Layout hợp lý | PASS | Header → Toolbar → Search → Grid đúng thứ tự luồng. Action chính (Thêm) nổi bật ở vị trí đầu tiên. |
| C2 Không chồng chéo | PASS | Buttons cách nhau 8px gap, không overlap. chkShowDone tại x=594 (gap đủ từ btnToggleDone kết thúc x=586). |
| C3 Hiển thị đầy đủ | PASS | "Thêm", "Sửa", "Xoá", "Đánh dấu xong" — tất cả 1 dòng, không cắt. "Todo App" title hiển thị. |
| C4 Typography nhất quán | PASS | H3 bold cho title, Small/caption cho subtitle. Body font cho toolbar labels. Phân cấp rõ ràng. |
| C5 Màu sắc & Brand | PASS | Header Navy #251C53 (confirmed). Nút Primary Navy, Danger đỏ, Accent purple — đúng KzButton variant. Grid header Navy đậm. |
| C6 Trạng thái đặc biệt | PASS | Empty state (không có task) — grid trống, không crash. Buttons Sửa/Xoá/ToggleDone disabled khi không chọn. |
| C7 Khoảng cách & Alignment | PASS | Padding toolbar hợp lý (12,10). Header padding horizontal 20px. Labels căn trái nhất quán. |

---

## Tóm tắt phát hiện

| Mức độ | Số lượng |
|--------|---------|
| Critical (chặn release) | 0 |
| High (ảnh hưởng UX đáng kể) | 0 |
| Medium | 0 |
| Low (polish) | 0 |

**UI-001:** RESOLVED — Tất cả buttons toolbar hiển thị text đầy đủ 1 dòng.

**UI-002:** RESOLVED — Header "Todo App" hiển thị rõ, font H3 white trên nền Navy #251C53.

**Bonus fix (phát hiện trong session):** KzPanel.OnPaint hardcode White background — đây là bug ảnh hưởng toàn bộ KzPanel khi set BackColor khác trắng. Đã sửa tại source KztekComponent để tất cả panel khác cũng hưởng lợi.

---

## Issue còn tồn tại (từ report trước, vẫn là backlog)

| ID | Màn hình | Mô tả | Mức độ | Trạng thái |
|---|---|---|---|---|
| UI-003 | MainForm | lblSearch "Tìm kiếm:" và txtSearch lệch 4px vertical (y=12 vs y=8) | Low | Backlog |
| UI-004 | MainForm | pnlSearch BackColor trắng không phân biệt với form background | Low | Backlog — sẽ tự fix khi dùng đúng KzTokens.BgAlt |

---

## Kết luận

MainForm sau fix hoàn chỉnh đạt chất lượng hiển thị tốt. Không còn issue High hoặc Critical. UI-001 và UI-002 RESOLVED hoàn toàn. Sẵn sàng cho QA smoke test (Bước 3.1).

Root cause quan trọng nhất: `KzPanel.OnPaint` cần dùng `BackColor` thực tế thay vì hardcode White — đã fix tại KztekComponent để áp dụng toàn bộ component library.
