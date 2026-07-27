# Avalonia 12: `TextBox.Watermark` và `Window.SystemDecorations` bị obsolete

**Category:** avalonia
**Ngày:** 2026-07-26
**Project:** iPGSv4 CCU (ccu-avalonia)
**Loại:** Gotcha

---

## Triệu chứng

Sau khi nâng lên Avalonia 12.1.0, build thành công (0 errors) nhưng sinh **142 lượt warning `AVLN5001`**:

```
Views/ZcuEditWindow.axaml(25,12): Avalonia warning AVLN5001:
  'TextBox.Watermark' is obsolete: Use PlaceholderText instead.
Views/LoadingWindow.axaml(11,9): Avalonia warning AVLN5001:
  'Window.SystemDecorations' is obsolete: Use WindowDecorations instead.
```

Warning kiểu này dễ bị bỏ qua vì build vẫn xanh — nhưng nó lấp kín output, che mất warning thật, và property sẽ bị gỡ ở bản Avalonia sau.

## Nguyên nhân

Avalonia 12 đổi tên hai API để đồng bộ với chuẩn đặt tên chung:

| Avalonia ≤ 11 | Avalonia 12 |
|---|---|
| `TextBox.Watermark` | `TextBox.PlaceholderText` |
| `Window.SystemDecorations` | `Window.WindowDecorations` |

Giá trị enum không đổi (`WindowDecorations="None"` vẫn hợp lệ).

## Cách khắc phục

Thay hàng loạt trong `.axaml`:

```xml
<!-- TRƯỚC -->
<TextBox Watermark="Nhập tên đăng nhập..." />
<Window SystemDecorations="None">

<!-- SAU -->
<TextBox PlaceholderText="Nhập tên đăng nhập..." />
<Window WindowDecorations="None">
```

Và trong code-behind:

```csharp
tb.Watermark = value;        // ❌ obsolete
tb.PlaceholderText = value;  // ✅
```

Script thay hàng loạt (chạy từ root project):

```python
import io, glob, os, re
for p in glob.glob("**/*.axaml", recursive=True):
    if os.sep+"obj"+os.sep in p or os.sep+"bin"+os.sep in p: continue
    s = io.open(p, encoding="utf-8-sig").read()
    if "Watermark=" in s:
        io.open(p, "w", encoding="utf-8").write(re.sub(r'\bWatermark=', 'PlaceholderText=', s))
```

## ⚠️ Bẫy quan trọng — custom control có property tên `Watermark`

`KzPasswordTextBox` (KztekComponentAvalonia) tự khai báo `StyledProperty<string?> WatermarkProperty` là **API công khai của thư viện dùng chung**. Thay mù bằng regex sẽ phá API của mọi project đang dùng.

Quy tắc:
- **Giữ nguyên** tên property công khai `Watermark` của custom control.
- **Chỉ đổi** chỗ nó gán xuống `TextBox` nội bộ:

```csharp
private void ApplyWatermark()
{
    if (this.FindControl<TextBox>("PART_Input") is { } tb)
        tb.PlaceholderText = Watermark;   // ✅ property ngoài giữ tên cũ
}
```

Kiểm tra trước khi thay: control đó `: TextBox` (kế thừa → dùng `PlaceholderText`) hay là `TemplatedControl` tự định nghĩa `Watermark` (giữ nguyên)?

```bash
grep -rn "class KzTextBox" Controls/     # KzTextBox : TextBox  → thay được
grep -rn "WatermarkProperty" Controls/   # có StyledProperty riêng → KHÔNG đổi tên
```

## Cách verify

```bash
dotnet build <sln>.sln -c Debug -v n --nologo -t:Rebuild 2>&1 \
  | grep -oE "warning AVLN[0-9]+" | sort | uniq -c
```
Phải ra rỗng. Lưu ý: đếm bằng `grep` trên output `-v n` sẽ **gấp đôi** số thật (MSBuild in warning cả ở pass build lẫn summary) — lấy số ở dòng `N Warning(s)` của summary mới chính xác.

## Liên quan

- [[avalonia-12-breaking-changes-rabbitmq7-migration]]
- [[avalonia-devtools-package-migration-v12]]
- [[kz-component-wrap-workaround-pattern]]
