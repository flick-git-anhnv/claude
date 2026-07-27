---
category: avalonia
tags: [canvas, horizontalalignment, layout, centering, StackPanel, Grid]
severity: high
created: 2026-07-22
updated: 2026-07-22
project-origin: iPGSv4 (KIOSK VERTICAL — LocationAndPayment)
---

# Canvas bỏ qua HorizontalAlignment/VerticalAlignment của con trực tiếp — nội dung "Width=1080 + Center" vẫn lệch trái

## Tình huống gặp phải

Đang fix bug UI màn hình `CarInforDetailView`/`MotorInforDetailView` (Avalonia, port từ WinForms `frmCarInforDetail`/`frmMotorInforDetail`). User báo: dòng cảnh báo "VUI LÒNG KIỂM TRA LẠI THÔNG TIN..." và khối "Biển số xe/Tầng/Cột" bị lệch trái thay vì căn giữa theo canvas 1080px, dù XAML đã ghi rõ `Width="1080" HorizontalAlignment="Center"`.

## Triệu chứng / Lỗi

```xml
<Canvas Width="1080" Height="1920">
  <StackPanel Canvas.Left="0" Canvas.Top="1141" Width="1080"
              Orientation="Horizontal" HorizontalAlignment="Center">
    <Image .../>
    <TextBlock Text="..."/>
  </StackPanel>

  <Grid Canvas.Left="0" Canvas.Top="1200" Width="1080"
        ColumnDefinitions="Auto,30,Auto" HorizontalAlignment="Center">
    ...
  </Grid>
</Canvas>
```
Kết quả render: cả `StackPanel` lẫn `Grid` đều dồn về cạnh TRÁI của canvas, dù đã set `Width="1080"` (=đúng chiều rộng canvas) và `HorizontalAlignment="Center"`. Bug lặp lại 2 lần trong cùng session vì fix vòng 1 chỉ sửa `StackPanel` cảnh báo, quên rằng `Grid` bên dưới (khối biển số/tầng/cột) bị **CÙNG MỘT NGUYÊN NHÂN GỐC**.

## Nguyên nhân gốc rễ (Root Cause)

`Canvas` trong Avalonia (giống WPF) **hoàn toàn bỏ qua** `HorizontalAlignment`/`VerticalAlignment` của các con **trực tiếp**. Cơ chế Arrange của Canvas luôn gọi:
```
child.Arrange(new Rect(Canvas.Left, Canvas.Top, child.DesiredSize.Width, child.DesiredSize.Height))
```
— tức là Arrange rect LUÔN khít với `DesiredSize` của con (không phải khoảng trống rộng hơn), nên thuộc tính Alignment (vốn chỉ có tác dụng khi ArrangeSize > DesiredSize, để control tự định vị bên trong khoảng dư) **không bao giờ có cơ hội phát huy** khi cha trực tiếp là `Canvas`.

Việc set `Width="1080"` trên chính `StackPanel`/`Grid` đó KHÔNG giúp gì — nó chỉ ép `DesiredSize.Width = 1080`, khiến Arrange rect rộng 1080px, nhưng nội dung bên trong (StackPanel Horizontal auto-size theo children, hoặc Grid với `ColumnDefinitions="Auto,..."`) vẫn tự xếp từ mép trái (x=0) của chính nó — không có cơ chế nào dịch chuyển nội dung sang giữa 1080px đó, vì `HorizontalAlignment="Center"` đặt trên chính phần tử này bị Canvas bỏ qua hoàn toàn.

## Giải pháp

Bọc thêm 1 lớp `Grid` (hoặc bất kỳ Panel không phải `Canvas`) làm cha trung gian: lớp NGOÀI là con trực tiếp của `Canvas` (dùng `Canvas.Left/Top` + `Width` cố định để xác định "khung căn giữa"), lớp TRONG mới đặt `HorizontalAlignment="Center"` — lúc này alignment có hiệu lực thật vì cha của nó (Grid ngoài) tôn trọng Alignment khi arrange con.

