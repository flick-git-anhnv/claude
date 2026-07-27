---
category: avalonia
tags: [devtools, f12, nuget, package-version, avalonia-diagnostics, avaloniaui-diagnosticssupport, appbuilder]
severity: medium
created: 2026-07-21
updated: 2026-07-21
project-origin: iPGSv4 (IPGS.Kiosk.Avalonia), tham chiếu parking-v8-app-avalonia (ParkingV8.App)
---

# Avalonia core lên 12.1.0 → package DevTools đổi tên: `Avalonia.Diagnostics` → `AvaloniaUI.DiagnosticsSupport`, API đổi `AttachDevTools()` → `.WithDeveloperTools()`

## Tình huống gặp phải

> Đang làm gì? Tính năng gì? Môi trường nào?

Bật Avalonia DevTools (F12) cho `IPGS.Kiosk.Avalonia` — core đang ở `Avalonia`/`Avalonia.Desktop`/`Avalonia.Themes.Fluent` **12.1.0**. Theo pattern cũ (xem [[avalonia-attachdevtools-double-window]], viết khi parking-v8-app-avalonia còn ở Avalonia 11.2.7): thêm `PackageReference Avalonia.Diagnostics` + gọi `this.AttachDevTools()` trong `App.axaml.cs`.

## Triệu chứng / Lỗi

```
error NU1102: Unable to find package Avalonia.Diagnostics with version (>= 12.1.0)
  - Found 105 version(s) in nuget.org [ Nearest version: 11.3.18 ]
```

Thử ghim `Avalonia.Diagnostics` xuống `11.3.18` (mismatch version so với core `12.1.0`) → **restore/build vẫn PASS** (API `AttachDevTools()` còn tương thích ngược), nên ban đầu tưởng đã xong — nhưng đây là hướng SAI, vì package đã bị **archive/ngừng phát triển theo core mới** (xem phần "Nguyên nhân").

## Nguyên nhân gốc rễ (Root Cause)

Kiểm tra NuGet flat-container: `Avalonia.Diagnostics` dừng ở `11.3.18`, không có bản nào khớp core `12.x`, trong khi các sub-package khác (`Avalonia.Controls.DataGrid`, `Avalonia.Skia`, `Avalonia.Win32`, `Avalonia.X11`...) đều đã có `12.1.0`. Đối chiếu với `parking-v8-app-avalonia/src/ParkingV8.App/ParkingV8.App.csproj` (project cùng tổ chức, cũng đã lên core 12.1.0 trước iPGSv4) → phát hiện họ đã **thay thế hẳn package**: `AvaloniaUI.DiagnosticsSupport` (versioning độc lập, hiện tại `2.2.3`, không đi theo số version của Avalonia core). Đây là package DevTools thế hệ mới của Avalonia, kiến trúc khác hẳn — DevTools chạy **out-of-process** (`DeveloperToolsRunner`, `StartDevToolsProcessIfNeededAsync`, giao tiếp qua `HttpDeveloperToolsProtocol`/`NamedPipeDeveloperToolsProtocol`) thay vì overlay window in-process như bản cũ.

API cũng đổi tên: namespace vẫn là `Avalonia` nhưng class là `Avalonia.DeveloperToolsExtensions` với extension method **`.WithDeveloperTools()`** gọi trên `AppBuilder` (trong `Program.cs.BuildAvaloniaApp()`) — KHÔNG còn `this.AttachDevTools()` gọi trên `Application` trong `App.axaml.cs` nữa.

**Lưu ý quan trọng:** `ParkingV8.App.csproj` MỚI CHỈ khai báo `PackageReference AvaloniaUI.DiagnosticsSupport` — chưa từng gọi `.WithDeveloperTools()` ở đâu trong code (`grep` xác nhận). Tức là bên đó thêm gói nhưng chưa thực sự wire — không thể copy-paste "cách dùng" từ đó, chỉ tham khảo được đúng package ID + version.

