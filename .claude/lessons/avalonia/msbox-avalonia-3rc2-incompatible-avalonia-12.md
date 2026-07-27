---
category: avalonia
tags: [avalonia-12, msbox-avalonia, MessageBox, TypeLoadException, SystemDecorations, dialog, breaking-change, runtime-only-error]
severity: high
created: 2026-07-26
updated: 2026-07-26
project-origin: DoorAlarmv3.Avalonia (migrate WinForms → Avalonia)
---

# MsBox.Avalonia 3.0.0-rc2 KHÔNG chạy được trên Avalonia 12 — build xanh nhưng TypeLoadException lúc chạy

## Tình huống gặp phải

Migrate DoorAlarmv3 (WinForms) sang Avalonia 12.1.0. Cần thay `MessageBox.Show` của WinForms bằng
hộp thoại Avalonia → dùng `MsBox.Avalonia` 3.0.0-rc2 (bản duy nhất có trên nguồn NuGet của máy, và
cũng là bản mà `Kztek.Cameras.Avalonia` đang khai báo).

Build `dotnet build -c Release` **xanh hoàn toàn, 0 error, 0 warning liên quan**. Chỉ khi chạy thật
mới lộ lỗi.

## Triệu chứng / Lỗi

Gọi `MessageBoxManager.GetMessageBoxStandard(...)`:

```
TypeLoadException: Could not load type 'Avalonia.Controls.SystemDecorations'
from assembly 'Avalonia.Controls, Version=12.1.0.0, Culture=neutral, PublicKeyToken=c8d484a7012f9a8b'.
```

## Nguyên nhân gốc rễ (Root Cause)

1. `MsBox.Avalonia` 3.0.0-rc2 được biên dịch với **`Avalonia.Controls` 11.0.0** (kiểm bằng
   `MetadataLoadContext` → `GetReferencedAssemblies()`).
2. .NET Core/.NET 8 phân giải assembly **theo tên đơn giản**, bỏ qua version → lúc chạy nó nạp
   `Avalonia.Controls` 12.1.0 thay cho 11.0.0. Không có lỗi binding nào ở bước này.
3. **`Avalonia.Controls.SystemDecorations` đã bị xoá ở Avalonia 12.** MsBox tham chiếu kiểu đó
   trong code dựng cửa sổ → `TypeLoadException` ngay lần gọi đầu tiên.

Đây **cùng một dạng lỗi** với `Avalonia.Diagnostics` 11.x + core 12 (`TypeLoadException:
Avalonia.Reactive.SerialDisposableValue`) — xem lesson `avalonia-12-breaking-changes-rabbitmq7-migration`.
Quy luật chung: **gói bên thứ ba biên dịch cho Avalonia 11 mà chạm vào kiểu bị xoá ở Avalonia 12 sẽ
chết lúc chạy, không chết lúc build.**

## Giải pháp (ĐÃ KIỂM CHỨNG)

Tại thời điểm 2026-07-26, `https://api.nuget.org/v3-flatcontainer/msbox.avalonia/index.json` chỉ trả
về đúng `3.0.0-rc2` — **không có bản nào hỗ trợ Avalonia 12**. Nên không có đường "nâng version".

→ **Gỡ `MsBox.Avalonia`, tự viết `MessageDialogWindow`** (1 file `.axaml` + 1 file `.axaml.cs`,
~110 dòng cho cả 3 loại Info/Error/Confirm):

```csharp
// Views/Dialogs/MessageDialogWindow.axaml.cs
public static MessageDialogWindow Create(string title, string message, MessageDialogKind kind) { ... }
private void OnPrimaryClick(object? s, RoutedEventArgs e) => Close(true);
private void OnSecondaryClick(object? s, RoutedEventArgs e) => Close(false);

// DialogService
var dialog = MessageDialogWindow.Create(title, message, kind);
var owner = (Application.Current?.ApplicationLifetime as IClassicDesktopStyleApplicationLifetime)?.MainWindow;
return owner is null ? await dialog.ShowDialog<bool>(dialog)   // chưa có MainWindow (lỗi lúc khởi động)
                     : await dialog.ShowDialog<bool>(owner);
```

