@echo off
echo ========================================
echo Health Data Exchange - Project Setup
echo ========================================

echo.
echo [1/5] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    echo Creating new virtual environment...
    python -m venv venv
    call venv\Scripts\activate.bat
)

echo.
echo [2/5] Upgrading pip...
python -m pip install --upgrade pip

echo.
echo [3/5] Installing core dependencies...
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org cryptography==41.0.7

echo.
echo [4/5] Installing all requirements...
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements.txt

echo.
echo [5/5] Testing imports...
python -c "import cryptography; print('✅ cryptography installed')"
python -c "import fastapi; print('✅ fastapi installed')"
python -c "import sqlalchemy; print('✅ sqlalchemy installed')"
python -c "try: import sklearn; print('✅ scikit-learn installed'); except: print('⚠️ scikit-learn not installed')"

echo.
echo ========================================
echo Setup Complete! Starting server...
echo ========================================

echo.
echo Starting backend server...
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

pause
