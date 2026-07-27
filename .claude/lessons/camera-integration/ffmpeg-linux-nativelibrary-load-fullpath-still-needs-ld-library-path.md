---
category: camera-integration
tags: [ffmpeg, linux, nativelibrary, ld_library_path, dlopen, dynamic-linker, avalonia]
severity: high
created: 2026-07-25
updated: 2026-07-25
project-origin: LinuxDeployTool / iPGSv4 (IPGS.Kiosk.Avalonia, IPGSUseCam) — thư viện Kztek.Cameras.Avalonia
---

# `NativeLibrary.Load(fullpath)` nạp được lib FFmpeg đầu tiên, nhưng video/camera vẫn không chạy — thiếu LD_LIBRARY_PATH cho dependency NỘI BỘ giữa các .so

## Tình huống gặp phải

> Build `.deb` qua WSL cho `IPGS.Kiosk.Avalonia`/`IPGSUseCam` (dùng camera qua FFmpeg P/Invoke, thư viện dùng chung `Kztek.Cameras.Avalonia`). File `.so` FFmpeg (`libavformat.so`, `libavcodec.so`...) đã có đầy đủ trong `Players/FFMPEG/Resource/` bên trong `.deb` — nhưng khi cài và chạy trên Linux thật, xem video/camera không hoạt động.

## Triệu chứng / Lỗi

Không có exception rõ ràng ở tầng .NET (resolver `FFmpegLoader` trả về handle "thành công" cho lib đầu tiên nó nạp). Chỉ khi chạy `ldd` trực tiếp trên `.so` mới thấy:

```
$ ldd libavformat.so
	libavcodec.so.62 => not found
	libavutil.so.60 => not found
```

## Nguyên nhân gốc rễ (Root Cause)

`FFmpegLoader.cs` (custom `NativeLibrary.SetDllImportResolver`) nạp file FFmpeg **đầu tiên** bằng `NativeLibrary.Load(fullpath)` — dùng path tuyệt đối (`AppContext.BaseDirectory + "/Players/FFMPEG/Resource/libavformat.so"`), nên bước NÀY không phụ thuộc `LD_LIBRARY_PATH` chút nào, luôn thành công nếu file tồn tại.

NHƯNG các file FFmpeg `.so` này **phụ thuộc lẫn nhau** ở tầng ELF (`libavformat.so` có `NEEDED libavcodec.so.62`, `libavcodec.so` cần `libavutil.so.60`...). Khi CLR gọi `dlopen()` cho `libavformat.so`, glibc's dynamic linker (`ld.so`) tự động phải resolve các `NEEDED` entry đó — và `ld.so` **CHỈ tìm theo `LD_LIBRARY_PATH`/`RPATH`/`RUNPATH` embedded trong .so/system path (`/etc/ld.so.cache`, `/lib`, `/usr/lib`)**, KHÔNG hề biết (và không quan tâm) thư mục mà `dlopen()` vừa dùng để mở file `libavformat.so` là gì. Đây là 2 cơ chế hoàn toàn tách biệt: (1) tìm file lib chính — do code C# tự làm bằng full path; (2) resolve dependency NEEDED của lib đó — do `ld.so` làm, ngoài tầm kiểm soát của .NET.

Kết quả: bước (1) "thành công" (không throw), nhưng lib vừa nạp không dùng được vì thiếu symbol/dependency, hoặc process treo/lỗi khi thực sự gọi hàm FFmpeg — rất khó chẩn đoán vì không có exception .NET rõ ràng để lần theo.

## Giải pháp

1. Thêm thư mục chứa các `.so` FFmpeg vào `LD_LIBRARY_PATH` **trước khi** app khởi động — nơi đúng để làm việc này là launcher script (`run.sh`), KHÔNG phải trong code C#:
   ```bash
   export LD_LIBRARY_PATH="$DIR:$DIR/Players/FFMPEG/Resource:$LD_LIBRARY_PATH"
   ```
2. Verify bằng `ldd` trực tiếp trên từng `.so` chính (không chỉ chạy thử app và đoán) — set `LD_LIBRARY_PATH` thủ công rồi `ldd libavformat.so`, xác nhận không còn dòng `not found` nào, TRƯỚC khi coi là đã fix xong.
3. Không sửa `FFmpegLoader.cs` (code C#) — bước (1) của nó đã đúng, vấn đề nằm ở launcher script thiếu biến môi trường cho bước (2).

## Áp dụng lại (How to reuse)

- Bất kỳ khi nào app .NET nạp `.so` bằng `NativeLibrary.Load(fullpath)` (hoặc `dlopen` full path) mà lib đó thuộc 1 họ có nhiều file phụ thuộc lẫn nhau (FFmpeg, OpenCV, camera SDK...) → PHẢI đảm bảo `LD_LIBRARY_PATH` bao gồm thư mục chứa TOÀN BỘ họ lib đó, không chỉ tin rằng "load thành công lib đầu = mọi thứ ổn".
- Chẩn đoán "video/camera không chạy trên Linux nhưng không rõ lỗi gì" → luôn `ldd <file.so chính>` trước tiên để xem thiếu dependency nào, đây là công cụ chẩn đoán nhanh nhất, đáng tin hơn đọc log app.
- Khi review launcher script (`run.sh`) của app có dùng native lib đóng gói theo nhiều thư mục con (không phải tất cả nằm cùng cấp với binary chính) → kiểm tra `LD_LIBRARY_PATH` có liệt kê ĐỦ mọi thư mục con chứa `.so`, không chỉ thư mục gốc.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Comment cũ trong `FFmpegLoader.cs` ghi "CHƯA có file .so nào được đóng gói trong repo (D13 ADR — out-of-scope)" — đã lỗi thời từ khi ai đó bổ sung `.so` thật vào `Resource/` (2026-06-23) mà không cập nhật comment. Luôn nghi ngờ comment "chưa làm X" khi thấy file X đã tồn tại trên đĩa — đối chiếu thực tế trước khi tin comment.
- ⚠️ `dpkg-deb`/build .deb đóng gói đủ file `.so` không có nghĩa app chạy được — file có mặt (build-time) và file load được đúng cách (runtime, qua `ld.so`) là 2 việc khác nhau, phải verify riêng từng cái.
- ⚠️ Cùng bug lặp lại y hệt ở 2 project độc lập dùng chung thư viện `Kztek.Cameras.Avalonia` (`IPGS.Kiosk.Avalonia` và `IPGSUseCam`) — mỗi project có `run.sh` riêng (không dùng chung 1 file), nên fix 1 chỗ KHÔNG tự động fix chỗ kia; phải rà tất cả project dùng chung thư viện khi tìm thấy bug kiểu này.

## Tham chiếu

- Project liên quan: `IPGS.Kiosk.Avalonia/deploy-linux/run.sh`, `IPGSUseCam/deploy-linux/run.sh`
- Thư viện liên quan: `0.BaseLIB/Kztek.Camera/.../Kztek.Cameras.Avalonia/Players/FFMPEG/PINVOKE/FFmpegLoader.cs`
- Lesson liên quan: [wsl-required-for-linux-native-tools-not-git-bash.md](../dotnet-general/wsl-required-for-linux-native-tools-not-git-bash.md)
