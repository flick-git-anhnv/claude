---
category: avalonia
tags: [avalonia-12, rabbitmq-client-7, breaking-change, upgrade, GotFocusEventArgs, FocusChangedEventArgs, ExtendClientAreaChromeHints, AVLN2100, AVLN2000, x:DataType, ContentPresenter, TreeViewItem, ShowExpander]
severity: high
created: 2026-07-15
updated: 2026-07-20
project-origin: parking-v8-app-avalonia, iPGSv4
---

# Nâng cấp Avalonia 11→12 + RabbitMQ.Client 6→7: các breaking change gặp phải

## Tình huống gặp phải

> Đang làm gì? Tính năng gì? Môi trường nào?

User nâng cấp hàng loạt NuGet package qua Visual Studio (Consolidate/Update All): Avalonia 11.2.7→12.1.0, RabbitMQ.Client 6.8.1→7.2.1, RestSharp 112.1.0→114.0.0, áp dụng cho toàn bộ solution `parking-v8-app-avalonia` VÀ một project thư viện ngoài repo (`Kztek.Cameras.Avalonia`, tại `0.BaseLIB`) được tham chiếu qua ProjectReference.

## Triệu chứng / Lỗi

```
error CS0246: The type or namespace name 'GotFocusEventArgs' could not be found
error CS0246: The type or namespace name 'IModel' could not be found (RabbitMQ.Client)
Avalonia error AVLN2000: Unable to resolve suitable regular or attached property ExtendClientAreaChromeHints
Avalonia error AVLN2100: Cannot parse a compiled binding without an explicit x:DataType directive
```

## Nguyên nhân gốc rễ (Root Cause)

1. **RabbitMQ.Client 6→7 là rewrite toàn bộ sang async-only API**: `IModel`→`IChannel`, `CreateModel()`→`CreateChannelAsync()`, `CreateConnection()`→`CreateConnectionAsync()`, `BasicPublish/BasicConsume/BasicCancel/QueueDeclare/QueueBind` đều có hậu tố `Async` bắt buộc, `EventingBasicConsumer`→`AsyncEventingBasicConsumer` (event `Received`→`ReceivedAsync`). `IChannel`/`IConnection` chỉ còn `IAsyncDisposable`, KHÔNG còn `IDisposable` đồng bộ nữa → không thể `channel?.Dispose()` trực tiếp.
2. **Avalonia 12 xóa hẳn `GotFocusEventArgs`** — nhưng ⚠️ **KHÔNG phải** thay bằng `RoutedEventArgs` trơn (đã kiểm chứng lại 2026-07-20, thông tin trước đó SAI). Cả `InputElement.GotFocus` VÀ `InputElement.LostFocus` giờ dùng chung type mới **`Avalonia.Input.FocusChangedEventArgs`** (namespace `Avalonia.Input`, cùng namespace đã có sẵn qua `using Avalonia.Input;` — không cần using mới). Field/EventHandler khai báo `EventHandler<RoutedEventArgs>` cho các handler gán vào `GotFocus`/`LostFocus` sẽ lỗi `CS0029: Cannot implicitly convert ... RoutedEventArgs ... to ... FocusChangedEventArgs`. Xác nhận bằng cách grep `Avalonia.Base.xml` (nuget cache): `T:Avalonia.Input.FocusChangedEventArgs` có doc "Represents the arguments of GotFocus and LostFocus".
3. **Avalonia 12 xóa hẳn thuộc tính `ExtendClientAreaChromeHints`** trên `Window` — không có thay thế trực tiếp, chỉ còn `ExtendClientAreaToDecorationsHint` + `ExtendClientAreaTitleBarHeightHint`.
4. **Avalonia 12 siết chặt compiled binding** — bất kỳ `{Binding ...}` nào nằm trong 1 scope (DataTemplate, Popup, Flyout, ContextMenu, `ControlTheme` Setter...) không kế thừa được `x:DataType` từ ancestor sẽ lỗi cứng AVLN2100 lúc build (Avalonia 11.x fallback âm thầm về reflection binding, giờ bắt buộc phải khai báo `x:DataType` tường minh) — kể cả `ControlTheme x:Key="..." TargetType="...">` cũng cần thêm `x:DataType` nếu bên trong có Setter bind tới property của item DataContext (không phải property của control).
5. **`{Binding RelativeSource={RelativeSource AncestorType=UserControl}, Path=CustomProp}` hết tác dụng cho custom UserControl** — Avalonia 12 compiled binding resolve `AncestorType=UserControl` LITERALLY là base class `Avalonia.Controls.UserControl`, không phải kiểu con thực tế (VD `KzCard`), nên property tự định nghĩa như `CardContent` báo lỗi `AVLN2000: Unable to resolve property or method of name 'CardContent' on type 'Avalonia.Controls.UserControl'` dù property tồn tại trên class con. **Fix:** thêm `x:Name="Root"` vào root `<UserControl>`, đổi binding sang `{Binding CardContent, ElementName=Root}` — không cần biết kiểu con tường minh, tránh luôn phải thêm `xmlns` cho namespace của chính control.
6. **`TreeViewItem.ShowExpander` bị XÓA HẲN** trong Avalonia 12 (còn `IsExpanded`, `IsSelected`, `Level`) — code cũ dùng `{Binding $parent[TreeViewItem].ShowExpander}` để ẩn/hiện nút mở-rộng cho leaf node sẽ lỗi `AVLN2000: Unable to resolve property or method of name 'ShowExpander'`. **Fix:** không có property thay thế trực tiếp — bind theo field nghiệp vụ có sẵn trên item (VD `!IsLeaf`/`HasItems` tự định nghĩa trên ViewModel item), không dùng property có sẵn của `TreeViewItem`.

