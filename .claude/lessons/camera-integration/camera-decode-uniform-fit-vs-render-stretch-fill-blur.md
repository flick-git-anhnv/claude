---
category: camera-integration
tags: [kztek-cameras, avalonia, ffmpeg, sws_scale, resolution, blur, stretch-fill, aspect-ratio]
severity: critical
created: 2026-07-21
updated: 2026-07-21
project-origin: parking-v8-app-avalonia (Kztek.Cameras.Avalonia library)
---

# Decode Uniform-fit (giữ aspect ratio) nhưng Render vẽ Stretch=Fill (lấp đầy control) → 2 lớp scale không khớp nhau gây mờ + sai độ phân giải

## Tình huống gặp phải

User báo "camera phát mờ, độ phân giải không đúng thực tế, vừa mờ vừa giật" — ảnh hưởng cả camera LPR
và camera giám sát/preview. Không có exception, không crash — chỉ là chất lượng hiển thị kém hơn dữ
liệu camera thực tế.

## Nguyên nhân gốc rễ (Root Cause)

Pipeline hiển thị camera gồm 2 bước resize/scale ĐỘC LẬP, được viết ở 2 thời điểm khác nhau (lịch sử
BUG-004 fix RAM leak), không ai đối chiếu lại xem chúng có khớp nhau không:

1. **Decode** (`AnvPlayerService.cs` → `PollingDecodeFrameAsync()`): tính `decodeW/decodeH` theo
   **Uniform-fit** — giữ đúng tỷ lệ khung hình gốc camera (`scale = Math.Min(ctrlW/srcW, ctrlH/srcH)`),
   rồi `sws_scale` (FFmpeg) resize xuống đúng kích thước đó.
2. **Render** (`AnvPlayer.cs` → `Render()`): vẽ frame đã decode bằng
   `context.DrawImage(avaloniaBmp, srcRect, localBounds)` — đây là **Stretch = Fill** CÓ CHỦ Ý (comment
   gốc: "FORCE scale, Stretch = Fill: ảnh vừa đầy tile, không có black bar", cố tình khớp hành vi
   WinForms cũ `e.Graphics.DrawImage(bmp, ClientRectangle)` — không letterbox, luôn lấp đầy control).

Khi tỷ lệ khung hình camera gốc khác tỷ lệ khung hình control hiển thị (rất phổ biến — camera
16:9/4:3 khác tile UI) → bước 1 (Uniform-fit) cho ra `decodeW`/`decodeH` NHỎ HƠN `ctrlW`/`ctrlH` ở một
chiều (để giữ đúng aspect ratio, tức có "khoảng trống" nếu vẽ letterbox) — nhưng bước 2 (Render) lại
kéo giãn ảnh nhỏ hơn đó lên ĐẦY `localBounds` (không letterbox) → một lớp upscale THỨ HAI (GPU-side,
Avalonia `DrawImage`), CHỒNG lên lớp downscale đã làm ở bước 1 (`sws_scale`, `SWS_BILINEAR`). Ảnh bị
downscale rồi upscale lại (2 lần scale không khớp nhau) → mờ; đồng thời số pixel thực tế nhận được
(từ decode) ít hơn số pixel hiển thị trên màn hình → "độ phân giải không đúng thực tế".

## Giải pháp

Đổi bước decode (Uniform-fit) sang **Fill khớp chính xác `ctrlW × ctrlH`** (non-uniform), để khớp đúng
ý đồ Stretch=Fill của Render() — `sws_scale` trở thành bước resize DUY NHẤT:

```csharp
// Trước (Uniform-fit — giữ aspect ratio, gây mismatch với Render Stretch=Fill):
double scaleByWidth  = (double)ctrlW / srcW;
double scaleByHeight = (double)ctrlH / srcH;
double scale = Math.Min(scaleByWidth, scaleByHeight);
decodeW = Math.Max(1, (int)(srcW * scale));
decodeH = Math.Max(1, (int)(srcH * scale));

// Sau (Fill — khớp đúng Render Stretch=Fill):
decodeW = Math.Max(1, ctrlW);
decodeH = Math.Max(1, ctrlH);
```

