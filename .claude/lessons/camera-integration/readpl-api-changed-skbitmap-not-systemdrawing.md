---
category: camera-integration
tags: [readpl, lpr, skiasharp, system.drawing, cross-platform, nuget-version-drift]
severity: high
created: 2026-07-14
updated: 2026-07-14
project-origin: parking-v8-app-avalonia (Kztek.Cameras.Avalonia)
---

# ReadPL đổi API giữa version — 1.0.3 dùng System.Drawing.Bitmap, 1.0.8 dùng thẳng SkiaSharp.SKBitmap

## Tình huống gặp phải

Kiểm tra cross-platform packages trong `parking-v8-app-avalonia`, phát hiện `System.Drawing.Common` bị dùng trong `ParkingV8.App` (đã xóa vì unused) và trong project ngoài `Kztek.Cameras.Avalonia` (`0.BaseLIB`) — code có helper `SkBitmapToDrawingBitmap()`/`DrawingImageToSkBitmap()` để convert SKBitmap ↔ System.Drawing.Bitmap trước khi gọi `plateReader.Recognize()` (ReadPL — SDK nhận diện biển số).

## Triệu chứng / Lỗi

```
error CS1069: The type name 'Bitmap' could not be found in the namespace 'System.Drawing'.
This type has been forwarded to assembly 'System.Drawing.Common' ...
```//tương tự cho 'Image'. Comment trong code khẳng định "ReadPL Windows-only, cần System.Drawing.Common" nhưng csproj lại thiếu hẳn PackageReference đó.

## Nguyên nhân gốc rễ (Root Cause)

Project đang pin `ReadPL` version **1.0.8** (nuspec ghi `description: Mutil-Platform`), nhưng code + comment trong `AnvPlayerService.cs` được viết cho **ReadPL 1.0.3** — bản cũ có API `Recognize(System.Drawing.Bitmap)` và `Plate.Crop` kiểu `System.Drawing.Image?`.

Dùng reflection (`Assembly.LoadFrom` + liệt kê `GetMethods()`/`GetProperties()`) trên chính DLL `ReadPL.dll` 1.0.8 xác nhận API thực tế đã đổi hoàn toàn sang SkiaSharp:
- `NhanDangBienSo.Recognize(SkiaSharp.SKBitmap)` → `ReadPL.Result`
- `Plate.Crop` → `SkiaSharp.SKBitmap` (không phải `System.Drawing.Image`)

So sánh nuspec: ReadPL 1.0.3 phụ thuộc `System.Drawing.Common`; ReadPL 1.0.8 phụ thuộc `SkiaSharp` + `Sdcb.OpenVINO` — không còn System.Drawing nữa. Helper convert cũ là code thừa sống sót qua lần nâng version package, không ai xóa.

## Giải pháp

1. **Không** thêm `PackageReference System.Drawing.Common` để "fix" lỗi build (đó là che triệu chứng, không phải root cause).
2. Dùng reflection để xác nhận API thật của package đang pin (không tin comment cũ trong code):
   ```csharp
   var asm = Assembly.LoadFrom(pathToDll);
   foreach (var t in asm.GetTypes())
       foreach (var m in t.GetMethods(BindingFlags.Public|BindingFlags.Instance|BindingFlags.DeclaredOnly))
           Console.WriteLine(m); // xem parameter/return type thật
   ```
3. Xóa helper `SkBitmapToDrawingBitmap()` / `DrawingImageToSkBitmap()`, gọi thẳng `plateReader.Recognize(bmp)` (SKBitmap) và dùng thẳng `plate.Crop` (đã là `SKBitmap?`, khớp sẵn với `MotionAnalyzingEventArgs(float, SKBitmap?, SKBitmap?, string)`).
4. Cập nhật lại comment/doc trong csproj và code — comment cũ nói "Windows-only, cần System.Drawing.Common" đã sai sau khi upgrade version.

## Áp dụng lại (How to reuse)

- Khi thấy lỗi build kiểu "type forwarded to assembly X, consider adding a reference" trên một package interop (SDK ngoài) → **đừng vội thêm PackageReference** đó ngay. Kiểm tra trước: package hiện đang pin version bao nhiêu, và API thật của đúng version đó là gì (không tin comment trong code, vì comment có thể lỗi thời sau khi ai đó bump version package).
- So sánh `.nuspec` của 2 version (cũ vs mới đang dùng) trong `~/.nuget/packages/<pkg>/<version>/` để thấy dependency graph đổi (VD: System.Drawing.Common → SkiaSharp) — dấu hiệu rõ ràng API cũng đổi theo.
- Nếu nghi ngờ signature: `Assembly.LoadFrom` + reflection liệt kê method/property là cách nhanh nhất xác nhận sự thật, nhanh hơn xin decompiler.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Comment trong code có thể mô tả đúng một version cũ của dependency nhưng sai hoàn toàn ở version hiện tại — không dùng comment làm nguồn sự thật khi debug lỗi type/API.
- ⚠️ Khi reflection load 1 assembly ngoài có phụ thuộc SkiaSharp/thư viện khác, phải thêm PackageReference tương ứng vào project tool reflection tạm thời, nếu không sẽ gặp `FileNotFoundException` khi gọi `ToString()`/liệt kê method có tham số kiểu ngoài.
- ⚠️ Việc thêm ngược `System.Drawing.Common` để "fix cho qua" sẽ khiến project mất khả năng build/run thật trên Linux (đây là mục tiêu chính của Kztek.Cameras.Avalonia — RuntimeIdentifiers `win-x64;linux-x64`) dù compile vẫn pass trên Windows.

## Tham chiếu

- Project liên quan: `0.BaseLIB/Kztek.Camera/Kztek.Camera/1.Source/Kztek.Cameras.Avalonia` (file `Players/FFMPEG/UserControls/AnvPlayerService.cs`)
- Liên quan: [dotnet-linux-compat-tfm-resx-systemdrawing.md](../dotnet-general/dotnet-linux-compat-tfm-resx-systemdrawing.md)
