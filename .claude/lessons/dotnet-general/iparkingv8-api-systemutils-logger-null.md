---
category: dotnet-general
tags: [iparkingv8-api, systemutils, logger, nullreferenceexception, static-init]
severity: high
created: 2026-07-02
updated: 2026-07-02
project-origin: parking-v8-app (ClearVehicleTool)
---

# IParkingv8.API luôn crash NullReferenceException nếu quên khởi tạo SystemUtils.logger trước

## Tình huống gặp phải

Đang viết một tool console/service độc lập mới (`tools/clearVehicleTool`) trong repo `parking-v8-app`, dùng lại `IParkingv8.API.Implementation.v8.ApiServerv8` để gọi API server (login, lấy danh sách sự kiện Exit, xoá AccessKey). Đây là lần đầu dùng `IParkingv8.API` từ một project *ngoài* app WinForms chính (`IParkingv8`).

## Triệu chứng / Lỗi

Gọi `apiServer.Auth.LoginAsync()` (hoặc bất kỳ method nào trong `AccessKeyAPI`, `ReportEntry`, `ReportExit`...) crash ngay với:

```
Unhandled exception. System.NullReferenceException: Object reference not set to an instance of an object.
   at IParkingv8.API.Implementation.v8.AuthServicev8.LoginByAccountAsync()
   at IParkingv8.API.Implementation.v8.AuthServicev8.LoginAsync()
```

Exception xảy ra ngay ở dòng đầu tiên có gọi `SystemUtils.logger.SaveSystemLog(...)`.

## Nguyên nhân gốc rễ (Root Cause)

`Kztek.Tool.SystemUtils` có field static `public static ILogger logger;` — **không có giá trị mặc định, không lazy-init, không null-check ở nơi gọi**. Mọi class trong `IParkingv8.API` (AuthServicev8, AccessKeyAPI, ReportEntry, ReportExit, DataServicev8...) gọi thẳng `SystemUtils.logger.SaveSystemLog(...)` ở gần như đầu mỗi method, không kiểm tra null.

Trong app WinForms chính (`IParkingv8\Program.cs`), việc khởi tạo `SystemUtils.logger` được làm ở `LoadAppConfig()` (dòng ~240) *trước khi* bất kỳ API service nào được dùng:

```csharp
SystemUtils.logger = LoggerFactory.CreateLoggerService(AppData.AppConfig.LogServiceType, IparkingingPathManagement.baseBath);
```

Nhưng đây là code implicit, không nằm trong `ApiServerv8` hay bất kỳ constructor nào của `IParkingv8.API` — nên bất kỳ project mới nào dùng lại `IParkingv8.API`/`Kztek.Tool` mà không tự làm bước này sẽ luôn crash ngay lần gọi API đầu tiên.

## Giải pháp

Khởi tạo `SystemUtils.logger` **trước khi** tạo `ApiServerv8` (hoặc bất kỳ service nào trong `IParkingv8.API`), dùng `LoggerFactory.CreateLoggerService(...)` có sẵn trong `Kztek.Tool`:

```csharp
using Kztek.Object;   // EmLogServiceType
using Kztek.Tool;      // SystemUtils, LoggerFactory

// EmLogServiceType.OFFLINE_FILE -> LogToFile (chỉ ghi file, không cần SQLite) - phù hợp cho tool/service nhỏ.
// EmLogServiceType.OFFLINE_DB   -> LogToSQLite (dùng khi cần query log phức tạp).
SystemUtils.logger = LoggerFactory.CreateLoggerService(
    EmLogServiceType.OFFLINE_FILE,
    Path.Combine(AppContext.BaseDirectory, "SystemLogs"));

// Chỉ SAU dòng trên mới được new ApiServerv8(...) / gọi bất kỳ API nào.
var apiServer = new ApiServerv8(serverConfig);
```

1. Import `Kztek.Object` (cho `EmLogServiceType`) và `Kztek.Tool` (cho `SystemUtils`, `LoggerFactory`).
2. Gọi `SystemUtils.logger = LoggerFactory.CreateLoggerService(...)` ở đầu `Main()`/`Program.cs`, trước mọi dòng dùng `IParkingv8.API`.
3. Chọn `OFFLINE_FILE` cho tool nhỏ (chỉ tạo folder + ghi file text), `OFFLINE_DB` nếu cần log dạng SQLite như app chính.

## Áp dụng lại (How to reuse)

- Bất kỳ khi nào tạo project mới (console app, worker service, script) mà `ProjectReference` tới `IParkingv8.API` hoặc bất kỳ project nào transitively dùng `Kztek.Tool.SystemUtils` → **PHẢI** khởi tạo `SystemUtils.logger` ngay đầu `Main()`, kể cả khi tool đó không quan tâm đến log.
- Dấu hiệu nhận biết: `NullReferenceException` mà stack trace trỏ thẳng vào 1 trong các file `IParkingv8.API\Implementation\v8\*.cs` ở dòng gọi `SystemUtils.logger.SaveSystemLog(...)` ngay từ đầu method → 99% là quên init logger, không phải lỗi logic của tool.
- Không cần `IparkingingPathManagement.baseBath` (thuộc app WinForms chính) — có thể dùng path bất kỳ, ví dụ `AppContext.BaseDirectory` cho tool độc lập.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ `SystemUtils.logger` là **static toàn process** — nếu app có nhiều thread/worker khởi tạo lại nhiều lần sẽ ghi đè lẫn nhau; chỉ init 1 lần ở entry point.
- ⚠️ Nếu quên init, exception xảy ra ở lần gọi API *đầu tiên*, không phải lúc `new ApiServerv8(...)` — dễ nhầm tưởng lỗi ở logic nghiệp vụ hoặc ở `ServerConfig` sai.
- ⚠️ Copy `libs/Camera/libs/Kztek.Tool/...` là bản duplicate cũ của `libs/Tool/1.Source/Kztek.Tool` trong cùng repo — đảm bảo ProjectReference trỏ đúng bản `libs/Tool/1.Source/Kztek.Tool/Kztek.Tool.csproj` (bản chính, được `IParkingv8.API` dùng), không lấy nhầm bản trong `libs/Camera`.

## Tham chiếu

- File liên quan: `libs/Tool/1.Source/Kztek.Tool/SystemUtils.cs`, `libs/Tool/1.Source/Kztek.Tool/LogHelpers/LoggerFactory.cs`, `IParkingv8/Program.cs` (dòng ~240, ví dụ init đúng trong app chính)
- Project liên quan: `parking-v8-app` — mọi tool mới trong `tools/*` dùng `IParkingv8.API` (ví dụ tiếp theo sau `ClearVehicleTool`)
