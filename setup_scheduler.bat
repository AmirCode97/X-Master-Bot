@echo off
chcp 65001 >nul
echo ==================================================
echo    Setting up X Master Bot - Auto Run Every 30 Min
echo ==================================================
echo.

REM Get the current directory
set "BOT_PATH=%~dp0"
set "TASK_NAME=XMasterBot"
set "SCRIPT_PATH=%BOT_PATH%run_silent.vbs"

REM Create a VBS script to run Python silently
echo Set WshShell = CreateObject("WScript.Shell") > "%SCRIPT_PATH%"
echo WshShell.CurrentDirectory = "%BOT_PATH%" >> "%SCRIPT_PATH%"
echo WshShell.Run "python main.py", 0, True >> "%SCRIPT_PATH%"

echo [INFO] Bot Path: %BOT_PATH%
echo [INFO] Creating scheduled task...
echo.

REM Delete existing task if exists
schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1

REM Create new task - runs every 30 minutes using VBS script
schtasks /create /tn "%TASK_NAME%" /tr "wscript.exe \"%SCRIPT_PATH%\"" /sc minute /mo 30 /f

if %errorlevel% equ 0 (
    echo.
    echo ==================================================
    echo [SUCCESS] Task created successfully!
    echo.
    echo Task Name: %TASK_NAME%
    echo Schedule: Every 30 minutes
    echo.
    echo To view: Open Task Scheduler
    echo To stop: Run stop_scheduler.bat
    echo ==================================================
) else (
    echo.
    echo [ERROR] Failed to create task.
    echo [TIP] Try running this script as Administrator.
)

echo.
pause
