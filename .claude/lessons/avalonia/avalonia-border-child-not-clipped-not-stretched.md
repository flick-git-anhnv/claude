---
category: avalonia
tags: [border, clipping, stretch, camera-preview, cornerradius]
severity: medium
created: 2026-07-17
updated: 2026-07-17
project-origin: parking-v8-app-avalonia
---

# Border bo góc (CornerRadius) không tự clip nội dung; Control gán động vào Border.Child không tự Stretch

## Tình huống gặp phải

Camera live view (`CameraView.axaml` trong `ParkingV8.UI`) hiển thị video RTSP qua control
`AnvPlayer` được gán động vào `Border Name="LiveHost"` bằng code-behind:
`LiveHost.Child = camera.videoSourcePlayer as Control;`. Border cha (`RootBorder`) và
`LiveHost` đều có `CornerRadius` bo góc.

## Triệu chứng / Lỗi

User báo: khung xem camera bị "tràn border" và hình ảnh live hiển thị như một hình chữ nhật
nhỏ bên trong, không chiếm trọn khung bo góc — video tràn ra ngoài góc bo tròn thay vì bị cắt gọn.

## Nguyên nhân gốc rễ (Root Cause)

1. Avalonia `Border` với `CornerRadius` KHÔNG tự động clip nội dung con theo góc bo —
   phải set `ClipToBounds="True"` tường minh, khác với suy nghĩ mặc định "bo góc thì tự cắt".
2. Khi gán `Border.Child` bằng code-behind cho 1 control có sẵn (video player control),
   nếu control đó có thiết lập alignment khác Stretch từ nơi khác (hoặc do thư viện ngoài),
   nó không tự lấp đầy toàn bộ vùng Border cha.

## Giải pháp

```xml
<Border Name="RootBorder" CornerRadius="8" ClipToBounds="True"> <!-- thêm ClipToBounds -->
  <Grid Name="LiveRegion" ClipToBounds="True">
    <Border Name="LiveHost" CornerRadius="6" ClipToBounds="True" />
  </Grid>
</Border>
```

```csharp
if (camera.videoSourcePlayer is Control liveVideoControl)
{
    liveVideoControl.HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Stretch;
    liveVideoControl.VerticalAlignment = Avalonia.Layout.VerticalAlignment.Stretch;
    LiveHost.Child = liveVideoControl;
}
```

1. Thêm `ClipToBounds="True"` vào mọi `Border`/`Grid` bo góc có chứa nội dung động (video, image lớn).
2. Khi gán `Control` động vào `Border.Child`/`ContentControl.Content`, ép tường minh
   `HorizontalAlignment`/`VerticalAlignment = Stretch` trước khi gán — không tin vào default.

## Áp dụng lại (How to reuse)

- Khi thấy Border/Panel có `CornerRadius` chứa video/ảnh/preview động → luôn kiểm tra có
  `ClipToBounds="True"` chưa trước khi debug sâu hơn.
- Khi gán Control động (không qua XAML binding) vào 1 container layout → luôn set rõ
  HorizontalAlignment/VerticalAlignment=Stretch ngay tại điểm gán, đừng phụ thuộc default.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ `ClipToBounds` set trên Border cha KHÔNG tự lan xuống Grid/Border con lồng bên trong —
  phải set từng lớp lồng nhau nếu mỗi lớp đều có bo góc riêng.
- ⚠️ Fix này chỉ chắc chắn giải quyết phần "tràn góc bo" và "không lấp đầy do alignment sai";
  nếu còn hiện tượng hình chữ nhật đen do render dở dang (stale WriteableBitmap frame), đó là
  bug render riêng ở `AnvPlayer`/`SharedCameraStreamSession`, cần điều tra thêm bằng cách chạy
  app thật với camera thật.

## Tham chiếu

- File: `src/ParkingV8.UI/Controls/Axaml/CameraView.axaml`, `src/ParkingV8.UI/Controls/Cs/CameraView.axaml.cs`
- Project liên quan: parking-v8-app-avalonia
