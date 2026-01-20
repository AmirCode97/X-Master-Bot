@echo off
chcp 65001 >nul
echo ==================================================
echo    X Master Bot - Local Runner
echo ==================================================
echo.

cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist ".env" (
    echo [ERROR] .env file not found!
    echo Please create .env file with your settings.
    pause
    exit /b 1
)

REM Load environment variables from .env
echo [INFO] Loading environment variables...
for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
    if not "%%a"=="" if not "%%a:~0,1%"=="#" (
        set "%%a=%%b"
    )
)

REM Install requirements if needed
echo [INFO] Checking dependencies...
pip show playwright >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing playwright...
    pip install playwright python-dotenv
    playwright install chromium
)

echo.
echo [INFO] Starting X Master Bot...
echo [INFO] Press Ctrl+C to stop
echo ==================================================
echo.

python main.py

echo.
echo ==================================================
echo [DONE] Bot finished!
echo ==================================================
pause
