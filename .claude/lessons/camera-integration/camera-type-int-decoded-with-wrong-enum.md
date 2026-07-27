---
category: camera-integration
tags: [enum-ordinal, camera-type, rtsp, silent-mismatch, avalonia]
severity: critical
created: 2026-07-16
updated: 2026-07-16
project-origin: parking-v8-app-avalonia (KZTEK IPARKING v8 Avalonia)
---

# Camera.Type (int) bị decode nhầm bằng SAI enum → build sai RTSP URL, không bao giờ Live

## Tình huống gặp phải

Đang fix bug user báo: trong `LaneSettingsWindow` (màn hình cấu hình lane, tab Camera), camera cấu hình kiểu "Custom" (host là URL/đường dẫn tuỳ ý, không phải IP hãng camera chuẩn) đứng mãi ở trạng thái "Connecting" và không bao giờ lên "Live" — nhưng **cùng camera đó lại live bình thường ở màn hình chính (lane monitoring / "outside")**. Cả 2 màn hình dùng chung 1 control `CameraView` (Avalonia UI, `ParkingV8.UI/Controls/Cs/CameraView.axaml.cs`) và chung 1 camera engine (`Kztek.Cameras.Camera`), nên ban đầu nghi ngờ control/engine — nhưng nếu bug nằm ở engine thì phải fail ở CẢ 2 nơi.

## Triệu chứng / Lỗi

- UI hiện badge "Connecting" mãi, sau 25s watchdog chuyển "Waiting Frame" (`CameraView.axaml.cs` watchdog timeout).
- KHÔNG có exception, KHÔNG có log lỗi rõ ràng — vì code không "crash", nó chỉ build nhầm URL và cố kết nối tới 1 endpoint sai/không tồn tại.
- Chỉ xảy ra ở 1 màn hình cụ thể (LaneSettingsWindow), không xảy ra ở màn hình chính dùng cùng control.

## Nguyên nhân gốc rễ (Root Cause)

Codebase có **3 bảng mã hoá "loại camera" khác nhau, cùng dùng số int nhưng thứ tự member KHÁC NHAU**:

1. `iParkingv8.Object.Objects.Devices.Camera.GetCameraType()` (`src/Kztek.Object.MultyPlatform/LegacyiParkingv8/Objects/Devices/Camera.cs`) — bảng **legacy DB gốc**: `0=SECUS,1=SHANY,2=BOSCH,3=VANTECH,4=CNB,5=HIK,6=ENSTER,7=DAHUA,8=HANSE,9=TIANDY,10=DMAX,11=VIVANTEK,12=HANET,13=CUSTOM,14=PELCO,15=AVIGILON,16=ZKTECO`. Đây là bảng **THẬT SỰ dùng để lưu `camera.Type` trong DB** — nguồn chân lý duy nhất để decode int này.
2. `Kztek.Cameras.CameraType` (enum trong project nguồn `Kztek.Cameras.Avalonia`, dùng bởi `CameraView`) — thứ tự: `...,CNB(12),HANET(13),PELCO(14),Bosch(15),ZKteco(16),Hanwha(17),IPRO(18),Custom(19)`.
3. `Kztek.Cameras.Models.EmCameraType` (`src/ParkingV8.Camera/Models/EmCameraType.cs`, dùng bởi engine port khác) — thứ tự: `...,CNB(12),Custom(13),PELCO(14),Bosch(15),ZKteco(16),Hanwha(17),IPRO(18),HANET(19)`.

