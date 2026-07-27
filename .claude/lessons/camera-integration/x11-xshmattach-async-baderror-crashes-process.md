---
category: camera-integration
tags: [x11, xshm, linux, p-invoke, async-error, screen-capture]
severity: critical
created: 2026-07-23
updated: 2026-07-23
project-origin: IPGS.RemoteControl.ZcuAgent
---

# X11 XShmAttach: lỗi BadAccess bất đồng bộ giết chết process trước khi fallback kịp chạy

## Tình huống gặp phải

Đang test `IPGS.RemoteControl.ZcuAgent` (screen capture daemon cho ZCU, chạy Ubuntu 22.04 X11)
trên máy thật kết nối qua SSH với `DISPLAY=:0`. Agent khởi động, cố khởi tạo MIT-SHM để
capture màn hình, rồi crash toàn bộ tiến trình ngay lập tức.

## Triệu chứng / Lỗi

```
X Error of failed request:  BadAccess (attempt to access private resource denied)
  Major opcode of failed request:  131 (MIT-SHM)
  Minor opcode of failed request:  1 (X_ShmAttach)
  Serial number of failed request: 15
  Current serial number in output stream: 16
```

Tiến trình chết hoàn toàn. Code fallback `CaptureXGetImage()` đã viết đúng nhưng **không
bao giờ được thực thi**.

## Nguyên nhân gốc rễ (Root Cause)

`XShmAttach` (libXext) là **request bất đồng bộ (asynchronous)**:

- Hàm trả về `true` **ngay lập tức** mà không đợi phản hồi từ X server.
- Lỗi `BadAccess` từ X server đến **sau**, dưới dạng một X error event bất đồng bộ.
- Xlib có **error handler mặc định**: nhận error event → in ra stderr → **gọi `exit()`**.
- `exit()` chạy trước khi code C# có cơ hội kiểm tra giá trị trả về hay chạy fallback.

Kết quả: logic fallback đã viết đúng nhưng không bao giờ được thực thi vì process đã bị
kill bởi Xlib default error handler trước đó. Đây là gotcha cổ điển của Xlib — tài liệu
đề cập nhưng không nổi bật.

## Giải pháp

**Bước 1:** Thêm P/Invoke `XSetErrorHandler` vào `X11Interop.cs`:

```csharp
public delegate int XErrorHandler(IntPtr display, IntPtr errorEvent);

[DllImport("libX11.so.6")]
public static extern IntPtr XSetErrorHandler(XErrorHandler? handler);
```

**Bước 2:** Trong `X11ScreenCapturer.cs`, thêm static error handler và flag:

```csharp
// Phải là static field để GC không thu hồi delegate khi đang hoạt động
private static volatile bool _shmErrorOccurred;
private static readonly X11.XErrorHandler _x11ErrorHandlerDelegate = OnX11Error;

private static int OnX11Error(IntPtr display, IntPtr errorEvent)
{
    _shmErrorOccurred = true;
    return 0; // Không gọi exit()
}
```

**Bước 3:** Trong `TryInitSHM()`, cài handler **trước** `XShmAttach`, rồi kiểm tra flag
**sau** `XSync`:

```csharp
_shmErrorOccurred = false;
X11.XSetErrorHandler(_x11ErrorHandlerDelegate);           // cài handler

if (!XShm.XShmAttach(_display, ref _shmInfo)) { CleanupSHM(); return false; }

X11.XSync(_display, false);   // buộc async error phải flush về ngay bây giờ

if (_shmErrorOccurred)
{
    _logger.LogWarning("XShmAttach rejected (async BadAccess) — fallback XGetImage");
    CleanupSHM();
    return false;
}
return true;
```

> **Tại sao cần `XSync`?** `XSync` flush toàn bộ request queue và **đợi tất cả reply +
> error event** từ X server về trước khi return — điều này buộc `BadAccess` phải trigger
> `OnX11Error` trong lời gọi `XSync`, không phải tại một điểm không xác định sau đó.

## Áp dụng lại (How to reuse)

- Khi thấy tiến trình **crash không có stack trace .NET** kèm dòng `X Error of failed request`
  → đây là Xlib default error handler, không phải exception C#.
- Mọi X11 request "cấp quyền truy cập" (Attach, Grab, ...) đều bất đồng bộ → cần pattern:
  **set custom handler → gọi request → XSync → check flag**.
- Luôn lưu delegate trong `static readonly` field để tránh GC thu hồi khi handler đang hoạt động.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ **KHÔNG** lưu delegate trong biến local — GC có thể thu hồi trước khi Xlib gọi handler,
  gây crash ngẫu nhiên kiểu `ExecutionEngineException`.
- ⚠️ Sau khi cài custom handler, **MỌI** X error tiếp theo (kể cả ngoài giai đoạn SHM setup)
  đều đi qua handler đó — handler chỉ set flag, không gọi exit, nên không ẩn lỗi thật nhưng
  cũng không abort process. Đây là trade-off chấp nhận được cho daemon capture.
- ⚠️ `XShmQueryExtension` trả về `true` ngay cả trên display không cho phép SHM (SSH forwarded
  X) — `QueryExtension` chỉ hỏi "extension có load không?", không kiểm tra permission attach.
  Phải thử `XShmAttach` thật và bắt lỗi như trên.
- ⚠️ `XShmDetach` cũng bất đồng bộ — nếu gọi `CleanupSHM` sau khi `_shmErrorOccurred = true`,
  `XShmDetach` sẽ thất bại (chưa attach thành công). Bọc trong `try/catch` trong `CleanupSHM`.

## Tham chiếu

- Xlib Programming Manual §8.4 — Error Handling
- `XSetErrorHandler(3)` man page
- Project liên quan: `IPGS.RemoteControl.ZcuAgent` — `Capture/X11ScreenCapturer.cs`, `Interop/X11Interop.cs`
