---
category: camera-integration
tags: [suprema, bs2-sdk, facestation-f2, biometric, concurrency, static-field, multi-device]
severity: critical
created: 2026-08-25
updated: 2026-08-25
project-origin: iAccess Desktop v2 (App-Access-V2)
---

# SDK native context dùng chung nhiều thiết bị: static field ĐÚNG, nhưng phải static luôn cả gate đồng bộ — không chỉ static field

## Tình huống gặp phải

> `FSF2Controller` (P/Invoke BS_SDK_V2, Suprema FaceStation F2) — mỗi thiết bị Suprema trong hệ thống có
> 1 instance `FSF2Controller` riêng (factory tạo N instance cho N thiết bị), mỗi instance có 1
> `CheckConnectLoop` polling nền độc lập (Task riêng, 1 giây/lần). Field `_context` (con trỏ SDK context,
> `void* BS2_AllocateContext()`) ban đầu là `static`.

## Triệu chứng / Lỗi

- **Để `_context` static** (chỉ static field, KHÔNG có gate đồng bộ toàn cục — `_sdkGate` là
  `SemaphoreSlim` INSTANCE, chỉ serialize lệnh trong CHÍNH 1 thiết bị): app chạy được một lúc rồi crash
  (`0xe0434352` — unhandled CLR exception, KHÔNG phải access violation native trực tiếp). Task Manager
  trên máy khách cho thấy process "Not Responding" + "Working set delta" nhảy thất thường (có lúc âm).
- **Đổi `_context` thành INSTANCE field** (mỗi thiết bị tự `AllocateContext()` riêng, tưởng đây là fix
  đúng vì official SDK example (`UnitTest.cs`) khai báo `sdkContext` là instance field) — hết crash native
  nhưng lại phát sinh **lỗi UI khác** trên máy khách (nghi cạn USER/GDI handle do N thiết bị × chu kỳ
  reconnect nhân số lượng handle native lên, giống pattern ở
  `avalonia/avalonia-itemscontrol-array-churn-camera-handle-leak.md` với SDK camera khác).

## Nguyên nhân gốc rễ (Root Cause)

Hai lỗi ĐỘC LẬP bị nhầm là 1:

1. **Static field không sai về BẢN CHẤT** — SDK Suprema example thật (`UnitTest.cs`, có
   `deviceIDQueue`/`ReconnectionTask` quản lý NHIỀU thiết bị qua 1 `sdkContext` — dù field đó là instance
   trong class demo, ý tưởng thiết kế là **1 context phục vụ N thiết bị**, KHÔNG PHẢI 1 context/thiết bị).
   Đổi sang instance-per-device đi ngược thiết kế này → nhân số context/handle theo số thiết bị, đúng là
   nguyên nhân "lỗi UI" (cạn handle) khi có nhiều thiết bị.
2. **Cái thực sự thiếu là ĐỒNG BỘ CHÉO GIỮA CÁC INSTANCE**, không phải việc field static hay không. Kiến
   trúc `FSF2Controller` (khác demo gốc) cho MỖI thiết bị 1 `CheckConnectLoop` Task ĐỘC LẬP — nếu gate
   đồng bộ (`_sdkGate`) là INSTANCE field, 2 thiết bị vẫn gọi API SDK ĐỒNG THỜI trên CÙNG context static
   mà không ai chờ ai → race + 1 thiết bị dispose có thể giải phóng context thiết bị khác đang dùng
   (use-after-free).

## Giải pháp

**Cả 2 field phải cùng static — không phải chỉ `_context`:**

```csharp
private static IntPtr _context = IntPtr.Zero;                    // 1 context cho toàn app
private static readonly SemaphoreSlim _sdkGate = new(1, 1);       // serialize MỌI lệnh SDK của MỌI thiết bị
private static int _instanceRefCount = 0;                          // chỉ ReleaseContext khi về 0

public FSF2Controller(...) { ...; Interlocked.Increment(ref _instanceRefCount); }

public async ValueTask DisposeAsync()
{
    ...
    await _sdkGate.WaitAsync();
    try
    {
        if (_context != IntPtr.Zero && _deviceId != 0)
        { API.BS2_StopMonitoringLog(_context, _deviceId); API.BS2_DisconnectDevice(_context, _deviceId); } // theo deviceId — an toàn dù context chung
        int remaining = Interlocked.Decrement(ref _instanceRefCount);
        if (remaining <= 0 && _context != IntPtr.Zero) { API.BS2_ReleaseContext(_context); _context = IntPtr.Zero; }
    }
    finally { _sdkGate.Release(); }
}
```

