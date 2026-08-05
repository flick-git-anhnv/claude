---
category: ui-patterns
tags: [vite, network, cors, lan, firewall, dev-server]
severity: medium
created: 2026-08-05
updated: 2026-08-05
project-origin: Roboflow - Copy (KZTEK Labeling Studio)
---

# Máy khác trong LAN không truy cập được Vite dev server dù đã mở firewall

## Tình huống gặp phải

> Đang làm gì? Tính năng gì? Môi trường nào?

Chạy `vite` dev server (`npm run dev`, config `server: { port: 5173, proxy: {...} }`
KHÔNG có `host`) trên máy A, cố truy cập từ máy B cùng mạng LAN qua
`http://<IP-máy-A>:5173`.

## Triệu chứng / Lỗi

User báo "sửa máy khác ko truy cập được, đã mở filewall rồi" — đã mở Windows
Firewall inbound rule cho port 5173/4000 nhưng máy khác vẫn không kết nối
được (connection refused/timeout).

## Nguyên nhân gốc rễ (Root Cause)

**Mở firewall KHÔNG đủ** — firewall chỉ kiểm soát traffic ở tầng OS/network,
nhưng ứng dụng (Vite dev server) phải THỰC SỰ LẮNG NGHE (bind/listen) trên
network interface đó trước. Vite mặc định (khi không cấu hình `server.host`)
CHỈ bind vào `localhost`/`127.0.0.1` — không lắng nghe trên bất kỳ IP LAN nào
của máy, dù firewall có mở cổng hay không. Kết quả: request từ máy khác
KHÔNG BAO GIỜ tới được tiến trình Vite, vì hệ điều hành không có gì đang nghe
ở địa chỉ IP LAN:port đó để chuyển tiếp tới.

Vấn đề PHỤ (xảy ra SAU khi fix bind): nếu backend có CORS allowlist cứng
(chỉ `http://localhost:5173`), request từ máy khác dùng `Origin:
http://<IP-LAN>:5173` sẽ bị CORS chặn — trang có thể load được (static
files) nhưng MỌI lời gọi API đều fail, trông như "app bị hỏng" chứ không rõ
là do CORS.

## Giải pháp

**1. Vite — bind ra mọi network interface:**
```ts
// vite.config.ts
export default defineConfig({
  server: {
    port: 5173,
    host: true, // hoặc host: '0.0.0.0' — bind LAN, không chỉ localhost
    proxy: { '/api': 'http://localhost:4000', ... }, // proxy target GIỮ NGUYÊN
    // localhost — vì Vite proxy chạy trong tiến trình Node của Vite trên
    // CHÍNH máy A, luôn gọi được backend cùng máy qua localhost bất kể
    // client đang browse từ máy nào.
  },
});
```
Sau khi thêm `host: true`, log Vite sẽ tự in thêm dòng `➜ Network:
http://<IP-LAN>:5173/` cho MỌI network interface đang có — dùng đúng địa chỉ
đó để truy cập từ máy khác.

**2. Backend — CORS cho phép origin LAN (chỉ khi dev, KHÔNG production):**
```js
const IS_PROD = process.env.NODE_ENV === 'production';
const LAN_ORIGIN_RE = /^https?:\/\/(192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}):5173$/;
// trong callback origin của middleware cors():
if (!IS_PROD && LAN_ORIGIN_RE.test(origin)) return cb(null, true);
```
Regex khớp đúng 3 dải mạng riêng theo RFC 1918 (192.168.x.x, 10.x.x.x,
172.16-31.x.x) — KHÔNG mở cho origin public bất kỳ, giữ nguyên chặt trong
production (`NODE_ENV=production` luôn theo đúng allowlist tường minh
`CORS_ORIGIN`).

## Áp dụng lại (How to reuse)

- Bất kỳ report "máy khác không truy cập được [dev server]" → hỏi/kiểm tra
  NGAY 2 điều theo đúng thứ tự: (1) dev server có bind LAN không (`host: true`
  cho Vite, tương tự với Next.js/webpack-dev-server/CRA cũng cần cấu hình
  tương ứng), (2) backend có CORS chặn origin LAN không — firewall LUÔN LÀ
  ĐIỀU THỨ 3, thường KHÔNG phải nguyên nhân nếu user tự báo "đã mở rồi".
- Cách verify nhanh không cần máy thứ 2: xem log Vite có dòng "➜ Network:"
  hay không sau khi start — có dòng đó = đã bind LAN đúng.
- Verify CORS bằng `curl -X OPTIONS <api-url> -H "Origin: http://<LAN-IP>:5173"
  -H "Access-Control-Request-Method: GET"` — response có header
  `Access-Control-Allow-Origin` khớp đúng origin = OK.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ `host: true` khiến Vite lắng nghe TRÊN MỌI interface — bao gồm cả
  interface ảo (WSL, Docker, VPN) có thể hiện ra IP không mong đợi trong log
  "Network:" — không phải lỗi, chỉ là các adapter khác của máy.
- ⚠️ KHÔNG mở CORS LAN regex trong production — chỉ dùng khi
  `NODE_ENV !== 'production'`, vì mục đích ban đầu là hỗ trợ demo/test nội bộ
  trong văn phòng, không phải để expose ra ngoài an toàn.
- ⚠️ Nếu backend/API server (khác Vite) cũng cần LAN access, PHẢI kiểm tra
  riêng — `app.listen(PORT)` (không có host) trong Node.js MẶC ĐỊNH đã bind
  `0.0.0.0`/`::` (khác Vite!), nên thường KHÔNG cần sửa gì cho phần backend
  Node thuần — chỉ riêng Vite (và CORS) là điểm cần sửa.

## Tham chiếu

- Vite docs — `server.host`: https://vite.dev/config/server-options.html#server-host
- Project liên quan: KZTEK Labeling Studio
  (`client/vite.config.ts`, `server/src/index.js` — CORS middleware)
