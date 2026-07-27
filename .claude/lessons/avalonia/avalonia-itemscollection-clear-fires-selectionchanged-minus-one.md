---
category: avalonia
tags: [listbox, selectionchanged, items-clear, usercontrol-wrapper, kzsidebar]
severity: high
created: 2026-07-27
updated: 2026-07-27
project-origin: iAccess Desktop v2 (App-Access-V2, STEP-8.4 shell redesign)
---

# `ListBox.Items.Clear()` bắn `SelectionChanged(-1)` xuống consumer — crash ngầm khi wrapper control rebuild items lúc attach

## Tình huống gặp phải

Dựng `AppShellWindow` (shell sidebar 4 mục) dùng `KzSidebar` (KztekComponentAvalonia).
`KzSidebar.OnAttachedToVisualTree` gọi `RebuildItems()`: `lb.Items.Clear()` rồi add lại item.
App subscribe `ItemSelected` và map index → page: `Navigate((ShellSection)index)`.

## Triệu chứng / Lỗi

App crash ngay khi mở window, stacktrace bắt nguồn từ `AvaloniaList.Clear()`:

```
System.Collections.Generic.KeyNotFoundException: The given key '-1' was not present in the dictionary.
   at AppShellWindow.Navigate(ShellSection section)
   ...
   at Avalonia.Controls.ItemCollection.Clear()
   at KzSidebar.RebuildItems()
   at KzSidebar.OnAttachedToVisualTree(...)
```

## Nguyên nhân gốc rễ (Root Cause)

`Items.Clear()` của ListBox (SelectingItemsControl) reset selection và **bắn `SelectionChanged` với `SelectedIndex = -1` một cách đồng bộ ngay trong Clear()**. Wrapper control (KzSidebar) forward sự kiện này ra ngoài (`ItemSelected`) → consumer nhận index `-1` không lường trước → tra dictionary bằng enum cast từ -1 → crash. Ngoài ra selection đã set trước đó (qua property) bị mất vĩnh viễn sau rebuild.

## Cách xử lý

1. **Trong wrapper control** (KzSidebar.RebuildItems): lưu `SelectedIndex` TRƯỚC khi `Clear()`, khôi phục SAU khi add lại:
   ```csharp
   var keep = SelectedIndex;
   lb.Items.Clear();          // fires SelectionChanged(-1)!
   foreach (...) lb.Items.Add(...);
   if (keep >= 0 && keep < lb.Items.Count) lb.SelectedIndex = keep;
   ```
2. **Consumer luôn guard index âm**: `if (index >= 0) Navigate(...)`.
3. **Không set selection mặc định trong ctor của window** — set trong `Opened` event (sau khi ListBox đã attach + có items), nếu không selection bị RebuildItems lúc attach ghi đè về -1.

## Cách phòng tránh

- Mọi wrapper control forward `SelectionChanged` phải coi `-1` là giá trị hợp lệ sẽ xảy ra (Clear/rebuild/detach) — hoặc lọc tại wrapper, hoặc ghi rõ trong doc cho consumer guard.
- Khởi tạo selection mặc định: dùng `Window.Opened` / `Loaded`, không dùng ctor.
