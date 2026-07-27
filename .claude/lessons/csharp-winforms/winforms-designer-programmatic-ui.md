---
category: csharp-winforms
tags: [designer, partial-class, programmatic-ui, DesignerCategory]
severity: medium
created: 2026-06-24
updated: 2026-06-24
project-origin: IParkingDetectApp
---

# WinForms Designer Không Render Được Programmatic UI

## Tình huống gặp phải

> Đang tách UI code sang `DetectForm.Designer.cs` theo partial class pattern.  
> Mở designer tab trong VS thì form hiển thị trống (chỉ thấy form shell + SplitContainer handles).

## Triệu chứng / Lỗi

```
DetectForm.cs [Design] — form trống, không thấy controls
Toolbar, status bar, log panel không hiện
Chỉ thấy SplitContainer outline mờ
```

## Nguyên nhân gốc rễ (Root Cause)

VS WinForms Designer **phân tích tĩnh** (static analysis) `InitializeComponent()` — nó KHÔNG chạy code.  
Designer chỉ hiểu được:
- Direct `new Control()` call với property assignment trực tiếp
- Không hiểu helper method như `Theme.Btn()`, `BuildToolbar()` v.v.

Thêm vào đó: khi file `DetectForm.Designer.cs` tồn tại, VS nhận dạng nó là **output của WYSIWYG designer**, cố parse và thất bại → hiển thị form trống.

## Giải pháp

### Bước 1: Đổi tên file tránh VS nhận dạng

```
DetectForm.Designer.cs  →  DetectForm.UI.cs
```

VS nhận dạng `*.Designer.cs` là designer file. Đổi tên sang `*.UI.cs` thì VS coi đó là code file bình thường.

```bash
mv DetectForm.Designer.cs DetectForm.UI.cs
```

### Bước 2: Thêm attribute ngăn Designer mở

```csharp
// DetectForm.cs — đặt TRƯỚC class declaration
[System.ComponentModel.DesignerCategory("Code")]
public sealed partial class DetectForm : Form
{
    ...
}
```

Sau khi thêm: double-click vào `DetectForm.cs` trong Solution Explorer sẽ mở **code view** thay vì Designer view.

### Cấu trúc file đúng

```
IParkingDetectApp/
  DetectForm.cs        ← logic: fields, constructor, event handlers, Dispose
  DetectForm.UI.cs     ← UI: control fields, InitializeComponent(), Build* methods
```

**Quy tắc `DetectForm.UI.cs`:**
- `partial class DetectForm` (không cần `public sealed` — đã khai báo trong `.cs`)
- Chỉ chứa code tạo widget, KHÔNG chứa logic nghiệp vụ
- `InitializeComponent()` gọi các `Build*()` method
- Wire event handlers OK (lambda ngắn), nhưng business logic phải ở `.cs`

## Áp dụng lại (How to reuse)

- **Khi tách UI sang Designer file** → dùng tên `*.UI.cs` thay vì `*.Designer.cs`
- **Khi VS mở Designer view trống** → thêm `[DesignerCategory("Code")]` + đổi tên file
- **Programmatic dark-theme WinForms** → KHÔNG dùng VS Designer, code thuần sẽ luôn rõ hơn

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ `*.Designer.cs` là naming convention đặc biệt của VS — tránh dùng cho programmatic UI
- ⚠️ `[DesignerCategory("")]` (empty string) cũng hoạt động nhưng `"Code"` rõ ràng hơn
- ⚠️ VS có thể TỰ ĐỘNG GHI ĐÈ `*.Designer.cs` nếu bạn lỡ mở Designer tab → mất toàn bộ code UI
- ⚠️ Với partial class, `sealed` chỉ cần khai báo ở MỘT file (thường là file chính `.cs`)
- ⚠️ Cả hai file đều cần `using` riêng — partial class không share `using` directives

## Tham chiếu

- Project: IParkingDetectApp (KZTEK iParking Detection Tester)
- VS 2022 + .NET 8 WinForms