```xml
<!-- SAI: StackPanel/Grid là con TRỰC TIẾP của Canvas -->
<StackPanel Canvas.Left="0" Canvas.Top="1141" Width="1080"
            Orientation="Horizontal" HorizontalAlignment="Center">
  ...
</StackPanel>

<!-- ĐÚNG: bọc thêm 1 Grid trung gian -->
<Grid Canvas.Left="0" Canvas.Top="1141" Width="1080">
  <Grid HorizontalAlignment="Center" ColumnDefinitions="47,10,Auto">
    <Image Grid.Column="0" .../>
    <TextBlock Grid.Column="2" .../>
  </Grid>
</Grid>
```

1. Xác định phần tử đang bị lệch có phải **con trực tiếp của `Canvas`** không (kiểm tra bằng cách xem có `Canvas.Left`/`Canvas.Top` gắn trực tiếp trên nó).
2. Nếu có và nó cũng đang set `HorizontalAlignment`/`VerticalAlignment` để tự căn giữa/canh phải bên trong 1 `Width` cố định → đó chính là bug.
3. Bọc thêm 1 `Grid` cha (giữ nguyên `Canvas.Left/Top/Width`), chuyển toàn bộ nội dung + alignment vào `Grid` con bên trong.

## Áp dụng lại (How to reuse)

- Khi thấy XAML có pattern `Canvas.Left="0" Width="<full-canvas-width>" HorizontalAlignment="Center"` đặt trực tiếp trên con của `<Canvas>` → **nghi ngờ ngay**, đây gần như luôn là bug (alignment vô tác dụng).
- Trước khi fix 1 phần tử bị lệch trong 1 `Canvas` layout lớn, **grep toàn bộ file `.axaml`** tìm các phần tử khác cũng là con trực tiếp Canvas + có `HorizontalAlignment="Center"` — khả năng cao chúng CÙNG mắc lỗi này (xem case thực tế: sửa xong dòng cảnh báo, quên khối biển số/tầng/cột ngay bên dưới cùng file, user phải báo lại).
- Muốn ẩn/hiện 1 phần tử con (VD icon blink) mà KHÔNG muốn phần tử khác dịch chuyển vị trí → dùng `ColumnDefinitions` với **pixel cố định** (không phải `Auto`) cho cột chứa phần tử ẩn/hiện đó, để cột luôn giữ nguyên bề rộng bất kể `IsVisible` của nội dung bên trong.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ `IsVisible="False"` (Avalonia) làm control co về kích thước 0 trong layout (giống WPF `Visibility.Collapsed`), KHÔNG giống `Opacity=0` (vẫn giữ nguyên chỗ). Nếu muốn ẩn nhưng giữ layout, dùng `Opacity` binding (cần converter bool→double) thay vì `IsVisible`, HOẶC đặt trong cột/hàng có kích thước pixel cố định như trên.
- ⚠️ Đây là hành vi **giống hệt WPF** (`Canvas` cũng bỏ qua alignment của con trực tiếp) — dev quen WPF vẫn có thể mắc lỗi này vì hay quên, không phải riêng Avalonia.
- ⚠️ Root cause dễ bị chẩn đoán sai thành "do IsVisible toggle gây reflow" — thực ra là 2 lỗi độc lập cộng dồn: (1) Canvas bỏ qua alignment khiến toàn khối lệch trái ngay từ đầu, (2) StackPanel Horizontal auto-size khiến khối co giãn theo icon ẩn/hiện. Fix cả 2 cùng lúc bằng 1 pattern (Grid lồng Grid + cột pixel cố định).

## Tham chiếu

- Liên quan: [avalonia-border-child-not-clipped-not-stretched.md](avalonia-border-child-not-clipped-not-stretched.md) (Panel khác cũng có gotcha alignment tương tự)
- Project liên quan: iPGSv4 — `IPGS.Kiosk.Avalonia\Views\Car\CarInforDetailView.axaml`, `IPGS.Kiosk.Avalonia\Views\Moto\MotorInforDetailView.axaml`
