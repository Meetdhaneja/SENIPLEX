@echo off
setlocal EnableDelayedExpansion

echo ========================================================
echo        🚀 MEMAX OTT - STARTING CELERY WORKER
echo ========================================================
echo.

cd backend

:: Ensure Celery and Redis dependencies are installed
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo [INFO] Installing Celery Eventlet pool for Windows...
    pip install celery redis eventlet >nul 2>&1
    echo [OK] Dependencies verified.
    
    echo.
    echo [RUNNING] Starting Celery Worker (Eventlet Pool)...
    celery -A app.core.celery_app worker --loglevel=info -P eventlet
) else (
    echo [INFO] Installing Celery Eventlet pool for Windows globally...
    pip install celery redis eventlet >nul 2>&1
    echo [OK] Dependencies verified.
    
    echo.
    echo [RUNNING] Starting Celery Worker (Eventlet Pool)...
    celery -A app.core.celery_app worker --loglevel=info -P eventlet
)
