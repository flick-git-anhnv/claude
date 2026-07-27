---
category: avalonia
tags: [StyledProperty, OnPropertyChanged, CollectionChanged, subscription, MVVM, binding, visual-tree, race-condition]
severity: high
created: 2026-06-25
updated: 2026-06-25
project-origin: iPGSv4 - KztekComponentAvalonia
---

# AvaloniaProperty subscription phải nằm ngoài guard `_control is not null`

## Tình huống gặp phải

Đang implement `KzCrudControl` — control có DataGrid bên trong. `ItemsSource` là `StyledProperty` nhận binding từ ViewModel. Cần subscribe `CollectionChanged` để tự động cập nhật `TotalRows` khi collection thay đổi.

## Triệu chứng / Lỗi

`TotalRows` không cập nhật khi dùng MVVM binding — ví dụ:

```xml
<!-- ViewModel binding — TotalRows không bao giờ update -->
<kz:KzCrudControl ItemsSource="{Binding Cameras}" />
```

Nhưng khi set trực tiếp từ code-behind sau khi control đã attach thì hoạt động:
```csharp
crudControl.ItemsSource = viewModel.Cameras;  // works
```

Không có exception. Binding "hoạt động" (DataGrid hiển thị đúng data) nhưng subscription `CollectionChanged` không được thiết lập.

## Nguyên nhân gốc rễ (Root Cause)

`OnPropertyChanged` (override AvaloniaObject) được gọi **trước khi** visual tree attach. Nếu logic subscribe `CollectionChanged` bị đặt bên trong `if (_grid is not null)` guard, thì khi MVVM binding fires (trước `OnAttachedToVisualTree`), `_grid` vẫn là null → subscription bị bỏ qua hoàn toàn.

```csharp
// ❌ SAI — subscription bị bỏ qua khi binding fire trước attach
protected override void OnPropertyChanged(AvaloniaPropertyChangedEventArgs change)
{
    base.OnPropertyChanged(change);
    if (change.Property == ItemsSourceProperty)
    {
        if (_grid is not null)  // ← đây là vấn đề
        {
            _grid.ItemsSource = ItemsSource;
            // subscribe CollectionChanged nằm ở đây → KHÔNG CHẠY khi MVVM binding
        }
    }
}
```

## Giải pháp

Tách logic subscription ra ngoài guard `_grid is not null`. Chỉ gating việc sync sang `_grid`, không gating subscription:

```csharp
// ✅ ĐÚNG
private INotifyCollectionChanged? _subscribedCollection;
private NotifyCollectionChangedEventHandler? _onCollectionChanged;

protected override void OnPropertyChanged(AvaloniaPropertyChangedEventArgs change)
{
    base.OnPropertyChanged(change);
    if (change.Property == ItemsSourceProperty)
    {
        // Unsubscribe old — LUÔN làm, không cần guard
        if (_subscribedCollection is not null)
        {
            _subscribedCollection.CollectionChanged -= _onCollectionChanged;
            _subscribedCollection = null;
        }

        // Subscribe new — LUÔN làm, không cần guard
        if (ItemsSource is INotifyCollectionChanged incc)
        {
            _subscribedCollection = incc;
            _onCollectionChanged = (_, _) => TotalRows = GetCount(ItemsSource);
            _subscribedCollection.CollectionChanged += _onCollectionChanged;
        }

        // Sync count — không cần grid
        TotalRows = GetCount(ItemsSource);

        // Sync grid — có guard
        if (_grid is not null)
            _grid.ItemsSource = ItemsSource;
    }
}
```

Cleanup bắt buộc trong `OnDetachedFromVisualTree`:

```csharp
protected override void OnDetachedFromVisualTree(VisualTreeAttachmentEventArgs e)
{
    base.OnDetachedFromVisualTree(e);
    if (_subscribedCollection is not null)
    {
        _subscribedCollection.CollectionChanged -= _onCollectionChanged;
        _subscribedCollection = null;
    }
}
```

## Áp dụng lại (How to reuse)

- **Quy tắc chung:** Logic trong `OnPropertyChanged` chạy trước `OnAttachedToVisualTree` → bất kỳ subscription nào trong `OnPropertyChanged` KHÔNG ĐƯỢC phụ thuộc vào visual tree controls
- Khi cần subscribe event dựa trên DP value → làm trong `OnPropertyChanged`, KHÔNG đặt trong `if (_someControl is not null)` guard
- Chỉ guard những thao tác **cần có control** (như `_grid.ItemsSource = ...`), không guard subscription/unsubscription
- Luôn lưu delegate reference vào field riêng để `-=` đúng instance (lambda mới sẽ không match)

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Pattern này ảnh hưởng đặc biệt với MVVM — `{Binding}` fires rất sớm trong object lifecycle, thường trước visual tree attach
- ⚠️ Code-behind `control.Property = value` thường fires SAU attach → làm cho bug ẩn đi khi test thủ công
- ⚠️ Delegate reference: `_subscribedCollection.CollectionChanged -= (_, _) => ...` KHÔNG unsubscribe được — phải lưu delegate vào field: `_onCollectionChanged = (_, _) => ...; ... -= _onCollectionChanged`
- ⚠️ `_isUpdatingSelection` (hoặc bất kỳ guard bool nào) phải được bọc trong `try/finally` — exception giữa `= true` và `= false` sẽ permanent lock:
  ```csharp
  _isUpdatingSelection = true;
  try { SelectedItem = _grid.SelectedItem; }
  finally { _isUpdatingSelection = false; }
  ```

## Tham chiếu

- Project liên quan: iPGSv4 / KztekComponentAvalonia / `Controls/KzCrudControl.axaml.cs`
- Avalonia version: 11.2.7
- Verified: 2026-06-25