## Giải pháp

```csharp
// RabbitMQ.Client 7.x — Start()/Dispose() giữ nguyên chữ ký sync (constructor ViewModel
// không thể async) bằng cách bridge 1 lần, ConfigureAwait(false) xuyên suốt để tránh deadlock:
public void Start()
{
    try { StartAsync().ConfigureAwait(false).GetAwaiter().GetResult(); }
    catch (Exception ex) { NotifyError(...); }
}
private async Task StartAsync()
{
    connection = await factory.CreateConnectionAsync().ConfigureAwait(false);
    channel = await connection.CreateChannelAsync().ConfigureAwait(false);
    await channel.QueueDeclareAsync(...).ConfigureAwait(false);
    var consumer = new AsyncEventingBasicConsumer(channel);
    consumer.ReceivedAsync += OnReceivedAsync;   // handler: async Task OnReceivedAsync(...)
    consumerTag = await channel.BasicConsumeAsync(...).ConfigureAwait(false);
}
// lock (obj) { channel.BasicPublish(...) } KHÔNG compile được vì không await được trong lock
// → đổi sang SemaphoreSlim + await WaitAsync()/Release() trong try/finally.
// Dispose(): channel/connection chỉ còn DisposeAsync() → bridge tương tự Start().
```

1. Grep toàn bộ `IModel`, `EventingBasicConsumer`, `.CreateModel()`, `.BasicPublish(`, `.BasicConsume(` để tìm hết chỗ cần sửa trước khi bắt đầu.
2. Đổi `GotFocusEventArgs` → `Avalonia.Input.FocusChangedEventArgs` ở CẢ `GotFocus` VÀ `LostFocus` handler (không phải `RoutedEventArgs` — xem mục Root Cause #2 đã sửa lại).
3. Xóa `ExtendClientAreaChromeHints="..."` khỏi XAML, giữ 2 hint còn lại.
4. Với AVLN2100: đọc code-behind/ViewModel để biết đúng kiểu, thêm `x:DataType="vm:TênViewModel"` (hoặc kiểu item nếu là `ControlTheme`/`DataTemplate`) vào đúng scope đang thiếu — không đoán bừa.
5. Với lỗi `AncestorType=UserControl` không resolve property tự định nghĩa: thêm `x:Name="Root"` vào UserControl gốc, đổi `{Binding RelativeSource={RelativeSource AncestorType=UserControl}, Path=X}` → `{Binding X, ElementName=Root}`.
6. Với lỗi `TreeViewItem.ShowExpander` không tồn tại: tìm property nghiệp vụ tương đương trên item DataContext (đã kèm `x:DataType` cho ControlTheme) thay vì cố tìm property thay thế trên `TreeViewItem`.
5. **`Avalonia.Diagnostics` (gói DevTools cũ) đã NGỪNG cập nhật ở `11.3.18`** — Avalonia 12 thay bằng gói MỚI **`AvaloniaUI.DiagnosticsSupport`** (v2.2.3+, kiến trúc "Developer Tools" tách process riêng, remote debugging protocol). Giữ `Avalonia.Diagnostics` cũ + gọi `this.AttachDevTools()` khi core đã 12.1.0 → `System.TypeLoadException: Could not load type 'Avalonia.Reactive.SerialDisposableValue' from assembly 'Avalonia.Base, Version=12.1.0.0'` ngay lúc khởi động (Debug build).
   **Fix đúng (không phải bỏ hẳn DevTools):**
   - Gỡ `PackageReference Avalonia.Diagnostics`, thêm `PackageReference AvaloniaUI.DiagnosticsSupport` (bản mới nhất, check `curl -s https://api.nuget.org/v3-flatcontainer/avaloniaui.diagnosticssupport/index.json`).
   - Đổi tên gọi: `AttachDevTools()` → **`AttachDeveloperTools()`** (namespace `Avalonia`, đã có sẵn qua `using Avalonia;` — KHÔNG cần using mới, KHÔNG còn `using Avalonia.Diagnostics;`).
   - Gọi trong **`Initialize()`** (ngay sau `AvaloniaXamlLoader.Load(this);`), KHÔNG phải `OnFrameworkInitializationCompleted()` như bản cũ — vị trí gọi cũng đổi theo README chính thức của package mới.
   - Cách dùng: nhấn F12 lúc app chạy để app tự kết nối tới tiến trình AvaloniaUI Developer Tools riêng (không còn overlay nhúng trong process như bản cũ).

## Áp dụng lại (How to reuse)

- Khi thấy nâng cấp Avalonia lên major version mới → PHẢI build `--no-incremental` (không dựa vào build có cache, vì cache có thể che giấu lỗi AVLN2100 ở project ngoài ProjectReference) để lộ hết lỗi thật.
- Khi thấy nâng cấp RabbitMQ.Client qua major version → search ngay `IModel`/`EventingBasicConsumer` trong toàn solution trước khi bump version, ước lượng effort trước.
- Nếu app có ProjectReference tới thư viện ngoài repo (VD `0.BaseLIB`) và user nâng cấp Avalonia toàn solution qua NuGet UI (Consolidate) → project ngoài đó CŨNG bị đổi version, phải build riêng nó (`--no-incremental`) để kiểm tra, không chỉ build app chính.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ `dotnet build -c Release` (không chỉ định `-r <RID>`) có thể PASS dù ẩn chứa lỗi ở project ProjectReference ngoài do dùng cache incremental — chỉ `-r win-x64/linux-x64 --no-incremental` mới lộ lỗi thật.
- ⚠️ Đừng dùng `.Result`/`.Wait()` để né việc chuyển async khi migrate RabbitMQ.Client — dùng `ConfigureAwait(false)` + `GetAwaiter().GetResult()` CHỈ tại đúng 1 điểm bridge sync/async (Start/Dispose), không rải rác nhiều nơi.
- ⚠️ `lock (object) { await ... }` là lỗi biên dịch — phải đổi sang `SemaphoreSlim` khi có await bên trong critical section.

## Tham chiếu

- Project liên quan: `parking-v8-app-avalonia` (repo chính) + `Kztek.Cameras.Avalonia` (thư viện ngoài, `0.BaseLIB`)
- Xác nhận lại 2026-07-20 tại `iPGSv4` (project `KztekComponentAvalonia`, `IPGS.Control`): build thật với Avalonia 12.1.0 xác nhận `FocusChangedEventArgs` (không phải `RoutedEventArgs`), phát hiện thêm 2 gotcha mới (`AncestorType=UserControl` + `TreeViewItem.ShowExpander`) — xem Root Cause #5, #6.
