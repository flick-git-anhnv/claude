---
category: avalonia
tags: [layout, clipping, fontsize, width, port-winforms, kiosk]
severity: high
created: 2026-07-27
updated: 2026-07-27
project-origin: iPGSv4 — IPGS.Kiosk.Avalonia (kiosk màn NGANG)
---

# Avalonia: kích thước cố định CẮT nội dung âm thầm — không warning, không exception

## Tình huống gặp phải

Port UI từ WinForms Designer sang Avalonia (kiosk 1920×1080). Cách port là dịch trực tiếp các
con số `Size`/`Location` trong `*.Designer.cs` thành `Width`/`Height`/`Margin` của AXAML.

Build 0 Error, app chạy, không exception nào. Nhưng khi chụp ảnh app THẬT thì phát hiện nội dung
bị cắt ở 2 chỗ khác nhau — cả hai đều do cùng một loại nguyên nhân.

## Triệu chứng / Lỗi

**Ca 1 — chữ bị cắt phần trên/dưới:**

```xaml
<TextBlock Height="32" FontSize="28" Text="{Binding CurrentTime}" />
```
Nhãn giờ "06:15 pm" hiện ra bị cắt mất phần trên và đuôi chữ. Xuất hiện ở **13 view** cùng lúc
vì cùng copy một khuôn.

**Ca 2 — cả một cột nội dung bị cắt mép phải:**

```xaml
<UserControl Width="975">
  <Grid ColumnDefinitions="472,30,483" Margin="49,0,49,0">
```
Cột phải (chứa 4 thẻ chọn phương thức thanh toán + nút "Quay lại") bị cắt mất ~108px:
2 trong 4 thẻ mất một phần, nút bị cắt. **Không có warning nào.**

## Nguyên nhân gốc rễ

**Ca 1:** `FontSize="28"` cần hộp dòng (line box) khoảng **38–40px** — gồm cả ascender và
descender. Ép `Height="32"` thì Avalonia vẽ text trong 32px và **clip phần thừa**, không tự
giảm cỡ chữ, không cảnh báo. WinForms không bị vì `Label` có `AutoSize`/anchor xử lý khác.

**Ca 2:** Cộng lại nội dung cần `49 + 472 + 30 + 483 + 49 = 1083px` nhưng root chỉ rộng `975`.
Avalonia clip phần vượt, im lặng.

Sai gốc là **đọc nhầm Designer**: con số `49` vốn là lề trái của một `Label` **BÊN TRONG** panel
phải (`lblChoosePaymetMethodTittle`), bị hiểu thành lề của cả control. Số thật trong Designer:

```
Size = new Size(975, 435)
panelPaymentInfo.Location   = (3, 2)    Size = (472, 420)   → mép phải 475
panelPaymentAction.Location = (480, 2)  Size = (483, 415)   → mép phải 963
```
→ khe giữa 2 panel là **5px** (480−475), lề trái **3px**. Tổng 963 ≤ 975. Vừa khít.

## Giải pháp

**Ca 1** — đổi `Height` → `MinHeight`. Giữ đúng dải cao đã dành cho hàng (nên vị trí thiết kế
gần như không đổi), nhưng cho phép cao thêm khi chữ cần:

```xaml
<TextBlock MinHeight="32" FontSize="28" Text="{Binding CurrentTime}" />
```

**Ca 2** — cộng lại toàn bộ theo Designer rồi sửa cho khớp:

```xaml
<Grid ColumnDefinitions="472,5,483" Margin="3,0,0,0">   <!-- 3+472+5+483 = 963 ≤ 975 -->
```

## Áp dụng lại (How to reuse)

- Khi đặt `Height` cố định cho `TextBlock` → **luôn kiểm tra `Height >= FontSize * 1.4`**.
  Không đạt thì dùng `MinHeight`, đừng dùng `Height`.
- Trước khi tin một layout có `Width`/`Height` cố định: **cộng tay** tổng
  `Margin.Left + các cột + các khe + Margin.Right` rồi so với `Width` của root. Lệch là bị clip.
- Khi dịch số từ WinForms Designer: đọc **`Location` của các control con**, đừng suy lề từ
  `Margin`/`Padding` của control lồng bên trong. `Location` cho khe và lề thật.
- **Chỉ đọc code không phát hiện được loại lỗi này.** Phải chạy app thật + chụp ảnh mới thấy.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ `Height` → `MinHeight` làm hàng cao thêm ~6–8px, đẩy nội dung phía dưới xuống tương ứng.
  Chấp nhận được (chữ bị cắt tệ hơn nhiều) nhưng phải biết là có dịch chuyển, đừng ngạc nhiên
  khi so ảnh trước/sau.
- ⚠️ Bị clip **không** sinh warning, **không** sinh exception, build vẫn 0 Error. Đừng coi
  "build sạch" là bằng chứng layout đúng.
- ⚠️ Cùng một khuôn TextBlock thường được copy sang nhiều view → khi tìm thấy 1 chỗ, hãy grep
  cả project. Lần này 1 lỗi hoá ra nằm ở 13 file.

## Tham chiếu

- Project liên quan: `iPGSv4` / `IPGS.Kiosk.Avalonia` (branch `PAYMENT_KIOSK_HORIZONTAL_PARKING8`)
- Báo cáo đo được: `docs/ux-review/UX-REVIEW-payment-flow-2026-07-27.md` mục #1, #2
- Liên quan: [[avalonia-migration-review-checklist]]
