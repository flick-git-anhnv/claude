# `Style Selector="TextBlock"` toàn cục làm chữ trong nút biến mất (đen trên nền đen)

| Mục | Nội dung |
|---|---|
| Ngày | 2026-07-26 |
| Project | DoorAlarmv3.Avalonia |
| Mức độ | MEDIUM — build sạch, chỉ lộ khi nhìn màn hình |
| Từ khoá | Avalonia, Styles, Selector, ControlTemplate, ContentPresenter, Foreground |

## Bối cảnh

Muốn ép màu chữ mặc định toàn app về token KZTEK nên thêm vào `AppStyles.axaml`:

```xml
<Style Selector="TextBlock">
  <Setter Property="Foreground" Value="{DynamicResource kz.brush.text}" />
</Style>
```

## Điều thực tế xảy ra

Mọi nút nền đậm (`KzButton` variant Primary — nền navy, chữ trắng) đột nhiên **chữ tối trên nền
tối**, gần như không đọc được: "Lưu", "Đóng" chỉ còn thấy mờ mờ.

Lý do: selector `TextBlock` **không chỉ bắt TextBlock trong View** — nó bắt cả `TextBlock` do
`ControlTemplate` sinh ra bên trong `ContentPresenter` của Button. Setter trong Style thắng giá trị
Foreground mà Button kế thừa xuống, nên chữ của nút bị đổi màu theo.

Cùng cơ chế đó cũng ảnh hưởng chữ trong ComboBox, DataGrid header, TabItem…

## Cách khắc phục

Không đặt selector trần cho control nguyên thuỷ. Thay bằng:

- Selector có **phạm vi**: `Border.section-header > TextBlock`, `TextBlock.on-navy`
- Hoặc đặt `Foreground` trực tiếp trên TextBlock của View / trong DataTemplate

```xml
<!-- ĐÚNG: có phạm vi -->
<Style Selector="Border.section-header > TextBlock">
  <Setter Property="Foreground" Value="{DynamicResource kz.brush.navy.900}" />
</Style>
```

## Nguyên tắc rút ra

1. Trong Avalonia, `Selector="X"` áp cho **mọi** instance của X, kể cả instance nằm trong template
   của control khác. Đây là khác biệt lớn so với cách nghĩ "style này chỉ cho TextBlock tôi viết ra".
2. Muốn đổi diện mạo mặc định của một control → sửa `ControlTheme` của nó, đừng dùng selector trần
   cho control nguyên thuỷ (TextBlock, Border, Path…) vì chúng là vật liệu xây dựng của mọi template.
3. Triệu chứng đặc trưng: **chỉ chữ trên nền màu đậm bị sai**, chữ trên nền sáng vẫn đúng → nghi ngay
   một Style toàn cục đang đè Foreground kế thừa.

## Liên quan

- [[avalonia-12-breaking-changes-rabbitmq7-migration]]
