---
category: avalonia
tags: [loading-window, progress-report, device-filter, silent-bug, appstate]
severity: high
created: 2026-07-28
updated: 2026-07-28
project-origin: App-Access-V2 (iAccess Desktop v2)
---

# Loading báo "thành công N thiết bị" nhưng Main hiển thị 0/0 — đếm sai biến so với biến thực dùng

## Tình huống gặp phải

> App iAccess Desktop v2 (Avalonia). Sau khi LoadingWindow chạy xong bước "Tải thông tin thiết
> bị" báo "67 thiết bị" và bước "Tải thông tin khách hàng" báo "1555 khách hàng" (cả 2 xanh, không
> lỗi), user mở vào MainWindow (Tổng quan) thì mọi KPI đều rỗng.

## Triệu chứng / Lỗi

- LoadingWindow: "✔ Tải thông tin thiết bị — 67 thiết bị", "✔ Tải thông tin khách hàng — 1555
  khách hàng" — không có bước nào báo lỗi đỏ.
- MainWindow (Tổng quan): "Thiết bị online 0/0", "Sự kiện phiên này 0", danh sách "Thiết bị
  offline" rỗng, "Đồng bộ dữ liệu" đỏ (mất kết nối — đây là bug RabbitMQ độc lập, không liên quan).

## Nguyên nhân gốc rễ (Root Cause)

`LoadingWorks.GetDeviceConfigAsync` (`iAccessDesktopv2.Avalonia\...\Services\LoadingWorks.cs`) gọi
`DeviceService.GetDeviceDataAsync()` trả về **toàn bộ cây thiết bị** (mọi node: COMPUTER,
CONTROL_UNIT, DOOR...). Dòng hiển thị kết quả bước Loading dùng:

```csharp
step.ResultText = $"{deviceResponse.Data.Count} thiết bị";   // TỔNG toàn bộ node — 67
```

Nhưng ngay phía trên, code lọc ra danh sách **thực sự dùng ở Main**:

```csharp
AppState.BdkControllers = deviceResponse.GetBDKsByComputer(AppState.Computer);
```

`GetBDKsByComputer` chỉ giữ `CONTROL_UNIT` có `Parent.Id` khớp đúng `Computer` của máy đang chạy
(matching theo IP/hostname), và loại bỏ tiếp controller có attribute `purpose == 0`. Nếu bước lọc
này ra **0 phần tử** (do computer khớp nhầm bản ghi, hoặc toàn bộ controller có `purpose=0`) thì
`AppState.BdkControllers` rỗng — nhưng dòng `step.ResultText` KHÔNG dùng biến này, nên Loading vẫn
báo "67 thiết bị" thành công.

`MainViewModel.InitDataAsync()` chỉ tạo `AccessControllerClient` cho từng phần tử trong
`AppState.BdkControllers` → rỗng → `AppState.Controllers.Clients` rỗng → mọi KPI đếm từ đó ra 0/0.

**Bài học tổng quát:** một bước Loading hiển thị "N thiết bị/bản ghi" bằng biến A (tổng response
thô), trong khi màn hình dùng dữ liệu thực tế lại đọc biến B (kết quả sau lọc/match) — nếu A và B
không phải cùng một nguồn, con số hiển thị ở Loading **không đảm bảo** phản ánh đúng dữ liệu Main
sẽ dùng. Bug loại này không throw exception, không set `IsError` → hoàn toàn vô hình ở bước Loading.

## Giải pháp

1. Sửa `step.ResultText` dùng đúng biến đã lọc (`AppState.BdkControllers.Count`) thay vì tổng
   response thô (`deviceResponse.Data.Count`).
2. Thêm log chẩn đoán khi kết quả lọc ra rỗng dù `computer` khớp được — ghi rõ `Computer.Id/Name`
   và tổng số `CONTROL_UNIT` có trong response, để phân biệt 2 khả năng: (a) computer khớp sai bản
   ghi, (b) toàn bộ controller bị loại do `purpose == 0`.

```csharp
AppState.BdkControllers = deviceResponse.GetBDKsByComputer(AppState.Computer);
step.ResultText = $"{AppState.BdkControllers.Count} thiết bị";
if (AppState.BdkControllers.Count == 0)
{
    SystemUtils.logger?.SaveSystemLog(SystemLog.CreateApplicationProccess(
        $"GetDeviceConfig: Computer={computer.Id}/{computer.Name} khop nhung 0 BdkControllers " +
        $"(tong {deviceResponse.Data.Count(d => d.Type == EmDeviceType.CONTROL_UNIT)} control_unit trong response)"));
}
```

## Áp dụng lại (How to reuse)

- Khi thấy Loading báo thành công với số liệu X nhưng màn hình chính hiển thị rỗng/0 → nghi ngờ
  ngay: Loading và màn hình chính có đang đếm 2 biến khác nhau từ cùng 1 response không? Grep
  `step.ResultText =` hoặc tương đương, đối chiếu với biến `AppState.*` mà ViewModel màn chính
  thực sự bind vào.
- Bất kỳ dòng progress-text nào hiển thị `.Count` của response thô — kiểm tra xem có bước lọc nào
  ngay sau đó tạo ra biến khác được dùng thật sự hay không. Nếu có, progress-text phải dùng biến
  sau lọc.
- "Đồng bộ dữ liệu" đỏ trên status bar là dấu hiệu của kết nối RabbitMQ (`App.EventBus.IsConnected`)
  — luồng hoàn toàn độc lập với việc tải device/customer, đừng gộp chung khi debug 2 triệu chứng
  xuất hiện cùng lúc.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Việc lọc ra 0 phần tử không phải lúc nào cũng là lỗi — có thể do sai cấu hình dữ liệu server
  (COMPUTER record không khớp IP/hostname, hoặc `purpose` bị set sai hàng loạt). Log chẩn đoán chỉ
  giúp xác định NGUYÊN NHÂN, không tự fix dữ liệu.
- ⚠️ Đừng chỉ nhìn "Loading không báo lỗi" mà kết luận dữ liệu ổn — kiểm tra luôn biến mà màn hình
  đích thực sự dùng.

## Tham chiếu

- Liên quan: [[avalonia-navigation-null-api-response-wrong-route]], [[avalonia-migration-silent-behavior-drop-loading-flow]]
- Project liên quan: App-Access-V2 (iAccess Desktop v2 Avalonia)
- File: `iAccessDesktopv2.Avalonia\iAccessDesktopv2.Avalonia\Services\LoadingWorks.cs`
