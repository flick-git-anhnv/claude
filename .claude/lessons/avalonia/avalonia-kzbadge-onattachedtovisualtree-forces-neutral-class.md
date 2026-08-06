---
category: avalonia
tags: [custom-control, kzbadge, classes, OnAttachedToVisualTree, styledproperty, control-theme]
severity: high
created: 2026-08-06
updated: 2026-08-06
project-origin: KztekComponentAvalonia (App-Access-V2)
---

# KzBadge mất/sai màu vì OnAttachedToVisualTree ép Classes về mặc định Neutral+Pill

## Tình huống gặp phải

Thư viện `KztekComponentAvalonia`, control `KzBadge : TemplatedControl`
(`Controls/KzBadge.cs`). Đang xem preview của `KzBadge.axaml` (`Design.PreviewWith`) —
6 biến thể màu (success/warning/error/info/neutral/accent) x 2 dáng (pill/tag), mỗi badge
khai báo trực tiếp qua XAML:

```xml
<kz:KzBadge Classes="kz-badge-pill kz-badge-success" Content="Success" />
<kz:KzBadge Classes="kz-badge-tag kz-badge-warning" Content="Warning" />
```

## Triệu chứng / Lỗi

Preview hiện TẤT CẢ badge giống nhau — chỉ còn chữ đen trên nền trắng/xám, không có màu
nền pill/tag nào cả, trông như style không áp dụng. Không có exception, build sạch.
Dễ nhầm là lỗi riêng của Previewer (Design.PreviewWith, ResourceInclude, DynamicResource
Theme override...) vì hiện tượng chỉ "thấy" rõ ở preview.

## Nguyên nhân gốc rễ (Root Cause)

`KzBadge.cs` có 2 property `Variant`/`BadgeType` (dùng khi binding từ ViewModel) VÀ hỗ trợ
gán `Classes="..."` trực tiếp qua XAML (dùng phổ biến trong codebase, ví dụ
`RegisterStatusCardView.axaml`, `ServerDataChangeCardView.axaml`). Hai cách này xung đột:

```csharp
protected override void OnAttachedToVisualTree(VisualTreeAttachmentEventArgs e)
{
    base.OnAttachedToVisualTree(e);
    UpdateClasses();   // ← chạy VÔ ĐIỀU KIỆN mỗi lần control gắn vào visual tree
}
```

`UpdateClasses()` XÓA toàn bộ class hiện có rồi add lại DUY NHẤT theo `Variant`/`BadgeType`
hiện tại. Vì không ai set 2 property này khi dùng cách gán `Classes` trực tiếp, giá trị mặc
định (`Variant = Neutral`, `BadgeType = StatusPill`) luôn thắng — mọi badge bị ép về
`kz-badge-pill kz-badge-neutral` bất kể XAML khai báo gì.

Ở preview cụ thể này, hiện tượng còn bị "che" thêm 1 lớp: nền `kz.color.neutral.bg`
(`#F3F4F6`) trùng CHÍNH XÁC màu nền `Border` bọc ngoài `Design.PreviewWith`
(`Background="#F3F4F6"`) → badge Neutral hoà vào nền, tưởng như "mất màu hoàn toàn"
chứ không phải "toàn bộ sai thành 1 màu".

## Giải pháp

Chỉ tự sinh/ghi đè class theo `Variant`/`BadgeType` khi 1 trong 2 property này ĐÃ được set
rõ ràng — dùng `IsSet(...)` ngay trong `OnAttachedToVisualTree`:

```csharp
protected override void OnAttachedToVisualTree(VisualTreeAttachmentEventArgs e)
{
    base.OnAttachedToVisualTree(e);
    if (IsSet(VariantProperty) || IsSet(BadgeTypeProperty))
        UpdateClasses();
}
```

`OnPropertyChanged` giữ nguyên (không cần sửa) — nó chỉ chạy `UpdateClasses()` khi
`Variant`/`BadgeType` THỰC SỰ đổi giá trị (kể cả qua Binding), nên nếu sau này ai bind
`Variant="{Binding ...}"` thì màu vẫn tự cập nhật đúng, không phụ thuộc `IsSet` ở
`OnAttachedToVisualTree`.

## Áp dụng lại (How to reuse)

