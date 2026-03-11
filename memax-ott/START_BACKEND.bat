@echo off
echo ============================================================
echo  MEMAX OTT - PostgreSQL Backend Server
echo ============================================================
echo.
echo Database: Netflix
echo Host: localhost:5432
echo Port: 8000
echo.
echo Starting backend server...
echo.

cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
