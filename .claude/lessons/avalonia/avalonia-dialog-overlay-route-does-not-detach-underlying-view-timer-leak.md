---
category: avalonia
tags: [navigation, dialog, countdown, timer, dispatchertimer, kiosk, visa-payment]
severity: medium
created: 2026-07-22
updated: 2026-07-22
project-origin: IPGS.Kiosk.Avalonia (iPGSv4)
---

# Route dialog-overlay (`MotoPaymentComplete`) KHÔNG detach view phía sau → countdown/timer vẫn chạy ngầm sau khi thanh toán xong

## Tình huống gặp phải

> User hỏi: "MotoVisaTransactionIdViewModel cần gọi dừng countdown khi thanh toán xong thì làm
> thế nào?" — khi kiểm tra thấy `ExecutePaymentSuccessAsync()` chỉ set `IsPaymentSuccess = true`
> rồi `_nav.NavigateTo(AppRoutes.MotoPaymentComplete, vehicle)`, KHÔNG có chỗ nào dừng
> `KzRoundCountdown` trên `MotoVisaTransactionIdView`.

## Triệu chứng / Lỗi

```
Thanh toán Visa thành công → dialog "Thanh toán thành công" (MotoPaymentComplete) hiện đè lên.
Countdown (KzRoundCountdown) trên màn phía sau (MotoVisaTransactionIdView) VẪN chạy ngầm.
Nếu dialog hiển thị đủ lâu (≥ PaymentWaitingTime giây) → OnCountdownTick hết giờ tự gọi
GoBackCommand.Execute(null) NGAY CẢ KHI đã thanh toán xong — điều hướng sai/log sai description
"Người Dùng Chọn Hình Thức Thanh Toán Khác" dù thực tế đã thành công.
```

## Nguyên nhân gốc rễ (Root Cause)

`WindowNavigationService.NavigateToCore` (MainWindow.axaml.cs) chặn riêng route
`AppRoutes.MotoPaymentComplete` NGAY ĐẦU HÀM:

```csharp
if (viewKey == AppRoutes.MotoPaymentComplete)
{
    _ = ShowMotoPaymentCompleteDialogAsync(parameter);
    return;   // ← KHÔNG chạm _host.MainContent.Content — view hiện tại KHÔNG bị swap/detach
}
```

Đây là **Window dialog thật** (`ShowDialog` đè lên), không phải swap `MainContent`. Vì vậy
`DetachedFromVisualTree` của `MotoVisaTransactionIdView` (nơi có `StopCountdown()`) **không bao
giờ fire** khi thanh toán thành công — chỉ fire khi user thật sự điều hướng sang màn khác
(swap MainContent, ví dụ GoBack). Countdown/`DispatcherTimer` trong code-behind của view vẫn
sống và tick ngầm phía sau dialog cho tới khi dialog đóng và code gọi tiếp `NavigateTo` khác
(lúc đó MỚI detach).

Đây là biến thể khác của [[avalonia-goback-history-reenters-autonaviate-waiting-screen]] —
cùng gốc "coi mọi route như nhau" nhưng lần này do 1 route được cố tình THIẾT KẾ để không
detach (dialog overlay), khiến lifecycle cleanup (`DetachedFromVisualTree`) không đủ để dừng
hết mọi timer nền.

## Giải pháp

KHÔNG chờ `DetachedFromVisualTree` để dừng countdown khi biết trước sẽ điều hướng sang dialog
overlay. Dừng tường minh ngay khi ViewModel báo thành công, qua `PropertyChanged` (không cần
thêm event mới vì `IsPaymentSuccess` đã là `[ObservableProperty]` sẵn có):

```csharp
// MotoVisaTransactionIdView.axaml.cs — constructor nhận vm
vm.PropertyChanged += (_, e) =>
{
    if (e.PropertyName == nameof(MotoVisaTransactionIdViewModel.IsPaymentSuccess) && vm.IsPaymentSuccess)
        StopCountdown();
};
```

Đặt TRƯỚC `AttachedToVisualTree`/`DetachedFromVisualTree` wiring, cùng vị trí với các subscription
khác trong constructor.

## Áp dụng lại (How to reuse)

- Bất kỳ ViewModel nào navigate sang `AppRoutes.MotoPaymentComplete` (dialog overlay, không
  swap MainContent) mà View của nó có countdown/DispatcherTimer riêng → PHẢI dừng timer đó
  tường minh qua `PropertyChanged` hoặc event, KHÔNG dựa vào `DetachedFromVisualTree`.
- Trước khi thêm `NavigateTo(...)` bất kỳ, tự hỏi: "Route đích này có swap MainContent
  (`_host.MainContent.Content = view`) hay là dialog/overlay (return sớm, không chạm
  MainContent)?" Nếu là overlay → mọi cleanup dựa vào lifecycle attach/detach của view hiện tại
  sẽ KHÔNG chạy.
- **Nghi vấn cần rà soát thêm (cùng pattern, chưa verify):** `MotoQrImageViewModel` — cũng
  navigate `MotoPaymentComplete` sau khi set `IsPaymentSuccess = true` (L310), cũng có
  `KzRoundCountdown` riêng ở `MotoQrImageView` với cấu trúc `StartCountdown/StopCountdown` giống
  hệt — nhiều khả năng dính bug tương tự, cần thêm `PropertyChanged` wiring y hệt.
- Danh sách route dialog-overlay hiện có trong `NavigateToCore`: chỉ `AppRoutes.MotoPaymentComplete`
  tại thời điểm viết lesson này — grep `ShowMotoPaymentCompleteDialogAsync`/comment
  "KHÔNG swap MainContent" trong `MainWindow.axaml.cs` nếu có thêm route dialog mới sau này.

## Chú ý / Cạm bẫy (Gotchas)

- Bug này CHỈ lộ ra khi countdown đủ ngắn hoặc dialog hiển thị đủ lâu — dễ bỏ sót khi test
  nhanh (thanh toán xong, đóng dialog ngay).
- Đừng nhầm với bug GoBack ở lesson `avalonia-goback-history-reenters-autonaviate-waiting-screen.md`
  — bug đó là do `_nav.GoBack()` pop nhầm route waiting-screen; bug này là do route dialog
  overlay không detach view, khiến cleanup lifecycle bị bỏ qua hoàn toàn (không liên quan history
  stack).

## Tham chiếu

- File sửa: `IPGS.Kiosk.Avalonia/Views/Moto/MotoVisaTransactionIdView.axaml.cs` (constructor,
  thêm `vm.PropertyChanged` subscription)
- Liên quan: `IPGS.Kiosk.Avalonia/Views/MainWindow.axaml.cs` (`NavigateToCore`, chặn sớm
  `AppRoutes.MotoPaymentComplete` → `ShowMotoPaymentCompleteDialogAsync`)
- Lesson liên quan: [[avalonia-goback-history-reenters-autonaviate-waiting-screen]]
- Project: iPGSv4 (`IPGS.Kiosk.Avalonia`)
