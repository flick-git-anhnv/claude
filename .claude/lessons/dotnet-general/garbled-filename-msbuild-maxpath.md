---
category: dotnet-general
tags: [msbuild, avalonia-resource, max-path, windows, cp-command, glob]
severity: high
created: 2026-07-20
updated: 2026-07-20
project-origin: iPGSv4 (migrate-ipgs-kiosk-avalonia)
---

# File rác tên bị hỏng do lệnh `cp` chạy sai trên Windows chặn toàn bộ build MSBuild (AvaloniaResource glob)

## Tình huống gặp phải

Đang migrate `IPGS.Kiosk` (WinForms) sang Avalonia, subagent trước đó (task 2.A3, port FontHelper) chạy một lệnh `cp` để copy font `.otf` từ `IPGS.Ultility/Fonts` sang `IPGS.Kiosk.Avalonia/Assets/Fonts`. Lệnh `cp` bị lỗi do quoting/escaping sai trên môi trường Windows (Bash tool chạy Git Bash) — toàn bộ chuỗi lệnh (`cp e:\...\Gotham-Book.otf    e:\...\AssetsFonts`) bị NTFS chấp nhận làm MỘT tên file/thư mục duy nhất, với các ký tự đặc biệt (dấu `:`, khoảng trắng, xuống dòng) được NTFS map sang các ký tự Private Use Area (U+F022, U+F00A, U+F03A...). Kết quả: 5 "file" rác nằm ngay trong `Assets/Fonts` với tên dài hơn 230 ký tự.

## Triệu chứng / Lỗi

Mở Visual Studio build project `IPGS.Kiosk.Avalonia` báo lỗi:
```
Cannot expand metadata in expression "$([MSBuild]::ValueOrDefault('%(FullPath)', '').StartsWith($([MSBuild]::EnsureTrailingSlash($(MSBuildProjectDirectory)))))"
The item metadata "%(FullPath)" cannot be applied to the path "Assets\Fonts...cp e:\KZTEK\...".
Path: ... exceeds the OS max path limit. The fully qualified file name must be less than 260 characters.
```
Lỗi xảy ra vì `<AvaloniaResource Include="Assets\**" />` trong `.csproj` glob tất cả file trong `Assets/`, bao gồm cả 5 file rác này, và MSBuild cần expand `%(FullPath)` cho từng item — path quá dài (>260 ký tự) làm crash bước evaluate project, chặn TOÀN BỘ build (không chỉ warning).

`git status` cũng hiển thị các file này dưới dạng escaped octal (`\357\200\242...`) — dễ bị bỏ qua vì trông giống rác vô hại, không ai để ý xóa.

## Nguyên nhân gốc rễ (Root Cause)

1. Lệnh `cp` (hoặc PowerShell `Copy-Item`) chạy với đường dẫn có khoảng trắng nhưng KHÔNG được quote đúng cách trong ngữ cảnh Bash-on-Windows → shell parse sai, toàn bộ dòng lệnh (kể cả từ khóa `cp`, cờ, path đích) bị ghép thành 1 argument và trở thành TÊN FILE thay vì được thực thi như câu lệnh.
2. NTFS chấp nhận gần như mọi ký tự trong tên file (kể cả `:`, khoảng trắng, một số ký tự điều khiển được auto-map sang PUA) — nên lệnh sai không báo lỗi rõ ràng, chỉ âm thầm tạo ra file/thư mục có tên siêu dài.
3. Path vượt 260 ký tự (MAX_PATH cổ điển của Windows) khiến các Win32 API thông thường (`os.remove`, `File.Delete`, Explorer, thậm chí `git rm`) không thao tác được trực tiếp — phải dùng extended-length path prefix `\\?\`.

## Giải pháp

1. Xác định file rác: `git status --short` trong thư mục project, tìm dòng có tên chứa escape sequence lạ hoặc quá dài (VD `\357\200\242...`).
2. Liệt kê chính xác bằng Python (không dùng `ls`/`find` vì path quá dài làm shell hiển thị sai):
   ```python
   import os
   for name in os.listdir(target_dir):
       print(len(name), ascii(name[:30]))
   ```
3. Xóa bằng Python với extended-length path prefix (`\\?\` + absolute path) — bắt buộc vì path gốc vượt MAX_PATH:
   ```python
   full = "\\\\?\\" + target_dir + "\\" + name
   os.remove(full)   # hoặc os.rmdir(full) nếu là thư mục
   ```
   Lưu ý: KHÔNG `print(name)` trực tiếp trên Windows console (code page cp1252) — sẽ crash `UnicodeEncodeError` vì ký tự PUA không encode được. Dùng `ascii(name[:20])` hoặc in theo index thay vì in nguyên tên.
4. Build lại để xác nhận lỗi MSBuild path-length đã hết.

## Áp dụng lại (How to reuse)

- Khi thấy lỗi MSBuild "exceeds the OS max path limit" hoặc "Cannot expand metadata in expression" liên quan `%(FullPath)` → nghi ngay có file rác tên siêu dài trong thư mục bị glob (`Assets/**`, `**/*.cs`...), KHÔNG phải lỗi cấu hình project.
- Trước khi chạy bất kỳ lệnh copy file nào (`cp`, `Copy-Item`, `robocopy`) có đường dẫn chứa khoảng trắng trên Windows/Git Bash: LUÔN quote toàn bộ path bằng dấu ngoặc kép, và verify ngay sau đó bằng `ls`/`git status` xem file đích có đúng tên mong đợi không — đừng giả định lệnh chạy thành công chỉ vì exit code 0.
- Nếu `os.remove`/`rm` báo "cannot find path specified" dù `os.listdir` thấy file đó → thử ngay với prefix `\\?\` (extended-length path) trước khi kết luận file "ma".

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ `git status --short` hiển thị tên file lạ dưới dạng escaped octal — đừng bỏ qua, đó là dấu hiệu path bị hỏng.
- ⚠️ `os.path.isfile()`/`isdir()` trả về `False` cho các path vượt MAX_PATH dù file thực sự tồn tại (`os.listdir` thấy được) — đừng dùng kết quả đó để quyết định có xóa hay không, cứ thử `os.remove` với `\\?\` trước.
- ⚠️ In tên file chứa ký tự Private Use Area ra console Windows (cp1252) sẽ crash script — luôn `ascii()`-hoá trước khi print khi debug loại lỗi này.

## Tham chiếu

- Project liên quan: `iPGSv4` — `IPGS.Kiosk.Avalonia/Assets/Fonts` (phát sinh từ task 2.A3 trong plan `PLAN-migrate-ipgs-kiosk-avalonia-2026-07-20`)
