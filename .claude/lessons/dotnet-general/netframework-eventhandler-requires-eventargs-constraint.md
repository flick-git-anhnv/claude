---
category: dotnet-general
tags: [event, eventhandler, net-framework, net-core, port, generics]
severity: high
created: 2026-07-06
updated: 2026-07-06
project-origin: 3rdLedLib (KZtek.ControllerLib.Framework)
---

# Port class dùng `EventHandler<T>` từ .NET Core/.NET 8 sang .NET Framework — CS0311 nếu `T` không kế thừa `EventArgs`

## Tình huống gặp phải

Port `CardDispenserController`/`DispenserStatus` từ `KZtek.ControllerLib` (.NET 8) sang
`KZtek.ControllerLib.Framework` (.NET Framework 4.0). Bản .NET 8 khai báo
`event EventHandler<DispenserStatus> CardEvent;` với `DispenserStatus` là class thường, không kế thừa
`EventArgs` — build .NET 8 hoàn toàn bình thường. Copy y nguyên signature này sang project .NET Framework.

## Triệu chứng / Lỗi

Visual Studio Error List báo (không phát hiện được qua `dotnet build`/MSBuild CLI trên máy vì project còn lỗi
khác — thiếu Developer Pack .NET Framework 4.0 chặn build từ bước sớm hơn; chỉ IntelliSense/build thật trong VS
với đủ reference assemblies mới lộ ra):

```
CS0311: The type 'KZtek.ControllerLib.Framework.CardDispenser.DispenserStatus' cannot be used as type
parameter 'TEventArgs' in the generic type or method 'EventHandler<TEventArgs>'. There is no implicit
reference conversion from 'KZtek.ControllerLib.Framework.CardDispenser.DispenserStatus' to 'System.EventArgs'.
```

## Nguyên nhân gốc rễ (Root Cause)

`System.EventHandler<TEventArgs>` có **định nghĩa khác nhau** giữa hai runtime:

- **.NET Framework (mscorlib)**: `public delegate void EventHandler<TEventArgs>(object sender, TEventArgs e) where TEventArgs : EventArgs;` — **có ràng buộc** `TEventArgs : EventArgs`.
- **.NET Core / .NET 5+**: ràng buộc này đã bị **gỡ bỏ** trong BCL mới — cho phép dùng bất kỳ type nào làm `TEventArgs`, kể cả class thường không liên quan gì đến `EventArgs`.

Vì vậy code hợp lệ 100% trên .NET 8 (`EventHandler<DispenserStatus>` với `DispenserStatus` không kế thừa
`EventArgs`) **không hợp lệ** khi build lại trên .NET Framework — đây không phải lỗi cú pháp C#, mà là khác
biệt API giữa hai phiên bản BCL, nên không lộ ra khi review code bằng mắt hay so khớp style.

## Giải pháp

Cho class dữ liệu dùng làm `TEventArgs` kế thừa `EventArgs`:

```csharp
// Sai trên .NET Framework (đúng trên .NET 8):
public sealed class DispenserStatus
{
    ...
}

// Đúng trên cả hai:
public sealed class DispenserStatus : EventArgs
{
    ...
}
```

Không cần đổi gì ở phía .NET 8 — kế thừa `EventArgs` không phá vỡ gì (EventArgs chỉ có 1 static field `Empty`,
không có instance member nào xung đột).

## Áp dụng lại (How to reuse)

- Khi port bất kỳ class nào được dùng làm tham số của `EventHandler<T>` từ project .NET Core/.NET 5+/.NET 8
  sang project .NET Framework (hoặc ngược lại kiểm tra project .NET Framework cũ) → luôn kiểm tra class đó đã
  kế thừa `EventArgs` chưa, đừng giả định "build .NET 8 pass thì .NET Framework cũng pass".
- Dấu hiệu nhận biết nhanh: các class event-args "chuẩn" khác trong cùng project .NET Framework
  (`CardEventArgs`, `InputEventArgs`, `ConnectionStatusChangedEventArgs`...) đều `: EventArgs` — nếu class mới
  port vào không theo pattern này, gần như chắc chắn sẽ vỡ khi target .NET Framework.
- Nếu môi trường build không có Developer Pack cho target framework cũ (không build được qua CLI để tự phát
  hiện) → phải tự rà tay theo checklist BCL-difference này, không chỉ rà cú pháp C#.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Lỗi này **không xuất hiện** khi chỉ review cú pháp hoặc build bên phía .NET 8 — chỉ lộ ra khi build thật
  trên .NET Framework (hoặc IDE có đủ reference assemblies để phân tích).
- ⚠️ Không chỉ `EventHandler<T>` — bất kỳ API mscorlib nào có ràng buộc generic bị nới lỏng trên .NET
  Core/.NET 5+ đều có nguy cơ tương tự khi port ngược lại .NET Framework. Khi nghi ngờ, so sánh signature API
  trên cả hai target trước khi copy nguyên khối.

## Tham chiếu

- Project liên quan: `H:\Vitecode\Claude\3rdLedLib` (KZtek.ControllerLib.Framework, KZtek.ControllerLib)
- File sửa: `KZtek.ControllerLib.Framework/CardDispenser/Models/DispenserStatus.cs`
- Lesson liên quan: [[port-legacy-namespace-mismatch]]
