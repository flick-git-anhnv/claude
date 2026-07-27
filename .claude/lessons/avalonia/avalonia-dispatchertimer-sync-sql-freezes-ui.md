---
category: avalonia
tags: [dispatchertimer, ui-thread, sqlclient, freeze, not-responding, dotnet-stack, uiautomation]
severity: critical
created: 2026-07-26
updated: 2026-07-26
project-origin: iPGSv4 KIOSK HORIZONTAL (IPGS.Kiosk.Avalonia)
---

# DispatcherTimer chạy SqlConnection.Open() đồng bộ → UI đóng băng theo chu kỳ, cú chạm bị "mất"

## Tình huống gặp phải

Kiosk Avalonia (net8.0) màn cảm ứng. `MainViewModel` có 5 `DispatcherTimer`; một trong đó
(`_timerClearLog`, 10 giây/lần) dọn log và xoá bản ghi cũ trong SQL Server.

## Triệu chứng / Lỗi

Không có exception. Các triệu chứng rời rạc, thoạt trông không liên quan nhau:

- Bấm nút không phản ứng — **thất thường**: cùng một toạ độ, lúc ăn lúc không.
- Kéo-để-cuộn trên màn cảm ứng không ăn.
- Windows hiện hộp thoại **"IPGS.Kiosk.Avalonia is not responding"**.
- `Process.Responding = False` rồi vài giây sau lại `True`.
- Nhưng đồng hồ trên UI **vẫn nhảy** → dễ tưởng UI thread còn khoẻ.

Cực dễ chẩn đoán sai. Tôi đã mất nhiều vòng đi tìm "nút có vùng chạm quá nhỏ", "có lớp phủ vô
hình chặn hit-test", "input tổng hợp bị UIPI chặn" — tất cả đều SAI. Các kiểm tra loại trừ đều PASS
nên càng dẫn sai hướng:

```
IsWindowEnabled = True     WS_DISABLED = False     WS_EX_TRANSPARENT = False
WindowFromPoint(x,y) = đúng hwnd app     IsHungAppWindow = False
SendInput -> sent=3        Cursor.Position = đúng toạ độ
```

⚠️ `SendInput` trả `sent=3` chỉ nghĩa là input đã vào hàng đợi hệ thống — KHÔNG nghĩa là app xử lý.
Nếu UI thread đang bị chặn, message nằm chờ trong hàng đợi rồi bị bỏ qua/ngưng xử lý.

## Nguyên nhân gốc rễ (Root Cause)

`DispatcherTimer.Tick` chạy **trên UI thread**. Handler gọi thẳng công việc chặn:

```csharp
private void TimerClearLog_Tick(object? sender, EventArgs e)
{
    _timerClearLog.Stop();
    try
    {
        SystemUtils.logger?.ClearLogAfterDay(-10);   // IO file/SQLite
        CleanupOldTransactionResults();              // SqlConnection.Open() + DELETE, ĐỒNG BỘ
    }
    finally { _timerClearLog.Start(); }
}
```

Xác nhận bằng `dotnet-stack` lúc app đang "not responding" — UI thread đứng đúng ở đó:

```
Microsoft.Data.SqlClient!SNINativeMethodWrapper.SNIOpenSyncEx
Microsoft.Data.SqlClient!SqlConnection.Open()
IPGS.Kiosk.Avalonia!KioskDbService.OpenInternal()
IPGS.Kiosk.Avalonia!MainViewModel.CleanupOldTransactionResults()
IPGS.Kiosk.Avalonia!MainViewModel.TimerClearLog_Tick()
Avalonia.Base!Avalonia.Threading.DispatcherTimer.FireTick()
Avalonia.Win32!Avalonia.Win32.Win32Platform.WndProc
```

Vì sao đồng hồ vẫn nhảy: timer cập nhật đồng hồ chạy giữa các lần đóng băng, và bản thân việc
render do compositor thread lo. UI thread sống nhưng **bị chiếm dụng từng đợt**.

Vì sao "thất thường": cửa sổ đóng băng ~vài giây mỗi 10 giây. Cú chạm rơi vào đúng đợt đó thì mất;
rơi ngoài đợt thì ăn.

## Giải pháp

Đẩy toàn bộ thân xử lý sang thread nền; chỉ điều khiển `DispatcherTimer` trên UI thread:

```csharp
private void TimerClearLog_Tick(object? sender, EventArgs e)
{
    _timerClearLog.Stop();
    _ = Task.Run(() =>
    {
        try
        {
            SystemUtils.logger?.ClearLogAfterDay(-10);
            CleanupOldTransactionResults();
        }
        catch (Exception ex) { /* log */ }
        finally
        {
            // DispatcherTimer chỉ được điều khiển từ UI thread
            Dispatcher.UIThread.Post(() => _timerClearLog.Start());
        }
    });
}
```

Đo lại sau khi sửa: theo dõi 73 lần trong 40 giây → `Responding = False` **0 lần**. Ngay sau đó
chuột tổng hợp (`mouse_event`/wheel) cũng ăn bình thường — chứng minh "input bị chặn" chỉ là hệ quả.

