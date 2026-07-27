---
category: avalonia
tags: [dispatcher, async, task, UI-thread]
severity: medium
created: 2026-07-14
updated: 2026-07-14
project-origin: parking-v8-app-avalonia
---

# Avalonia `Dispatcher.UIThread.InvokeAsync` không có `.AsTask()` — dùng `await` trực tiếp

## Tình huống gặp phải

Đang implement cash payment UI callback trong `KioskOutLaneViewModel.cs`. Cần marshal callback từ background thread lên UI thread bằng Avalonia Dispatcher. Viết pattern:

```csharp
private Task ApplyCashPollEvent(CashResult cash)
{
    return Dispatcher.UIThread.InvokeAsync(() => { ... }).AsTask();
}
```

## Triệu chứng / Lỗi

```
error CS1061: 'DispatcherOperation' does not contain a definition for 'AsTask'
and no accessible extension method 'AsTask' accepting a first argument
of type 'DispatcherOperation' could be found
```

## Nguyên nhân gốc rễ (Root Cause)

Avalonia's `Dispatcher.UIThread.InvokeAsync()` trả về `DispatcherOperation` — không phải `Task`. `DispatcherOperation` **có thể await trực tiếp** nhưng **không có `.AsTask()` extension** như WPF's `DispatcherOperation`. Pattern `.AsTask()` là WPF, không phải Avalonia.

## Giải pháp

Dùng `async Task` + `await` trực tiếp thay vì `.AsTask()`:

```csharp
// SAI (WPF pattern — không dùng trong Avalonia)
private Task ApplyCashPollEvent(CashResult cash)
{
    return Dispatcher.UIThread.InvokeAsync(() => { ... }).AsTask();
}

// ĐÚNG (Avalonia pattern)
private async Task ApplyCashPollEvent(CashResult cash)
{
    await Dispatcher.UIThread.InvokeAsync(() => { ... });
}
```

## Áp dụng lại (How to reuse)

- Khi thấy lỗi `'DispatcherOperation' does not contain 'AsTask'` → đổi method sang `async Task` và thay `.AsTask()` bằng `await`
- Mọi callback cần marshal lên UI thread trong Avalonia: dùng `await Dispatcher.UIThread.InvokeAsync(() => { ... });`
- Pattern `await Dispatcher.UIThread.InvokeAsync(...)` có sẵn trong project — xem các method hiện có như `ApplyKioskFlowState`

## Chú ý / Cạm bẫy (Gotchas)

- `DispatcherOperation` là `IAwaitable` nhưng không phải `Task` — không thể dùng `Task.WhenAny`, `.AsTask()`, hay `.ContinueWith()`
- Nếu cần `Task` thực sự (để compose): tạo `TaskCompletionSource<bool>` và set result trong InvokeAsync callback
- `Dispatcher.UIThread.InvokeAsync` với `async () =>` lambda trả về `DispatcherOperation<Task>` — vẫn await được nhưng cần kiểm tra kỹ unwrap

## Tham chiếu

- Project liên quan: parking-v8-app-avalonia (Phase 5.4.6 cash payment binding)
- Avalonia docs: https://docs.avaloniaui.net/docs/concepts/the-main-window/dispatchers
