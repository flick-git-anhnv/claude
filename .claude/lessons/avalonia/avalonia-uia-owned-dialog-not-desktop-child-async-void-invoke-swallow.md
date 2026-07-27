---
category: avalonia
tags: [uiautomation, showdialog, owned-window, enumwindows, async-void, invokepattern, verify-runtime]
severity: medium
created: 2026-07-26
updated: 2026-07-26
project-origin: App-Access-V2 (migrate-avalonia STEP-4.2)
---

# UIAutomation không thấy dialog modal Avalonia (owned window) là con của desktop; exception async void handler bị InvokePattern.Invoke nuốt im lặng

## Tình huống gặp phải

> Verify runtime STEP-4.2: mở `CheckInSettingWindow` (dialog `ShowDialog(owner)`) từ ComponentGallery
> bằng UIAutomation (PowerShell UIAutomationClient) để chụp screenshot bằng chứng.

Avalonia 12.1.0, Windows 11. Script tự động: `InvokePattern.Invoke()` nút mở dialog → tìm dialog
bằng `RootElement.FindFirst/FindAll(TreeScope.Children, Name/ProcessId)` để chụp.

## Triệu chứng / Lỗi

```
Invoke xong: FindAll(TreeScope.Children) trên desktop CHỈ thấy main window,
KHÔNG thấy dialog "frmCheckInSetting" → script báo "Dialog not found".
Không exception, app không crash, không log gì.
```

Mất >30 phút debug nhầm hướng (nghi XAML lỗi, nghi handler không chạy, thử mouse click thật —
cũng fail vì SetForegroundWindow từ background process bị từ chối).

## Nguyên nhân gốc rễ (Root Cause)

1. **Owned window của Avalonia không được UIA liệt kê là con trực tiếp của desktop** (khác
   WinForms). Dialog THỰC SỰ đã mở — Win32 `EnumWindows` thấy hwnd visible, đúng title, đúng size.
2. Bẫy kép cùng triệu chứng: nếu handler `async void` Click ném exception thật,
   `InvokePattern.Invoke` cũng **nuốt im lặng** (không crash, không propagate về automation client)
   → không phân biệt được "dialog không mở" vs "dialog mở nhưng UIA không thấy".

## Giải pháp

```powershell
# Tìm hwnd dialog bằng EnumWindows lọc ProcessId + GetWindowText == Title
$hwndDlg = [Win32Cap]::FindByTitle([uint32]$proc.Id, "frmCheckInSetting")
$dlg = [System.Windows.Automation.AutomationElement]::FromHandle($hwndDlg)
# Từ đây FindAll con bên trong dialog (ListItem, Button...) hoạt động bình thường
```

1. KHÔNG tìm dialog Avalonia qua `TreeScope.Children` của desktop — dùng `EnumWindows` → `FromHandle`.
2. Khi nghi handler lỗi: bọc try/catch trong async void handler, ghi `ex.Message` ra 1 label UI
   rồi đọc label qua UIA — cách duy nhất thấy được exception bị nuốt.
3. Script mẫu hoàn chỉnh: `App-Access-V2/temp/migrate-avalonia-step42/capture.ps1` (hàm `FindByTitle`).

## Áp dụng lại (How to reuse)

- Khi verify dialog/modal Avalonia bằng UIAutomation → tìm hwnd bằng `EnumWindows` ngay từ đầu.
- Khi `Invoke()` xong mà "không có gì xảy ra" → đừng kết luận handler không chạy; kiểm tra bằng
  EnumWindows + label debug trước.
- `SelectionItemPattern.AddToSelection()` toggle được item của KzCheckedListBox (ListBox
  Multiple|Toggle) mà không cần mouse thật.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Mouse click giả lập (`SetCursorPos` + `mouse_event`) không tin cậy từ background process:
  `SetForegroundWindow` bị Windows từ chối → click rơi vào cửa sổ khác đang đè lên.
- ⚠️ `InvokePattern.Invoke` trên nút có handler `async void` trả về ở `await` đầu tiên —
  KHÔNG block đến khi dialog đóng (dùng được cho nút mở ShowDialog).

## Tham chiếu

- GOTCHAS G005 — `App-Access-V2/.claude/shared/GOTCHAS.md`
- Lesson liên quan: G004 (process treo lock exe → test binary cũ)
