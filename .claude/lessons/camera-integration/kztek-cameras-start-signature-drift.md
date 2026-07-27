---
category: camera-integration
tags: [kztek-cameras, breaking-change, shared-library, build-error, camera-start]
severity: high
created: 2026-07-26
updated: 2026-07-26
project-origin: DoorAlarm v3
---

# `Kztek.Cameras.Camera.Start()` đổi chữ ký — project consumer không build được cho tới lần build kế tiếp

## Tình huống gặp phải

Mở lại project `DoorAlarm v3` (WinForms .NET 8) để review code. Project tham chiếu
`Kztek.Cameras` bằng **ProjectReference** trỏ thẳng sang repo dùng chung
`0.BaseLIB/Kztek.Camera/...`. Repo dùng chung này được sửa liên tục cho ParkingV8/Avalonia,
DoorAlarm không đụng tới trong thời gian đó.

## Triệu chứng / Lỗi

`dotnet build` fail 7 lỗi, tất cả tại 2 call site gọi `camera.Start(...)`:

```
FrmMain.cs(763,30): error CS1503: Argument 1: cannot convert from 'bool' to 'double'
FrmMain.cs(763,43): error CS1503: Argument 4: cannot convert from 'int' to 'bool'
FrmMain.cs(763,46): error CS1503: Argument 5: cannot convert from 'bool' to 'List<AIBoxDetect>'
FrmMain.cs(763,124): error CS1503: Argument 6: cannot convert from 'List<AIBoxDetect>' to 'bool'
FrmMain.cs(763,138): error CS1503: Argument 7: cannot convert from 'bool' to 'EmVirtualLoopType'
CameraProperty.cs(179,...): error CS1503: (tương tự)
```

Lỗi lệch dồn từ tham số 1 → tham số cuối, kiểu "so le" — dấu hiệu điển hình của **đổi
chữ ký hàm** chứ không phải sai 1 tham số đơn lẻ.

## Nguyên nhân gốc rễ

Thư viện dùng chung đã bỏ 2 tham số và thêm 1 tham số mới:

```csharp
// CŨ (code DoorAlarm đang gọi theo)
public void Start(bool enableMotionDetection, double motionAlarmLevel, int cameraSDK,
                  int motionDetectionInterval, bool enableAIDetection = false,
                  List<AIBoxDetect> aiDetectBoxs = null, bool enableRecording = false)

// MỚI (hiện tại)
public void Start(double fromMotionAlarmLevel, double toMotionAlarmLevel, int motionDetectionInterval,
                  bool enableAIDetection = false, List<AIBoxDetect> aiDetectBoxs = null,
                  bool enableRecording = false, EmVirtualLoopType virtualLoopType = EmVirtualLoopType.None)
```

- Bỏ `bool enableMotionDetection` (nay suy ra từ `from/toMotionAlarmLevel`).
- Bỏ `int cameraSDK` (chọn player nay do `CameraRtspUrlBuilderFactory` quyết định, luôn `AnvPlayer`).
- Tách `motionAlarmLevel` thành cặp `from/to`.
- Thêm `EmVirtualLoopType` ở cuối.

Vì các tham số đều là `bool`/`int`/`double`, trình biên dịch KHÔNG phát hiện được ở lần
sửa thư viện — chỉ nổ khi project consumer build lại. Project nào lâu không build thì
"ngủ đông" trong trạng thái hỏng.

## Giải pháp

Ánh xạ lại theo ngữ nghĩa, **không** đếm tham số:

```csharp
// Liveview thuần (không motion, không AI) — giống hệt ParkingV8 đang dùng
temp.Start(0, 0, 0);

// Có AI detection
camera.Start(0, 0, 0,
             enableAIDetection: aiDetectBoxs.Count > 0 && isServerMode,
             aiDetectBoxs: aiDetectBoxs,
             enableRecording: camera.EnableRecording);
```

1. Đọc chữ ký hiện tại trong `0.BaseLIB/.../Kztek.Cameras/Camera.cs` (không tin comment cũ).
2. `git log -S"public void Start(bool" -- Camera.cs` để lấy chữ ký CŨ → lập bảng ánh xạ tham số.
3. Đối chiếu với các project ĐÃ migrate để lấy cách gọi chuẩn:
   `grep -rn "\.Start(0" --include=*.cs 1.IPARKING` → `ParkingV8` dùng `Start(0, 0, 0)` cho liveview.
4. Build lại xác nhận 0 error.

## Áp dụng lại (How to reuse)

- Khi mở lại project cũ có **ProjectReference sang repo `0.BaseLIB` dùng chung** →
  **chạy `dotnet build` TRƯỚC KHI đọc/sửa code**. Đừng giả định "code cũ chạy được thì vẫn build được".
- Khi thấy chuỗi `CS1503` lệch so le nhiều tham số liên tiếp → nghĩ ngay "đổi chữ ký",
  không sửa vá từng tham số.
- Cách nhanh nhất tìm cách gọi ĐÚNG: grep các project khác trong `1.Window` đã migrate,
  đừng tự suy diễn ánh xạ.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Tham số toàn kiểu primitive (`bool`/`int`/`double`) → thứ tự đổi mà vẫn "gần đúng"
  có thể compile được ở call site khác và chạy SAI ngầm (vd truyền nhầm `cameraSDK` vào
  `motionDetectionInterval`). Không chỉ dựa vào việc build pass.
- ⚠️ Dùng **named argument** (`enableAIDetection:`, `aiDetectBoxs:`) cho các tham số optional —
  lần đổi chữ ký sau sẽ fail-fast tại compile thay vì bind nhầm vị trí.
- ⚠️ `DoorAlarmv3.csproj` còn tham chiếu DLL bằng HintPath tuyệt đối sang repo `1.IPARKING` —
  cùng loại rủi ro coupling, máy khác clone về sẽ không build được.

## Tham chiếu

- `0.BaseLIB/Kztek.Camera/Kztek.Camera/1.Source/Kztek.Cameras/Camera.cs`
- Project liên quan: DoorAlarm v3, ParkingV8 (WinForms + Avalonia)
- Lesson liên quan: `camera-integration/camera-type-int-decoded-with-wrong-enum.md`
