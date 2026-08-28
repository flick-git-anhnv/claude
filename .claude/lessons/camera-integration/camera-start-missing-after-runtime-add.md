---
category: camera-integration
tags: [kztek-cameras, camera-start, runtime-add, videosourceplayer, getcurrentvideoframe]
severity: medium
created: 2026-08-24
updated: 2026-08-24
project-origin: DoorAlarm v3
---

# Camera vừa thêm mới lúc runtime: bấm "Lấy hình ảnh" lần đầu không có tác dụng vì chưa từng `Start()`

## Tình huống gặp phải

DoorAlarm v3 (WinForms .NET 8), màn `frmCameraSetting` (cấu hình vùng nhận diện AI cho
camera). User thêm 1 camera mới qua `CameraProperty.AddNewCamera()`, sau đó mở màn cấu
hình camera và bấm nút "Lấy hình ảnh" (`BtnGetImage_Click`) — không có gì xảy ra: không
ảnh hiện lên, không lỗi, không MessageBox.

## Triệu chứng / Lỗi

- Bấm "Lấy hình ảnh" lần đầu sau khi thêm camera mới → im lặng, `picSetting.Image` vẫn null.
- Restart lại app rồi mở lại đúng camera đó → bấm nút hoạt động bình thường.
- Không có exception nào bị catch — vì `Camera.GetCurrentVideoFrame()` chỉ trả `null` khi
  chưa có frame, không throw.

## Nguyên nhân gốc rễ

`Kztek.Cameras.Camera` cần gọi `Start(...)` (mở `videoSourcePlayer`, bắt đầu decode RTSP/HTTP)
thì `GetCurrentVideoFrame()` mới có dữ liệu — trước đó `IsRunning == false` và
`GetCurrentVideoFrame()` luôn trả `null`.

Trong DoorAlarm v3, việc gọi `camera.Start(...)` cho TẤT CẢ camera trong `AppData.cameras`
chỉ xảy ra **một lần duy nhất** lúc app khởi động, trong `FrmMain.ConnectWithCamera()`
(gọi từ `CheckAppMode()`). Khi user thêm 1 camera mới lúc app đang chạy
(`CameraProperty.AddNewCamera()` → `AppData.cameras.Add(CurrentCamera)`), object camera
mới chỉ được thêm vào list — **không ai gọi `Start()` cho nó** cho tới lần restart app kế
tiếp (khi `ConnectWithCamera()` chạy lại và duyệt qua list đã có camera mới).

`frmCameraSetting` (`Forms/frmCameraSetting.cs`) không biết điều này — nó giả định camera
truyền vào đã sẵn sàng (`IsRunning == true`) và gọi thẳng `GetCurrentVideoFrame()`.

## Giải pháp

Tại `BtnGetImage_Click`, tự kiểm tra `camera.IsRunning`, nếu chưa chạy thì tự `Start()`
tại chỗ (dùng named argument theo đúng khuyến nghị của
`camera-integration/kztek-cameras-start-signature-drift.md`), rồi **poll** `GetCurrentVideoFrame()`
thay vì lấy ngay 1 lần — vì `Start()` là bất đồng bộ nội bộ (`videoSourcePlayer.Start()` mở
kết nối rồi mới bắt đầu bắn `NewFrame` event), lấy ngay sau `Start()` vẫn ra `null`.

```csharp
if (!this.camera.IsRunning)
{
    this.camera.RecordingFolder = Properties.Settings.Default.SaveVideoPath;
    this.camera.Start(0, 0, 0,
        enableAIDetection: false,
        aiDetectBoxs: [],
        enableRecording: this.camera.EnableRecording);
}

currentCameraImage = this.camera.GetCurrentVideoFrame();
for (int i = 0; i < 10 && currentCameraImage is null; i++)
{
    await Task.Delay(200);
    currentCameraImage = this.camera.GetCurrentVideoFrame();
}
```

(tối đa ~2s chờ frame đầu tiên; nếu camera thực sự không kết nối được thì sau 2s vẫn null
— UI hiển thị ảnh trống, không crash, người dùng bấm lại được.)

## Áp dụng lại (How to reuse)

- Bất kỳ màn hình nào gọi `Camera.GetCurrentVideoFrame()` trực tiếp trên 1 `Camera` object
  lấy từ `AppData.cameras`/DB mà KHÔNG chắc chắn nó đã qua `ConnectWithCamera()` (ví dụ:
  camera vừa thêm mới, hoặc màn hình mở độc lập không qua luồng khởi động app) → PHẢI check
  `camera.IsRunning` trước, tự `Start()` nếu cần, rồi poll vài trăm ms thay vì lấy ngay.
- Dấu hiệu nhận biết bug này: "bấm nút lấy hình/liveview lần đầu không có tác dụng, nhưng
  restart app xong thì lại chạy được" → nghĩ ngay đến "camera chưa được Start() lần nào"
  chứ không phải lỗi UI/event binding.
- Khi thêm 1 entity mới cần "kết nối thiết bị" (camera, controller, IO...) vào 1 hệ thống mà
  logic kết nối gốc chỉ chạy 1 lần lúc app khởi động → luôn tự hỏi: "entity mới thêm lúc
  runtime có được đưa vào vòng đời kết nối đó không, hay phải tự kết nối tại chỗ / restart
  mới có tác dụng?".

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Không dùng `Task.Delay` cố định 1 lần rồi lấy frame — thời gian camera trả frame đầu
  phụ thuộc mạng/camera, dùng vòng lặp poll ngắn (200ms) sẽ ổn định hơn số delay đoán mò.
- ⚠️ `GetCurrentVideoFrame()` không throw khi chưa có frame — không thể dựa vào try/catch
  để phát hiện tình huống này, phải chủ động check `IsRunning`/poll kết quả null.
- ⚠️ Đây chỉ là fix tại điểm dùng (`frmCameraSetting`) — nếu có thêm màn hình khác cũng gọi
  `GetCurrentVideoFrame()` trên camera mới thêm (chưa tìm thấy trong DoorAlarm v3 tại thời
  điểm viết lesson này) thì cần áp dụng lại đúng pattern trên, không giả định đã fix toàn cục.

## Tham chiếu

- `DoorAlarmv3/Forms/frmCameraSetting.cs` — `BtnGetImage_Click`
- `DoorAlarmv3/FrmMain.cs` — `ConnectWithCamera()`, `CheckAppMode()`
- `DoorAlarmv3/UserControls/CameraProperty.cs` — `AddNewCamera()`
- `0.BaseLIB/Kztek.Camera/Kztek.Camera/1.Source/Kztek.Cameras/Camera.cs` — `IsRunning`,
  `Start()`, `GetCurrentVideoFrame()`
- Lesson liên quan: `camera-integration/kztek-cameras-start-signature-drift.md`
