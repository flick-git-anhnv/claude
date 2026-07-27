---
category: avalonia
tags: [config-tool, ux-gap, chicken-egg-bug, loading-window, sql-config]
severity: high
created: 2026-07-24
updated: 2026-07-24
project-origin: iPGSv4 (IPGSUseCam)
---

# LoadingWindow báo lỗi kết nối rồi chỉ có nút "Đóng" — không có đường mở tool sửa config

## Tình huống gặp phải

> Đang làm gì? Tính năng gì? Môi trường nào?

Sau khi fix `avalonia-config-tool-crash-on-corrupted-password.md` (ApplicationConfig tool không còn crash khi Password hỏng), user vẫn báo "không được" và gửi screenshot: cửa sổ `LoadingWindow` (app chính IPGSUseCam) hiện "Không Kết Nối Được Đến SQL Server." với DUY NHẤT nút "Đóng". Hóa ra yêu cầu gốc "không mở được app config" không phải (chỉ) nói về việc ApplicationConfig tự crash, mà còn nói về việc từ màn hình lỗi của app chính, KHÔNG CÓ CÁCH NÀO để mở tool cấu hình lên sửa — bấm "Đóng" chỉ thoát hẳn ứng dụng.

## Triệu chứng / Lỗi

`IPGSUseCam/Views/LoadingWindow.axaml` chỉ có 1 button `PART_Close` ("Đóng") ở footer, không có button nào khác. `ShowError()` trong `LoadingWindow.axaml.cs` chỉ set `_closeBtn.IsVisible = true`. Khi SQL/Parking/LPR config sai hoặc thiếu, user bị kẹt ở màn hình loading với lựa chọn duy nhất là đóng app — không có lối vào ApplicationConfig để sửa.

## Nguyên nhân gốc rễ (Root Cause)

Thiết kế `LoadingWindow` chỉ tính đến 2 trạng thái: loading thành công hoặc lỗi + đóng. Không có nhánh "lỗi do config → mở tool sửa config → thử lại". Đây không phải bug logic (không throw, không crash) mà là **UX gap** — thiếu 1 action đường-thoát-đúng cho tình huống rất hay gặp lúc setup máy mới hoặc đổi config.

Điểm thuận lợi phát hiện được: `IPGSUseCam.csproj` đã có sẵn `<ProjectReference Include="..\ApplicationConfig\ApplicationConfig.csproj" />`, và `ConfigPathManagement.baseBath` đã được set 1 lần trong `IPGSUseCam/Program.cs` (`Main()`) — vì `ConfigPathManagement` là class tĩnh dùng chung namespace `ApplicationConfig.Objects`, path config giống hệt nhau giữa 2 app. Nghĩa là có thể **new trực tiếp `ApplicationConfig.Views.MainWindow()` trong process của IPGSUseCam**, không cần Process.Start ra file .exe riêng (tránh phải dò đường dẫn exe, tránh 2 tiến trình chạy song song).

## Giải pháp

```csharp
// LoadingWindow.axaml — thêm nút "Mở Cấu Hình" cạnh "Đóng" trong footer, IsVisible="False" mặc định
<Button x:Name="PART_OpenConfig" IsVisible="False" Content="Mở Cấu Hình" Width="120" Height="36" />

// LoadingWindow.axaml.cs
private async void OnOpenConfigClick(object? sender, RoutedEventArgs e)
{
    var configWindow = new ApplicationConfig.Views.MainWindow();
    await configWindow.ShowDialog(this);

    // Sau khi đóng cửa sổ config, reset UI và thử tải lại từ đầu
    ...
    await RunLoadingTasksAsync();
}
```

1. Thêm button `PART_OpenConfig` trong AXAML, ẩn mặc định giống `PART_Close`.
2. `ShowError()` hiện CẢ HAI button (`_closeBtn` và `_openConfigBtn`), không chỉ 1.
3. Click "Mở Cấu Hình" → mở `ApplicationConfig.Views.MainWindow` bằng `ShowDialog(this)` (đã sẵn ProjectReference, không cần launch process ngoài).
4. Sau khi user lưu và đóng cửa sổ config → tự động gọi lại `RunLoadingTasksAsync()` để retry, không bắt user phải tự khởi động lại cả app.

## Áp dụng lại (How to reuse)

- Khi user báo "không mở được app config" / "không sửa được config" trong ngữ cảnh 1 app CHÍNH (không phải bản thân tool config) — luôn kiểm tra 2 khả năng riêng biệt, đừng dừng ở khả năng đầu:
  1. Bản thân tool config bị crash khi mở (lỗi bên trong tool).
  2. App chính không có đường dẫn/nút để MỞ tool config khi phát hiện lỗi cấu hình (UX gap, không phải bug).
- Trước khi launch 1 tool con bằng `Process.Start(exePath)`, kiểm tra xem có `ProjectReference` sẵn không — nếu 2 project đã reference nhau và dùng chung 1 class quản lý path config tĩnh (`ConfigPathManagement.baseBath`), có thể `new Window()` thẳng trong cùng process, đơn giản hơn, không phải lo tìm đường dẫn exe, không có 2 tiến trình song song tranh chấp file config.
- Sau khi sửa xong 1 chỗ bị "chặn không mở được", luôn hỏi lại: hành động ĐÓ có thực sự tương ứng với TRIỆU CHỨNG user nhìn thấy trên UI không (xin screenshot nếu mơ hồ), đừng chỉ tin vào suy luận code-only.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Đừng launch `ApplicationConfig.exe` bằng `Process.Start` nếu đã có `ProjectReference` — sẽ tạo 2 tiến trình có thể ghi đè file config của nhau, và phải tự dò đường dẫn exe (dễ sai khi publish/deploy khác cấu trúc thư mục).
- ⚠️ `ConfigPathManagement.baseBath` là `static` toàn cục — nếu tool con và app chính chạy trong CÙNG process (như cách làm ở đây), chỉ cần set 1 lần là đủ cho cả 2; nhưng nếu tách process riêng thì mỗi process phải tự set lại (đã đúng ở cả `ApplicationConfig/App.axaml.cs` và `IPGSUseCam/Program.cs`).
- ⚠️ Sau khi user sửa config qua dialog và đóng lại, phải chủ động reset UI (ẩn error, hiện lại progress indeterminate) trước khi gọi lại `RunLoadingTasksAsync()` — nếu không, các control cũ (`_error.IsVisible=true`, `_closeBtn.IsVisible=true`) vẫn còn hiển thị chồng lên trạng thái loading mới.

## Tham chiếu

- File: `IPGSUseCam/Views/LoadingWindow.axaml`, `IPGSUseCam/Views/LoadingWindow.axaml.cs`
- Liên quan: `avalonia/avalonia-config-tool-crash-on-corrupted-password.md` (bug crash bên trong ApplicationConfig — fix trước đó trong cùng yêu cầu của user)
- Project liên quan: iPGSv4 (nhánh zcu-avalonia)
