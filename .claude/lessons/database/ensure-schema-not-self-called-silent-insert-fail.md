---
category: database
tags: [ensure-schema, sql-server, silent-exception, winforms, migration-table-missing]
severity: high
created: 2026-08-24
updated: 2026-08-24
project-origin: DoorAlarmv3 (v3)
---

# EnsureSchema() không tự gọi trong bảng mới → INSERT thất bại im lặng

## Tình huống gặp phải

> Project WinForms DoorAlarmv3 (v3), dùng thư viện dùng chung `Kztek.Database.MDB`
> (`0.BaseLIB/Kztek.Database`). Màn "Cài đặt hệ thống" > Bản đồ: user bấm "Lưu" để
> thêm mới 1 Map (tên + ảnh nền) nhưng báo lỗi "Thêm mới không thành công!" mặc dù
> các bảng khác (Thiết bị, Nhóm, BĐK...) vẫn hoạt động bình thường.

## Triệu chứng / Lỗi

```
MessageBox: "Thêm mới không thành công!" (tblMap.AddMap trả về false)
Không có exception nào xuất hiện, không có log — vì thư viện MDB dùng
catch (Exception ex) { /* nothing, log bị comment out */ } trong ExecuteCommand().
```

## Nguyên nhân gốc rễ (Root Cause)

`DatabaseService.CreateDatabase()` (nơi tập trung gọi `EnsureSchema()` cho tất cả
bảng khi khởi tạo DB) đã bị vô hiệu hóa — toàn bộ thân hàm bị comment, chỉ còn
`return true;`. Trong khi đó `tblMap.cs` (AddMap/UpdateMap/GetAll) **không tự gọi
`EnsureSchema()`** trong từng hàm — khác với `tblMapDetail.cs` cùng project đã có
sẵn pattern tự gọi `EnsureSchema()` ở đầu mọi hàm public (self-healing schema).

Kết quả: nếu bảng `tblMap` chưa từng được tạo trong DB (tính năng Map mới hơn các
bảng khác, DB cũ chưa có bảng này), lệnh INSERT ném SQL exception ("Invalid object
name 'tblMap'") — nhưng exception bị nuốt im lặng trong `MDB.ExecuteCommand()`
(catch rỗng, dòng log bị comment) → hàm trả `false` → UI chỉ hiện thông báo chung
chung "Thêm mới không thành công!", không có gợi ý nguyên nhân thật.

## Giải pháp

```csharp
public static bool AddMap(Map map, out string mapId)
{
    EnsureSchema();   // <-- thêm dòng này, giống pattern tblMapDetail.cs
    mapId = string.Empty;
    ...
}
```

1. Thêm `EnsureSchema();` vào đầu mọi hàm public thao tác DB của bảng (GetAll,
   AddXxx, UpdateXxx) — không phụ thuộc vào 1 điểm khởi tạo tập trung
   (`DatabaseService.CreateDatabase()`) vì điểm đó có thể bị vô hiệu hóa/refactor
   sau này mà không ai để ý các bảng con còn phụ thuộc vào nó.
2. KHÔNG cần thêm vào `DeleteMap` — xóa trên bảng chưa tồn tại vốn dĩ là no-op,
   không phải lỗi thật.
3. Build lại (`dotnet build`) để xác nhận không phá vỡ gì khác.

## Áp dụng lại (How to reuse)

- Khi thấy 1 class `tblXxx.cs` có hàm `EnsureSchema()` nhưng các hàm Add/Update/Get
  không tự gọi nó → kiểm tra ngay xem có điểm khởi tạo tập trung (`CreateDatabase()`,
  `InitDb()`...) có đang bị disable/comment không. Nếu có → bảng đó có nguy cơ
  "silent fail" y hệt.
- Khi 1 tính năng DB mới báo "thêm/sửa không thành công" mà KHÔNG có exception/log
  cụ thể nào → nghi ngờ đầu tiên là bảng/cột chưa tồn tại (schema chưa EnsureSchema)
  trước khi nghi ngờ logic nghiệp vụ.
- Grep nhanh: `grep -rn "EnsureSchema" Databases/` rồi so sánh class nào tự gọi
  trong hàm public (an toàn) và class nào chỉ định nghĩa hàm nhưng không ai gọi
  (rủi ro) — nếu điểm khởi tạo tập trung bị comment.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Thư viện dùng chung `Kztek.Database.MDB.ExecuteCommand()` nuốt MỌI exception
  im lặng (catch rỗng, dòng `SaveLogFile`/`MessageBox` đều bị comment) — đây là
  cạm bẫy có tính hệ thống trên MỌI project dùng thư viện này (không riêng
  DoorAlarmv3). Khi debug "insert/update fail không rõ lý do" trên bất kỳ project
  nào dùng `Kztek.Database.MDB`, đừng trông chờ log — phải tự chạy SQL bằng tay
  hoặc tạm thời sửa MDB để bật log khi debug.
- ⚠️ Đừng vội bật lại `DatabaseService.CreateDatabase()` (uncomment toàn bộ) khi
  chưa hiểu tại sao nó bị tắt trước đó — có thể là chủ ý (tránh check schema mỗi
  lần login gây chậm) — cách an toàn hơn là tự-heal ở từng bảng như đã làm.

## Tham chiếu

- File sửa: `DoorAlarmv3/Databases/tblMap.cs`
- Pattern tham chiếu: `DoorAlarmv3/Databases/tblMapDetail.cs`
- Điểm bị vô hiệu hóa: `DoorAlarmv3/Databases/DatabaseService.cs` (`CreateDatabase()`)
- Project liên quan: DoorAlarmv3 v3 (WinForms .NET 8)
