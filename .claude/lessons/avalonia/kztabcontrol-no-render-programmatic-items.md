---
category: avalonia
tags: [KzTabControl, TabControl, items, rendering, programmatic, ControlTheme, BasedOn]
severity: high
created: 2026-06-24
updated: 2026-06-25
project-origin: iPGSv4 - ApplicationConfig
---

# KzTabControl không render items — dùng TabControl chuẩn hoặc đăng ký ControlTheme

## Tình huống gặp phải

Đang migrate ApplicationConfig (WinForms → Avalonia). Cần hiển thị 3 tab: SQL, LPR, Parking. Dùng `KzTabControl` (kế thừa từ `TabControl` của Avalonia, không override gì).

## Triệu chứng / Lỗi

`KzTabControl` render ra một khung trắng hoàn toàn — không có tab headers, không có content — dù:
- Đã khai báo `<TabItem>` trong AXAML
- Đã thêm items qua `tabs.Items.Add()`  
- Debug log xác nhận `tabs.Items.Count == 3`, `Items[0].GetType() == TabItem`
- Không có exception nào trong OnLoaded

## Nguyên nhân gốc rễ (Root Cause)

`KzTabControl` kế thừa từ `TabControl` nhưng Avalonia's control template lookup không apply FluentTheme's TabControl template cho subclass theo cách mong đợi, hoặc có conflict giữa style selectors dạng `kz|KzTabControl TabItem` và control template mặc định.

Điều này khiến toàn bộ phần visual của TabControl (tab strip + content panel) không render, cho ra hình chữ nhật trắng.

## Giải pháp

Dùng `TabControl` chuẩn của Avalonia thay vì `KzTabControl`:

```xml
<!-- AXAML: khai báo tabs trong AXAML (không phải programmatic) -->
<TabControl Grid.Row="1" x:Name="PART_Tabs" Margin="0">
  <TabItem Header="Tab 1" />
  <TabItem Header="Tab 2" />
  <TabItem Header="Tab 3" />
</TabControl>
```

```csharp
// Code-behind: set Content via Items index (FindControl không tìm được TabItem bên trong ItemsControl)
var tabs = this.FindControl<TabControl>("PART_Tabs")!;
// ...tạo views...
((TabItem)tabs.Items[0]!).Content = _view1;
((TabItem)tabs.Items[1]!).Content = _view2;
((TabItem)tabs.Items[2]!).Content = _view3;
```

## Áp dụng lại (How to reuse)

- Khi cần TabControl trong project Avalonia → dùng `<TabControl>` chuẩn, KHÔNG dùng `<kz:KzTabControl>`
- Khi cần set Content từ code-behind → truy cập qua `tabs.Items[i]` (cast sang `TabItem`), KHÔNG dùng `FindControl<TabItem>("tên")` vì FindControl không tìm được items bên trong ItemsControl
- Khi cần khai báo tabs → khai báo trong AXAML (không phải `tabs.Items.Add()` thuần) để đảm bảo render

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ `KzTabControl` không báo lỗi gì — chỉ render trắng. Debug log sẽ cho thấy Items.Count > 0 nhưng UI vẫn trắng.
- ⚠️ `FindControl<TabItem>("PART_Tab1")` LUÔN trả về null cho TabItems nằm trong ItemsControl — phải dùng `tabs.Items[i]`
- ⚠️ `tabs.Items.Add(new TabItem {...})` sẽ thêm item vào collection nhưng KHÔNG render khi dùng KzTabControl

## Giải pháp thay thế — Fix KzTabControl bằng ControlTheme (update 2026-06-25)

Thay vì workaround (dùng `TabControl` chuẩn), có thể fix trực tiếp `KzTabControl` bằng cách đăng ký `ControlTheme` với `BasedOn` FluentTheme TabControl:

```xml
<!-- Trong Default.axaml (được load qua UseKztekTheme()) -->
<ControlTheme x:Key="{x:Type kz:KzTabControl}"
              TargetType="kz:KzTabControl"
              BasedOn="{StaticResource {x:Type TabControl}}">
  <!-- Style overrides cho KZTEK brand — không cần copy toàn bộ template -->
  <Style Selector="^ /template/ TabItem:selected">
    <Setter Property="BorderBrush" Value="{StaticResource kz.brush.orange.500}" />
  </Style>
</ControlTheme>
```

**Tại sao `BasedOn` hoạt động:** Avalonia's `ControlTheme` với `BasedOn="{StaticResource {x:Type TabControl}}"` kế thừa toàn bộ visual template của FluentTheme TabControl, rồi override thêm brand styles. Không cần copy template — chỉ thêm style selectors cho phần cần thay đổi.

**Khi nào nên dùng cách này:** Khi đang dùng `KzTabControl` trong nhiều nơi và muốn nhất quán brand style. Nếu chỉ dùng ở 1–2 chỗ, workaround `<TabControl>` chuẩn vẫn OK.

## Tham chiếu

- Project liên quan: iPGSv4 / ApplicationConfig, KztekComponentAvalonia
- Workaround verified: 2026-06-24 với Avalonia 11.2.7
- ControlTheme fix implemented: 2026-06-25 (PLAN-fix-kztek-components-avalonia step 1E.2–1E.3)
