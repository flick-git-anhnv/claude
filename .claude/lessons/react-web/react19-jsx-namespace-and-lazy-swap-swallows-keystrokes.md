# React 19: JSX namespace chuyển vào module `react` · Tráo component sau `import()` động nuốt phím đang gõ

**Category:** react-web
**Ngày:** 2026-07-26
**Môi trường:** React 19.2, TypeScript 5.9, Vite 7, Vitest 4, `mathlive` 0.110

---

## Lesson 1 — Custom element trong React 19

### Triệu chứng
Khai báo custom element theo cách quen thuộc vẫn fail khi `tsc -b`:

```ts
declare global {
  namespace JSX {
    interface IntrinsicElements { 'math-field': ... }
  }
}
```
```
error TS2339: Property 'math-field' does not exist on type 'JSX.IntrinsicElements'.
error TS7006: Parameter 'e' implicitly has an 'any' type.
```

### Nguyên nhân
React 19 **bỏ JSX namespace toàn cục**; kiểu JSX nay lấy từ chính module `react`.

### Cách xử lý
```ts
import type { MathfieldElement } from 'mathlive'

declare module 'react' {
  namespace JSX {
    interface IntrinsicElements {
      'math-field': React.DetailedHTMLProps<
        React.HTMLAttributes<MathfieldElement>, MathfieldElement>
    }
  }
}
```
Kèm theo: ghi kiểu tường minh cho handler — `onInput={(e: React.FormEvent<MathfieldElement>) => …}`.

### Bẫy đi cùng
`vite.config.ts` có khối `test: { … }` báo `TS2769: 'test' does not exist in type 'UserConfigExport'`.
Sửa: `import { defineConfig } from 'vitest/config'` (không phải `'vite'`).

---

## Lesson 2 — Lazy-load rồi tráo component lúc người dùng đang gõ = mất phím, im lặng

### Triệu chứng
Ô nhập nhẹ tự tráo sang component nặng khi người dùng focus (để lazy-load thư viện 219KB gzip).
Người dùng gõ `1/2`, bấm nút → hệ thống báo **"chưa nhập gì"**. Không exception, không warning.
Rất dễ đi debug nhầm sang logic xử lý giá trị.

### Nguyên nhân
`import()` resolve **bất đồng bộ, ngay giữa lúc đang gõ**. Khi promise xong, component re-render và
**thay hẳn node DOM**; node cũ bị gỡ khỏi cây → phím đang xử lý và các phím sau rơi vào node đã chết,
state cha không bao giờ nhận được giá trị.

### Cách xử lý
Không bao giờ tráo cây DOM theo sự kiện focus/typing. Chỉ tráo khi:
- người dùng **chủ động** bấm nút yêu cầu (nút "ƒx" mở bàn phím công thức), **hoặc**
- ngay lúc mount, trước khi có thể gõ (ví dụ chế độ dành cho trẻ em cần bàn phím công thức mặc định).

Focus chỉ dùng để **nạp trước** (prefetch) thư viện, không đổi cấu trúc DOM.

### Không cần làm lại
- Không cần đồng bộ giá trị thủ công giữa hai ô — không giải quyết được gốc (race vẫn còn).
- Không cần bỏ lazy-load: bỏ đi sẽ phá ngân sách bundle (≤200KB gzip mỗi trang bài học).
