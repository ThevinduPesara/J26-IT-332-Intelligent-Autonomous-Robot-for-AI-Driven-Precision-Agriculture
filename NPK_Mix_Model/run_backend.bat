@echo off
cd /d "%~dp0"
echo Starting NutrientOS NPK Mix Model on Port 8001...
if exist "C:\Users\LENOVO\anaconda3\envs\torch_gpu\python.exe" (
    "C:\Users\LENOVO\anaconda3\envs\torch_gpu\python.exe" -m uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload
) else (
    python -m uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload
)
pause
