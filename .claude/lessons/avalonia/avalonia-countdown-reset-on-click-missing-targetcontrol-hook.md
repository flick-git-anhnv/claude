---
category: avalonia
tags: [countdown, auto-return, dispatchertimer, migration, winforms-parity, event-routing]
severity: high
created: 2026-07-21
updated: 2026-07-21
project-origin: iPGSv4 (migrate-ipgs-kiosk-avalonia)
---

# Countdown auto-return không reset khi user click — thiếu port `KzRoundCountdown.TargetControl`

## Tình huống gặp phải

Migrate `IPGS.Kiosk` (WinForms) → `IPGS.Kiosk.Avalonia`. Nhiều màn hình (CarInforDetail,
MotorInforDetail, LocateVehicle, MotoPaymentComplete, BikePaymentResult, CarVehicleResult,
MotorVehicleResult, Invoice, MotoVoucher) có countdown auto-return-về-Main sau N giây không thao tác.

## Triệu chứng / Lỗi

User bấm vào item/control trên màn hình (thao tác thật, không phải đứng yên) nhưng countdown vẫn
tiếp tục đếm lùi bình thường — không reset lại về giá trị ban đầu. Sau khi hết giờ, app tự động
quay về Main dù người dùng đang thao tác dở, gây trải nghiệm rất khó chịu (kiosk tự "đá" người dùng
ra giữa lúc đang nhập liệu/xem thông tin).

## Nguyên nhân gốc rễ (Root Cause)

Bản gốc dùng `KztekComponent.Controls.KzRoundCountdown` (custom control WinForms) với property
`TargetControl`: setter của property này **hook đệ quy `MouseDown` lên chính Form VÀ TOÀN BỘ
control con** (kể cả control thêm động sau này qua `ControlAdded` event), gọi `Reset()+Start()`
mỗi khi bắt được sự kiện — nghĩa là bất kỳ click nào ở bất kỳ đâu trên form đều tự động gia hạn
countdown, hoàn toàn transparent với code gọi (chỉ cần gán `kzRoundCountdown.TargetControl = this;`
một lần).

Khi port sang Avalonia, KHÔNG có sẵn control `KzRoundCountdown` trong `ParkingV8.UI` (thư viện
Avalonia dùng chung) — mỗi ViewModel/View tự viết `DispatcherTimer` đếm ngược thủ công, nhưng
**không ai port lại cơ chế "hook mọi click để reset"**. Countdown vẫn hoạt động đúng về mặt đếm lùi
và auto-return, nhưng hoàn toàn "điếc" với tương tác người dùng — bug này không lộ ra khi build/test
nhanh (không lỗi biên dịch, không exception), chỉ phát hiện khi thao tác tay đủ lâu để countdown
chạy hết trong lúc đang dùng màn hình.

## Giải pháp

1. Tạo interface dùng chung `IResettableCountdown { void ResetCountdown(); }`
   (`Services/Abstractions/IResettableCountdown.cs`).
2. Mọi ViewModel/View có `DispatcherTimer` đếm ngược auto-return → implement interface này, expose
   `public void ResetCountdown()` (đổi từ `private` nếu đã có sẵn, hoặc thêm mới) set lại
   `_countdownRemaining = AppState.NormalWaitingTime` (hoặc `PaymentWaitingTime` tuỳ màn).
3. Tại `MainWindow` (shell chứa `ContentControl` swap toàn bộ màn hình) — bắt `PointerPressed` ở
   tầng **Tunnel** (chạy trước khi control con xử lý, không bị chặn bởi `e.Handled` ở tầng Bubble):

```csharp
AddHandler(InputElement.PointerPressedEvent, OnAnyPointerPressed, RoutingStrategies.Tunnel);

private void OnAnyPointerPressed(object? sender, PointerPressedEventArgs e)
{
    var content = MainContent.Content;
    if (content is IResettableCountdown selfReset) selfReset.ResetCountdown();
    if (content is Control { DataContext: IResettableCountdown vmReset }) vmReset.ResetCountdown();
}
```

4. Chỉ cần wire 1 chỗ duy nhất (MainWindow) — không cần sửa từng View con, vì `ContentControl`
   luôn chứa View hiện tại và `PointerPressed` Tunnel bubble xuyên suốt toàn bộ visual tree con.

## Áp dụng lại (How to reuse)

- Khi port bất kỳ WinForms custom control nào có property dạng `TargetControl`/`AttachTo` — PHẢI
  đọc kỹ implementation của property đó (không chỉ API bề mặt), vì rất có thể nó ẩn chứa side-effect
  quan trọng (hook event đệ quy, auto-wiring) mà nếu chỉ port "giao diện" (Duration, hiển thị số)
  sẽ bỏ sót hoàn toàn.
- Pattern "1 global handler tại Shell/MainWindow + interface đánh dấu" áp dụng được cho MỌI hành vi
  cross-cutting cần áp dụng đồng loạt cho nhiều View (không chỉ countdown) — tránh phải sửa lặp lại
  từng View.
- Dùng `RoutingStrategies.Tunnel` (không phải Bubble) khi cần đảm bảo handler LUÔN chạy bất kể
  control con có gọi `e.Handled = true` hay không.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ 2 ViewModel (`LocateVehicleViewModel`, `MotorVehicleResultViewModel`) đã có sẵn method tên
  đúng `ResetCountdown()` nhưng là `private`, chỉ gọi nội bộ ở vài điểm nghiệp vụ cụ thể (search
  thành công, phím bấm) — dễ nhầm tưởng "đã có reset-on-interaction" trong khi thực ra chưa cover
  trường hợp click chung chung. Phải kiểm tra TOÀN BỘ call site, không chỉ tên method trùng khớp.
- ⚠️ Countdown implement ở code-behind (View, VD `InvoiceView`, `MotoVoucherView`) chứ không phải
  ViewModel — interface phải áp lên đúng class chứa `DispatcherTimer` thật (View hoặc ViewModel tuỳ
  từng màn), kiểm tra cả `MainContent.Content` (View) lẫn `.DataContext` (ViewModel) trong handler.

## Tham chiếu

- `KztekComponent/Controls/KzRoundCountdown.cs` (dòng 107-118, 200-225) — cơ chế `TargetControl`
  hook `MouseDown` đệ quy gốc.
- `IPGS.Kiosk.Avalonia/Services/Abstractions/IResettableCountdown.cs`,
  `IPGS.Kiosk.Avalonia/Views/MainWindow.axaml.cs` — bản fix.
- Project liên quan: iPGSv4 (migrate-ipgs-kiosk-avalonia)
