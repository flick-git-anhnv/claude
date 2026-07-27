---
category: avalonia
tags: [avalonia-12, visualroot, toplevelhost, showdialog, silent-failure, drawn-decorations]
severity: high
created: 2026-07-27
updated: 2026-07-27
project-origin: App-Access-V2 (migrate-avalonia, fix BUG-810-01)
---

# Avalonia 12.1: `VisualRoot` là `TopLevelHost`, KHÔNG phải `Window` — guard `VisualRoot is Window` chết im lặng

## Tình huống gặp phải

> Fix regression P1 (BUG-810-01) sau redesign Phase 8: từ AppShellWindow (shell thật) không mở được 2 dialog `PageSettingWindow`/`CheckInSettingWindow` — cả nút action lẫn menu chuột phải. Avalonia 12.1.0, Windows 11.

Code mở dialog dùng pattern phổ biến để lấy owner:

```csharp
if (ViewModel == null || VisualRoot is not Window owner) return;
_ = new PageSettingWindow(vm).ShowDialog(owner);
```

## Triệu chứng / Lỗi

```
Click nút / chọn menu → KHÔNG có gì xảy ra:
- Không window mới (EnumWindows + UIA xác nhận)
- Không exception, không log — "im lặng tuyệt đối"
- Verify qua --gallery (dev-mode) thì dialog mở bình thường → lọt qua review
```

## Nguyên nhân gốc rễ (Root Cause)

Avalonia 12.1 khi window dùng **drawn/managed decorations**, visual root của mọi control con là `Avalonia.Controls.TopLevelHost` (derive `Control`, quản lý Decorations/ResizeGrips/FullscreenState) — **KHÔNG phải `Window`**. Bằng chứng runtime từ shell thật:

```
VisualRoot            = Avalonia.Controls.TopLevelHost
TopLevel.GetTopLevel  = AppShellWindow   ← API đúng vẫn trả Window
FindAncestorOfType<Window> = AppShellWindow
```

Guard `VisualRoot is not Window` vì vậy LUÔN đúng → return im lặng. Gallery không dính vì mở dialog bằng `TopLevel.GetTopLevel(this)` hoặc `Show()` không owner.

Bẫy thứ 2 đi kèm: `_ = window.ShowDialog(owner)` vứt bỏ Task → nếu ShowDialog fault, exception KHÔNG tới `Dispatcher.UIThread.UnhandledException` (global handler), chỉ tới `UnobservedTaskException` khi GC finalize (thực tế = không bao giờ thấy).

## Giải pháp

```csharp
// ĐÚNG: lấy owner qua TopLevel.GetTopLevel — xử lý sẵn TopLevelHost
private async void OpenDialog()
{
    if (TopLevel.GetTopLevel(this) is not Window owner)
    {
        SystemUtils.logger?.SaveSystemLog(...); // guard fail PHẢI log, không return im lặng
        return;
    }
    try
    {
        await new MyDialog(vm).ShowDialog(owner); // await, KHÔNG "_ ="
    }
    catch (Exception ex)
    {
        SystemUtils.logger?.SaveSystemLog(..., ex);
    }
}
```

1. Sweep toàn codebase mọi chỗ `VisualRoot is Window` / `VisualRoot as Window` / `VisualRoot as XxxWindow` — cùng lớp lỗi (dự án này dính 3 chỗ: 2 hàm mở dialog + property `Shell => VisualRoot as AppShellWindow` làm chết 2 link điều hướng dashboard).
2. Thay bằng `TopLevel.GetTopLevel(this) as Window` (hoặc `FindAncestorOfType<Window>`).
3. Guard fail → ghi log; ShowDialog → await + try/catch.

## Bài học rút ra

- **Silent guard-return là kẻ thù của chẩn đoán**: triệu chứng "không có gì xảy ra + không exception" thường là guard return im lặng, KHÔNG phải exception bị nuốt — instrument guard trước khi đoán exception.
- Verify UI PHẢI đi đúng đường người dùng đi (shell thật), không tin verify qua harness dev-mode — đường mở dialog khác nhau che mất bug.
- Pattern `_ = SomeTask` trong UI code = tự tắt global exception handler cho đường đó.

## Cách phát hiện nhanh lần sau

Log `VisualRoot?.GetType().FullName` — thấy `TopLevelHost` là dính gotcha này.
