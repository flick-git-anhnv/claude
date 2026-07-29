---
category: database
tags: [sqlite, migration, alter-table, outbox-pattern, silent-skip]
severity: high
created: 2026-07-28
updated: 2026-07-28
project-origin: App-Access-V2 (iAccessDesktopv2.Avalonia)
---

# Thêm cột mới vào bảng SQLite: `CreateTable()` chỉ chạy khi DB CHƯA tồn tại — DB cũ không bao giờ được migrate nếu gọi sai chỗ

## Tình huống gặp phải

Đang đổi `TblEvent` (SQLite local, `_database.db`) từ "gửi event lên server ngay trong
đường nhận event, không lưu trước" sang outbox pattern (nhận → lưu DB local → hiển thị
→ polling đẩy server tuần tự) theo yêu cầu USER, để không mất event khi app tắt/mất
mạng. Cần thêm 2 cột mới: `Synced INTEGER DEFAULT 0` + `RawLogJson TEXT`.

## Triệu chứng / Lỗi

Thêm logic `ALTER TABLE Event ADD COLUMN ...` vào trong `TblEvent.CreateTable()` —
tưởng là xong, nhưng suýt bỏ sót: `SqliteHelper` ctor
(`iAccess.Core/Data/SqliteHelper.cs`) chỉ gọi `TblEvent.CreateTable()` (cùng 3 bảng
khác) **bên trong khối `if (!File.Exists(_databasePath))`** — tức CHỈ chạy đúng 1 lần
khi file `_database.db` chưa từng tồn tại. Với bất kỳ máy nào đã chạy app trước đó
(gần như chắc chắn đúng cho production/máy đang test) — file DB đã tồn tại từ lâu —
migration `ALTER TABLE` sẽ **không bao giờ được gọi**, 2 cột mới sẽ không tồn tại, và
toàn bộ code outbox mới viết sẽ throw exception ("no such column: Synced") ngay khi
chạy trên máy thật, dù build sạch 100% và test trên máy dev (DB mới toanh) chạy đúng.

## Nguyên nhân gốc rễ (Root Cause)

`SqliteHelper` ctor coi việc "tạo bảng" đồng nghĩa với "tạo DB file lần đầu" — đúng
cho lần cài đặt đầu tiên, nhưng sai hoàn toàn cho migration schema sau này. Bất kỳ
thay đổi schema nào thêm vào bên trong `CreateTable()` chỉ có tác dụng với máy MỚI cài,
không có tác dụng với máy đang chạy production (đúng đối tượng cần migrate nhất).

## Giải pháp

1. Tách logic migrate cột mới ra khỏi `CreateTable()` (dùng `CREATE TABLE IF NOT EXISTS`
   + `ALTER TABLE ADD COLUMN` bọc try/catch nuốt lỗi "duplicate column name" — SQLite
   không có `ADD COLUMN IF NOT EXISTS`) thành 1 method `public static void
   EnsureOutboxColumns()` riêng, gọi được độc lập với `CreateTable()`.
2. Trong `SqliteHelper` ctor, thêm nhánh `else` (DB đã tồn tại) gọi
   `TblEvent.EnsureOutboxColumns()` — đảm bảo migration chạy ở CẢ 2 nhánh: DB mới
   (qua `CreateTable()`) và DB cũ (qua nhánh `else`).

```csharp
if (!File.Exists(_databasePath))
{
    // ... tạo file + 4 bảng (CreateTable() gọi EnsureOutboxColumns() bên trong) ...
}
else
{
    // DB đã tồn tại — CreateTable() không chạy, phải gọi migration riêng ở đây
    TblEvent.EnsureOutboxColumns();
}
```

## Áp dụng lại (How to reuse)

- Bất kỳ khi nào cần thêm cột/bảng vào SQLite/DB local của 1 project đã release
  (không phải mới viết) → PHẢI kiểm tra ctor/bootstrap code có đang gate logic tạo
  schema sau `if (!File.Exists(...))` hay tương đương "chỉ tạo lần đầu" hay không.
  Nếu có → migration PHẢI được gọi ở nhánh else (hoặc unconditionally mỗi lần khởi
  động), không được nhét chung vào hàm chỉ chạy lúc tạo mới.
- Test migration KHÔNG được chỉ test trên máy dev (DB luôn mới toanh sau mỗi lần xóa
  `bin/`) — phải test bằng cách COPY 1 file `_database.db` cũ (schema trước khi sửa)
  vào rồi chạy app, xác nhận cột mới tự xuất hiện.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ SQLite không có cú pháp `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` — phải tự
  bọc try/catch và chấp nhận nuốt lỗi "duplicate column name" mỗi lần app khởi động
  (idempotent nhưng hơi tốn 1 câu lệnh SQL thừa — chấp nhận được, không đáng tối ưu).
- ⚠️ File dev thường bị xóa (`rm -rf bin/obj`) trong lúc test build → dev tự nhiên
  luôn có "DB mới toanh" nên KHÔNG BAO GIỜ tự phát hiện được lỗi "migration không chạy
  trên DB cũ" nếu chỉ test theo thói quen thông thường.

## Tham chiếu

- File: `iAccessDesktopv2.Avalonia/iAccess.Core/Data/SqliteHelper.cs`,
  `iAccessDesktopv2.Avalonia/iAccess.Core/Data/TblEvent.cs`
- Project liên quan: App-Access-V2 (iAccess/iAccessDesktopv2.Avalonia)
- Liên quan: [[rabbitmq-basicpublish-blocks-during-autorecovery-hangs-ui]] (cùng luồng
  fix "màn Giám sát không hiển thị sự kiện" — bug này là bước tiếp theo sau khi fix
  treo UI, để giải quyết triệt để nguy cơ MẤT event khi tắt app/mất mạng)
