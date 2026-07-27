---
category: camera-integration
tags: [camera-type, milesight, hikvision, rtsp-builder, kztek-cameras-avalonia, ipgsusecam]
severity: medium
created: 2026-07-20
updated: 2026-07-20
project-origin: iPGSv4 (IPGSUseCam — wiring LiveView sang Kztek.Cameras.Avalonia)
---

> **Cập nhật 2026-07-20 (đã fix dứt điểm):** User cung cấp tài liệu RTSP chính hãng Milesight
> (Network Camera → Network → Advanced → RTSP) xác nhận scheme `rtsp://ip:rtspPort/main`
> (Primary), `/sub` (Secondary), `/third` (Tertiary), port mặc định 554 — khớp đúng giả định
> ban đầu. Đã thêm chính thức: `CameraType.Milesight` (member MỚI, thêm **cuối** enum để
> không dịch chuyển ordinal các member khác — xem lesson `camera-type-int-decoded-with-wrong-enum.md`)
> + `BuildMilesight()` trong `CameraRtspUrlBuilderFactory.cs`. `MainWindow.axaml.cs` giờ map thẳng
> `Milesight → KzCameraType.Milesight`, không còn cần hack `Custom` + tự build URL thủ công như mô
> tả bên dưới (giữ nguyên phần dưới làm lịch sử điều tra — hữu ích nếu gặp hãng camera khác chưa có
> builder).
>
> **Cập nhật 2026-07-20 (bug thứ 2, phát hiện ngay sau bản fix trên):** Bản `BuildMilesight()`
> đầu tiên chọn stream theo `Camera.StreamIndex` (0=main/1=sub/≥2=third) — NHƯNG
> `MainWindow.axaml.cs` (`OpenLiveViewAsync`) chỉ set `Chanel = cam.channel`, KHÔNG BAO GIỜ set
> `StreamIndex` → field này luôn ở giá trị default (`1` = "sub", xem `Camera.cs` field
> `streamIndex = 1`) bất kể user cấu hình channel gì trong UI — mọi camera Milesight luôn mở
> nhầm luồng "/sub" thay vì đúng luồng mong muốn. **Fix:** đổi `BuildMilesight()` sang dùng
> `Camera.Chanel` (field THẬT SỰ được set từ `cam.channel`), đánh số kênh bắt đầu từ 1
> (parity với Dahua/HIKVISION2/CNB: `Chanel <= 0 ? 1 : Chanel`) — 1=main, 2=sub, ≥3=third.

# `IPGS.Object` CameraType (HIKVision/Dahua/Milesight) không map 1-1 sang `Kztek.Cameras.CameraType` — HIKVision phải map HIKVISION2, Milesight ban đầu chưa có builder (đã fix)

## Tình huống gặp phải

Thêm project `Kztek.Cameras.Avalonia` vào solution `IPGSUseCam` (IPGSv4/PGS ZCU) để LiveView dùng engine camera thật (`Kztek.Cameras.Camera` + `frmViewCamera`) thay placeholder `LiveViewWindow` cũ (chưa nối SDK). Cần map `IPGS.Object.Objects.DeviceDatas.CameraType` (chỉ có 3 giá trị: `HIKVision`, `Dahua`, `Milesight`) sang `Kztek.Cameras.CameraType` (19 giá trị hãng khác nhau) để `CameraRtspUrlBuilderFactory.TryBuild()` build đúng URL RTSP.

## Triệu chứng / Lỗi

Không phải runtime bug — phát hiện khi ĐỌC code `CameraRtspUrlBuilderFactory.cs` trước khi wiring (tránh lặp lại lesson `camera-type-int-decoded-with-wrong-enum.md`). Nếu map cẩu thả theo tên "trông giống" sẽ gây lỗi im lặng giống lesson đó (treo "Connecting", build sai URL, không exception).

## Nguyên nhân gốc rễ (Root Cause)

`Kztek.Cameras.CameraType` (`Objects/CameraType.cs`) có member `HIKVISION` (không dấu, viết hoa hoàn toàn) **và** `HIKVISION2` — nhưng `CameraRtspUrlBuilderFactory._builders` dictionary **chỉ đăng ký `HIKVISION2`** (builder PSIA path `/PSIA/streaming/channels/...`). `HIKVISION` (bản gốc, không số 2) **không có builder nào** — comment trong factory ghi rõ "no entry (không có case trong switch gốc)" — nếu lỡ map `IPGS CameraType.HIKVision` → `Kztek.Cameras.CameraType.HIKVISION` (khớp tên, sai chọn) thì `TryBuild()` trả `false`, `Camera.Start()` không tạo `videoSourcePlayer`, LiveView im lặng không có gì xảy ra — không exception, không log.

Nghiêm trọng hơn: `Milesight` **hoàn toàn không có** member/builder tương ứng trong `Kztek.Cameras.CameraType` — hãng này chưa từng được port sang thư viện Avalonia. Không có "đáp án đúng" sẵn có để map — phải tự build RTSP URL thủ công và dùng `CameraType.Custom` (builder `BuildCustom()` trả thẳng `cam.VideoSource`, không xử lý gì thêm).

