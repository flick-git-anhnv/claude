@echo off
setlocal EnableDelayedExpansion

REM ============================================================
REM  KZTEK Agent Dashboard — start.bat
REM  One-command startup for Windows.
REM  Run from ANY directory; resolves paths relative to this file.
REM ============================================================

set "SCRIPT_DIR=%~dp0"
set "BACKEND_DIR=%SCRIPT_DIR%backend"
set "FRONTEND_DIR=%SCRIPT_DIR%frontend"
set "DIST_DIR=%FRONTEND_DIR%\dist"
set "PORT=7770"
set "URL=http://127.0.0.1:%PORT%"

echo.
echo  ========================================
echo   KZTEK Agent Dashboard  ^|  port %PORT%
echo  ========================================

REM ── 1. Python check ──────────────────────────────────────────
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Install Python 3.10+ and add it to PATH.
    pause
    exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo  Python : %%v

REM ── 2. Backend dependencies ──────────────────────────────────
python -c "import uvicorn, fastapi, watchdog, aiosqlite" >nul 2>&1
if %errorlevel% neq 0 (
    echo  Installing backend dependencies (first run only)...
    pip install -r "%BACKEND_DIR%\requirements.txt" --quiet
    if %errorlevel% neq 0 (
        echo [ERROR] pip install failed. Check your Python environment.
        pause
        exit /b 1
    )
    echo  Dependencies installed.
) else (
    echo  Backend deps  : OK
)

REM ── 3. Frontend dist ─────────────────────────────────────────
if not exist "%DIST_DIR%\index.html" (
    echo  Frontend dist not found. Building...
    where node >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Node.js not found. Install Node.js 18+ to build the frontend.
        pause
        exit /b 1
    )
    pushd "%FRONTEND_DIR%"
    call npm install --silent
    call npm run build
    popd
    if not exist "%DIST_DIR%\index.html" (
        echo [ERROR] Frontend build failed. Check npm output above.
        pause
        exit /b 1
    )
    echo  Frontend built OK.
) else (
    echo  Frontend dist : OK
)

REM ── 4. Open browser after 2-second delay (background) ────────
echo.
echo  Starting server at %URL% ...
echo  Press Ctrl+C to stop the dashboard.
echo.
start "" cmd /c "timeout /t 2 >nul & start %URL%"

REM ── 5. Start backend (foreground — Ctrl+C to stop) ───────────
pushd "%BACKEND_DIR%"
python -m agent_dashboard
popd

endlocal
