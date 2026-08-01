---
category: avalonia
tags: [ux-pattern, auto-select, kiosk-deploy, ssh-scan]
severity: high
created: 2026-07-30
updated: 2026-07-30
project-origin: 6.RemoteControlTool (KioskDeployWindow — Config phần mềm / App exec autofill)
---

# Auto-fill "best match" chỉ lọc theo `ExistsOnSystem`, quên lọc `IsRecommended` → tự chọn nhầm app hệ thống

## Tình huống gặp phải

`KioskDeployWindow` quét danh sách app kiosk có thể autostart từ máy ZCU qua
`LoadKioskAppsAsync` (SSH). Mỗi app trả về có `IsRecommended` (tên/lệnh chứa
"ipgs"/"kiosk") và `ExistsOnSystem` (binary có thật trên máy). Sau khi nạp danh
sách, code tự động điền ComboBox "App exec" bằng "best match" để tiện UX.

## Triệu chứng / Lỗi

Trên máy ZCU vừa gỡ sạch ZcuAgent/kiosk app để test lại từ đầu (không còn app nào
recommended), ComboBox "App exec" tự động điền `software-properties-gtk --open-tab=4`
(dialog "Software & Updates" của hệ thống) — hoàn toàn không liên quan kiosk. Bấm
Deploy → `2-configure-system.sh` fail (exit 1) vì binary đó không tồn tại đúng path
kỳ vọng. User tưởng do tự bấm nhầm, nhưng thực ra là code TỰ chọn.

## Nguyên nhân gốc rễ (Root Cause)

```csharp
// SAI — chỉ lọc ExistsOnSystem, không lọc IsRecommended
var bestMatch = _loadedApps.FirstOrDefault(a => a.ExistsOnSystem);
```

`LoadedApp` (record nội bộ ánh xạ display-text) KHÔNG lưu `IsRecommended` — field
này chỉ được dùng để build chuỗi hiển thị (⭐ ... — khuyến nghị) rồi bị bỏ qua khi
tạo record. Khi không còn app nào `IsRecommended && ExistsOnSystem`, code fallback
chọn ĐẠI app tồn tại ĐẦU TIÊN trong danh sách (thường là 1 tiện ích hệ thống bất kỳ
quét được từ `/usr/share/applications/*.desktop`), thay vì để trống.

## Giải pháp

```csharp
private sealed record LoadedApp(string DisplayText, string ExecCommand, bool ExistsOnSystem, bool IsRecommended);
...
return new LoadedApp(display, a.ExecCommand, a.ExistsOnSystem, a.IsRecommended);
...
// ĐÚNG — chỉ tự chọn khi ĐÃ CÀI THẬT + LÀ APP KIOSK KHUYẾN NGHỊ
var bestMatch = _loadedApps.FirstOrDefault(a => a.ExistsOnSystem && a.IsRecommended);
PART_AppExec.Text = bestMatch?.DisplayText ?? "";  // không match → để trống
```

## Áp dụng lại (How to reuse)

- Khi thiết kế "auto-select best match" cho dropdown quét từ hệ thống thật (SSH scan,
  file scan...), PHẢI mang đủ TẤT CẢ cờ phân loại (relevance/recommended) qua record
  nội bộ — không chỉ giữ lại field dùng để hiển thị rồi bỏ field dùng để LỌC.
- Auto-select "best match" phải luôn có điều kiện phù hợp NGỮ CẢNH (ở đây: "là app
  kiosk"), không chỉ điều kiện tồn tại vật lý (`ExistsOnSystem`) — "tồn tại" không
  đồng nghĩa "đúng".
- Khi test 1 tính năng auto-fill trên môi trường ĐÃ BỊ DỌN SẠCH (không còn app đích),
  luôn kiểm tra nhánh "không tìm thấy match tốt" có thực sự để trống hay âm thầm rơi
  vào 1 giá trị khác — đây là edge case dễ bị bỏ sót khi test trên máy luôn có sẵn app.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ Lỗi này CHỈ xuất hiện khi máy đích KHÔNG có app kiosk thật cài sẵn — nếu luôn test
  trên máy đã cài app thật, `IsRecommended` entry luôn tồn tại và che giấu bug này.
- ⚠️ Thông báo lỗi cuối cùng ("không tìm thấy binary software-properties-gtk") dễ khiến
  người debug nghĩ do user chọn sai tay — phải truy ngược lên UI auto-fill logic để
  thấy đây là bug code, không phải thao tác sai của user.

## Cập nhật 2026-07-30 (F24) — Validation trùng lặp ở 2 tầng, sửa 1 tầng chưa đủ

Sau khi sửa auto-fill (F23) ở tầng UI (`KioskDeployWindow.axaml.cs`) để nút "Deploy Config
máy tính" không bắt buộc App exec, deploy **vẫn crash** với message khác:
`"Chưa chọn lệnh autostart app (App exec)..."` — lần này ném ra từ tầng SERVICE
(`KioskDeployService.DeployAsync`), một check ĐỘC LẬP, KHÔNG BIẾT gì về việc UI đã tự tắt
Autostart/Watchdog:

```csharp
// SAI — chặn vô điều kiện bất cứ khi nào RunConfigureSystem=true, không xét
// Autostart/Watchdog có đang bật hay không
if (string.IsNullOrWhiteSpace(options.AppExec))
    throw new Exception("Chưa chọn lệnh autostart app...");
```

**Bài học:** khi có 2 lớp validate cùng 1 điều kiện (ở đây: "cần AppExec khi nào") nằm ở
2 file khác nhau (UI code-behind + Service), sửa 1 lớp KHÔNG đủ — phải tìm và đồng bộ
TẤT CẢ chỗ check trùng. Grep theo message lỗi hoặc theo field liên quan (`AppExec`,
`EnableAutostart`, `EnableWatchdog`) trên toàn bộ 2 file trước khi coi là "đã sửa xong".

Fix: đổi điều kiện service-layer thành
`string.IsNullOrWhiteSpace(options.AppExec) && (options.EnableAutostart || options.EnableWatchdog)`
— khớp đúng với lý do thực sự cần AppExec (script chỉ dùng giá trị này trong nhánh
Autostart=1 hoặc Watchdog=1, xác nhận bằng cách đọc trực tiếp `2-configure-system.sh`).

## Tham chiếu

- Project liên quan: `6.RemoteControlTool` — `IPGS.RemoteControl.CcuUI/Views/KioskDeployWindow.axaml.cs` (F23)
- Liên quan: `[[gext-dead-code-slows-kiosk-deploy]]` (nếu có) — cùng khu vực KioskDeployWindow, cùng đợt hardening F21-F23
