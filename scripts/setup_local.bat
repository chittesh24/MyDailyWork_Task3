@echo off
REM Windows batch script for local setup (no Docker)

echo ================================================
echo    IMAGE CAPTIONING - LOCAL SETUP (NO DOCKER)
echo ================================================
echo.

echo [1/5] Installing Python dependencies...
cd backend
python -m pip install --upgrade pip
pip install -r requirements.txt
cd ..

echo.
echo [2/5] Creating SQLite database...
python backend/database/init_sqlite.py

echo.
echo [3/5] Creating demo model and vocabulary...
python scripts/create_demo_model.py

echo.
echo [4/5] Copying local environment file...
copy backend\.env.local backend\.env

echo.
echo ================================================
echo    ✅ SETUP COMPLETE!
echo ================================================
echo.
echo Next steps:
echo   1. Open TWO command prompts
echo   2. In first: python scripts/run_local_backend.py
echo   3. In second: python scripts/run_local_frontend.py
echo   4. Browser will open automatically!
echo.
pause