## Áp dụng lại (How to reuse)

- **Rà soát mọi `DispatcherTimer.Tick`**: nếu bên trong có `SqlConnection.Open()`, `ExecuteNonQuery`,
  `File.*`, `HttpClient` bản đồng bộ, `SerialPort.Open()` → BẮT BUỘC bọc `Task.Run`.
  Mẫu đúng có sẵn trong cùng file (`TimerUpdateConfig_Tick`, `TimerConnectionStatus_Tick`).
- **Khi UI "đôi lúc không nhận chạm"** → nghi UI thread bị chặn TRƯỚC, đừng nghi hit-test/vùng chạm.
  Kiểm tra rẻ nhất: poll `(Get-Process x).Responding` 0,5 giây/lần trong ~40 giây và đếm số lần False.
- **Công cụ chỉ đích danh chỗ treo:**
  ```powershell
  dotnet tool install -g dotnet-stack
  & "$env:USERPROFILE\.dotnet\tools\dotnet-stack.exe" report --process-id <pid>
  ```
  Chạy ĐÚNG LÚC đang đóng băng. Frame đầu của thread có `Program.Main` chính là chỗ chặn.
- Nguy hiểm hơn khi SQL **không kết nối được**: mỗi `Open()` chờ hết connect timeout (mặc định 15s)
  → kiosk gần như tê liệt. Đây là lý do lỗi này là `critical`, không phải `medium`.

## Chú ý / Cạm bẫy (Gotchas)

- ⚠️ `Process.Responding = True` tại một thời điểm KHÔNG loại trừ được lỗi này — phải poll liên tục.
- ⚠️ `IsHungAppWindow` chỉ True khi treo > ~5s liên tục; đóng băng từng đợt ngắn sẽ lọt lưới.
- ⚠️ `DispatcherTimer.Start()/Stop()` phải gọi trên UI thread → dùng `Dispatcher.UIThread.Post`
  trong `finally` của task nền.
- ⚠️ Đừng dùng `PrintWindow` để chụp cửa sổ Avalonia khi đang nghi treo: nó gửi `WM_PRINT` buộc
  render đồng bộ trên UI thread, làm triệu chứng nặng thêm và gây nhiễu chẩn đoán. Dùng
  `Graphics.CopyFromScreen` (chỉ đọc framebuffer, không chạm tiến trình đích).

## Phụ lục — điều khiển UI Avalonia bằng UI Automation (dùng khi kiểm chứng)

Khi cần kịch bản hoá việc kiểm chứng UI, gọi automation peer đáng tin hơn bơm chuột (không phụ
thuộc focus/activation, và không "mất" khi UI vừa hồi phục):

```powershell
Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes
$root = [System.Windows.Automation.AutomationElement]::RootElement
$cond = New-Object System.Windows.Automation.PropertyCondition `
        ([System.Windows.Automation.AutomationElement]::NameProperty), "IPGS Kiosk"
$w = $root.FindFirst([System.Windows.Automation.TreeScope]::Children, $cond)
$all = $w.FindAll([System.Windows.Automation.TreeScope]::Descendants,
                  [System.Windows.Automation.Condition]::TrueCondition)
foreach ($e in $all) {
  if ($e.Current.AutomationId -eq "BtnSetting") {
    $e.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke()
  }
}
```

- `AutomationId` = `x:Name` trong XAML. `ValuePattern.SetValue()` để nhập text, `SetFocus()` để focus.
- ⚠️ `FindFirst` với `PropertyCondition(AutomationIdProperty, ...)` nhiều lúc không thấy element dù
  có mặt → `FindAll(TrueCondition)` rồi tự lọc.
- ⚠️ Dialog con mở bằng `ShowDialog` là top-level window ở tầng Win32 nhưng trong cây UIA các
  control của nó nằm dưới **window CHA**.
- ⚠️ `BoundingRectangle` của control trong `ScrollViewer` là toạ độ **nội dung**, chưa trừ offset
  cuộn (có thể lớn hơn chiều cao cửa sổ) → đừng dùng trực tiếp để bơm chuột.
- ⚠️ Control không có automation peer (VD `Image`/`Path` chỉ gắn `Tapped`, không phải `Button`) sẽ
  không xuất hiện trong cây → không Invoke được.
- ⚠️ Tiêu đề tiếng Việt bị PowerShell 5.1 in sai (`Xác thực` → `Xác th?c`) nên so tên chuỗi trượt.
- ⚠️ `$pid` là biến read-only của PowerShell — đặt tên khác (`$procId`).
- ⚠️ Tool PowerShell không giữ state giữa các lần gọi → `Add-Type` phải nằm trong 1 file `.ps1`
  tự chứa, gọi lại mỗi lần.

## Tham chiếu

- Xem thêm [[avalonia-onscreen-keyboard-overlay-blocks-scroll]] — lỗi bố cục tìm ra trong cùng phiên.
