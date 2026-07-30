---
title: Dùng chung 1 handler cho 2 event khác kiểu delegate làm mất Click âm thầm
category: avalonia
tags: [event-binding, click, routedevent, xaml-compile-error, kzbutton]
created: 2026-07-30
---

## Vấn đề

`IdentitySearchView.axaml` bind cùng 1 method `OnBackRequested(object?, System.EventArgs)` cho
CẢ HAI event:
- `KioskHeaderBar.BackRequested="OnBackRequested"` — event kiểu `EventHandler` (System.EventArgs) → OK
- `KzButton.Click="OnBackRequested"` — event kiểu `EventHandler<RoutedEventArgs>` → SAI kiểu

Build lỗi AVLN3000: "Unable to find suitable setter or adder for property Click ...
available setter parameter lists are: System.EventHandler`1<Avalonia.Interactivity.RoutedEventArgs>".

## Nguyên nhân

XAML compiler tìm overload khớp CHÍNH XÁC kiểu delegate của property đang gán (`Click` cần
`EventHandler<RoutedEventArgs>`). Vì trong code-behind chỉ có 1 overload nhận `System.EventArgs`,
nó không tự nới lỏng/tự cast — lỗi biên dịch, và nút Back mất luôn wiring Click.

Dễ xảy ra khi: 1 View vừa có `shared:KioskHeaderBar` (dùng `EventHandler` cho `BackRequested`)
vừa có `kz:KzButton` cùng chức năng Back ở khu vực footer — cả hai đặt tên method trùng do
copy-paste từ View khác, nhưng quên rằng `Click` của Avalonia control luôn là
`EventHandler<RoutedEventArgs>`, khác `BackRequested` custom event.

## Cách fix

Tạo thêm 1 handler wrapper riêng cho `Click` với đúng chữ ký `RoutedEventArgs`, gọi lại logic chung:

```csharp
private void OnBackRequested(object? sender, System.EventArgs e) =>
    _nav.NavigateTo(new SelectionView(_nav, _state));

private void OnBackButtonClick(object? sender, RoutedEventArgs e) =>
    OnBackRequested(sender, System.EventArgs.Empty);
```

Trong `.axaml`: `Click="OnBackButtonClick"` thay vì `Click="OnBackRequested"`.

## Cách phát hiện sớm

- Đây LÀ lỗi build-time (AVLN3000), không phải runtime silent — nhưng dễ bị đọc lướt qua nếu
  Error List không được xem trước khi báo "đã sửa xong".
- Khi review PR có View mới dùng chung tên handler cho `BackRequested` (custom event,
  `EventHandler`) và `Click`/`Tapped` (Avalonia control, `EventHandler<RoutedEventArgs>`) →
  kiểm tra kỹ 2 chữ ký khác nhau.
- Grep nhanh để tìm case tương tự trong project: `Click="OnBackRequested"` hoặc tổng quát hơn
  tìm các method chỉ có 1 overload `System.EventArgs` nhưng được XAML gán cho property `Click`.

## Liên quan

[[avalonia-back-button-only-icon-wired-not-label]] — cùng chủ đề nút Back bị mất wiring nhưng do
nguyên nhân khác (chỉ wire icon, không wire label).
