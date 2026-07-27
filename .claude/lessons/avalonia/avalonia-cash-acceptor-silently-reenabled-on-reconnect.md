---
category: avalonia
tags: [cash-device, cba9, ssp, fire-and-forget, command-queue, reconnect, silent-state-override]
severity: high
created: 2026-07-24
updated: 2026-07-24
project-origin: iPGSv4 (IPGS.Kiosk.Avalonia)
---

# DisableAcceptor() "không có tác dụng" — driver tự re-enable acceptor sau mỗi (re)connect

## Tình huống gặp phải

Kiosk gọi `KioskServices.CashDevice.Connect()` rồi `DisableAcceptor()` ngay lúc startup (`MainViewModel.OnLoadedAsync`) để giữ máy nhận tiền ở trạng thái "không nhận" khi đang màn idle — chỉ `EnableAcceptor()` khi user thực sự vào màn Cash thanh toán. Cả 2 lệnh implement bằng `CashDeviceServiceImpl` (IPGS.Kiosk.Avalonia) bọc `CBA9ControllersV3` (thư viện ngoài `ParkingV8.Cash`, project khác: `parking-v8-app-avalonia`).

## Triệu chứng / Lỗi

User báo: acceptor thỉnh thoảng vẫn nhận tiền dù đã gọi `DisableAcceptor()` — nghi ngờ ban đầu là do `Connect()`/`DisableAcceptor()` dùng pattern fire-and-forget (`_ = ...Task`) nên "không có tác dụng". Bug không tái hiện ổn định (lúc có lúc không), khó debug.

## Nguyên nhân gốc rễ (Root Cause)

Pattern `_ = _cba9.Connect()` / `_ = _cba9.DisableValidator()` **không phải nguyên nhân** — cả hai được enqueue vào 1 command-queue FIFO single-consumer (`CBA9ControllersV3._queue` + `WorkerLoopAsync`), nên thứ tự Connect → Disable luôn được đảm bảo đúng khi gọi tuần tự trên cùng thread.

Có **2 nguyên nhân xếp chồng**, phải sửa cả hai mới hết bug (chỉ sửa 1 vẫn còn "không có tác dụng"):

1. **Auto re-enable liên tục mỗi chu kỳ poll (~100ms) — nguyên nhân chính, gây "never sticks":**
   Trong `DoPollOnceCore_FullSwitchAsOld()`, có đoạn kiểm tra thô theo string:
   ```csharp
   if (b.Contains("E8") && !IsStopGetEvent)
       EnableValidator();
   ```
   `0xE8` = `SSP_POLL_DISABLED` (`SspProtocolCommands.cs:127`) — tức CHÍNH byte trạng thái mà thiết bị trả về khi nó đang **đúng như app vừa yêu cầu** (disabled). Code lại diễn giải "thấy DISABLED → tự bật lại", nên chạy mỗi 100ms trong lúc polling — `DisableAcceptor()` không bao giờ giữ được quá 1 chu kỳ poll, không cần chờ reconnect gì cả.

2. **Auto-enable ở cuối mọi lần (re)connect — gây tái phát sau khi đã fix (1):**
   `TryConnectCore()` (bên trong `Connect()`/`EnsureConnectedAsync()`) luôn gọi `EnableValidatorCore()` ở bước cuối cùng của MỌI lần connect thành công — kể cả auto-reconnect ngầm khi `WorkerLoopAsync` phát hiện mất kết nối thoáng qua (nhiễu serial...). Sự kiện này chỉ báo qua `ConnectionStatusEvent(isConnected=true)`, không tự nhớ ý định "disabled" trước đó của app.

## Giải pháp

