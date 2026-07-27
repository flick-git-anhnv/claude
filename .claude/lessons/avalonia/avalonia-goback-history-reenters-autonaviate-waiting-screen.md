---
category: avalonia
tags: [navigation, mvvm, goback, history-stack, kiosk, qr-payment, visa-payment]
severity: high
created: 2026-07-22
updated: 2026-07-22
project-origin: IPGS.Kiosk.Avalonia (iPGSv4)
---

# `_nav.GoBack()` (pop history) quay lại "waiting screen" tự động navigate tiếp — nút Back trông như vô tác dụng

## Tình huống gặp phải

> User báo lỗi qua screenshot màn `MotoQrImageView` (hiển thị QR thanh toán xe máy):
> "Bấm back không có tác dụng". Không có exception, không log lỗi.
> Project: `IPGS.Kiosk.Avalonia`, luồng `MotoWaitingQrView → MotoQrImageView`.

## Triệu chứng / Lỗi

```
User bấm nút "Quay lại" trên MotoQrImageView.
Màn hình chớp/nháy rồi quay lại ĐÚNG màn QR y hệt (transaction ID mới, QR mới) —
KHÔNG về màn chọn phương thức thanh toán (MotorPaymentView) như mong đợi.
```

## Nguyên nhân gốc rễ (Root Cause)

`WindowNavigationService` (trong `MainWindow.axaml.cs`) dùng 1 stack `_history` chung cho
MỌI route, push route hiện tại trước khi chuyển route mới (trừ khi route đích == route hiện tại
hoặc route hiện tại là "Main"). `GoBack()` chỉ đơn giản `_history.Pop()` rồi `NavigateToCore(...)`.

Luồng QR có 2 route dây chuyền:
```
MotorBranch → NavigateTo(MotoQrImage)        // = MotoWaitingQrView (tạo giao dịch)
           → (tạo QR xong) NavigateTo(MotoQrImageDisplay)  // = MotoQrImageView (hiển thị QR)
```

Khi `NavigateTo(MotoQrImageDisplay, ...)` được gọi, route trước đó (`"MotoQrImage"`) bị PUSH vào
`_history` (đúng theo logic push chung). Khi user bấm Back trên `MotoQrImageDisplay`, code gọi
`_nav.GoBack()` → pop ra `"MotoQrImage"` → **tạo mới `MotoWaitingQrViewModel` + `MotoWaitingQrView`**.

Nhưng `MotoWaitingQrView.axaml.cs` có:
```csharp
AttachedToVisualTree += async (_, _) => { TryLoadImages(); await vm.InitializeAsync(); };
```
`InitializeAsync()` → `CreateTransactionAsync()` **tự động tạo giao dịch QR MỚI** và tự
`_nav.NavigateTo(AppRoutes.MotoQrImageDisplay, param)` ngay khi thành công — quay lại đúng
màn QR (khác transaction ID) trong tích tắc. User thấy màn hình như "không phản ứng gì".

Đây là hệ quả của việc dùng **1 history stack chung, generic cho mọi route** — nó coi
"waiting/transition screen" (screen tự động navigate tiếp khi attach) giống hệt "screen thường",
trong khi push nó vào history rồi pop lại là vô nghĩa (không có UI thật để quay về).

## Giải pháp

KHÔNG dùng `_nav.GoBack()` cho các case có "waiting/transition screen" ở giữa. Thay bằng
**event `BackRequested` trên ViewModel** (đã có sẵn pattern này ở `MotoCashViewModel` /
`MotoVoucherViewModel`) để `MainWindow` điều hướng THẲNG về đích đúng (ví dụ `MotorBranch`),
bỏ qua hoàn toàn history stack:

```csharp
// ViewModel — thay _nav.GoBack() bằng raise event
public event EventHandler? BackRequested;
...
BackRequested?.Invoke(this, EventArgs.Empty);

// MainWindow.axaml.cs — wire tại nơi tạo ViewModel, navigate thẳng, không qua _history
vmQI.BackRequested += (_, _) => NavigateTo(AppRoutes.MotorBranch, new MotoPaymentVehicleDto { ... });
```

