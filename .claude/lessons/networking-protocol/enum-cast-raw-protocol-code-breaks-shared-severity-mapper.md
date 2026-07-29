---
category: networking-protocol
tags: [enum-cast, access-control, event-severity, zkteco, e02, e05, elv485, code-smell]
severity: high
created: 2026-07-29
updated: 2026-07-29
project-origin: App-Access-V2 (iAccessDesktopv2 / iAccessDesktopv2.Avalonia)
---

# Ép raw code giao thức thiết bị vào enum app-wide (`EmTypeEvent`) làm sai severity UI ở nơi khác không liên quan

## Tình huống gặp phải

Đang kiểm tra logic controller thiết bị chấm công/kiểm soát vào ra (E02Net, E05Net, ELV485 —
cả bản legacy WinForms lẫn bản port Avalonia). Dòng code:

```csharp
log.Event = (EmTypeEvent)(log.Pin == 0 ? 1 : 27); // E02
log.Event = (EmTypeEvent)(isAccessGrantEvent ? 1 : 27); // E05, ELV485
```

`EmTypeEvent` (Kztek.Object.Entity/Enums/ZktecoV5L.cs) chỉ có 2 giá trị: `Deny=0, Grant=1`.
Nhưng code ép kiểu (cast) raw code của giao thức thiết bị gốc (1 = "thẻ lạ"/"granted" tuỳ
controller, 27 = "hợp lệ"/"denied") thẳng vào enum này — trong khi `EmTypeEvent.Grant=1` lại
trùng SỐ với code raw "1" của protocol nhưng KHÁC Ý NGHĨA hoàn toàn tuỳ controller.

## Triệu chứng / Lỗi

Không lộ ra lúc build (build sạch), không crash. Chỉ phát hiện khi truy vết
`EventSeverityMapper.FromTypeEvent(int)` (thêm sau, ở STEP-8.5, cùng ngày) — hàm này được
`MainViewModel.cs:230` gọi trực tiếp `(int)log.Event` để tô màu severity trên UI realtime:
`1 → Normal(xanh)`, `0 → Warning`, còn lại → `Normal` (mặc định, tránh báo động giả).

Hệ quả thật: **thẻ lạ** ở E02 (`Pin==0`, đáng lẽ Deny) bị encode = 1 → UI hiển thị **Normal**
như thể granted bình thường. Sự kiện **bị từ chối** ở E05/ELV485 bị encode = 27 → rơi vào
nhánh mặc định → cũng hiển thị **Normal** thay vì Warning.

## Nguyên nhân gốc rễ (Root Cause)

Khi migrate/port, các controller này đã "giữ nguyên parity nguồn" (comment `// parity E02:137`)
kể cả phần raw magic number 1/27 vốn chỉ có ý nghĩa trong ngữ cảnh phản hồi text của từng giao
thức thiết bị (không phải index chuẩn của app). Field `LogEventVerify.Event` lại được TYPE
CỨNG là `EmTypeEvent` (chỉ 2 giá trị hợp lệ) — ép một domain giá trị khác (raw protocol code)
vào domain enum 2 giá trị là type-abuse: compiler không cảnh báo (enum không có `[Flags]`,
không validate range khi cast), nhưng downstream code khác (severity mapper, status string
"granted"/"denied" ở `ZktecoPushEventHandler.cs`, DB/RabbitMQ payload) đều giả định
`Event` LUÔN là Grant/Deny thật — chỉ 2 controller (E02, E05, ELV485) làm khác so với
E32/ESD/FSF2/Q2i (dùng đúng `EmTypeEvent.Grant`/`EmTypeEvent.Deny`).

