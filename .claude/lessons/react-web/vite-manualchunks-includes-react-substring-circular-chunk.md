---
category: react-web
tags: [vite, rollup, manualChunks, code-splitting, blank-page, circular-chunk]
severity: high
created: 2026-08-07
updated: 2026-08-07
project-origin: Roboflow (KZTEK Labeling Studio)
---

# Vite `manualChunks` dùng `id.includes('react')` gộp nhầm dep gián tiếp (react-redux, react-is) → circular chunk → trang trắng

## Tình huống gặp phải

> Đang làm gì? Tính năng gì? Môi trường nào?

Fix script `start_server.bat` để double-click là chạy đúng server production (client build tĩnh, Express phục vụ chung origin `:4000`). Sau khi vá xong lỗi CORS (server tự chặn origin của chính nó), server chạy OK, HTTP 200, nhưng khi mở bằng browser thật trang vẫn **trắng hoàn toàn** — không lỗi hiển thị rõ trên terminal server.

Stack: Vite 5 + React 18 + `recharts` (dùng `react-redux`/`@reduxjs/toolkit` nội bộ) + `vite.config.ts` có `build.rollupOptions.output.manualChunks` tự viết bằng tay để tách vendor-react / vendor-recharts / vendor-icons / vendor-utils.

## Triệu chứng / Lỗi

```
Circular chunk: vendor-utils -> vendor-react -> vendor-utils. Please adjust the manual chunk logic for these chunks.
```

Cảnh báo này xuất hiện ngay trong log `vite build` — dễ bị bỏ qua vì build vẫn "thành công" (exit code 0, `dist/` vẫn được tạo đủ file). Hậu quả thực tế: khi load trang trong browser, React không mount được gì (`#root` rỗng ban đầu), thường kèm `ReferenceError: Cannot access 'X' before initialization` trong console — đúng dấu hiệu Temporal Dead Zone (TDZ) do 2 chunk ESM import vòng lẫn nhau.

## Nguyên nhân gốc rễ (Root Cause)

`manualChunks` viết tay theo pattern:

```js
manualChunks(id) {
  if (id.includes('node_modules')) {
    if (id.includes('recharts')) return 'vendor-recharts';
    if (id.includes('lucide-react')) return 'vendor-icons';
    if (id.includes('react-dom') || id.includes('react-router-dom') || id.includes('react')) return 'vendor-react';
    return 'vendor-utils';
  }
}
```

`id.includes('react')` là substring match quá rộng — nó match luôn `node_modules/react-redux/...`, `node_modules/react-is/...`, `node_modules/react-smooth/...` — đây là **dependency gián tiếp của `recharts`**, không phải React core. Vì check `recharts` chỉ match đúng path `node_modules/recharts/...`, các package con của nó (react-redux, reselect, immer, use-sync-external-store, victory-vendor...) lọt qua và bị gộp sai:

- `react-redux` (dùng bởi recharts) → bị gộp vào `vendor-react` (do chứa substring "react")
- Phần lõi Redux/reselect/immer của nó → rơi vào `vendor-utils` (không chứa "react"/"recharts")
- `vendor-recharts` import `react-redux` (nằm trong `vendor-react`) → `vendor-react` import ngược lại phần Redux core (nằm trong `vendor-utils`) → **vendor-utils ⇄ vendor-react** thành vòng lặp ESM.

Rollup vẫn build ra file, nhưng thứ tự khởi tạo module giữa 2 chunk vòng nhau không xác định được đúng — lúc runtime một chunk cố truy cập biến của chunk kia trước khi nó được gán giá trị (TDZ) → exception ngay khi entry script chạy → React không bao giờ gọi `createRoot().render()` → `<div id="root">` mãi trống → trang trắng, không lỗi network, không lỗi CORS, response HTML/JS đều 200 OK (dễ đánh lừa là "server có vấn đề" trong khi lỗi ở tầng client bundle).

## Giải pháp

Xoá hẳn `manualChunks` viết tay, để Rollup tự quyết định chia chunk (mặc định không tạo vòng lặp vì nó phân tích đúng graph phụ thuộc thật, không dựa vào tên chuỗi):

```ts
// client/vite.config.ts
build: {
  // Không tự chia manualChunks — cách chia bằng id.includes('react') vô tình gộp
  // luôn dependency gián tiếp của recharts (react-redux, react-is...) vào chunk
  // 'vendor-react', tạo vòng tham chiếu với 'vendor-utils'. Để Rollup tự quyết định.
  chunkSizeWarningLimit: 1000,
},
```

1. Xoá field `manualChunks` (và có thể tăng `chunkSizeWarningLimit` để khỏi cảnh báo bundle to do gộp chung).
2. Rebuild (`npm run build --prefix client`) → xác nhận log **không còn** dòng `Circular chunk: ...`.
3. **PHẢI verify bằng browser thật** (không chỉ `curl`/`Invoke-WebRequest` — response HTTP 200 không nói lên gì về lỗi JS runtime). Dùng Playwright:
   ```js
   const { chromium } = require('playwright');
   const browser = await chromium.launch();
   const page = await browser.newPage();
   page.on('pageerror', e => console.log('[pageerror]', e.message));
   await page.goto('http://localhost:4000/', { waitUntil: 'networkidle' });
   console.log(await page.evaluate(() => document.getElementById('root').innerHTML.slice(0,200)));
   ```
   Nếu `#root` có nội dung thật (không rỗng) và không có `pageerror` → xác nhận đã fix.

## Áp dụng lại (How to reuse)

- Thấy dòng `Circular chunk: X -> Y -> X` trong log `vite build`/`rollup build` (bất kỳ project Vite nào) → **không được bỏ qua dù build "thành công"** — đây gần như chắc chắn sẽ gây lỗi runtime khi chạy thật.
- Trước khi tự viết `manualChunks` bằng `id.includes(<tên gói>)`, kiểm tra transitive dependencies của các gói lớn (`recharts`, `antd`, `@mui/*`, ...) — nhiều gói UI/chart lớn kéo theo `react-redux`, `react-is`, `use-sync-external-store` mà tên chứa substring dễ match nhầm ("react", "dom", "router"...).
- Ưu tiên **không** tự viết `manualChunks` trừ khi bundle thật sự quá lớn cần tối ưu — mặc định của Rollup an toàn hơn optimize sớm.
- Khi debug "trang trắng nhưng server trả 200" → luôn nghi ngờ lỗi JS runtime ở client bundle (circular chunk, TDZ, unhandled exception khi mount), không chỉ nghi CORS/network. Mở DevTools Console hoặc dùng Playwright `page.on('pageerror')` để bắt lỗi thật, đừng chỉ test bằng `curl`/`Invoke-WebRequest`.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ `id.includes('react')` cũng match `react-redux`, `react-is`, `react-smooth`, `react-transition-group`, `use-sync-external-store` (một số bản có `react` trong path phụ) — bất kỳ check substring "react" nào trong `manualChunks` đều có rủi ro này.
- ⚠️ Build exit code 0 và `dist/` đủ file **không đảm bảo** bundle chạy đúng — luôn kiểm cảnh báo circular chunk trong log build, và verify bằng browser thật trước khi kết luận "đã fix".
- ⚠️ `curl`/`Invoke-WebRequest` chỉ test được tầng HTTP, không chạy JS — không đủ để verify lỗi client-side rendering.

## Tham chiếu

- Rollup docs — Circular chunk warning: https://rollupjs.org/troubleshooting/#warning-circular-dependency
- Project liên quan: Roboflow (KZTEK Labeling Studio) — `client/vite.config.ts`
