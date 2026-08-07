---
category: ui-patterns
tags: [css, flexbox, min-width, input, overflow, sidebar]
severity: high
created: 2026-08-05
updated: 2026-08-05
project-origin: Roboflow - Copy (KZTEK Labeling Studio)
---

# `<input>` trong hàng flex hẹp (`flex:1`) không co như mong đợi — đẩy nút/control khác ra ngoài vùng nhìn thấy

## Tình huống gặp phải

> Đang làm gì? Tính năng gì? Môi trường nào?

React + CSS thường (không Tailwind), 1 hàng flex trong sidebar hẹp (~260-280px) gồm:
`<input type="color">` (swatch màu) + `<input type="text">` (tên, `flex:1`) +
`<input class="hotkey-input">` (phím tắt, `flex:none`, width cố định 26px) +
`<button>✕</button>` (xoá). User báo "không xóa được nhãn, không gán được phím tắt".

## Triệu chứng / Lỗi

Ảnh chụp thực tế: chỉ thấy 1 vạch mỏng "|" (đáng ra là swatch màu 22×22px) + tên +
1 ô vuông có dấu "—" (hotkey input placeholder) — **hoàn toàn không thấy nút xoá ✕**.
Đo bằng Playwright `boundingBox()`:
- `input[type=color]`: chỉ rộng **6px** (CSS khai `width:22px`)
- `<button>✕</button>`: `x: 273`, trong khi `.class-row` (container) chỉ rộng đến
  `x: 265` → **nút nằm NGOÀI vùng nhìn thấy của container, bị tràn/clip**
- `input[type=text]` (tên nhãn): đo được **172px** dù CSS khai `flex: 1` trong 1
  container chỉ có ~224px khả dụng cho 4 phần tử.

## Nguyên nhân gốc rễ (Root Cause)

Mọi phần tử `<input>`/`<select>`/`<button>` trong flex container có **giá trị mặc
định `min-width: auto`** — với input, giá trị này gần bằng độ rộng mặc định của
trình duyệt cho input rỗng (thường 170-190px), **KHÔNG PHẢI 0**. Đặt `flex: 1`
(hoặc bất kỳ `flex-shrink` khác 0) trên input **KHÔNG ghi đè `min-width: auto`** —
input vẫn từ chối co xuống dưới ngưỡng đó dù `flex-shrink` yêu cầu co lại.

Khi tổng min-content-width của các phần tử KHÔNG co được (input text ~172px +
input hotkey cố định 26px) đã vượt quá container (224px), flexbox buộc phải
**tràn (overflow)** — phần "tràn" này rơi vào các phần tử co được còn lại
(color input, button), khiến chúng bị bóp cực nhỏ (6px) hoặc bị đẩy hẳn ra
ngoài container (button `x=273` > container edge `x=265`).

## Giải pháp

```css
/* Bắt buộc min-width: 0 cho MỌI input có flex:1 (hoặc flex-shrink khác 0)
   trong 1 hàng flex hẹp — đây là bước KHÔNG THỂ THIẾU, không phải tuỳ chọn. */
.class-row input[type=text] { flex: 1; min-width: 0; ... }

/* Các phần tử cố định kích thước nên khai flex-shrink: 0 rõ ràng
   (đừng chỉ dựa vào width) để không bị bóp/tràn khi container hẹp. */
.class-row input[type=color] { width: 22px; min-width: 22px; flex-shrink: 0; ... }
.class-row button { flex-shrink: 0; ... }
```

1. Tìm mọi `<input>`/`<textarea>`/`<select>` đặt `flex: 1` (hoặc `flex-grow`/`flex-shrink`
   khác giá trị mặc định) trong 1 hàng flex — kiểm tra đã có `min-width: 0` chưa.
2. Với các phần tử KHÔNG nên co (icon button, ô cố định kích thước) → khai
   `flex-shrink: 0` rõ ràng, không chỉ dựa vào `width` (width không tự bảo vệ
   khỏi bị co khi anh em cùng hàng không đủ chỗ).
3. Verify bằng cách đo `boundingBox()` thực tế (Playwright) hoặc DevTools —
   đừng chỉ đọc CSS source, vì hành vi tràn/co chỉ lộ ra khi RENDER thật với
   dữ liệu thật (tên nhãn dài, container hẹp).

## Áp dụng lại (How to reuse)

- Khi thấy 1 hàng flex trong sidebar/panel hẹp có `<input>` với `flex:1`, VÀ
  có report kiểu "không thấy nút X", "nút Y biến mất", "ô Z bị bóp nhỏ" →
  nghi ngay `min-width: auto` mặc định của input, KHÔNG cần đợi đến khi đọc
  code mới nghi.
- Cách phát hiện nhanh không cần code: DevTools → chọn input đó → tab
  "Computed" → tìm `min-width` → nếu ra `auto` (không phải `0px`) trong 1 flex
  container hẹp → chính là nguyên nhân.
- Test case tối thiểu: đặt tên/nội dung DÀI vào input đó rồi resize container
  xuống hẹp (hoặc test luôn ở viewport hẹp) — bug chỉ lộ khi tổng min-content
  các phần tử KHÔNG co (input, hotkey cố định) vượt quá container.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Đây là hành vi ĐÚNG theo spec CSS Flexbox (không phải browser bug) —
  `min-width: auto` cho flex item được kế thừa từ **automatic minimum size**,
  áp dụng cho MỌI phần tử "replaced" hoặc có nội dung intrinsic (input, img,
  ...), không chỉ input text.
- ⚠️ Không phải lúc nào cũng dễ nhận ra qua screenshot — phần tử bị đẩy RA
  NGOÀI container (không phải bị `display:none`) vẫn NẰM TRONG DOM, các click
  test (`locator.click()` không `force`) có thể báo "not visible"/timeout,
  nhưng `force: true` hoặc click theo toạ độ tuyệt đối vẫn "thành công" về mặt
  test framework dù người dùng thật không bao giờ bấm trúng — luôn đo
  `boundingBox()` so với container để xác nhận phần tử thực sự nằm TRONG vùng
  hiển thị, không chỉ kiểm tra "click có chạy không".
- ⚠️ `confirm()`/`alert()` (dialog trình duyệt gốc) trong code xoá bị Playwright
  TỰ ĐỘNG dismiss (return `false`) nếu không đăng ký `page.on('dialog', ...)` —
  dễ nhầm "nút xoá không hoạt động" (do dialog bị auto-cancel) với bug thật
  (nút bị tràn ra ngoài). Luôn tách 2 kiểm tra: (1) đo vị trí nút có nằm trong
  container không, (2) accept dialog rồi thử click thật để xác nhận logic xoá.

## Tham chiếu

- CSS Flexbox spec — "Automatic Minimum Size of Flex Items":
  https://www.w3.org/TR/css-flexbox-1/#min-size-auto
- Project liên quan: KZTEK Labeling Studio
  (`client/src/pages/ProjectDetailPage.tsx` — `.class-row`, `client/src/styles.css`)
