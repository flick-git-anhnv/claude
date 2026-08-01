# Workflow tool: tham số `args` bị serialize thành string, không tự parse thành object

**Ngày phát hiện:** 2026-07-31
**Ngữ cảnh:** Project EnglishTool (LangTool) — chạy Workflow đa-agent sinh từ vựng mới, truyền cấu hình (đường dẫn file, số từ cần sinh...) qua tham số `args`.

## Vấn đề

Gọi `Workflow` với `args` là một object JSON lồng nhau (`{"en":{"packs":{...}}}`) được gõ trực tiếp làm giá trị tham số `args` trong lời gọi tool. Script bên trong truy cập `args.en.packs` → workflow fail ngay lập tức (0 agent chạy, ~25ms):

```
Error: undefined is not an object (evaluating 'args.en.packs')
```

Log lỗi trả về từ hệ thống cho thấy `args` thực chất được truyền dưới dạng **chuỗi JSON đã escape** (`args: "{\"en\":{...}}"`), không phải object thật — nên `args.en` là `undefined` (string không có property `.en`).

## Nguyên nhân

Tool Workflow ghi rõ: *"Pass arrays/objects as actual JSON values in the tool call, NOT as a JSON-encoded string"* — nhưng khi gõ JSON trực tiếp làm nội dung tham số trong lời gọi tool (không có cách nào tường minh để "đánh dấu kiểu object" khác với text thường), hệ thống vẫn coi đó là chuỗi text và KHÔNG tự parse thành object trước khi gán vào biến `args` trong script.

## Fix

Không dùng `args` cho cấu hình phức tạp. Thay vào đó, nhúng cấu hình trực tiếp thành 1 object JS literal (`const CONFIG = {...}`) ngay trong thân script Workflow — script body (khác với `meta`) được phép chứa bất kỳ JS hợp lệ nào, kể cả object literal lồng sâu. Chỉ `export const meta = {...}` mới bắt buộc là pure literal không biến/hàm.

```js
// SAI — dựa vào args để truyền cấu hình phức tạp
const enPackKeys = Object.keys(args.en.packs); // args.en undefined nếu bị serialize thành string

// ĐÚNG — nhúng thẳng object literal trong script body
const CONFIG = { en: { packs: { A: {...}, B: {...}, C: {...} } }, jp: {...}, zh: {...} };
const enPackKeys = Object.keys(CONFIG.en.packs);
```

## Cách nhận biết nhanh lần sau

- Workflow fail gần như ngay lập tức (duration ~vài chục ms, `agent_count: 0`) → khả năng cao là lỗi cú pháp/tham chiếu trong script TRƯỚC khi agent đầu tiên kịp chạy, không phải lỗi từ subagent.
- Đọc kỹ nội dung `<recovery>` trong task-notification: nếu thấy `args: "{\"...\":..."}"` (chuỗi có dấu escape `\"`) thay vì object thật — đó là bằng chứng `args` đã bị stringify.

## Khi nào vẫn nên dùng `args`

Dùng `args` khi giá trị đơn giản (string ngắn, số, mảng string phẳng) và không có gì để lo về serialize — rủi ro chỉ rõ rệt khi cấu trúc lồng sâu nhiều cấp. Để chắc chắn nhất, ưu tiên nhúng object cấu hình trực tiếp trong script thay vì qua `args` bất cứ khi nào có thể.