Lợi ích kèm theo: hộp thoại tự viết theo được token thương hiệu (`kz.brush.navy.900`,
`kz.brush.border`) nên nhìn đồng bộ với `KztekComponentAvalonia`, điều mà MsBox không làm được.

## Cách phát hiện sớm (quan trọng nhất)

Lỗi này **không thể phát hiện bằng build**. Cách hiệu quả: một hàm **self-test chạy bằng biến môi
trường**, dựng tất cả service trong DI + **dựng (không cần hiện) hộp thoại**, in PASS/FAIL rồi thoát:

```csharp
// App.OnFrameworkInitializationCompleted()
if (Environment.GetEnvironmentVariable("DA_SELFTEST") == "1") { SelfTest.Run(Services); Environment.Exit(0); return; }
```

```bash
# Windows
$env:DA_SELFTEST=1; .\App.exe
# Linux (WSL) — publish self-contained rồi copy vào /tmp
DA_SELFTEST=1 ./App
```

Chỉ cần **dựng** đối tượng là đã đủ để nạp kiểu → bắt được `TypeLoadException` mà không cần bấm tay
qua UI. Chính self-test này đã lộ ra lỗi MsBox trong vài giây.

## Áp dụng lại (How to reuse)

- Trước khi thêm **bất kỳ** gói UI bên thứ ba vào project Avalonia 12: kiểm
  `GetReferencedAssemblies()` của DLL trong nuget cache. Nếu thấy `Avalonia.* 11.x` → coi là **rủi ro
  runtime**, phải chạy thử thật trước khi dựa vào nó.
- Kiểm nhanh version có sẵn: `curl -s https://api.nuget.org/v3-flatcontainer/<packageid>/index.json`.
- Mọi project Avalonia 12 của KZTEK nên có 1 hàm self-test kiểu trên — chi phí ~80 dòng, bắt được cả
  lớp lỗi "chỉ lộ lúc chạy" (gói lệch version, `System.Drawing.Common` trên Linux, WMI…).
- ⚠️ `Kztek.Cameras.Avalonia` (`0.BaseLIB`) **vẫn đang khai báo** `MsBox.Avalonia 3.0.0-rc2` cùng
  Avalonia 12.1.0 → build xanh, nhưng nếu có code path nào gọi `MessageBoxManager` thì sẽ chết y hệt.
  Cần kiểm lại thư viện đó.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Namespace của MsBox 3.0.0-rc2 bị **tách rời và không nhất quán**: `MsBox.Avalonia.MessageBoxManager`,
  `MsBox.Avalonia.Enums.Icon`, nhưng `MessageBox.Avalonia.Enums.ButtonEnum` và
  `MessageBox.Avalonia.DTO.MessageBoxStandardParams` (tên namespace CŨ). Dù có dùng được thì cũng
  phải khai báo alias — liên quan lesson `msbox-avalonia-namespace-split`.
- ⚠️ Đừng kết luận "gói ổn" chỉ vì một project KZTEK khác đang khai báo nó — khai báo được ≠ có gọi
  thật lúc chạy.
- ⚠️ `Dispatcher.UIThread.InvokeAsync(async () => ...)` KHÔNG có `.AsTask()`/`.GetTask()`; `await`
  trực tiếp kết quả (lesson `avalonia-dispatcher-invokeAsync-no-AsTask`).

## Tham chiếu

- Project: `DoorAlarmv3.Avalonia` — `Services/DialogService.cs`, `Views/Dialogs/MessageDialogWindow.axaml(.cs)`, `SelfTest.cs`
- Plan: `docs/plans/PLAN-migrate-dooralarmv3-avalonia-2026-07-26/steps/STEP-2.4-platform-services.md` (rủi ro R9)
- Liên quan: `avalonia-12-breaking-changes-rabbitmq7-migration.md`, `msbox-avalonia-namespace-split.md`,
  `avalonia-devtools-package-migration-v12.md`
