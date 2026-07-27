---
category: dotnet-general
tags: [rabbitmq, rabbitmq-client-v7, async-events, recovery, IConnection]
severity: medium
created: 2026-07-22
updated: 2026-07-22
project-origin: IPGS.Kiosk.Avalonia (PAYMENT_KIOSK_VERTICAL)
---

# RabbitMQ.Client v7: Recovery events nằm trực tiếp trên IConnection, không cần cast IAutorecoveringConnection

## Tình huống gặp phải

Implement RabbitMQ auto-recovery hooks trong `MainViewModel.cs` — muốn hook `RecoverySucceededAsync` và `ConnectionRecoveryErrorAsync` sau khi tạo connection với `AutomaticRecoveryEnabled=true`.

## Triệu chứng / Lỗi

```
error CS0246: The type or namespace name 'IAutorecoveringConnection' could not be found
  (are you missing a using directive or an assembly reference?)
```

```
error CS0123: No overload for 'OnRabbitRecoverySucceeded' matches delegate
  'AsyncEventHandler<AsyncEventArgs>'
```

## Nguyên nhân gốc rễ (Root Cause)

**Lỗi 1 — IAutorecoveringConnection không cần thiết:**
Trong RabbitMQ.Client v7.2.1, `RecoverySucceededAsync` và `ConnectionRecoveryErrorAsync` đã được đưa lên thẳng `IConnection` interface — không cần cast sang `IAutorecoveringConnection` như v6.x.

**Lỗi 2 — EventArgs sai type:**
`RecoverySucceededAsync` là `AsyncEventHandler<AsyncEventArgs>` (namespace `RabbitMQ.Client.Events`), KHÔNG phải `System.EventArgs`. Handler phải nhận `AsyncEventArgs`, không phải `EventArgs`.

## Giải pháp

```csharp
// ĐÚNG — v7.2.1: hook trực tiếp trên IConnection, không cần cast
_rabbitConn.ConnectionShutdownAsync      += OnRabbitConnectionShutdown;
_rabbitConn.RecoverySucceededAsync       += OnRabbitRecoverySucceeded;
_rabbitConn.ConnectionRecoveryErrorAsync += OnRabbitConnectionRecoveryError;

// Handler signature đúng — dùng AsyncEventArgs (RabbitMQ.Client.Events)
private Task OnRabbitConnectionShutdown(object? sender, ShutdownEventArgs e)
    => Task.CompletedTask;  // ShutdownEventArgs vẫn như cũ

private Task OnRabbitRecoverySucceeded(object? sender, AsyncEventArgs e)
    => Task.CompletedTask;  // PHẢI là AsyncEventArgs, không phải EventArgs!

private Task OnRabbitConnectionRecoveryError(object? sender, ConnectionRecoveryErrorEventArgs e)
    => Task.CompletedTask;  // ConnectionRecoveryErrorEventArgs có property .Exception
```

```csharp
// SAI — không cần cast, type không tồn tại trong using mặc định
if (_rabbitConn is IAutorecoveringConnection autoConn)
{
    autoConn.RecoverySucceededAsync += ...;  // compile error CS0246
}

// SAI — EventArgs thay vì AsyncEventArgs
private Task OnRabbitRecoverySucceeded(object? sender, EventArgs e) // CS0123
```

## Áp dụng lại (How to reuse)

- Khi hook recovery events RabbitMQ.Client v7 → dùng `_rabbitConn.RecoverySucceededAsync` trực tiếp, KHÔNG cast.
- Khi viết handler cho `RecoverySucceededAsync` → parameter phải là `AsyncEventArgs` (từ `using RabbitMQ.Client.Events;`).
- Verify nhanh bằng XML docs: tìm `ConnectionRecoveryErrorAsync` trong `RabbitMQ.Client.xml` — thấy `IConnection` namespace là đúng, không cần `IAutorecoveringConnection`.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Trong v7 với `TopologyRecoveryEnabled=true`, consumer đã đăng ký qua `BasicConsumeAsync` TỰ ĐỘNG được re-subscribe sau recovery — **KHÔNG cần re-call** `BasicConsumeAsync` trong `RecoverySucceededAsync`.
- ⚠️ `ConnectionFactory.AutomaticRecoveryEnabled` default là `true` trong v7 — set tường minh chỉ để defensive/documentation, không bắt buộc.
- ⚠️ Khi unhook (dispose): dùng `-=` với cùng method reference, không dùng lambda (lambda mỗi lần là object mới, `-=` không unsubscribe được).
- ⚠️ `IConnection` và `IChannel` v7 là `IAsyncDisposable` — nên `await DisposeAsync()` thay vì `Dispose()` khi có thể.

## Tham chiếu

- RabbitMQ.Client.xml v7.2.1: `RabbitMQ.Client.IConnection.RecoverySucceededAsync` và `ConnectionRecoveryErrorAsync`
- Project liên quan: IPGS.Kiosk.Avalonia — `MainViewModel.cs` ConnectRabbitMQAsync + event handlers
