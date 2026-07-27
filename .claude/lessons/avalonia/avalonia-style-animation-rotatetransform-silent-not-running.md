---
category: avalonia
tags: [animation, keyframe, rotatetransform, spinner, dispatchertimer, silent-failure]
severity: medium
created: 2026-07-26
updated: 2026-07-26
project-origin: App-Access-V2 (iAccessDesktopv2.Avalonia — STEP-6.1 migrate FrmLoading)
---

# Style Animation KeyFrame `RotateTransform.Angle` không chạy (silent) trên Avalonia 12.1 — spinner đứng hình

## Tình huống gặp phải

> Đang làm gì? Tính năng gì? Môi trường nào?

Migrate `FrmLoading` (WinForms, PictureBox + loading.gif) sang Avalonia 12.1.0 / net8.0. `loading.gif` không tồn tại trong repo (nguồn `Image.FromFile` runtime, catch nuốt lỗi) → thay bằng spinner `Arc` xoay thuần XAML theo recipe phổ biến: `Window.Styles` → `Style Selector="Arc#Spinner"` → `Style.Animations` → `Animation Duration="0:0:1.2" IterationCount="INFINITE"` với KeyFrame Setter `RotateTransform.Angle` 0 → 360.

## Triệu chứng / Lỗi

> Lỗi hiện ra như thế nào? Exception message? Behavior sai?

```
Build 0 error, 0 warning liên quan. Window mở bình thường, Arc render đúng.
Nhưng spinner ĐỨNG HÌNH hoàn toàn — screenshot chụp cách nhau đúng NỬA CHU KỲ
(0.6s trên chu kỳ 1.2s → lẽ ra gap arc phải lệch 180°) cho hình y hệt nhau.
Không exception, không log, không binding error — silent.
```

Thử cả 2 biến thể đều không xoay:
- Có `RenderTransform="rotate(0deg)"` local trên Arc
- Bỏ hẳn RenderTransform local

## Nguyên nhân gốc rễ (Root Cause)

> Tại sao xảy ra?

Animator composite của property ảo "RotateTransform.Angle" trong style Animation không kích hoạt trên `Arc` trong app này ở Avalonia 12.1 — root cause bên trong framework chưa xác định được từ phía app (không có API/log nào báo animation có chạy hay không). Điểm quan trọng: **thất bại hoàn toàn im lặng**, mọi thứ khác của style (Setter màu, Classes) vẫn hoạt động.

## Giải pháp

> Làm gì để fix?

Xoay bằng code-behind với `DispatcherTimer` — deterministic, không phụ thuộc hệ animation của style:

```csharp
private readonly DispatcherTimer _spinTimer;
private readonly RotateTransform _spinTransform = new();

// trong ctor sau InitializeComponent():
Spinner.RenderTransform = _spinTransform;          // RenderTransformOrigin mặc định = center
_spinTimer = new DispatcherTimer { Interval = TimeSpan.FromMilliseconds(33) }; // 30fps
_spinTimer.Tick += (_, _) => _spinTransform.Angle = (_spinTransform.Angle + 10) % 360; // 360°/1.2s
_spinTimer.Start();
Closed += (_, _) => _spinTimer.Stop();
```

Verify bằng pixel-diff 2 screenshot cách 450ms: 76 điểm khác nhau (trước đó 0) + gap arc đổi vị trí rõ trong ảnh.

## Áp dụng lại (How to reuse)

> Lần sau gặp tình huống tương tự, làm gì ngay lập tức?

- Cần spinner/rotation ở app Avalonia 12 → dùng thẳng DispatcherTimer code-behind hoặc `ProgressBar IsIndeterminate`, đừng tin recipe style Animation KeyFrame `RotateTransform.Angle` mà không verify chạy thật.
- Verify animation PHẢI bằng 2 ảnh chụp lệch thời gian KHÔNG phải bội số chu kỳ (chọn ~1/4 chu kỳ) — lệch đúng nửa/nguyên chu kỳ vẫn phát hiện được đứng hình nhưng dễ nhầm pha.
- Animation "chạy hay không" là silent — không có warning; luôn kiểm chứng bằng runtime capture.

## Chú ý / Cạm bẫy (Gotchas)

> Điều gì dễ sai khi apply solution này?

- ⚠️ **Bẫy verify kèm theo (G008):** `Process.MainWindowHandle` trỏ về window ACTIVE gần nhất — script capture xác định window đích bằng "loại trừ MainWindowHandle" sẽ bắt nhầm window (ở đây diff nhầm trên gallery tĩnh → 2 lần "diff=0" giả). Phải match window theo title qua `EnumWindows` + `GetWindowTextW`, in title ra log và MỞ XEM file ảnh trước khi kết luận.
- ⚠️ Nhớ `Stop()` timer trong `Closed` — timer sống theo Dispatcher, không tự chết theo window.
- ⚠️ `RotateTransform` mutate `Angle` trực tiếp là đủ invalidate render — không cần gán lại `RenderTransform`.

## Tham chiếu

- Project liên quan: App-Access-V2 — `iAccessDesktopv2.Avalonia/Views/LoadingWindow.axaml(.cs)`
- GOTCHAS nội bộ: `.claude/shared/GOTCHAS.md` G007 (animation) + G008 (MainWindowHandle)
