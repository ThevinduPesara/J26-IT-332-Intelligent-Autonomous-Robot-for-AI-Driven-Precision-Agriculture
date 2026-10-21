@echo off
setlocal
cd /d "%~dp0PaddyVision_Studio_Complete\PaddyVision_Studio"
echo Starting PaddyVision Seed Dispensing Model on Port 8003...

set "PYTHON_CMD="
if exist ".venv\Scripts\python.exe" (
    set "PYTHON_CMD=%CD%\.venv\Scripts\python.exe"
) else (
    where python >nul 2>nul
    if not errorlevel 1 set "PYTHON_CMD=python"
)

if not defined PYTHON_CMD (
    echo [ERROR] Python was not found. Install Python 3.10-3.12 and create the virtual environment.
    goto :setup
)

"%PYTHON_CMD%" -c "import sys; raise SystemExit(0 if (3, 10) <= sys.version_info[:2] <= (3, 12) else 1)" >nul 2>nul
if errorlevel 1 (
    echo [ERROR] PaddyVision requires Python 3.10-3.12; selected interpreter is unsupported.
    goto :setup
)

"%PYTHON_CMD%" -c "import fastapi, uvicorn, multipart, numpy, PIL, torch, transformers, segmentation_models_pytorch" >nul 2>nul
if errorlevel 1 (
    echo [ERROR] PaddyVision dependencies are missing from this Python environment.
    goto :setup
)

"%PYTHON_CMD%" -m uvicorn backend.main:app --host 0.0.0.0 --port 8003 --reload
goto :end

:setup
echo.
echo From this folder, run:
echo   py -3.12 -m venv .venv
echo   .venv\Scripts\python.exe -m pip install --upgrade pip
echo   .venv\Scripts\python.exe -m pip install -r requirements.txt
echo.
pause

:end
endlocal
