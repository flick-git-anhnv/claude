---
category: avalonia
tags: [kztek-component-avalonia, KzPasswordTextBox, binding, TwoWay, UserControl, silent-failure]
severity: high
created: 2026-07-26
updated: 2026-07-26
project-origin: App-Access-V2 (migrate iAccessDesktopv2 WinForms → Avalonia)
---

# KzPasswordTextBox (UserControl) — binding Text mặc định OneWay, VM không nhận giá trị gõ vào mà không báo lỗi

## Tình huống gặp phải

> Đang làm gì? Tính năng gì? Môi trường nào?

STEP-3.2 PLAN-migrate-avalonia: migrate `ucServerConfig` (tab Server của ConnectionConfig) sang Avalonia 12.1.0, field mật khẩu RabbitMQ dùng `KzPasswordTextBox` của KztekComponentAvalonia, bind `Text="{Binding RabbitMqPassword}"` vào ViewModel.

## Triệu chứng / Lỗi

> Lỗi hiện ra như thế nào? Exception message? Behavior sai?

```
- UI hiển thị đúng giá trị ban đầu từ VM, nhưng user gõ mật khẩu mới → VM.RabbitMqPassword
  KHÔNG đổi → Save ghi ra file giá trị cũ/rỗng. KHÔNG có binding error, KHÔNG exception.
- Placeholder tự hiện "Nhập mật khẩu" dù XAML không set Watermark.
- CornerRadius="8" FontSize="16" set trong XAML không có tác dụng gì trên control.
```

## Nguyên nhân gốc rễ (Root Cause)

`KzPasswordTextBox` là **UserControl** (composite: Border + TextBox PART_Input + nút mắt), KHÔNG kế thừa TextBox:

1. `TextProperty` tự đăng ký bằng `AvaloniaProperty.Register<KzPasswordTextBox, string?>(nameof(Text))` — **không có `defaultBindingMode: BindingMode.TwoWay`** → binding từ ngoài mặc định **OneWay**. (Khác `TextBox.Text` vốn default TwoWay — nên `KzTextBox : TextBox` không bị.)
2. `WatermarkProperty` đăng ký với **default value `"Nhập mật khẩu"`**.
3. `CornerRadius`/`FontSize` của UserControl không được forward vào `PART_Border`/`PART_Input`; `ApplySize()` còn ghi đè FontSize theo `KzSize` lúc attach.

## Giải pháp

```xml
<!-- ĐÚNG -->
<kz:KzPasswordTextBox Height="36" Watermark=""
                      Text="{Binding RabbitMqPassword, Mode=TwoWay}" />
```

1. Luôn ghi rõ `Mode=TwoWay` khi bind `Text` của `KzPasswordTextBox`.
2. Set `Watermark=""` nếu nguồn/parity không có placeholder.
3. Không set `CornerRadius`/`FontSize` trực tiếp — dùng `KzSize` (Sm/Md/Lg) + `Height`.

## Áp dụng lại (How to reuse)

- Khi bind property của **bất kỳ control Kz nào là UserControl** (KzPasswordTextBox, KzIPTextbox, KzNumericUpDown, KzCard...) → mở source control kiểm tra `AvaloniaProperty.Register` có `defaultBindingMode: TwoWay` không; không có → viết `Mode=TwoWay` tường minh.
- Dấu hiệu nhận biết: UI hiển thị OK nhưng VM không nhận input, không có lỗi nào → nghi OneWay binding trước tiên.
- Kiểm tra default value của StyledProperty (Watermark...) — default không rỗng sẽ lộ ra UI.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Đây là silent failure — build sạch, chạy không lỗi, chỉ phát hiện khi test save/load thật.
- ⚠️ `KzTextBox : TextBox` hành xử NGƯỢC LẠI (TwoWay mặc định, nhận CornerRadius/FontSize/Height) — đừng suy từ KzTextBox sang các control UserControl khác.
- ⚠️ Không tự vá library 5.BaseUI trong task migrate — workaround XAML đủ; muốn sửa gốc phải mở task riêng cho repo KztekComponentAvalonia.

## Tham chiếu

- Source: `5.BaseUI/KztekComponentAvalonia/KztekComponentAvalonia/Controls/KzPasswordTextBox.axaml.cs` (TextProperty dòng ~28, ApplySize ~149)
- GOTCHAS.md entry G004
- Project liên quan: App-Access-V2 (STEP-3.2 `ServerConfigSectionView.axaml`)
