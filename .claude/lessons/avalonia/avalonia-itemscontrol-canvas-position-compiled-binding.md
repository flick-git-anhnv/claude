---
category: avalonia
tags: [itemscontrol, canvas, compiled-binding, avln2000, datatemplate, positioning]
severity: medium
created: 2026-07-26
updated: 2026-07-26
project-origin: iPGSv4 (branch PAYMENT_KIOSK_HORIZONTAL_PARKING8) — migrate kiosk màn ngang sang Avalonia
---

# ItemsControl + Canvas: không định vị được item bằng Canvas.Left/Top khi bật compiled bindings

## Tình huống gặp phải

Port màn bản đồ bãi xe (`frmCarLocation` WinForms → Avalonia). Cần vẽ N điểm đánh dấu
(vị trí kiosk, thang máy, thang cuốn) lên ảnh bản đồ, mỗi điểm ở toạ độ X/Y riêng do
ViewModel tính sẵn. Dùng `ItemsControl` với `ItemsPanel` là `Canvas`, mỗi item là 1 `Button`
chứa icon.

Project bật `<AvaloniaUseCompiledBindingsByDefault>true</AvaloniaUseCompiledBindingsByDefault>`
và View khai báo `x:DataType="vm:CarLocationViewModel"`.

## Triệu chứng / Lỗi

Cách 1 — đặt `Canvas.Left/Top` ngay trên gốc của `ItemTemplate`: **build sạch nhưng mọi item
chồng lên nhau tại (0,0)**.

Cách 2 — đặt qua `Style` nhắm vào container:

```xml
<ItemsControl.Styles>
  <Style Selector="ItemsControl > ContentPresenter">
    <Setter Property="Canvas.Left" Value="{Binding X}" />
    <Setter Property="Canvas.Top"  Value="{Binding Y}" />
  </Style>
</ItemsControl.Styles>
```

```
Avalonia error AVLN2000: Unable to resolve property or method of name 'X'
on type 'IPGS.Kiosk.Avalonia.ViewModels.Car.CarLocationViewModel'.
```

## Nguyên nhân gốc rễ (Root Cause)

Hai nguyên nhân riêng biệt chồng lên nhau:

1. **Phần tử con thật sự của Canvas là `ContentPresenter` (container), không phải gốc của
   `ItemTemplate`.** `Canvas.Left/Top` là attached property — chỉ có tác dụng khi đặt trên
   *con trực tiếp* của Canvas. Đặt trong template là đặt lên cháu → Canvas bỏ qua.

2. **Compiled binding trong `Style` resolve theo `x:DataType` của file XAML chứa nó**, tức
   `CarLocationViewModel`, chứ KHÔNG phải kiểu của item (`MapMarker`). `MapMarker.X` tồn tại
   nhưng `CarLocationViewModel.X` thì không → AVLN2000 lúc biên dịch XAML.

Nói cách khác: chỗ *có thể* đặt Canvas.Left/Top thì binding sai kiểu; chỗ binding *đúng* kiểu
thì Canvas.Left/Top vô tác dụng.

## Giải pháp

Bỏ Canvas, dùng `Grid` làm `ItemsPanel` và định vị bằng `Margin` — binding nằm gọn trong
`ItemTemplate` nên đúng DataType của item.

Thêm vào model một property trả thẳng `Thickness`:

```csharp
using Avalonia;

public sealed record MapMarker(MapMarkerKind Kind, string Id, double X, double Y, bool IsClickable)
{
    // Margin = (left, top, 0, 0) → tương đương Canvas.Left/Top
    public Thickness Offset => new(X, Y, 0, 0);
}
```

```xml
<ItemsControl ItemsSource="{Binding CrossFloorMarkers}"
              Width="{Binding MapDisplayWidth}"
              Height="{Binding MapDisplayHeight}">
  <!-- Grid: mọi item chồng cùng 1 ô, tự định vị bằng Margin -->
  <ItemsControl.ItemsPanel>
    <ItemsPanelTemplate>
      <Grid />
    </ItemsPanelTemplate>
  </ItemsControl.ItemsPanel>

  <ItemsControl.ItemTemplate>
    <DataTemplate DataType="{x:Type models:MapMarker}">
      <Button HorizontalAlignment="Left"
              VerticalAlignment="Top"
              Margin="{Binding Offset}"
              Command="{Binding $parent[ItemsControl].((vm:CarLocationViewModel)DataContext).MarkerTappedCommand}"
              CommandParameter="{Binding}">
        <Image Source="{Binding IconSource}"
               Width="{Binding IconWidth}" Height="{Binding IconHeight}" />
      </Button>
    </DataTemplate>
  </ItemsControl.ItemTemplate>
</ItemsControl>
```

1. Thêm property `Thickness Offset => new(X, Y, 0, 0)` vào model item.
2. Đổi `ItemsPanelTemplate` từ `Canvas` sang `Grid`.
3. Trong `ItemTemplate`: `HorizontalAlignment="Left"` + `VerticalAlignment="Top"` +
   `Margin="{Binding Offset}"` (thiếu 2 alignment thì item sẽ giãn full ô, Margin thành padding).
4. Gọi command của ViewModel cha bằng `$parent[ItemsControl].((vm:XxxViewModel)DataContext).YyyCommand`
   — ép kiểu tường minh vì compiled binding không tự suy ra DataContext của cha.

## Áp dụng lại (How to reuse)

- Khi cần **định vị tuyệt đối từng item trong ItemsControl** → dùng ngay Grid + Margin,
  đừng mất thời gian với Canvas + Style.
- Khi thấy `AVLN2000: Unable to resolve property ... on type <ViewModel>` mà property đó rõ ràng
  có trên **item model** → binding đang bị resolve theo `x:DataType` của View. Chuyển binding vào
  trong `DataTemplate` có `DataType` đúng, hoặc ép kiểu tường minh.
- Cần gọi command của VM cha từ trong item template → `$parent[ItemsControl].((vm:T)DataContext).Cmd`.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Thiếu `HorizontalAlignment="Left"`/`VerticalAlignment="Top"` → item bị stretch full ô Grid,
  `Margin` biến thành khoảng đệm chứ không phải toạ độ. Đây là lỗi im lặng, không báo gì.
- ⚠️ Cách đặt `Canvas.Left/Top` trong `ItemTemplate` **build sạch, không warning** — rất dễ tưởng
  đã đúng cho tới khi chạy thấy mọi item nằm đè nhau ở góc trên-trái.
- ⚠️ `ItemContainerTheme` cũng đặt được attached property lên container, nhưng vẫn vướng đúng vấn
  đề compiled-binding resolve sai kiểu → không giải quyết được gốc.
- ⚠️ Grid + Margin không hỗ trợ toạ độ ÂM giống Canvas (Margin âm vẫn chạy nhưng dễ bị clip bởi
  `ClipToBounds` của cha). Nếu cần toạ độ âm thật, cân nhắc bù offset dương cho cả tập điểm.

## Tham chiếu

- Avalonia docs — Attached properties & ItemsControl containers
- Project: iPGSv4, branch `PAYMENT_KIOSK_HORIZONTAL_PARKING8`
- File: `IPGS.Kiosk.Avalonia/Models/MapMarker.cs`, `Views/Car/CarLocationView.axaml`
- Liên quan: `avalonia-canvas-direct-child-horizontalalignment-ignored.md` (cùng họ vấn đề
  "Canvas bỏ qua thuộc tính bố cục của con không trực tiếp")
