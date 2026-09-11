# FitFuel AI - PowerShell 1-Click Launcher
Set-Location $PSScriptRoot

Write-Host "========================================================" -ForegroundColor Green
Write-Host "        FitFuel AI - From Movement to Nutrition" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green
Write-Host ""

if (Test-Path ".\.venv\Scripts\streamlit.exe") {
    Write-Host "[OK] Virtual environment ready." -ForegroundColor Cyan
} else {
    Write-Host "[INFO] Creating virtual environment (.venv)..." -ForegroundColor Yellow
    & "C:\Users\kunal\AppData\Local\Programs\Python\Python311\python.exe" -m venv .venv
    .\.venv\Scripts\Activate.ps1
    Write-Host "[INFO] Installing requirements..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

.\.venv\Scripts\Activate.ps1
Write-Host "[INFO] Launching FitFuel AI at http://localhost:8501 ..." -ForegroundColor Green
streamlit run app.py
