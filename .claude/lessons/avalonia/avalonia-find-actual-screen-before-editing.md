---
category: avalonia
tags: [component-discovery, canvas, zone-editor, pointer-events]
severity: high
created: 2026-06-24
updated: 2026-06-24
project-origin: iPGSv4 — IPGSUseCam
---

# Xác định đúng màn hình/component trước khi sửa tính năng UI

## Tình huống gặp phải

> Thêm tính năng move + resize cho các zone box trên ảnh camera trong IPGSUseCam (Avalonia).

User yêu cầu thêm move/resize cho zone box (các hình chữ nhật vẽ lên ảnh camera). Codebase có component `KzZoneEditor` trong `KztekComponentAvalonia` — tên nghe có vẻ đúng → sửa file đó.

## Triệu chứng / Lỗi

```
App chạy lại nhưng tính năng move/resize vẫn không có.
Build thành công, DLL đã copy vào output — nhưng không có hiệu quả.
```

## Nguyên nhân gốc rễ (Root Cause)

`KzZoneEditor` là component **được định nghĩa nhưng chưa được dùng ở đâu** trong `IPGSUseCam`. Màn hình thực tế hiển thị zone box là `CameraSettingWindow.axaml.cs` — dùng `ConfigRegion` + `Border` trực tiếp trên `Canvas`, không liên quan đến `KzZoneEditor`.

Grep `KzZoneEditor` trong toàn project → chỉ thấy file định nghĩa, không thấy file nào `using` hoặc `<kz:KzZoneEditor>`.

## Giải pháp

**Bước 1 — Xác nhận component nào thực sự đang chạy trước khi sửa:**

```bash
# Tìm file nào dùng ConfigRegion (class zone đang dùng trong app)
grep -r "ConfigRegion" IPGSUseCam/Views/ --include="*.cs" -l

# Xem danh sách window Avalonia trong app
ls IPGSUseCam/Views/*.axaml
```

**Bước 2 — Mở file đúng (`CameraSettingWindow.axaml.cs`) và thêm:**

```csharp
// Interaction modes
private enum InteractionMode { None, Drawing, Moving, Resizing }
private InteractionMode _mode = InteractionMode.None;
private int    _activeIndex = -1;
private Point  _interactOrigin;
private IpgsRect _rectAtDragStart;
private bool   _rL, _rR, _rT, _rB;
private const double HandleTol = 10.0;
```

`OnCanvasPointerPressed` → hit-test region index → nếu trúng: set Moving/Resizing; nếu miss: start Drawing.

`OnCanvasPointerMoved` → cập nhật `Canvas.SetLeft/Top` và `border.Width/Height` trực tiếp.

`OnCanvasPointerReleased` → reset mode, cập nhật `_regions[i].Rect`.

## Áp dụng lại (How to reuse)

- **Trước khi sửa bất kỳ tính năng UI nào** → chạy grep tên class/feature đang thấy trong app để tìm file nguồn thực sự:
  ```bash
  grep -r "ConfigRegion\|ZoneEditor\|canvas\|PointerPressed" IPGSUseCam/Views/ -l
  ```
- Khi tên component nghe "có vẻ đúng" (vd: `KzZoneEditor`) → **bắt buộc verify** nó có được dùng trong app không trước khi sửa.
- Component trong thư viện shared (`KztekComponentAvalonia`) có thể tồn tại nhưng **chưa được tích hợp** vào app chính.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Build thành công + DLL copy vào output **KHÔNG có nghĩa** feature đang được dùng — component có thể không được instantiate.
- ⚠️ `KzZoneEditor` (component library) và zone editing thực tế trong app (`CameraSettingWindow`) là **hai thứ khác nhau** — dù cùng tên miền.
- ⚠️ Khi app đang chạy, build sẽ fail do lock file — phải đóng app trước khi rebuild.
- ⚠️ `Border.IsHitTestVisible` mặc định là `true` — các `Border` region sẽ chặn pointer event của `Canvas` nếu không đặt `IsHitTestVisible = false` hoặc xử lý ở canvas level.

## Tham chiếu

- File thực tế: `IPGSUseCam/Views/CameraSettingWindow.axaml.cs`
- Component chưa dùng: `KztekComponentAvalonia/Controls/KzZoneEditor.axaml.cs`
- WinForms reference có đầy đủ move/resize: `IPGSUseCam/Forms/DataForm/KZUI_DragDropPictureBox.cs`