- Custom control nào hỗ trợ ĐỒNG THỜI 2 cách cấu hình style — (a) gán `Classes` trực tiếp
  qua XAML, (b) property riêng (`Variant`/`Type`/`Size`...) rồi tự suy ra class trong code —
  PHẢI kiểm tra: code có nơi nào override/xoá `Classes` vô điều kiện trong
  `OnAttachedToVisualTree` không? Nếu có, chỉ nên chạy khi property điều khiển đã được set
  (`IsSet`), tránh phá `Classes` gán tay.
- Nếu preview/UI hiện "mất màu" thay vì "sai màu" — nghi ngờ ngay khả năng bị ép về đúng 1
  biến thể mặc định mà biến thể đó VÔ TÌNH cùng màu với nền xung quanh (dễ đánh lạc hướng
  sang nghĩ do ResourceInclude/DynamicResource/Previewer).

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ **`IsSet` KHÔNG phải lúc nào cũng dùng được** — xem lesson liên quan
  [[avalonia-control-overwrites-xaml-property]]: với property gán qua `{DynamicResource ...}`
  (ví dụ `Foreground`), `IsSet` tại thời điểm `OnAttachedToVisualTree` có thể vẫn trả `false`
  vì resource chưa phân giải xong → cách sửa bằng `IsSet` KHÔNG ăn trong trường hợp đó.
  `IsSet` chỉ đáng tin cho property enum/giá trị đơn giản gán trực tiếp qua XAML attribute
  hoặc Binding thường (không phải DynamicResource) — đúng như case `Variant`/`BadgeType`
  của `KzBadge` (không ai dùng DynamicResource cho 2 property này).
- ⚠️ Vì `KzBadge` có `OnPropertyChanged` xử lý đúng khi `Variant`/`BadgeType` đổi giá trị
  (bất kể trước/trong/sau khi attach), fix bằng `IsSet` ở `OnAttachedToVisualTree` an toàn —
  khác với case `KzLabel.Foreground` (không có handler tương ứng để "sửa lại" sau nếu bỏ
  qua lúc attach).
- ⚠️ Bug này ảnh hưởng RUNTIME thật, không chỉ preview — mọi nơi trong app dùng
  `<kz:KzBadge Classes="..."/>` trực tiếp mà không set `Variant`/`BadgeType` đều bị ép về
  Neutral+Pill trước khi có fix này.

## Lần gặp lại

- **2026-08-06 (cùng ngày, cùng task "viết Design.PreviewWith cho toàn bộ thư viện"):**
  `KzButton.cs` mắc CHÍNH XÁC bug họ này — `OnAttachedToVisualTree` gọi
  `UpdateStyleClasses()` vô điều kiện, ép `Variant`/`KzSize` về mặc định
  (`Primary`/`Md`) mỗi lần attach, xoá `Classes="kz-btn-primary kz-size-sm"` gán qua
  XAML. NẶNG HƠN KzBadge: `KzButton` KHÔNG có `OnPropertyChanged` override — chỉ gọi
  `UpdateStyleClasses()` trong CLR setter của `Variant`/`KzSize` — nên trước khi fix,
  `Variant="{Binding ...}"` qua Binding (không đi qua CLR setter) **không đổi màu được
  luôn**, không chỉ riêng vấn đề `OnAttachedToVisualTree`. Fix áp dụng cả 2: (1) guard
  `IsSet(...)` ở `OnAttachedToVisualTree` giống KzBadge, (2) THÊM MỚI `OnPropertyChanged`
  override gọi `UpdateStyleClasses()` khi `VariantProperty`/`KzSizeProperty` đổi — vá luôn
  lỗ hổng Binding chưa từng được xử lý.
- **Gợi ý quét thêm:** bất kỳ Kz custom control nào có `Variant`/`Size`/`Type` property
  + cơ chế `Classes` kép đều nên kiểm tra lại theo checklist này — không chỉ 2 control đã
  gặp (`KzBadge`, `KzButton`).

## Tham chiếu

- File: `KztekComponentAvalonia/Controls/KzBadge.cs`, `KztekComponentAvalonia/Controls/KzButton.cs` (repo `5.BaseUI`)
- Phát hiện khi debug preview `KzBadge.axaml` trong project `App-Access-V2`, 2026-08-06.
- Liên quan: [[avalonia-control-overwrites-xaml-property]] (cùng họ lỗi "custom control ghi
  đè property/class đặt qua XAML", được ghi chú trước đó là "chưa xử lý" cho KzBadge — lesson
  này chốt lại phần đó).
