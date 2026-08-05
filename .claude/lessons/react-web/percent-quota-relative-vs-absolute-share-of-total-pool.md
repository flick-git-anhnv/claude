---
category: react-web
tags: [percent, quota, distribution, allocation, algorithm-design, self-caught]
severity: high
created: 2026-08-05
updated: 2026-08-05
project-origin: Roboflow - Copy (KZTEK Labeling Studio)
---

# Chia % công việc cho nhiều user — % phải là tỉ lệ TUYỆT ĐỐI trên tổng, không phải TƯƠNG ĐỐI giữa các user đã cấu hình

## Tình huống gặp phải

Xây tính năng "Phân công công việc" (admin giao User A 50%, User B 30%, User
C 20% số ảnh trong project). User yêu cầu rõ: "Cho phép tự do, không bắt buộc
= 100%" — admin có thể chỉ gán 80%, để dư 20% ảnh chưa ai nhận.

## Lỗi (tự phát hiện khi viết Playwright test verify tính năng của chính mình)

Bản đầu tiên implement:
```js
const totalPercent = percents.reduce((s, p) => s + p.percent, 0);
const quotas = percents.map((p) => ({
  user_id: p.user_id,
  base: Math.floor((p.percent / totalPercent) * unassignedPool.length), // ❌ chia theo tỉ lệ TƯƠNG ĐỐI
}));
```
Test: đặt CHỈ 1 user duy nhất percent=30 (trong project 10 ảnh, kỳ vọng
user đó nhận đúng 3 ảnh, còn 7 ảnh phải để trống theo đúng yêu cầu "cho phép
tự do"). Kết quả thực tế: user đó nhận **10/10 ảnh** — vì `totalPercent` lúc
đó = 30 (chỉ tính user này), nên `30/30 = 100%` → nhận trọn vẹn pool. Giá trị
tuyệt đối của % (30 so với 100) hoàn toàn không có ý nghĩa gì trong công thức
— chỉ có tỉ lệ SO VỚI CÁC USER KHÁC ĐANG ĐƯỢC CẤU HÌNH mới quyết định kết quả.

## Nguyên nhân gốc rễ (Root Cause)

Nhầm lẫn giữa 2 ngữ nghĩa khác nhau của "%":
1. **% tương đối** (chia theo trọng số giữa những người tham gia) — đúng cho
   bài toán "chia đều theo tỉ lệ ưu tiên" khi TỔNG luôn phải dùng hết (VD:
   chia bánh giữa N người theo khẩu phần).
2. **% tuyệt đối** (target = mục tiêu cố định trên TỔNG pool, độc lập với
   người khác) — đúng cho bài toán "giao chỉ tiêu KPI/khối lượng công việc",
   nơi KHÔNG bắt buộc dùng hết 100% và mỗi người có 1 con số mục tiêu độc lập.

Yêu cầu "cho phép tự do, không bắt buộc = 100%" là dấu hiệu RÕ RÀNG của ngữ
nghĩa (2) — nhưng code viết theo công thức của ngữ nghĩa (1), nên khi tổng %
đã cấu hình < 100 (trường hợp NGƯỜI DÙNG THỰC TẾ SẼ LÀM, vì đó chính là tính
năng được yêu cầu), công thức tự động "co giãn" phần trăm lên thành 100% của
riêng nhóm đã cấu hình — hành vi hoàn toàn trái với ý định.

## Giải pháp

Đổi công thức: `target = round(percent/100 * TOTAL_POOL)` (percent tuyệt đối
trên **tổng toàn bộ pool**, không phải tổng percent đã cấu hình), sau đó
`need = max(0, target - đã_có)` — chỉ "top-up" phần còn thiếu, lấy ngẫu nhiên
từ pool chưa gán. Nếu tổng `need` của mọi người < pool còn lại → phần dư mãi
mãi không ai đạt target, TỰ NHIÊN nằm ngoài phân công (đúng ý "cho phép tự
do"). Nếu tổng `need` > pool còn lại (percent cấu hình vượt 100% hoặc pool
nhỏ hơn dự kiến) → dùng largest-remainder method để chia phần còn lại công
bằng theo đúng tỉ lệ nhu cầu tương đối (ở bước NÀY dùng % tương đối là ĐÚNG,
vì đây là bài toán "chia phần khan hiếm" thực sự, không phải bài toán gốc).

## Áp dụng lại (How to reuse)

- Bất kỳ tính năng nào cho phép nhập "%" cho nhiều đối tượng độc lập (quota,
  KPI, phân công, giới hạn ngân sách theo phòng ban...) — trước khi viết công
  thức, hỏi rõ: **"Nếu chỉ 1 đối tượng có % > 0, họ có nhận TRỌN VẸN 100% pool
  không, hay chỉ nhận ĐÚNG BẰNG % đã ghi?"** Câu trả lời quyết định dùng công
  thức (1) hay (2) — đừng suy luận từ tên biến "percent" mà bỏ qua ngữ cảnh.
- Dấu hiệu ngôn ngữ cần bắt: "cho phép để dư/chưa gán", "không bắt buộc tổng
  = 100%", "mỗi người 1 chỉ tiêu độc lập" → LUÔN là % tuyệt đối (2), không
  phải % tương đối (1).
- Cách tự phát hiện lỗi này SỚM: viết đúng 1 test case "CHỈ 1 đối tượng có %
  bất kỳ (không phải 100)" — nếu % tuyệt đối, họ phải nhận ĐÚNG số lượng ứng
  với % đó (không phải toàn bộ pool). Đây là test case rẻ nhất để lộ ra nhầm
  lẫn (1) vs (2) — không cần setup nhiều user để thấy bug.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Bug này KHÔNG lộ ra nếu test case đầu tiên luôn dùng ≥2 user với tổng =
  100% (VD 50/30/20) — công thức (1) và (2) cho ra KẾT QUẢ GIỐNG HỆT NHAU khi
  tổng % đúng 100. Chỉ lộ ra khi tổng % ≠ 100 hoặc chỉ có 1 người — đúng
  những case mà tính năng NÀY được thiết kế để hỗ trợ, nên nhất định phải test
  riêng, không suy ra an toàn từ test case "đẹp".
- ⚠️ Vẫn cần công thức (1) (tương đối) làm bước OVERFLOW-HANDLING phụ khi
  tổng nhu cầu vượt pool khả dụng — không phải lúc nào cũng loại bỏ hoàn
  toàn, chỉ là không dùng nó làm công thức CHÍNH.

## Tham chiếu

- Project liên quan: KZTEK Labeling Studio
  (`server/src/routes/assignments.js` — endpoint `POST .../distribute`)
