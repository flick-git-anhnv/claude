---
category: avalonia
tags: [tabcontrol, datagrid, visual-tree, lazy-loading, columns]
severity: high
created: 2026-06-26
updated: 2026-06-26
project-origin: iPGSv4 CCU Avalonia
---

# Avalonia TabControl: Columns không hiển thị ở tab không được chọn lần đầu

## Tình huống gặp phải

> Đang migrate SettingWindow (WinForms → Avalonia). Window có `TabControl` với 10 TabItems, mỗi TabItem chứa một `KzCrudControl` (custom UserControl wrapping DataGrid + toolbar + navigation). Setup tất cả controls trong sự kiện `Loaded` của Window.

## Triệu chứng / Lỗi

```
- Tab "Tầng" (tab đầu tiên, được chọn mặc định) hiển thị đúng: dữ liệu + cột đầy đủ.
- Tất cả tab còn lại (ZCU, Nhóm Zone, Zone, Bản đồ, LED, Kiosk, ...):
  - Footer navigation hiển thị đúng số bản ghi ("5 bản ghi")
  - Grid trắng hoàn toàn — không có cột, không có dòng
```

## Nguyên nhân gốc rễ (Root Cause)

**Avalonia `TabControl` virtualizes content by default**: nội dung của tab chưa được chọn CHƯA được attach vào visual tree.

Trong `KzCrudControl.OnAttachedToVisualTree()`, `_grid` (DataGrid) mới được khởi tạo:
```csharp
protected override void OnAttachedToVisualTree(VisualTreeAttachmentEventArgs e)
{
    _grid = this.FindControl<DataGrid>("PART_Grid")!;
    // ...
    SyncAll(); // Sets _grid.ItemsSource
}
public DataGrid? InnerGrid => _grid; // null nếu chưa được attach
```

Khi `SetupCrud()` chạy trong `OnWindowLoaded()` cho TẤT CẢ controls:
```csharp
private static void SetupCrud(KzCrudControl ctrl, IEnumerable source,
                               List<DataGridTextColumn> columns)
{
    if (ctrl.InnerGrid is { } grid) // ← NULL với non-selected tabs!
    {
        grid.Columns.Clear();
        foreach (var col in columns)
            grid.Columns.Add(col); // ← KHÔNG BAO GIỜ CHẠY với tab chưa chọn
    }
    ctrl.ItemsSource = source; // ← Được lưu vào styled property (OK)
    ctrl.TotalPages  = 1;
}
```

Kết quả:
- Tab đầu tiên: `InnerGrid != null` → columns được add → hiển thị đúng.
- Tab còn lại: `InnerGrid == null` → columns KHÔNG được add.
- Khi tab được chọn lần đầu: `OnAttachedToVisualTree` fires → `SyncAll()` set `_grid.ItemsSource` → data có nhưng **không có columns** → grid trắng.
- Footer hiển thị đúng vì `TotalRows` được tính từ `ItemsSource` (không cần grid attach).

## Giải pháp

Thêm `_pendingColumns` + `SetColumns()` vào `KzCrudControl` để lưu columns và apply khi `SyncAll()` được gọi sau khi `_grid` available:

```csharp
// Trong KzCrudControl.axaml.cs

private List<DataGridColumn>? _pendingColumns;

public void SetColumns(IEnumerable<DataGridColumn> columns)
{
    if (_grid is not null)
    {
        _grid.Columns.Clear();
        foreach (var col in columns) _grid.Columns.Add(col);
    }
    else
    {
        _pendingColumns = new List<DataGridColumn>(columns);
    }
}

private void SyncAll()
{
    if (_grid is null) return;
    if (_pendingColumns is not null)
    {
        _grid.Columns.Clear();
        foreach (var col in _pendingColumns) _grid.Columns.Add(col);
        _pendingColumns = null;
    }
    _grid.ItemsSource  = ItemsSource;
    // ...
}
```

Trong `SettingWindow.axaml.cs`:
```csharp
private static void SetupCrud(KzCrudControl ctrl, IEnumerable source,
                               List<DataGridTextColumn> columns)
{
    ctrl.SetColumns(columns.Cast<DataGridColumn>()); // ← Dùng SetColumns thay InnerGrid
    ctrl.ItemsSource = source;
    ctrl.TotalPages  = 1;
}
```

## Áp dụng lại (How to reuse)

- Khi dùng `TabControl` trong Avalonia và cần khởi tạo tất cả tabs trong `Loaded` event → KHÔNG truy cập trực tiếp `InnerGrid` / controls bên trong custom UserControl.
- Custom UserControl phải expose API deferred-safe (ví dụ `SetColumns()`) thay vì để caller access inner controls.
- Kiểm tra: nếu control có `OnAttachedToVisualTree` để khởi tạo inner controls → mọi caller phải biết control có thể chưa attach.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ **Footer/navigation hiển thị đúng nhưng grid trắng** là dấu hiệu đặc trưng: data có (ItemsSource được lưu vào styled property) nhưng columns thiếu → grid render trống.
- ⚠️ **Chỉ tab đầu tiên (selected mặc định) hoạt động** → chắc chắn đây là vấn đề lazy visual tree.
- ⚠️ `_pendingColumns = null` sau khi apply trong `SyncAll()` — tránh apply lại khi `SyncAll()` bị gọi nhiều lần (ví dụ khi `ItemsSource` thay đổi).
- ⚠️ `DataGridTextColumn` instances trong `_pendingColumns` không thể chia sẻ giữa nhiều DataGrid — mỗi `SetColumns()` tạo list mới.

## Tham chiếu

- Avalonia TabControl: content virtualization là behavior mặc định, khác WinForms TabPage.
- Project: iPGSv4 CCU Avalonia — `KztekComponentAvalonia/Controls/KzCrudControl.axaml.cs` + `IPGSv4/Views/SettingWindow.axaml.cs`
