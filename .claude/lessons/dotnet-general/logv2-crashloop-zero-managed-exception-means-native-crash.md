---
category: dotnet-general
tags: [crash-diagnosis, sqlite-log, unhandled-exception, native-crash, avalonia, p-invoke]
severity: critical
created: 2026-08-11
updated: 2026-08-11
project-origin: ParkingV8 Avalonia (parking-v8-app-avalonia)
---

# App văng liên tục (32 lần/26h) nhưng DB log không có 1 dòng exception nào → dấu hiệu crash native, không phải managed exception

## Tình huống gặp phải

User đưa file `logv2.db` (SQLite log app) của app Avalonia ParkingV8 để tìm nguyên nhân
app "thường xuyên bị văng" — biết được app restart vì thấy log `Application Start` xuất
hiện lại. Cần xác định nguyên nhân crash từ log.

## Triệu chứng / Lỗi

- `tblSystemLog` có 32 dòng `Application Start` trong ~26 giờ (10/8 11:28 → 11/8 13:07),
  nhiều lần cách nhau chỉ 6–90 giây → rõ ràng là crash-loop, không phải người dùng tắt/mở
  máy chủ động.
- Trước MỖI lần crash, dòng log cuối cùng luôn là hoạt động nghiệp vụ bình thường
  (card event, gọi API, lưu ảnh camera) — **không có bất kỳ dòng Ex/exception nào ngay
  trước thời điểm văng**.
- Code (`App.axaml.cs`) ĐÃ đăng ký đủ 3 global exception hook:
  `AppDomain.CurrentDomain.UnhandledException`, `TaskScheduler.UnobservedTaskException`,
  `Dispatcher.UIThread.UnhandledException` — mỗi hook đều gọi `AppLogService.Error(...)`.
- Nhưng query `SELECT COUNT(*) FROM tblSystemLog WHERE Description LIKE '%UnhandledException%'`
  trả về **0** — suốt 32 lần crash, không hook nào từng ghi log.

## Nguyên nhân gốc rễ (Root Cause)

Khi cả 3 managed exception hook đã đăng ký đúng nhưng **0 lần fire** dù app crash liên tục,
kết luận gần như chắc chắn: crash xảy ra ở tầng **native/unmanaged**, không phải managed
.NET exception. Các loại lỗi native mà `AppDomain.UnhandledException` **không bao giờ**
bắt được (theo thiết kế CLR, kể cả khi hook đã đăng ký đúng):

- `AccessViolationException` / native access violation từ code P/Invoke (camera SDK,
  FFmpeg native DLL, LED SDK) — kể từ .NET Core, các exception "corrupted state" này giết
  process ngay, managed handler không chạy.
- `StackOverflowException` — luôn terminate process ngay lập tức, không handler nào chạy.
- OS-level kill (Access Violation ở driver, GPU crash, native heap corruption) — process
  chết mà không qua managed runtime.

App này dùng nhiều điểm P/Invoke rủi ro: `ANV.Cameras.PINVOKE` (camera SDK), FFmpeg native
DLL (`FFmpegLoader.Init()` + `avformat_network_init()` chạy trên background thread ngay khi
app khởi động), LED SDK Huidu (`CSDKExport.cs`). Đây là các nghi phạm hàng đầu.

## Giải pháp

1. **Đừng tốn thời gian đọc thêm app-level log (SQLite/file) để tìm root cause** — log
   managed sẽ KHÔNG BAO GIỜ chứa nguyên nhân native crash, vì crash xảy ra trước khi bất kỳ
   dòng code C# nào (kể cả exception handler) có cơ hội chạy.
2. Bật **Windows Error Reporting (WER) LocalDumps** để bắt crash dump thật:
   ```
   HKLM\SOFTWARE\Microsoft\Windows\Windows Error Reporting\LocalDumps
   DumpFolder = C:\CrashDumps
   DumpType = 2   (full dump)
   ```
   hoặc dùng `procdump -ma -e -w ParkingV8.App.exe C:\CrashDumps` chạy nền.
3. Sau khi có `.dmp`, mở bằng WinDbg (`!analyze -v`) để xem **faulting module** — nếu là
   `ffmpeg*.dll`, `ANV.Cameras*.dll`, hoặc driver camera/LED → xác nhận đúng nghi phạm.
4. Đối chiếu Windows Event Viewer → Application log → tìm event id 1000 (Application
   Error) hoặc .NET Runtime event có "Faulting module" đúng thời điểm timestamp
   `Application Start` kế tiếp trong `logv2.db` (crash luôn xảy ra ngay TRƯỚC dòng
   `Application Start` mới).
5. Nếu xác nhận là camera/FFmpeg: cách ly camera decode/capture ra process con
   (out-of-process) để 1 crash native chỉ giết process con, không kéo sập cả app UI.

## Áp dụng lại (How to reuse)

- Khi debug "app tự văng, restart lại" từ SQLite/file log: luôn kiểm tra trước —
  **có managed exception nào được log ngay trước lần restart không?** Nếu KHÔNG một lần nào
  trong nhiều chục lần crash → dừng đào log app-level ngay, chuyển sang tìm crash dump/Event
  Viewer vì đây là crash native.
- Cách kiểm tra nhanh: `SELECT COUNT(*) FROM <log_table> WHERE Description LIKE
  '%UnhandledException%'` — so với tổng số lần restart. Nếu 0/N → native crash.
- Ưu tiên nghi ngờ mọi P/Invoke / native SDK (camera, LED, FFmpeg, driver) khi app có các
  điểm này và crash không rõ nguyên nhân.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Đăng ký đủ `AppDomain.UnhandledException` + `TaskScheduler.UnobservedTaskException` +
  `Dispatcher.UIThread.UnhandledException` **KHÔNG** đảm bảo bắt được mọi loại crash — vẫn có
  lỗ hổng với native crash / StackOverflow / corrupted-state exception. Không nên coi 3 hook
  này là "lưới an toàn hoàn chỉnh".
- ⚠️ `Dispatcher.UIThread.UnhandledException` với `e.Handled = true` chỉ nuốt được exception
  ném từ UI thread quản lý bởi Avalonia dispatcher — không áp dụng cho exception/crash từ
  native callback thread do camera SDK tạo ra ngoài dispatcher.
- ⚠️ Log chỉ ra các lần crash không đều tần suất — có lúc crash sau loạt lỗi mạng timeout
  (`TaskCanceledException` gọi API), nhưng đây có thể là correlation ngẫu nhiên (app đang
  bận network) không phải nguyên nhân trực tiếp — cần crash dump để xác nhận thay vì suy diễn
  từ log business.

## Tham chiếu

- Project: `parking-v8-app-avalonia` — `src/ParkingV8.App/App.axaml.cs` (RegisterGlobalExceptionLogging)
- File log đã phân tích: `logv2.db` (`tblSystemLog`, `tblAPILog`)
