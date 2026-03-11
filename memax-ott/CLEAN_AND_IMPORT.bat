@echo off
echo ========================================
echo Netflix Dataset Cleaner
echo ========================================
echo.

cd backend

echo Checking Netflix dataset...
if not exist "app\data\raw\Netflix_dataset.csv" (
    echo ERROR: Netflix_dataset.csv not found!
    pause
    exit /b 1
)

for %%A in ("app\data\raw\Netflix_dataset.csv") do set size=%%~zA
if %size% LSS 100 (
    echo ERROR: Netflix_dataset.csv is empty or too small
    echo File size: %size% bytes
    echo.
    echo Please paste your Netflix CSV data into:
    echo   backend\app\data\raw\Netflix_dataset.csv
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

echo ========================================
echo Step 1: Cleaning and Processing Dataset
echo ========================================
echo.
echo This will:
echo - Remove duplicates
echo - Clean and standardize all fields
echo - Validate data
echo - Create cleaned version
echo.

python clean_netflix_dataset.py

if errorlevel 1 (
    echo.
    echo Cleaning failed! Check errors above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Step 2: Import Cleaned Dataset
echo ========================================
echo.

set /p import="Import cleaned dataset to database? (y/n): "
if /i "%import%"=="y" (
    echo.
    echo Importing cleaned dataset...
    python import_dataset.py app/data/raw/Netflix_dataset_cleaned.csv
    
    echo.
    echo ========================================
    echo Import Complete!
    echo ========================================
    echo.
    echo Next steps:
    echo 1. Start backend: python -m app.main
    echo 2. Start frontend: cd ..\frontend ^&^& npm run dev
    echo 3. Visit: http://localhost:3000
    echo.
    echo Or simply run: START.bat
)

echo.
pause
