@echo off
setlocal enabledelayedexpansion

title AgriBot AI Engine - Master Launcher
color 0A

echo ===============================================================================
echo     AGRIBOT PRECISION AGRICULTURE - 4-MODEL AI MASTER LAUNCHER
echo ===============================================================================
echo.

:: 1. Detect Python Executable
set PYTHON_CMD=python
if exist "C:\Users\LENOVO\anaconda3\envs\torch_gpu\python.exe" (
    set "PYTHON_CMD=C:\Users\LENOVO\anaconda3\envs\torch_gpu\python.exe"
    echo [OK] Using Anaconda torch_gpu environment: !PYTHON_CMD!
) else if exist "%~dp0.venv\Scripts\python.exe" (
    set "PYTHON_CMD=%~dp0.venv\Scripts\python.exe"
    echo [OK] Using local virtualenv: !PYTHON_CMD!
) else (
    echo [INFO] Using system PATH Python: !PYTHON_CMD!
)

echo.
echo Starting all 4 FastAPI Model Backends simultaneously...
echo -------------------------------------------------------------------------------

:: Model 1: Chilli Plant Detection (Port 8000)
echo [1/4] Starting Model 1: Chilli Plant Detection on Port 8000...
start "Model 1: Chilli Plant Detection [Port 8000]" cmd /k "title Model 1: Chilli Plant Detection [Port 8000] && color 0B && cd /d "%~dp0Chilli_Plant_Detection_Model\Chilli_Plant_Detection_System\backend" && "!PYTHON_CMD!" -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

:: Wait 1.5 seconds before launching next
timeout /t 2 /nobreak >nul

:: Model 2: NPK Mix Model (Port 8001)
echo [2/4] Starting Model 2: NPK Mix Model (NutrientOS) on Port 8001...
start "Model 2: NPK Mix Model [Port 8001]" cmd /k "title Model 2: NPK Mix Model [Port 8001] && color 0E && cd /d "%~dp0NPK_Mix_Model" && "!PYTHON_CMD!" -m uvicorn backend.main:app --host 0.0.0.0 --port 8001"

timeout /t 2 /nobreak >nul

:: Model 3: Pest Detection Model (Port 8002)
echo [3/4] Starting Model 3: Pest Detection (ChilliGuard Vision) on Port 8002...
start "Model 3: Pest Detection [Port 8002]" cmd /k "title Model 3: Pest Detection [Port 8002] && color 0C && cd /d "%~dp0pest-detection-model\ChilliGuard_Vision\ChilliGuard_Vision\backend" && "!PYTHON_CMD!" -m uvicorn app.main:app --host 0.0.0.0 --port 8002"

timeout /t 2 /nobreak >nul

:: Model 4: Seed Dispensing Model (Port 8003)
echo [4/4] Starting Model 4: Seed Dispensing (PaddyVision) on Port 8003...
start "Model 4: Seed Dispensing [Port 8003]" cmd /k "title Model 4: Seed Dispensing [Port 8003] && color 0D && cd /d "%~dp0seed_dispensing_model" && call run_backend.bat"

echo.
echo ===============================================================================
echo     ALL 4 AI MODELS STARTED SUCCESSFULLY!
echo ===============================================================================
echo.
echo  * Model 1 (Chilli Detection):  http://127.0.0.1:8000  (Docs: /docs)
echo  * Model 2 (NPK Mix Nutrient):  http://127.0.0.1:8001  (Docs: /docs)
echo  * Model 3 (Pest Detection):    http://127.0.0.1:8002  (Docs: /docs)
echo  * Model 4 (Seed Dispensing):   http://127.0.0.1:8003  (Docs: /docs)
echo.
echo  * Next.js Frontend Dashboard: http://localhost:3000/analysis
echo.
echo Tip: Keep this window or the 4 model terminal windows open.
echo To shut down all 4 servers cleanly at any time, run: stop_all_models.bat
echo ===============================================================================
echo.
pause