`LaneSettingsWindowViewModel.ResolveCameraType()` lấy `camera.Type` (int, encode theo bảng #1) rồi decode bằng **`Enum.GetName(typeof(Kztek.Cameras.CameraType), camera.Type)`** (bảng #2) — SAI bảng. Với `camera.Type = 13` (CUSTOM theo bảng #1), bảng #2 tại index 13 lại là `HANET` → camera Custom bị biến thành camera HANET, mà `BuildHANET()` trong `CameraRtspUrlBuilderFactory.cs` **hardcode 1 URL demo cố định** (`rtsp://192.168.20.50:554/user:hanet;pwd:hanet123-main264`) — cố kết nối tới địa chỉ không tồn tại → không bao giờ nhận frame.

Trong khi đó, đường code "outside" (main lane view, `EntryLaneViewModel`) KHÔNG tự decode int — nó dùng lại chuỗi `LaneCameraModel.CameraType` đã được `AppStartupLoader.cs` set 1 lần duy nhất bằng `camera.GetCameraType()` (bảng #1, đúng) rồi truyền chuỗi này xuyên suốt. Đây là lý do bug CHỈ xuất hiện ở 1 màn hình — màn hình đó tự ý decode lại từ int bằng sai bảng thay vì tái sử dụng chuỗi đã đúng.

## Giải pháp

```csharp
// SAI (cross-decode 2 enum khác thứ tự):
return camera.Type switch
{
    >= 0 and <= 24 => Enum.GetName(typeof(Kztek.Cameras.CameraType), camera.Type) ?? fallback ?? "Tiandy",
    _ => string.IsNullOrWhiteSpace(fallback) ? "Tiandy" : fallback,
};

// ĐÚNG: ưu tiên chuỗi đã persist cho lane (khớp cách EntryLaneViewModel dùng),
// chỉ derive từ int khi thật sự chưa có, và derive bằng ĐÚNG decoder gốc (GetCameraType()):
if (!string.IsNullOrWhiteSpace(fallback))
{
    return fallback;
}
var resolved = camera.GetCameraType();
return string.IsNullOrWhiteSpace(resolved) ? "Tiandy" : resolved;
```

1. Tìm decoder "chân lý" thật sự của int (ở đây là `Camera.GetCameraType()`) — không giả định enum nào "trông có vẻ đúng thứ tự" là đúng.
2. Ưu tiên tái sử dụng chuỗi/giá trị đã được decode & persist sẵn ở nơi khác trong codebase thay vì tự decode lại từ int — giảm nguy cơ dùng nhầm bảng.
3. Build lại, xác nhận camera Custom parse ra đúng `CameraType.Custom` (không phải HANET/brand khác).

## Áp dụng lại (How to reuse)

- Khi thấy **"cùng 1 control/engine nhưng chỉ lỗi ở 1 màn hình cụ thể"** → nghi ngay **dữ liệu đầu vào khác nhau giữa 2 nơi gọi**, không phải bug ở control/engine dùng chung. Trace ngược xem 2 nơi build tham số truyền vào control có giống nhau không.
- Khi thấy code có `Enum.GetName(typeof(X), someInt)` hoặc `(X)someInt` mà `someInt` đến từ 1 field/DB column KHÔNG do chính enum `X` định nghĩa (field đặt tên chung chung như `Type`, `Kind`, `Category`) → **nghi ngờ ngay có ≥2 enum khác nhau đang bị đánh đồng theo thứ tự số** — grep toàn repo tìm các enum "loại camera/thiết bị" khác có thể trùng field này, so từng member theo index.
- Ưu tiên tìm decoder chuỗi (method như `GetXxxType()`) đã tồn tại sẵn trong model gốc thay vì tự viết switch/enum-cast mới — decoder cũ thường là nguồn chân lý (đã dùng để ghi DB).

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Nhiều enum "loại camera"/"loại thiết bị" cùng tên members giống nhau (Tiandy, Dahua, Custom, HANET...) NHƯNG thứ tự khai báo khác nhau => cùng 1 int cho ra 2 kết quả khác nhau. Đừng tin "tên enum quen mắt" — luôn kiểm tra thứ tự khai báo thật (đọc file .cs, không đoán).
- ⚠️ Lỗi này KHÔNG throw exception, KHÔNG log — chỉ biểu hiện bằng "treo mãi ở Connecting" hoặc kết nối tới sai IP/URL im lặng. Loại bug này rất dễ bị bỏ qua khi chỉ xem log lỗi.
- ⚠️ Khi 1 dự án có nhiều "camera engine" port song song (ở đây: `Kztek.Cameras.Avalonia` control-level và `ParkingV8.Camera`/`Kztek.Cameras.Models` service-level), rất dễ có 2-3 enum tương tự nhau cùng tồn tại — luôn xác định RÕ enum nào đang thực sự được dùng ở điểm decode, đừng giả định do tên type giống nhau.

## Tham chiếu

- File chứa bug: `src/ParkingV8.App/ViewModels/LaneSettingsWindowViewModel.cs` (`ResolveCameraType`)
- Bảng đúng (chân lý): `src/Kztek.Object.MultyPlatform/LegacyiParkingv8/Objects/Devices/Camera.cs` (`GetCameraType()`)
- 2 enum gây nhầm: `Kztek.Cameras.CameraType` (source project `0.BaseLIB/Kztek.Camera/.../Kztek.Cameras.Avalonia/Objects/CameraType.cs`) vs `Kztek.Cameras.Models.EmCameraType` (`src/ParkingV8.Camera/Models/EmCameraType.cs`)
- Project liên quan: parking-v8-app-avalonia — plan `.claude/plans/PLAN-lanesettings-gap-2026-07-16.md` (Bước 1.15)