Rủi ro này ĐÃ được ghi nhận lúc migrate (`STEP-3.4-port-elv485.md`, `STEP-4.2-migrator-review.md`)
nhưng bị đánh giá thấp: "chỉ ảnh hưởng UI grid hiển thị ToString() (hiện số thay vì tên) —
KHÔNG ảnh hưởng RabbitMQ/DB". Đánh giá đó đúng tại THỜI ĐIỂM ghi (chưa có severity mapper).
`EventSeverityMapper` ra đời SAU (cùng ngày, STEP-8.5) và đọc trực tiếp raw int này — biến rủi
ro "cosmetic" thành bug hiển thị sai mức độ nghiêm trọng thật.

## Giải pháp

```csharp
// Trước (raw code, sai domain enum)
log.Event = (EmTypeEvent)(log.Pin == 0 ? 1 : 27);

// Sau (đúng semantic Grant/Deny, khớp pattern E32/ESD/FSF2/Q2i)
log.Event = log.Pin == 0 ? EmTypeEvent.Deny : EmTypeEvent.Grant;
```

1. Xác định lại Ý NGHĨA THẬT (grant hay deny) của từng nhánh, KHÔNG dựa vào số raw của protocol.
2. Gán thẳng bằng tên enum (`EmTypeEvent.Grant`/`.Deny`), không cast số nguyên.
3. Sửa đồng bộ cả 2 bản (legacy `iAccessDesktopv2.Controller` VÀ Avalonia port) — bug tồn tại
   song song ở cả 2 vì port giữ parity với legacy có sẵn bug.
4. Grep toàn repo `(EmTypeEvent)\(` để tìm hết các chỗ cast trực tiếp còn sót (không chỉ chỗ
   đang sửa) — bug lặp ở 3 controller khác nhau (E02, E05, ELV485), tổng 6 vị trí (3 legacy + 3 Avalonia).

## Áp dụng lại (How to reuse)

- Khi thấy `(EnumName)(someCondition ? rawA : rawB)` với `rawA/rawB` là con số không khớp giá
  trị enum liệt kê (hoặc trùng số nhưng bối cảnh khác) → dừng lại, tra domain thật của enum đó
  trước khi tin comment "parity nguồn".
- Trước khi chấp nhận 1 rủi ro migrate là "chỉ ảnh hưởng cosmetic/display" → kiểm tra xem có
  downstream consumer nào (mapper, converter, status-string) đọc TRỰC TIẾP giá trị int/enum đó
  không, và liệu tương lai gần (cùng plan, sprint) có thêm consumer mới không (ở đây:
  EventSeverityMapper thêm CÙNG NGÀY, khiến đánh giá "an toàn" hết hiệu lực gần như ngay lập tức).
- Field typed là enum 2 giá trị (`Deny`/`Grant`) thì KHÔNG BAO GIỜ cast raw protocol code vào
  nó — nếu cần giữ raw code cho mục đích khác (severity 3 mức tương lai), thêm field riêng
  (`RawEventCode`) thay vì lạm dụng field domain hiện có.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Giá trị enum trùng SỐ (`EmTypeEvent.Grant == 1`) với 1 raw code protocol không có nghĩa
  chúng CÙNG Ý NGHĨA — dễ nhầm lẫn nguy hiểm vì code compile được, chạy được, chỉ sai kết quả.
- ⚠️ Đánh giá rủi ro migrate ("chấp nhận được") có thể hết hạn NGAY khi codebase thêm 1 consumer
  mới đọc field đó — không có gì đảm bảo rủi ro cosmetic sẽ mãi cosmetic.
- ⚠️ Bug loại này thường LẶP LẠI ở nhiều controller cùng họ (E02/E05/ELV485 cùng pattern parity)
  — sửa 1 chỗ phải grep tìm hết các chỗ anh em.

## Tham chiếu

- `docs/plans/PLAN-devicehost-kztek-2026-07-27/steps/STEP-3.4-port-elv485.md` (D2)
- `docs/plans/PLAN-devicehost-kztek-2026-07-27/steps/STEP-4.2-migrator-review.md`
- `docs/plans/PLAN-migrate-avalonia-2026-07-26/steps/STEP-8.5-main-events-redesign.md`
- Project liên quan: App-Access-V2 (KZTEK iAccess v2)
