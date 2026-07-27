---
category: avalonia
tags: [config, newtonsoft-json, migration, winforms-parity, deserialization]
severity: critical
created: 2026-07-21
updated: 2026-07-21
project-origin: iPGSv4 (migrate-ipgs-kiosk-avalonia)
---

# Config model port từ WinForms bị rỗng vì tên field JSON không khớp (dù file config.txt dùng chung)

## Tình huống gặp phải

Migrate `IPGS.Kiosk` (WinForms) → `IPGS.Kiosk.Avalonia`. Cấu hình kết nối (Parking API, RabbitMQ,
PGS DB, Controller, QR/Visa) được lưu tại `{AppRoot}/config/config.txt` (JSON), và file này được
**chia sẻ/copy trực tiếp** từ máy production WinForms sang Avalonia để test — không phải file mẫu tự tạo.

## Triệu chứng / Lỗi

Sau khi copy `config.txt` thật từ bản WinForms production, chạy Avalonia app: toàn bộ ô "Tên đăng
nhập SQL", "Mật khẩu SQL", "Tên database" trong màn Cấu hình kết nối RỖNG, ứng dụng không kết nối
được SQL. Debug thấy object `KioskAppConfig` sau `DeserializeObjectFromPath` có các field liên quan
DB đều `string.Empty` dù file JSON có dữ liệu thật. Đồng thời dropdown "Loại bộ điều khiển" cũng rỗng
dù JSON có giá trị.

## Nguyên nhân gốc rễ (Root Cause)

Khi tạo lớp `KioskAppConfig` (POCO thuần, không phụ thuộc WinForms) cho Avalonia, agent đặt tên
property theo convention "đẹp" (`DbServer`, `DbUsername`, `RabbitMqHost`, `QrMethod`...) thay vì copy
NGUYÊN VĂN tên field của class gốc `PaymentKioskConfig` (IPGS.Object, dùng bởi
`frmConnectionConfig.cs`). Nhưng `config.txt` là file JSON DÙNG CHUNG giữa 2 bản (không phải file mới
sinh ra từ Avalonia) nên khoá JSON vẫn là tên gốc: `PGSDbServer`, `PGSDbUsername`, `PGSDbPassword`,
`PGSDbDbName`, `RabbitMQUrl`, `PasskingPassword` (lỗi chính tả CÓ CHỦ Ý trong code gốc, không phải
typo cần sửa), `ControllerComunication` (thiếu chữ "m", cũng là "lỗi" gốc phải giữ nguyên).
Newtonsoft.Json mặc định khớp tên case-insensitive nhưng KHÔNG suy luận được ánh xạ tên khác hẳn nhau
(`PGSDbServer` ≠ `DbServer`) → property giữ nguyên giá trị default (rỗng).

Ngoài ra một số field gốc là **enum serialize dạng số nguyên ordinal** trong JSON
(`CardFormat`, `CardFormatOption`, `ControllerType`, `QRMethod`) vì code gốc gán thẳng
`(int)cbControllerType.SelectedIndex` khi Save — nhưng model Avalonia định nghĩa các field này là
`string` với default text ("KZE02", "HEXA"...). Newtonsoft đọc số nguyên vào field string vẫn "chạy"
(convert bằng ToString()) nhưng cho ra chuỗi số ("0", "5"...) không khớp bất kỳ item nào trong
ComboBox (Items là danh sách tên enum: "KZE02","QR500"...) → dropdown hiển thị rỗng dù có giá trị.

## Giải pháp

1. Thêm `[JsonProperty("TenGocTrongFileJson")]` (Newtonsoft.Json) lên từng property có tên khác với
   field gốc, để đọc đúng file config chia sẻ mà KHÔNG cần đổi tên property C# (giữ tên đẹp cho code
   Avalonia).
2. Với field vốn là enum ở bản gốc: giữ kiểu `int` (ordinal) trong model JSON, KHÔNG chuyển thành
   `string` trong model — chỉ chuyển đổi ordinal ↔ label hiển thị ở tầng ViewModel (`Load()`/`Save()`)
   bằng bảng tra cứu (`string[]` theo đúng thứ tự khai báo enum gốc), không phải trong model.

```csharp
[JsonProperty("PGSDbServer")]
public string DbServer { get; set; } = string.Empty;

[JsonProperty("QRMethod")]
public int QrMethod { get; set; } = 1; // ordinal, không phải string

// ViewModel.Load():
QrMethod = OrdinalToLabel(QrMethodLabels, cfg.QrMethod, "VIMO_QR_CODE");
// ViewModel.Save():
QrMethod = LabelToOrdinal(QrMethodLabels, QrMethod, 1),
```

3. LUÔN lấy đúng thứ tự khai báo enum gốc (Grep trực tiếp file `.cs` định nghĩa `enum Em...`) để dựng
   bảng label — sai thứ tự sẽ chọn nhầm option dù không lỗi biên dịch.

## Áp dụng lại (How to reuse)

- Khi port 1 config/DTO class từ WinForms sang Avalonia mà FILE DỮ LIỆU (JSON/XML/ini) được
  DÙNG CHUNG với bản gốc (không phải file mới) → PHẢI đối chiếu tên field JSON thực tế (đọc file mẫu
  thật hoặc code Save() gốc) chứ không suy đoán theo convention đẹp. Không tin tưởng property tên
  "hợp lý" là đúng.
- Khi thấy field nào trong config gốc được gán bằng `(int)enumValue` hoặc `(EnumType)someIndex` khi
  Save, hoặc đọc bằng `cbXxx.SelectedIndex = (int)cfg.Field` khi Load → đó là field serialize dạng
  ordinal int, KHÔNG phải string — giữ int trong model, quy đổi label ở ViewModel.
- Sau khi sửa mapping, kiểm tra bằng cách đọc lại chính file config.txt thật (không phải file tự tạo)
  và log/breakpoint xem field có load đúng không, đừng chỉ test với file JSON mẫu tự viết (dễ tự khớp
  nhầm với chính tên property mới).

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Các "lỗi chính tả" trong tên gốc (`PasskingPassword`, `ControllerComunication`) PHẢI giữ nguyên
  trong `[JsonProperty]` — đây là tên khoá JSON thật trong file production, sửa "cho đúng chính tả"
  sẽ làm mất khả năng đọc file cấu hình hiện có.
- ⚠️ Newtonsoft.Json convert ngầm int → string mà KHÔNG throw lỗi — khiến bug này rất khó phát hiện
  qua log/exception, chỉ lộ ra khi so sánh UI thực tế với giá trị mong đợi.

## Tham chiếu

- `IPGS.Kiosk/Forms/frmConnectionConfig.cs` (dòng ~127-166, ~266-291) — nguồn tên field + cơ chế
  enum→ordinal gốc.
- `IPGS.Kiosk.Avalonia/Models/KioskAppConfig.cs`, `Views/ConnectionConfig/ConnectionConfigViewModel.cs`
  — bản đã fix.
- Project liên quan: iPGSv4 (migrate-ipgs-kiosk-avalonia)
