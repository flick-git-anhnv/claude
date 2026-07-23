# KioskDeployTool.ps1 — GUI Windows để deploy setup kiosk iPGS (ẩn top bar +
# cấu hình hệ thống) TỪ XA qua SSH vào bất kỳ máy Ubuntu kiosk nào, không cần
# mở terminal/plink thủ công.
#
# Yêu cầu: cài PuTTY (cung cấp plink.exe + pscp.exe). Script tự dò các đường
# dẫn cài đặt phổ biến, hoặc dùng bản có sẵn trong PATH.
#
# Chạy (double-click hoặc):
#   powershell -sta -File scripts\windows-tools\KioskDeployTool.ps1
#
# Script tự relaunch ở chế độ STA nếu chưa đúng apartment state (bắt buộc cho WinForms).

if ([System.Threading.Thread]::CurrentThread.GetApartmentState() -ne 'STA') {
    Start-Process powershell -ArgumentList "-NoProfile -STA -ExecutionPolicy Bypass -File `"$PSCommandPath`""
    exit
}

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# ─────────────────────────────────────────────────────────────
# Dò đường dẫn plink.exe / pscp.exe
function Find-PuttyTool {
    param([string]$ToolName)
    $candidates = @(
        (Get-Command $ToolName -ErrorAction SilentlyContinue).Source,
        "C:\Program Files\PuTTY\$ToolName",
        "C:\Program Files (x86)\PuTTY\$ToolName"
    )
    foreach ($c in $candidates) {
        if ($c -and (Test-Path $c)) { return $c }
    }
    return $null
}

$PlinkPath = Find-PuttyTool "plink.exe"
$PscpPath  = Find-PuttyTool "pscp.exe"

$ScriptRoot   = Split-Path -Parent $PSCommandPath
$KioskDir     = Join-Path (Split-Path -Parent $ScriptRoot) "linux-kiosk"
$Script1Path  = Join-Path $KioskDir "1-install-software.sh"
$Script2Path  = Join-Path $KioskDir "2-configure-system.sh"
$Script3Path  = Join-Path $KioskDir "3-toggle-topbar.sh"

# ─────────────────────────────────────────────────────────────
# Form
$form = New-Object System.Windows.Forms.Form
$form.Text = "KZTEK — Kiosk Deploy Tool (iPGS)"
$form.Size = New-Object System.Drawing.Size(620, 700)
$form.StartPosition = "CenterScreen"
$form.FormBorderStyle = "FixedDialog"
$form.MaximizeBox = $false

$labelFont = New-Object System.Drawing.Font("Segoe UI", 9)
$y = 15

function New-Label($text, $y) {
    $l = New-Object System.Windows.Forms.Label
    $l.Text = $text
    $l.Location = New-Object System.Drawing.Point(15, $y)
    $l.Size = New-Object System.Drawing.Size(220, 20)
    $l.Font = $labelFont
    return $l
}
function New-TextBox($y, [bool]$isPassword) {
    $t = New-Object System.Windows.Forms.TextBox
    $t.Location = New-Object System.Drawing.Point(240, $y)
    $t.Size = New-Object System.Drawing.Size(340, 24)
    $t.Font = $labelFont
    if ($isPassword) { $t.UseSystemPasswordChar = $true }
    return $t
}

$lblIp = New-Label "Địa chỉ IP máy kiosk:" $y
$txtIp = New-TextBox $y $false
$form.Controls.AddRange(@($lblIp, $txtIp)); $y += 32

$lblUser = New-Label "SSH user:" $y
$txtUser = New-TextBox $y $false
$txtUser.Text = "kztek"
$form.Controls.AddRange(@($lblUser, $txtUser)); $y += 32

$lblPass = New-Label "SSH password:" $y
$txtPass = New-TextBox $y $true
$form.Controls.AddRange(@($lblPass, $txtPass)); $y += 32

$lblSudoPass = New-Label "Sudo password (để trống nếu giống SSH password):" $y
$txtSudoPass = New-TextBox $y $true
$form.Controls.AddRange(@($lblSudoPass, $txtSudoPass)); $y += 32

$lblKioskUser = New-Label "Kiosk user (autologin):" $y
$txtKioskUser = New-TextBox $y $false
$txtKioskUser.Text = "kztek"
$form.Controls.AddRange(@($lblKioskUser, $txtKioskUser)); $y += 32

$lblAppExec = New-Label "App exec:" $y
$txtAppExec = New-TextBox $y $false
$txtAppExec.Text = "ipgskioskavalonia"
$form.Controls.AddRange(@($lblAppExec, $txtAppExec)); $y += 40

$chk1 = New-Object System.Windows.Forms.CheckBox
$chk1.Text = "Chạy Script 1 — Cài phần mềm (extension ẩn top bar + unclutter)"
$chk1.Location = New-Object System.Drawing.Point(15, $y)
$chk1.Size = New-Object System.Drawing.Size(560, 22)
$chk1.Checked = $true
$chk1.Font = $labelFont
$form.Controls.Add($chk1); $y += 26

$chk2 = New-Object System.Windows.Forms.CheckBox
$chk2.Text = "Chạy Script 2 — Cấu hình hệ thống (autologin, autostart, dock/sleep/update...)"
$chk2.Location = New-Object System.Drawing.Point(15, $y)
$chk2.Size = New-Object System.Drawing.Size(560, 22)
$chk2.Checked = $true
$chk2.Font = $labelFont
$form.Controls.Add($chk2); $y += 30

$lblToggle = New-Label "Top Bar/Dock/Desktop Icons:" $y
$form.Controls.Add($lblToggle)

$radioNone = New-Object System.Windows.Forms.RadioButton
$radioNone.Text = "Không đổi"
$radioNone.Location = New-Object System.Drawing.Point(240, $y)
$radioNone.Size = New-Object System.Drawing.Size(100, 22)
$radioNone.Checked = $true
$radioNone.Font = $labelFont
$form.Controls.Add($radioNone)

$radioHide = New-Object System.Windows.Forms.RadioButton
$radioHide.Text = "Ẩn"
$radioHide.Location = New-Object System.Drawing.Point(345, $y)
$radioHide.Size = New-Object System.Drawing.Size(80, 22)
$radioHide.Font = $labelFont
$form.Controls.Add($radioHide)

$radioShow = New-Object System.Windows.Forms.RadioButton
$radioShow.Text = "Hiện lại"
$radioShow.Location = New-Object System.Drawing.Point(430, $y)
$radioShow.Size = New-Object System.Drawing.Size(100, 22)
$radioShow.Font = $labelFont
$form.Controls.Add($radioShow)
$y += 32

$btnDeploy = New-Object System.Windows.Forms.Button
$btnDeploy.Text = "Deploy"
$btnDeploy.Location = New-Object System.Drawing.Point(240, $y)
$btnDeploy.Size = New-Object System.Drawing.Size(140, 34)
$btnDeploy.Font = New-Object System.Drawing.Font("Segoe UI", 10, [System.Drawing.FontStyle]::Bold)
$form.Controls.Add($btnDeploy); $y += 46

$lblLog = New-Label "Log:" $y
$form.Controls.Add($lblLog); $y += 22

$txtLog = New-Object System.Windows.Forms.TextBox
$txtLog.Location = New-Object System.Drawing.Point(15, $y)
$txtLog.Size = New-Object System.Drawing.Size(580, 260)
$txtLog.Multiline = $true
$txtLog.ScrollBars = "Vertical"
$txtLog.ReadOnly = $true
$txtLog.Font = New-Object System.Drawing.Font("Consolas", 9)
$form.Controls.Add($txtLog)

function Append-Log([string]$text) {
    if ($txtLog.InvokeRequired) {
        $txtLog.Invoke([Action]{ Append-Log $text })
        return
    }
    $txtLog.AppendText("$text`r`n")
}

if (-not $PlinkPath -or -not $PscpPath) {
    Append-Log "CẢNH BÁO: không tìm thấy plink.exe/pscp.exe. Cài PuTTY (https://www.putty.org) rồi mở lại tool này."
}
if (-not (Test-Path $Script1Path) -or -not (Test-Path $Script2Path) -or -not (Test-Path $Script3Path)) {
    Append-Log "CẢNH BÁO: thiếu 1 trong 3 script (1-install-software.sh / 2-configure-system.sh / 3-toggle-topbar.sh) tại $KioskDir"
}

# ─────────────────────────────────────────────────────────────
# Toàn bộ logic deploy chạy trong 1 BACKGROUND JOB (Start-Job — tiến trình
# PowerShell riêng), không chạy trên UI thread — tránh đứng hình WinForms
# trong lúc chờ SSH (có thể mất vài phút).
#
# GHI CHÚ (đã test thực tế, đừng quay lại cách cũ):
# - KHÔNG dùng BeginOutputReadLine/BeginErrorReadLine (async event) để đọc
#   stdout/stderr của plink/pscp — đã test và phát hiện `pscp` bị MẤT TOÀN BỘ
#   nội dung stderr khi đọc theo event (dù `exit code` vẫn đúng), khiến bước
#   tự trích fingerprint host key từ stderr luôn thất bại. CHỈ dùng
#   `StandardOutput.ReadToEnd()`/`StandardError.ReadToEnd()` đồng bộ (đáng tin
#   cậy 100% qua nhiều lần test) — đây là lý do phải chạy trong Job riêng để
#   không khoá UI thread trong lúc ReadToEnd blocking.
# - KHÔNG feed "y\n" qua StandardInput để tự chấp nhận host key — đã test treo
#   vô thời hạn (PuTTY tools không đọc prompt Y/N từ stdin redirect qua .NET
#   Process giống cách hoạt động khi pipe qua bash). Thay vào đó: chạy `-batch`
#   trước, nếu bị chặn vì host key chưa cache thì trích fingerprint từ stderr
#   (regex `ssh-\S+ \d+ SHA256:\S+`) rồi chạy lại với `-hostkey "<fp>" -batch`.
$DeployScriptBlock = {
    param($PlinkPath, $PscpPath, $ip, $sshUser, $sshPass, $sudoPass, $kioskUser, $appExec,
          $toggleMode, $runStep1, $runStep2, $Script1Path, $Script2Path, $Script3Path)

    function Invoke-PuttyCommandRaw {
        param([string]$ExePath, [string]$Arguments)
        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = $ExePath
        $psi.Arguments = $Arguments
        $psi.RedirectStandardOutput = $true
        $psi.RedirectStandardError = $true
        $psi.UseShellExecute = $false
        $psi.CreateNoWindow = $true
        $proc = [System.Diagnostics.Process]::Start($psi)
        $stdout = $proc.StandardOutput.ReadToEnd()
        $stderr = $proc.StandardError.ReadToEnd()
        $proc.WaitForExit()
        return @{ ExitCode = $proc.ExitCode; StdOut = $stdout; StdErr = $stderr }
    }

    function Invoke-PuttyCommand {
        param([string]$ExePath, [string]$BaseArguments)
        # QUAN TRỌNG: cờ (-batch/-hostkey) PHẢI đứng TRƯỚC BaseArguments (source/dest
        # positional). Đã test thực tế: đặt "-batch" SAU đường dẫn đích khiến `pscp`
        # hiểu nhầm thành "More than one remote source not supported" — pscp không
        # tự phân biệt option/positional theo thứ tự như plink, luôn cần option trước.
        $r = Invoke-PuttyCommandRaw -ExePath $ExePath -Arguments "-batch $BaseArguments"
        if ($r.StdOut) { Write-Output $r.StdOut.TrimEnd() }
        if ($r.ExitCode -eq 0) { return $r }

        $fp = [regex]::Match($r.StdErr, 'ssh-\S+ \d+ SHA256:\S+').Value
        if ($fp) {
            Write-Output "--- Lần đầu kết nối tới host này — tự chấp nhận host key ($fp) ---"
            $r2 = Invoke-PuttyCommandRaw -ExePath $ExePath -Arguments "-hostkey `"$fp`" -batch $BaseArguments"
            if ($r2.StdOut) { Write-Output $r2.StdOut.TrimEnd() }
            if ($r2.ExitCode -ne 0 -and $r2.StdErr) { Write-Output $r2.StdErr.TrimEnd() }
            return $r2
        }
        if ($r.StdErr) { Write-Output $r.StdErr.TrimEnd() }
        return $r
    }

    Write-Output "=== Bắt đầu deploy tới $sshUser@$ip ==="
    Write-Output "--- [1] Copy script sang máy kiosk ---"
    $filesToCopy = @()
    if ($runStep1) { $filesToCopy += "`"$Script1Path`"" }
    if ($runStep2) { $filesToCopy += "`"$Script2Path`"" }
    if (-not [string]::IsNullOrEmpty($toggleMode)) { $filesToCopy += "`"$Script3Path`"" }
    $pscpArgs = "-pw `"$sshPass`" $($filesToCopy -join ' ') $sshUser@${ip}:/home/$sshUser/"
    $rCopy = Invoke-PuttyCommand -ExePath $PscpPath -BaseArguments $pscpArgs

    if ($rCopy.ExitCode -ne 0) {
        Write-Output "LỖI: copy script thất bại (exit $($rCopy.ExitCode)). Kiểm tra IP/user/password."
        Write-Output "RESULT_FAILURE"
        return
    }

    Write-Output "--- [2] Chạy setup trên máy kiosk (có thể mất vài phút) ---"
    $remoteCmd = "chmod +x ~/1-install-software.sh ~/2-configure-system.sh ~/3-toggle-topbar.sh 2>/dev/null; " +
                 "export DISPLAY=:0; export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/`$(id -u)/bus; " +
                 "echo '$sudoPass' | sudo -S -v && echo SUDO_CACHED_OK; "
    if ($runStep1) { $remoteCmd += "bash ~/1-install-software.sh; " }
    if ($runStep2) { $remoteCmd += "bash ~/2-configure-system.sh '$kioskUser' '$appExec'; " }
    if (-not [string]::IsNullOrEmpty($toggleMode)) { $remoteCmd += "bash ~/3-toggle-topbar.sh $toggleMode; " }

    $plinkArgs = "-ssh -t -pw `"$sshPass`" $sshUser@$ip `"$remoteCmd`""
    $rRun = Invoke-PuttyCommand -ExePath $PlinkPath -BaseArguments $plinkArgs

    if ($rRun.ExitCode -eq 0) {
        Write-Output "=== HOÀN THÀNH — exit code 0 ==="
        Write-Output "RESULT_SUCCESS"
    } else {
        Write-Output "=== THẤT BẠI — exit code $($rRun.ExitCode). Xem log phía trên. ==="
        Write-Output "RESULT_FAILURE"
    }
}

$script:DeployJob = $null
$DeployTimer = New-Object System.Windows.Forms.Timer
$DeployTimer.Interval = 400
$DeployTimer.Add_Tick({
    if (-not $script:DeployJob) { return }
    $lines = Receive-Job -Job $script:DeployJob -ErrorAction SilentlyContinue
    foreach ($line in $lines) {
        if ($line -eq "RESULT_SUCCESS" -or $line -eq "RESULT_FAILURE") { continue }
        Append-Log "$line"
    }
    if ($script:DeployJob.State -in @('Completed', 'Failed', 'Stopped')) {
        $DeployTimer.Stop()
        $success = $lines -contains "RESULT_SUCCESS"
        if ($script:DeployJob.State -eq 'Failed') {
            Append-Log "LỖI JOB: $((Receive-Job -Job $script:DeployJob -Keep -ErrorAction SilentlyContinue) -join "`n")"
        }
        Remove-Job -Job $script:DeployJob -Force -ErrorAction SilentlyContinue
        $script:DeployJob = $null
        $btnDeploy.Enabled = $true
        if ($success) {
            [System.Windows.Forms.MessageBox]::Show("Deploy thành công. Nhớ RESTART máy kiosk để áp dụng autologin + autostart.", "Xong", "OK", "Information") | Out-Null
        } else {
            [System.Windows.Forms.MessageBox]::Show("Deploy thất bại hoặc chưa hoàn tất đúng ý. Xem log để biết chi tiết.", "Lỗi", "OK", "Error") | Out-Null
        }
    }
})

$btnDeploy.Add_Click({
    $ip = $txtIp.Text.Trim()
    $sshUser = $txtUser.Text.Trim()
    $sshPass = $txtPass.Text
    $sudoPass = if ([string]::IsNullOrEmpty($txtSudoPass.Text)) { $sshPass } else { $txtSudoPass.Text }
    $kioskUser = $txtKioskUser.Text.Trim()
    $appExec = $txtAppExec.Text.Trim()

    if (-not $ip -or -not $sshUser -or -not $sshPass) {
        [System.Windows.Forms.MessageBox]::Show("Nhập đủ IP, SSH user, SSH password.", "Thiếu thông tin", "OK", "Warning") | Out-Null
        return
    }
    $toggleMode = if ($radioHide.Checked) { "hide" } elseif ($radioShow.Checked) { "show" } else { "" }

    if (-not $chk1.Checked -and -not $chk2.Checked -and [string]::IsNullOrEmpty($toggleMode)) {
        [System.Windows.Forms.MessageBox]::Show("Chọn ít nhất 1 hành động (Script 1, Script 2, hoặc Ẩn/Hiện Top Bar).", "Thiếu lựa chọn", "OK", "Warning") | Out-Null
        return
    }
    if (-not $PlinkPath -or -not $PscpPath) {
        [System.Windows.Forms.MessageBox]::Show("Không tìm thấy plink.exe/pscp.exe. Cài PuTTY trước.", "Thiếu công cụ", "OK", "Error") | Out-Null
        return
    }

    $btnDeploy.Enabled = $false
    $txtLog.Clear()

    $script:DeployJob = Start-Job -ScriptBlock $DeployScriptBlock -ArgumentList @(
        $PlinkPath, $PscpPath, $ip, $sshUser, $sshPass, $sudoPass, $kioskUser, $appExec,
        $toggleMode, $chk1.Checked, $chk2.Checked, $Script1Path, $Script2Path, $Script3Path
    )
    $DeployTimer.Start()
})

[void]$form.ShowDialog()
