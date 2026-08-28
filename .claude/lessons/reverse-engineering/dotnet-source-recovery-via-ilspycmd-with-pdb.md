---
category: dotnet-general
tags: [ilspycmd, decompile, pdb, source-recovery, dotnet5, winforms]
severity: high
created: 2026-08-13
updated: 2026-08-13
project-origin: ExcelTool (5.Friends/Trang)
---

# Mất source .NET nhưng còn .dll + .pdb → decompile bằng ilspycmd gần như khôi phục 100% source gốc

## Tình huống gặp phải

> User mất toàn bộ source code project WinForms (.NET 5, "ExcelTool" — công cụ xuất
> hóa đơn điện tử từ Excel sang XML/PDF ký số cho nhiều nhà cung cấp: AcMan, FPT,
> VETC, Hải Phòng...). Chỉ còn lại thư mục publish output: `Test.exe`, `Test.dll`,
> `Test.pdb`, cùng các DLL thư viện thứ ba (SpreadsheetLight, DocumentFormat.OpenXml,
> itextsharp, BouncyCastle.Crypto).

## Triệu chứng / Lỗi

> Ban đầu tưởng phải viết lại toàn bộ logic nghiệp vụ từ đầu (rất tốn thời gian,
> rủi ro sai format XML hóa đơn điện tử theo từng nhà cung cấp).

## Nguyên nhân gốc rễ (Root Cause)

Không phải "mất code" theo nghĩa không thể khôi phục — vì đây là managed .NET DLL
(IL, không phải native), và **đi kèm file `.pdb` (debug symbols)**. Khi có đủ cặp
`.dll` + `.pdb`, decompiler (ilspycmd/dnSpy/ILSpy) khôi phục được gần như nguyên vẹn:
đúng tên class, tên biến, tên property, cấu trúc namespace, kể cả code
`InitializeComponent()` của WinForms Designer — vì PDB chứa toàn bộ metadata tên gốc,
decompiler chỉ cần dịch ngược IL → C# theo đúng tên đó.

## Giải pháp

```powershell
# Cài công cụ (chỉ cần 1 lần, dùng lại mọi project)
dotnet tool install -g ilspycmd

# Decompile toàn bộ project (-p = tạo cấu trúc project .csproj đầy đủ, không phải 1 file)
ilspycmd -p -o <thư_mục_output> Test.dll
```

Sau decompile, để build lại được cần sửa vài chỗ ilspy sinh sai:

1. `TargetFramework`: nếu project gốc dùng `UseWindowsForms`/`UseWPF`, phải thêm hậu
   tố `-windows` (vd `net5.0` → `net5.0-windows`) — nếu không sẽ lỗi
   `NETSDK1136: target platform must be set to Windows`.
2. `LangVersion`: ilspy đôi khi ghi ra version không hợp lệ (vd `15.0` không tồn tại).
   Xóa dòng đó hoặc đặt `LangVersion>latest`.
3. File-scoped namespace (`namespace X;`) cần `LangVersion` ≥ 10 — nếu để nguyên
   `LangVersion` cũ/thấp sẽ lỗi `CS8773`.
4. Các DLL third-party chỉ được reference qua `<Reference HintPath>` (không phải
   NuGet) — phải tự copy toàn bộ `.dll` phụ thuộc (kể cả dependency gián tiếp như
   `BouncyCastle.Crypto.dll` mà itextsharp cần) vào thư mục project và thêm
   `<Reference>` tương ứng, vì ilspy không tự biết các dependency gián tiếp không
   được project trực tiếp `using`.
5. Build thử ngay bằng `dotnet build -c Release` để xác nhận decompile "sạch" —
   nếu build pass 0 error, gần như chắc chắn logic nghiệp vụ được khôi phục đúng.

## Áp dụng lại (How to reuse)

- Khi user báo "mất code, không mã hóa" → **luôn kiểm tra thư mục build/publish
  output trước** xem có `.dll`/`.exe` (managed .NET) không, và đặc biệt tìm file
  `.pdb` đi kèm — đây là chìa khóa khôi phục gần như hoàn hảo, ưu tiên hơn hẳn việc
  đề xuất "viết lại từ đầu" (tốn công + rủi ro sai logic nghiệp vụ đặc thù, ví dụ
  format XML hóa đơn điện tử theo luật).
- Kiểm tra `*.runtimeconfig.json` để biết chính xác TFM (`net5.0`, `net6.0`...) và
  `*.deps.json` để biết danh sách NuGet package gốc + version — dùng để tái tạo lại
  đúng cấu hình csproj.
- Luôn build thử ngay sau decompile để verify, đừng chỉ đọc code bằng mắt.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Nếu KHÔNG có `.pdb` đi kèm, decompiler vẫn chạy được nhưng tên biến/property
  sẽ bị đổi thành generic (`class1`, `method_0`...) — vẫn dùng được logic nhưng khó
  đọc hơn nhiều. Luôn ưu tiên tìm `.pdb` trước khi báo user "không khôi phục được".
- ⚠️ File native (C++, không phải .NET managed) — ví dụ `.exe` biên dịch bằng C++,
  Delphi, hay ahead-of-time (AOT) — KHÔNG áp dụng được kỹ thuật này; phải dùng
  Ghidra/IDA (xem các lesson RE khác trong category này).
- ⚠️ Sau khi build thành công, nên nâng cấp `TargetFramework` lên bản LTS còn hỗ trợ
  (vd .NET 8) nếu muốn maintain lâu dài — net5.0 đã EOL (cảnh báo `NETSDK1138`).

## Tham chiếu

- Công cụ: `ilspycmd` (NuGet global tool, package `ilspycmd`)
- Project liên quan: ExcelTool (i:\5.Friends\Trang\ExcelTool)
