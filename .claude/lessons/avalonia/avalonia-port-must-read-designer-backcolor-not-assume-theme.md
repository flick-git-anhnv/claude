---
category: avalonia
tags: [migration, winforms, parity, color, designer, kiosk]
severity: high
created: 2026-07-20
updated: 2026-07-20
project-origin: IPGS.Kiosk.Avalonia (migrate frmXxx → Avalonia)
---

# Port WinForms → Avalonia: PHẢI đọc màu từ .Designer.cs, KHÔNG tự áp theme thương hiệu

## Tình huống gặp phải

Wave migrate `frmCarVehicleResult`, `frmMotorVehicleResult`, `frmCarInforDetail`,
`frmMotorInforDetail`, `frmBikePaymentResult`, `frmMotoPaymentComplete`, `frmInvoice`
sang Avalonia. Agent trước áp **theme navy tối** (`Background="#251C53"`/`#1A1A2E`, chữ trắng,
thẻ `#2D2460`, textbox `#2A2A4A`) cho TẤT CẢ view — vì tưởng đó là brand KZTEK.

Thực tế TẤT CẢ form gốc là **White-theme**:
`BackColor = Color.White` hoặc `SystemColors.ButtonHighlight` (= White). Hậu quả:
- Sai visual parity toàn bộ màn hình.
- Một số text vẫn để `Foreground="White"` trên nền đã đúng là trắng → **chữ trắng trên nền trắng, vô hình**.

## Nguyên nhân & cách xử lý

- KHÔNG suy đoán theme từ brand guideline. Mỗi Form/UserControl PHẢI đọc `.Designer.cs`
  lấy đúng hex: `BackColor`, `ForeColor`, `FillColor`, `Font`, `Image`.
- Bảng màu gốc thường gặp ở kiosk này (ghi để tái dùng):
  - Nền form: `White`
  - lblTime: `Color.FromArgb(158,161,162)` = `#9EA1A2`
  - Value/label chữ: `#2A2F30` (42,47,48) hoặc `#251C53` (37,28,83)
  - Nút phụ (Back/Done): `FillColor = SystemColors.ControlLight` ≈ `#E3E3E3` + `ForeColor Black`
  - Nút Invoice: `#251C53` + White ; Nút CTA (Lookup/Confirm/Pay lookup): `#F05922` + White
  - Số tiền "còn lại": đỏ `#DA291C` (218,41,28)
- `SystemColors.ButtonHighlight` = White, `SystemColors.ControlLight` ≈ #E3E3E3 — tra đúng khi thấy tên SystemColors.

## KzKeyboard KHÔNG phải lúc nào cũng khớp control gốc

`SearchNumberControl` port `ucSearchNumber` — gốc là **dialpad SỐ tròn**
(`SiticoneCircleButton` 124×124 trắng, layout 3×3 + 0 giữa + Delete + nút Search bo tròn).
Tái dùng `KzKeyboard` (ParkingV8.UI) = bàn phím ký tự đầy đủ → sai hoàn toàn giao diện.
→ Build lại control riêng khớp gốc thay vì ép dùng thư viện chung. Trong Avalonia,
để bắt click mọi nút số không phụ thuộc thứ tự dựng visual tree:
`AddHandler(Button.ClickEvent, handler, RoutingStrategies.Bubble)` ở root UserControl,
dispatch theo `Tag`/tên nút (KHÔNG gọi `GetVisualDescendants` trong constructor — visual tree chưa dựng).

## Áp dụng lại

- Trước khi viết axaml cho 1 màn hình port: mở `.Designer.cs` tương ứng, chép đúng hex màu.
- Sau khi đổi nền: rà lại mọi `Foreground="White"` xem còn nằm trên nền trắng không.
- Bug build hay gặp ở port dở: thiếu `.axaml.cs` (→ AVLN2000 "Unable to find type"),
  và `{x:Static BoolConverters.False}` KHÔNG tồn tại (chỉ có And/Or/Not).
