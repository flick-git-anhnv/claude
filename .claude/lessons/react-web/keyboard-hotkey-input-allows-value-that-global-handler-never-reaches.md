---
category: ui-patterns
tags: [react, keyboard-shortcut, ux, input-validation, hotkey, dead-config]
severity: medium
created: 2026-08-05
updated: 2026-08-05
project-origin: Roboflow - Copy (KZTEK Labeling Studio)
---

# Ô nhập "phím tắt tuỳ chỉnh" cho phép lưu giá trị mà global keydown handler KHÔNG BAO GIỜ khớp tới

## Tình huống gặp phải

> Đang làm gì? Tính năng gì? Môi trường nào?

`AnnotatorPage.tsx` có 1 global `keydown` handler xử lý NHIỀU lớp phím tắt theo thứ tự
ưu tiên cứng: (1) `Ctrl+K`, (2) `Ctrl+Z/Y/C/V`, (3) `Escape`/`Delete`, (4) **phím số
1-9 → chọn nhãn theo MRU (nhãn dùng gần nhất)** — nhánh này `return` ngay khi khớp,
(5) phím chữ a-z → buffer 1-2 ký tự so khớp với `class.hotkey` do user tự đặt trong
panel "NHÃN (Classes)" (`ProjectDetailPage.tsx`, `<input className="hotkey-input">`).

Ô input hotkey đó là `<input type="text" maxLength={2}>` — **không có validation gì**,
cho phép gõ bất kỳ ký tự nào kể cả chữ số.

## Triệu chứng / Lỗi

User báo "lỗi ko gắn được label khi bấm phím rồi" — đã vào panel NHÃN, gõ `"1"`, `"2"`,
... `"9"` làm phím tắt cho từng nhãn (rất trực quan: nhãn thứ N ↔ phím N), lưu thành công
(không có cảnh báo gì), nhưng khi vào Annotator bấm đúng phím đó thì **hoàn toàn không có
tác dụng gì** — không đổi nhãn cho box đang chọn, không có lỗi console.

## Nguyên nhân gốc rễ (Root Cause)

Nhánh xử lý phím số trong keydown handler nằm **TRƯỚC** và **return ngay** khi khớp
`e.key >= '1' && e.key <= '9'` — không bao giờ đi tiếp tới đoạn so khớp
`classes.find(c => c.hotkey === buf)`:

```ts
if (e.key >= '1' && e.key <= '9') {
  const classId = mruClassIds[Number(e.key) - 1];   // theo VỊ TRÍ trong MRU, không phải hotkey field
  if (classId) assignClassToSelected(classId);
  return;                                            // ⛔ không bao giờ chạm tới nhánh hotkey chữ bên dưới
}
if (e.key.length === 1 && /[a-zA-Z]/.test(e.key)) {  // chỉ nhận CHỮ — số không lọt vào đây
  ...
}
```

Vì vậy **bất kỳ `class.hotkey` nào chỉ gồm chữ số** — dù lưu thành công trong DB, dù
hiển thị đúng trên UI (`<span className="key custom">{c.hotkey}</span>`) — đều là
**cấu hình chết (dead config)**: không phím vật lý nào có thể kích hoạt nó, vì phím số
luôn bị nhánh MRU "chặn đường" trước.

Đây KHÔNG phải bug logic trong keydown handler (thứ tự ưu tiên đó là chủ đích thiết
kế — "Phím 1-9 = 9 class dùng gần nhất (MRU)" đã ghi rõ trong UI hint) — bug thật sự
nằm ở **ô nhập liệu không validate**, tạo ảo giác (affordance giả) rằng gõ số vào đó
sẽ có tác dụng.

## Giải pháp

1. **Chặn tại input (client, UX ngay lập tức):** `onBlur` của ô hotkey, nếu giá trị
   chỉ gồm chữ số → `alert()` giải thích lý do + revert về giá trị cũ, KHÔNG gọi API
   lưu:
   ```ts
   if (v && /^[0-9]+$/.test(v)) {
     alert('Không thể dùng số làm phím tắt — phím 1-9 luôn dành cho "chọn nhãn dùng gần nhất" (MRU). Hãy dùng chữ cái, ví dụ: a, b, cd.');
     e.target.value = cls.hotkey || '';
     return;
   }
   ```
2. **Chặn tại server (defense in depth — phòng trường hợp gọi API trực tiếp, không
   qua UI):** `normalizeHotkey()` trong route `classes.js` trả `null` nếu giá trị chỉ
   gồm chữ số, thay vì lưu nguyên văn.
3. **Dọn dữ liệu cũ:** các class đã lỡ lưu hotkey dạng số (từ trước khi có validation)
   vẫn nằm trong DB, hiển thị trên UI như bình thường nhưng vĩnh viễn không dùng được
   — cần rà + `PATCH hotkey: null` thủ công cho các class đó (không có migration tự
   động dọn, vì hotkey là dữ liệu do user tự đặt, không nên tự ý xoá hàng loạt mà không
   soát qua).

## Áp dụng lại (How to reuse)

- Bất kỳ hệ thống có **nhiều lớp phím tắt xử lý theo thứ tự ưu tiên** (global hotkey +
  hotkey per-item do user tự cấu hình) → PHẢI đảm bảo **ô cấu hình hotkey validate
  ngay tại input**, chặn mọi giá trị trùng với dải phím đã bị lớp ưu tiên cao hơn
  "chiếm" vĩnh viễn — không thể dựa vào tài liệu/hint text để user tự tránh.
- Dấu hiệu cần rà: tìm mọi nhánh `return`/`break` sớm trong global key handler (ưu
  tiên cao) → liệt kê chính xác tập ký tự nó "chiếm dụng" → đối chiếu với input nào
  cho phép user gõ tự do vào đúng tập ký tự đó.
- Khi user báo "đã set nhưng bấm không có tác dụng" đối với MỘT tính năng có phím tắt
  tuỳ chỉnh + phím tắt hệ thống cùng tồn tại → nghi ngay khả năng va chạm dải phím,
  đừng chỉ kiểm tra logic so khớp hotkey của riêng tính năng đó.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Bug này **im lặng ở CẢ 2 đầu**: lưu thành công (không lỗi), bấm phím cũng không
  lỗi console — chỉ biểu hiện qua "không có chuyện gì xảy ra", cực khó tự phát hiện
  nếu không biết trước tập phím bị lớp ưu tiên cao hơn chiếm.
- ⚠️ `maxLength={2}` trên input hotkey không ngăn được gì về NỘI DUNG ký tự — chỉ giới
  hạn độ dài. Validate độ dài và validate nội dung là 2 việc khác nhau, dễ tưởng đã
  đủ khi chỉ làm 1 trong 2.
- ⚠️ Đây có thể chính là dữ liệu do CHÍNH mình tạo ra lúc test thủ công trước đó (gõ
  "1".."9" làm hotkey vì tiện, không để ý trùng MRU) — khi audit dữ liệu nghi vấn,
  đừng mặc định đó luôn là do user thật tạo ra.

## Tham chiếu

- Project liên quan: KZTEK Labeling Studio
  (`client/src/pages/ProjectDetailPage.tsx` — ô `.hotkey-input`;
  `server/src/routes/classes.js` — `normalizeHotkey()`;
  `client/src/pages/AnnotatorPage.tsx` — nhánh `e.key >= '1' && e.key <= '9'`)
