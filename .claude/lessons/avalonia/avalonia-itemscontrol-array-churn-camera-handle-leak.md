---
category: avalonia
tags: [itemscontrol, itemssource, handle-leak, camera, winforms-interop, user-object-quota]
severity: high
created: 2026-08-25
updated: 2026-08-25
project-origin: parking-v8-app-avalonia
---

# ItemsControl.ItemsSource đổi reference (dù nội dung giống) → destroy/recreate toàn bộ item container → leak native handle nếu item control mở resource ngoài (camera, WinForms interop...)

## Tình huống gặp phải

App Avalonia (ParkingV8) hiển thị nhiều camera tile trên mỗi lane qua `LaneCameraBlock`
(`src/ParkingV8.App/Lanes/Views/Blocks/LaneCameraBlock.axaml.cs`). Mỗi tile là
`EntryLaneCameraTileView` chứa `CameraView` — control bọc thư viện camera SDK closed-source
`Kztek.Cameras` (AnvPlayer), start/stop RTSP player khi Attached/DetachedFromVisualTree.

## Triệu chứng / Lỗi

Sau một thời gian chạy (không rõ pattern tái hiện chính xác — chỉ có log lỗi), app crash:

```
System.ComponentModel.Win32Exception: Error creating window handle.
   at System.Windows.Forms.NativeWindow.CreateHandle(CreateParams cp)
   at System.Windows.Forms.Control.CreateHandle()
   at System.Windows.Forms.Control.get_Handle()
   ...
   at System.Windows.Forms.Control.WmPaint(Message& m)
   at System.Windows.Forms.Control.WndProc(Message& m)
NativeErrorCode: 1406
```

Đây là dấu hiệu kinh điển của cạn **USER object handle quota** (mặc định 10.000/process trên
Windows) — process đã leak handle dần theo thời gian, không phải lỗi tại đúng thời điểm crash.

## Nguyên nhân gốc rễ (Root Cause)

`LaneCameraBlock.RefreshLayout()` (trước fix) LUÔN:
1. Tạo **array mới** bằng `.ToArray()` cho `VisibleCameras`/`VerticalCameras`/`HorizontalCameras`.
2. Gọi `NotifyChanged(...)` vô điều kiện — kể cả khi nội dung danh sách camera **giống hệt** lần trước.

`VerticalCameras`/`HorizontalCameras` được bind vào `ItemsControl.ItemsSource` trong XAML. Avalonia
(giống WPF) không so sánh nội dung — chỉ cần property `ItemsSource` bắn `PropertyChanged` với
reference mới là `ItemsControl` coi đó là **danh sách hoàn toàn khác** và **destroy + recreate
toàn bộ item container** (tức toàn bộ `EntryLaneCameraTileView` cho block đó), dù các
`EntryLaneCameraViewModel` bên trong là cùng instance.

`RefreshLayout()` bị trigger bởi:
- Bất kỳ camera nào đổi `IsLiveVisible`/`DisplayIndex` (`OnCameraPropertyChanged`) — kể cả khi giá
  trị gán lại giống giá trị cũ (không có no-op check ở setter phía ViewModel).
- Lane settings reload (`ApplyCameraVisibility()`) gán lại visibility cho toàn bộ camera cùng lúc.

Mỗi lần tile bị destroy/recreate: `DetachedFromVisualTree` → `StopCamera()` (chỉ gọi
`camera.Stop()` của SDK, KHÔNG có `Dispose()` tường minh nào trên `camera`/`videoSourcePlayer`) rồi
`AttachedToVisualTree` của tile mới → `StartCamera()` → `new Camera()` lại từ đầu. Vì
`Kztek.Cameras` là thư viện compiled sẵn (không có source để verify), không thể chắc `Stop()` giải
phóng hết native window handle nó có thể mở nội bộ (video render surface) — nếu không, mỗi chu kỳ
churn rò rỉ 1 USER handle, tích lũy dần tới khi cạn quota.

## Giải pháp

Chỉ gán array mới / notify khi nội dung thực sự thay đổi — giữ nguyên reference cũ nếu danh sách
camera hiển thị không đổi, để tránh Avalonia coi `ItemsSource` là mới:

