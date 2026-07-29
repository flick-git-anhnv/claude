---
category: dotnet-general
tags: [console, encoding, utf8, redirect, winexe, powershell, vietnamese]
severity: medium
created: 2026-07-29
updated: 2026-07-29
project-origin: App-Access-V2 (tool ZkPushMonitor — mode --headless)
---

# `Console.OutputEncoding = UTF8` ném IOException khi stdout bị redirect — gộp try/catch làm `Console.SetOut` không bao giờ chạy, log tiếng Việt thành `?`

## Tình huống gặp phải

Viết tool `ZkPushMonitor` (Avalonia, `OutputType=WinExe`) có thêm mode `--headless` in log tiếng Việt ra console. Test tự động chạy tool bằng PowerShell `Start-Process ... -RedirectStandardOutput proxy.log` rồi đọc lại file để verify.

Để log tiếng Việt không hỏng, đã viết:

```csharp
try
{
    Console.OutputEncoding = new UTF8Encoding(false);
    Console.SetOut(new StreamWriter(Console.OpenStandardOutput(), new UTF8Encoding(false)) { AutoFlush = true });
}
catch (IOException) { /* không có console — bỏ qua */ }
```

## Triệu chứng / Lỗi

File log ra vẫn sai dấu, dù đã set UTF-8 **và** đọc lại đúng bằng `Get-Content -Encoding UTF8`:

```
[08:32:07] INFO: �ang l?ng nghe c?ng 18080 � forward t?i 127.0.0.1:18088
    ? Kh?i t?o � thi?t b? xin c?u h�nh
```

Không có exception, không có cảnh báo — chương trình chạy bình thường, chỉ chữ có dấu bị thay bằng `?`/ký tự rác.

Dễ chẩn đoán sai thành "PowerShell 5.1 hiển thị sai" (lesson `powershell-vietnamese-bom-parse-error` / `powershell-utf8-no-bom-string-parse-corruption` khiến ta nghĩ ngay tới hướng đó). Thực tế **byte trong file đã sai** ngay lúc ghi.

## Nguyên nhân gốc rễ (Root Cause)

Trên Windows, gán `Console.OutputEncoding` khi stdout **đã bị redirect** (`Start-Process -RedirectStandardOutput`, pipe, hoặc WinExe không có console thật) sẽ **ném `IOException`** — vì không có console handle hợp lệ để đổi code page.

Do 2 câu lệnh nằm trong CÙNG một `try`, exception ở dòng đầu làm **dòng `Console.SetOut(...)` không bao giờ được thực thi**. Writer mặc định do runtime tạo cho stdout redirect dùng encoding ANSI của hệ thống ⇒ mọi ký tự ngoài code page thành `?`.

Nói cách khác: đúng cả 2 lệnh, nhưng thứ tự + gộp try/catch làm lệnh QUAN TRỌNG (`SetOut`) bị "che" bởi lệnh phụ trợ (`OutputEncoding`).

## Giải pháp

Tách riêng try/catch, và ưu tiên `Console.SetOut` — đây là lệnh thực sự quyết định encoding khi stdout bị redirect:

```csharp
// 1. Bọc lại standard output bằng writer UTF-8 tường minh (hiệu lực CẢ khi bị redirect)
try
{
    Console.SetOut(new StreamWriter(Console.OpenStandardOutput(), new UTF8Encoding(false))
    {
        AutoFlush = true,
    });
}
catch (IOException)
{
    // không có stdout khả dụng
}

// 2. Đổi code page console THẬT (chỉ có tác dụng khi chạy trong cửa sổ console)
try
{
    Console.OutputEncoding = new UTF8Encoding(false);
}
catch (Exception)
{
    // stdout đã redirect / console không hỗ trợ — không quan trọng
}
```

Verify: `Get-Content proxy.log -Encoding UTF8` phải hiện đúng dấu.

## Áp dụng lại (How to reuse)

- Cần log Unicode/tiếng Việt từ app .NET ra file qua redirect → **luôn** dùng `Console.SetOut` + `StreamWriter(Console.OpenStandardOutput(), UTF8)`; `Console.OutputEncoding` một mình là KHÔNG đủ.
- Thấy chữ có dấu thành `?` trong file log dù đã "set UTF-8" → kiểm tra ngay xem lệnh set writer có bị exception phía trước che mất không (đặt breakpoint/ghi thử 1 dòng ASCII "ENCODING OK").
- Nguyên tắc chung rút ra: **không gộp 2 lệnh vào 1 `try` khi lệnh đầu có thể ném và lệnh sau là lệnh chính** — exception biến lệnh chính thành no-op im lặng.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ `UTF8Encoding(false)` (không BOM) là đúng cho log stream; dùng `new UTF8Encoding(true)` sẽ chèn BOM vào GIỮA output nếu writer được tạo lại.
- ⚠️ `AutoFlush = true` bắt buộc với tool bị `Stop-Process` (kill) — không flush thì mất phần log cuối, dễ tưởng tool treo.
- ⚠️ PowerShell 5.1 `Get-Content` mặc định đọc ANSI ⇒ ngay cả file UTF-8 đúng cũng hiện sai. Luôn thêm `-Encoding UTF8` khi verify, để không "fix" nhầm phía app khi app vốn đã đúng.
- ⚠️ Với `OutputType=WinExe`, `Console.Write*` chỉ thấy được khi stdout được redirect; chạy trực tiếp trong terminal sẽ không hiện gì (không phải lỗi encoding).

## Tham chiếu

- Project liên quan: App-Access-V2 — `iAccessDesktopv2.Avalonia/iAccess.Tools.ZkPushMonitor/Proxy/HeadlessRunner.cs`
- Liên quan: [powershell-utf8-no-bom-string-parse-corruption.md](powershell-utf8-no-bom-string-parse-corruption.md) (cùng chủ đề encoding nhưng nguyên nhân khác: file `.ps1` không BOM)
