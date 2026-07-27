---
category: avalonia
tags: [cash-acceptor, cba9, ssp-protocol, migration-parity, stateful-driver, event-dedup]
severity: critical
created: 2026-07-22
updated: 2026-07-22
project-origin: iPGSv4 (IPGS.Kiosk.Avalonia — CashDeviceServiceImpl)
---

# Driver máy nhận tiền (CBA9/SSP) reuse 1 object CashResult xuyên suốt phiên poll — consumer PHẢI tự reset cờ sau mỗi tờ tiền, nếu không tờ tiền thứ 2 trở đi sẽ không bao giờ có event

## Tình huống gặp phải

Migrate cash acceptor service từ WinForms (`IPGS.Cash.Controllers.CBA9Controllers`, dùng trong `ucCarCash.cs`/`frmMotoCash.cs`) sang cross-platform `ParkingV8.Cash.Controllers.CBA9ControllersV3` cho Avalonia (`CashDeviceServiceImpl.cs`). Test thực tế trên máy nhận tiền: chỉ nhận được sự kiện `BillReceived` của tờ tiền ĐẦU TIÊN, các tờ tiền sau đó (thứ 2, thứ 3...) không sinh event nào nữa dù máy vẫn nuốt tiền bình thường ở tầng phần cứng.

## Triệu chứng / Lỗi

- Tờ tiền đầu tiên: nhận đủ 2 event (Escrow → Credit) đúng như mong đợi.
- Tờ tiền thứ 2 trở đi: không có event nào (không Escrow, không Credit, không DeviceError) — im lặng hoàn toàn dù cắm tiền vào máy vật lý bình thường.

## Nguyên nhân gốc rễ (Root Cause)

Cả driver cũ (`CBA9Controllers.PollingGetEventFunc`) và driver mới (`CBA9ControllersV3.PollingStart`/`DoPollOnceCore_FullSwitchAsOld`) đều tạo **CHỈ 1 object `CashResult cash`** khi bắt đầu polling, rồi **reuse đúng object đó qua TẤT CẢ các vòng poll (mỗi 100ms) trong suốt phiên** — không tạo mới. Trong switch-case xử lý poll, cờ `IsValidMoney` chỉ được set `= true` tại case `SSP_POLL_CREDIT_NOTE` — **không có bất kỳ case nào set nó về `false`**. Tương tự `IsRejected` chỉ được set `true`, không tự reset.

Bản gốc (`ucCarCash.cs`, `frmMotoCash.cs`) xử lý đúng vì consumer tự gọi `ClearCash(cash)` (set `MoneyValue=0; IsValidMoney=false; IsRejected=false; ...`) trực tiếp lên object `cash` nhận được từ event — ngay sau khi xử lý xong 1 tờ tiền (credit hoặc reject). Vì `CashResult` là class (reference type) và `PollEvent` truyền đúng instance nội bộ của driver, mutate `cash` trong consumer sẽ phản ánh lại vào lần poll tiếp theo của driver.

Khi migrate sang `CashDeviceServiceImpl.cs` (Avalonia), người viết chỉ tạo 2 biến local `_lastEscrowDenomination`/`_creditFired` để dedup event — **quên không port lại bước `ClearCash(cash)`** dù comment trong file tự nhận "giữ nguyên logic cũ / parity". Hệ quả: sau khi `AcceptBill()` reset `_creditFired = false` để sẵn sàng nhận tờ tiếp theo, `cash.IsValidMoney` vẫn còn `true` (kẹt vĩnh viễn từ tờ đầu) → ngay vòng poll kế tiếp fire nhầm 1 Credit event giả (dùng giá trị stale) rồi khoá `_creditFired = true` lại — và vì `cash.IsValidMoney` không bao giờ được set về `false`, nhánh Escrow (`!cash.IsValidMoney && ...`) không bao giờ đúng nữa cho các tờ tiền tiếp theo.

## Giải pháp

```csharp
// Trong nhánh Credit (Trường hợp 1) — CashDeviceServiceImpl.OnCba9PollAsync
BillReceived?.Invoke(this, new BillReceivedEventArgs { ... IsEscrowed = false });

// BẮT BUỘC: reset object cash dùng chung, parity với ClearCash() bản gốc
cash.IsValidMoney = false;
cash.MoneyValue = 0;

// Trong nhánh Reject (Trường hợp 3)
DeviceError?.Invoke(this, "Bill rejected");
cash.IsRejected = false;
cash.MoneyValue = 0;
_lastEscrowDenomination = 0;
```

1. Xác định driver có tái sử dụng cùng 1 object trạng thái (state object) qua các lần callback/poll hay không (đọc code driver, không giả định).
2. Nếu có → sau khi consumer đã "tiêu thụ" xong 1 trạng thái (đã raise event / đã xử lý xong), PHẢI tự reset các cờ liên quan trên chính object đó về trạng thái trung lập — không chỉ dùng biến local để dedup.
3. Build lại, test thực tế với ≥ 2 tờ tiền liên tiếp (không chỉ test 1 tờ).

## Áp dụng lại (How to reuse)

- Khi migrate bất kỳ device driver nào (cash, card reader, barcode scanner...) có event/callback định kỳ (poll) → luôn kiểm tra: object trạng thái truyền qua event là **new mỗi lần** hay **reuse 1 instance**? Đọc thẳng source constructor + polling loop, đừng suy đoán.
- Nếu object trạng thái là reused/mutable và code cũ có bước "clear/reset" tường minh (`ClearCash`, `ResetState`, `cash.Xxx = false`...) sau khi xử lý — bước đó là PHẦN LOGIC BẮT BUỘC, không phải boilerplate có thể bỏ qua khi refactor.
- Khi review PR migrate driver: tìm bằng được đoạn code cũ có gọi hàm "clear/reset" nào không, nếu có mà bản mới thiếu → REQUEST CHANGES ngay, đừng chỉ nhìn code mới có compile/chạy được tờ đầu tiên là đủ.
- Test case bắt buộc cho cash acceptor: LUÔN test tối thiểu 2 tờ tiền liên tiếp trong cùng 1 phiên, không chỉ test 1 tờ — bug loại này chỉ lộ ra từ tờ thứ 2.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Guard variable dùng để dedup (`_creditFired`, `_lastEscrowDenomination`) rất dễ khiến người review tưởng "đã có state management đầy đủ" — nhưng guard local không thay thế được việc reset field thật trên object dùng chung.
- ⚠️ Bug này KHÔNG xuất hiện khi build/chạy demo nhanh 1 tờ tiền — chỉ lộ ra khi test tờ thứ 2, rất dễ bị bỏ sót trong smoke test.
- ⚠️ `IsStackerFull` là lỗi phần cứng nghiêm trọng (khay đầy) — KHÔNG reset cờ này, vì đây là trạng thái cần dừng hẳn phiên nhận tiền cho tới khi được xử lý (khác với `IsValidMoney`/`IsRejected` là trạng thái theo từng tờ tiền).

## Tham chiếu

- File liên quan: `IPGS.Kiosk.Avalonia/Services/Implementations/CashDeviceServiceImpl.cs`
- Driver cũ: `IPGS.Cash/Controllers/CBA9Controllers.cs`, `IPGS.Kiosk/LotteDesigns/CarUserControls/CashUC/ucCarCash.cs` (hàm `ClearCash`)
- Driver mới: `ParkingV8.Cash/Controllers/CBA9ControllersV3.cs` (field `cash` tạo 1 lần trong `PollingStart()`)
- Project liên quan: iPGSv4 (T-F12 migrate WinForms → Avalonia)
