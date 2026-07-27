# ClaudeConfigAudit.ps1 — GUI kiểm tra project nào còn copy tay ".claude" trùng
# với repo config KZTEK này, để biết an toàn xóa phần nào sau khi đã chuyển
# sang cơ chế junction user-level (xem docs/SETUP-GLOBAL.md).
#
# KHÔNG tự xóa gì khi quét — chỉ báo cáo. Xóa (nếu chọn) luôn đưa vào Thùng rác
# (Recycle Bin), không xóa vĩnh viễn, và chỉ cho phép xóa các mục được đánh giá
# "An toàn xóa" (giống hệt repo, không có tùy biến riêng).
#
# Chạy (double-click hoặc):
#   powershell -sta -File scripts\windows-tools\ClaudeConfigAudit.ps1
#
# Script tự relaunch ở chế độ STA nếu chưa đúng apartment state (bắt buộc cho WinForms).

if ([System.Threading.Thread]::CurrentThread.GetApartmentState() -ne 'STA') {
    Start-Process powershell -ArgumentList "-NoProfile -STA -ExecutionPolicy Bypass -File `"$PSCommandPath`""
    exit
}

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName Microsoft.VisualBasic

# ─────────────────────────────────────────────────────────────
# Đường dẫn repo (script nằm ở <repo>\scripts\windows-tools\)
$ScriptDir = Split-Path -Parent $PSCommandPath
$ScriptsDir = Split-Path -Parent $ScriptDir
$RepoRoot = Split-Path -Parent $ScriptsDir
$RepoClaude = Join-Path $RepoRoot ".claude"
$HomeClaude = Join-Path $env:USERPROFILE ".claude"

if (-not (Test-Path -LiteralPath $RepoClaude)) {
    [System.Windows.Forms.MessageBox]::Show(
        "Không tìm thấy '$RepoClaude'. Script phải nằm trong <repo>\scripts\windows-tools\ của repo config KZTEK.",
        "Lỗi", "OK", "Error") | Out-Null
    exit 1
}

# Các thư mục con hạ tầng cần so sánh: tên trong project  =>  tên tương ứng trong repo
$SubfoldersToCompare = [ordered]@{
    'agents'     = 'agents'
    'commands'   = 'commands'
    'shared'     = 'shared'
    'templates'  = 'templates'
    'references' = 'references'
    'evals'      = 'evals'
    'hooks'      = 'hooks'
}

# Tên thư mục bỏ qua khi quét đệ quy tìm ".claude" (tránh quét node_modules/bin/obj rất chậm)
$IgnoreDirNames = @('node_modules', '.git', 'bin', 'obj', '.vs', 'packages', 'dist', 'build', '__pycache__', '.venv', 'venv')

# ─────────────────────────────────────────────────────────────
function Test-IsJunction {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return $false }
    $item = Get-Item -LiteralPath $Path -Force
    return [bool]($item.Attributes -band [IO.FileAttributes]::ReparsePoint)
}

# Quét đệ quy tìm thư mục ".claude", bỏ qua thư mục nặng, giới hạn độ sâu
function Find-ClaudeFolders {
    param([string]$Root, [int]$MaxDepth)

    $found = New-Object System.Collections.Generic.List[string]
    $stack = New-Object System.Collections.Generic.Stack[object]
    $stack.Push(@{ Path = $Root; Depth = 0 })
    $tick = 0

    while ($stack.Count -gt 0) {
        $cur = $stack.Pop()
        $tick++
        if ($tick % 200 -eq 0) { [System.Windows.Forms.Application]::DoEvents() }

        $dirs = $null
        try { $dirs = [System.IO.Directory]::GetDirectories($cur.Path) } catch { continue }

        foreach ($d in $dirs) {
            $name = Split-Path -Leaf $d
            if ($name -eq '.claude') {
                # Bỏ qua .claude thuộc chính repo này
                if ($d.TrimEnd('\') -ieq $RepoClaude.TrimEnd('\')) { continue }
                $found.Add($d)
                continue  # không cần đi sâu vào bên trong .claude
            }
            if ($IgnoreDirNames -icontains $name) { continue }
            if ($cur.Depth -lt $MaxDepth) {
                $stack.Push(@{ Path = $d; Depth = $cur.Depth + 1 })
            }
        }
    }
    return $found
}

# So sánh 1 thư mục con của project với thư mục tương ứng trong repo
function Compare-ClaudeSubfolder {
    param([string]$ProjectSubDir, [string]$RepoSubDir)

    if (Test-IsJunction -Path $ProjectSubDir) {
        return @{ Status = 'DaLaJunction'; Detail = 'Đã là junction — không cần làm gì' }
    }
    if (-not (Test-Path -LiteralPath $ProjectSubDir)) {
        return @{ Status = 'KhongTonTai'; Detail = 'Không có thư mục này trong project' }
    }
    if (-not (Test-Path -LiteralPath $RepoSubDir)) {
        return @{ Status = 'KhacBiet'; Detail = 'Repo không có thư mục tương ứng — cần xem lại thủ công' }
    }

    $projFiles = Get-ChildItem -LiteralPath $ProjectSubDir -Recurse -File -Force -ErrorAction SilentlyContinue
    $repoFiles = Get-ChildItem -LiteralPath $RepoSubDir -Recurse -File -Force -ErrorAction SilentlyContinue

    $repoMap = @{}
    foreach ($f in $repoFiles) {
        $rel = $f.FullName.Substring($RepoSubDir.Length).TrimStart('\')
        $repoMap[$rel] = $f.FullName
    }

    $diffFiles = New-Object System.Collections.Generic.List[string]
    $extraFiles = New-Object System.Collections.Generic.List[string]
    $missingFiles = New-Object System.Collections.Generic.List[string]
    $total = 0
    $seenRel = @{}

    foreach ($f in $projFiles) {
        $rel = $f.FullName.Substring($ProjectSubDir.Length).TrimStart('\')
        $seenRel[$rel] = $true
        $total++
        if (-not $repoMap.ContainsKey($rel)) {
            $extraFiles.Add($rel)
            continue
        }
        $h1 = (Get-FileHash -LiteralPath $f.FullName -Algorithm SHA256 -ErrorAction SilentlyContinue).Hash
        $h2 = (Get-FileHash -LiteralPath $repoMap[$rel] -Algorithm SHA256 -ErrorAction SilentlyContinue).Hash
        if ($h1 -ne $h2) { $diffFiles.Add($rel) }
    }
    foreach ($rel in $repoMap.Keys) {
        if (-not $seenRel.ContainsKey($rel)) { $missingFiles.Add($rel) }
    }

    $diffCount = $diffFiles.Count
    $extraCount = $extraFiles.Count
    $missingCount = $missingFiles.Count

    if ($total -eq 0) {
        return @{ Status = 'KhongTonTai'; Detail = 'Thư mục rỗng' }
    }
    if ($diffCount -eq 0 -and $extraCount -eq 0) {
        $note = if ($missingCount -gt 0) { " (repo có thêm $missingCount file mới hơn — vẫn an toàn xóa, sẽ có bản mới khi dùng junction)" } else { "" }
        return @{
            Status = 'AnToanXoa'; Detail = "$total/$total file giống hệt repo$note"
            DiffFiles = $diffFiles; ExtraFiles = $extraFiles; MissingFiles = $missingFiles
        }
    }
    return @{
        Status = 'KhacBiet'; Detail = "$diffCount file khác nội dung, $extraCount file lạ (chỉ có ở project) trong tổng $total file — CÓ THỂ đã tùy biến riêng"
        DiffFiles = $diffFiles; ExtraFiles = $extraFiles; MissingFiles = $missingFiles
    }
}

# ─────────────────────────────────────────────────────────────
# Form
$form = New-Object System.Windows.Forms.Form
$form.Text = "KZTEK — Claude Config Audit"
$form.Size = New-Object System.Drawing.Size(1180, 720)
$form.StartPosition = "CenterScreen"
$form.MinimumSize = New-Object System.Drawing.Size(900, 500)

$font = New-Object System.Drawing.Font("Segoe UI", 9)

# --- Hàng trên: chọn thư mục gốc + độ sâu + nút quét ---
$lblRoot = New-Object System.Windows.Forms.Label
$lblRoot.Text = "Thư mục gốc để quét:"
$lblRoot.Location = New-Object System.Drawing.Point(15, 15)
$lblRoot.Size = New-Object System.Drawing.Size(140, 22)
$lblRoot.Font = $font

$txtRoot = New-Object System.Windows.Forms.TextBox
$txtRoot.Location = New-Object System.Drawing.Point(160, 13)
$txtRoot.Size = New-Object System.Drawing.Size(600, 24)
$txtRoot.Font = $font
$txtRoot.Text = Split-Path -Parent $RepoRoot

$btnBrowse = New-Object System.Windows.Forms.Button
$btnBrowse.Text = "Chọn..."
$btnBrowse.Location = New-Object System.Drawing.Point(768, 12)
$btnBrowse.Size = New-Object System.Drawing.Size(70, 26)
$btnBrowse.Font = $font

$lblDepth = New-Object System.Windows.Forms.Label
$lblDepth.Text = "Độ sâu quét:"
$lblDepth.Location = New-Object System.Drawing.Point(850, 15)
$lblDepth.Size = New-Object System.Drawing.Size(80, 22)
$lblDepth.Font = $font

$numDepth = New-Object System.Windows.Forms.NumericUpDown
$numDepth.Location = New-Object System.Drawing.Point(930, 13)
$numDepth.Size = New-Object System.Drawing.Size(50, 24)
$numDepth.Minimum = 1
$numDepth.Maximum = 20
$numDepth.Value = 6
$numDepth.Font = $font

$btnScan = New-Object System.Windows.Forms.Button
$btnScan.Text = "Quét"
$btnScan.Location = New-Object System.Drawing.Point(995, 12)
$btnScan.Size = New-Object System.Drawing.Size(150, 26)
$btnScan.Font = New-Object System.Drawing.Font("Segoe UI", 9, [System.Drawing.FontStyle]::Bold)
$btnScan.BackColor = [System.Drawing.Color]::FromArgb(37, 28, 83)   # Navy KZTEK
$btnScan.ForeColor = [System.Drawing.Color]::White

# --- Banner trạng thái junction global ---
$lblJunction = New-Object System.Windows.Forms.Label
$lblJunction.Location = New-Object System.Drawing.Point(15, 45)
$lblJunction.Size = New-Object System.Drawing.Size(1130, 22)
$lblJunction.Font = $font

function Update-JunctionBanner {
    # Tên 9 junction THẬT ở ~/.claude (khác với tên thư mục con phía project — vd 'hooks-kztek' chứ không phải 'hooks')
    $globalJunctionNames = @('agents', 'commands', 'shared', 'templates', 'references', 'evals', 'hooks-kztek', 'scripts', 'lessons')
    $ok = 0; $total = $globalJunctionNames.Count
    foreach ($name in $globalJunctionNames) {
        $link = Join-Path $HomeClaude $name
        if (Test-IsJunction -Path $link) { $ok++ }
    }
    if ($ok -eq $total) {
        $lblJunction.Text = "Junction toàn cục ($HomeClaude): OK — $ok/$total thư mục đã trỏ về repo. An toàn dọn project theo báo cáo bên dưới."
        $lblJunction.ForeColor = [System.Drawing.Color]::FromArgb(0, 130, 0)
    } else {
        $lblJunction.Text = "Junction toàn cục ($HomeClaude): CHƯA ĐỦ — $ok/$total thư mục. Chạy scripts\link-global.ps1 TRƯỚC KHI xóa bất kỳ project nào."
        $lblJunction.ForeColor = [System.Drawing.Color]::FromArgb(240, 89, 34)   # Cam KZTEK
    }
}
Update-JunctionBanner

# --- Log quét (dòng tiến trình) ---
$txtLog = New-Object System.Windows.Forms.TextBox
$txtLog.Location = New-Object System.Drawing.Point(15, 72)
$txtLog.Size = New-Object System.Drawing.Size(1130, 50)
$txtLog.Multiline = $true
$txtLog.ScrollBars = "Vertical"
$txtLog.ReadOnly = $true
$txtLog.Font = New-Object System.Drawing.Font("Consolas", 8.5)

function Write-Log([string]$msg) {
    $txtLog.AppendText("$msg`r`n")
    [System.Windows.Forms.Application]::DoEvents()
}

# --- Bảng kết quả ---
$grid = New-Object System.Windows.Forms.DataGridView
$grid.Location = New-Object System.Drawing.Point(15, 128)
$grid.Size = New-Object System.Drawing.Size(1130, 480)
$grid.Anchor = "Top, Bottom, Left, Right"
$grid.AllowUserToAddRows = $false
$grid.AllowUserToDeleteRows = $false
$grid.ReadOnly = $false
$grid.SelectionMode = "FullRowSelect"
$grid.AutoSizeColumnsMode = "Fill"
$grid.Font = New-Object System.Drawing.Font("Segoe UI", 8.5)
$grid.RowHeadersVisible = $false

$colChon = New-Object System.Windows.Forms.DataGridViewCheckBoxColumn
$colChon.Name = "Chon"
$colChon.HeaderText = "Chọn"
$colChon.FillWeight = 40

$colProject = New-Object System.Windows.Forms.DataGridViewTextBoxColumn
$colProject.Name = "Project"
$colProject.HeaderText = "Project"
$colProject.ReadOnly = $true
$colProject.FillWeight = 220

$colItem = New-Object System.Windows.Forms.DataGridViewTextBoxColumn
$colItem.Name = "Item"
$colItem.HeaderText = "Mục"
$colItem.ReadOnly = $true
$colItem.FillWeight = 90

$colStatus = New-Object System.Windows.Forms.DataGridViewTextBoxColumn
$colStatus.Name = "Status"
$colStatus.HeaderText = "Trạng thái"
$colStatus.ReadOnly = $true
$colStatus.FillWeight = 160

$colDetail = New-Object System.Windows.Forms.DataGridViewTextBoxColumn
$colDetail.Name = "Detail"
$colDetail.HeaderText = "Chi tiết"
$colDetail.ReadOnly = $true
$colDetail.FillWeight = 300

$colPath = New-Object System.Windows.Forms.DataGridViewTextBoxColumn
$colPath.Name = "Path"
$colPath.HeaderText = "Đường dẫn"
$colPath.ReadOnly = $true
$colPath.FillWeight = 300

$grid.Columns.Add($colChon) | Out-Null
$grid.Columns.Add($colProject) | Out-Null
$grid.Columns.Add($colItem) | Out-Null
$grid.Columns.Add($colStatus) | Out-Null
$grid.Columns.Add($colDetail) | Out-Null
$grid.Columns.Add($colPath) | Out-Null

$grid.add_CellFormatting({
    param($s, $e)
    if ($e.ColumnIndex -eq $colStatus.Index -and $e.RowIndex -ge 0) {
        $val = $grid.Rows[$e.RowIndex].Cells["Status"].Value
        switch ($val) {
            "An toàn xóa"     { $e.CellStyle.BackColor = [System.Drawing.Color]::FromArgb(198, 239, 206); $e.CellStyle.ForeColor = [System.Drawing.Color]::FromArgb(0, 97, 0) }
            "Khác biệt"       { $e.CellStyle.BackColor = [System.Drawing.Color]::FromArgb(255, 235, 156); $e.CellStyle.ForeColor = [System.Drawing.Color]::FromArgb(156, 87, 0) }
            "Đã là junction"  { $e.CellStyle.BackColor = [System.Drawing.Color]::FromArgb(197, 217, 241); $e.CellStyle.ForeColor = [System.Drawing.Color]::FromArgb(31, 73, 125) }
            "Không tồn tại"   { $e.CellStyle.BackColor = [System.Drawing.Color]::White; $e.CellStyle.ForeColor = [System.Drawing.Color]::Gray }
        }
    }
})

# --- Hàng dưới: nút xóa + xuất báo cáo + đếm ---
$lblCount = New-Object System.Windows.Forms.Label
$lblCount.Location = New-Object System.Drawing.Point(15, 614)
$lblCount.Size = New-Object System.Drawing.Size(500, 22)
$lblCount.Anchor = "Bottom, Left"
$lblCount.Font = $font

$btnSelectAllSafe = New-Object System.Windows.Forms.Button
$btnSelectAllSafe.Text = "Chọn tất cả mục 'An toàn xóa'"
$btnSelectAllSafe.Location = New-Object System.Drawing.Point(15, 640)
$btnSelectAllSafe.Size = New-Object System.Drawing.Size(220, 30)
$btnSelectAllSafe.Anchor = "Bottom, Left"
$btnSelectAllSafe.Font = $font

$btnDelete = New-Object System.Windows.Forms.Button
$btnDelete.Text = "Xóa mục đã chọn (vào Thùng rác)"
$btnDelete.Location = New-Object System.Drawing.Point(245, 640)
$btnDelete.Size = New-Object System.Drawing.Size(240, 30)
$btnDelete.Anchor = "Bottom, Left"
$btnDelete.Font = New-Object System.Drawing.Font("Segoe UI", 9, [System.Drawing.FontStyle]::Bold)
$btnDelete.BackColor = [System.Drawing.Color]::FromArgb(240, 89, 34)   # Cam KZTEK
$btnDelete.ForeColor = [System.Drawing.Color]::White

$btnOpenFolder = New-Object System.Windows.Forms.Button
$btnOpenFolder.Text = "Mở thư mục"
$btnOpenFolder.Location = New-Object System.Drawing.Point(495, 640)
$btnOpenFolder.Size = New-Object System.Drawing.Size(130, 30)
$btnOpenFolder.Anchor = "Bottom, Left"
$btnOpenFolder.Font = $font

$btnDetail = New-Object System.Windows.Forms.Button
$btnDetail.Text = "Xem chi tiết khác biệt"
$btnDetail.Location = New-Object System.Drawing.Point(635, 640)
$btnDetail.Size = New-Object System.Drawing.Size(180, 30)
$btnDetail.Anchor = "Bottom, Left"
$btnDetail.Font = $font

$btnExport = New-Object System.Windows.Forms.Button
$btnExport.Text = "Xuất báo cáo (.csv)"
$btnExport.Location = New-Object System.Drawing.Point(1010, 640)
$btnExport.Size = New-Object System.Drawing.Size(135, 30)
$btnExport.Anchor = "Bottom, Right"
$btnExport.Font = $font

$form.Controls.AddRange(@($lblRoot, $txtRoot, $btnBrowse, $lblDepth, $numDepth, $btnScan,
    $lblJunction, $txtLog, $grid, $lblCount, $btnSelectAllSafe, $btnDelete, $btnOpenFolder, $btnDetail, $btnExport))

# ─────────────────────────────────────────────────────────────
# Sự kiện
$btnBrowse.add_Click({
    $dlg = New-Object System.Windows.Forms.FolderBrowserDialog
    $dlg.Description = "Chọn thư mục gốc chứa các project cần kiểm tra"
    $dlg.SelectedPath = $txtRoot.Text
    if ($dlg.ShowDialog() -eq "OK") { $txtRoot.Text = $dlg.SelectedPath }
})

$btnScan.add_Click({
    $root = $txtRoot.Text
    if (-not (Test-Path -LiteralPath $root)) {
        [System.Windows.Forms.MessageBox]::Show("Thư mục gốc không tồn tại.", "Lỗi", "OK", "Error") | Out-Null
        return
    }
    Update-JunctionBanner
    $grid.Rows.Clear()
    $txtLog.Clear()
    $script:RowDetailMap = @{}
    $btnScan.Enabled = $false
    Write-Log "Đang quét '$root' (độ sâu $($numDepth.Value))..."

    $claudeDirs = Find-ClaudeFolders -Root $root -MaxDepth ([int]$numDepth.Value)

    Write-Log "Tìm thấy $($claudeDirs.Count) thư mục '.claude' (không tính repo này)."

    $safeCount = 0; $diffCount = 0
    foreach ($claudeDir in $claudeDirs) {
        $projectRoot = Split-Path -Parent $claudeDir
        $projectName = Split-Path -Leaf $projectRoot
        Write-Log "  - $projectName ($projectRoot)"

        foreach ($name in $SubfoldersToCompare.Keys) {
            $projSub = Join-Path $claudeDir $name
            $repoSub = Join-Path $RepoClaude $SubfoldersToCompare[$name]
            $result = Compare-ClaudeSubfolder -ProjectSubDir $projSub -RepoSubDir $repoSub

            $statusText = switch ($result.Status) {
                'AnToanXoa'      { $safeCount++; "An toàn xóa" }
                'KhacBiet'       { $diffCount++; "Khác biệt" }
                'DaLaJunction'   { "Đã là junction" }
                'KhongTonTai'    { "Không tồn tại" }
            }
            $rowIdx = $grid.Rows.Add($false, $projectName, $name, $statusText, $result.Detail, $projSub)
            if ($result.Status -ne 'AnToanXoa') { $grid.Rows[$rowIdx].Cells["Chon"].ReadOnly = $true }
            $script:RowDetailMap[$rowIdx] = $result
        }
        [System.Windows.Forms.Application]::DoEvents()
    }

    Write-Log "Xong. $safeCount mục an toàn xóa, $diffCount mục khác biệt cần xem lại thủ công."
    $lblCount.Text = "Tổng $($grid.Rows.Count) dòng — $safeCount an toàn xóa, $diffCount khác biệt (không thể chọn xóa)."
    $btnScan.Enabled = $true
})

$btnSelectAllSafe.add_Click({
    foreach ($row in $grid.Rows) {
        if ($row.Cells["Status"].Value -eq "An toàn xóa") { $row.Cells["Chon"].Value = $true }
    }
})

$btnOpenFolder.add_Click({
    if ($grid.CurrentRow -eq $null) {
        [System.Windows.Forms.MessageBox]::Show("Chưa chọn dòng nào — bấm vào 1 dòng trong bảng trước.", "Thông báo", "OK", "Information") | Out-Null
        return
    }
    $path = $grid.CurrentRow.Cells["Path"].Value
    if (-not (Test-Path -LiteralPath $path)) {
        [System.Windows.Forms.MessageBox]::Show("Thư mục không còn tồn tại (có thể đã bị xóa hoặc chưa từng có):`r`n$path", "Thông báo", "OK", "Information") | Out-Null
        return
    }
    Start-Process explorer.exe -ArgumentList "`"$path`""
})