## Áp dụng lại (How to reuse)

- **Bất kỳ route nào tự động `NavigateTo` tiếp khi `AttachedToVisualTree` (waiting/spinner/loading
  screen)** → KHÔNG BAO GIỜ để nó là target của `_nav.GoBack()`. Luôn dùng event `BackRequested`
  + wiring trực tiếp ở `MainWindow` map sang đích đúng.
- Trước khi dùng `_nav.GoBack()` ở bất kỳ ViewModel nào, tự hỏi: "Route ngay trước route hiện tại
  trong luồng nghiệp vụ này có phải screen tạm/tự-động-chuyển-tiếp không?" Nếu có → GoBack() sẽ sai.
- Danh sách nghi vấn cần rà soát thêm trong cùng codebase (cùng pattern waiting→display):
  `frmCarQr`/`CarQrView` nếu có waiting screen tương ứng.
- ✅ **XÁC NHẬN (2026-07-22):** `MotoWaitingVisaView → MotoVisaTransactionIdView` ĐÚNG là bị bug này —
  `MotoVisaTransactionIdViewModel.GoBack()` gọi thẳng `_nav.GoBack()`, pop lại route
  `"MotoVisaTransactionId"` (= `MotoWaitingVisaView`), attach lại tự tạo giao dịch Visa MỚI rồi
  tự `NavigateTo(MotoVisaTransactionIdDisplay,...)` — y hệt case QR. Fix: đổi
  `_nav.GoBack()` → `_nav.NavigateTo(AppRoutes.MotorBranch, _param.Vehicle)` (navigate thẳng, bỏ
  qua history) — KHÔNG dùng pattern event `BackRequested` như case QR vì ViewModel này đã tự giữ
  `INavigationService _nav` sẵn (không cần MainWindow wiring hộ) — 2 cách tương đương về hiệu quả,
  chọn cách nào ít thay đổi code hơn tùy ViewModel đã có `_nav` trực tiếp hay chỉ có qua constructor
  của MainWindow.
- Đối chiếu WinForms gốc: `frmMotoQrImage` là **Form con `.Show(this)` lồng trên `frmMotoWaitingQr`**
  (không phải route thay thế) — back chỉ `this.Close()` rồi bubble `onBackClickEvent` để
  `frmMotoWaitingQr` cũng tự đóng theo. Avalonia port thay Form-lồng-Form bằng route stack phẳng
  (ContentControl swap) — đây là chỗ parity dễ vỡ nhất khi thay đổi mental model điều hướng.

## Chú ý / Cạm bẫy (Gotchas)

- Bug này KHÔNG throw exception, KHÔNG log lỗi rõ ràng — chỉ phát hiện được qua quan sát UI
  (screenshot/video) hoặc đọc kỹ side-effect của ViewModel được pop ra từ history.
- `_isGoBackCalled` guard trong `MotoQrImageViewModel` không liên quan đến bug này (chỉ ngừa
  double-click) — dễ nhầm là nguyên nhân khi debug.

## Tham chiếu

- File sửa: `IPGS.Kiosk.Avalonia/ViewModels/Moto/MotoQrImageViewModel.cs` (thêm `BackRequested`),
  `IPGS.Kiosk.Avalonia/Views/MainWindow.axaml.cs` (wire tại case `AppRoutes.MotoQrImageDisplay`)
- File sửa (case Visa, 2026-07-22): `IPGS.Kiosk.Avalonia/ViewModels/Moto/MotoVisaTransactionIdViewModel.cs`
  method `GoBack()` — đổi `_nav.GoBack()` → `_nav.NavigateTo(AppRoutes.MotorBranch, _param.Vehicle)`
- Đối chiếu bug gốc: `IPGS.Kiosk/LotteDesigns/BikeUserControls/QrUC/frmMotoWaitingQr.cs` +
  `frmMotoQrImage.cs` (Form-lồng-Form + `onBackClickEvent`)
- Pattern event `BackRequested` tham khảo: `MotoCashViewModel.cs`, `MotoVoucherViewModel.cs`
- Project: iPGSv4 (`IPGS.Kiosk.Avalonia`)
