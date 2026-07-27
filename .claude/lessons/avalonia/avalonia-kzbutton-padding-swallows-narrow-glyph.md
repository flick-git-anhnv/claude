---
category: avalonia
tags: [KzButton, KzNumericUpDown, padding, ControlTheme, DataGrid]
severity: medium
created: 2026-07-20
updated: 2026-07-20
project-origin: iPGSv4 (KztekComponentAvalonia)
---

# KzButton Padding (kz-size-md = 16,0) nuốt mất glyph khi Width cố định nhỏ (40px)

## Tình huống gặp phải

> Đang fix bug UI theo báo cáo user: nút +/- trong `KzNumericUpDown` (dùng ở dialog Sửa Camera, field Channel/ZCU Index) hiển thị y hệt nhau, chỉ thấy 1 dấu chấm "." thay vì "−" và "+".

Control `KzNumericUpDown.axaml` đặt `Width="40" Height="40"` trực tiếp trên `KzButton` (Decrease/IncreaseBtn), dùng class `kz-size-md`.

## Triệu chứng / Lỗi

Cả 2 nút Decrease ("−") và Increase ("+") đều render giống hệt nhau, chỉ thấy một dấu chấm nhỏ ở giữa — không phân biệt được nút nào là trừ, nút nào là cộng.

## Nguyên nhân gốc rễ (Root Cause)

`KzButton.axaml` (ControlTheme) style `^.kz-size-md` set `Padding="{StaticResource kz.padding.btn.md}"` = `Thickness("16,0")` → Avalonia diễn giải Thickness 2 giá trị là (horizontal, vertical), tức là **16px áp cho CẢ trái lẫn phải** = tổng 32px padding ngang.

Với `Width="40"` cố định, vùng còn lại cho `ContentPresenter` chỉ còn `40 - 32 = 8px` — không đủ để vẽ glyph "−"/"+" (cần ~12-14px ở FontSize mặc định), nên bị co/clip gần như biến mất, chỉ còn 1 điểm ảnh mờ trông như dấu chấm.

Đây là lỗi tiềm ẩn (không có gì báo lỗi/warning khi build) — chỉ phát hiện được khi nhìn UI thật.

## Giải pháp

Set `Padding="0"` trực tiếp (local value) trên các nút icon-only có `Width`/`Height` cố định nhỏ — local property luôn thắng Style class setter trong Avalonia nên override an toàn, không ảnh hưởng các `KzButton` khác dùng `kz-btn-secondary`/`kz-size-md` ở nơi khác (không set Width cố định thì vẫn dùng padding mặc định để tự size theo nội dung).

```xml
<kz:KzButton Name="DecreaseBtn" Content="−" Width="40" Height="40"
             Padding="0" FontSize="18"
             Classes="kz-btn-secondary kz-size-md" />
```

Áp dụng cho cả 4 nút trong `KzNumericUpDown.axaml` (Horizontal: DecreaseBtn/IncreaseBtn; Vertical: IncreaseBtnV/DecreaseBtnV).

## Áp dụng lại (How to reuse)

- Khi thấy 1 `KzButton`/control kế thừa nó bị đặt `Width`/`Height` cố định NHỎ (icon-only, < ~48px) cùng lúc với 1 class size (`kz-size-sm/md/lg`) → PHẢI kiểm tra token padding tương ứng (`kz.padding.btn.*` trong `KzTokens.axaml`) có ăn hết phần lớn Width cố định không, trước khi debug xa hơn.
- Công thức nhanh: `nội dung khả dụng = Width - 2 × giá trị_ngang_của_Thickness_padding` (Thickness 2 giá trị = (ngang, dọc), áp cho cả 2 bên, KHÔNG phải tổng).
- Fix chuẩn: set `Padding="0"` (hoặc giá trị nhỏ hơn) local trên chính element đó — không sửa token global trừ khi muốn đổi toàn hệ thống.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Thickness Avalonia 2 giá trị `"H,V"` nghĩa là H áp cho CẢ Left và Right (không phải chia đôi) — dễ tính nhầm dẫn đến đánh giá sai dung lượng còn lại.
- ⚠️ Lỗi loại này KHÔNG xuất hiện trong build log/warning — chỉ phát hiện khi chạy app thật và nhìn UI (đúng lý do vì sao WF-FASTTRACK/UXR luôn yêu cầu kiểm tra trực quan trước khi merge).
- ⚠️ Cùng gốc rễ này cũng gây triệu chứng tương tự ở `KzDataGrid` cell/header (`Padding="12,8"`/`"12,10"`) khiến cột hẹp (Port, Kênh, ZCU index) bị cắt chữ — đã giảm còn `"8,8"`/`"8,10"` trong cùng lần fix.

## Tham chiếu

- File: `KztekComponentAvalonia/KztekComponentAvalonia/Controls/KzNumericUpDown.axaml`
- File liên quan: `KztekComponentAvalonia/KztekComponentAvalonia/Themes/KzButton.axaml`, `Theme/KzTokens.axaml` (`kz.padding.btn.md`)
- Project liên quan: iPGSv4 / IPGS.Control CameraWindow (Channel, ZCU Index dùng KzNumericUpDown)
