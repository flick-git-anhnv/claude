---
category: react-web
tags: [javascript, date-parsing, python, iso8601, nan, typescript, vite]
severity: high
created: 2026-08-06
updated: 2026-08-06
project-origin: agent-dashboard
---

# JavaScript Date.parse trả NaN với timestamp Python có microseconds (6 chữ số) và +00:00

## Tình huống gặp phải

Đang implement Agent Dashboard (Vite/React/TS), frontend nhận timestamp từ backend Python/FastAPI qua REST API và WebSocket. Hàm `fmtRelative()` hiển thị thời gian tương đối trên AgentCard bị hiển thị "NaNh trước" cho tất cả session cũ hơn vài phút.

## Triệu chứng / Lỗi

```
AgentCard hiển thị: "NaNh trước" (NaN hours ago)
Chỉ session rất mới (~55s) hiển thị đúng "55s trước"
Mọi session từ ngày trước: "NaNh trước"
```

Root expression trong code:
```typescript
const diff = Math.floor((Date.now() - new Date(iso).getTime()) / 1000)
// new Date(iso).getTime() → NaN khi iso = "2026-08-06T08:30:00.123456+00:00"
```

## Nguyên nhân gốc rễ (Root Cause)

Python `datetime.now(timezone.utc).isoformat()` tạo ra chuỗi có **2 vấn đề**:

1. **6 chữ số microseconds**: `"2026-08-06T08:30:00.123456+00:00"` — ECMAScript chỉ hỗ trợ tối đa **3 chữ số** (milliseconds) trong phần thập phân của giây. V8 (Chrome/Node) trả `Invalid Date` / `NaN` với 6+ chữ số.
2. **`+00:00` timezone suffix**: thay vì `Z`. Tuy nhiên, issue chính là microseconds.

Mock data (`.toISOString()`) dùng `Z`-suffix + 3 chữ số → luôn parse đúng, che giấu bug khi test trước khi kết nối backend thật.

**Kiểm tra nhanh trong browser console:**
```javascript
new Date("2026-08-06T08:30:00.123456+00:00").getTime()  // NaN  ← Python format
new Date("2026-08-06T08:30:00.123Z").getTime()           // OK   ← JS .toISOString()
```

## Giải pháp

Thêm hàm `normalizeIso()` trước khi parse và cập nhật mọi hàm format:

```typescript
/** Normalize Python datetime.isoformat() → JS-parseable ISO string */
export function normalizeIso(iso: string): string {
  return iso
    .replace(/(\.\d{3})\d+/, '$1') // truncate microseconds → milliseconds
    .replace(/\+00:00$/, 'Z')      // +00:00 → Z (broader engine support)
}

export function fmtRelative(iso: string): string {
  const ts = new Date(normalizeIso(iso)).getTime()
  if (isNaN(ts)) return fmtDateShort(iso)   // graceful fallback
  const diff = Math.floor((Date.now() - ts) / 1000)
  if (diff < 5) return 'vừa xong'
  if (diff < 60) return `${diff}s trước`
  if (diff < 3600) return `${Math.floor(diff / 60)}m trước`
  if (diff < 86400) {
    const h = Math.floor(diff / 3600)
    const m = Math.floor((diff % 3600) / 60)
    return m > 0 ? `${h}h ${m}m trước` : `${h}h trước`
  }
  return fmtDateShort(iso)  // ≥ 24h: hiện "dd/MM HH:mm" thay "240h trước"
}
```

Áp dụng `normalizeIso()` cho **tất cả** hàm format (`fmtTime`, `fmtDateTime`, `fmtDate`) vì cùng nguồn dữ liệu.

## Áp dụng lại (How to reuse)

- Khi thấy `NaN` trong hiển thị thời gian frontend nhận từ backend Python → nghi ngờ ngay microseconds 6 chữ số
- Bất kỳ project nào mix Python backend + JS/TS frontend: **luôn normalize timestamp** tại lớp utility trước khi dùng `new Date()`
- Thêm `normalizeIso()` vào `format.ts` (hoặc tương đương) ngay khi setup project, không đợi gặp lỗi
- Kiểm tra nhanh: mở DevTools console, chạy `new Date(timestamp_thực_từ_api).getTime()` → nếu `NaN` → cần normalize

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Mock data dùng JS `new Date().toISOString()` (Z + 3 digits) → test với mock luôn pass, bug chỉ lộ khi kết nối backend thật
- ⚠️ Session rất mới (< vài giây) không bị ảnh hưởng nếu backend dùng `datetime.now()` không có microseconds đáng kể (microseconds = 000000 → truncate không đổi gì), che giấu thêm bug
- ⚠️ `diff < 0` có thể xảy ra nếu đồng hồ client/server lệch nhau → nên thêm `Math.max(0, diff)` nếu cần hiển thị "vừa xong" cho diff âm nhỏ
- ⚠️ Python `datetime.isoformat()` trên naive datetime (không timezone) tạo ra `"2026-08-06T08:30:00.123456"` (không có `+00:00`) — normalizeIso vẫn xử lý đúng (chỉ truncate microseconds, không đổi suffix)

## Tham chiếu

- ECMAScript spec: Date Time String Format — https://tc39.es/ecma262/#sec-date-time-string-format
- Python docs: `datetime.isoformat()` — https://docs.python.org/3/library/datetime.html#datetime.datetime.isoformat
- Project liên quan: agent-dashboard (tools/agent-dashboard/frontend/src/utils/format.ts)