File: `Kztek.Camera/1.Source/Kztek.Cameras.Avalonia/Players/FFMPEG/UserControls/AnvPlayerService.cs`,
method `PollingDecodeFrameAsync()`, nhánh `else if (srcW > 0 && srcH > 0)` (khi `controlReady`).

Constraint quan trọng: fix KHÔNG được đổi cơ chế resize khỏi `sws_scale` (FFmpeg) — chỉ đổi CÁCH TÍNH
`dstW/dstH` truyền vào. `SwsCacheState` (rebuild context chỉ khi src/dst size đổi) không bị ảnh hưởng
tần suất rebuild vì `ctrlW/ctrlH` đã được làm tròn bội số 16 từ trước (`AnvPlayer.cs` `_cachedWidth`).

## Áp dụng lại (How to reuse)

- Khi 1 pipeline có NHIỀU bước scale/resize độc lập (decode-time + render-time, hoặc bất kỳ 2 tầng nào
  đều tự ý resize) — PHẢI xác nhận CẢ HAI dùng CÙNG chiến lược (Uniform-fit letterbox vs Fill/stretch),
  không được để mỗi tầng tự quyết định độc lập. Grep comment "FIX", "RAM leak", "BUG-XXX" xung quanh mã
  resize để hiểu ý đồ thiết kế gốc trước khi thêm/sửa tầng resize khác — dễ có trường hợp 1 tầng được
  sửa vì lý do A (VD tối ưu RAM) mà không ai đối chiếu lại tầng kia đã giả định aspect ratio nào.
- Triệu chứng "ảnh mờ" + "độ phân giải không đúng thực tế" (không phải crash, không phải distortion rõ
  rệt) khi có pipeline decode→render 2 tầng → nghi ngờ NGAY 2 tầng đang dùng chiến lược scale khác nhau
  (1 bên giữ aspect ratio, 1 bên stretch fill) trước khi nghi ngờ chất lượng codec/bitrate camera.
- Đọc comment trong `Render()`/hàm vẽ cuối cùng TRƯỚC để biết ý đồ hiển thị thật sự (letterbox hay
  fill) — rồi mới sửa bước decode cho khớp, không phải ngược lại (đổi Render để khớp decode có thể phá
  vỡ hành vi UI cố ý "không có black bar" đã port từ WinForms).

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Đừng nhầm với GOTCHAS.md G008 (cap 640×360 khi control CHƯA layout xong — nhánh `!controlReady`) —
  đó là nhánh KHÁC, không bị ảnh hưởng bởi fix này. Fix này chỉ đổi nhánh `controlReady` (control đã có
  Bounds hợp lệ).
- ⚠️ `Kztek.Cameras.Avalonia` là BaseLIB dùng chung nhiều project KZTEK — sửa ở đây ảnh hưởng rộng hơn
  1 project. Không đổi public API/signature, chỉ đổi công thức tính bên trong — rủi ro thấp nhưng nên
  thông báo team khác dùng chung lib.
- ⚠️ Hiện tượng "giật" đi kèm CHƯA xác nhận được root cause cụ thể chỉ bằng đọc code — cần QA test với
  camera thật để đo lại sau fix (loại bỏ lớp upscale thứ 2 giảm khối lượng xử lý/frame, có thể giảm giật
  như tác dụng phụ, nhưng chưa verify).

## Tham chiếu

- `Kztek.Camera/1.Source/Kztek.Cameras.Avalonia/Players/FFMPEG/UserControls/AnvPlayerService.cs` —
  `PollingDecodeFrameAsync()` (~dòng 394-508, fix tại nhánh `controlReady`, dòng ~449-457)
- `Kztek.Camera/1.Source/Kztek.Cameras.Avalonia/Players/FFMPEG/UserControls/AnvPlayer.cs` — `Render()`
  (~dòng 275-315, comment gốc xác nhận ý đồ Stretch=Fill)
- `docs/bugs/BUG-005-camera-blur-wrong-resolution-stutter.md` (parking-v8-app-avalonia)
- Project liên quan: parking-v8-app-avalonia, session 2026-07-21
