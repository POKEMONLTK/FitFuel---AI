@echo off
title FitFuel AI - From Movement to Nutrition
cd /d "%~dp0"
echo ========================================================
echo         FitFuel AI - From Movement to Nutrition
echo ========================================================
echo.

if exist ".venv\Scripts\streamlit.exe" (
    echo [OK] Virtual environment detected.
) else (
    echo [INFO] Creating Python virtual environment...
    "C:\Users\kunal\AppData\Local\Programs\Python\Python311\python.exe" -m venv .venv 2>nul || python -m venv .venv
    call .venv\Scripts\activate.bat
    echo [INFO] Installing dependencies from requirements.txt...
    pip install -r requirements.txt
)

call .venv\Scripts\activate.bat
echo [INFO] Starting Streamlit App on http://localhost:8501 ...
streamlit run app.py
pause
