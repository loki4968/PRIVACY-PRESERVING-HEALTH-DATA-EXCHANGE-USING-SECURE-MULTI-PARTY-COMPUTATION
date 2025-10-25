# Health Data Exchange - PowerShell Test Runner
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Health Data Exchange - Test Runner" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`n[1/5] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
    $pythonCmd = "python"
} catch {
    try {
        $pythonVersion = py --version 2>&1
        Write-Host "Found: $pythonVersion" -ForegroundColor Green
        $pythonCmd = "py"
    } catch {
        Write-Host "ERROR: Python not found. Please install Python 3.8+" -ForegroundColor Red
        exit 1
    }
}

Write-Host "`n[2/5] Checking project structure..." -ForegroundColor Yellow
$requiredFiles = @(
    "backend\tests\test_auth.py",
    "backend\tests\test_smpc.py", 
    "backend\tests\conftest.py",
    "validate_project.py",
    "docker-compose.yml",
    "Dockerfile.backend"
)

$missingFiles = @()
foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "✅ $file" -ForegroundColor Green
    } else {
        Write-Host "❌ $file" -ForegroundColor Red
        $missingFiles += $file
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host "ERROR: Missing required files" -ForegroundColor Red
    exit 1
}

Write-Host "`n[3/5] Installing test dependencies..." -ForegroundColor Yellow
& $pythonCmd -m pip install pytest pytest-cov pytest-asyncio httpx fastapi sqlalchemy cryptography paillier

Write-Host "`n[4/5] Running project validation..." -ForegroundColor Yellow
& $pythonCmd validate_project.py

Write-Host "`n[5/5] Running backend test suite..." -ForegroundColor Yellow
Set-Location backend
& $pythonCmd -m pytest tests\ -v --tb=short

Set-Location ..
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Test execution completed!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
