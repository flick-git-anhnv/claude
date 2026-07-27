---
category: avalonia
tags: [contentcontrol, navigation, payment, remain-zero, sentinel-value, callback]
severity: critical
created: 2026-07-21
updated: 2026-07-21
project-origin: iPGSv4 IPGS.Kiosk.Avalonia (migrate ucPaymentInfo)
---

# Avalonia: 2 bug cùng gốc trong PaymentInfoViewModel — remain=0 blank + GoHome không chuyển trang

## Tình huống gặp phải

Audit parity `ucPaymentInfo` (WinForms, 1227 LOC) vs `PaymentInfoViewModel` Avalonia.
Control lớn nhất trong nhánh Ô TÔ, xử lý chọn phương thức thanh toán + callback flow.

## Triệu chứng / Lỗi

**Bug 1 — remain=0:** Xe đã thanh toán hết (remain ≤ 0) vào màn PaymentInfo
→ WinForms: hiển thị ngay `ucCarPaymentComplete` (cảm ơn)
→ Avalonia port: `PaymentCompleted` event được fire đúng, nhưng màn hình trắng — ContentControl không hiện gì.

**Bug 2 — "Trang chủ" sai:** Sau khi hoàn tất thanh toán, nhấn "Trang chủ" trên `CarPaymentCompleteView`
→ WinForms: `KioskHelper.OpenMainWindow()` → về màn chủ (SelectLanguage)
→ Avalonia port: `OnPaymentCancelled(PaymentMethod.None)` → xóa `ActivePaymentContent` → quay lại chọn phương thức, KHÔNG điều hướng về Home.

## Nguyên nhân gốc rễ (Root Cause)

**Bug 1:** `Init()` đã fire `PaymentCompleted?.Invoke(...)` nhưng KHÔNG set `ActivePaymentContent = new CarPaymentCompleteViewModel(...)` trước đó.
`ContentControl` bind tới `ActivePaymentContent` → vẫn null → blank.
WinForms dùng `Control.Controls.Add(ucComplete)` trực tiếp nên không cần "bind" — Avalonia thì ContentControl PHẢI có object để render DataTemplate.

**Bug 2:** `CarPaymentCompleteViewModel.GoHome()` gọi `_callback.OnPaymentCancelled(PaymentMethod.None)` (dùng `PaymentMethod.None` làm sentinel "về trang chủ").
Nhưng `PaymentInfoViewModel.OnPaymentCancelled()` không có branch xử lý riêng cho `PaymentMethod.None` → rơi vào code chung: xóa `ActivePaymentContent`, reset về method selection → người dùng thấy trang chọn QR/Visa thay vì trang chủ.

## Giải pháp

**Fix 1** — `PaymentInfoViewModel.Init()`:
```csharp
if (vehicleData.GetRemain() <= 0)
{
    // PHẢI set ActivePaymentContent trước khi invoke event
    // nếu không ContentControl sẽ blank (không có object để render DataTemplate)
    ActivePaymentContent = new CarPaymentCompleteViewModel(this, vehicleData, DateTime.Now);
    ActivePaymentMethod  = PaymentMethod.None;
    PaymentCompleted?.Invoke(this,
        new PaymentCompletedEventArgs(PaymentMethod.None, true, string.Empty, vehicleData.GetTotalPaid()));
}
```

**Fix 2** — `PaymentInfoViewModel.OnPaymentCancelled()`:
```csharp
public void OnPaymentCancelled(PaymentMethod method)
{
    if (method == PaymentMethod.None)
    {
        // PaymentMethod.None = sentinel từ CarPaymentCompleteViewModel.GoHome()
        // Parity WinForms: UcComplete_onBackClick → KioskHelper.OpenMainWindow()
        ActivePaymentContent = null;
        _nav.NavigateTo(AppRoutes.SelectLanguage);
        return;
    }
    ActivePaymentContent = null;
    ActivePaymentMethod  = PaymentMethod.None;
}
```

Cần thêm `using IPGS.Kiosk.Avalonia.Services.Abstractions;` nếu chưa có (để resolve `AppRoutes`).

## Áp dụng lại (How to reuse)

- Khi port WinForms `Control.Controls.Add(ucFoo)` → Avalonia ContentControl:
  **PHẢI set `ActiveContent = new FooViewModel(...)` trước khi fire event** — ContentControl bind vào object, không tự nạp.
- Khi port `callback.OnSomething(SentinelValue)` dùng enum sentinel:
  **Đọc kỹ tất cả caller** của method đó, xem sentinel nào được dùng và với mục đích gì — không chỉ xem default case.
- `PaymentMethod.None` trong project này = "về trang chủ" (không phải "không có phương thức").

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Build PASS 0 error không phát hiện được 2 bug này — cần test tay đúng luồng.
- ⚠️ `AppRoutes.SelectLanguage` là route "trang chủ" trong IPGS.Kiosk.Avalonia (không phải `"Main"` hay `"Home"`).
- ⚠️ Khi thêm `NavigateTo(AppRoutes.X)` mới, phải kiểm tra `WindowNavigationService` có case `AppRoutes.X` chưa (xem lesson 57).
- ⚠️ WinForms `RegisterUIEvent()` có commentout Cash+Voucher click — parity Avalonia: Cash+Voucher row đặt `IsVisible="False"`.

## Tham chiếu

- Lesson 57: `avalonia/avalonia-navigation-switch-missing-entry-routes.md` (route missing in NavigateTo switch)
- Project: iPGSv4 IPGS.Kiosk.Avalonia, file `ViewModels/Payment/PaymentInfoViewModel.cs`
- WinForms source: `IPGS.Kiosk/LotteDesigns/CarUserControls/ucPaymentInfo.cs` — `GetPaymentInfor()`, `DisplayCompletePayment()`, `UcComplete_onBackClick`
