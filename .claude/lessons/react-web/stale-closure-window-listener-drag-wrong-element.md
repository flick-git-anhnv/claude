---
category: ui-patterns
tags: [react, closure, window-event-listener, drag-drop, canvas, state-vs-ref, rubber-band-select]
severity: high
created: 2026-08-05
updated: 2026-08-05
project-origin: Roboflow - Copy (KZTEK Labeling Studio)
---

# Drag/resize trên canvas dùng `window.addEventListener` bị stale closure — kéo A lại thao tác nhầm B

## Tình huống gặp phải

> Đang làm gì? Tính năng gì? Môi trường nào?

React + canvas 2D, component `AnnotatorPage.tsx` cho phép vẽ/chọn/kéo-di chuyển/resize
nhiều bounding box trên 1 ảnh. Vì cần drag tiếp tục hoạt động ngay cả khi chuột ra ngoài
`<canvas>`, `onMouseDown` gọi `attachWindowDragListeners()` để đăng ký
`window.addEventListener('mousemove'/'mouseup', ...)` trỏ tới 2 hàm thường (không
`useCallback`) `handleDragMove`/`handleDragUp` — các hàm này đọc `selectedId` (React state)
để biết đang kéo box nào.

## Triệu chứng / Lỗi

User bấm-kéo 1 box **CHƯA được chọn từ trước** (box khác đang được chọn) → box **ĐANG
ĐƯỢC CHỌN TRƯỚC ĐÓ** bị di chuyển, không phải box vừa bấm. Trực quan: "kéo ô A lại thả/di
chuyển ô B". Chỉ xảy ra khi có ≥ 2 box và đang chuyển vùng chọn ngay trong cùng 1 lần
mousedown; nếu chỉ có 1 box hoặc box vừa bấm đã sẵn đang được chọn từ trước thì không thấy
lỗi (dễ bị bỏ sót khi test qua loa với 1 box).

## Nguyên nhân gốc rễ (Root Cause)

Trong `onMouseDown`:
```ts
const hit = hitTestBox(x, y);
if (hit) {
  setSelectedId(hit.id);              // (1) chỉ SCHEDULE re-render, chưa update ngay
  dragRef.current = { mode: 'move', orig: cloneBox(hit) }; // (2) ref — update NGAY
  attachWindowDragListeners();        // (3) tạo closure MỚI cho move/up NGAY LÚC NÀY
}
```
`attachWindowDragListeners()` tạo closure `move = (e) => handleDragMove(...)` tại đúng
thời điểm (3) — nhưng `handleDragMove` là hàm thường (được tạo lại mỗi render), nên closure
này vẫn đóng theo **state `selectedId` của LẦN RENDER TRƯỚC** (giá trị cũ, trước khi (1)
kịp re-render). Trong khi đó `dragRef.current` là `ref` — mutate NGAY, không chờ re-render.
Bên trong `handleDragMove`, code lại dùng `selectedId` (state, cũ) để xác định box cần
cập nhật thay vì `drag.orig.id` (ref, luôn mới) → áp update lên box SAI (box được chọn từ
trước khi bấm chuột).

## Giải pháp

Trong mọi logic chạy bên trong window-level listener được gắn từ `onMouseDown`/`onPointerDown`
(tồn tại xuyên suốt 1 lần drag), **luôn dùng dữ liệu đã lưu trong `ref` tại thời điểm mousedown
để xác định "đối tượng đang bị tác động"**, KHÔNG dùng lại state (`selectedId`, hay bất kỳ
state khác có thể đổi ngay trong cùng handler) — vì state closure có thể vẫn là giá trị cũ.

```ts
// ĐÚNG — closure chỉ đọc drag.orig.id (từ ref, luôn đồng bộ với đúng lần mousedown này)
} else if (drag.mode === 'move' && drag.orig) {
  const targetId = drag.orig.id;
  setBoxes((prev) => prev.map((b) => (b.id === targetId ? { ...b, ... } : b)));
}
```
```ts
// SAI — đọc `selectedId` (state) có thể vẫn là giá trị TRƯỚC lần setSelectedId() vừa gọi
} else if (drag.mode === 'move' && drag.orig && selectedId) {
  setBoxes((prev) => prev.map((b) => (b.id === selectedId ? { ...b, ... } : b)));
}
```

1. Xác định mọi nơi trong `handleDragMove`/`handleDragUp` (hay tương đương) có so sánh
   `b.id === selectedId` (hoặc bất kỳ state tương tự) khi đang trong 1 phiên drag.
2. Đổi sang so sánh với id đã lưu trong `dragRef.current.orig.id` (hoặc field ref tương ứng)
   — field này được set NGAY trong `onMouseDown`, đồng bộ tuyệt đối với đúng đối tượng vừa
   bấm chuột, không phụ thuộc React đã re-render xong hay chưa.

## Áp dụng lại (How to reuse)

- Khi thấy code **vừa `setState(newSelection)` vừa NGAY SAU ĐÓ đăng ký
  `window.addEventListener`/`setTimeout`/callback khác đọc lại state đó trong CÙNG 1 event
  handler** → nghi ngờ stale closure ngay. Kiểm tra: giá trị đọc lại có phải luôn nhất quán
  với state VỪA set không, hay có thể vẫn là giá trị của lần render trước?
