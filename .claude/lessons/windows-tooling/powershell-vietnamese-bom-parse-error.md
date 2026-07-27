---
category: windows-tooling
tags: [powershell, encoding, bom, utf-8, tieng-viet, parser-error]
severity: high
created: 2026-07-25
updated: 2026-07-25
project-origin: claude (repo config KZTEK)
---

# PowerShell 5.1 đọc `.ps1` không BOM theo ANSI → chữ Việt làm parser báo lỗi sai hướng

## Tình huống gặp phải

Viết `scripts/link-global.ps1` (script tạo junction đưa config KZTEK lên user-level scope).
File được tạo bằng tool `Write` của Claude Code → UTF-8 **không có BOM**.
Trong script có dùng chữ Việt ở cả comment, chuỗi hiển thị, **và key hashtable**:

```powershell
$results += [pscustomobject]@{ Link = $name; Trạng_thái = $status }
```

## Triệu chứng / Lỗi

Chạy `powershell -ExecutionPolicy Bypass -File scripts\link-global.ps1` → hàng loạt lỗi parser
trỏ vào những dòng **hoàn toàn bình thường**:

```
At link-global.ps1:134 char:58
+   $results += [pscustomobject]@{ Link = $name; Tráº¡ng_thÃ¡i =  ...
+                                                    ~
Missing '=' operator after key in hash literal.
At link-global.ps1:212 char:80
The string is missing the terminator: ".
At link-global.ps1:122 char:18
Missing closing '}' in statement block or type definition.
```

Điểm nguy hiểm: thông báo lỗi nói về **thiếu `=`, thiếu `}`, thiếu dấu `"`** — đọc xong sẽ đi
soát ngoặc và dấu bằng, trong khi cú pháp vốn đã đúng 100%. Dấu hiệu nhận biết thật nằm ở
chuỗi echo lại: `Tráº¡ng_thÃ¡i` (mojibake), không phải `Trạng_thái`.

## Nguyên nhân gốc rễ

**Windows PowerShell 5.1 (`powershell.exe`) mặc định đọc file `.ps1` không có BOM theo codepage
ANSI (Windows-1252), KHÔNG phải UTF-8.**

Chữ Việt là ký tự nhiều byte trong UTF-8. Khi bị giải mã theo Windows-1252, mỗi byte thành một
ký tự riêng → `ạ` (0xE1 0xBA 0xA1) thành `áº¡`. Ký tự rác này không hợp lệ làm identifier
→ parser vỡ token → sinh ra chuỗi lỗi vô nghĩa lan ra các dòng sau.

PowerShell 7+ (`pwsh.exe`) mặc định UTF-8 nên **không** bị. Đây là lý do lỗi chỉ xuất hiện
trên môi trường 5.1.

## Giải pháp

Làm **cả hai**, không chỉ một:

**1. Không dùng chữ Việt trong identifier** (tên biến, key hashtable, tên property).
Chỉ dùng chữ Việt trong comment và chuỗi hiển thị.

```powershell
# SAI
$results += [pscustomobject]@{ Link = $name; Trạng_thái = $status }
# ĐÚNG
$results += [pscustomobject]@{ Link = $name; Status = $status }
```

**2. Lưu file `.ps1` có UTF-8 BOM** để comment/chuỗi tiếng Việt hiển thị đúng khi chạy:

```python
p = 'scripts/link-global.ps1'
raw = open(p, 'rb').read()
if not raw.startswith(b'\xef\xbb\xbf'):
    open(p, 'wb').write(b'\xef\xbb\xbf' + raw)
```

Kiểm tra đã có BOM: `head -c 6 file.ps1 | xxd` → phải thấy `efbb bf`.

## Áp dụng lại (How to reuse)

- Ghi **bất kỳ** file `.ps1` có tiếng Việt bằng tool `Write`/`Edit` → thêm BOM ngay sau đó,
  trước khi chạy lần đầu.
- Thấy lỗi PowerShell dạng `Missing '=' operator` / `missing the terminator` / `Missing closing '}'`
  mà cú pháp trông đúng → **kiểm tra encoding trước**, đừng soát cú pháp. Nhìn dòng echo lại
  trong thông báo lỗi: có mojibake (`Ã`, `áº`, `Ä`) là xác nhận.
- Nguyên tắc chung: identifier chỉ ASCII, tiếng Việt chỉ ở comment/chuỗi.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ `Set-Content` / `Add-Content` của PowerShell 5.1 mặc định ghi **ANSI** — dùng để "sửa lại"
  file sẽ làm hỏng thêm. Phải `Out-File -Encoding utf8` (5.1 ghi kèm BOM) hoặc ghi BOM bằng Python.
- ⚠️ Lỗi báo ở dòng 134 nhưng ký tự Việt đầu tiên có thể ở dòng 2 — parser chỉ vỡ khi ký tự rác
  rơi vào vị trí cú pháp quan trọng (như key hashtable). Đừng tin số dòng trong thông báo lỗi.
- ⚠️ File chạy được trên máy có PowerShell 7 nhưng lỗi trên máy chỉ có 5.1 → luôn test bằng
  `powershell.exe` (5.1) nếu script cần chạy trên máy Windows mặc định.

## Bổ sung 2026-07-26 — tái phát ở iPGSv4 + mở rộng sang file `.sql`

Gặp lại y hệt khi ghi `temp/manual-ipgsv4/seed-data.ps1` (script seed dữ liệu SQL, chuỗi
tiếng Việt trong câu `INSERT ... N'Tầng 2'`). Hai điểm mới rút ra:

**1. Công cụ `Edit` xoá BOM đã thêm.** Thêm BOM xong, sửa file bằng `Edit` một lần nữa
→ BOM biến mất, lỗi tái phát y hệt. ⚠️ **Phải kiểm tra lại BOM sau MỖI lần Edit**, không
chỉ sau lần Write đầu tiên:

```powershell
$p = "temp\manual-ipgsv4\seed-data.ps1"
$b = [System.IO.File]::ReadAllBytes($p)
if (-not ($b[0] -eq 0xEF -and $b[1] -eq 0xBB -and $b[2] -eq 0xBF)) {
    [System.IO.File]::WriteAllBytes($p, ([byte[]](0xEF,0xBB,0xBF) + $b))
}
```

**2. File `.sql` chứa tiếng Việt cần BOM **và** `sqlcmd -f 65001`** — hai thứ khác nhau,
thiếu một trong hai là dữ liệu vào DB thành `Tầng`:

```powershell
[System.IO.File]::WriteAllText($sqlFile, $sql, (New-Object System.Text.UTF8Encoding $true))
sqlcmd -S ".\SQLEXPRESS" -d MyDb -E -f 65001 -i $sqlFile
```

Lưu ý phân biệt với `$env:PYTHONIOENCODING="utf-8"` — cái đó chỉ giải quyết phía Python,
không liên quan và không thay thế được BOM/`-f 65001`.

## Tham chiếu

- Gotcha tương ứng trong repo: `.claude/shared/GOTCHAS.md` → G002
- Project liên quan: repo config KZTEK (`Desktop\Claude-Git\claude`)
- Xem thêm: `docs/SETUP-GLOBAL.md` (bối cảnh vì sao cần script này)
