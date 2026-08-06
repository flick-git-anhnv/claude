---
category: avalonia
tags: [custom-control, binding-priority, foreground, styledproperty, kzlabel]
severity: high
created: 2026-07-27
updated: 2026-07-27
project-origin: iPGSUseCam (KztekComponentAvalonia)
---

# Custom control ghi đè property đặt trong XAML khi gán ở mức LocalValue

## Tình huống gặp phải

> Đang làm gì? Tính năng gì? Môi trường nào?

Thư viện `KztekComponentAvalonia`, control `KzLabel : TextBlock` (repo `E:\KZTEK\Code_Git\5.BaseUI`).
Dùng trong app Avalonia `IPGSUseCam`, màn hình `CameraSettingWindow`/Zone Camera có tiêu đề khai báo:

```xml
<kz:KzLabel Text="Cấu hình Zone Camera" LabelType="H3"
            Foreground="{DynamicResource kz.brush.white}" />
```

đặt trên nền navy đậm.

## Triệu chứng / Lỗi

Tiêu đề hiện ra màu TỐI gần như không đọc được trên nền navy, dù XAML đã khai báo rõ
`Foreground="{DynamicResource kz.brush.white}"`. Nhìn thoáng qua dễ tưởng chữ bị
clipping/cắt, phải phóng to ảnh chụp mới nhận ra là sai màu chứ không phải sai layout.

```
Không có exception, không có warning build. Chỉ sai màu hiển thị lúc runtime.
```

## Nguyên nhân gốc rễ (Root Cause)

`KzLabel.ApplyStyle()` gán thẳng `Foreground = KzTokens.TextBrush;` — đây là ghi ở mức ưu
tiên **LocalValue** trong hệ thống property của Avalonia, cùng mức với giá trị đặt trong
XAML nên đè lên được (ai gán sau cùng thắng). Tệ hơn, `ApplyStyle()` được gọi trong
`OnAttachedToVisualTree`, tức chạy lại MỖI LẦN control gắn vào visual tree — nên màu XAML
bị xoá kể cả khi ban đầu áp đúng, không chỉ 1 lần lúc khởi tạo.

## Giải pháp

Ghi giá trị mặc định ở mức ưu tiên **Style** — thấp hơn LocalValue nên XAML luôn thắng khi
người dùng có set:

```csharp
using Avalonia.Data;
// ...
IBrush? typeForeground = KzTokens.TextBrush;
switch (LabelType)
{
    // ... gán typeForeground theo từng loại (H1, H2, H3, Body, ...)
}
SetValue(ForegroundProperty, typeForeground, BindingPriority.Style);
```

1. Xác định property nào control tự set mặc định nhưng cũng có thể bị override từ XAML
   (Foreground, Background, FontSize, FontWeight...).
2. Thay mọi chỗ gán trực tiếp `Property = value;` bằng
   `SetValue(Property, value, BindingPriority.Style);`.
3. Test lại: đặt giá trị tường minh trong XAML → phải thắng; không đặt gì → dùng đúng
   default theo `LabelType`.

## Áp dụng lại (How to reuse)

- Khi thấy 1 property của Kz custom control "không nhận" giá trị XAML dù binding đúng,
  không exception → kiểm tra ngay code-behind của control có gán trực tiếp
  `Property = value` trong `ApplyStyle()`/`OnAttachedToVisualTree`/setter hay không.
- Trước khi viết custom control mới cho `KztekComponentAvalonia`, mặc định dùng
  `SetValue(..., BindingPriority.Style)` cho MỌI property có giá trị mặc định theo biến
  thể (variant/type/size) — không dùng phép gán CLR trực tiếp.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ **Cách sửa SAI đã thử:** dùng `this.IsSet(ForegroundProperty)` để dò xem người dùng
  có tự đặt màu không rồi mới bỏ qua override — KHÔNG ăn. Với `{DynamicResource ...}`, tại
  thời điểm `OnAttachedToVisualTree` chạy thì resource có thể chưa phân giải xong nên
  `IsSet` vẫn trả về `false`, control vẫn đè màu như cũ. Đừng lặp lại hướng debug này.
- ⚠️ Bug này lặp lại MỖI LẦN control re-attach vào visual tree (đổi tab, mở lại dialog...),
  không chỉ 1 lần lúc khởi tạo — nếu test chỉ mở màn hình 1 lần rồi không mở lại, rất dễ bỏ
  sót vì lần đầu có thể tình cờ đúng thứ tự.
- ⚠️ Cùng họ với lỗi `KzBadge`: CLR setter gọi `UpdateClasses()` nhưng binding ghi thẳng
  vào StyledProperty nên không đi qua setter — nguyên tắc chung: **binding và XAML KHÔNG
  đi qua CLR setter**, phải xử lý trong `OnPropertyChanged` hoặc dùng đúng `BindingPriority`.
  Đã fix và ghi lại chi tiết ở [[avalonia-kzbadge-onattachedtovisualtree-forces-neutral-class]]
  (2026-08-06) — khác với case `Foreground` ở trên, `KzBadge` dùng property enum thường
  (không phải `DynamicResource`) nên `IsSet(...)` dùng được, không gặp vấn đề resource
  chưa phân giải xong.

## Tham chiếu

- Commit tham chiếu: `5506933` (repo `5.BaseUI`), phát hiện 2026-07-27 trên project iPGSUseCam.
- Project liên quan: `KztekComponentAvalonia` (`5.BaseUI`), `iPGSUseCam` (`iPGSv4`).
