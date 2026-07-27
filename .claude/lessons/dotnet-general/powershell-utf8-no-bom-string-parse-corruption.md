---
category: dotnet-general
tags: [powershell, encoding, utf8, bom, winforms, parse-error]
severity: high
created: 2026-07-23
updated: 2026-07-23
project-origin: iPGSv4 (KioskDeployTool.ps1)
---

# PowerShell 5.1 đọc sai file .ps1 UTF-8 không BOM chứa ký tự Unicode → string bị "cắt" giữa chừng

## Tình huống gặp phải

> Đang làm gì? Tính năng gì? Môi trường nào?

Viết `scripts/windows-tools/KioskDeployTool.ps1` — 1 tool GUI WinForms (Windows PowerShell 5.1)
để deploy setup kiosk qua SSH. File chứa nhiều text tiếng Việt (dấu) và 1 ký tự em dash "—"
trong tiêu đề form (`"KZTEK — Kiosk Deploy Tool (iPGS)"`). File được tạo bằng công cụ ghi file
UTF-8 thông thường (không có BOM).

## Triệu chứng / Lỗi

> Lỗi hiện ra như thế nào? Exception message? Behavior sai?

```
Line 48: Unexpected token 'Kiosk' in expression or statement.
Line 266: Unexpected token 'export' in expression or statement.
Line 267: Unexpected token 'echo' in expression or statement.
Line 267: The token '&&' is not a valid statement separator in this version.
```

Parser báo lỗi ở dòng chứa em dash VÀ ở nhiều dòng KHÔNG liên quan phía sau (cách xa hàng
trăm dòng) — nhìn tưởng là 2 lỗi độc lập, nhưng thực chất chỉ có 1 nguyên nhân gốc.

Repro tối thiểu (không cần WinForms):
```powershell
$x = "KZTEK — test"
```
Parse file này bằng `[System.Management.Automation.Language.Parser]::ParseFile(...)` cho:
```
TerminatorExpectedAtEndOfString: The string is missing the terminator: ".
```

## Nguyên nhân gốc rễ (Root Cause)

> Tại sao xảy ra? Không ghi "chưa rõ" — phải điều tra đến cùng.

Windows PowerShell 5.1 (`powershell.exe`, KHÔNG phải PowerShell 7 `pwsh.exe`) không tự nhận
diện UTF-8 khi file **không có BOM** — nó đọc file theo codepage ANSI hệ thống (VD:
Windows-1252). Ký tự em dash U+2014 mã hoá UTF-8 là 3 byte `0xE2 0x80 0x94`. Khi đọc nhầm theo
ANSI, 3 byte này bị tách thành các ký tự rác riêng biệt, làm parser không tìm thấy dấu `"` đóng
chuỗi đúng vị trí → toàn bộ phần còn lại của file bị dịch pha (offset lệch), khiến các dòng code
hợp lệ ở xa phía sau cũng bị hiểu sai thành token rác.

Điều này áp dụng cho **bất kỳ ký tự non-ASCII nào** trong file (em dash, dấu tiếng Việt, ký tự
Unicode khác) — không riêng gì em dash.

## Giải pháp

> Làm gì để fix? Bước nào theo thứ tự nào?

```powershell
$path = "scripts\windows-tools\KioskDeployTool.ps1"
$content = Get-Content -Path $path -Raw -Encoding UTF8
Set-Content -Path $path -Value $content -Encoding UTF8 -NoNewline
```
`Set-Content -Encoding UTF8` trong Windows PowerShell 5.1 **tự thêm BOM** (`EF BB BF`) — khác
với PowerShell 7 (`pwsh`) nơi `UTF8` mặc định KHÔNG có BOM (phải dùng `-Encoding utf8BOM`).

1. Viết/sửa xong file `.ps1` có chứa ký tự Unicode (tiếng Việt, em dash, ký tự đặc biệt...).
2. Verify cú pháp bằng `[System.Management.Automation.Language.Parser]::ParseFile(path, [ref]$tokens, [ref]$errors)` — nếu `$errors.Count -gt 0`, kiểm tra byte đầu file bằng `[System.IO.File]::ReadAllBytes($path)[0..2]`; nếu KHÔNG phải `239,187,191` (EF BB BF) → thiếu BOM.
3. Chạy lệnh `Set-Content -Encoding UTF8` ở trên để thêm BOM, parse lại để xác nhận `SYNTAX_OK`.

## Áp dụng lại (How to reuse)

> Lần sau gặp tình huống tương tự, làm gì ngay lập tức?

- Bất kỳ khi nào tạo file `.ps1` mới có chứa tiếng Việt/ký tự Unicode (kể cả chỉ 1 dấu gạch
  ngang dài "—" hay 1 icon "✓") → **luôn verify cú pháp bằng ParseFile ngay sau khi Write**,
  đừng đợi đến khi user chạy thử mới phát hiện.
- Nếu thấy lỗi parser chỉ ở NHỮNG DÒNG XA, KHÔNG liên quan logic bị sửa gần đây → nghi ngay
  vấn đề encoding/BOM trước khi debug logic.
- Việc này KHÔNG xảy ra với PowerShell 7 (`pwsh.exe`) vì nó mặc định coi file không-BOM là
  UTF-8 — chỉ là vấn đề của Windows PowerShell 5.1 (`powershell.exe`), vốn vẫn là default
  trên nhiều máy Windows doanh nghiệp/kiosk.

## Chú ý / Cạm bẫy (Gotchas)

> Điều gì dễ sai khi apply solution này?

- ⚠️ `Set-Content -Encoding UTF8` (PS 5.1) thêm BOM; cùng lệnh đó trên PowerShell 7 (`pwsh`)
  **không** thêm BOM (dùng `-Encoding utf8BOM` trên pwsh nếu cần BOM tường minh) — đừng giả
  định hành vi giống nhau giữa 2 runtime.
- ⚠️ Đừng "fix" bằng cách xoá hết ký tự Unicode khỏi UI text tiếng Việt để né lỗi — làm vậy
  mất luôn phần dịch thuật; giải pháp đúng là thêm BOM, không phải ASCII-hoá nội dung.
- ⚠️ Nếu dùng `-NoNewline` khi Set-Content lại toàn bộ nội dung `-Raw`, đảm bảo file gốc đã
  có `\n` cuối dòng đúng ý muốn trước khi ghi lại (Raw đọc nguyên văn, không tự thêm newline).

## Tham chiếu

- Project liên quan: iPGSv4 — `scripts/windows-tools/KioskDeployTool.ps1`
- Repro tối thiểu lưu tại: `C:\Users\nguye\AppData\Local\Temp\claude\...\scratchpad` (tạm thời, không commit)
