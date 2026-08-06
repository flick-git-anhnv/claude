<#
.SYNOPSIS
    Cai git hook post-commit de tu dong chay sync-to-gemini.py sau moi commit
    trong repo Claude-Git.
.DESCRIPTION
    Sau khi cai, moi lan "git commit" trong repo nay ma cham vao CLAUDE.md,
    RULES.md, WORKFLOW.md, hoac .claude/{agents,commands,evals,templates,
    shared,references,hooks,lessons}/ hay scripts/ -> tu dong chay
    scripts/sync-to-gemini.py --apply de cap nhat repo GeminiGit. Hook KHONG
    bao gio lam fail commit hien tai.
.EXAMPLE
    powershell -ExecutionPolicy Bypass -File scripts\install-sync-hook.ps1
#>

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$RepoRoot = Split-Path -Parent $ScriptDir
$HookSrc = Join-Path $ScriptDir "git-hooks\post-commit"
$HooksDir = Join-Path $RepoRoot ".git\hooks"
$HookDst = Join-Path $HooksDir "post-commit"

if (-not (Test-Path $HookSrc)) {
    Write-Error "Khong tim thay hook nguon: $HookSrc"
    exit 1
}
if (-not (Test-Path $HooksDir)) {
    Write-Error "Khong tim thay $HooksDir -- day co phai la git repo khong?"
    exit 1
}

Copy-Item $HookSrc $HookDst -Force
Write-Host "[OK] Da cai git hook post-commit." -ForegroundColor Green
Write-Host "Tu gio, moi commit dung vao config dung chung se tu dong dong bo sang GeminiGit." -ForegroundColor Gray
Write-Host "Goi thu ngay bang tay: python scripts\sync-to-gemini.py --apply" -ForegroundColor Gray
