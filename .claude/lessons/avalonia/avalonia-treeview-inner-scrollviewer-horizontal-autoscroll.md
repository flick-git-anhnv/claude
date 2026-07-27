---
category: avalonia
tags: [treeview, scrollviewer, auto-scroll, bringintoview, template]
severity: medium
created: 2026-07-27
updated: 2026-07-27
project-origin: App-Access-V2 (iAccess Desktop v2) + KztekComponentAvalonia
---

# TreeView có ScrollViewer NỘI BỘ — bọc ScrollViewer ngoài Disabled không chặn được auto-scroll ngang khi select

## Tình huống gặp phải

Fix finding F2 UX review Phase 8 redesign iAccess (Avalonia 12.1.0): panel cây thiết bị dùng `KzDeviceTree` (KztekComponentAvalonia) — control này bọc `TreeView` trong 1 `ScrollViewer` ngoài với `HorizontalScrollBarVisibility="Disabled"`.

## Triệu chứng / Lỗi

```
Click chọn 1 node dài trong cây → toàn bộ tree TỰ SCROLL NGANG,
header "Danh sách thiết bị" bị cụt thành "anh sách thiết bị",
dù ScrollViewer bao ngoài đã đặt HorizontalScrollBarVisibility="Disabled".
```

## Nguyên nhân gốc rễ (Root Cause)

`TreeView` của Avalonia có **ScrollViewer riêng bên trong ControlTemplate mặc định** (Fluent theme). ScrollViewer ngoài do mình bọc thêm không có gì để scroll (TreeView tự quản scroll), còn ScrollViewer nội bộ vẫn Auto → khi select node, `BringIntoView` đẩy offset ngang của ScrollViewer NỘI BỘ, gây auto-scroll cụt header. Disabled ở lớp ngoài hoàn toàn vô tác dụng.

## Giải pháp

Đặt attached property trực tiếp trên TreeView — nó được template mặc định bind vào ScrollViewer nội bộ:

```xml
<TreeView Name="PART_Tree"
          ScrollViewer.HorizontalScrollBarVisibility="Disabled">
```

1. Bỏ (hoặc giữ vô hại) ScrollViewer bọc ngoài — không phải chỗ quyết định.
2. Set `ScrollViewer.HorizontalScrollBarVisibility="Disabled"` trên chính TreeView → ScrollViewer nội bộ không thể đổi offset ngang → hết auto-scroll khi select.
3. Nội dung node dài → thêm `ToolTip.Tip` để vẫn đọc được khi bị giới hạn bề ngang.

Áp dụng tại: `5.BaseUI/KztekComponentAvalonia/Controls/KzDeviceTree.axaml` (commit `0519a00`).

## Cách phòng tránh lần sau

- Với các ItemsControl có scroll tích hợp (TreeView, ListBox, DataGrid...), cấu hình scroll bằng **attached property `ScrollViewer.*` trên chính control**, KHÔNG bọc thêm ScrollViewer ngoài rồi kỳ vọng nó điều khiển được.
- Khi thấy "đã Disabled mà vẫn scroll" → nghi ngay có ScrollViewer thứ hai trong template mặc định của control.
