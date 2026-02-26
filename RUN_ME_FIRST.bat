@echo off
REM ONE-CLICK SETUP AND RUN (Windows)

echo ╔════════════════════════════════════════════════════════╗
echo ║   IMAGE CAPTIONING SYSTEM - ONE CLICK DEPLOY          ║
echo ║   No Docker Required!                                 ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.11+ first
    echo    Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Run setup
echo Running setup script...
call scripts\setup_local.bat

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║   STARTING APPLICATION...                             ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Start backend in new window
start "Backend Server" cmd /k "python scripts\run_local_backend.py"

REM Wait 5 seconds for backend to start
timeout /t 5 /nobreak >nul

REM Start frontend in new window
start "Frontend Server" cmd /k "python scripts\run_local_frontend.py"

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║   ✅ APPLICATION STARTED!                              ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo Two windows opened:
echo   1. Backend Server (Port 8000)
echo   2. Frontend Server (Port 3000)
echo.
echo Browser will open automatically at http://localhost:3000
echo.
echo Press any key to close this window...
pause >nul
