---
category: dotnet-general
tags: [linux, cross-platform, net8.0, tfm, resx, system.drawing, skiasharp]
severity: high
created: 2026-06-25
updated: 2026-06-25
project-origin: iPGSv4 (IPGSUseCam — Avalonia)
---

# Linux compat: đổi TFM + loại bỏ System.Drawing + exclude RESX WinForms

## Tình huống gặp phải

Migrate IPGSUseCam từ WinForms sang Avalonia (branch `zcu-avalonia`). Cần build được trên Linux để deploy cross-platform. Các project đang dùng `net8.0-windows`, `System.Drawing.Common`, và có `.resx` WinForms chứa non-string resource.

## Triệu chứng / Lỗi

**Lỗi 1 — TFM block Linux:**
```
The type or namespace name 'Color' could not be found (CS0246)
```
(sau khi chuyển TFM sang `net8.0` mà vẫn còn code dùng `System.Drawing.Color`)

**Lỗi 2 — RESX non-string:**
```
MSB3822: Non-string resources require the System.Resources.Extensions assembly at runtime,
but it was not found in this project's references.
```
(khi build `net8.0` có `.resx` WinForms với embedded images/bitmaps)

## Nguyên nhân gốc rễ (Root Cause)

1. **TFM `net8.0-windows`** — block build Linux. Phải đổi sang `net8.0` và thêm `<RuntimeIdentifiers>win-x64;linux-x64</RuntimeIdentifiers>`.
2. **`System.Drawing.Common` từ .NET 7+** — Windows-only (`PlatformNotSupportedException` trên Linux). Nếu `net8.0-windows` thì SDK tự inject; khi đổi sang `net8.0` phải bỏ package + bỏ global using.
3. **`.resx` WinForms còn sót** — khi `.cs` bị `<Compile Remove>` nhưng `.resx` chưa, MSBuild `net8.0` (không có WinForms SDK) không tìm được `System.Resources.Extensions` để xử lý non-string resources.

## Giải pháp

### Bước 1 — Đổi TFM và thêm RuntimeIdentifiers

```xml
<PropertyGroup>
  <TargetFramework>net8.0</TargetFramework>
  <RuntimeIdentifiers>win-x64;linux-x64</RuntimeIdentifiers>
</PropertyGroup>
```

### Bước 2 — Xử lý System.Drawing.Common

Xóa package khỏi `.csproj`:
```xml
<!-- Xóa: -->
<PackageReference Include="System.Drawing.Common" Version="8.0.0" />
<!-- Và xóa global using nếu có: -->
<Using Include="System.Drawing" />
```

Với code dùng `System.Drawing.Color`, `SystemColors`:
- Nếu tất cả callers nằm trong file excluded → xóa luôn field/method đó
- Nếu vẫn cần dùng trên Windows-only path → giữ package, thêm `[SupportedOSPlatform("windows")]`

### Bước 3 — Thay System.Drawing image processing bằng SkiaSharp

```csharp
// Trước (Windows-only):
using var bmp = new System.Drawing.Bitmap(path);

// Sau (cross-platform):
using SkiaSharp;
var bmp = SKBitmap.Decode(path);
var resized = bmp.Resize(new SKImageInfo(w, h), SKFilterQuality.High);
```

SkiaSharp đã có transitively qua Avalonia — không cần thêm package riêng (hoặc thêm `<PackageReference Include="SkiaSharp" Version="2.88.9" />`).

### Bước 4 — Exclude các `.resx` WinForms bị sót

Glob `**/*.resx` trong project → với mỗi `.resx` của WinForms form/control đã excluded, thêm:

```xml
<ItemGroup>
  <EmbeddedResource Remove="MainForm.resx" />
  <EmbeddedResource Remove="Forms\DataForm\frmCamera.resx" />
  <EmbeddedResource Remove="UserControls\General_CRUD_uc.resx" />
  <!-- ... tất cả .resx có embedded images -->
</ItemGroup>
```

> **Pattern:** mỗi `<Compile Remove="Forms\Xxx\Yyy.cs" />` thường đi kèm `.resx` cùng tên — phải exclude cả hai.

