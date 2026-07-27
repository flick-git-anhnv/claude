---
category: avalonia
tags: [namespace, collision, cs0234, build-error, migration]
severity: high
created: 2026-07-20
updated: 2026-07-20
project-origin: IPGS.Kiosk.Avalonia (migrate-ipgs-kiosk-avalonia STEP-2.B4)
---

# Namespace collision: `IPGS.Kiosk.Avalonia` che khuất `Avalonia.*` framework

## Tình huống gặp phải

Đang migrate IPGS.Kiosk (WinForms) sang Avalonia. Project namespace mới là `IPGS.Kiosk.Avalonia`. Trong các file code-behind (`.axaml.cs`), code của 2.B3 viết `Avalonia.VisualTreeAttachmentEventArgs` để override method của Avalonia framework.

## Triệu chứng / Lỗi

```
error CS0234: The type or namespace name 'VisualTreeAttachmentEventArgs' does not exist
in the namespace 'IPGS.Kiosk.Avalonia' (are you missing an assembly reference?)
```

Compiler hiểu `Avalonia.VisualTreeAttachmentEventArgs` là sub-namespace/type trong `IPGS.Kiosk.Avalonia` vì project namespace KẾT THÚC bằng `.Avalonia`. Khi code nằm trong namespace `IPGS.Kiosk.Avalonia`, identifier `Avalonia` được resolve nội bộ trước khi tìm top-level namespace.

## Nguyên nhân gốc rễ (Root Cause)

C# namespace resolution: trong namespace `IPGS.Kiosk.Avalonia`, khi gặp `Avalonia.X`, compiler tìm trong namespace hierarchy hiện tại trước:
- `IPGS.Kiosk.Avalonia.X` → không tìm thấy → lỗi CS0234
Không fallback ra top-level `Avalonia.X` vì `Avalonia` đã match với phần cuối của namespace hiện tại.

## Giải pháp

**Cách 1 (khuyến nghị):** Dùng `using Avalonia;` ở đầu file + tham chiếu type không có prefix:

```csharp
using Avalonia;                        // ← import namespace top-level
// ...
protected override void OnAttachedToVisualTree(VisualTreeAttachmentEventArgs e)
//                                              ↑ KHÔNG viết Avalonia.VisualTreeAttachmentEventArgs
```

**Cách 2 (khi bắt buộc viết qualified name):** Dùng `global::` để force top-level:

```csharp
protected override void OnAttachedToVisualTree(global::Avalonia.VisualTreeAttachmentEventArgs e)
```

## Áp dụng lại (How to reuse)

- Mọi file trong project `IPGS.Kiosk.Avalonia`: KHÔNG viết `Avalonia.SomeType` trực tiếp — luôn thêm `using Avalonia;` rồi dùng unqualified `SomeType`.
- Khi thấy `CS0234: does not exist in namespace 'IPGS.Kiosk.Avalonia'` với một type của framework Avalonia → đây chính là lỗi này.
- Lần sau tạo project Avalonia: tránh đặt project namespace kết thúc bằng `.Avalonia` (chọn `.AvaloniaUI` hoặc `.Ui` thay thế).

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Ảnh hưởng toàn bộ project namespace `IPGS.Kiosk.Avalonia` — mọi agent/dev làm task sau đều phải biết.
- ⚠️ Không chỉ `VisualTreeAttachmentEventArgs` — BẤT KỲ type nào trong namespace `Avalonia.*` đều bị ảnh hưởng nếu viết qualified.
- ⚠️ Lỗi xuất hiện ở thời điểm compile — không phải runtime — dễ phát hiện nhưng confusing message.

## Tham chiếu

- C# spec: namespace resolution §7.6.2 — qualified names lookup in current namespace hierarchy first
- Project liên quan: IPGS.Kiosk.Avalonia (iPGSv4 repo, STEP-2.B4)