Ban đầu chỉ sửa ở wrapper (`CashDeviceServiceImpl.cs`) tưởng đã đủ (chặn nguyên nhân #2 — reconnect), nhưng user xác nhận "vẫn chưa disable được" → phải sửa **tận gốc trong `CBA9ControllersV3.cs` (ParkingV8.Cash)**, vì nguyên nhân #1 (auto-enable mỗi chu kỳ poll) nằm hẳn bên trong thư viện, wrapper không can thiệp được (nó chạy trước khi `PollEvent` được raise ra ngoài).

**Fix #1 — trong `CBA9ControllersV3.cs` (ParkingV8.Cash, sửa tận gốc, ảnh hưởng mọi consumer dùng chung thư viện):**

```csharp
// Ý định mới nhất của caller — không phải trạng thái thiết bị báo về qua poll.
private volatile bool _acceptorShouldBeEnabled = true;   // default true = giữ hành vi lịch sử

private bool EnableValidatorCore()
{
    _acceptorShouldBeEnabled = true;
    ...
}

private bool DisableValidatorCore()
{
    _acceptorShouldBeEnabled = false;
    ...
}

// Trong DoPollOnceCore_FullSwitchAsOld():
if (b.Contains("E8") && !IsStopGetEvent && _acceptorShouldBeEnabled)   // + guard ý định
    EnableValidator();
```

Chỉ tự re-enable khi caller THỰC SỰ muốn acceptor đang bật (self-heal sau lỗi phần cứng/reset ngoài ý muốn) — nếu caller vừa chủ động Disable, tôn trọng ý định đó, không tự bật lại chỉ vì poll thấy response DISABLED (đúng như mong đợi).

**Fix #2 — trong `CashDeviceServiceImpl.cs` (wrapper, project của mình):**

```csharp
private volatile bool _acceptorShouldBeEnabled;

public bool EnableAcceptor()  { _acceptorShouldBeEnabled = true;  _ = _cba9.EnableValidator();  return true; }
public bool DisableAcceptor() { _acceptorShouldBeEnabled = false; _ = _cba9.DisableValidator(); return true; }

private void OnConnectionStatus(object sender, bool isConnected)
{
    _isConnected = isConnected;
    if (isConnected)
    {
        // Tái áp đặt lại đúng ý định gần nhất — vô hiệu hoá auto-enable ngầm
        // của TryConnectCore() (STEP10) sau MỌI lần (re)connect.
        if (_acceptorShouldBeEnabled) _ = _cba9.EnableValidator();
        else                          _ = _cba9.DisableValidator();
    }
}
```

1. Sửa thư viện (Fix #1) trước — đây là nguyên nhân chính, liên tục.
2. Sửa wrapper (Fix #2) — phòng vệ thêm cho trường hợp reconnect (TryConnectCore STEP10 vẫn luôn auto-enable ở cuối mỗi connect, kể cả sau khi có Fix #1).
3. Build cả 2 project (`ParkingV8.Cash.csproj` rồi `IPGS.Kiosk.Avalonia.csproj`) — verify không đổi public interface (`ICashController`/`ICashDeviceService`), không cần cập nhật CODE-GRAPH vì chỉ sửa logic nội bộ.
4. **Vì sửa thư viện dùng chung** — cần build/smoke-test lại các app khác cũng tham chiếu `ParkingV8.Cash` trước khi coi là xong hoàn toàn (ngoài phạm vi 1 lần fix này).

## Áp dụng lại (How to reuse)

- Khi thấy 1 lệnh điều khiển thiết bị (enable/disable/mode...) "thỉnh thoảng/liên tục không có tác dụng" → nghi ngờ **driver tự diễn giải sai chính response mà nó vừa nhận và tự đảo ngược lại lệnh** (ví dụ: thấy trạng thái DISABLED trong response → tưởng là lỗi → tự enable lại). Grep các callback xử lý poll/response cho các từ khoá kiểu "auto", "retry", "self-heal", hoặc so sánh string thô như `Contains("E8")` — đây là dấu hiệu logic tự-sửa-lỗi không phân biệt được "lỗi thật" với "đúng ý người dùng".
- Nếu sau khi sửa 1 chỗ mà user báo "vẫn chưa được" → đừng vội nghi ngờ fix sai, mà **tìm nguyên nhân thứ 2 xếp chồng** hoạt động ở tần suất khác (ví dụ: 1 nguyên nhân theo sự kiện reconnect hiếm khi xảy ra, 1 nguyên nhân lặp lại mỗi poll cycle 100ms — cái sau sẽ che lấp hoàn toàn hiệu quả của việc sửa cái trước).
- Với mọi thiết bị có cơ chế auto-reconnect: bất kỳ state nào app set qua API (enable/disable, mode, threshold...) PHẢI được tái áp đặt lại trong handler `ConnectionStatusEvent`/`OnReconnected`, không giả định driver tự nhớ giúp.
- Đừng vội kết luận `_ = someTask()` (fire-and-forget) là nguyên nhân gây "no effect" nếu nó ghi vào 1 command-queue FIFO single-consumer — thứ tự vẫn đúng miễn 2 lệnh được enqueue tuần tự trên cùng thread. Phải trace tiếp vào code triển khai queue/worker trước khi kết luận.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ `CBA9ControllersV3` nằm ở project khác (`ParkingV8.Cash`, repo `parking-v8-app-avalonia`) — sửa tận gốc ở đây ảnh hưởng MỌI app dùng chung thư viện (không chỉ `iPGSv4`). Đã hỏi + được user xác nhận trước khi sửa (recommended option, không phải workaround). Cần build/smoke-test lại các app kiosk khác tham chiếu `ParkingV8.Cash` sau khi merge.
- ⚠️ Field ý định (`_acceptorShouldBeEnabled` trong wrapper) phải default an toàn (`false` = không nhận tiền) để tránh trạng thái ban đầu vô tình cho phép nhận tiền trước khi app kịp gọi `DisableAcceptor()` lần đầu. Field cùng tên trong `CBA9ControllersV3` default `true` để giữ đúng hành vi lịch sử (SDK tự enable ngay sau `Connect()`) — 2 field khác tầng, không dùng chung giá trị default.
- ⚠️ Guard `_acceptorShouldBeEnabled` trong switch-case poll chỉ chặn auto-enable theo nhánh "E8-string-check" — `TryConnectCore()` STEP10 vẫn luôn gọi `EnableValidatorCore()` ở cuối MỌI lần connect (kể cả reconnect), nên vẫn cần Fix #2 (wrapper tái áp đặt qua `ConnectionStatusEvent`) — thiếu 1 trong 2 fix thì bug tái phát theo đường khác.

## Tham chiếu

- File wrapper: `IPGS.Kiosk.Avalonia/Services/Implementations/CashDeviceServiceImpl.cs` (project `iPGSv4`)
- File thư viện (sửa tận gốc): `E:\KZTEK\Code_Git\1.Window\1.IPARKING\v8\6.Avalonia\parking-v8-app-avalonia\src\ParkingV8.Cash\Controllers\CBA9ControllersV3.cs` — `DoPollOnceCore_FullSwitchAsOld()` (đoạn check `Contains("E8")`), `EnableValidatorCore()`/`DisableValidatorCore()`, `TryConnectCore()` (dòng ~259 gọi `EnableValidatorCore()` ở STEP10), `WorkerLoopAsync()` (dòng ~1211 tự gọi lại `EnsureConnectedAsync()`)
- SSP constant xác nhận: `SspProtocolCommands.cs:127` — `SSP_POLL_DISABLED = 0xE8`
- Lesson liên quan: `avalonia-cash-acceptor-reused-cashresult-stale-flag.md`, `avalonia-cash-device-disconnect-shared-singleton-grey-icon.md`
- Project: `iPGSv4` (IPGS.Kiosk.Avalonia) + `parking-v8-app-avalonia` (ParkingV8.Cash, thư viện dùng chung)
