---
category: csharp-winforms
tags: [kztek-control8, kzbutton, guna2button, focus-events, custom-color]
severity: medium
created: 2026-07-08
updated: 2026-07-08
project-origin: parking-v8-app (IParkingv8 — tính năng env-prerequisite-check)
---

# KzButton tự động reset FillColor/BorderColor/ForeColor khi Focus thay đổi

## Tình huống gặp phải

> Đang thiết kế dialog cảnh báo `FrmEnvironmentCheck` (WinForms), cần 1 nút "Đóng ứng dụng" màu cam thương hiệu `#F05922` để phân biệt với nút "Tiếp tục" mặc định, dùng control `KzButton` (`Kztek.Control8.Controls`, kế thừa `Guna2Button`).

## Triệu chứng / Lỗi

Set `btn.FillColor = Color.FromArgb(0xF0, 0x59, 0x22)` ngay sau khi khởi tạo (hoặc trong Designer) — màu hiển thị đúng lúc đầu, nhưng **tự động đổi về màu mặc định** ngay khi control mất focus hoặc được focus (VD: khi dialog mở lên và nút kia đang là `AcceptButton`/focus mặc định).

## Nguyên nhân gốc rễ (Root Cause)

`KzButton` (`Kztek.Control8/1.GeneralControls/2.Buttons/KzButton.cs`) tự đăng ký `GotFocus`/`LostFocus` handler ngay trong constructor:

```csharp
this.GotFocus += KzButton_GotFocus;   // set FillColor/BorderColor/ForeColor = BUTTON_FOCUS_*
this.LostFocus += KzButton_LostFocus; // set FillColor/BorderColor/ForeColor = BUTTON_NORMAL_*
```

Hai handler này **ghi đè vô điều kiện** `FillColor`/`BorderColor`/`ForeColor` về giá trị lấy từ `ButtonColorManagement` mỗi khi focus thay đổi — không quan tâm việc code bên ngoài đã set màu tùy chỉnh trước đó. Vì các handler này là `private` method reference được subscribe sẵn trong constructor, code bên ngoài KHÔNG thể unsubscribe chúng.

## Giải pháp

Subscribe thêm `GotFocus`/`LostFocus` của CHÍNH mình **sau khi** control đã được tạo — vì C# event invocation chạy theo đúng thứ tự subscribe, handler của `KzButton` chạy trước (reset về màu chuẩn), handler mới thêm chạy sau (ghi đè lại màu mong muốn):

```csharp
var btnClose = new KzButton { Text = "Đóng ứng dụng", Width = 160, Height = 38 };
Color closeColor = Color.FromArgb(0xF0, 0x59, 0x22); // #F05922
void ApplyCloseColor(object? s, EventArgs e) => btnClose.FillColor = closeColor;
ApplyCloseColor(null, EventArgs.Empty);           // set màu ban đầu
btnClose.GotFocus  += ApplyCloseColor;             // ghi đè lại sau khi KzButton tự đổi màu focus
btnClose.LostFocus += ApplyCloseColor;             // ghi đè lại sau khi KzButton tự đổi màu về normal
```

1. Set màu mong muốn ngay sau khởi tạo (cho lần render đầu tiên trước khi có sự kiện focus nào).
2. Subscribe thêm `GotFocus` và `LostFocus` của CHÍNH mình SAU khi đối tượng `KzButton` đã tồn tại (không phải override trong class con, trừ khi thực sự cần class con riêng).
3. Handler mới chỉ cần set lại đúng field màu bị `KzButton` ghi đè — không cần gọi `base` hay hủy đăng ký gì thêm.

## Áp dụng lại (How to reuse)

- Khi thấy dùng `KzButton` (hoặc bất kỳ control nào kế thừa `Guna2Button` có custom `GotFocus`/`LostFocus` trong `Kztek.Control8`) và cần custom màu cố định khác với `ButtonColorManagement` mặc định → PHẢI áp dụng pattern subscribe-sau-để-ghi-đè ở trên, KHÔNG chỉ set property 1 lần rồi thôi.
- Kiểm tra `ButtonColorManagement` (namespace `iParkingv8.Ultility`) trước — nếu có thể, cân nhắc thêm 1 bộ màu mới vào đó thay vì workaround per-instance, để nhất quán toàn hệ thống.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Set màu trong Designer.cs (`InitializeComponent`) KHÔNG đủ — vẫn bị `LostFocus` ghi đè ngay khi control khác nhận focus lần đầu (VD: `AcceptButton` tự nhận focus khi `ShowDialog()`).
- ⚠️ Áp dụng tương tự cho `ForeColor`/`BorderColor` nếu cũng bị custom — cả 3 property đều bị 2 handler này quản lý.
- ⚠️ Không set màu qua Designer property window rồi assume nó "cố định" — bất kỳ WinForms Guna2Button-based custom control nào có "hover/focus effect" đều có nguy cơ tương tự, luôn đọc source control trước khi custom màu.

## Tham chiếu

- File gốc: `Kztek.Control8/1.GeneralControls/2.Buttons/KzButton.cs`
- Project liên quan: `parking-v8-app` — `IParkingv8/Forms/FrmEnvironmentCheck.cs` (Junior Developer, task EPC-T03, plan `.claude/plans/PLAN-env-prerequisite-check-2026-07-08.md`)
