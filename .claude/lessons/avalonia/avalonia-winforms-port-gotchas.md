---
category: avalonia
tags: [migration, winforms, mvvm, communitytoolkit, skiasharp, datagrid, combobox]
severity: medium
created: 2026-06-25
updated: 2026-06-25
project-origin: IParkingDetectApp (Avalonia migration)
---

# Avalonia port từ WinForms: gotcha thực tế khi build (CommunityToolkit, ComboBox, Theme name, SkiaSharp)

## Tình huống gặp phải

Migrate IParkingDetectApp (YOLO/OpenVINO tester) từ WinForms → Avalonia 11.2.7 + CommunityToolkit.Mvvm 8.4.0,
thay toàn bộ `System.Drawing` bằng SkiaSharp để build cross-platform (win-x64 + linux-x64). Một loạt gotcha
chỉ lộ ra lúc build, không thấy trong tài liệu.

## Các gotcha + cách xử lý

### 1. `[ObservableProperty]` đụng tên với method (CS0102)
`[ObservableProperty] private string _statusText;` sinh property `StatusText`. Nếu trong class còn một
`static string StatusText(...)` → **CS0102 "already contains a definition for 'StatusText'"** (lỗi báo ở file
`.g.cs` của source generator, dễ hiểu nhầm là lỗi generator).
→ **Fix:** đổi tên method (vd `StatusLabel`). Quy tắc: tên method/field KHÔNG được trùng tên property mà
`[ObservableProperty]` sẽ sinh ra (field `_xxx` → property `Xxx`).

### 2. `Theme` static class đụng `Control.Theme` instance property
Trong custom `Control`, viết `Theme.DeepBrush` (Theme là static class của mình) → compiler resolve nhầm sang
`this.Theme` (kiểu `ControlTheme` kế thừa từ `StyledElement`) → **CS1061 'ControlTheme' does not contain ...**.
`using Theme = ...` alias KHÔNG cứu được vì member-access ưu tiên instance member.
→ **Fix:** đặt alias tên KHÁC: `using Brand = IParkingDetect.UI.Theme;` rồi dùng `Brand.DeepBrush`.

### 3. ComboBox Avalonia KHÔNG có `IsEditable` / `Text`
WinForms `ComboBox` với `DropDownStyle = DropDown` (editable, free-text + history) không map sang Avalonia
`ComboBox` (chỉ chọn item, có `SelectedItem`, không `Text`/`IsEditable`) → AVLN2000.
→ **Fix:** dùng `AutoCompleteBox` (`ItemsSource` + `Text` two-way) cho ô nhập có gợi ý lịch sử.
ComboBox chỉ-chọn: bind `ItemsSource` (mảng string) + `SelectedItem`. KHÔNG dùng `<ComboBoxItem>` literal +
`SelectedItem="{Binding stringProp}"` (SelectedItem sẽ là ComboBoxItem, không phải string).

### 4. Custom `Control` không có `Background`
Kế thừa `Control` (không phải `TemplatedControl`/`Border`/`Panel`) → KHÔNG có property `Background` → set
`Background=` trong AXAML báo AVLN2000.
→ **Fix:** tự vẽ nền trong `Render(DrawingContext)`, hoặc bọc trong `Border`.

### 5. Compiled binding trong TreeDataTemplate cần `DataType` riêng
`x:DataType` của Window là ViewModel, nhưng item của `TreeView`/`TreeDataTemplate` là kiểu node khác
(`TreeNodeVm`) → compiled binding không resolve `Children`/`Label` ("XamlPseudoType").
→ **Fix:** `<TreeDataTemplate DataType="views:TreeNodeVm" ItemsSource="{Binding Children}">`.

### 6. SkiaSharp 2.88: API text khác bản 3.x
Bản 2.88.9 (đi cùng Avalonia 11.2.x): vẽ chữ qua `SKPaint { Typeface, TextSize }` + `canvas.DrawText(str, x, y, paint)`,
đo bằng `paint.MeasureText(str)`. KHÔNG có overload `DrawText(str, x, y, SKTextAlign, SKFont, SKPaint)` (đó là API 3.x).

### 7. Thay `Bitmap.LockBits` (NCHW) bằng SKBitmap
GDI+ dùng `Format24bppRgb` (3 byte BGR, có stride padding). `SKBitmap` Rgba8888 = 4 byte RGBA.
Khi viết NCHW phải đọc offset `x*4` (R=+0, G=+1, B=+2), stride = `SKBitmap.RowBytes`, pixel qua `GetPixels()`.
Letterbox: `SKCanvas.Clear(SKColor(114,114,114))` + `DrawBitmap(src, SKRect dest, paint)` thay `Graphics.DrawImage`.

### 8. SKBitmap → Avalonia Bitmap để hiển thị
Convert qua `WriteableBitmap(size, dpi, PixelFormat.Rgba8888, AlphaFormat.Premul)` + `Lock()` rồi
`Buffer.MemoryCopy` từng dòng (chú ý `RowBytes` của src và `fb.RowBytes` của đích có thể khác nhau → copy min).

## Áp dụng lại

- Trước khi đặt tên field `[ObservableProperty]` → kiểm tra không có method trùng tên property sinh ra.
- Trong custom Control, dùng alias tên lạ cho static helper trùng tên Avalonia member (`Theme`, `Styles`, `Resources`).
- WinForms editable ComboBox → Avalonia `AutoCompleteBox`. ComboBox chỉ-chọn → ItemsSource string + SelectedItem.
- Item template của control list/tree → luôn khai báo `DataType` cho compiled binding.
- Kiểm tra phiên bản SkiaSharp khớp Avalonia (2.88.x cho Avalonia 11.2.x) trước khi viết code vẽ text.

## Chú ý / Cạm bẫy

- ⚠️ CS0102 ở file `.g.cs` source-gen thường là do trùng tên với property generator sinh — đọc kỹ tên thành viên.
- ⚠️ Build win-x64 xanh KHÔNG đảm bảo linux-x64 xanh; luôn `dotnet build -r linux-x64` để bắt dependency Windows-only.
- ⚠️ Publish self-contained linux-x64 phải có `libSkiaSharp.so` + `libHarfBuzzSharp.so` trong publish dir mới render được.
- ⚠️ OpenVINO `Sdcb.OpenVINO.runtime.win-x64` chỉ là native Windows — build linux vẫn pass (nạp lúc chạy),
  nhưng để inference trên Linux phải thêm `Sdcb.OpenVINO.runtime.linux-x64`. Đặt PackageReference điều kiện theo RID.

## Tham chiếu

- Project: IParkingDetectApp.Avalonia
- File: ViewModels/MainViewModel.cs, Controls/ImageCanvas.cs, Helpers/BboxRenderer.cs, Inference/YoloRunner.cs
- Liên quan: avalonia-migration-from-winforms.md, dotnet-linux-compat-tfm-resx-systemdrawing.md
