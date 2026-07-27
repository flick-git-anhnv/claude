---
category: avalonia
tags: [devtools, f12, application-lifecycle, attachdevtools]
severity: medium
created: 2026-07-15
updated: 2026-07-15
project-origin: parking-v8-app-avalonia
---

# AttachDevTools() gọi sau khi gán desktop.MainWindow → mở 2 bảng DevTools khi bấm F12 1 lần

## Tình huống gặp phải

> Đang làm gì? Tính năng gì? Môi trường nào?

Thêm Avalonia DevTools (F12) cho app ParkingV8.App (Avalonia 11.2.7, .NET 8, Windows). Trong `App.axaml.cs`, `OnFrameworkInitializationCompleted()` gán `desktop.MainWindow = new LoginWindow();` TRƯỚC, rồi mới gọi `this.AttachDevTools();` (bọc `#if DEBUG`) ngay sau đó.

## Triệu chứng / Lỗi

Bấm F12 **một lần duy nhất** trên MainShellWindow (window duy nhất đang mở, không có cửa sổ con nào khác) nhưng mở ra **2 cửa sổ "Avalonia DevTools" giống hệt nhau** chồng lên nhau (cùng nội dung Logical Tree/Application root).

## Nguyên nhân gốc rễ (Root Cause)

`Application.AttachDevTools()` (extension trong `Avalonia.Diagnostics`) làm 2 việc khi được gọi:
1. Nếu `desktop.MainWindow` đã có giá trị tại thời điểm gọi → attach DevTools handler ngay lập tức vào window đó.
2. Đồng thời subscribe vào sự kiện `Window.WindowOpenedEvent` (class handler, áp dụng cho MỌI Window sẽ mở sau này) để tự động attach cho các window mở sau.

Nếu code gán `desktop.MainWindow = new LoginWindow()` (hoặc bất kỳ window nào) **trước** khi gọi `AttachDevTools()`, window đó bị attach lần 1 ngay khi gọi (theo nhánh 1). Sau đó khi Avalonia framework thực sự gọi `window.Show()` (xảy ra sau `OnFrameworkInitializationCompleted()` return), sự kiện `WindowOpened` mới fire, và class handler (nhánh 2) attach DevTools **lần thứ 2** vào CHÍNH window đó → 1 lần F12 kích hoạt cả 2 handler → 2 cửa sổ DevTools.

## Giải pháp

```csharp
public override void OnFrameworkInitializationCompleted()
{
    // ... các bước init khác (config, localization, logger...) ...

#if DEBUG
    this.AttachDevTools();   // PHẢI gọi TRƯỚC khi gán desktop.MainWindow
#endif

    if (ApplicationLifetime is IClassicDesktopStyleApplicationLifetime desktop)
    {
        desktop.MainWindow = new LoginWindow();   // gán SAU AttachDevTools()
    }

    base.OnFrameworkInitializationCompleted();
}
```

1. Di chuyển `this.AttachDevTools()` lên **trước** dòng gán `desktop.MainWindow = ...`.
2. Khi đó tại thời điểm `AttachDevTools()` chạy, `desktop.MainWindow` vẫn còn `null` → nhánh 1 (attach ngay) không chạy, chỉ còn nhánh 2 (subscribe `WindowOpened`) → mỗi window chỉ được attach đúng 1 lần khi nó thực sự mở.

## Áp dụng lại (How to reuse)

- Khi thêm `AttachDevTools()` vào bất kỳ Avalonia app nào → LUÔN đặt lệnh này ở **đầu** `OnFrameworkInitializationCompleted()`, trước mọi dòng gán `desktop.MainWindow`.
- Nếu thấy F12 mở ra nhiều bảng DevTools giống hệt nhau (không phải nhiều cửa sổ app khác nhau) → kiểm tra ngay thứ tự gọi `AttachDevTools()` so với `desktop.MainWindow = ...` trong `App.axaml.cs`.
- Dấu hiệu nhận biết qua ảnh chụp: 2 cửa sổ "Avalonia DevTools" xếp chồng, cùng nội dung Logical Tree rỗng/giống nhau, phía sau chỉ có 1 cửa sổ app duy nhất.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Đây không phải lỗi do nhiều cửa sổ app mở cùng lúc (owned window, dialog...) — dễ nhầm hướng điều tra sang đó trước.
- ⚠️ Template mặc định của Avalonia (`dotnet new avalonia.app`) đã đặt `AttachDevTools()` trước `MainWindow = new MainWindow()` — nếu tự viết lại `App.axaml.cs` từ đầu (không dùng template) rất dễ đảo thứ tự.
- ⚠️ Lỗi chỉ xuất hiện ở luồng có gán `desktop.MainWindow` TRƯỚC khi AttachDevTools chạy — nếu app có nhiều bước chuyển window (Login → Loading → MainShell như ParkingV8), chỉ window ĐẦU TIÊN được gán lúc AttachDevTools() chạy mới bị double-attach; các window sau (LoadingWindow, MainShellWindow...) chỉ bị attach 1 lần qua `WindowOpened` bình thường.

## Tham chiếu

- Project liên quan: parking-v8-app-avalonia (`src/ParkingV8.App/App.axaml.cs`)
- Package: `Avalonia.Diagnostics` 11.2.7
