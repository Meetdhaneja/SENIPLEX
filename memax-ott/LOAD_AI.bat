@echo off
echo ========================================
echo MEMAX OTT - AI Model Initialization
echo ========================================
echo.

cd backend

echo Loading all AI models and building FAISS index...
echo This may take a few minutes on first run...
echo.

python initialize_ai.py

echo.
echo ========================================
echo AI Initialization Complete!
echo ========================================
echo.
pause
