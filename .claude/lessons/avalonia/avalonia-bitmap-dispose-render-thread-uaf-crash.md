---
category: avalonia
tags: [bitmap, dispose, skiasharp, render-thread, compositor, use-after-free, sigsegv, crash-dump]
severity: critical
created: 2026-08-11
updated: 2026-08-12
project-origin: parking-v8-app-avalonia (ParkingV8.App)
---

# Dispose Bitmap ngay sau khi gán property mới → SIGSEGV trong libSkiaSharp.so trên render thread (Linux)

## Tình huống gặp phải

App ParkingV8.App (Avalonia 11, deploy Linux Ubuntu 22.04 + Intel GPU) bị văng ngẫu nhiên ngoài field.
Trước đó team đã nghi ngờ và thay `SkiaSharp` → `ImageSharp` cho phần encode ảnh (commit "Replace
SkiaSharp with ImageSharp and add encoder") nhưng app vẫn văng — chứng tỏ nguyên nhân không nằm ở
encoder mà sâu hơn, trong chính renderer nội bộ của Avalonia.

## Triệu chứng / Lỗi

Phân tích file `.crash` (Ubuntu apport, chứa core dump base64+gzip nhúng sẵn — tự viết script Python
giải nén ELF core, parse `NT_PRSTATUS`/`NT_FILE` để lấy register + backtrace vì không có gdb trên máy dev):

```
Signal: 11 (SIGSEGV), si_code=1 (SEGV_MAPERR)
Crash tại thread RIỆNG (render thread, tid khác main UI thread)
RIP nằm trong libSkiaSharp.so (native, không có debug symbol — .dynsym chỉ có 1 export)
fault_addr nằm trong 1 register vừa được dùng để dereference
```

Không phải exception .NET — crash native, không log được exception message, chỉ có file `.crash`.

## Nguyên nhân gốc rễ (Root Cause)

Toàn bộ `EntryLaneViewModel.cs` / `ExitLaneViewModel.cs` có pattern lặp lại ở property setter của
mọi `Bitmap?` binding (PlateInImage, CapturedImage, EntryPlateImage, EntryPanoramaImage,
EntryVehicleImage, PlateOutImage, ExitPanoramaImage, ExitVehicleImage — 8 chỗ), cộng thêm 1 chỗ thứ 9
phát hiện SAU khi audit lại (`kioskQrImage?.Dispose()` trong `KioskOutLaneViewModel.ApplyQrCode()` —
ảnh QR thanh toán, bind vào `KioskQrImage`) — grep ban đầu `old\?\.Dispose\(\)` bỏ sót vì tên biến
field khác. **Bài học: audit pattern này phải grep rộng `\.Dispose\(\)` trên toàn bộ file có field
`Bitmap?`, không chỉ theo tên biến tạm cụ thể** (`old`, hay field riêng như `kioskQrImage`):

```csharp
var old = entryPlateImage;
if (SetProperty(ref entryPlateImage, value))
{
    old?.Dispose();   // dispose NGAY trên UI thread, ngay sau khi set property mới
}
```

Comment cũ giả định: "gán mới rồi dispose cũ, cùng UI thread, tuần tự" = an toàn vì "render frame
sau sẽ thấy giá trị mới". **Giả định này SAI với Avalonia 11+ compositor renderer**: renderer chạy
trên **compositor/render thread riêng**, bất đồng bộ với UI thread, và có thể **trễ 1 hoặc nhiều
frame** so với thời điểm UI thread set property — đặc biệt dưới tải GPU/driver (Intel `iris_dri.so`
trên Linux, camera decode threads chạy song song). Khi UI thread `Dispose()` native Skia
texture/pixmap ngay sau khi set property mới, render thread có thể **vẫn đang đọc buffer cũ đó** để
composite frame trước → use-after-free → SIGSEGV trong `libSkiaSharp.so`.

Có lesson cũ [[avalonia-writeablebitmap-binding-not-disposed-leak]] nói "gán mới → dispose cũ, cùng
UI thread" là pattern ĐÚNG để tránh leak — điều đó vẫn đúng để tránh **leak**, nhưng **không đủ** để
tránh **race với compositor thread** khi ảnh được gán/thay liên tục (nhiều event/giây) hoặc dưới tải
GPU cao. Hai lesson bổ sung nhau, không mâu thuẫn: lesson kia áp dụng cho stream tốc độ cao cần
kiểm soát leak chủ động; lesson này áp dụng khi correctness (không crash) quan trọng hơn việc tối ưu
GC — với ảnh event (vào/ra xe, không phải stream nhiều fps), rủi ro leo RAM tạm thời trước khi GC
chạy là chấp nhận được, còn UAF crash thì không.

## Giải pháp

Bỏ hoàn toàn `old?.Dispose()` ở property setter của Bitmap dùng để bind UI — để GC/finalizer của
`Avalonia.Media.Imaging.Bitmap` tự thu hồi native memory khi không còn reference nào (managed +
compositor) trỏ tới:

```csharp
public Bitmap? EntryPlateImage
{
    get => entryPlateImage;
    private set
    {
        // KHÔNG dispose bitmap cũ ở đây — compositor render thread có thể còn đang đọc
        // native Skia texture của nó (trễ 1+ frame). Để GC/finalizer tự thu hồi.
        if (SetProperty(ref entryPlateImage, value))
        {
            RaisePropertyChanged(nameof(HasEntryPlateImage));
        }
    }
}
```

Áp dụng cho toàn bộ 8 property tương tự trong `EntryLaneViewModel.cs` và `ExitLaneViewModel.cs`, và
`kioskQrImage` trong `KioskOutLaneViewModel.ApplyQrCode()` (chỗ thứ 9). `KioskInLaneViewModel.cs` /
`KioskOutLaneViewModel.cs` kế thừa `EntryLaneViewModel`/`ExitLaneViewModel` và chỉ override các
computed getter (`KioskFlowImage1/2`) — không có setter riêng nên tự động hưởng fix từ base, không
cần sửa thêm gì ở lớp Kiosk (trừ chỗ `kioskQrImage` là field riêng của `KioskOutLaneViewModel`).

## Áp dụng lại (How to reuse)

- Khi thấy pattern `var old = ...; SetProperty(...); old?.Dispose();` trên một property
  `Bitmap`/`WriteableBitmap`/`RenderTargetBitmap` **đang bind trực tiếp vào `Image.Source` hiển thị
  trên UI** → nghi ngờ ngay, không mặc định là an toàn dù code chạy trên UI thread.
- Phân biệt 2 trường hợp trước khi quyết định dispose hay không:
  - **Stream tốc độ cao (10+ fps, camera live view)** → PHẢI dispose để tránh leak (native buffer
    lớn, GC không theo kịp) — xem [[avalonia-writeablebitmap-binding-not-disposed-leak]], nhưng cần
    chấp nhận rủi ro race nếu tải GPU cao, hoặc cân nhắc double-buffer.
  - **Ảnh theo sự kiện (event-driven, vài lần/phút như vào/ra xe)** → KHÔNG dispose thủ công, để GC
    tự lo — an toàn tuyệt đối với render thread, rủi ro leak không đáng kể vì tần suất thấp.
- Crash native (SIGSEGV, không có .NET exception/stack trace managed) trong `libSkiaSharp.so` trên
  Linux, đặc biệt trên **thread khác main UI thread** → luôn nghi ngờ use-after-free của native Skia
  resource (Bitmap/Image/Surface bị dispose sớm), không phải lỗi renderer/driver ngẫu nhiên.
- Script phân tích file `.crash` Ubuntu (giải nén core dump nhúng base64+gzip, parse ELF NT_PRSTATUS
  để lấy register/backtrace không cần gdb) đã lưu tạm — có thể viết lại nhanh nếu gặp `.crash` khác:
  đọc từ `CoreDump: base64` block, `zlib.decompressobj(16 + zlib.MAX_WBITS)`, parse PT_NOTE (NT_FILE
  cho maps, NT_PRSTATUS cho registers mỗi thread offset 112 = 27 x uint64 theo thứ tự
  r15..r14..r13..r12..rbp..rbx..r11..r10..r9..r8..rax..rcx..rdx..rsi..rdi..orig_rax..rip..cs..eflags..rsp..ss..fs_base..gs_base..ds..es..fs..gs).

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ "Cùng UI thread, tuần tự (gán mới rồi dispose cũ)" **không loại bỏ được race với compositor
  thread** — đây là nhầm lẫn phổ biến vì tưởng compositor render đồng bộ theo UI thread, nhưng Avalonia
  11 dùng composition thread riêng, có buffer/latency riêng.
- ⚠️ Trên máy dev Windows, race này **khó/không tái hiện được** vì Avalonia dùng driver Direct3D/ANGLE
  khác Linux + Intel `iris_dri.so` (timing giữa UI thread và compositor thread khác hẳn) — không thể
  dùng "chạy thử trên Windows không crash" làm bằng chứng bug không tồn tại.
- ⚠️ `.dynsym` của `libSkiaSharp.so` build release hầu như không có symbol function thật (chỉ 1 export
  "rác") — không resolve được tên hàm chính xác từ offset, chỉ xác định được "crash trong module nào,
  thread nào, do dereference con trỏ nào" — đủ để chẩn đoán pattern nhưng không đủ để trace dòng code
  Skia cụ thể.
- ⚠️ Muốn stress-test lại race này: dùng tính năng có sẵn `Ctrl+F7` (Stress Test) trong
  `MainShellWindowViewModel.StartStressTestAsync()` — lặp `SimulateCardInAsync`/`SimulateCardOutAsync`
  đẩy nhanh tốc độ thay Bitmap. Lưu ý: `SimulateCardInAsync` gọi `ProcessManualWriteInAsync(simulateDispenserButton: true)`
  → chạy **toàn bộ flow thật** (ghi API backend thật, nhả thẻ thật qua MT166) — cần xác nhận với
  business trước khi chạy lặp nhiều lần trên thiết bị/backend thật, không chỉ là test UI thuần.

## Tham chiếu

- File sửa: `src/ParkingV8.App/Lanes/ViewModels/EntryLaneViewModel.cs`,
  `src/ParkingV8.App/Lanes/ViewModels/ExitLaneViewModel.cs` (8 property setter)
- Crash dump: `_opt_kztek_parkingv8_ParkingV8.App.1000/_opt_kztek_parkingv8_ParkingV8.App.1000.crash`
- Lesson liên quan: [[avalonia-writeablebitmap-binding-not-disposed-leak]] (trường hợp ngược lại — cần
  dispose để tránh leak khi stream tốc độ cao)
- Project: parking-v8-app-avalonia / ParkingV8.App
