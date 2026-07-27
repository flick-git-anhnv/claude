---
category: avalonia
tags: [build, msbuild, xaml-compile, no-dependencies, false-negative, avln2100]
severity: high
created: 2026-07-26
updated: 2026-07-26
project-origin: iPGSv4 (branch PAYMENT_KIOSK_HORIZONTAL_PARKING8) — migrate kiosk màn ngang sang Avalonia
---

# `dotnet build --no-dependencies` báo 0 Error dù AXAML đang lỗi — build tăng dần bỏ qua XAML compile

## Tình huống gặp phải

Migrate ~25 view Avalonia, mỗi lần sửa 1 view thì verify nhanh bằng:

```bash
dotnet build App.csproj -r win-x64 -v m --no-dependencies | grep -E ": error|Error\(s\)"
```

Vòng lặp sửa-build-sửa-build hàng chục lần, lần nào cũng `0 Error(s)` → tin là mọi AXAML đều hợp lệ.

## Triệu chứng / Lỗi

Hành vi **lật qua lật lại** rất dễ gây nhầm:

```
lần 1:  2 Error(s)          ← có lỗi
lần 2 (chạy lại y nguyên):  0 Error(s)   ← "tự hết"?!
...
lần n:  28 Error(s)
lần n+1 (chạy lại y nguyên): 0 Error(s)  ← lại "tự hết"
```

Chỉ khi xoá sạch `obj/` + `bin/` rồi build lại mới lộ lỗi thật:

```
Avalonia error AVLN2100: Cannot parse a compiled binding without an explicit
x:DataType directive to give a starting data type for bindings. Line 28, position 16.
```

## Nguyên nhân gốc rễ (Root Cause)

Bước biên dịch XAML của Avalonia (`Avalonia.Build.Tasks` / `CompileAvaloniaXaml`) chạy **sau** khi
biên dịch C# và **phụ thuộc vào input/output timestamp** của MSBuild. Khi:

1. Lần build trước đã tạo được assembly trung gian, **và**
2. `--no-dependencies` khiến MSBuild bỏ qua việc dựng lại project phụ thuộc,

thì MSBuild coi target là "up-to-date" và **bỏ qua hẳn `CompileAvaloniaXaml`**. C# compile vẫn chạy
(nên lỗi CS vẫn hiện), nhưng lỗi AXAML thì không bao giờ được kiểm tra → `0 Error(s)` giả.

Chuỗi "N errors rồi 0 errors" là hệ quả: lần đầu XAML compile chạy và fail; fail xong nó vẫn ghi
được output trung gian nên lần sau MSBuild coi là up-to-date và skip → báo sạch.

## Giải pháp

```bash
# Verify NHANH trong lúc code (chấp nhận chỉ bắt lỗi C#):
dotnet build App.csproj -r win-x64 -v m --no-dependencies

# Verify THẬT trước khi kết luận "build sạch" — BẮT BUỘC:
rm -rf App/obj App/bin
dotnet build App.csproj -r win-x64 -v m -m:1     # KHÔNG dùng --no-dependencies
```

1. Trong vòng lặp sửa code: dùng build nhanh, nhưng **không được coi kết quả là bằng chứng AXAML đúng**.
2. Trước khi báo "0 Error" / đóng task / commit: xoá `obj` + `bin` rồi build **đầy đủ**.
3. Thêm `-m:1` cho build đầy đủ — xem lesson `avalonia-parallel-build-file-lock.md`
   (build song song gây `AVLN9999`/`CS0006` file lock ngẫu nhiên trên solution nhiều project).
4. Sau khi xoá `obj`, **không** dùng `--no-dependencies` nữa: project phụ thuộc chưa có
   `obj/Debug/net8.0/ref/*.dll` → lỗi giả khác (`CS0006 Metadata file ... could not be found`).

## Áp dụng lại (How to reuse)

- Thấy số lỗi **giảm về 0 khi chạy lại y nguyên lệnh build** → gần như chắc chắn là XAML compile bị
  skip, KHÔNG phải lỗi đã được sửa. Xoá `obj` rồi build lại để biết sự thật.
- Chỉ tin `0 Error(s)` khi lệnh đó là **clean + full build**.
- Mỗi lần thêm/sửa `.axaml`: nhớ rằng build nhanh không phát hiện được `AVLN*`.
- Với `x:CompileBindings` / `x:DataType`: mọi lỗi thuộc nhóm `AVLN21xx` chỉ lộ ra ở XAML compile,
  không bao giờ lộ ở C# compile.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Nguy hiểm nhất là **im lặng**: view lỗi binding vẫn build "sạch", chỉ crash lúc chạy khi
  navigate tới đúng màn đó — rất dễ trôi vào commit rồi vào bản deploy.
- ⚠️ `dotnet build -v q` cũng in "Build succeeded" trong tình huống này — verbosity không giúp gì.
- ⚠️ `dotnet clean` KHÔNG chắc dọn hết trạng thái làm MSBuild coi là up-to-date; xoá thẳng thư mục
  `obj`/`bin` mới đáng tin (xem thêm `dotnet-general/msbuild-obj-filelistabsolute-stale-conflict-marker.md`).
- ⚠️ Đừng suy ra "sửa xong rồi" từ việc số lỗi tụt xuống giữa 2 lần build liên tiếp.

## Tham chiếu

- Project: iPGSv4, branch `PAYMENT_KIOSK_HORIZONTAL_PARKING8`
- Liên quan: `avalonia/avalonia-parallel-build-file-lock.md` (bắt buộc `-m:1`),
  `dotnet-general/msbuild-obj-filelistabsolute-stale-conflict-marker.md` (obj bẩn),
  `avalonia/avalonia-itemscontrol-canvas-position-compiled-binding.md` (lỗi AVLN2000 phát hiện được
  nhờ đúng cách build này)
