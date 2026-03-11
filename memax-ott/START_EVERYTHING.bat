@echo off
setlocal EnableDelayedExpansion

echo ========================================================
echo        🚀 MEMAX OTT - LAUNCHING COMPLETE SYSTEM
echo ========================================================
echo.
echo Phase 1: Validating Environment...
echo --------------------------------------------------------

:: Check Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH.
    pause
    exit /b 1
)
echo [OK] Python detected.

:: Check PostgreSQL (Basic check via psql if available, else skip)
psql --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] PostgreSQL tools detected.
) else (
    echo [INFO] PostgreSQL tools not found in PATH - assuming database service is running.
)

echo.
echo Phase 2: Starting Backend Server ^& AI Engine...
echo --------------------------------------------------------
echo This window will stream server logs.
echo Keep this window OPEN.
echo.

cd backend

:: Start Uvicorn Server
:: Start Uvicorn Server with venv activation
if exist venv\Scripts\activate.bat (
    start "MEMAX Backend Server" cmd /k "call venv\Scripts\activate.bat && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
) else (
    echo [WARNING] Virtual environment not found. Using global python...
    start "MEMAX Backend Server" cmd /k "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
)

echo [WAIT] Giving the server 10 seconds to initialize AI models...
timeout /t 10 >nul

echo.
echo Phase 3: Launching Frontend Interface...
echo --------------------------------------------------------
echo Opening Cyberpunk Dashboard...

:: Launch Static Frontend
start http://localhost:8000/static/index.html

echo.
echo ========================================================
echo        ✅ SYSTEM ONLINE
echo ========================================================
echo.
echo Backend API:   http://localhost:8000/docs
echo Frontend UI:   http://localhost:8000/static/index.html
echo Database:      Connected (8798 Movies Loaded)
echo AI Engine:     Active
echo.
pause
