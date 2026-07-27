---
category: dotnet-general
tags: [msbuild, git-merge, obj-folder, build-error]
severity: medium
created: 2026-07-18
updated: 2026-07-18
project-origin: IPGSv1
---

# MSB3541 "Files has invalid value" do file cache obj/*.FileListAbsolute.txt sót conflict marker git

## Tình huống gặp phải

> Build lại solution `iParkingPGS.sln` (IPGSv1, .NET Framework WinForms) sau khi
> chỉnh code (không đụng .csproj) bằng `MSBuild.exe /t:Build` để verify thay đổi.

## Triệu chứng / Lỗi

```
Microsoft.Common.CurrentVersion.targets(5708,5): error MSB3541:
Files has invalid value "<<<<<<< HEAD". Illegal characters in path.
[...\ApplicationConfig.csproj]
```
Lỗi trỏ vào `.csproj` nhưng bản thân `.csproj` không hề chứa `<<<<<<<`.

## Nguyên nhân gốc rễ (Root Cause)

Marker conflict nằm trong file **cache incremental build** —
`obj\Debug\<ProjectName>.csproj.FileListAbsolute.txt` — không phải trong `.csproj`
nguồn. File này là danh sách output file tuyệt đối MSBuild tự sinh để track
incremental clean/copy; nó bị commit ở trạng thái conflict marker chưa resolve
(rất có thể từ 1 lần merge cũ, do `obj/` không được `.gitignore` đúng cách trong
project này). Task `Copy`/`GetCopyToOutputDirectoryItems` của MSBuild đọc file này
làm input Items và coi dòng `<<<<<<< HEAD` như 1 "file path" → path chứa ký tự bất
hợp lệ → MSB3541. Lỗi xảy ra ở CẢ project phụ thuộc (`ApplicationConfig`) lẫn
project chính (`iParkingPGS`) — mỗi project có file `obj/Debug/*.FileListAbsolute.txt`
riêng, phải kiểm tra hết.

## Giải pháp

```bash
grep -rln "<<<<<<<" --include="*.txt" .    # tìm hết các file obj/*.FileListAbsolute.txt bị dính
rm "obj/Debug/<ProjectName>.csproj.FileListAbsolute.txt"   # xóa an toàn — MSBuild tự sinh lại
```

1. `grep -rln "<<<<<<<"` trong toàn bộ thư mục `obj/` của các project trong solution.
2. Xóa từng file `*.FileListAbsolute.txt` bị dính marker (an toàn 100%, đây là file
   cache tự sinh, không phải source, không track thủ công).
3. Build lại — MSBuild tự tạo lại file cache mới, sạch.

## Áp dụng lại (How to reuse)

- Khi gặp `MSB3541: Files has invalid value "<<<<<<< HEAD"` (hoặc `=======`,
  `>>>>>>>`) → đừng tìm trong `.csproj`, tìm trong `obj/**/*.FileListAbsolute.txt`
  của TẤT CẢ project trong solution (kể cả project không phải project đang sửa).
- Trước khi build để verify 1 thay đổi code, nếu build lỗi liên quan path/file lạ
  không match với thay đổi vừa làm → nghi ngờ ngay file cache `obj/`/`bin/` cũ,
  không phải lỗi do code mới.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Đừng xóa nhầm `.csproj` hay file source khi thấy path lỗi trong message —
  message chỉ path *chứa* Items bị lỗi (project sở hữu), không phải file thực sự
  có nội dung `<<<<<<< HEAD`.
- ⚠️ Nếu `obj/`/`bin/` bị track trong git (dấu hiệu: `git status` thấy hàng loạt
  file `.dll`/`.cache`/`.txt` trong `obj/Debug`), nên đề xuất thêm `.gitignore`
  cho các thư mục này để tránh tái diễn — nhưng đây là thay đổi ngoài phạm vi 1
  bugfix nhỏ, cần hỏi ý kiến user trước khi sửa `.gitignore`/xóa hàng loạt file
  tracked.

## Tham chiếu

- Project liên quan: IPGSv1 (`PGS_4_number/iParkingPGS/`)
- Liên quan: [[kz-led-p5-udp-outdoor-integration]]
