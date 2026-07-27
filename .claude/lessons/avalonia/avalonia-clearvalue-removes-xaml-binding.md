---
category: avalonia
tags: [clearvalue, borderbrush, xaml-binding, kztek-component, custom-control]
severity: medium
created: 2026-07-16
updated: 2026-07-16
project-origin: parking-v8-app-avalonia
---

# `Border.ClearValue(BorderBrushProperty)` trong code-behind xóa luôn binding XAML ban đầu — border biến mất

## Tình huống gặp phải

> Đang sửa `KzPasswordTextBox` (control custom trong `ParkingV8.UI.KztekComponents.Controls`) vì user báo "KzPassword không hiển thị border".

Control có `<Border Name="OuterBorder" BorderBrush="{Binding BorderBrush, RelativeSource={RelativeSource AncestorType=UserControl}}" .../>` trong XAML — set border brush ban đầu bằng binding tới property `BorderBrush` của chính `UserControl`. Code-behind (`OnAttachedToVisualTree`) sau đó gọi `ApplyInputState()` để áp style theo `InputState` (Normal/Error/Disabled).

## Triệu chứng / Lỗi

Border của `KzPasswordTextBox` không hiển thị ở trạng thái `Normal` (mặc định), trong khi `Error` và `Disabled` vẫn có border bình thường. Không có exception, chỉ là visual bug.

## Nguyên nhân gốc rễ (Root Cause)

Trong nhánh `default:` của `ApplyInputState()` và trong `ApplyBorderDefault()`, code gọi:

```csharp
border.ClearValue(Border.BorderBrushProperty);
```

`ClearValue()` không chỉ xóa giá trị code-behind set trước đó — nó xóa **toàn bộ local value**, bao gồm cả binding đã khai báo trong XAML (`{Binding BorderBrush, RelativeSource=...}`). Sau khi `ClearValue`, property fallback về default của `Border.BorderBrush` (là `null`), không phải quay lại binding gốc. Vì vậy ở trạng thái Normal, control không có border nào cả — kể cả khi consumer (view dùng control) đã set `BorderBrush="..."` khi khai báo instance.

`Error`/`Disabled` không bị ảnh hưởng vì 2 nhánh đó **set trực tiếp** `border.BorderBrush = KzTokens.ErrorBrush` / `KzTokens.BorderBrush` thay vì `ClearValue`.

## Giải pháp

Thay `ClearValue(BorderBrushProperty)` bằng cách set trực tiếp brush mặc định của input (theo token semantic `Brush.InputBorder` — cùng token mà `KzTextBox` dùng cho border mặc định), thay vì trông cậy vào binding còn sống sau `ClearValue`:

```csharp
private static IBrush ResolveBrush(string resourceKey, string fallbackHex)
{
    if (Application.Current?.TryFindResource(resourceKey, out var resource) == true &&
        resource is IBrush brush)
        return brush;
    return new SolidColorBrush(Color.Parse(fallbackHex));
}

// trong ApplyInputState() nhánh default, và ApplyBorderDefault():
border.BorderBrush = ResolveBrush("Brush.InputBorder", "#BFD0F2");
```

1. Xác định control đã dùng `ClearValue` ở đâu (grep `ClearValue(Border` trong `.axaml.cs`).
2. Đối chiếu control tương tự cùng nhóm (ở đây là `KzTextBox`) xem token brush mặc định nào đang dùng cho border — dùng lại đúng token đó để nhất quán theme.
3. Thay `ClearValue` bằng set trực tiếp giá trị brush (không dựa vào binding "sống lại" sau ClearValue).
4. Build lại, kiểm tra bằng mắt (chạy app thật) ở cả 3 trạng thái Normal/Error/Disabled và cả 2 theme Light/Dark.

## Áp dụng lại (How to reuse)

- Khi thấy control custom Avalonia có border/brush "biến mất" ở 1 trạng thái cụ thể nhưng các trạng thái khác vẫn ổn → grep `ClearValue(` trong code-behind của control đó trước tiên.
- Nguyên tắc chung: **không dùng `ClearValue()` để "reset về mặc định XAML"** nếu property đó được set bằng `{Binding ...}` trong XAML — `ClearValue` sẽ xóa cả binding, không phải chỉ giá trị code-behind ghi đè. Muốn quay lại giá trị ban đầu, phải set lại giá trị tường minh (constant hoặc resolved resource), không trông cậy fallback.
- Khi 1 control có nhiều state (Normal/Error/Disabled/Focused/Hover) set brush theo state trong code-behind, PHẢI đảm bảo state "Normal/default" cũng set brush tường minh giống các state khác — không được là nhánh duy nhất dùng `ClearValue`.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ `ClearValue()` hoạt động đúng như "xóa local value" theo tài liệu Avalonia — không phải bug của framework, mà là hiểu sai rằng nó sẽ "quay lại binding ban đầu trong XAML". Binding trong XAml CŨNG LÀ local value, nên bị xóa theo.
- ⚠️ Bug loại này chỉ hiện ở đúng 1 trạng thái cụ thể (thường là trạng thái mặc định `default:`/`Normal` vì đó là nơi hay bị "lười" set giá trị, chỉ ClearValue cho gọn) — dễ bị bỏ sót nếu chỉ test control ở trạng thái Error/Disabled.
- ⚠️ Nên kiểm tra các control "chị em" cùng nhóm (VD: `KzTextBox`, `KzNumericUpDown`) xem đã dùng token brush semantic nào cho border mặc định để giữ nhất quán, tránh mỗi control 1 màu border khác nhau.

## Tham chiếu

- File liên quan: `src/ParkingV8.UI/Controls/Cs/KzPasswordTextBox.axaml.cs`, `src/ParkingV8.UI/Controls/Axaml/KzPasswordTextBox.axaml`
- Control tham chiếu style nhất quán: `src/ParkingV8.UI/Controls/Axaml/KzTextBox.axaml` (dùng `Brush.InputBorder` cho border mặc định)
- Project liên quan: parking-v8-app-avalonia
