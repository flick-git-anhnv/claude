---
category: camera-integration
tags: [kztek-cameras, camera-start, config-reload, event-subscription-leak, aidetectanalyzing]
severity: medium
created: 2026-08-24
updated: 2026-08-24
project-origin: DoorAlarm v3
---

# Sửa xong "vùng nhận dạng AI" và quay về FrmMain không tự cập nhật — phải restart app

## Tình huống gặp phải

DoorAlarm v3 (WinForms .NET 8). User vào `FrmSetting` → `frmCameraSetting` sửa vùng cấu
hình AI của camera (`BtnSave_Click` — UPDATE `tblCamera.ConfigRegions`), đóng dialog quay
về `FrmMain`. Camera vẫn giám sát bằng vùng cấu hình CŨ cho tới khi restart app.

## Triệu chứng / Lỗi

- Lưu cấu hình vùng nhận dạng → không có lỗi, DB đã update đúng (`tblCamera.ConfigRegions`).
- Quay lại màn hình chính, camera vẫn dùng bộ `AIBoxDetect` cũ để phát hiện mở/đóng.
- Chỉ sau khi tắt bật lại app thì cấu hình mới có hiệu lực.

## Nguyên nhân gốc rễ

`Camera.Start(...)` (thứ tạo `AnvPlayer` với `AiDetectBoxes` cố định lúc gọi) chỉ được gọi
từ `FrmMain.ConnectWithCamera()`, và hàm này **chỉ chạy 1 lần lúc app khởi động**
(`CheckAppMode()`). `frmCameraSetting.BtnSave_Click` chỉ UPDATE DB, không có cách nào báo
lại cho `FrmMain`/`Camera` instance đang chạy để nạp lại `ConfigRegions` mới — vì
`frmCameraSetting` được mở lồng trong `FrmSetting` (`new FrmSetting().ShowDialog()` tại
`FrmMain.BtnSetting_Click`), và `FrmSetting` không giữ tham chiếu ngược về `FrmMain`.

Đây là biến thể khác của cùng gốc rễ đã ghi ở
`camera-integration/camera-start-missing-after-runtime-add.md`: **`ConnectWithCamera()` là
điểm DUY NHẤT nạp `ConfigRegions` từ DB vào `AiDetectBoxes` đang chạy, và nó chỉ được gọi
1 lần lúc khởi động** — bất kỳ thay đổi ConfigRegions nào sau đó (thêm camera mới, hoặc sửa
vùng cấu hình camera có sẵn) đều không có tác dụng cho tới khi hàm này chạy lại.

`FrmMain.BtnSetting_Click` đã có sẵn đúng PATTERN xử lý việc này cho controller I/O:
`DisconnectWithDevices()` trước khi mở `FrmSetting`, `ConnectWithController()` sau khi đóng
— nhưng thiếu cặp tương ứng cho camera (`DisconnectWithDevices()` cố ý KHÔNG dừng camera,
comment `//item.Stop();` ngay trong đó, và không có `ConnectWithCamera()` sau khi đóng).

## Giải pháp

Thêm `ConnectWithCamera();` ngay sau `await ConnectWithController();` trong
`BtnSetting_Click` (`FrmMain.cs`) — `Camera.Start()` tự `CloseVideoSource()` trước khi mở
lại nên gọi lại an toàn, không cần tự `Stop()` trước:

```csharp
await ConnectWithController();
// Camera KHÔNG bị dừng bởi DisconnectWithDevices() (chỉ IO controller), nhưng
// ConfigRegions vừa sửa trong Settings vẫn nằm im trong DB cho tới khi Start() lại.
ConnectWithCamera();
```

**Gotcha đi kèm phát hiện khi sửa (PHẢI fix cùng lúc):** `ConnectWithCamera()` có dòng
`camera.AIDetectAnalyzing += Camera_AIDetectAnalyzing;` KHÔNG `-=` trước. Gọi hàm này nhiều
lần trong vòng đời app (mỗi lần đóng Settings) sẽ cộng dồn subscriber trên CÙNG 1 `Camera`
object (event field sống trên `Camera`, không bị reset bởi `Start()`/`CloseVideoSource()`
vì đó là field của `videoSourcePlayer`, không phải của `Camera`) → mở/đóng Settings N lần
thì 1 sự kiện AI detect bắn ra N lần (N lần insert DB, N lần bật cảnh báo). Fix: đổi thành
`-=` rồi `+=` (idempotent) trước khi gọi lại `ConnectWithCamera()` nhiều lần trong runtime.

## Áp dụng lại (How to reuse)

- Bất kỳ hàm "Connect/Setup X 1 lần lúc khởi động" nào đọc config từ DB vào 1 object sống
  lâu (không phải tạo mới mỗi lần dùng) → nếu có màn hình sửa config runtime cho X, PHẢI có
  chỗ gọi lại đúng hàm Connect/Setup đó sau khi đóng màn cấu hình, không chỉ ghi DB xong là
  coi như đã xong việc.
- Khi thêm 1 lệnh gọi lại 1 hàm "chỉ chạy lúc khởi động" vào một chỗ mới trong runtime →
  BẮT BUỘC kiểm tra bên trong hàm đó có `+=` event subscription nào không idempotent
  (thiếu `-=` trước) — nếu có, sửa cùng lúc, đừng để lại bug rò rỉ subscription cho lần sau.
- Dấu hiệu nhận biết: "sửa cấu hình xong quay lại màn chính không thấy hiệu lực, restart app
  thì đúng" → nghĩ ngay tới "có hàm Connect/Start chỉ chạy 1 lần lúc khởi động, thiếu gọi lại
  sau khi đóng màn cấu hình", tra theo lesson liên quan
  `camera-start-missing-after-runtime-add.md` trước khi debug từ đầu.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Gọi lại `ConnectWithCamera()` sẽ restart TẤT CẢ camera (không chỉ camera vừa sửa) —
  chấp nhận được vì đây là hành vi hệ thống vốn đã dùng y hệt cho `ConnectWithController()`
  (restart toàn bộ controller mỗi lần đóng Settings dù chỉ sửa 1 thiết bị); không tối ưu
  riêng cho từng camera trong lần fix này.
- ⚠️ `DisconnectWithDevices()` CỐ Ý không dừng camera (code cũ đã comment `//item.Stop()`)
  — đừng "dọn dẹp" bật lại đoạn Stop() đó nếu không kiểm tra kỹ, có thể có lý do khác (tránh
  camera bị ngắt hình khi vào Settings) mà comment không giải thích.
- ⚠️ Đừng nhầm lẫn: bug này (sửa CONFIG không refresh) khác với bug
  `camera-start-missing-after-runtime-add.md` (camera MỚI THÊM chưa từng Start()) — cùng gốc
  rễ (`ConnectWithCamera()` chỉ chạy 1 lần) nhưng 2 điểm kích hoạt khác nhau, cả 2 đều đã fix
  trong cùng đợt (fix tại `frmCameraSetting` cho case thêm mới, fix tại `FrmMain.BtnSetting_Click`
  cho case sửa config).

## Tham chiếu

- `DoorAlarmv3/FrmMain.cs` — `BtnSetting_Click`, `ConnectWithCamera()`, `DisconnectWithDevices()`
- `DoorAlarmv3/Forms/frmCameraSetting.cs` — `BtnSave_Click`
- Lesson liên quan: `camera-integration/camera-start-missing-after-runtime-add.md`
