# tblLed.GetData() crash khi cột NULL-able để trống — app chết ngay lúc khởi động

| | |
|---|---|
| **Category** | dotnet-general |
| **Ngày** | 2026-07-26 |
| **Project** | iPGSv4 (CCU, branch ccu-avalonia) |
| **Loại** | Lỗi |
| **Mức độ** | Cao — app không khởi động được, không có thông báo lỗi cho người dùng |

---

## Hiện tượng

Sau khi thêm bản ghi vào `tblLed` bằng SQL (để có dữ liệu demo), app chết ngay lúc
khởi động, trước cả màn hình đăng nhập. Không có popup lỗi — tiến trình biến mất.

Chỉ thấy được nguyên nhân khi chạy `.exe` bằng cmd và redirect stderr ra file:

```
Unhandled exception. System.FormatException: The input string '' was not in a correct format.
   at System.Int32.Parse(String s)
   at IPGS.Object.Databases.tblLed.GetData() in IPGS.Object\Databases\tblLed.cs:line 87
   at IPGSv4.ViewModels.LoadingViewModel.LoadLed()
```

## Nguyên nhân gốc rễ

`tblLed.GetData()` parse cứng bằng `int.Parse(row[...].ToString())` cho các cột mà
**schema DB khai báo là NULL-able**. `DBNull.ToString()` trả về `""` → `int.Parse("")`
ném `FormatException`. Exception xảy ra trong `LoadingViewModel` chạy nền → không ai
bắt → chết tiến trình.

Các cột NULL-able nhưng bị parse cứng (tblLed.cs:76–93):

| Cột | Dòng | Schema |
|---|---|---|
| `zero_color` | 87 | `int NULL` |
| `led_function` | 90 | `int NULL` |
| `number_of_line` | 86 | `int NULL` |
| `type_detail` | 77 | `int NULL` |
| `lines_config` | 88 | `varchar(max) NULL` (chỉ ToString, không crash) |
| `resolution` | 89 | `varchar(500) NULL` (chỉ ToString, không crash) |

`current_number` còn nguy hiểm hơn: `.Split(",").Select(int.Parse)` → chuỗi rỗng
cũng ném exception.

## Cách khắc phục

**Khi chèn dữ liệu tblLed bằng SQL — bắt buộc điền đủ 5 cột này:**

```sql
INSERT INTO tblLed(..., zero_color, led_function, lines_config, resolution, led_row_index)
VALUES (..., 1, 0, '', '64x32', 0);

-- Vét lại bản ghi cũ còn NULL:
UPDATE tblLed SET
    zero_color    = ISNULL(zero_color, 1),
    led_function  = ISNULL(led_function, 0),
    lines_config  = ISNULL(lines_config, ''),
    resolution    = ISNULL(resolution, '64x32'),
    led_row_index = ISNULL(led_row_index, 0);
```

`zero_color = 1` ứng với `EmLedColor.Red`; `led_function = 0` là giá trị mặc định
của `Led.LedFunction`.

**Fix ở tầng code — ĐÃ ÁP DỤNG 2026-07-26:**

```csharp
// tblLed.cs
private static int ParseIntOr(object? value, int fallback = 0)
    => int.TryParse(value?.ToString(), out int n) ? n : fallback;

private static List<int> ParseIntList(object? value) { /* bỏ qua phần tử không hợp lệ */ }
```

Quan trọng hơn: bọc try/catch ở **`LoadingViewModel.RunAsync()`** — tức bao mọi bước
nạp, không riêng `LoadLed`. Mọi bảng khác (`tblZCU`, `tblZone`, `tblLoop`, `tblKiosk`)
đều dùng chung pattern parse cứng, nên đặt lưới an toàn ở vòng lặp chung mới đúng chỗ:

```csharp
try { await Task.Run(work); }
catch (Exception ex) { _failedSteps.Add($"{label}: {ex.Message}"); }
```

Kiểm chứng: đặt lại `zero_color`/`led_function`/`number_of_line` = NULL cho 1 bản ghi
LED → đăng nhập → app vào được màn hình chính (trước đó chết ngay lúc khởi động).

## Cách phát hiện nhanh khi app chết im lặng

App Avalonia chết không popup → chạy qua cmd để giữ lại stderr:

```powershell
Start-Process cmd.exe -ArgumentList "/c","App.exe > out.txt 2>&1" -WindowStyle Hidden
# doc out.txt sau vai giay
```

Chạy trực tiếp `& app.exe` trong PowerShell dễ mất stack trace vì tiến trình
detach ngay.

## Bài học rút ra

- **Schema NULL-able không có nghĩa code chịu được NULL.** Trước khi seed dữ liệu
  bằng SQL, phải đọc hàm `GetData()` tương ứng để biết cột nào bị parse cứng —
  đừng tin mỗi `sys.columns.is_nullable`.
- Các bảng khác trong `IPGS.Object/Databases/` dùng chung pattern này
  (`tblZCU`, `tblZone`, `tblLoop`, `tblKiosk`) — kiểm tra tương tự trước khi seed.

## Liên quan

- [[powershell-51-ps1-khong-bom-vo-tieng-viet]]
- [[avalonia-config-window-blocks-ui-thread-sql-timeout]]