## Giải pháp

```csharp
private static KzCameraType MapToKztekCameraType(string ipgsCameraType)
{
    if (ipgsCameraType == CameraType.Dahua.ToString())
        return KzCameraType.Dahua;          // có builder — map thẳng
    if (ipgsCameraType == CameraType.HIKVision.ToString())
        return KzCameraType.HIKVISION2;      // LƯU Ý: không phải HIKVISION (không có builder)

    // Milesight (và mọi loại chưa có builder) → Custom: PHẢI tự build URL RTSP đầy đủ
    // trước khi gán vào camera.VideoSource, vì BuildCustom() trả thẳng VideoSource.
    return KzCameraType.Custom;
}

// Khi dùng Custom, VideoSource phải là URL RTSP đầy đủ, KHÔNG phải IP thô:
VideoSource = kzType == KzCameraType.Custom
    ? $"rtsp://{login}:{password}@{ip}:554/main"   // ⚠️ path "/main" là GIẢ ĐỊNH, chưa xác nhận với camera Milesight thật
    : ip,
```

1. Trước khi map bất kỳ enum "loại camera" nào sang `Kztek.Cameras.CameraType`, luôn mở `CameraRtspUrlBuilderFactory.cs` xem `_builders` dictionary có đăng ký entry cho member đó không — member enum tồn tại KHÔNG đồng nghĩa có builder.
2. Với hãng chưa có builder (Milesight, VideoCaptureDevice, VideoFile, HIKVISION bản gốc) → dùng `CameraType.Custom` + tự build URL RTSP đầy đủ vào `VideoSource`.
3. Path RTSP tự build cho hãng chưa có builder chính thức PHẢI được ghi chú rõ là giả định, cần xác nhận với thiết bị thật trước khi go-live (không coi là final).

## Áp dụng lại (How to reuse)

- Khi map bất kỳ enum "loại camera nội bộ app" (VD `IPGS.Object...CameraType`, hoặc DB int) sang `Kztek.Cameras.CameraType` → luôn check `CameraRtspUrlBuilderFactory._builders` trước, đừng tin việc member cùng tên nghĩa là có builder tương ứng.
- Khi thấy tên enum có hậu tố số (`HIKVISION` vs `HIKVISION2`) trong `Kztek.Cameras.CameraType` → hậu tố số thường là bản có builder thật, bản không hậu tố có thể là "no-op" placeholder giữ chỗ.
- Khi 1 hãng camera (Milesight) chưa có builder trong `Kztek.Cameras.Avalonia` → không tự ý thêm builder mới trong project nguồn (BaseLIB dùng chung nhiều app) nếu task hiện tại không yêu cầu — dùng `Custom` tạm thời + ghi rõ giả định, để Tech Lead quyết định có nên thêm builder chính thức (`BuildMilesight`) hay không.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Khi builder mới cần đọc 1 field của `Camera` (VD `StreamIndex`) để chọn nhánh logic, PHẢI xác
  nhận field đó thực sự được caller set — không giả định field "nghe hợp lý" (StreamIndex có vẻ đúng
  để chọn main/sub/third) là field đang được dùng thực tế. Ở đây `MainWindow.axaml.cs` chỉ set
  `Chanel`, không set `StreamIndex` → builder đọc default value âm thầm, không exception, không log,
  y hệt pattern lỗi "im lặng" đã ghi ở lesson `camera-type-int-decoded-with-wrong-enum.md`.
- ⚠️ `TryBuild()` trả `false` mà không throw — nếu map sai (VD chọn `HIKVISION` thay vì `HIKVISION2`), `Camera.Start()` chạy xong nhưng `videoSourcePlayer` = null, LiveView mở ra trắng/im lặng không lỗi gì — dễ nhầm là bug camera thật (offline, sai IP) thay vì bug mapping.
- ⚠️ URL RTSP tự build cho Custom/Milesight (`/main` path) là suy đoán theo pattern phổ biến — KHÔNG phải xác nhận từ thiết bị Milesight thật hay tài liệu SDK chính thức, cần test với camera thật trước khi go-live.

## Tham chiếu

- File liên quan: `0.BaseLIB/Kztek.Camera/Kztek.Camera/1.Source/Kztek.Cameras.Avalonia/CameraRtspUrlBuilderFactory.cs`, `Objects/CameraType.cs`
- File áp dụng: `iPGSv4/IPGSUseCam/Views/MainWindow.axaml.cs` (`OpenLiveViewAsync`, `MapToKztekCameraType`)
- Lesson liên quan: [camera-type-int-decoded-with-wrong-enum.md](camera-type-int-decoded-with-wrong-enum.md) — cùng chủ đề "nhiều enum loại camera dễ đánh đồng sai", khác cơ chế lỗi (int-ordinal vs string-map thiếu builder)
- Project liên quan: iPGSv4 (IPGSUseCam), Kztek.Camera (BaseLIB)
