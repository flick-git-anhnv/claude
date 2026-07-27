---
category: avalonia
tags: [appstate, config, logo, wiring-gap, silent-failure]
severity: high
created: 2026-07-22
updated: 2026-07-22
project-origin: iPGSv4 (KIOSK VERTICAL — LocationAndPayment)
---

# `AppState.LogoPath/SubLogoPath/AdsPath` chưa từng được gán trong `App.axaml.cs` — logo luôn trống trên MỌI màn hình

## Tình huống gặp phải

User báo bug "thiếu logo" trên màn hình `MotorInforDetailView` (kiosk vertical, port từ WinForms `frmMotorInforDetail`). Code-behind các view (`CarInforDetailView.axaml.cs`, `MotorInforDetailView.axaml.cs`, ...) đều có logic đúng:
```csharp
if (File.Exists(AppState.SubLogoPath))
{
    var bmp = new Avalonia.Media.Imaging.Bitmap(AppState.SubLogoPath);
    ImgLogo.Source = bmp;
}
```

## Triệu chứng / Lỗi

Logo không hiển thị (khoảng trống trắng phía trên đồng hồ), không có exception, không có log lỗi nào xuất hiện (vì `File.Exists("")` chỉ trả `false`, code âm thầm bỏ qua — không rơi vào nhánh `catch`).

## Nguyên nhân gốc rễ (Root Cause)

`AppState.cs` khai báo `LogoPath`, `SubLogoPath`, `AdsPath` với comment "load từ appsettings hoặc tblKioskConfig" / "Set từ KioskAppConfig khi App.axaml.cs khởi động" — nhưng khi grep thực tế `App.axaml.cs`, KHÔNG có bất kỳ dòng nào gán 3 property này từ `kioskConfig` (trong khi các field khác như `IsShowInvoiceForm`, `ParkingApiUrl`, `VisaPosId`, `QrPosId`... đều được wire đầy đủ ở cùng vị trí). `KioskAppConfig.cs` có sẵn `MainLogoPath`/`SubLogoPath`/`AdsPath` (đọc đúng từ config.txt) nhưng dữ liệu chưa bao giờ được copy sang `AppState` — nghĩa là **MỌI view** trong toàn bộ app (không riêng gì Car/MotorInforDetail) đều nhận `AppState.SubLogoPath == string.Empty` mặc định, logo luôn trống. Đây là lỗ hổng "bỏ sót dòng wiring" — 3 dòng code không tồn tại, không phải logic sai.

## Giải pháp

```csharp
// App.axaml.cs, ngay sau khi kioskConfig được load (cạnh các dòng AppState.* khác)
AppState.LogoPath = kioskConfig.MainLogoPath;
AppState.SubLogoPath = kioskConfig.SubLogoPath;
AppState.AdsPath = kioskConfig.AdsPath;
```

1. Grep `AppState\.\w+\s*=` trong `App.axaml.cs` để liệt kê field nào ĐÃ wire.
2. Đối chiếu với toàn bộ property khai báo trong `AppState.cs` có comment "set từ KioskAppConfig" → field nào thiếu trong danh sách Bước 1 là field chưa wire.
3. Thêm dòng gán còn thiếu, đặt cạnh nhóm gán liên quan (asset paths) để dễ maintain.

## Áp dụng lại (How to reuse)

- Khi 1 UI element bind vào `AppState.X` mà luôn rỗng/mặc định dù chắc chắn app đã đọc config đúng (`kioskConfig.X` có giá trị) → **grep ngay** `AppState\.X\s*=` trong `App.axaml.cs`/entry point — khả năng cao là thiếu dòng wiring, không phải lỗi UI/binding.
- Comment kiểu "Set từ Y khi Z khởi động" trong file model/state KHÔNG PHẢI bằng chứng code đã làm việc đó — luôn verify bằng grep thực tế trước khi tin.
- Bug loại này silent hoàn toàn (không exception, build PASS, không log) — chỉ phát hiện được qua kiểm tra UI trực quan (đúng lý do CLAUDE.md §4 yêu cầu UX/UI Reviewer chạy app thật sau mỗi thay đổi giao diện).

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Đừng chỉ fix cho 1 view đang bị báo lỗi ("MotorInforDetailView thiếu logo") — root cause nằm ở tầng `App.axaml.cs` toàn cục, ảnh hưởng TẤT CẢ view dùng `AppState.SubLogoPath`/`LogoPath`/`AdsPath`. Sửa đúng 1 chỗ (App.axaml.cs) là đủ, KHÔNG cần sửa từng view.
- ⚠️ Trước khi kết luận "logo không hiển thị vì file ảnh không tồn tại trên máy" (lỗi data/config), luôn kiểm tra code wiring trước — dễ nhầm lẫn 2 loại nguyên nhân khác nhau (thiếu wiring vs. thiếu file thật).

## Tham chiếu

- Project liên quan: iPGSv4 — `IPGS.Kiosk.Avalonia\App.axaml.cs`, `IPGS.Kiosk.Avalonia\Services\AppState.cs`, `IPGS.Kiosk.Avalonia\Models\KioskAppConfig.cs`