```csharp
private void RefreshLayout(bool forceNotify = false)
{
    var newVisibleCameras = EnumerateCameraViewModels(Cameras)
        .Where(x => x.IsLiveVisible)
        .OrderBy(x => x.Purpose == (int)EmCameraPurpose.Panorama ? 0 : 1)
        .ThenBy(x => x.DisplayIndex)
        .ThenBy(x => x.Name)
        .ToArray();

    if (!forceNotify && newVisibleCameras.SequenceEqual(visibleCameras))
    {
        return; // nội dung giống hệt -> KHÔNG gán lại, KHÔNG notify -> ItemsControl không churn
    }

    VisibleCameras = newVisibleCameras;
    NotifyChanged(/* ... */);
}
```

`CameraDirectionProperty` change (đổi layout hướng — hiếm, do user chủ động) vẫn dùng
`forceNotify: true` vì lúc đó `UseVerticalLayout`/`UseHorizontalLayout` thực sự đổi giá trị.

1. So sánh nội dung (`SequenceEqual`, reference equality trên từng `EntryLaneCameraViewModel`) trước
   khi gán array mới cho property bind vào `ItemsSource`.
2. Chỉ gọi `NotifyChanged` khi có thay đổi thực sự.
3. Build lại để xác nhận không có lỗi biên dịch (đã build `ParkingV8.App.csproj` thành công).

## Áp dụng lại (How to reuse)

- Khi thấy property kiểu `IReadOnlyList<T>`/array bind vào `ItemsControl.ItemsSource` (hoặc bất kỳ
  control nào tự "materialize" children theo item, ví dụ `TabControl.Items`, `TreeDataGrid`) được
  RECOMPUTE (`.ToArray()`/`.ToList()`) mỗi lần một trigger nhỏ bắn ra (property changed trên item con,
  collection changed...) → LUÔN so sánh nội dung với giá trị cũ trước khi gán lại + notify. Đừng
  assume "cùng nội dung thì UI tự biết không đổi" — Avalonia/WPF chỉ nhìn reference + PropertyChanged.
- Khi item template của `ItemsControl` chứa control mở resource ngoài (camera SDK, file handle, socket,
  WinForms/native interop qua `NativeWindow`) → destroy/recreate item KHÔNG PHẢI thao tác rẻ. Phải coi
  reference churn của `ItemsSource` là nguy hiểm ngang với gọi `Dispose()`+ tạo lại resource đó thủ công.
- Gặp `Win32Exception: Error creating window handle` (NativeErrorCode 1406) hoặc app dần chậm/crash sau
  thời gian dài chạy, không rõ nguyên nhân tức thời → nghi ngay leak USER/GDI handle tích lũy, tìm
  vòng lặp tạo/hủy control (không phải lỗi tại thời điểm crash — phải trace ngược lịch sử churn).

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ `SequenceEqual` mặc định dùng `Equals` — chỉ đáng tin nếu item (`EntryLaneCameraViewModel`) là
  cùng instance được reuse (không bị recreate ở tầng ViewModel cao hơn). Nếu tầng trên cũng tái tạo VM
  mỗi lần refresh thì fix này vô nghĩa — phải fix triệt để từ tầng tạo VM.
- ⚠️ Đây chỉ là fix giảm churn ở tầng UI (Avalonia) — KHÔNG chắc chắn giải quyết dứt điểm leak nếu SDK
  `Kztek.Cameras` cũng leak handle ngay cả khi `Stop()` được gọi đúng 1 lần/camera trong vòng đời app.
  Nếu lỗi vẫn tái diễn sau fix này, cần điều tra tiếp bên trong SDK (không có source — có thể cần hỏi
  vendor hoặc decompile) hoặc theo dõi USER Object count qua Task Manager để xác nhận leak đã hết.
- ⚠️ `forceNotify: true` cho `CameraDirectionProperty` vẫn có thể gây churn (nhưng đây là hành động
  chủ động, hiếm, chấp nhận được).

## Tham chiếu

- File sửa: `src/ParkingV8.App/Lanes/Views/Blocks/LaneCameraBlock.axaml.cs` (RefreshLayout)
- Control liên quan: `src/ParkingV8.UI/Controls/Cs/CameraView.axaml.cs` (StartCamera/StopCamera —
  không có Dispose tường minh trên `camera`/`videoSourcePlayer`)
- Project liên quan: parking-v8-app-avalonia