$btnDetail.add_Click({
    if ($grid.CurrentRow -eq $null) {
        [System.Windows.Forms.MessageBox]::Show("Chưa chọn dòng nào — bấm vào 1 dòng trong bảng trước.", "Thông báo", "OK", "Information") | Out-Null
        return
    }
    $rowIdx = $grid.CurrentRow.Index
    $result = $script:RowDetailMap[$rowIdx]
    $projectName = $grid.CurrentRow.Cells["Project"].Value
    $itemName = $grid.CurrentRow.Cells["Item"].Value

    if ($null -eq $result -or ($null -eq $result.DiffFiles -and $null -eq $result.ExtraFiles -and $null -eq $result.MissingFiles)) {
        [System.Windows.Forms.MessageBox]::Show("Mục này không có danh sách file chi tiết (trạng thái: $($grid.CurrentRow.Cells['Status'].Value)).", "Thông báo", "OK", "Information") | Out-Null
        return
    }

    $sb = New-Object System.Text.StringBuilder
    [void]$sb.AppendLine("Project: $projectName  —  Mục: $itemName")
    [void]$sb.AppendLine("=" * 70)

    if ($result.DiffFiles.Count -gt 0) {
        [void]$sb.AppendLine("")
        [void]$sb.AppendLine("KHÁC NỘI DUNG — cùng tên nhưng nội dung khác repo ($($result.DiffFiles.Count)):")
        foreach ($f in $result.DiffFiles) { [void]$sb.AppendLine("  ~ $f") }
    }
    if ($result.ExtraFiles.Count -gt 0) {
        [void]$sb.AppendLine("")
        [void]$sb.AppendLine("FILE LẠ — chỉ có ở project, repo không có ($($result.ExtraFiles.Count)):")
        foreach ($f in $result.ExtraFiles) { [void]$sb.AppendLine("  + $f") }
    }
    if ($result.MissingFiles.Count -gt 0) {
        [void]$sb.AppendLine("")
        [void]$sb.AppendLine("FILE THIẾU — chỉ có ở repo, project chưa có ($($result.MissingFiles.Count)):")
        foreach ($f in $result.MissingFiles) { [void]$sb.AppendLine("  - $f") }
    }
    if ($result.DiffFiles.Count -eq 0 -and $result.ExtraFiles.Count -eq 0 -and $result.MissingFiles.Count -eq 0) {
        [void]$sb.AppendLine("")
        [void]$sb.AppendLine("Không có khác biệt nào.")
    }

    $detailForm = New-Object System.Windows.Forms.Form
    $detailForm.Text = "Chi tiết khác biệt — $projectName / $itemName"
    $detailForm.Size = New-Object System.Drawing.Size(760, 560)
    $detailForm.StartPosition = "CenterParent"

    $txtDetail = New-Object System.Windows.Forms.TextBox
    $txtDetail.Multiline = $true
    $txtDetail.ScrollBars = "Vertical"
    $txtDetail.ReadOnly = $true
    $txtDetail.Dock = "Fill"
    $txtDetail.Font = New-Object System.Drawing.Font("Consolas", 9)
    $txtDetail.Text = $sb.ToString()

    $detailForm.Controls.Add($txtDetail)
    $detailForm.ShowDialog($form) | Out-Null
})

