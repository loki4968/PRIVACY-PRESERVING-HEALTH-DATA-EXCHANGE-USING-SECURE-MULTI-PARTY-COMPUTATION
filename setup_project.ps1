# Health Data Exchange - Project Setup Script
Write-Host "========================================" -ForegroundColor Green
Write-Host "Health Data Exchange - Project Setup" -ForegroundColor Green  
Write-Host "========================================" -ForegroundColor Green

Write-Host ""
Write-Host "[1/5] Setting up virtual environment..." -ForegroundColor Yellow

# Check if virtual environment exists
if (Test-Path "venv") {
    Write-Host "Virtual environment found. Activating..." -ForegroundColor Cyan
    & "venv\Scripts\Activate.ps1"
} else {
    Write-Host "Creating virtual environment..." -ForegroundColor Cyan
    python -m venv venv
    & "venv\Scripts\Activate.ps1"
}

Write-Host ""
Write-Host "[2/5] Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

Write-Host ""
Write-Host "[3/5] Installing core dependencies..." -ForegroundColor Yellow
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org cryptography==41.0.7 fastapi==0.104.1 uvicorn==0.24.0

Write-Host ""
Write-Host "[4/5] Installing all requirements..." -ForegroundColor Yellow
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

Write-Host ""
Write-Host "[5/5] Testing imports..." -ForegroundColor Yellow

try {
    python -c "import cryptography; print('✅ cryptography installed')"
    python -c "import fastapi; print('✅ fastapi installed')"
    python -c "import sqlalchemy; print('✅ sqlalchemy installed')"
    python -c "import pydantic; print('✅ pydantic installed')"
    python -c "try: import sklearn; print('✅ scikit-learn installed'); except: print('⚠️ scikit-learn not installed (optional)')"
    python -c "try: import pandas; print('✅ pandas installed'); except: print('⚠️ pandas not installed (optional)')"
} catch {
    Write-Host "Some imports failed, but core dependencies should work" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

Write-Host ""
Write-Host "🚀 Starting backend server..." -ForegroundColor Cyan
Write-Host "Server will be available at: http://localhost:8000" -ForegroundColor White
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow

Set-Location backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
