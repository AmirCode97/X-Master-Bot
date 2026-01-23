@echo off
cd /d "%~dp0"
echo ==================================================
echo    X Master Bot - Auto Run (Visible)
echo ==================================================
echo.

REM Load environment variables
if exist .env (
    for /f "tokens=*" %%i in (.env) do set %%i
)

echo Starting Bot...
python main.py

echo.
echo Closing in 10 seconds...
timeout /t 10
exit
