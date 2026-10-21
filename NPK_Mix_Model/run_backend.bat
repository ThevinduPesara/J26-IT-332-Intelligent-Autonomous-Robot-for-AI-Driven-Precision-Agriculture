@echo off
setlocal
cd /d "%~dp0"
echo Starting NutrientOS NPK Mix Model on Port 8501...

set "PYTHON_CMD="
if exist ".venv\Scripts\python.exe" (
    set "PYTHON_CMD=%CD%\.venv\Scripts\python.exe"
) else (
    where python >nul 2>nul
    if not errorlevel 1 set "PYTHON_CMD=python"
)

if not defined PYTHON_CMD (
    echo [ERROR] Python was not found. Install Python and create this model's virtual environment.
    goto :setup
)

"%PYTHON_CMD%" -c "import fastapi, pydantic, uvicorn" >nul 2>nul
if errorlevel 1 (
    echo [ERROR] NPK API dependencies are missing from this Python environment.
    goto :setup
)

"%PYTHON_CMD%" -m uvicorn backend.main:app --host 0.0.0.0 --port 8501 --reload
goto :end

:setup
echo.
echo From this folder, run:
echo   python -m venv .venv
echo   .venv\Scripts\python.exe -m pip install --upgrade pip
echo   .venv\Scripts\python.exe -m pip install -r requirements.txt
echo.
pause

:end
endlocal
