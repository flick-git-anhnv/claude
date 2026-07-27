---
category: avalonia
tags: [restart, process, config, kiosk, application-lifetime]
severity: high
created: 2026-07-22
updated: 2026-07-22
project-origin: iPGSv4 (IPGS.Kiosk.Avalonia)
---

# Avalonia không có `Application.Restart()` — port giả định sai "OS/supervisor sẽ tự mở lại app"

## Tình huống gặp phải

Migrate màn hình cấu hình kết nối (`FrmConnectionConfig` → `ConnectionConfigWindow`) từ WinForms sang Avalonia
trong `IPGS.Kiosk.Avalonia`. Bản gốc WinForms, sau khi user lưu cấu hình mới, gọi `Application.Restart()`
(`frmMain.cs`) để app tự đóng và tự mở lại ngay lập tức, áp dụng config vừa lưu.

## Triệu chứng / Lỗi

Sau khi lưu cấu hình kết nối trên bản Avalonia, app tắt hẳn và **không tự mở lại** — máy kiosk đứng màn hình đen,
phải có người vào bật tay lại ứng dụng. Không có exception, không log lỗi.

## Nguyên nhân gốc rễ (Root Cause)

Khi port, `MainView.axaml.cs` (`OnSettingClicked`) chỉ gọi `Environment.Exit(0)` sau khi lưu config, kèm comment:
"Avalonia không có Application.Restart() — clean shutdown rồi để OS/supervisor khởi động lại." Đây là **giả định
sai** — máy kiosk thực tế không chạy app dưới bất kỳ service/supervisor nào (không phải Windows Service, không có
watchdog process) tự khởi động lại executable khi nó thoát. Kết quả: `Exit(0)` = tắt hẳn, không có cơ chế nào relaunch.

## Giải pháp

Avalonia (.NET) không có API tương đương `Application.Restart()` của WinForms — phải tự implement bằng cách spawn
1 process mới trỏ đúng executable hiện tại TRƯỚC KHI thoát process cũ.

```csharp
private static void RestartApplication()
{
    try
    {
        var exePath = Environment.ProcessPath;
        if (string.IsNullOrEmpty(exePath)) return;

        Process.Start(new ProcessStartInfo(exePath)
        {
            UseShellExecute = true,
            WorkingDirectory = AppContext.BaseDirectory,
        });
    }
    catch (Exception ex)
    {
        Kztek.Tool.SystemUtils.logger?.SaveSystemLog(
            Kztek.Tool.SystemLog.CreateApplicationProccess("RestartApplication failed", ex));
    }
}
```

Gọi `RestartApplication()` NGAY TRƯỚC `Environment.Exit(0)` tại điểm code cũ chỉ gọi Exit — không đổi luồng nào khác.

1. Bước 1: Xác nhận có `Environment.ProcessPath` (hoặc `Assembly.GetExecutingAssembly().Location` fallback — pattern
   đã dùng sẵn ở `App.axaml.cs` cho `IAutostartService.Register()`).
2. Bước 2: `Process.Start(new ProcessStartInfo(exePath) { UseShellExecute = true })` — process mới độc lập.
3. Bước 3: Gọi `Environment.Exit(0)` (hoặc để flow tiếp tục shutdown) — process cũ thoát sau khi process mới đã spawn.

## Áp dụng lại (How to reuse)

- Khi thấy comment kiểu "Avalonia không có X — để OS/supervisor lo" → ĐỪNG tin giả định đó nếu không xác nhận
  môi trường deploy thật sự có supervisor (systemd service, Windows Service Recovery tab, watchdog script...).
  Với kiosk chạy app thường (không phải Windows Service), giả định này luôn sai.
- Bất kỳ chỗ nào bản WinForms gốc gọi `Application.Restart()` → khi port sang Avalonia, PHẢI thay bằng
  `Process.Start(exePath) + Environment.Exit(0)`, không được rút gọn thành chỉ `Environment.Exit(0)`.
- Grep `Application.Restart()` trong toàn bộ code WinForms gốc trước khi coi migrate 1 màn hình là xong — đây
  là dấu hiệu cần port riêng cơ chế restart, không tự nhiên có sẵn ở .NET/Avalonia.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ `UseShellExecute = true` cần thiết để `Process.Start` hoạt động đáng tin cậy trên cả Windows/Linux khi chạy
  executable trực tiếp (không qua shell script).
- ⚠️ Phải spawn process MỚI trước khi Exit process cũ — không đảo ngược thứ tự, nếu không có khoảng trống không có
  instance nào chạy (không nghiêm trọng ở đây vì rất nhanh, nhưng vẫn nên giữ đúng thứ tự để an toàn).
- ⚠️ Không cần logic "kill duplicate process" như `Program.cs` (WinForms, `StartApp:` goto label với Mutex) — vì
  process cũ tự thoát ngay sau khi spawn cái mới, không có 2 instance chạy chồng lâu dài.

## Tham chiếu

- `IPGS.Kiosk/LotteDesigns/frmMain.cs:123,157,212` — 3 chỗ gọi `Application.Restart()` bản gốc WinForms
- `IPGS.Kiosk.Avalonia/Views/MainView.axaml.cs` — `OnSettingClicked` + `RestartApplication()` (fix)
- Project liên quan: iPGSv4 (IPGS.Kiosk.Avalonia)
