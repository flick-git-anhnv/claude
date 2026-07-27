---
category: avalonia
tags: [win32, findwindow, enumwindows, uiautomation, verify-runtime]
severity: medium
created: 2026-07-26
updated: 2026-07-26
project-origin: App-Access-V2 (PLAN-migrate-avalonia STEP-4.3)
---

# Win32 `FindWindowW(null, title)` KHÔNG tìm thấy window Avalonia — kể cả top-level MainWindow

## Tình huống gặp phải

> Verify runtime `ConfirmPasswordWindow` (gate mật khẩu ConnectionConfig standalone) bằng PowerShell + P/Invoke user32, Avalonia 12.1.0, Windows 11.

Script test tự động cần tìm hwnd window theo title `"Xác thực thông tin"` để chụp screenshot + điều khiển qua UIAutomation.

## Triệu chứng / Lỗi

```
TIMEOUT: khong thay window 'Xác thực thông tin'   (poll FindWindowW 15s, luôn trả 0)
```

Trong khi đó app chạy hoàn toàn bình thường: process sống, `Process.MainWindowTitle` trả đúng chuỗi, dump từng codepoint xác nhận title khớp 100% dạng precomposed (không phải lỗi encoding/combining characters). Dễ kết luận nhầm "app crash khi khởi động / window không mở" và đi debug XAML vô ích.

## Nguyên nhân gốc rễ (Root Cause)

Window của Avalonia không được `FindWindow`/`FindWindowW` match theo window name như window Win32/WinForms cổ điển. Trước đây (lesson `avalonia-uia-owned-dialog-not-desktop-child-async-void-invoke-swallow.md`, G005) tưởng chỉ owned dialog bị UIA/desktop-children bỏ sót — thực tế **cả MainWindow top-level cũng không tìm được bằng FindWindowW**.

## Giải pháp

```csharp
// EnumWindows + GetWindowTextW (CharSet.Unicode) + IsWindowVisible, so sánh chuỗi thủ công
public static IntPtr FindByTitle(string title) {
    IntPtr found = IntPtr.Zero;
    EnumWindows((h, l) => {
        if (!IsWindowVisible(h)) return true;
        var sb = new StringBuilder(256); GetWindowTextW(h, sb, 256);
        if (sb.ToString() == title) { found = h; return false; }
        return true;
    }, IntPtr.Zero);
    return found;
}
```

1. Tìm hwnd bằng `FindByTitle` (lọc thêm ProcessId nếu nhiều instance).
2. `AutomationElement.FromHandle(hwnd)` → FindFirst/FindAll con bên trong hoạt động bình thường.
3. Screenshot: `ShowWindow(hwnd, 9)` + `PrintWindow(hwnd, dc, 2)` như cũ.

Script mẫu đã chạy thật: `temp/migrate-avalonia-step43/verify-confirm-password.ps1` (repo App-Access-V2).

## Áp dụng lại (How to reuse)

- Khi test/automation app Avalonia cần hwnd → dùng thẳng `EnumWindows` + `GetWindowTextW`, ĐỪNG thử `FindWindowW` trước.
- Khi `FindWindowW` trả 0 mà `Process.MainWindowTitle` đúng → không phải bug app, đổi cơ chế tìm window.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Không debug encoding/BOM của title khi gặp lỗi này — codepoint đã xác nhận khớp vẫn không match, không phải nguyên nhân (BOM chỉ là vấn đề riêng của file `.ps1`, xem G002).
- ⚠️ `GetWindowTextW` phải khai `CharSet.Unicode`, nếu không title tiếng Việt đọc về bị hỏng và so sánh vẫn fail.

## Tham chiếu

- GOTCHAS G005 (owned dialog không là desktop child) + G006 (entry này) — `.claude/shared/GOTCHAS.md` repo App-Access-V2
- Project liên quan: App-Access-V2 (PLAN-migrate-avalonia)
