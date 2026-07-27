---
category: avalonia
tags: [avalonia, systemutils, logger, nullreferenceexception, kztek-tool-multyplatform, static-init]
severity: high
created: 2026-07-21
updated: 2026-07-21
project-origin: iPGSv4 (IPGS.Kiosk.Avalonia)
---

# IPGS.Kiosk.Avalonia crash NullReferenceException vì Program.cs/App.axaml.cs quên init SystemUtils.logger (bản Avalonia dùng project Kztek.Tool khác bản WinForms)

## Tình huống gặp phải

Chạy app `IPGS.Kiosk.Avalonia` (bản migrate từ WinForms `IPGS.Kiosk`), lần đầu gọi API tới Parking server (ví dụ `KioskApiServiceImpl`, `ParkingAuthServiceImpl`...) thì crash ngay:

```
System.NullReferenceException: 'Object reference not set to an instance of an object.'
  at ... SystemUtils.logger.SaveAPILogDetail(apiLogDetail, callerName, lineNumber, filePath);
```
(exception dialog hiện dll `KztekApi.MultyPlatform.dll`)

## Nguyên nhân gốc rễ (Root Cause)

Đây cùng bản chất với lesson đã có [[iparkingv8-api-systemutils-logger-null]] (`dotnet-general/iparkingv8-api-systemutils-logger-null.md`): `SystemUtils.logger` là static field không có default, không lazy-init.

Bản WinForms gốc `IPGS.Kiosk/Program.cs:26` có init:
```csharp
SystemUtils.logger = LoggerFactory.CreateLoggerService(EmLogServiceType.OFFLINE_DB, SettingPathManagement.SaveConfigFolder);
```

Nhưng khi migrate sang Avalonia, `IPGS.Kiosk.Avalonia/Program.cs` (entry point mới, dùng `BuildAvaloniaApp().StartWithClassicDesktopLifetime(args)`) và `App.axaml.cs` (nơi wiring các service — parity với phần còn lại của `Program.cs` gốc) **không copy dòng init logger này** — dòng init nằm implicit trong code cũ, dễ bị bỏ sót khi tách entry point.

**Khác biệt quan trọng so với lesson gốc:** `IPGS.Kiosk.Avalonia.csproj` KHÔNG reference cùng `Kztek.Tool` project với bản WinForms — nó reference:
```
E:\KZTEK\...\parking-v8-app-avalonia\src\Kztek.Tool.MultyPlatform\Kztek.Tool.MultyPlatform.csproj
```
Trong project này, `LoggerFactory` nằm ở namespace **`Kztek.Tool.LogHelpers`** (không phải `Kztek.Tool` như bản WinForms cũ) — nên chỉ `using Kztek.Tool;` là KHÔNG đủ, compiler báo `CS0103: The name 'LoggerFactory' does not exist in the current context`.

## Giải pháp

Trong `App.axaml.cs`, dòng đầu tiên của `OnFrameworkInitializationCompleted()` (trước khi wire bất kỳ service nào dùng Kztek.Tool.MultyPlatform):

```csharp
using Kztek.Object;          // EmLogServiceType
using Kztek.Tool;             // SystemUtils
using Kztek.Tool.LogHelpers;  // LoggerFactory — namespace RIÊNG trong Kztek.Tool.MultyPlatform, khác bản WinForms

public override void OnFrameworkInitializationCompleted()
{
    SystemUtils.logger = LoggerFactory.CreateLoggerService(EmLogServiceType.OFFLINE_DB, AppContext.BaseDirectory);
    // ... phần còn lại (LoadAppSettings, LoadKioskAppConfig, wire services...)
}
```

## Áp dụng lại (How to reuse)

- Khi migrate bất kỳ app WinForms nào dùng `Kztek.Tool.SystemUtils` sang Avalonia (đặc biệt nếu project Avalonia mới reference `Kztek.Tool.MultyPlatform` thay vì `Kztek.Tool` gốc) → **PHẢI** kiểm tra lại namespace của `LoggerFactory` bằng Grep/Read trực tiếp source (`LogHelpers/LoggerFactory.cs`), KHÔNG giả định giống bản WinForms.
- Dấu hiệu nhận biết nhanh: `NullReferenceException` trỏ vào `SystemUtils.logger.SaveAPILogDetail(...)` hoặc `SaveSystemLog(...)` ngay dòng đầu 1 API call — 99% do quên init logger ở entry point mới (Program.cs/App.axaml.cs), không phải lỗi logic nghiệp vụ.
- Kiểm tra `.csproj` của project Avalonia bằng Grep `Kztek.Tool` để biết đang reference bản Kztek.Tool nào (`libs/Tool/1.Source/Kztek.Tool` hay `Kztek.Tool.MultyPlatform`) trước khi copy code init logger từ bản WinForms — 2 bản có thể khác namespace.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Nhiều nơi trong `IPGS.Kiosk.Avalonia` gọi `SystemUtils.logger?.SaveSystemLog(...)` với null-conditional (`?.`) nên KHÔNG crash khi logger null — chỉ im lặng không ghi log. Nhưng code trong `Kztek.Tool.MultyPlatform`/`KztekApi.MultyPlatform` (API layer, không phải code app) gọi thẳng `SystemUtils.logger.SaveAPILogDetail(...)` KHÔNG có `?.` → crash cứng. Đừng chủ quan vì thấy code app đã dùng `?.` là an toàn.
- ⚠️ `EmLogServiceType.OFFLINE_DB` tạo `LogToSQLite` — cần path ghi được; dùng `AppContext.BaseDirectory` (cross-platform, parity `AppPathService.AppRoot`) thay `SettingPathManagement.SaveConfigFolder` (chỉ có ở WinForms/IPGS.Ultility).

## Tham chiếu

- File liên quan: `IPGS.Kiosk.Avalonia/App.axaml.cs` (OnFrameworkInitializationCompleted, dòng init logger), `IPGS.Kiosk/Program.cs:26` (bản gốc WinForms để đối chiếu parity)
- Lesson liên quan: [[iparkingv8-api-systemutils-logger-null]]
- Project liên quan: `iPGSv4` (IPGS.Kiosk.Avalonia) — migrate-ipgs-kiosk-avalonia plan
