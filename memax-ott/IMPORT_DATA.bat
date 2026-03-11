@echo off
echo ========================================
echo MEMAX OTT - Dataset Import Tool
echo ========================================
echo.

cd backend

echo Checking for datasets in app/data/raw/...
echo.

if exist "app\data\raw\*.csv" (
    echo Found CSV files:
    dir /b app\data\raw\*.csv
    echo.
) else (
    echo No CSV files found in app/data/raw/
    echo.
    echo Please place your dataset file in:
    echo   backend\app\data\raw\
    echo.
    echo Supported formats:
    echo   - netflix.csv
    echo   - movies.csv
    echo   - dataset.csv
    echo.
    echo Or download from:
    echo   https://www.kaggle.com/datasets/shivamb/netflix-shows
    echo.
    pause
    exit /b 1
)

echo Starting import...
echo.

if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate
) else (
    echo Virtual environment not found!
    echo Please run SETUP.bat first
    pause
    exit /b 1
)

python import_dataset.py

echo.
echo ========================================
pause
