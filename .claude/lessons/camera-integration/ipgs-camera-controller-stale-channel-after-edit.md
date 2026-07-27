---
category: camera-integration
tags: [avalonia, camera-controller, hik, dahua, milesight, stale-state, edit-dialog]
severity: high
created: 2026-07-20
updated: 2026-07-20
project-origin: iPGSv4 - IPGSUseCam
---

# Sửa camera đang chạy (channel/IP/port/user/pass) không có tác dụng cho tới khi restart app

## Tình huống gặp phải

Người dùng sửa 1 camera đang kết nối (qua `CameraWindow` — "Sửa Camera"), đổi giá trị **Channel**
(hoặc IP/Port/Username/Password), bấm Xác nhận. DB và `CameraObject` in-memory đều được cập nhật
đúng (`tblCamera.UpdateData()` + `CameraObjectCollection.UpdateCameraInfo()` cả hai đều chính xác).
Nhưng camera thực tế vẫn hoạt động theo channel/IP/port CŨ.

## Triệu chứng / Lỗi

- Không có exception, không có log lỗi.
- DB đã update đúng giá trị mới (kiểm tra trực tiếp SQL thấy đúng).
- `CameraObject.channel` (in-memory) cũng đúng giá trị mới.
- NHƯNG hành vi thực tế của camera (ảnh chụp, URL gọi ISAPI/cgi-bin, polling) vẫn dùng channel/IP/port cũ.
- Sau khi restart toàn bộ app → hoạt động đúng với giá trị mới.

## Nguyên nhân gốc rễ (Root Cause)

`ICameraController` (`HikCameraController`, `DahuaCameraController`, `MilesightCameraController`)
đọc `Channel` từ `CameraObject` **CHỈ MỘT LẦN trong constructor**:

```csharp
public HikCameraController(CameraObject cameraObject)
{
    ...
    Channel = cameraObject.channel;   // chỉ set 1 lần ở đây
}
```

`CameraObject.Start()` có refresh `IP`/`Port`/`Login`/`Password` mỗi lần gọi lại (nằm ngoài guard
`if (cameraController == null)`), nhưng **KHÔNG refresh `Channel`** — field này hoàn toàn phụ thuộc
vào constructor. Vì camera đang chạy dùng chung 1 `cameraController` instance cũ (không bị null),
gọi lại `Start()` (nếu có) cũng không tạo controller mới → `Channel` field mãi mãi giữ giá trị cũ.

Việc edit dialog (`CameraWindow`) chỉ cập nhật `CameraObject` (DB + in-memory field) — không hề biết
tới, và không đụng vào, `cameraController` instance đang chạy của camera đó.

## Giải pháp

Sau khi lưu chỉnh sửa 1 camera đang có `cameraController` active, PHẢI restart camera đó (Stop rồi
Start lại) để buộc tạo controller instance MỚI, đọc lại toàn bộ property (bao gồm `Channel`, và
`camera_Type` nếu loại camera bị đổi) từ `CameraObject` hiện tại:

```csharp
_crudCamera.EditClicked += async (_, _) =>
{
    if (_crudCamera.SelectedItem is not CameraObject selected) return;
    var dlg = new CameraWindow(selected.id);
    var cam = await dlg.ShowDialog<CameraObject?>(this);
    if (cam is not null)
    {
        SaveLastCameraSettings();

        if (selected.cameraController is not null)   // đang chạy → phải restart
        {
            await selected.Stop();   // set cameraController = null
            await selected.Start();  // tạo controller MỚI, đọc lại channel/IP/port/type
        }

        RefreshGrid();
    }
};
```

`selected` ở đây CHÍNH LÀ instance trong `StaticPool.cameraObjects.InnerList` (đã được
`UpdateCameraInfo()` mutate tại chỗ), nên không cần re-fetch — chỉ cần Stop/Start lại nó.

## Áp dụng lại (How to reuse)

- Khi thấy 1 property của `CameraObject` chỉ được đọc **trong constructor** của
  `ICameraController` implementation (không có setter nào refresh nó sau đó) → mặc định coi đây là
  "cached-once" field, PHẢI restart controller sau khi property đó bị sửa lúc đang chạy.
- Trước khi thêm field mới vào `ICameraController` (VD: resolution, stream type...) → kiểm tra ngay
  xem field đó được set ở đâu ngoài constructor; nếu không có, áp dụng cùng pattern restart này.
- Bất kỳ dialog "Sửa camera" nào khác (không chỉ `SettingsWindow`) mà cho phép sửa camera đang chạy
  đều cần áp dụng cùng logic Stop/Start sau khi lưu.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ `CameraObject.Start()` refresh IP/Port/Login/Password mỗi lần gọi (nằm NGOÀI guard
  `cameraController == null`) — dễ lầm tưởng TẤT CẢ property đều tự refresh, nhưng `Channel` là
  ngoại lệ vì nó chỉ nằm trong constructor của từng `ICameraController` implementation, không có
  chỗ nào set lại trong `Start()`.
- ⚠️ Đừng gọi Stop/Start vô điều kiện cho MỌI camera vừa sửa — chỉ gọi khi
  `selected.cameraController is not null` (tức đang thực sự chạy); camera chưa từng Start thì không
  cần và không nên restart.
- ⚠️ Nếu sau này đổi `camera_Type` khi đang chạy (VD: HIK → Dahua), restart theo pattern này cũng
  tự động xử lý đúng vì `Start()` tạo lại đúng loại controller dựa trên `camera_Type` hiện tại.

## Tham chiếu

- File liên quan: `IPGSUseCam/Views/SettingsWindow.axaml.cs` (EditClicked handler),
  `IPGS.Control/Views/CameraWindow.axaml.cs`, `IPGS.Object/Objects/DeviceDatas/CameraObject.cs`
  (`Start()`/`Stop()`), `IPGS.Object/Devices/HIKCameraController.cs`,
  `IPGS.Object/Devices/DahuaCameraController.cs`, `IPGS.Object/Devices/MilesightCameraController.cs`
- Project liên quan: iPGSv4 / IPGSUseCam
