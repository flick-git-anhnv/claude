---
category: camera-integration
tags: [x11, xrandr, shm, screen-capture, resolution, linux, xgetgeometry]
severity: high
created: 2026-07-23
updated: 2026-07-23
project-origin: iPGSv4 / IPGS.RemoteControl.ZcuAgent
---

# X11ScreenCapturer: ScreenSize cache cũ khi user đổi độ phân giải hoặc xoay màn hình lúc agent đang chạy

## Tình huống gặp phải

Đang fix bug remote-control của ZCU agent (Linux X11). Khi user dùng `xrandr` để xoay màn hình ZCU từ landscape → portrait (hoặc đổi resolution) trong lúc agent đang stream, phía CCU không xem được nữa (ảnh đen hoặc X error).

## Triệu chứng / Lỗi

- CCU nhận frame đen hoặc bị cắt sau khi ZCU đổi orientation xrandr.
- Log X error lặp liên tục: `request_code=73` (X_GetImage), `error_code=8` (BadMatch) — vô hạn, không tự phục hồi.
- Agent restart sau khi màn hình đã ở portrait → detect ĐÚNG ngay (vì `XOpenDisplay` populate cache mới). Nhưng khi xoay từ portrait → landscape MÀ KHÔNG restart → BadMatch liên tục mãi mãi.

## Nguyên nhân gốc rễ (Root Cause)

`X11ScreenCapturer.ScreenSize` được đọc **một lần duy nhất** trong `Initialize()` qua `XDisplayWidth`/`XDisplayHeight`, rồi cache mãi mãi suốt phiên.

Sau khi `xrandr` thay đổi resolution/orientation:
1. **SHM path**: buffer `_shmXImage` vẫn có kích thước cũ — `XShmGetImage` đọc ngoài vùng drawable → X error / ảnh sai.
2. **XGetImage path**: `CaptureXGetImage()` gọi `XGetImage(..., w, h, ...)` với `w`/`h` cũ — nếu root window đã nhỏ hơn, request vượt bounds.

## ⚠️ GOTCHA QUAN TRỌNG: XDisplayWidth/XDisplayHeight là MACRO cache — KHÔNG dùng để detect live resolution change

`XDisplayWidth(display, screen)` và `XDisplayHeight(display, screen)` trong Xlib là **client-side macros** đọc struct `Display*` được populate **DUY NHẤT** lúc `XOpenDisplay()`. Chúng KHÔNG gửi request lên X server, và KHÔNG BAO GIỜ tự cập nhật khi RandR đổi resolution/rotation trong khi kết nối đang mở.

Hệ quả: fix đầu tiên dùng `XDisplayWidth`/`XDisplayHeight` mỗi frame để detect change đã SAI — giá trị luôn là kích thước tại thời điểm `XOpenDisplay()`, không phản ánh thực tế sau khi màn hình xoay.

**PHẢI dùng `XGetGeometry`** — đây là real round-trip lên X server, luôn trả về kích thước CURRENT của drawable (root window), phản ánh đúng sau khi RandR thay đổi.

## Giải pháp đúng

### 1. Thêm P/Invoke `XGetGeometry` vào `X11Interop.cs`

```csharp
/// <summary>
/// Queries the current geometry of a drawable directly from the X server (real round-trip).
/// GOTCHA: XDisplayWidth/XDisplayHeight là macro cache client-side, KHÔNG dùng để detect
/// live resolution change — PHẢI dùng XGetGeometry (request thật lên server).
/// Returns non-zero (Status) on success, 0 on error.
/// </summary>
[DllImport(Lib)]
public static extern int XGetGeometry(IntPtr display, IntPtr drawable,
    out IntPtr root, out int x, out int y,
    out uint width, out uint height, out uint borderWidth, out uint depth);
```

### 2. Sửa `Capture()` — dùng `XGetGeometry` + throttle mỗi N frame

```csharp
// Check resolution every ResolutionCheckInterval frames (không phải mỗi frame)
// XGetGeometry là round-trip (~100–300 µs trên LAN) — throttle 1 lần/giây (ở 15fps) là đủ
private const int ResolutionCheckInterval = 15;
private int _framesSinceResolutionCheck;

public CapturedFrame? Capture()
{
    _framesSinceResolutionCheck++;
    if (_framesSinceResolutionCheck >= ResolutionCheckInterval)
        _framesSinceResolutionCheck = 0;

    uint currentW, currentH;
    if (_framesSinceResolutionCheck == 0 &&
        X11.XGetGeometry(_display, _rootWindow,
            out _, out _, out _, out currentW, out currentH, out _, out _) != 0 &&
        (currentW != (uint)ScreenSize.Width || currentH != (uint)ScreenSize.Height))
    {
        _logger.LogInformation(
            "Screen resolution changed: {OldW}x{OldH} → {NewW}x{NewH}, reinitializing capture",
            ScreenSize.Width, ScreenSize.Height, currentW, currentH);

        ScreenSize = new ScreenSize((int)currentW, (int)currentH);

        if (_useSHM)
        {
            CleanupSHM();
            if (!TryInitSHM((int)currentW, (int)currentH))
            {
                _logger.LogWarning(
                    "SHM reinit failed after resolution change — falling back to XGetImage for this session");
                _useSHM = false;
            }
        }
    }

    return _useSHM ? CaptureSHM() : CaptureXGetImage();
}
```

## Áp dụng lại (How to reuse)

- Bất kỳ X11 capturer nào cache `ScreenSize`: PHẢI dùng `XGetGeometry` (không phải `XDisplayWidth`/`XDisplayHeight`) để detect live resolution change.
- Throttle `XGetGeometry` mỗi N frame (không phải mỗi frame) để giảm round-trip overhead trên kết nối LAN.
- Sau khi phát hiện đổi resolution: nếu dùng SHM → `CleanupSHM()` + `TryInitSHM(newW, newH)`, thất bại → `_useSHM = false` (fallback XGetImage, tiếp tục capture được).

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ **`XDisplayWidth`/`XDisplayHeight` là MACRO cache, KHÔNG phải round-trip**: dùng chúng để detect live change là **SAI HOÀN TOÀN** — chúng luôn trả về giá trị tại thời điểm `XOpenDisplay()`.
- ⚠️ **`XGetGeometry` là round-trip thật**: cost ~100–300 µs trên LAN — throttle mỗi 15 frame để tránh overhead mỗi frame.
- ⚠️ **Race condition**: KHÔNG cần lock thêm vì class doc đã quy định `Initialize()` và `Capture()` phải gọi từ cùng 1 thread — reinit trong chính `Capture()` là safe.
- ⚠️ **`XDisplayWidth`/`XDisplayHeight` VẪN ĐÚNG trong `Initialize()`**: tại thời điểm `XOpenDisplay()` vừa gọi xong, cache chứa đúng giá trị ban đầu — chỉ không nên dùng sau đó để detect change.
- ⚠️ **`CapturedFrame.Width/Height`**: `CopyPixels()` đọc từ `XImageHeader` thực tế — sau reinit, frame tự phản ánh đúng resolution mới.

## Tham chiếu

- Project: iPGSv4 / IPGS.RemoteControl.ZcuAgent
- Files: `IPGS.RemoteControl.ZcuAgent/Capture/X11ScreenCapturer.cs`, `IPGS.RemoteControl.ZcuAgent/Interop/X11Interop.cs`
- Related lesson: `x11-xshmattach-async-baderror-crashes-process.md` (cùng X11/SHM context)
