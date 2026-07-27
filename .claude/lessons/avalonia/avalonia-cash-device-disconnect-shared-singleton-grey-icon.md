---
category: avalonia
tags: [cash-device, singleton, shared-resource, icon-status, lifecycle]
severity: high
created: 2026-07-23
updated: 2026-07-23
project-origin: IPGS.Kiosk.Avalonia
---

# `CleanUp()` gọi `CashDevice.Disconnect()` → icon Cash xám vĩnh viễn sau giao dịch

## Tình huống gặp phải

> Đang debug: icon trạng thái "Cash" ở `MainView` hiện xanh đúng khi app khởi động,
> nhưng sau khi user thanh toán tiền mặt xong và quay về `MainView`, icon chuyển XÁM vĩnh viễn
> dù thiết bị vật lý vẫn cắm và hoạt động bình thường.

Project: `IPGS.Kiosk.Avalonia` — Kiosk thanh toán xe máy/ô tô.

## Triệu chứng / Lỗi

```
Icon Cash trên MainView xanh → sau thanh toán tiền mặt → xám, không phục hồi.
Không có exception, không có log lỗi. Thiết bị vật lý vẫn kết nối.
```

`ICashDeviceService.IsConnected` trả về `false` sau khi thanh toán xong, dù
dây vẫn cắm và `CashDeviceServiceImpl` chưa bao giờ mất kết nối thật sự.

## Nguyên nhân gốc rễ (Root Cause)

`MotoCashViewModel.CleanUp()` và `CarCashViewModel.CleanUp()` đều gọi
`KioskServices.CashDevice.Disconnect()` khi kết thúc phiên giao dịch.

`CashDeviceServiceImpl.Disconnect()` set `_isConnected = false` vô điều kiện
(đồng thời dừng polling loop và unsubscribe `PollEvent`).

`MainViewModel` là **singleton** (được cache ở `WindowNavigationService`, không recreate
khi quay về Main). `OnLoadedAsync()` có guard `if (IsLoaded) return` — chỉ gọi
`CashDevice.Connect()` MỘT LẦN duy nhất lúc app start.

Kết quả:
1. `MotoCashViewModel.CleanUp()` gọi `Disconnect()` → `_isConnected = false`
2. `MainViewModel` không bao giờ gọi lại `Connect()` → icon đọc `IsConnected` → xám mãi

Đây là anti-pattern điển hình: **ViewModel thoáng (transient) cầm giữ và đóng
tài nguyên chia sẻ cấp ứng dụng (shared singleton)**.

## Giải pháp

Xóa lời gọi `KioskServices.CashDevice.Disconnect()` khỏi `CleanUp()` của cả hai ViewModel.
Chỉ unsubscribe event là đủ.

```csharp
// MotoCashViewModel.CleanUp() — TRƯỚC (sai)
KioskServices.CashDevice.BillReceived -= OnBillReceived;
KioskServices.CashDevice.DeviceError  -= OnDeviceError;
KioskServices.CashDevice.Disconnect();   // ← BUG: đóng tài nguyên dùng chung

// SAU (đúng)
KioskServices.CashDevice.BillReceived -= OnBillReceived;
KioskServices.CashDevice.DeviceError  -= OnDeviceError;
// Không gọi Disconnect() — CashDevice là singleton dùng chung toàn app
```

Cùng fix áp dụng cho `CarCashViewModel.CleanUp()`.

**Tại sao an toàn không gọi Disconnect():**
- Sau khi unsubscribe `BillReceived`/`DeviceError`, polling loop tiếp tục chạy nhưng
  event fire vào null (`BillReceived?.Invoke(...)` — null-checked → safe).
- Khi user vào màn Cash lần sau, constructor gọi `Connect()` → guard
  `if (_isConnected) return true` → không double-subscribe PollEvent.
- `EnableAcceptor()` trong constructor kích hoạt lại máy đúng lúc cần.

## Áp dụng lại (How to reuse)

- Khi thấy icon trạng thái thiết bị xám sau khi dùng xong màn hình thanh toán → kiểm tra
  `CleanUp()`/`Dispose()` của ViewModel có gọi `Disconnect()` / `Close()` / `Stop()` trên
  service dùng chung không.
- Trước khi viết `Disconnect()` trong `CleanUp()`: hỏi "service này có phải singleton
  toàn app không, hay chỉ của màn hình này?" Nếu là singleton → chỉ unsubscribe event,
  không đóng kết nối.
- Tài nguyên cấp APP (như CashDevice, RabbitMQ, SocketServer, SQL Connection Pool) chỉ
  được teardown thật sự khi app sắp restart/shutdown — KHÔNG teardown khi rời 1 màn hình.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ `ICashDeviceService` không có `DisableAcceptor()` — không có cách "tạm dừng nhận tiền"
  mà không đóng kết nối. Giải pháp đúng là không cần tạm dừng: polling loop "idle" hoàn toàn
  safe khi không có subscriber.
- ⚠️ Bug này KHÔNG sinh exception, không sinh warning build. Chỉ lộ qua UI (icon màu sắc)
  và phải test flow đầy đủ (thanh toán xong → quay về Main → quan sát icon).
- ⚠️ Pattern này dễ tái phát khi thêm ViewModel mới xử lý CashDevice: lập trình viên có xu
  hướng "đối xứng" — Connect() khi vào, Disconnect() khi ra — nhưng đối xứng sai khi tài nguyên
  là shared singleton.

## Tham chiếu

- `CashDeviceServiceImpl.Connect()` — có guard `if (_isConnected) return true` (an toàn gọi lại)
- `CashDeviceServiceImpl.Disconnect()` — dừng polling + `_isConnected = false` (không gọi khi rời màn hình)
- `MainViewModel.OnLoadedAsync()` — chỉ chạy 1 lần (guard `IsLoaded`), là nơi duy nhất gọi `Connect()` ban đầu
- Lesson liên quan: `avalonia-navigation-recreated-vm-reconnects-infra-every-visit.md` (singleton ViewModel cache pattern)
- Project: `IPGS.Kiosk.Avalonia` — branch `PAYMENT_KIOSK_VERTICAL`
