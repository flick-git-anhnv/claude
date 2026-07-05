# UX/UI Review Report — 2026-07-05

**App / Module:** TodoApp — MainForm (WinForms, KztekComponent)
**Reviewer:** UX/UI Reviewer Agent
**Môi trường:** Local Windows 11 | Build: Debug (dotnet run)
**Tổng số màn hình review:** 1 (MainForm — trạng thái mặc định)
**Kết quả tổng quan:** Cần cải thiện

> **Lưu ý môi trường:** App chạy thật qua `dotnet run`, chụp screenshot thật bằng PowerShell WinAPI. App chạy trong môi trường Windows 11 với DPI scaling có thể ảnh hưởng kích thước hiển thị.

---

## Tóm tắt phát hiện

| Mức độ | Số lượng |
|--------|---------|
| Critical (chặn release) | 0 |
| High (ảnh hưởng UX đáng kể) | 2 |
| Medium (khó chịu nhưng dùng được) | 1 |
| Low (polish / nice-to-have) | 1 |

---

## Chi tiết từng màn hình

### MainForm — Màn hình chính (default state)

**Screenshots:**
- `screenshots/2026-07-05/mainform-full.png` — Toàn bộ cửa sổ (900x620)
- `screenshots/2026-07-05/mainform-search-zoom.png` — Khu vực toolbar + search panel
- `screenshots/2026-07-05/mainform-header-zoom.png` — Khu vực header

| Tiêu chí | Kết quả | Ghi chú |
|---|---|---|
| C1 Layout hợp lý | Cần cải thiện | Search panel nằm đúng vị trí giữa toolbar và grid. Luồng Header → Toolbar → Search → Grid hợp lý, dễ hiểu. Tuy nhiên header không hiển thị đủ (xem C3). |
| C2 Không chồng chéo | Pass | Không phát hiện overlap giữa các control. Label "Tìm kiếm:" và textbox nằm trong bounds panel. |
| C3 Hiển thị đầy đủ | Fail | (1) **Toolbar buttons bị cắt text**: "Thêm" → "T", "Sửa" → "S↵ủ", "Xoá" → "X↵o", "Đánh dấu xong" wrap 2 dòng. (2) Header title "Todo App" (H3, Location y=14) không hiển thị — bị che bởi titlebar của Windows hoặc không đủ không gian render. |
| C4 Typography nhất quán | Pass | KzLabel Body cho "Tìm kiếm:", KzTextBox với font Body 13px — nhất quán với design system. Placeholder "Nhập tên task..." đọc được. |
| C5 Màu sắc & Brand | Pass | pnlSearch = BgDefault (#FFFFFF), pnlToolbar = BgAlt (#FAFAFA) — đúng palette KZTEK. Header NavY900 (#251C53) hiển thị đúng màu navy đậm. Không có màu lạ. |
| C6 Trạng thái đặc biệt | N/A | Empty state (grid trống khi không có task) hiển thị bình thường — grid header vẫn render đủ 4 cột. |
| C7 Khoảng cách & Alignment | Cần cải thiện | (1) Search panel: label "Tìm kiếm:" tại y=12, textbox tại y=8 — lệch nhau 4px. Về thị giác midpoint label (~12+8=20px) vs midpoint textbox (8+15=23px) — lệch ~3px, chấp nhận được với UX thực tế. (2) Gap label → textbox: ~12px (label kết thúc ~x=70, textbox bắt đầu x=82) — đủ, không bị chật. (3) Padding search panel 46px height / 30px textbox = 8px trên-dưới — cân đối. |

---

## Phân tích 4 điểm Tech Lead yêu cầu

| Điểm | Đánh giá |
|---|---|
| (i) Gap label→textbox (12px) | Đủ — không chật, không quá rộng. Người dùng nhận ra ngay label gắn với input. |
| (ii) Panel 46px / textbox 30px → padding 8px | Cân đối — textbox không bị tràn hoặc bị cắt viền. |
| (iii) BgDefault (white) vs BgAlt (#FAFAFA) | Chênh lệch màu rất nhỏ (~5/255 per channel) — trên màn hình thực tế gần như không phân biệt được bằng mắt. Tuy nhiên có đường phân cách (divider) giữa 2 panel nên vẫn tạo được phân tách trực quan. Chấp nhận được. |
| (iv) Placeholder "Nhập tên task..." | Rõ nghĩa, phù hợp với label "Tìm kiếm:". Người dùng hiểu ngay cần gõ gì. |

---

## Danh sách issue cần fix

| ID | Màn hình | Mô tả | Mức độ | Tiêu chí | Đề xuất fix |
|---|---|---|---|---|---|
| UI-001 | MainForm | Toolbar buttons "Thêm", "Sửa", "Xoá" bị cắt text do width quá hẹp so với font size (DPI scaling). "Thêm" (88px) → "T", "Sửa" (80px) → "S u". | High | C3 | Tăng width: btnAdd → 100px, btnEdit → 90px, btnDelete → 90px. Điều chỉnh x tương ứng. |
| UI-002 | MainForm | Header title "Todo App" (KzLabel H3, Location y=14) không hiển thị trong vùng nhìn thấy — có thể bị titlebar Windows che. Chỉ thấy subtitle ở y=42. | High | C3 | Kiểm tra client area offset: dùng `ClientRectangle` thay vì Location tuyệt đối, hoặc tăng Location.Y của lblAppTitle thêm 8-10px. |
| UI-003 | MainForm | Vertical alignment label "Tìm kiếm:" (y=12) vs txtSearch (y=8) lệch 4px — mắt tinh có thể nhận ra label cao hơn textbox một chút. | Low | C7 | Đồng nhất y=10 cho cả hai, hoặc căn giữa theo chiều cao panel (46px): label 16px → y=15; textbox 30px → y=8 (đã ổn). Hoặc giữ nguyên — lệch 4px là chấp nhận được. |
| UI-004 | MainForm | Màu BgDefault vs BgAlt (search vs toolbar) gần như không phân biệt được bằng mắt (#FFFFFF vs #FAFAFA). | Medium | C5 | Có thể thêm bottom border 1px cho pnlToolbar dùng màu #CBCBCB (Xám nhạt KZTEK) để tạo phân tách rõ hơn, hoặc giữ nguyên (divider tự nhiên của WinForms panel). |

---

## Kết luận & Đề xuất

**Search panel mới (mục tiêu chính của review này)**: Bố cục hợp lý, khoảng cách đủ, màu sắc đúng brand, placeholder rõ nghĩa. Không có vấn đề layout đáng phải sửa ở search panel.

**Vấn đề đáng chú ý nhất** (không phải do search box mà là toolbar sẵn có): Buttons "Thêm/Sửa/Xoá" bị cắt text nghiêm trọng trên màn hình thực tế — đây là UI-001, mức High, nên fix trước release. Nguyên nhân nhiều khả năng là DPI scaling 125-150% trên Windows 11 khiến font render lớn hơn nhưng button width cố định không đổi.

**Khuyến nghị**: Fix UI-001 (button width) và kiểm tra lại UI-002 (header title). UI-003 và UI-004 là low priority, có thể để backlog.