## Giải pháp

```xml
<!-- .csproj -->
<PackageReference Include="AvaloniaUI.DiagnosticsSupport" Version="2.2.3" Condition="'$(Configuration)' == 'Debug'" />
```

```csharp
// Program.cs
public static AppBuilder BuildAvaloniaApp()
{
    var builder = AppBuilder.Configure<App>()
        .UsePlatformDetect()
        .LogToTrace();

#if DEBUG
    builder = builder.WithDeveloperTools();
#endif

    return builder;
}
```

1. Gỡ hoàn toàn `Avalonia.Diagnostics` / `AttachDevTools()` — không dùng cho core `12.x`.
2. Thêm `AvaloniaUI.DiagnosticsSupport` (version theo dòng riêng, KHÔNG khớp core), điều kiện `Configuration == 'Debug'`.
3. Wire bằng `.WithDeveloperTools()` trên `AppBuilder` trong `BuildAvaloniaApp()` (`Program.cs`) — không gọi trong `App.axaml.cs` nữa vì API mới không có extension method trên `Application`.
4. `dotnet build -c Debug` xác nhận `0 Error(s)` trước khi coi là xong.
5. Vì kiến trúc mới chạy out-of-process, KHÔNG áp dụng lỗi "double window" của [[avalonia-attachdevtools-double-window]] (lỗi đó chỉ xảy ra với in-process `AttachDevTools()` cũ) — nhưng thứ tự gọi vẫn nên đặt sớm (trong `BuildAvaloniaApp`, trước `StartWithClassicDesktopLifetime`) để an toàn.

## Áp dụng lại (How to reuse)

- Khi thấy `Avalonia.Diagnostics` báo NU1102 (không tìm thấy version khớp core) → đây là dấu hiệu Avalonia đã tách DevTools sang package mới `AvaloniaUI.DiagnosticsSupport` — KHÔNG cố ghim version cũ hơn cho `Avalonia.Diagnostics`, chuyển hẳn sang package mới.
- Muốn tra API thật của 1 package chưa quen (không có doc rõ ràng) → đọc trực tiếp chuỗi ASCII trong DLL đã tải về `~/.nuget/packages/<id>/<version>/lib/<tfm>/*.dll` bằng PowerShell (`[System.Text.Encoding]::ASCII.GetString($bytes)` + regex `[ -~]{4,}`) để tìm tên class/method — nhanh hơn đoán mò hoặc build-thử-sai nhiều lần.
- Trước khi copy pattern từ project khác trong cùng tổ chức, `grep` xác nhận method thực sự ĐƯỢC GỌI ở đâu đó, không chỉ dựa vào việc package có được khai báo trong `.csproj` — khai báo package không đồng nghĩa đã wire.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Build PASS với version mismatch (`Avalonia.Diagnostics` 11.3.18 + core 12.1.0) KHÔNG có nghĩa là hướng đi đúng — package có thể đã bị bỏ maintain theo core mới, cần kiểm tra xem tổ chức đã có giải pháp thay thế nào chưa trước khi chấp nhận.
- ⚠️ `.csproj` có `PackageReference` không đảm bảo tính năng đã được bật — luôn `grep` code thực tế xem method liên quan có được gọi hay không.
- ⚠️ API mới (`WithDeveloperTools`) gắn vào `AppBuilder`/`Program.cs`, không phải `Application`/`App.axaml.cs` như API cũ — đừng áp nguyên xi vị trí gọi của lesson cũ.

## Tham chiếu

- Project liên quan: `IPGS.Kiosk.Avalonia` (iPGSv4), `ParkingV8.App` (parking-v8-app-avalonia, chỉ có package chưa wire)
- File: `IPGS.Kiosk.Avalonia/IPGS.Kiosk.Avalonia.csproj`, `IPGS.Kiosk.Avalonia/Program.cs`
- Lesson liên quan: [[avalonia-attachdevtools-double-window]] (API cũ, core 11.x)
