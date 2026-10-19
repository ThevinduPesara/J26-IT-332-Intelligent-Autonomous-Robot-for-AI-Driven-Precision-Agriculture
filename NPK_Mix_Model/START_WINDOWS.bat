@echo off
cd /d "%~dp0"
start "NutrientOS API" "%~dp0RUN_API.bat"
timeout /t 2 >nul
start "NutrientOS Dashboard" "%~dp0RUN_DASHBOARD.bat"
echo.
echo Dashboard: http://127.0.0.1:8501
echo API docs : http://127.0.0.1:8071/docs
echo.
pause