### Bước 5 — Đánh dấu Windows-only API

```csharp
using System.Runtime.Versioning;

[SupportedOSPlatform("windows")]
public static void AddToStartup() { /* Registry code */ }
```

## Áp dụng lại (How to reuse)

- Khi thấy `MSB3822: Non-string resources require System.Resources.Extensions` → glob `**/*.resx`, thêm `<EmbeddedResource Remove>` cho từng file WinForms
- Khi thấy `CS0246 Color not found` sau khi đổi TFM → kiểm tra `System.Drawing.Common` đã bị xóa chưa, tìm tất cả callers, xóa nếu dead code
- Trước khi đổi `net8.0-windows` → `net8.0`, chạy grep `System.Drawing`, `SystemColors`, `Microsoft.Win32.Registry`, `System.Management` để tìm tất cả điểm cần xử lý
- Luôn chạy `dotnet build` sau từng bước để phát hiện lỗi tuần tự (không đổi hết rồi build một lần)

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ `<Compile Remove>` KHÔNG tự động exclude `.resx` cùng tên — phải thêm `<EmbeddedResource Remove>` riêng
- ⚠️ `System.Drawing.Color` là Windows-only từ .NET 7+ — không dùng được trên Linux dù đã thêm package
- ⚠️ `System.Management` (WMI) — Windows-only; kiểm tra zero usage trong code Avalonia trước khi xóa
- ⚠️ `Microsoft.Win32.Registry` — Windows-only; cần `[SupportedOSPlatform("windows")]` trên mọi method dùng nó
- ⚠️ SkiaSharp đã có transitively qua Avalonia nhưng có thể cần explicit package ref để dùng `SKBitmap`, `SKCanvas` API
- ⚠️ Camera SDK HIK/Dahua dùng `System.Drawing.Bitmap` — chỉ cần chuyển sang SKBitmap ngay sau khi nhận image, path xử lý camera vẫn là Windows-only

## Gotcha bổ sung: OpenCvSharp4.Windows kéo WPF

`OpenCvSharp4.Windows` là convenience meta-package gồm: `OpenCvSharp4`, `OpenCvSharp4.Extensions` (WinForms), `OpenCvSharp4.WpfExtensions` (WPF), `OpenCvSharp4.runtime.win`. Khi project có `linux-x64` trong RuntimeIdentifiers, MSBuild tìm WPF runtime pack cho linux-x64 → NETSDK1082.

**Fix:** Thay bằng:
```xml
<!-- Trước: -->
<PackageReference Include="OpenCvSharp4.Windows" Version="x.x" />
<PackageReference Include="OpenCvSharp4.Extensions" Version="x.x" />

<!-- Sau: -->
<PackageReference Include="OpenCvSharp4" Version="x.x" />
<PackageReference Include="OpenCvSharp4.runtime.win" Version="x.x" />
```

`OpenCvSharp4.runtime.win` cung cấp native Windows DLLs nhưng không đòi WPF runtime pack → build thành công cho cả linux-x64.

## Gotcha bổ sung 2: Project WinForms trong .sln gây NETSDK1082

Khi build solution (`.sln`) với `linux-x64` RuntimeIdentifier, tất cả project trong solution đều được resolve — kể cả project **không phải dependency** của app chính. Nếu có project `net8.0-windows` + `UseWindowsForms=true` trong `.sln`, MSBuild cố tìm WinForms runtime pack cho linux-x64 → NETSDK1082.

**Dấu hiệu:** Build project riêng lẻ pass, nhưng build `.sln` fail với NETSDK1082.

**Fix:** Xóa project WinForms cũ ra khỏi `.sln` (không xóa file — chỉ xóa entry trong sln). Kiểm tra xem project đó có thực sự là dependency không trước khi xóa.

## Tham chiếu

- Project: iPGSv4 / IPGSUseCam (branch `zcu-avalonia`)
- Các file đã sửa: `IPGSUseCam.csproj`, `IPGS.Controls.csproj`, `IPGS.Ultility.csproj`, `CameraSettingWindow.axaml.cs`, `UltilityManagement.cs`, `Options/Option.cs`, `ApplicationEx.cs`
