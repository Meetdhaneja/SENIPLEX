@echo off
echo ========================================
echo Testing Dataset Import
echo ========================================
echo.

cd backend

if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate
) else (
    echo Virtual environment not found!
    echo Please run SETUP.bat first
    pause
    exit /b 1
)

echo Importing sample dataset...
echo.

python import_dataset.py app/data/raw/sample_movies.csv

echo.
echo ========================================
echo.
echo Sample import complete!
echo.
echo Next steps:
echo 1. Check the results above
echo 2. Try importing your own dataset
echo 3. Start the application with START.bat
echo.
pause