- Quy tắc chung: bất kỳ giá trị nào cần **đúng ngay lập tức, không chờ re-render**, và được
  1 window/document listener sống lâu hơn 1 lần render đọc lại → phải lưu trong `ref`, không
  lưu trong state.
- Test case tối thiểu để phát hiện lỗi này: cần ≥ 2 object có thể chọn, thao tác "click+drag
  1 object CHƯA được chọn từ trước" (không phải object đang active) — test với 1 object duy
  nhất hoặc luôn thao tác trên object đã sẵn chọn sẽ KHÔNG phát hiện ra bug.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Bug này **im lặng hoàn toàn** — không throw lỗi, không log console, chỉ sai lệch hành
  vi trực quan (rất dễ bị coi là "chuột lag" hoặc "user bấm nhầm" khi report qua lời nói).
- ⚠️ `dragRef.current.mode`/`.handle` đã đúng kiểu ref từ đầu (không bug) — chỉ riêng phần
  tính "áp update vào box nào" bị lẫn dùng state là bug; dễ sót nếu chỉ review code theo
  từng dòng mà không truy nguyên toàn bộ chuỗi state→ref→closure.
- ⚠️ `preDragSnapshotRef`/`selectedId` vẫn ĐÚNG cho mục đích khác (hiển thị UI, undo/redo) —
  chỉ riêng bên trong hàm chạy trong window-listener attach 1 lần mỗi phiên drag là cần cẩn
  trọng.

## Lần lặp lại thứ 2 (2026-08-05, cùng ngày, cùng file) — rubber-band select đọc `selectRect` (state) trong `handleDragUp`

Khi thêm tính năng rubber-band multi-select (kéo vùng chọn nhiều box), pattern
```ts
// onMouseDown — bắt đầu kéo vùng chọn
dragRef.current = { mode: 'select', ... };
setSelectRect({ x0: x, y0: y, x1: x, y1: y });   // (1) chỉ SCHEDULE update
attachWindowDragListeners();                      // (2) tạo closure move/up NGAY

// handleDragMove — cập nhật preview khi kéo (được gọi lặp lại qua listener 'move')
setSelectRect({ x0: drag.startX, y0: drag.startY, x1: x, y1: y }); // chỉ set, không đọc lại → AN TOÀN

// handleDragUp — tính box nào nằm trong vùng chọn khi thả chuột
} else if (drag.mode === 'select' && selectRect) {   // ❌ đọc `selectRect` (state) — STALE
  // rect luôn là rect lúc mousedown (kích thước ~0), KHÔNG PHẢI rect cuối cùng
  // đã kéo tới → rubber-band chỉ "chọn" đúng 1 box tại điểm bắt đầu, bỏ sót
  // toàn bộ các box khác nằm trong vùng đã kéo qua.
}
```
tái hiện đúng lỗi này lần thứ 2, dù đã biết pattern: `setSelectRect(...)` gọi
NHIỀU LẦN trong `handleDragMove` (qua `window.addEventListener('mousemove', ...)`)
đều an toàn (chỉ SET, không đọc), nhưng `handleDragUp` (qua `mouseup` listener,
gắn 1 LẦN DUY NHẤT tại mousedown) lại ĐỌC LẠI `selectRect` từ closure — closure đó
đóng theo state tại **thời điểm mousedown**, trước khi bất kỳ `setSelectRect` nào
trong lúc kéo có cơ hội "thấy" bởi hàm `handleDragUp` cụ thể này.

**Gotcha bổ sung phát hiện lần này:** Chỉ SET một state trong suốt phiên drag
(không có nơi nào ĐỌC LẠI nó bên trong cùng phiên) là AN TOÀN dù dùng state hay ref
— staleness chỉ xảy ra ở nơi ĐỌC state đó lại bên trong 1 listener sống lâu hơn 1
render. Vì vậy khi audit, phải tách riêng "nơi set" và "nơi đọc lại" của cùng 1
state, không thể kết luận an toàn/không an toàn chỉ từ việc thấy `setX(...)` xuất
hiện nhiều lần.

**Fix giống hệt lần 1:** thêm `selectRectRef` (ref) song song với `selectRect`
(state), `handleDragMove` ghi đồng thời vào cả hai (`ref.current = ...; setState(...)`),
`handleDragUp` đọc từ `ref.current` (luôn mới) thay vì đọc `selectRect` (state, cũ).
State `selectRect` vẫn giữ lại — chỉ dùng để RENDER preview trong `draw()`, không
bao giờ đọc lại trong logic bên trong window listener.

**Verify:** Playwright rubber-band kéo qua 3 box mới vẽ → trước fix chỉ thấy
"1 khung đã chọn" trong header dù đã kéo qua cả 3; sau fix thấy đúng
"3 khung đã chọn". Đây là cách phát hiện thực tế lỗi lần 2 — không đoán mò, đo bằng
Playwright rồi mới sửa.

## Tham chiếu

- Project liên quan: KZTEK Labeling Studio (`client/src/pages/AnnotatorPage.tsx`,
  hàm `onMouseDown`/`handleDragMove`/`handleDragUp`) — 2 lần xuất hiện: di chuyển
  box đơn (2026-08-05, lần 1) và rubber-band multi-select (2026-08-05, lần 2)
