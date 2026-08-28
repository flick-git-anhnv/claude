# SQLite: so sánh ngày dạng chuỗi làm retention "im lặng" bỏ sót, và `rowid` không index được

**Ngày:** 2026-08-26
**Project/Module:** vietanh / App-Access-V2 (iAccess Avalonia) — PLAN-db-scale-200-devices
**Loại:** Gotcha
**Mức độ:** ⚠️ HIGH — gây tồn dữ liệu vĩnh viễn mà không có lỗi nào được ném ra

---

## Triệu chứng

DB khách hàng thật 707 MB. Câu dọn log cũ chạy mỗi giờ, không báo lỗi, `return true`, nhưng bảng
`Event` **không hề nhỏ đi** qua nhiều tháng. Chạy tay câu `DELETE` với ngưỡng năm 2099 (tức là "xóa
tất cả") chỉ xóa được **713 / 7.069** dòng đủ điều kiện.

## Nguyên nhân

Cột `Time` là `TEXT` và chứa **hai** định dạng khác nhau do hai bản app cùng ghi vào một file DB:

| Bản app | Định dạng ghi | Ví dụ |
|---|---|---|
| Avalonia (.NET, `ToString("yyyy-MM-dd HH:mm:ss")`) | ISO | `2026-08-26 21:30:00` |
| WinForms (`DateTime.ToString()` theo culture vi-VN) | dd/MM/yyyy + SA/CH | `21/01/2026 10:24:10 SA` |

`WHERE Time < '2026-08-01 00:00:00'` là **so sánh chuỗi**, không phải so sánh ngày:

```
'25/05/2026 ...' vs '2026-08-01 ...'
 ký tự 0: '2' == '2'
 ký tự 1: '5'  >  '0'   →  '25/05/...' LỚN HƠN  →  điều kiện FALSE
```

Nên mọi dòng do bản WinForms ghi **không bao giờ** thỏa `Time < threshold` → tồn vĩnh viễn. Không có
exception, không có log, hàm vẫn trả `true`.

## Hệ quả kèm theo (cùng gốc rễ)

Code đọc cột đó dùng `DateTime.ParseExact(x.Time, "yyyy-MM-dd HH:mm:ss", InvariantCulture)` trong một
LINQ `Where` chạy trên **toàn bộ** bảng → gặp dòng định dạng WinForms là ném `FormatException`, cả khối
`try` bị hủy. Kết quả: một tính năng (gắn ảnh xác minh vào event) **chết hoàn toàn** trên mọi DB mang
từ bản cũ sang, mà nhìn code thì không thấy gì sai.

## Cách xử lý

**1. Retention: bắt cả dòng "không đúng định dạng" thay vì chỉ so sánh ngày**

```sql
DELETE FROM Event
WHERE (Time < @threshold OR Time NOT LIKE '____-__-__%')   -- bắt dòng định dạng lạ
  AND (Synced <> 0 OR RawLogJson IS NULL OR RawLogJson = '')  -- vẫn không xóa dòng chưa đẩy
```

**2. Đọc: luôn parse khoan dung, không bao giờ `ParseExact` một định dạng duy nhất**

```csharp
public static bool TryParseEventTime(string? raw, out DateTime value)
{
    value = default;
    if (string.IsNullOrWhiteSpace(raw)) return false;
    if (DateTime.TryParseExact(raw, "yyyy-MM-dd HH:mm:ss",
            CultureInfo.InvariantCulture, DateTimeStyles.None, out value)) return true;
    return DateTime.TryParse(raw, new CultureInfo("vi-VN"), DateTimeStyles.None, out value)
        || DateTime.TryParse(raw, CultureInfo.InvariantCulture, DateTimeStyles.None, out value);
}
```
Trả `false` và **bỏ qua dòng đó**, đừng để một dòng xấu giết cả vòng lặp.

**3. Chuẩn hóa từ đầu:** nếu tự thiết kế bảng mới, lưu thời gian dạng ISO-8601 (`yyyy-MM-dd HH:mm:ss`)
hoặc Unix epoch số nguyên. Đừng bao giờ ghi `DateTime.ToString()` không tham số vào DB — nó phụ thuộc
culture của máy, nên **cùng một app trên hai máy sẽ ghi hai định dạng khác nhau**.

## Gotcha thứ hai: SQLite không index được `rowid`

```sql
CREATE INDEX IX_Event_Unsynced ON Event(rowid) WHERE Synced = 0;
-- Error: no such column: rowid
```

`rowid` là cột ẩn, không dùng được trong định nghĩa index. Truy vấn dạng
`WHERE Synced = 0 ... ORDER BY rowid` thì dùng **partial index trên cột lọc**:

```sql
CREATE INDEX IX_Event_Unsynced ON Event(Synced) WHERE Synced = 0;
```

Vì mọi dòng trong index đều có `Synced = 0`, thứ tự index trùng thứ tự `rowid` → `ORDER BY rowid`
không phát sinh sort. Index cũng chỉ chứa các dòng đang chờ (thường vài dòng) thay vì cả triệu dòng
lịch sử, nên luôn nằm trong page cache.

## Cách phát hiện sớm

Đừng tin "hàm dọn chạy không lỗi" là "hàm dọn có tác dụng". Kiểm tra bằng số:

```sql
-- Bao nhiêu dòng KHÔNG khớp định dạng mình tưởng?
SELECT COUNT(*) FROM Event WHERE Time NOT LIKE '____-__-__%';
-- Hàm dọn thực sự xóa được bao nhiêu? (chạy trên bản COPY của DB thật)
```

Luôn verify trên **bản copy của DB production thật**, không phải DB dev — DB dev luôn mới toanh nên
chỉ có một định dạng và mọi thứ trông như đang hoạt động. Xem thê
[[sqlite-schema-migration-skipped-when-db-already-exists]] (cùng dạng bẫy: dev test luôn pass vì DB dev
luôn mới).

## Liên quan

- [[sqlite-schema-migration-skipped-when-db-already-exists]]
- [[ensure-schema-not-self-called-silent-insert-fail]] — cùng chủ đề "lỗi bị nuốt im lặng ở tầng DB"
