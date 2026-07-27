---
category: avalonia
tags: [msbox, messagebox, namespace, nuget, dialog]
severity: high
created: 2026-07-13
updated: 2026-07-13
project-origin: Kztek.Camera (migrate WinForms→Avalonia G5.10)
---

# MsBox.Avalonia 3.0.0-rc2: ButtonEnum và Icon nằm ở 2 namespace khác nhau

## Tình huống gặp phải

Đang migrate CameraDescriptionPage (WinForms → Avalonia), cần dùng MsBox.Avalonia để
thay thế `MessageBox.Show()`. Dùng `using MsBox.Avalonia.Enums;` rồi gọi:

```csharp
MessageBoxManager.GetMessageBoxStandard("Thông báo", "Lỗi!", ButtonEnum.Ok, Icon.Stop)
```

## Triệu chứng / Lỗi

```
error CS0103: The name 'ButtonEnum' does not exist in the current context
```

Dù đã `using MsBox.Avalonia.Enums;` — vẫn không tìm thấy `ButtonEnum`.

## Nguyên nhân gốc rễ (Root Cause)

MsBox.Avalonia 3.0.0-rc2 là package **transition** — chứa cả namespace cũ và mới trong cùng 1 DLL:

| Type | Namespace thực tế |
|---|---|
| `ButtonEnum` | `MessageBox.Avalonia.Enums` ← namespace **CŨ** |
| `ButtonResult` | `MsBox.Avalonia.Enums` ← namespace mới |
| `ClickEnum` | `MsBox.Avalonia.Enums` |
| `Icon` | `MsBox.Avalonia.Enums` ← namespace mới |
| `MessageBoxManager` | `MsBox.Avalonia` |

`ButtonEnum` **không tồn tại** trong `MsBox.Avalonia.Enums` — chỉ có trong
`MessageBox.Avalonia.Enums` (legacy).

## Giải pháp

Dùng **2 using riêng biệt**:

```csharp
using MsBox.Avalonia;                       // MessageBoxManager
using MessageBox.Avalonia.Enums;            // ButtonEnum (legacy namespace)
using MsBox.Avalonia.Enums;                // Icon (namespace mới)
```

Gọi:

```csharp
_ = MessageBoxManager
    .GetMessageBoxStandard("Thông báo", "Đã tồn tại Camera với tên này!", ButtonEnum.Ok, Icon.Stop)
    .ShowAsync();
```

**Hoặc** dùng overload 2 tham số (không cần ButtonEnum):

```csharp
using MsBox.Avalonia;   // đủ

_ = MessageBoxManager
    .GetMessageBoxStandard("Thông báo", "Đã tồn tại Camera với tên này!")
    .ShowAsync();
```

## Áp dụng lại (How to reuse)

- Khi dùng `ButtonEnum` → `using MessageBox.Avalonia.Enums;` (namespace cũ `MessageBox.`)
- Khi dùng `Icon` → `using MsBox.Avalonia.Enums;` (namespace mới `MsBox.`)
- Nếu chỉ cần dialog đơn giản → dùng overload 2 tham số để tránh import phức tạp

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ MsBox.Avalonia chỉ có version `3.0.0-rc2` trên NuGet (tính đến 2026-07) — **không tự upgrade** (theo lesson TL-014)
- ⚠️ `ButtonResult` (kết quả sau khi user click) khác với `ButtonEnum` (cấu hình nút hiển thị)
- ⚠️ Trong context sync (Apply() của IWizardPage), phải fire-and-forget: `_ = ...ShowAsync()` — dialog vẫn hiện nhưng caller không block chờ
- ⚠️ `MessageBox.Avalonia.Enums` (namespace cũ) và `MsBox.Avalonia.Enums` (mới) có thể gây ambiguity nếu dùng cùng lúc nhiều type — prefer overload 2 tham số khi có thể

## Tham chiếu

- Project liên quan: `Kztek.Camera` — task G5.10 migrate CameraDescriptionPage
- Commit: `4cea384` — `[PLAN-kztek-cameras-to-avalonia] Bước G5.10`
- MsBox.Avalonia NuGet: https://www.nuget.org/packages/MsBox.Avalonia/3.0.0-rc2
