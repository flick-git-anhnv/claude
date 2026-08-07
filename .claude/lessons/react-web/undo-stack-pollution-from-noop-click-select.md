---
category: ui-patterns
tags: [undo-redo, canvas, drag-drop, ux]
severity: medium
created: 2026-08-05
updated: 2026-08-05
project-origin: Roboflow - Copy (KZTEK Labeling Studio)
---

# Undo stack bị "rác" bởi snapshot no-op khi mousedown+mouseup không thực sự di chuyển gì

## Tình huống gặp phải

> Đang làm gì? Tính năng gì? Môi trường nào?

Canvas annotator có undo/redo (Ctrl+Z/Ctrl+Y) cho việc vẽ/di chuyển/resize box.
`onMouseDown` khi click vào 1 box đã tồn tại → luôn set `dragRef.current = {mode:
'move', ...}` + capture `preDragSnapshotRef` (trạng thái TRƯỚC đó) — bất kể
sau đó user có thực sự KÉO đi đâu hay chỉ CLICK để chọn (mousedown+mouseup gần
như cùng vị trí).

## Triệu chứng / Lỗi

User báo "Ctrl+Z, Ctrl+Y lúc được lúc không" — bấm Ctrl+Z nhiều lần mới thấy
tác dụng thật, có cảm giác không nhất quán.

## Nguyên nhân gốc rễ (Root Cause)

`handleDragUp` (nhánh `move`/`resize`) push `preDragSnapshotRef.current` vào
`undoStackRef` **VÔ ĐIỀU KIỆN**, không kiểm tra box có thực sự thay đổi
vị trí/kích thước hay không. Mỗi lần user CLICK CHỌN 1 box đã có (không kéo đi
đâu) vẫn tạo ra 1 "snapshot rỗng" — snapshot giống HOÀN TOÀN trạng thái hiện tại
— chiếm 1 slot trong undo stack. Khi user bấm Ctrl+Z, nó "undo" đúng những
snapshot rỗng này trước (không thấy gì đổi trên màn hình vì trạng thái y hệt),
User phải bấm Ctrl+Z NHIỀU LẦN mới lùi qua hết các snapshot rỗng để tới thao
tác THẬT gần nhất — cảm giác như Ctrl+Z "lúc được lúc không".

## Giải pháp

So sánh snapshot trước/sau khi kết thúc drag — chỉ push vào undo stack nếu
THỰC SỰ có thay đổi:

```ts
const changed = preDragSnapshotRef.current
  && JSON.stringify(preDragSnapshotRef.current) !== JSON.stringify(boxesRef.current);
if (changed && preDragSnapshotRef.current) {
  undoStackRef.current.push(preDragSnapshotRef.current);
  // ...
}
```

1. Xác định MỌI nơi push snapshot vào undo stack sau 1 drag session
   (mousedown→mousemove→mouseup) — không chỉ nhánh `move`, còn `resize` và bất
   kỳ tương tác nào khác có thể kết thúc mà không thực sự đổi dữ liệu.
2. So sánh trạng thái TRƯỚC (snapshot capture lúc mousedown) với trạng thái
   SAU (lúc mouseup) — nếu giống nhau (deep-equal, dùng `JSON.stringify` đủ an
   toàn cho mảng object phẳng chỉ có number/string) → BỎ QUA, không push.

## Áp dụng lại (How to reuse)

- Bất kỳ hệ thống undo/redo theo mô hình "capture-before, push-after-if-changed"
  cho drag/move/resize → LUÔN kiểm tra "có thực sự thay đổi" trước khi push,
  KHÔNG BAO GIỜ push vô điều kiện chỉ vì 1 drag-session đã bắt đầu (mousedown
  không đồng nghĩa có thay đổi — click-để-chọn cũng đi qua đúng flow mousedown
  → mouseup).
- Test case bắt buộc cho mọi tính năng undo: (1) click chọn 1 object đã có mà
  KHÔNG di chuyển, kiểm tra undo count KHÔNG tăng; (2) di chuyển thật, kiểm tra
  undo count TĂNG đúng 1; (3) Ctrl+Z ngay sau (1) phải KHÔNG làm gì (vì chưa
  có gì để undo, hoặc undo đúng thao tác thật gần nhất nếu có).
- Dấu hiệu nhận biết loại bug này khi review code cũ: tìm `push(...)` vào undo
  stack trong nhánh xử lý `mouseup`/`pointerup` mà KHÔNG có so sánh trước/sau —
  nghi ngay.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Việc "vẽ box mới" (nhánh `draw`, khác `move`/`resize`) đã có sẵn 1 dạng
  guard tương tự (`willFinalize = lastSize.w > 3 && lastSize.h > 3`) — chỉ
  kiểm tra kích thước tối thiểu, KHÔNG phải so sánh trước/sau đầy đủ, nhưng đủ
  cho case đó (vẽ hụt = box quá nhỏ). Đừng nhầm 2 cơ chế guard khác nhau cho 2
  nhánh khác nhau của cùng 1 handler.
- ⚠️ Bug này KHÔNG gây lỗi hiển thị/console error nào — chỉ là "cảm giác không
  nhất quán" rất khó report chính xác từ phía user ("lúc được lúc không") —
  phải TỰ TÁI HIỆN bằng cách click-chọn nhiều lần rồi đếm số undo hiển thị
  trên nút UI, không thể chỉ đọc code suy luận chắc chắn.

## Tham chiếu

- Project liên quan: KZTEK Labeling Studio
  (`client/src/pages/AnnotatorPage.tsx` — `handleDragUp`, nhánh `move`/`resize`)
