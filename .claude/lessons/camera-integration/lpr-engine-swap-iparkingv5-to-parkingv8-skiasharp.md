---
category: camera-integration
tags: [LPR, ILpr, ParkingV8.Lpr, iParkingv5.Lpr, SkiaSharp, ReadPL, ProjectReference-swap]
severity: high
created: 2026-07-20
updated: 2026-07-20
project-origin: iPGSv4
---

# Đổi engine LPR từ iParkingv5.Lpr (Windows-only, HawkeyeCS.dll thiếu) sang ParkingV8.Lpr (cross-platform, SkiaSharp)

## Tình huống gặp phải

Đang sửa lỗi build `IPGS.Object` sau khi đổi `ProjectReference` sang bộ thư viện `Kztek.*.MultyPlatform` mới ([[projectreference-swap-drops-transitive-deps-silently]]). Ban đầu tạm re-add `ProjectReference` tới `iParkingv5.Lpr` cũ để có type `ILpr`/`DetectLprResult`, và viết bridge `SkiaDrawingBridge` để convert `SKBitmap` (pipeline camera mới) sang `System.Drawing.Bitmap` (ILpr cũ yêu cầu) — nhưng `iParkingv5.Lpr` bị lỗi build vì thiếu file native `HawkeyeCS.dll` (không có trên máy, có thể do `.gitignore`) và dùng `OpenVINO.CSharp.Windows` (Windows-only, không giúp gì cho mục tiêu cross-platform). Giữa chừng, user tự đổi `ProjectReference` sang project MỚI **`ParkingV8.Lpr`** (`1.IPARKING\v8\6.Avalonia\parking-v8-app-avalonia\src\ParkingV8.Lpr`) và báo "đã ref lại vào ParkingV8.Lpr, hãy sửa nốt".

## Triệu chứng / Lỗi

```
error CS0234: 'LprDetecter' does not exist in namespace 'iParkingv5' → sau khi đổi ref, còn:
error CS0234: 'HawkeyeCS' could not be found (are you missing an assembly reference?)
error CS0246: 'KztekLpr' could not be found
```
Sau khi đổi sang `ParkingV8.Lpr`, các lỗi build MỚI xuất hiện (namespace cũ + API đã đổi):
```
error CS0234: type or namespace 'LprDetecter' does not exist in namespace 'iParkingv5' (using cũ chưa update)
error CS1061: 'ILpr' does not contain a definition for 'GetPlateNumber' (chỉ còn GetPlateNumberAsync)
error CS0234: 'LoggerFactory' does not exist in namespace 'Kztek.Tool' (đổi namespace con)
error CS0103: 'NetWorkTools' does not exist (thiếu using Kztek.Tool.NetWorkHelpers ở 1 vài file)
```

## Nguyên nhân gốc rễ (Root Cause)

1. **`ParkingV8.Lpr` là bản kế nhiệm cross-platform của `iParkingv5.Lpr`**, cùng cấu trúc thư mục (`LprDetecters/ILpr.cs`, `LprDetecters/KztekLprs/*`, `LprDetecters/AmericalLprs/*`, `Models/DetectLprResult.cs`, `Events/Events.cs`) nhưng đổi hoàn toàn kiểu ảnh sang `SkiaSharp.SKBitmap`/`SKRectI` thay vì `System.Drawing.Image`/`Rectangle` — dùng NuGet `ReadPL 1.0.8` (khớp lesson đã có [[readpl-api-changed-skbitmap-not-systemdrawing]]).
2. **`ILpr.GetPlateNumberAsync` là method DUY NHẤT còn lại** — bản cũ có cả `GetPlateNumber` (sync) và `GetPlateNumberAsync`; bản mới chỉ còn async. Code cũ gọi `StaticPool.LprDetecter?.GetPlateNumber(...)` (sync) sẽ lỗi CS1061 vì method không tồn tại nữa.
3. **`LprFactory.CreateLprDetecter` giảm từ 2 tham số xuống 1** (`(LprConfig)` thay vì `(LprConfig, object?)`).
4. **`LoggerFactory` di chuyển namespace con**: `Kztek.Tool.LoggerFactory` (bản cũ, hoặc giả định) → `Kztek.Tool.LogHelpers.LoggerFactory` (bản MultyPlatform mới) — cùng root namespace `Kztek.Tool` nên dễ tưởng nhầm không đổi.
5. **Vì `ILpr` mới nhận thẳng `SKBitmap`**, toàn bộ bridge chuyển đổi ảnh (`SkiaDrawingBridge.ToDrawingBitmap`) viết trước đó để tương thích `ILpr` cũ trở thành THỪA — phải xóa hẳn, không giữ lại "cho chắc", tránh code chết gây hiểu nhầm về kiến trúc.