$btnDelete.add_Click({
    $selected = @($grid.Rows | Where-Object { $_.Cells["Chon"].Value -eq $true -and $_.Cells["Status"].Value -eq "An toàn xóa" })
    if ($selected.Count -eq 0) {
        [System.Windows.Forms.MessageBox]::Show("Chưa chọn mục nào (chỉ có thể xóa mục 'An toàn xóa').", "Thông báo", "OK", "Information") | Out-Null
        return
    }
    $list = ($selected | ForEach-Object { "  - $($_.Cells['Path'].Value)" }) -join "`r`n"
    $confirm = [System.Windows.Forms.MessageBox]::Show(
        "Sẽ đưa $($selected.Count) thư mục sau vào Thùng rác (Recycle Bin, có thể khôi phục):`r`n`r`n$list",
        "Xác nhận xóa", "YesNo", "Warning")
    if ($confirm -ne "Yes") { return }

    $okCount = 0; $errCount = 0
    foreach ($row in $selected) {
        $path = $row.Cells["Path"].Value
        try {
            [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteDirectory(
                $path, 'OnlyErrorDialogs', 'SendToRecycleBin')
            $row.Cells["Status"].Value = "Đã xóa (Thùng rác)"
            $row.Cells["Chon"].ReadOnly = $true
            $okCount++
        } catch {
            Write-Log "  LỖI xóa '$path': $($_.Exception.Message)"
            $errCount++
        }
    }
    [System.Windows.Forms.MessageBox]::Show("Đã xóa $okCount mục. Lỗi: $errCount.", "Kết quả", "OK", "Information") | Out-Null
})

$btnExport.add_Click({
    $dlg = New-Object System.Windows.Forms.SaveFileDialog
    $dlg.Filter = "CSV|*.csv"
    $dlg.FileName = "claude-config-audit-report.csv"
    if ($dlg.ShowDialog() -ne "OK") { return }

    $rows = foreach ($row in $grid.Rows) {
        [pscustomobject]@{
            Project    = $row.Cells["Project"].Value
            Muc        = $row.Cells["Item"].Value
            TrangThai  = $row.Cells["Status"].Value
            ChiTiet    = $row.Cells["Detail"].Value
            DuongDan   = $row.Cells["Path"].Value
        }
    }
    $rows | Export-Csv -Path $dlg.FileName -NoTypeInformation -Encoding UTF8
    [System.Windows.Forms.MessageBox]::Show("Đã lưu báo cáo: $($dlg.FileName)", "Xong", "OK", "Information") | Out-Null
})

[System.Windows.Forms.Application]::Run($form)

