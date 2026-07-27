---
category: avalonia
tags: [onscreen-keyboard, scrollviewer, touch, kiosk, layout]
severity: high
created: 2026-07-26
updated: 2026-07-26
project-origin: iPGSv4 KIOSK HORIZONTAL (IPGS.Kiosk.Avalonia)
---

# Bàn phím ảo dạng lớp phủ làm ScrollViewer không co viewport → phần form dưới không bao giờ cuộn tới được

## Tình huống gặp phải

Màn "Cấu hình kết nối" của kiosk cảm ứng 1920×1080 (Avalonia 12.1). Form dài hơn màn hình nên
đặt trong `ScrollViewer`, kèm bàn phím ảo `KzKeyboard` chỉ hiện khi người dùng chạm vào ô nhập.

Bàn phím được đặt làm **lớp phủ đáy**:

```xml
<Grid RowDefinitions="Auto,*,Auto">
  <Border Grid.Row="0" ... />                    <!-- header -->
  <ScrollViewer Grid.Row="1"> ... </ScrollViewer><!-- form -->
  <Border Grid.Row="2"> ... </Border>            <!-- thanh Lưu/Huỷ -->

  <!-- SAI: phủ lên Row 1+2 -->
  <Border x:Name="KeyboardPanel" Grid.Row="1" Grid.RowSpan="2"
          VerticalAlignment="Bottom" IsVisible="False"> ... </Border>
</Grid>
```

## Triệu chứng / Lỗi

Không có exception. Người dùng báo: *"phần config bị bàn phím che mất, tôi đã cuộn hết cỡ"*.

- Bàn phím che ~45% dưới màn hình.
- Cuộn `ScrollViewer` đến cuối vẫn còn trường bị bàn phím che — **không có cách nào nhập nó**.
- Thanh nút Lưu / Quay lại cũng bị che hoàn toàn → không lưu được cấu hình.

## Nguyên nhân gốc rễ (Root Cause)

Lớp phủ nằm ĐÈ LÊN chứ không CHIẾM CHỖ. `ScrollViewer` vẫn được cấp nguyên chiều cao của Row 1,
nên `Viewport` của nó không đổi. `ScrollViewer` chỉ cuộn được tối đa `Extent - Viewport`; vì
`Viewport` vẫn tính theo chiều cao đầy đủ (kể cả phần bị bàn phím che), phần nội dung nằm dưới
bàn phím **luôn nằm trong viewport theo tính toán của ScrollViewer** → nó coi như đã hiển thị và
không cuộn thêm. Vùng đó vĩnh viễn không thể đưa lên chỗ nhìn thấy.

Đây là khác biệt căn bản giữa "che" (overlay) và "chiếm chỗ" (layout): chỉ cái thứ hai làm
`Viewport` co lại và tăng `ScrollableHeight` tương ứng.

## Giải pháp

Cho bàn phím **một hàng riêng** trong Grid, không dùng `RowSpan` để phủ:

```xml
<Grid RowDefinitions="Auto,*,Auto,Auto">
  <Border      Grid.Row="0"> ... </Border>          <!-- header -->
  <ScrollViewer Grid.Row="1"> ... </ScrollViewer>   <!-- form: `*` tự co khi bàn phím hiện -->
  <Border      Grid.Row="2"> ... </Border>          <!-- thanh nút: LUÔN thấy -->
  <Border x:Name="KeyboardPanel" Grid.Row="3" IsVisible="False"> ... </Border>
</Grid>
```

Kèm auto-cuộn ô đang nhập vào tầm nhìn — nhưng phải **post sang lượt layout sau**:

```csharp
item.InputFocused += (_, tb) =>
{
    KbMain.TargetTextBox = tb;
    KeyboardPanel.IsVisible = true;

    // Gọi BringIntoView() ngay lập tức sẽ dùng chiều cao viewport CŨ (chưa co) → cuộn sai chỗ.
    Dispatcher.UIThread.Post(() => tb.BringIntoView(), DispatcherPriority.Background);
};
```

1. Đổi `RowDefinitions` thêm 1 hàng `Auto` ở cuối.
2. Chuyển bàn phím sang hàng đó, bỏ `Grid.RowSpan` và `VerticalAlignment="Bottom"`.
3. Đặt thanh nút hành động ở hàng TRƯỚC bàn phím để nó không bị che.
4. `BringIntoView()` qua `Dispatcher.UIThread.Post(..., DispatcherPriority.Background)`.
5. Giảm chiều cao bàn phím vừa đủ ngưỡng chạm (~320px cho phím ~52px) — mỗi px bàn phím lấy là
   1 px form mất, khác hẳn khi nó chỉ là lớp phủ.

## Áp dụng lại (How to reuse)

- Khi user nói *"đã cuộn hết cỡ mà vẫn bị che"* → gần như chắc chắn có phần tử phủ lên
  `ScrollViewer` thay vì chiếm hàng/cột riêng. Kiểm tra `Grid.RowSpan` / `VerticalAlignment="Bottom"`
  / `Canvas` / `Panel` chồng lớp.
- Nguyên tắc: **cái gì che mất nội dung cuộn thì phải nằm NGOÀI ScrollViewer và CHIẾM CHỖ trong
  layout** — bàn phím ảo, thanh công cụ dưới, banner thông báo đều vậy.
- Thanh nút xác nhận/huỷ luôn đặt ở hàng riêng phía trên bàn phím, không bao giờ trong vùng cuộn.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ `BringIntoView()` gọi đồng bộ ngay sau khi `IsVisible = true` sẽ tính theo viewport cũ →
  phải `Post` sang lượt sau.
- ⚠️ Avalonia tự focus ô nhập ĐẦU TIÊN khi window mở → bàn phím bật sẵn dù chưa ai chạm. Chặn bằng
  cờ "đã có chạm thật", bật ở `PointerPressedEvent` với `RoutingStrategies.Tunnel` (Tunnel để cờ
  bật TRƯỚC khi TextBox nhận focus):
  ```csharp
  AddHandler(PointerPressedEvent, (_, _) => _userInteracted = true, RoutingStrategies.Tunnel);
  ```
- ⚠️ Trên kiosk cảm ứng, `ScrollViewer` trơn KHÔNG cuộn được bằng ngón tay (không chuột, không bánh
  xe). Cần attached property kéo-để-cuộn (dự án này: `controls:TouchDragScroll.IsEnabled="True"`).

## Tham chiếu

- Xem thêm [[avalonia-synthetic-mouse-click-ignored-use-uiautomation]] — cách kiểm chứng UI Avalonia
  khi chuột tổng hợp bị bỏ qua.