## Giải pháp

1. Đổi mọi `using iParkingv5.LprDetecter.LprDetecters;` / `using iParkingv5.Lpr.Objects;` → `using ParkingV8.Lpr.LprDetecters;` / `using ParkingV8.Lpr.Models;`.
2. Đổi `StaticPool.LprDetecter?.GetPlateNumber(cropImage, true, null, 0)` (sync) → gọi `GetPlateNumberAsync` qua `Task.Run` (giữ nguyên hành vi offload thread cũ vì engine LPR block thread dù là "Async"):
   ```csharp
   var lprResult = StaticPool.LprDetecter is null
       ? null
       : await Task.Run(() => StaticPool.LprDetecter.GetPlateNumberAsync(cropImage, true, null, 0));
   ```
3. Bỏ hẳn bridge `SkiaDrawingBridge` — truyền thẳng `SKBitmap` đã crop vào `GetPlateNumberAsync`, không cần convert.
4. Đổi `LprFactory.CreateLprDetecter(config, null)` → `LprFactory.CreateLprDetecter(config)`.
5. Đổi `Kztek.Tool.LoggerFactory` → `Kztek.Tool.LogHelpers.LoggerFactory`.
6. Grep toàn bộ camera controller khác dùng chung pattern (`NetWorkTools`, `ImageHelper`) để đảm bảo cùng thêm đủ `using Kztek.Tool.NetWorkHelpers;`/`using Kztek.Tool.ImageHelpers;` — 1 file đã có sẵn không có nghĩa file khác cùng loại cũng có.
7. Sau khi build hết lỗi CS, build lại `--no-incremental` để lộ lỗi AVLN2000/2100 XAML (compiled binding) phát sinh riêng biệt — không liên quan LPR nhưng cùng đợt Avalonia 12.

## Áp dụng lại (How to reuse)

- Khi thấy 1 dependency Windows-only (native DLL, OpenVINO Windows, OpenCvSharp4.Windows) gây lỗi build trong nỗ lực cross-platform hóa → tìm xem có bản kế nhiệm cross-platform cùng hệ sinh thái (thường cùng root namespace, đặt cạnh các project `*.MultyPlatform`) trước khi cố fix riêng lẻ dependency cũ.
- Khi đổi 1 dependency LPR/Camera SDK → luôn kiểm tra lại: (a) method sync có còn không hay chỉ còn async, (b) số tham số factory method, (c) namespace con của các class dùng chung root namespace (VD `Kztek.Tool.X`).
- Nếu đã viết bridge convert kiểu dữ liệu (SKBitmap↔System.Drawing) để tương thích 1 API cũ, và API đó sau này đổi hẳn sang cùng kiểu dữ liệu (SKBitmap) → XÓA bridge ngay, đừng giữ lại.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ `dotnet build <sln>` bình thường có cache incremental — dùng `--no-incremental` khi vừa đổi ProjectReference/NuGet lớn để chắc chắn thấy hết lỗi thật, tránh báo "0 Error" giả.
- ⚠️ Namespace con đổi (`Kztek.Tool` → `Kztek.Tool.LogHelpers`) dễ bị bỏ sót vì root namespace không đổi — IDE auto-complete có thể gợi ý sai nếu cache stale.

## Tham chiếu

- [[readpl-api-changed-skbitmap-not-systemdrawing]] — nguồn gốc việc ReadPL 1.0.8 đổi sang SKBitmap
- [[projectreference-swap-drops-transitive-deps-silently]] — bối cảnh trước đó dẫn tới việc đổi LPR engine
- Project liên quan: `iPGSv4` (`IPGS.Object`, `IPGSUseCam`), `ParkingV8.Lpr` (`1.IPARKING\v8\6.Avalonia\parking-v8-app-avalonia\src\ParkingV8.Lpr`)
