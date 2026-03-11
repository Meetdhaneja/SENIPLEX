@echo off
echo ========================================
echo Import Netflix Dataset
echo ========================================
echo.

echo Your Netflix dataset file is located at:
echo backend\app\data\raw\Netflix_dataset.csv
echo.

cd backend

echo Checking if file exists and has data...
if not exist "app\data\raw\Netflix_dataset.csv" (
    echo ERROR: Netflix_dataset.csv not found!
    echo Please make sure your CSV file is in:
    echo   backend\app\data\raw\Netflix_dataset.csv
    pause
    exit /b 1
)

for %%A in ("app\data\raw\Netflix_dataset.csv") do set size=%%~zA
if %size% LSS 100 (
    echo WARNING: Netflix_dataset.csv appears to be empty or very small
    echo File size: %size% bytes
    echo.
    echo Please copy your Netflix CSV data into:
    echo   backend\app\data\raw\Netflix_dataset.csv
    echo.
    pause
    exit /b 1
)

echo File found! Size: %size% bytes
echo.

if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate
) else (
    echo Virtual environment not found!
    echo Please run SETUP.bat first
    pause
    exit /b 1
)

echo Starting import of Netflix dataset...
echo This may take a few minutes depending on file size...
echo.

python import_dataset.py app/data/raw/Netflix_dataset.csv

echo.
echo ========================================
echo.
echo Import process completed!
echo.
echo Next steps:
echo 1. Start the backend: python -m app.main
echo 2. Start the frontend: cd ..\frontend ^&^& npm run dev
echo 3. Visit: http://localhost:3000
echo.
echo Or simply run: START.bat
echo.
pause
