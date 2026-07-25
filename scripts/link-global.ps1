# ============================================================================
#  link-global.ps1 — Liên kết config KZTEK từ repo này vào user-level scope
# ============================================================================
#
#  MỤC ĐÍCH
#  --------
#  Claude Code đọc config theo 3 tầng: user (~/.claude) -> project (.claude)
#  -> local. Script này tạo junction từ ~/.claude trỏ vào repo, để MỌI project
#  trên máy dùng chung một bộ agents/commands/templates/scripts — không copy tay.
#
#  File thật vẫn nằm trong repo (git quản lý). ~/.claude chỉ chứa con trỏ.
#  Sửa qua ~/.claude\agents\cto.md == sửa file trong repo == git thấy ngay.
#
#  CÁCH DÙNG
#  ---------
#      powershell -ExecutionPolicy Bypass -File scripts\link-global.ps1
#      powershell -ExecutionPolicy Bypass -File scripts\link-global.ps1 -WhatIf
#      powershell -ExecutionPolicy Bypass -File scripts\link-global.ps1 -Unlink
#
#  Idempotent: chạy lại nhiều lần vô hại. KHÔNG cần quyền admin (junction, không
#  phải symlink). Chạy lại sau khi di chuyển repo sang đường dẫn khác.
#
#  ⚠️  CẢNH BÁO QUAN TRỌNG — KHÔNG BAO GIỜ tạo junction vào bên trong working
#      tree của một git repo khác. Git đi XUYÊN junction và coi nó là thư mục
#      thật, nên `git add -A` ở project đó sẽ hút toàn bộ file của repo này vào
#      repo đó. Chỉ junction tại ~/.claude — chỗ này nằm ngoài mọi working tree.
# ============================================================================

[CmdletBinding(SupportsShouldProcess = $true)]
param(
    # Xoá toàn bộ junction đã tạo (file thật trong repo KHÔNG bị ảnh hưởng)
    [switch]$Unlink
)

$ErrorActionPreference = 'Stop'

# --- Xác định đường dẫn ------------------------------------------------------
# $PSScriptRoot = <repo>\scripts  ->  repo root là thư mục cha
$RepoRoot   = Split-Path -Parent $PSScriptRoot
$RepoClaude = Join-Path $RepoRoot '.claude'
$HomeClaude = Join-Path $env:USERPROFILE '.claude'

# --- Bảng mapping: tên junction ở ~/.claude  =>  thư mục nguồn trong repo ----
#  hooks-kztek: KHÔNG dùng tên 'hooks' vì ~/.claude\hooks đã có hook riêng của
#  máy (code-graph-lesson-reminder.js) không nằm trong repo này.
$Links = [ordered]@{
    'agents'      = (Join-Path $RepoClaude 'agents')
    'commands'    = (Join-Path $RepoClaude 'commands')
    'shared'      = (Join-Path $RepoClaude 'shared')
    'templates'   = (Join-Path $RepoClaude 'templates')
    'references'  = (Join-Path $RepoClaude 'references')
    'evals'       = (Join-Path $RepoClaude 'evals')
    'hooks-kztek' = (Join-Path $RepoClaude 'hooks')
    'scripts'     = (Join-Path $RepoRoot   'scripts')
}

# ============================================================================
#  Hàm phụ trợ
# ============================================================================

function Test-IsJunction {
    param([string]$Path)
    if (-not (Test-Path -LiteralPath $Path)) { return $false }
    $item = Get-Item -LiteralPath $Path -Force
    # ReparsePoint = junction hoặc symlink
    return [bool]($item.Attributes -band [IO.FileAttributes]::ReparsePoint)
}

function Get-JunctionTarget {
    param([string]$Path)
    try {
        $item = Get-Item -LiteralPath $Path -Force
        if ($item.PSObject.Properties.Name -contains 'Target' -and $item.Target) {
            return @($item.Target)[0]
        }
    } catch { }
    return $null
}

function Remove-Junction {
    param([string]$Path)
    # Dùng cmd rmdir: xoá con trỏ, KHÔNG đi vào xoá nội dung đích.
    # (Remove-Item -Recurse trên junction từng có bug xoá xuyên target ở PS cũ)
    & cmd.exe /c rmdir "$Path" 2>$null | Out-Null
    return -not (Test-Path -LiteralPath $Path)
}

function New-Junction {
    param([string]$Link, [string]$Target)
    & cmd.exe /c mklink /J "$Link" "$Target" 2>&1 | Out-Null
    return (Test-IsJunction -Path $Link)
}

# ============================================================================
#  Bắt đầu
# ============================================================================

Write-Host ''
Write-Host '  KZTEK — Liên kết config vào user-level scope' -ForegroundColor Cyan
Write-Host '  ---------------------------------------------' -ForegroundColor Cyan
Write-Host "  Repo : $RepoRoot"
Write-Host "  Home : $HomeClaude"
Write-Host ''

if (-not (Test-Path -LiteralPath $RepoClaude)) {
    throw "Không tìm thấy '$RepoClaude'. Script phải nằm trong <repo>\scripts\ của repo config KZTEK."
}
if (-not (Test-Path -LiteralPath $HomeClaude)) {
    New-Item -ItemType Directory -Path $HomeClaude -Force | Out-Null
    Write-Host "  Đã tạo $HomeClaude" -ForegroundColor Yellow
}

$results = @()

