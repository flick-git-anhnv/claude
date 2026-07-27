# `DatePicker.SelectedDate` là `DateTimeOffset?` — bind vào `DateTime` làm hỏng cả màn hình

| Mục | Nội dung |
|---|---|
| Ngày | 2026-07-27 |
| Project | DoorAlarmv3.Avalonia (màn Báo cáo) |
| Mức độ | HIGH — màn hình không dùng được, nhưng build sạch |
| Từ khoá | Avalonia, DatePicker, SelectedDate, DateTimeOffset, InvalidCastException, binding |

## Bối cảnh

Màn Báo cáo có 2 ô chọn ngày. ViewModel giữ `DateTime StartTime` / `DateTime EndTime` (kiểu tự nhiên
cho truy vấn SQL), View bind thẳng:

```xml
<DatePicker SelectedDate="{Binding StartTime, Mode=TwoWay}" />
```

## Điều thực tế xảy ra

Build sạch, không warning. Nhưng khi mở màn hình, **ngay tại vị trí ô chọn ngày** hiện dòng chữ đỏ:

```
System.InvalidCastException: Could not convert '27/07/2026 00:00:00' (System.DateTime)
to 'System.Nullable`1[System.DateTimeOffset]'.
```

Ô ngày trống, không chọn được ngày nào ⇒ **không tìm kiếm được gì, cả màn Báo cáo vô dụng**.
Không có exception nào nổi lên tầng ứng dụng, không có gì trong log.

## Nguyên nhân

`DatePicker.SelectedDate` của Avalonia có kiểu **`DateTimeOffset?`**, không phải `DateTime`.
Binding engine không tự chuyển `DateTime` → `DateTimeOffset?` và báo lỗi ngay trên control.

## Cách khắc phục

Thêm property quy đổi ở ViewModel, giữ nguyên `DateTime` cho phần nghiệp vụ:

```csharp
public DateTimeOffset? StartDate
{
    get => new DateTimeOffset(StartTime);
    set { if (value.HasValue) StartTime = value.Value.Date; }          // 00:00:00
}

public DateTimeOffset? EndDate
{
    get => new DateTimeOffset(EndTime);
    set { if (value.HasValue) EndTime = value.Value.Date.AddDays(1).AddSeconds(-1); }  // 23:59:59
}

partial void OnStartTimeChanged(DateTime value) => OnPropertyChanged(nameof(StartDate));
partial void OnEndTimeChanged(DateTime value) => OnPropertyChanged(nameof(EndDate));
```

## Nguyên tắc rút ra

1. **Lỗi binding trong Avalonia hiện TRÊN CONTROL, không ném exception.** Build sạch + self-test
   dựng được cửa sổ vẫn không chứng minh màn hình dùng được — phải **mở và nhìn** từng màn.
2. Nhóm control hay lệch kiểu: `DatePicker`/`TimePicker` (`DateTimeOffset?`/`TimeSpan?`),
   `CalendarDatePicker` (`DateTime?`) — ba control ngày giờ, ba kiểu khác nhau.
3. Đừng đổi kiểu nghiệp vụ theo control: thêm property quy đổi ở ViewModel, giữ `DateTime` cho SQL.

## Liên quan

- [[avalonia-12-breaking-changes-rabbitmq7-migration]]
- [[avalonia-global-textblock-style-breaks-button-content]]
