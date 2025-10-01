@echo off
REM Start Admin Panel for LinguaBot (Windows)

echo Starting LinguaBot Admin Panel...

cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "new_venv\Scripts\activate.bat" (
    echo Virtual environment not found. Please run: python -m venv new_venv
    exit /b 1
)

REM Activate virtual environment
call new_venv\Scripts\activate.bat

REM Install requirements if needed
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo Installing FastAPI dependencies...
    pip install fastapi uvicorn
)

REM Set environment variables
set PYTHONPATH=%PYTHONPATH%;%CD%

REM Start admin panel
echo Admin panel starting on http://localhost:8081
echo Press Ctrl+C to stop
echo.

cd lingua_bot
python -m uvicorn admin_app.app:app --host 0.0.0.0 --port 8081 --reload
