@echo off
setlocal

echo ========================================================
echo        🚀 MEMAX OTT - STARTING REDIS IN DOCKER
echo ========================================================
echo.

docker --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Docker is not installed or not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

echo [INFO] Pulling and running Redis container on port 6379...
docker kill memax-redis >nul 2>&1
docker rm memax-redis >nul 2>&1

docker run -d --name memax-redis -p 6379:6379 redis:alpine

if %ERRORLEVEL% EQU 0 (
    echo [OK] Redis is now running in Docker!
) else (
    echo [ERROR] Failed to start Redis in Docker.
)

pause