Đánh đổi: N thiết bị không còn xử lý SDK song song (mỗi lệnh phải chờ lượt) — nhưng đây đúng là cách SDK
thật hỗ trợ multi-device (1 context, xử lý tuần tự); polling 1s/thiết bị vẫn đủ nhanh để không tồn đọng.

## Áp dụng lại (How to reuse)

- Khi 1 SDK native (context/handle) được thiết kế để DÙNG CHUNG cho nhiều thiết bị/kết nối: nếu field
  đó là `static`, MỌI cơ chế đồng bộ bảo vệ nó (lock/semaphore) và MỌI logic giải phóng (`Release`/
  `Dispose`) đều PHẢI cũng static/reference-counted theo đúng phạm vi chia sẻ — không được để field
  chia sẻ (static) nhưng gate bảo vệ lại instance-scoped (per-object). Đây là NGUỒN GỐC thật của bug,
  không phải việc chọn static hay instance.
- Trước khi đổi 1 field static → instance (hoặc ngược lại) vì lý do concurrency, kiểm tra xem field đó
  đại diện cho TÀI NGUYÊN GÌ (context/handle SDK dùng chung hay state riêng từng thiết bị) — đối chiếu
  với ví dụ CHÍNH THỨC của SDK (không chỉ nhìn field đó là `static` hay không trong ví dụ, mà nhìn Ý
  TƯỞNG THIẾT KẾ: 1 context quản lý N thiết bị hay N context độc lập).
- 2 loại lỗi này có triệu chứng HOÀN TOÀN KHÁC NHAU và dễ nhầm là "sửa cái này lại sinh cái khác nên
  revert": crash native/exception đột ngột (race/use-after-free) ≠ lỗi UI/cạn handle dần theo thời gian
  (resource leak nhân theo số instance). Đừng vội revert khi thấy 1 loại lỗi mất đi nhưng loại khác xuất
  hiện — đó là dấu hiệu ĐANG SỬA ĐÚNG HƯỚNG nhưng CHƯA ĐỦ (thiếu đồng bộ chéo), không phải sai hướng.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ `SemaphoreSlim` không reentrant — nếu đổi gate từ instance sang static, kiểm tra lại MỌI call site
  gọi lồng nhau (VD `CheckConnectLoop` gọi `ConnectCore()` thẳng, không qua `ConnectAsync()` public, để
  tránh tự deadlock khi đã giữ gate).
- ⚠️ `BS2_DisconnectDevice`/`BS2_StopMonitoringLog` nhận `deviceId` riêng từng thiết bị — vẫn AN TOÀN gọi
  dù `context` dùng chung; chỉ riêng `BS2_ReleaseContext(context)` mới ảnh hưởng TẤT CẢ thiết bị, cần
  reference-count.
- ⚠️ Exception code `0xe0434352` trong Windows Event Viewer là **unhandled .NET CLR exception** (managed),
  KHÔNG phải access violation native (`0xc0000005`) — dù nguyên nhân gốc có thể vẫn là native (context bị
  free sớm khiến 1 lệnh SDK trả về dữ liệu/handle không hợp lệ, code managed đọc nó ném
  NullReferenceException/ObjectDisposedException rồi crash cả process vì exception nằm trong
  Task nền không được try/catch bao ngoài).

## Tham chiếu

- Project liên quan: iAccess Desktop v2 (`App-Access-V2`), branch `fix/suprema-sdk-audit-2026-08-25`
- SDK thật: `H:\Hardware\26.Suprema\BioStarDeviceSDK_2.9.12.0_20260306\Example\cli\csharp\common\UnitTest.cs`
- File production: `iAccessDesktopv2.Avalonia/iAccess.Devices.Suprema/FSF2Controller.cs`
- Lesson liên quan (case tương tự với SDK khác): [[avalonia-itemscontrol-array-churn-camera-handle-leak]]
