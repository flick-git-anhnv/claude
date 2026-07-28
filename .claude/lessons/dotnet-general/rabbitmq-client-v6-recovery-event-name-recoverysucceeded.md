---
category: dotnet-general
tags: [rabbitmq, rabbitmq-client-v6, IAutorecoveringConnection, recovery, sync-api]
severity: low
created: 2026-07-28
updated: 2026-07-28
project-origin: App-Access-V2 (iAccessDesktopv2.Avalonia — RabbitMqEventBus)
---

# RabbitMQ.Client v6.x (sync API): event auto-recovery tên là `RecoverySucceeded`, không phải `Recovery`

## Tình huống gặp phải

Thêm hook cảnh báo mất kết nối/kết nối lại vào `RabbitMqEventBus.cs` (dự án CỐ Ý giữ RabbitMQ.Client
6.8.1 sync API — B11, không nâng v7 để tránh rewrite async, xem [[avalonia-12-breaking-changes-rabbitmq7-migration]]).
Muốn hook sự kiện auto-recovery trên `IAutorecoveringConnection`, đoán tên là `Recovery` (theo trực giác
đặt tên .NET) hoặc theo lesson v7 sẵn có [[rabbitmq-client-v7-recovery-event-api]] (`RecoverySucceededAsync`).

## Triệu chứng / Lỗi

```
error CS1061: 'IAutorecoveringConnection' does not contain a definition for 'Recovery'
```

## Nguyên nhân gốc rễ

Trong RabbitMQ.Client **6.8.1** (namespace `RabbitMQ.Client`, sync API — khác hẳn v7 async), interface
`IAutorecoveringConnection` có các event:

```
RecoverySucceeded            : EventHandler<EventArgs>
ConnectionRecoveryError      : EventHandler<ConnectionRecoveryErrorEventArgs>
ConsumerTagChangeAfterRecovery: EventHandler<ConsumerTagChangedAfterRecoveryEventArgs>
QueueNameChangeAfterRecovery  : EventHandler<QueueNameChangedAfterRecoveryEventArgs>
RecoveringConsumer           : EventHandler<RecoveringConsumerEventArgs>
```

Không có event tên `Recovery`. Tên đúng là `RecoverySucceeded` — GIỐNG tên method (không có suffix
`Async`) so với v7's `RecoverySucceededAsync`, nhưng handler v6 là `EventHandler<EventArgs>` (System.EventArgs
thường, không phải `AsyncEventArgs` như v7).

## Giải pháp

```csharp
// v6.x sync — ĐÚNG
if (conn is IAutorecoveringConnection autoConn)
{
    autoConn.RecoverySucceeded += OnConnectionRecovery; // EventHandler<EventArgs>
}

private void OnConnectionRecovery(object? sender, EventArgs e) { ... }
```

Verify nhanh khi không chắc tên event đúng trên 1 version cụ thể — dùng PowerShell reflect thẳng vào DLL
đã restore trong `~/.nuget/packages/rabbitmq.client/<version>/lib/<tfm>/RabbitMQ.Client.dll` thay vì đoán
hoặc suy từ version khác:

```powershell
$asm = [System.Reflection.Assembly]::LoadFrom("<path-to>\RabbitMQ.Client.dll")
$t = $asm.GetType("RabbitMQ.Client.IAutorecoveringConnection")
$t.GetEvents() | ForEach-Object { "$($_.Name): $($_.EventHandlerType)" }
```
(XML doc trong package không liệt kê hết các event này — không đáng tin để tra cứu, phải reflect DLL thật.)

## Áp dụng lại

- Dự án nào cố tình PIN RabbitMQ.Client ở dòng 6.x (API sync, `IModel`/`IConnection`) → auto-recovery event
  là `RecoverySucceeded` (không suffix Async, EventArgs thường), khác hẳn v7's `RecoverySucceededAsync`
  (AsyncEventArgs) — xem [[rabbitmq-client-v7-recovery-event-api]] để đối chiếu.
- Khi không chắc tên/API 1 version cụ thể của thư viện .NET đã restore → reflect thẳng DLL trong
  `.nuget/packages` bằng PowerShell thay vì đoán qua compile-fail-retry hoặc suy từ version khác.

## Chú ý / Cạm bẫy

- ⚠️ `ConnectionShutdown` (bắt mất kết nối) vẫn nằm trực tiếp trên `IConnection` (không cần cast) cả ở
  v6.x lẫn v7 — chỉ auto-recovery mới cần `IAutorecoveringConnection`.
- ⚠️ `ShutdownEventArgs.Initiator == ShutdownInitiator.Application` khi tự gọi `Dispose()/Close()` chủ
  động (app thoát, đổi config) — PHẢI lọc case này ra để không bắn cảnh báo "mất kết nối" giả khi thực ra
  là app tự đóng.
- ⚠️ Unhook trong `Dispose()` dùng `-=` với method reference (không lambda) — giống nguyên tắc v7.

## Tham chiếu

- RabbitMQ.Client.dll 6.8.1 (netstandard2.0) — reflect trực tiếp `IAutorecoveringConnection.GetEvents()`
- Project: App-Access-V2 — `iAccess.Core/Messaging/RabbitMqEventBus.cs` (thêm Disconnected/Reconnected event
  + KzToast warning ở `App.axaml.cs`)
