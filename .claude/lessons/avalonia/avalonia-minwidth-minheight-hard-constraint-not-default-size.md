---
category: avalonia
tags: [minwidth, minheight, layout, video-player, winforms-port, camera]
severity: high
created: 2026-07-17
updated: 2026-07-17
project-origin: parking-v8-app-avalonia (thư viện dùng chung Kztek.Cameras.Avalonia)
---

# MinWidth/MinHeight trong Avalonia là RÀNG BUỘC CỨNG, không phải "kích thước khởi tạo" như WinForms Width/Height

## Tình huống gặp phải

Port control video (`AnvPlayer`, hiển thị RTSP camera) từ WinForms sang Avalonia. Ở bản
WinForms gốc, constructor set `Width = 640; Height = 480;` làm kích thước khởi tạo — khi đặt
control trong container có `Dock=Fill`/`Anchor` phù hợp, WinForms tự co giãn nó nhỏ lại bình
thường theo container.

Khi port, lập trình viên đổi thẳng `Width/Height` → `MinWidth/MinHeight` (Avalonia không có
setter `Width/Height` "mềm" tương đương), kèm comment "giống WinForms Width=640/Height=480".

## Triệu chứng / Lỗi

Camera tile nhỏ (preview ~350×120px trong sidebar) hiển thị:
- **Nếu container cha không `ClipToBounds`**: video tràn hẳn ra ngoài border (che khuất UI khác).
- **Nếu container cha có `ClipToBounds="True"`**: video bị crop chỉ còn thấy 1 mảnh nhỏ/zoom
  cực sâu vào 1 góc của khung hình gốc (trông như "chỉ thấy 1 phần rất nhỏ của cảnh", khác hẳn
  full FOV khi so với VLC/nguồn RTSP gốc).

Hai triệu chứng nhìn rất khác nhau (tràn ra ngoài vs zoom hẹp) nhưng **cùng 1 nguyên nhân gốc** —
dễ khiến người debug tưởng đó là 2 bug riêng biệt, đi tìm sai hướng ở tầng decode/stretch/RTSP
stream thay vì tầng layout.

## Nguyên nhân gốc rễ (Root Cause)

`MinWidth`/`MinHeight` trong Avalonia không tương đương "kích thước mặc định ban đầu" như
WinForms `Width`/`Height` — đó là **ràng buộc cứng tối thiểu trong hệ thống layout**: dù
`HorizontalAlignment`/`VerticalAlignment = Stretch` và container cha nhỏ hơn nhiều, Avalonia
vẫn ép Arrange control tối thiểu bằng `MinWidth × MinHeight`, khiến nó luôn LỚN HƠN khung hiển
thị thực tế của container nhỏ.

Việc AnvPlayer tự lấy `Bounds.Width/Height` (đã bị ép tối thiểu 640×480) để quyết định
`destWidth/destHeight` cho FFmpeg decode/scale (`sws_scale`) càng khiến sai lệch: decode ra
đúng 640×480 (hoặc lớn hơn), nhưng panel hiển thị thật lại nhỏ hơn nhiều → phần thừa bị tràn/crop.

## Giải pháp

Xoá hẳn `MinWidth`/`MinHeight` cứng trong constructor — để control tự co giãn hoàn toàn theo
`HorizontalAlignment`/`VerticalAlignment = Stretch` (giá trị mặc định của Avalonia `Control`)
khớp với panel cha thật sự.

```csharp
// SAI (port trực tiếp từ WinForms Width/Height):
MinWidth  = 640;
MinHeight = 480;

// ĐÚNG — bỏ hẳn, để Stretch alignment tự quyết định kích thước theo container cha:
// (không set gì cả — Bounds.Width/Height sẽ phản ánh đúng kích thước panel cha)
```

1. Xác định control có `MinWidth`/`MinHeight` cứng port từ WinForms `Width`/`Height` không.
2. Xoá hẳn — không thay bằng giá trị nhỏ hơn "cho chắc", vì bất kỳ giá trị > 0 nào cũng có thể
   gây lỗi tương tự với container nhỏ hơn giá trị đó trong tương lai.
3. Nếu thực sự cần 1 kích thước tối thiểu hợp lý để tránh control co về 0×0 khi chưa có container
   nào ràng buộc (trường hợp dùng standalone/designer preview), dùng giá trị RẤT nhỏ (VD 1×1)
   thay vì kích thước "đẹp" như 640×480.

## Áp dụng lại (How to reuse)

- Khi port bất kỳ control WinForms nào có `Width = X; Height = Y;` trong constructor sang
  Avalonia → **KHÔNG** tự động đổi thành `MinWidth = X; MinHeight = Y;`. Cân nhắc bỏ hẳn, để
  layout Stretch tự quyết định.
- Khi thấy video/preview control bị tràn border HOẶC bị crop/zoom bất thường so với nguồn gốc,
  luôn kiểm tra `MinWidth`/`MinHeight`/`Width`/`Height` cứng trên chính control đó trước khi nghi
  ngờ tầng decode/stretch/RTSP — dùng Avalonia DevTools (F12) → chọn control → tab Layout để đọc
  trực tiếp `MinWidth`/`MinHeight` và so với `Bounds` thực tế của panel cha.
- Xem thêm [[avalonia-border-child-not-clipped-not-stretched]] — 2 lesson này cùng 1 chuỗi bug:
  thiếu `ClipToBounds` che giấu bug tràn thành "trông như ổn", rồi thêm `ClipToBounds` lại lộ ra
  triệu chứng crop/zoom của CHÍNH bug MinWidth/MinHeight này.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Đừng chỉ nhìn 1 triệu chứng rồi kết luận nguyên nhân — "tràn border" và "zoom/crop hẹp" có
  thể là 2 MẶT của CÙNG 1 bug tuỳ vào việc container cha có `ClipToBounds` hay không. Thêm
  `ClipToBounds` để fix tràn border có thể vô tình "che" triệu chứng cũ và lộ ra triệu chứng mới
  (zoom/crop) từ đúng 1 nguyên nhân gốc chưa được xử lý.
- ⚠️ Nếu control tự đọc `Bounds.Width/Height` của chính nó để quyết định resolution decode/render
  (pattern phổ biến ở video player), một MinWidth/MinHeight cứng sẽ làm sai lệch luôn cả phần
  decode, không chỉ phần hiển thị — cần xoá đúng gốc, không patch ở tầng khác (VD ép Stretch từ
  bên ngoài chỉ che triệu chứng, không xoá được ràng buộc MinWidth/MinHeight bên trong).

## Tham chiếu

- File: `Kztek.Cameras.Avalonia/Players/FFMPEG/UserControls/AnvPlayer.cs` (thư viện BaseLIB dùng
  chung nhiều sản phẩm KZTEK — sửa ở đây ảnh hưởng mọi app tham chiếu, không chỉ 1 project)
- Project liên quan: parking-v8-app-avalonia (`src/ParkingV8.UI/Controls/Axaml/CameraView.axaml`)
- Liên quan: [[avalonia-border-child-not-clipped-not-stretched]]