foreach ($name in $Links.Keys) {
    $link   = Join-Path $HomeClaude $name
    $target = $Links[$name]
    $status = ''
    $color  = 'Gray'

    # ---------------- Chế độ -Unlink ----------------
    if ($Unlink) {
        if (Test-IsJunction -Path $link) {
            if ($PSCmdlet.ShouldProcess($link, 'Xoá junction')) {
                if (Remove-Junction -Path $link) { $status = 'ĐÃ XOÁ'; $color = 'Yellow' }
                else                             { $status = 'XOÁ THẤT BẠI'; $color = 'Red' }
            } else { $status = 'BỎ QUA (WhatIf)'; $color = 'Gray' }
        }
        elseif (Test-Path -LiteralPath $link) {
            $status = 'BỎ QUA — thư mục thật, không phải junction'; $color = 'Yellow'
        }
        else { $status = 'không tồn tại'; $color = 'Gray' }

        $results += [pscustomobject]@{ Link = $name; Status = $status }
        Write-Host ("  {0,-14} {1}" -f $name, $status) -ForegroundColor $color
        continue
    }

    # ---------------- Chế độ tạo link ----------------
    if (-not (Test-Path -LiteralPath $target)) {
        $status = "LỖI — nguồn không tồn tại: $target"; $color = 'Red'
        $results += [pscustomobject]@{ Link = $name; Status = $status }
        Write-Host ("  {0,-14} {1}" -f $name, $status) -ForegroundColor $color
        continue
    }

    if (Test-IsJunction -Path $link) {
        $current = Get-JunctionTarget -Path $link
        if ($current -and ($current.TrimEnd('\') -ieq $target.TrimEnd('\'))) {
            $status = 'OK — đã trỏ đúng'; $color = 'Green'
            $results += [pscustomobject]@{ Link = $name; Status = $status }
            Write-Host ("  {0,-14} {1}" -f $name, $status) -ForegroundColor $color
            continue
        }
        # Junction cũ trỏ sai đích (repo đã di chuyển) -> tạo lại
        if ($PSCmdlet.ShouldProcess($link, 'Tạo lại junction (đích đã đổi)')) {
            if (-not (Remove-Junction -Path $link)) {
                $status = 'LỖI — không xoá được junction cũ'; $color = 'Red'
                $results += [pscustomobject]@{ Link = $name; Status = $status }
                Write-Host ("  {0,-14} {1}" -f $name, $status) -ForegroundColor $color
                continue
            }
        } else {
            Write-Host ("  {0,-14} BỎ QUA (WhatIf)" -f $name) -ForegroundColor Gray
            continue
        }
    }
    elseif (Test-Path -LiteralPath $link) {
        # ĐÂY LÀ THƯ MỤC THẬT — tuyệt đối không tự xoá, có thể chứa dữ liệu của user
        $count = @(Get-ChildItem -LiteralPath $link -Force -ErrorAction SilentlyContinue).Count
        if ($count -gt 0) {
            $status = "DỪNG — '$name' là thư mục thật chứa $count mục. Backup + xoá thủ công rồi chạy lại."
            $color  = 'Red'
            $results += [pscustomobject]@{ Link = $name; Status = $status }
            Write-Host ("  {0,-14} {1}" -f $name, $status) -ForegroundColor $color
            continue
        }
        # Thư mục rỗng -> an toàn để thay bằng junction
        if ($PSCmdlet.ShouldProcess($link, 'Xoá thư mục rỗng để tạo junction')) {
            Remove-Item -LiteralPath $link -Force -Confirm:$false
        } else {
            Write-Host ("  {0,-14} BỎ QUA (WhatIf)" -f $name) -ForegroundColor Gray
            continue
        }
    }

    if ($PSCmdlet.ShouldProcess($link, "Tạo junction -> $target")) {
        if (New-Junction -Link $link -Target $target) { $status = 'ĐÃ TẠO'; $color = 'Green' }
        else { $status = 'LỖI — mklink thất bại'; $color = 'Red' }
    } else { $status = 'BỎ QUA (WhatIf)'; $color = 'Gray' }

    $results += [pscustomobject]@{ Link = $name; Status = $status }
    Write-Host ("  {0,-14} {1}" -f $name, $status) -ForegroundColor $color
}

# ============================================================================
#  Tổng kết
# ============================================================================

$failed = @($results | Where-Object { $_.Status -match '^(LỖI|DỪNG|XOÁ THẤT BẠI)' })

Write-Host ''
if ($failed.Count -gt 0) {
    Write-Host "  ✗ $($failed.Count)/$($results.Count) mục có vấn đề — xem chi tiết ở trên." -ForegroundColor Red
    Write-Host ''
    exit 1
}

if ($Unlink) {
    Write-Host '  ✓ Đã bỏ liên kết. File thật trong repo KHÔNG bị ảnh hưởng.' -ForegroundColor Green
} else {
    Write-Host "  ✓ Hoàn tất $($results.Count)/$($results.Count) junction." -ForegroundColor Green
    Write-Host ''
    Write-Host '  Việc còn lại (chỉ làm 1 lần trên máy mới):' -ForegroundColor Cyan
    Write-Host '    1. Merge .claude\templates\settings-global.json vào ~\.claude\settings.json'
    Write-Host '    2. Xem docs\SETUP-GLOBAL.md để biết chi tiết và cách rollback'
}
Write-Host ''
exit 0
