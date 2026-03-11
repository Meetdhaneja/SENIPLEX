@echo off
echo ========================================
echo Starting MEMAX OTT Platform
echo ========================================
echo.

echo Starting Backend Server...
start "MEMAX Backend" cmd /k "cd backend && venv\Scripts\activate && python -m app.main"

timeout /t 3 /nobreak > nul

echo Starting Frontend Server...
start "MEMAX Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo MEMAX OTT Platform is starting...
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to stop all servers...
pause > nul

echo Stopping servers...
taskkill /FI "WindowTitle eq MEMAX Backend*" /T /F
taskkill /FI "WindowTitle eq MEMAX Frontend*" /T /F

echo.
echo All servers stopped.
pause
