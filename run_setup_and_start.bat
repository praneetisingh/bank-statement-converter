@echo off
title Bank Statement Converter Launcher
echo =====================================================================
echo    BANK STATEMENT CONVERTER -- AUTOMATIC SETUP AND LAUNCHER
echo =====================================================================
echo.

:: 1. Verify Python installation
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to your system PATH.
    echo Please install Python 3.10 or higher from https://www.python.org/
    pause
    exit /b
)

:: 2. Verify Node.js installation
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not added to your system PATH.
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b
)

echo [✓] Prerequisites checked (Python and Node.js are installed).
echo.

:: 3. Setup Backend virtual environment and install packages
echo [1/3] Setting up Python Backend...
cd backend
if not exist .venv (
    echo Creating virtual environment (.venv)...
    python -m venv .venv
)
echo Activating virtual environment and installing dependencies...
call .venv\Scripts\activate
python -m pip install --upgrade pip >nul 2>nul
pip install -r requirements.txt
cd ..
echo.

:: 4. Install Frontend dependencies
echo [2/3] Setting up React Frontend...
cd frontend
echo Installing node modules (this might take a minute)...
call npm install
cd ..
echo.

:: 5. Start Servers
echo [3/3] Launching servers...
echo.
echo =====================================================================
echo   SUCCESS! The application is starting up.
echo   - It will open in your browser shortly at: http://localhost:5173/
echo   - To stop the application, simply close this command window.
echo =====================================================================
echo.

:: Start backend in a separate minimized window
start "Bank Statement Converter Backend" /min cmd /c "cd backend && .venv\Scripts\activate && python main.py"

:: Start frontend in this window
cd frontend
npm run dev
