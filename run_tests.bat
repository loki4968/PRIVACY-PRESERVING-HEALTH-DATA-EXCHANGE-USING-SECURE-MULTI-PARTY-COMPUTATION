@echo off
echo ========================================
echo Health Data Exchange - Test Runner
echo ========================================

echo.
echo [1/4] Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo Python not found in PATH. Trying py...
    py --version
    if %errorlevel% neq 0 (
        echo ERROR: Python not found. Please install Python 3.8+
        pause
        exit /b 1
    )
    set PYTHON_CMD=py
) else (
    set PYTHON_CMD=python
)

echo.
echo [2/4] Installing test dependencies...
%PYTHON_CMD% -m pip install pytest pytest-cov pytest-asyncio httpx

echo.
echo [3/4] Running project validation...
%PYTHON_CMD% validate_project.py

echo.
echo [4/4] Running backend test suite...
cd backend
%PYTHON_CMD% -m pytest tests/ -v --tb=short --cov=. --cov-report=term-missing

echo.
echo ========================================
echo Test execution completed!
echo ========================================
pause
