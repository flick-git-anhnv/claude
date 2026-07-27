---
category: avalonia
tags: [listbox, pointerpressed, handled, drag-drop, routed-event, handledEventsToo]
severity: high
created: 2026-06-27
updated: 2026-06-27
project-origin: iPGSv4 (branch ccu-avalonia)
---

# Avalonia ListBox: PointerPressed không fire khi dùng `+=`

## Tình huống gặp phải

Drag-drop từ ListBox sang Canvas không hoạt động. Handler `ListBox_PointerPressed` được đăng ký bằng `+=` nhưng không bao giờ chạy → `_listDragEntry` mãi null → drop bị reject.

## Root cause

Trong Avalonia, `ListBoxItem` nội bộ **mark `PointerPressed` là `e.Handled = true`** để xử lý selection. Khi dùng `control.PointerPressed += handler` (tức `AddHandler(..., handledEventsToo: false)`), handler sẽ **bị skip hoàn toàn** với các event đã handled.

```csharp
// ❌ KHÔNG HOẠT ĐỘNG — ListBoxItem handled PointerPressed trước, handler này bị skip
ZoneListBox.PointerPressed += ListBox_PointerPressed;
ZoneListBox.PointerMoved   += ListBox_PointerMoved;
```

## Fix bắt buộc

Dùng `AddHandler` với `handledEventsToo: true`:

```csharp
// ✅ ĐÚNG — handledEventsToo: true đảm bảo handler vẫn chạy dù ListBoxItem đã handled
foreach (var lb in new[] { ZoneListBox, ZcuListBox, KioskListBox, ElevatorListBox, EscalatorListBox })
{
    lb.AddHandler(PointerPressedEvent, ListBox_PointerPressed,
        RoutingStrategies.Bubble, handledEventsToo: true);
    lb.AddHandler(PointerMovedEvent, ListBox_PointerMoved,
        RoutingStrategies.Bubble, handledEventsToo: true);
}
```

## Dấu hiệu nhận biết

- Drag-drop từ ListBox sang Canvas không hoạt động dù code logic đúng
- Double-click (`DoubleTapped`) trên cùng ListBox vẫn hoạt động bình thường (DoubleTapped không bị handled trước)
- Đặt breakpoint vào handler → không bao giờ hit khi click trên ListBox item

## Các controls khác bị ảnh hưởng tương tự

| Control | Event thường bị handled nội bộ |
|---------|-------------------------------|
| `ListBox` / `ListBoxItem` | `PointerPressed` (selection) |
| `Button` | `PointerReleased` (click) |
| `TextBox` | `PointerPressed`, `KeyDown` (text editing) |
| `Slider` | `PointerMoved` (thumb drag) |

## Nguyên tắc chung

> Bất kỳ khi nào cần hook sự kiện từ BÊN TRONG một control tổng hợp (composite), **LUÔN dùng `AddHandler(..., handledEventsToo: true)`** thay vì `+=`.

**Why:** `+=` tương đương `AddHandler(..., handledEventsToo: false)`. Controls Avalonia thường xử lý nội bộ và mark handled → `+=` không đáng tin cậy cho cross-child event hooking.

**How to apply:** Khi triển khai drag-from-list, cross-control pointer tracking, hay custom gesture — dùng `AddHandler` với `handledEventsToo: true` cho tất cả các ListBox/ItemsControl.
