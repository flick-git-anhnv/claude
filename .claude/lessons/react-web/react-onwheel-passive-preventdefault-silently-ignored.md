---
category: ui-patterns
tags: [react, wheel-event, passive-listener, zoom, canvas, preventDefault]
severity: high
created: 2026-08-05
updated: 2026-08-05
project-origin: Roboflow - Copy (KZTEK Labeling Studio)
---

# `onWheel={handler}` trong JSX — `e.preventDefault()` bị trình duyệt lặng lẽ bỏ qua (passive listener)

## Tình huống gặp phải

> Đang làm gì? Tính năng gì? Môi trường nào?

React 18 + canvas annotator, cần zoom ảnh tại đúng vị trí con trỏ khi lăn chuột
(tương tự Tkinter `MouseWheel` bind ở tool desktop cũ). Code dùng JSX
`<div onWheel={onWheelZoom}>` với `onWheelZoom` gọi `e.preventDefault()` để chặn
scroll native của trình duyệt, tự tính `container.scrollLeft/scrollTop` theo
logic zoom riêng.

## Triệu chứng / Lỗi

Console warning: `Unable to preventDefault inside passive event listener
invocation.` — zoom vẫn "chạy" (state zoom đổi đúng %) nhưng cảm giác giật/lệch,
vì trình duyệt **VẪN tự scroll native đồng thời** với scroll do code tự tính,
2 cơ chế cộng dồn lên nhau → không mượt như hành vi mong đợi ("giống bản desktop
tool cũ").

## Nguyên nhân gốc rễ (Root Cause)

Từ React 17+ (theo sau thay đổi của Chrome 2019 khuyến nghị wheel/touch listener
mặc định `passive: true` để không block scroll performance), **React tự động gắn
handler cho `onWheel`/`onTouchStart`/`onTouchMove` dưới dạng passive listener**.
Passive listener CAM KẾT với trình duyệt là "tôi sẽ không gọi preventDefault()" —
nếu code vẫn gọi, trình duyệt lặng lẽ BỎ QUA (chỉ log 1 warning, không throw lỗi),
và hành vi scroll/zoom native mặc định VẪN diễn ra bình thường song song với state
update của app.

## Giải pháp

Gắn wheel listener bằng `addEventListener` thủ công với `{ passive: false }`
trong `useEffect`, KHÔNG dùng prop JSX `onWheel`:

```tsx
useEffect(() => {
  const container = containerRef.current;
  if (!container) return;
  const handler = (e: WheelEvent) => {
    e.preventDefault(); // giờ mới có hiệu lực thật
    // ...logic zoom
  };
  container.addEventListener('wheel', handler, { passive: false });
  return () => container.removeEventListener('wheel', handler);
}, [/* dep khiến effect re-run SAU KHI containerRef đã gắn vào DOM thật, xem Gotcha */]);
```

1. Xoá `onWheel={...}` khỏi JSX.
2. Viết lại handler nhận `WheelEvent` gốc (không phải `React.WheelEvent`).
3. Đọc state cần dùng (VD `zoom`) qua **ref** (`zoomRef.current`, cập nhật bằng
   1 `useEffect` phụ `useEffect(() => { zoomRef.current = zoom }, [zoom])`) —
   KHÔNG đọc trực tiếp state đóng trong closure của effect gắn 1 lần, để tránh
   stale closure (xem lesson liên quan `stale-closure-window-listener-drag-wrong-element.md`).

## Áp dụng lại (How to reuse)

- Khi thấy console warning "Unable to preventDefault inside passive event
  listener invocation" → luôn là JSX `onWheel`/`onTouchStart`/`onTouchMove` với
  `preventDefault()` bên trong. Chuyển ngay sang `addEventListener` thủ công.
- Bất kỳ tính năng "zoom tại cursor", "chặn scroll trang khi tương tác canvas",
  "custom pinch-to-zoom" → PHẢI dùng native listener `{passive:false}`, không
  dùng prop JSX tương ứng.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ **Bẫy kép khi component có early-return trước khi render container thật**
  (VD `if (!image) return <p>Đang tải...</p>;` trước JSX chính chứa
  `containerRef`): nếu effect gắn listener dùng `deps: []`, nó chạy NGAY LẦN
  RENDER ĐẦU — lúc đó `containerRef.current` còn `null` (vì JSX chứa ref đó
  chưa từng render) → effect `return` sớm, KHÔNG BAO GIỜ gắn lại được listener
  sau khi container thật sự xuất hiện. Phải thêm dependency đúng (VD `[image]`
  — thứ khiến early-return chuyển sang render container thật) để effect re-run
  và tìm thấy ref đã gắn. Đây là lỗi RẤT DỄ mắc lại khi convert từ JSX prop
  sang effect — test sau khi sửa PHẢI thử với component thật có early-return,
  không chỉ đọc code.
- ⚠️ Chrome DevTools/console warning này KHÔNG fail test tự động (không throw),
  rất dễ bị bỏ qua nếu không chủ động bắt console message trong test — luôn
  assert `console errors/warnings` rỗng trong test tương tác canvas.
- ⚠️ Copy nguyên logic tính `contentX`/`contentY`/`ratio` từ handler JSX cũ sang
  handler mới KHÔNG đủ — phải đổi type từ `React.WheelEvent` sang `WheelEvent`
  gốc (API giống nhau về field cần dùng như `deltaY`/`clientX`/`clientY` nên
  không cần đổi logic, chỉ đổi type annotation + nguồn gắn listener).

## Tham chiếu

- MDN — `EventTarget.addEventListener()`, tham số `passive`:
  https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener#passive
- Chrome "Intervention" 2019 — default passive cho wheel/touch listener trên
  document/window/body (React áp dụng tương tự cho JSX props tương ứng).
- Project liên quan: KZTEK Labeling Studio
  (`client/src/pages/AnnotatorPage.tsx` — wheel-zoom effect)
- Lesson liên quan: `react-web/stale-closure-window-listener-drag-wrong-element.md`
  (cùng pattern "native listener gắn ngoài React render cycle cần cẩn trọng ref vs state")
