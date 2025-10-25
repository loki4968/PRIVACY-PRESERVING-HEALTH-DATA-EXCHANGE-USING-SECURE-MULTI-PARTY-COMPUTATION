@echo off
echo ========================================
echo Health Data Exchange - Complete Setup
echo ========================================

echo.
echo [1/5] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

echo.
echo [2/5] Upgrading pip...
python -m pip install --upgrade pip

echo.
echo [3/5] Installing core dependencies...
pip install fastapi==0.104.1 uvicorn==0.24.0 python-multipart==0.0.6 sqlalchemy==2.0.23 pydantic==2.5.2 python-dotenv==1.0.0

echo.
echo [4/5] Testing installations...
python -c "import fastapi; print('✅ FastAPI OK')"
python -c "import uvicorn; print('✅ Uvicorn OK')"
python -c "import sqlalchemy; print('✅ SQLAlchemy OK')"

echo.
echo [5/5] Starting server...
echo ========================================
echo Server will be available at:
echo   http://localhost:8000
echo   http://localhost:8000/docs (API Documentation)
echo ========================================
echo.

cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

pause
