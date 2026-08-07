---
category: ui-patterns
tags: [css, flexbox, overflow, scroll, justify-content, align-items, zoom, canvas]
severity: critical
created: 2026-08-05
updated: 2026-08-05
project-origin: Roboflow - Copy (KZTEK Labeling Studio)
---

# `justify-content: center` / `align-items: center` trên container `overflow: auto` — nội dung tràn ra bị cắt VĨNH VIỄN, không scroll tới được

## Tình huống gặp phải

> Đang làm gì? Tính năng gì? Môi trường nào?

Canvas annotator (zoom ảnh), container `.canvas-stage` dùng `display: flex;
align-items: center; justify-content: center; overflow: auto;` để canh giữa
ảnh nhỏ (khi chưa zoom, ảnh nhỏ hơn container) VÀ cho phép scroll khi ảnh lớn
hơn container (khi đã zoom).

## Triệu chứng / Lỗi

User báo: "sau khi zoom không move được hết hình" — kéo/scroll về "góc trên-trái"
vẫn không thấy mép trái thật của ảnh (dừng giữa đường, ví dụ thấy cột D thay vì
cột A). Đo thực tế: `canvas.getBoundingClientRect().width` (kích thước canvas
thật) LỚN HƠN `container.scrollWidth` (vùng scroll trình duyệt cho phép) —
chênh lệch TĂNG DẦN theo mức zoom (zoom 125% chênh ~107px, zoom 381% chênh
~1210px). Nghĩa là zoom cao thì phần ảnh KHÔNG THỂ SCROLL TỚI càng lớn.

## Nguyên nhân gốc rễ (Root Cause)

Đây là hành vi ĐÚNG THEO SPEC của CSS Flexbox, không phải browser bug — nhưng
là 1 cạm bẫy rất phổ biến: khi 1 flex item lớn hơn flex container và
`justify-content`/`align-items` = `center` (không phải `flex-start`/`start`),
trình duyệt **canh giữa item bằng cách tràn ĐỀU 2 phía** (trái+phải hoặc
trên+dưới) — nhưng vùng overflow phía ĐẦU (trái/trên) bị coi là "trước điểm
scroll 0" và KHÔNG được tính vào phạm vi có thể scroll tới. Kết quả: dù item
tràn ra 2 phía bằng nhau, scroll container CHỈ cho phép truy cập phần tràn ở
CUỐI (phải/dưới), phần tràn ở ĐẦU (trái/trên) bị cắt vĩnh viễn không cách nào
kéo tới — dù v���n "tồn tại" trong DOM/canvas.

## Giải pháp

Đổi `center` → `safe center` (CSS Box Alignment Level 3, hỗ trợ tốt trên
Chromium/Firefox hiện đại):

```css
.canvas-stage {
  display: flex;
  align-items: safe center;      /* thay vì: align-items: center; */
  justify-content: safe center;  /* thay vì: justify-content: center; */
  overflow: auto;
}
```

`safe` báo trình duyệt: "canh giữa NẾU đủ chỗ (không tràn); nếu tràn (nội dung
lớn hơn container) → tự chuyển về canh `start` để tránh mất khả năng truy cập
nội dung (data loss)". Giữ đúng hành vi canh giữa mong muốn khi ảnh còn nhỏ
(chưa zoom), tự sửa đúng khi ảnh đã zoom lớn hơn container.

**Verify sau khi fix:** đo lại `scrollWidth` phải BẰNG (không còn nhỏ hơn)
`canvas.getBoundingClientRect().width` tại mọi mức zoom; scroll tới max phải
cho `canvas.right === container.right` (không còn cắt mép).

## Áp dụng lại (How to reuse)

- Bất kỳ container có `overflow: auto/scroll` VÀ `display: flex` VÀ
  `justify-content`/`align-items` = `center` VÀ nội dung con CÓ THỂ lớn hơn
  container tại runtime (ảnh zoom, canvas resize động, nội dung load động độ
  dài không biết trước) → PHẢI dùng `safe center`, không dùng `center` trần.
- Cách phát hiện nhanh không cần đọc hết code: so sánh `element.scrollWidth`
  (hoặc `scrollHeight`) với `child.getBoundingClientRect().width/height` —
  nếu `scrollWidth < child width` khi container có overflow → chính là bug này.
- Test case bắt buộc cho MỌI tính năng zoom/pan trên canvas: scroll về (0,0)
  và verify vị trí thật của nội dung (VD `canvas.getBoundingClientRect().left`
  phải khớp container's left khi ở mép), KHÔNG chỉ test "scroll có đổi số hay
  không" (số scrollLeft/Top đổi không có nghĩa là đã tới được TRUE edge).

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ **RẤT DỄ NHẦM VỚI BUG KHÁC**: hiện tượng "canvas to hơn vùng scroll" nhìn
  qua số liệu giống như đang có 1 phép tính `fitScale`/`zoom` SAI ở JS — dễ
  lãng phí thời gian debug logic JS (đã kiểm tra kỹ và logic tính canvas.width
  hoàn toàn ĐÚNG trong case này) trước khi nhận ra nguyên nhân là 3 dòng CSS.
  Luôn kiểm tra CSS `justify-content`/`align-items` của container scroll TRƯỚC
  khi đi sâu debug JS logic zoom/resize.
- ⚠️ `align-items: safe center` cần browser tương đối mới (Chrome ~2022+,
  Firefox lâu hơn); nếu cần hỗ trợ browser cũ hơn, fallback an toàn hơn là bỏ
  hẳn flex-centering trên container scroll, dùng `margin: auto` trên chính
  phần tử con (canvas) khi chưa tràn, hoặc căn giữa bằng padding tính toán
  trong JS dựa theo kích thước thật.
- ⚠️ Chênh lệch TĂNG DẦN theo zoom (không phải hằng số) — nếu chỉ test ở 1 mức
  zoom thấp có thể thấy chênh lệch nhỏ, dễ tưởng "chấp nhận được"/"sai số làm
  tròn" — PHẢI test ở nhiều mức zoom khác nhau, đặc biệt zoom cao, để thấy rõ
  bug là hệ thống không phải nhiễu.

## Tham chiếu

- CSS Box Alignment Level 3 — "safe" và "unsafe" alignment:
  https://www.w3.org/TR/css-align-3/#overflow-values
- MDN `justify-content`, mục "Values" giải thích `safe`/`unsafe`:
  https://developer.mozilla.org/en-US/docs/Web/CSS/justify-content
- Project liên quan: KZTEK Labeling Studio
  (`client/src/pages/AnnotatorPage.tsx` / `client/src/styles.css` — `.canvas-stage`)
