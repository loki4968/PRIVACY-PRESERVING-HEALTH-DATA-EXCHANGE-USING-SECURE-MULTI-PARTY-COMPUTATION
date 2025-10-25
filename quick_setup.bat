@echo off
echo ========================================
echo Quick Setup - Health Data Exchange
echo ========================================

echo.
echo [1/4] Installing basic requirements...
pip install --upgrade pip
pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org -r requirements-simple.txt

echo.
echo [2/4] Testing basic imports...
python -c "import fastapi; print('✅ FastAPI installed')"
python -c "import sqlalchemy; print('✅ SQLAlchemy installed')"
python -c "import uvicorn; print('✅ Uvicorn installed')"

echo.
echo [3/4] Testing cryptography (fallback mode)...
python -c "try: import cryptography; print('✅ Cryptography available'); except: print('⚠️ Using fallback encryption')"

echo.
echo [4/4] Starting server...
cd backend
echo Server starting at: http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

pause
