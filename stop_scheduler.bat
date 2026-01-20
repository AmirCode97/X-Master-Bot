@echo off
chcp 65001 >nul
echo ==================================================
echo    Stopping X Master Bot Auto-Run
echo ==================================================
echo.

set "TASK_NAME=XMasterBot"

schtasks /delete /tn "%TASK_NAME%" /f

if %errorlevel% equ 0 (
    echo.
    echo [SUCCESS] Scheduled task removed!
    echo The bot will no longer run automatically.
) else (
    echo.
    echo [INFO] Task was not found or already removed.
)

echo.
pause
