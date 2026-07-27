---
category: ui-patterns
tags: [avalonia, kztek-component, grid-column, overflow, numericupdown]
severity: medium
created: 2026-07-16
updated: 2026-07-16
project-origin: parking-v8-app-avalonia (KZTEK IPARKING v8 Avalonia)
---

# KzNumericUpDown (horizontal) có width cố định ~170px — nhét vào cột hẹp hơn sẽ bị chồng/lấn border

## Tình huống gặp phải

Đang thu gọn 1 panel cấu hình (Vùng Loop trong `LaneSettingsWindow.axaml`) theo yêu cầu user "tốn quá nhiều diện tích hiển thị" — giảm bề rộng panel từ 390px xuống 340px và gộp 2 hàng control thành 1 hàng 2 cột để tiết kiệm không gian dọc.

## Triệu chứng / Lỗi

Sau khi giảm width panel và/hoặc chia cột hẹp hơn, user báo "view vẫn bị chồng lấp" — nút `+`/giá trị của `KzNumericUpDown` (control cấu hình "Ngưỡng đến", "Chống trùng biển") bị cắt/tràn qua viền phải của khung chứa, nhìn như bị đè lên border.

## Nguyên nhân gốc rễ (Root Cause)

`KzNumericUpDown` (layout ngang, `src/ParkingV8.UI/Controls/Axaml/KzNumericUpDown.axaml`) gồm 3 phần trong 1 `StackPanel Orientation="Horizontal"`, MỖI phần có `Width` cố định (không co giãn):
- Nút giảm: `Width="45"`
- Ô giá trị: `Width="80"`
- Nút tăng: `Width="45"`

Tổng **170px cố định**, không có `MinWidth` linh hoạt, không co lại được dù được đặt trong cột Grid hẹp hơn. Khi cột chứa nó hẹp hơn 170px (sau khi giảm width panel cha hoặc chia đôi 1 hàng thành 2 cột bằng nhau), control vẫn render đúng 170px và **tràn ra ngoài** biên cột/border cha — Avalonia Grid mặc định không tự ép co nội dung có Width cố định.

## Giải pháp

1. Trước khi đặt `KzNumericUpDown` vào bất kỳ cột/StackPanel nào, tính available width thực tế của cột đó (trừ margin/padding 2 lớp: Grid margin ngoài + margin cục bộ của StackPanel chứa control).
2. Đảm bảo cột đó **≥ 170px** khả dụng. Nếu ghép 2 control cùng hàng (VD ComboBox + KzNumericUpDown), ưu tiên cho NumericUpDown cột cố định ≥170px và để phần còn lại (thường co giãn tốt hơn, VD ComboBox) nhận phần dư — KHÔNG chia đều 50/50 nếu tổng < ~350px.
3. Nếu bắt buộc phải thu hẹp panel, đo lại từng row có NumericUpDown trước khi đổi `ColumnDefinitions`/width tổng — đừng chỉ nhìn tổng thể "trông có vẻ vừa".

## Áp dụng lại (How to reuse)

- Trước khi giảm width bất kỳ panel/Grid nào chứa `KzNumericUpDown` (horizontal) → kiểm tra ngay cột/StackPanel chứa nó có ≥170px available không.
- Khi ghép nhiều control cùng 1 hàng để "gọn giao diện" → không chia cột đều nhau mặc định; ưu tiên đủ width cho control có kích thước cứng (NumericUpDown, control có Width literal trong XAML gốc) trước.
- Muốn NumericUpDown thật sự co giãn được → phải sửa control gốc (đổi `Width` cố định trong `KzNumericUpDown.axaml` thành `MinWidth` + cho `TextBox` value `HorizontalAlignment="Stretch"`), không sửa được từ nơi dùng.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ `KzComboBox` co giãn tốt (có `HorizontalAlignment="Stretch"`, không Width cứng) nên trông "vừa" trong preview nhỏ — dễ khiến người sửa layout tưởng nhầm cả 2 control đều co giãn được như nhau.
- ⚠️ Lỗi tràn border này KHÔNG gây exception, không có warning build — chỉ thấy qua chạy app thật/screenshot, dễ bị bỏ sót nếu chỉ build & đọc code.

## Tham chiếu

- Control: `src/ParkingV8.UI/Controls/Axaml/KzNumericUpDown.axaml`
- Nơi gặp: `src/ParkingV8.App/Views/LaneSettingsWindow.axaml` (panel Vùng Loop, tab Camera)
- Project liên quan: parking-v8-app-avalonia — plan `.claude/plans/PLAN-lanesettings-gap-2026-07-16.md`
