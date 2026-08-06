---
category: avalonia
tags: [ObservableCollection, Dispatcher.UIThread, thread-safety, InvalidOperationException, System.Timers.Timer]
severity: high
created: 2026-08-06
updated: 2026-08-06
project-origin: App-Access-V2 (iAccessDesktopv2.Avalonia)
---

# ObservableCollection: chỉ dispatch phần WRITE lên UIThread là chưa đủ — READ (foreach/LINQ) cũng phải qua UIThread

## Tình huống gặp phải

`MainViewModel.RunCMDFromServerAsync()` chạy trên callback `Elapsed` của
`System.Timers.Timer` (`timerRefreshStatus`) — tức **background/ThreadPool thread**, không
phải UI thread. Method này tìm lại 1 row đã tồn tại trong
`ObservableCollection<RegisterStatusRow> RegisterStatuses` theo `CmdId`, rồi cập nhật
`row.Status`/`row.Message` qua `Dispatcher.UIThread.InvokeAsync` (đúng). Nhưng bước ĐỌC
(`FirstOrDefault`) để tìm row lại gọi trực tiếp trên background thread, không qua Dispatcher.

Trong khi đó, các luồng khác (VD: `AddRegisterStatusRowAsync` được gọi từ realtime
RabbitMQ handler) `Insert(0, row)` / `RemoveAt(...)` trên đúng `RegisterStatuses` — có
dispatch UIThread đàng hoàng.

## Triệu chứng / Lỗi

```
Exception caught: System.InvalidOperationException in iAccessDesktopv2.Avalonia.dll
"Collection was modified; enumeration operation may not execute."
```

Lỗi xuất hiện ngẫu nhiên trong Output window (VS Exception Settings bắt "First chance"),
không có stack trace rõ ràng dẫn thẳng tới dòng lỗi — khó tìm nếu chỉ đọc log.

## Nguyên nhân gốc rễ (Root Cause)

`ObservableCollection<T>` KHÔNG thread-safe. Không chỉ 2 thread cùng WRITE mới lỗi — 1
thread ĐỌC (enumerate qua `foreach`/LINQ `FirstOrDefault`/`Where`...) trong khi thread khác
đang WRITE (`Add`/`Insert`/`Remove`/`Clear`) cùng lúc cũng ném đúng exception này, vì cả hai
thao tác cùng chạm `_version`/internal array của collection không có lock.

Pattern sai thường gặp: developer nhớ "set property có INPC phải qua Dispatcher" (đúng, để
khỏi vỡ binding) nhưng quên rằng **enumerate cả collection** (kể cả read-only LINQ) từ
background thread cũng phải qua Dispatcher nếu bất kỳ nơi nào khác có thể Add/Remove nó từ
UI thread cùng lúc.

## Giải pháp

Bọc luôn bước ĐỌC (không chỉ bước GHI) bằng `Dispatcher.UIThread.InvokeAsync`:

```csharp
// SAI — enumerate trực tiếp trên background thread trong khi UI thread có thể Insert/RemoveAt
var row = RegisterStatuses.FirstOrDefault(r => r.CmdId == data.CmdId);

// ĐÚNG — toàn bộ truy cập RegisterStatuses (đọc lẫn ghi) đều marshal qua UI thread
var row = await Dispatcher.UIThread.InvokeAsync(
    () => RegisterStatuses.FirstOrDefault(r => r.CmdId == data.CmdId));
```

1. Xác định method có đang chạy trên non-UI thread không (Timer.Elapsed, Task.Run,
   RabbitMQ consumer callback, socket event...).
2. Nếu có — grep TOÀN BỘ chỗ method đó chạm vào field `ObservableCollection<T>` (đọc lẫn
   ghi), không chỉ chỗ set property.
3. Bọc mọi truy cập đó bằng `Dispatcher.UIThread.Invoke`/`InvokeAsync`.

## Áp dụng lại (How to reuse)

- Thấy exception "Collection was modified; enumeration operation may not execute" trong app
  Avalonia/WPF có nhiều thread (timer + realtime event + UI) → nghi ngờ NGAY
  `ObservableCollection` bị truy cập (đọc HOẶC ghi) từ ≥2 thread mà không đồng bộ qua
  Dispatcher.
- Đừng chỉ kiểm tra chỗ set property (INPC) — phải kiểm tra CẢ chỗ `foreach`/LINQ enumerate
  trên field đó, vì đọc cũng có thể là nguyên nhân, không chỉ ghi.
- Nếu 1 method chạm ObservableCollection nhiều lần và chạy trên background thread, cân nhắc
  gộp toàn bộ block liên quan vào 1 lần `Dispatcher.UIThread.InvokeAsync` thay vì bọc rời rạc
  từng dòng — đỡ context-switch nhiều lần và tránh sót dòng.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ `AccessMemoryCollection` (custom `CollectionBase`) đã tự lock đầy đủ (`_instanceLock`,
  `_accessKeysLock`) — không phải mọi "Collection was modified" đều do class đó; đừng giả
  định nguồn lỗi mà không kiểm tra thread thực sự chạy method nào.
- ⚠️ `System.Timers.Timer.Elapsed` LUÔN chạy trên ThreadPool thread bất kể được start ở đâu —
  khác với `DispatcherTimer` (Avalonia) chạy đúng UI thread. Nhầm 2 loại timer này là nguồn
  gốc phổ biến của bug loại này.

## Tham chiếu

- Project liên quan: App-Access-V2 (iAccessDesktopv2.Avalonia) —
  `ViewModels/Main/MainViewModel.cs`, method `RunCMDFromServerAsync`.
