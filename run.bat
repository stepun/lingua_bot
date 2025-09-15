@echo off
REM LinguaBot Windows Startup Script

echo Starting LinguaBot...

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if .env exists
if not exist ".env" (
    echo ERROR: .env file not found!
    echo Please copy .env.example to .env and fill in your API keys.
    pause
    exit /b 1
)

REM Install/update dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create directories if they don't exist
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "exports" mkdir exports

REM Start the bot
echo Starting LinguaBot...
python main.py

pause