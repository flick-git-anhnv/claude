---
category: avalonia
tags: [contentcontrol, datatemplate, z-order, grid, xaml-declaration-order, blank-view]
severity: high
created: 2026-07-21
updated: 2026-07-21
project-origin: iPGSv4 IPGS.Kiosk.Avalonia (migrate ucPaymentInfo)
---

# Avalonia: 2 bug layout — thiếu DataTemplate (ContentControl blank) + z-order sai trong Grid

## Tình huống gặp phải

Audit parity `ucPaymentInfo` → `PaymentMethodPanelView` Avalonia.
ContentControl dùng để host sub-views (QR / Visa / Cash / Voucher / Complete).
BtnBack (nút Quay lại) nằm cùng Grid với ContentControl.

## Bug 3 — Thiếu DataTemplate: ContentControl blank

### Triệu chứng
Khi `ActivePaymentContent = new CarVoucherViewModel(...)`, ContentControl không render gì — màn trắng.

### Nguyên nhân
`App.axaml` thiếu `<DataTemplate DataType="{x:Type vmCar:CarVoucherViewModel}">`.
Avalonia ContentControl dùng DataTemplate để ánh xạ ViewModel → View.
Không có DataTemplate → không biết render View nào → blank (không lỗi, không exception).

### Giải pháp
```xml
<!-- App.axaml — trong Application.DataTemplates -->
<DataTemplate DataType="{x:Type vmCar:CarVoucherViewModel}">
  <viewCar:CarVoucherView/>
</DataTemplate>
```

### Áp dụng lại
- Mỗi lần thêm 1 ViewModel mới vào `ActivePaymentContent` (hoặc bất kỳ ContentControl nào),
  **phải đăng ký DataTemplate tương ứng trong App.axaml NGAY**.
- Audit checklist khi migrate: đối chiếu danh sách tất cả sub-UC WinForms được Add vào panel
  vs danh sách DataTemplate trong App.axaml — thiếu 1-1 là bug.

---

## Bug 4 — Z-order sai: BtnBack luôn che ContentControl

### Triệu chứng
Sub-view (QR/Visa/...) hiển thị bị che một phần bởi BtnBack nằm đè lên trên.
WinForms: `ucCash.BringToFront()` → sub-UC che btnBack.
Avalonia port: BtnBack được khai báo cuối cùng trong XAML → z-order cao nhất → LUÔN trên cùng.

### Nguyên nhân
Trong Avalonia `<Grid>` (và hầu hết Panel) không có `ZIndex` tường minh:
**phần tử khai báo SAU trong XAML có z-order CAO HƠN** (render trên cùng).
Port ban đầu khai báo ContentControl trước, BtnBack sau → BtnBack luôn đè lên sub-UC.

### Giải pháp
Đảo thứ tự trong XAML: khai báo BtnBack TRƯỚC ContentControl.

```xml
<!-- PaymentMethodPanelView.axaml — thứ tự đúng -->

<!-- BtnBack khai báo TRƯỚC → z-order thấp hơn ContentControl -->
<controls:ArcButton x:Name="BtnBack"
                    VerticalAlignment="Bottom"
                    ... />

<!-- ContentControl khai báo SAU → z-order cao hơn, che BtnBack khi active -->
<ContentControl IsVisible="{Binding !IsMethodSelectionVisible}"
                Content="{Binding ActivePaymentContent}"
                ... />
```

### Áp dụng lại
- Khi port WinForms `.BringToFront()` / `.SendToBack()` → Avalonia:
  **Đặt lại thứ tự khai báo XAML** (hoặc dùng `Canvas.ZIndex` / `Panel.ZIndex` nếu cần dynamic).
- Rule nhớ: **"Sau là trên" trong Avalonia XAML** (tương tự HTML z-stacking với flow DOM).

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Missing DataTemplate không gây exception hay warning — ContentControl âm thầm blank.
  Cần kiểm tra App.axaml khi thêm ViewModel mới, không chỉ kiểm tra View tồn tại.
- ⚠️ `Panel.ZIndex` (explicit) override thứ tự XAML — nếu file cũ có ZIndex tường minh thì thứ tự khai báo không còn có nghĩa.
- ⚠️ `Canvas` dùng explicit `Canvas.Left`/`Canvas.Top` nhưng z-order vẫn theo thứ tự khai báo khi không có `Canvas.ZIndex`.

## Tham chiếu

- Project: iPGSv4 IPGS.Kiosk.Avalonia
  - `App.axaml` — DataTemplate registration
  - `Views/Payment/PaymentMethodPanelView.axaml` — z-order fix
- WinForms source: `ucPaymentInfo.cs` — `SelectQr()`, `SelectVisa()` call `.BringToFront()`
