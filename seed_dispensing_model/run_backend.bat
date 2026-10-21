@echo off
cd /d "%~dp0PaddyVision_Studio_Complete\PaddyVision_Studio"
echo Starting PaddyVision Seed Dispensing Model on Port 8003...
if exist "C:\Users\LENOVO\anaconda3\envs\torch_gpu\python.exe" (
    "C:\Users\LENOVO\anaconda3\envs\torch_gpu\python.exe" -m uvicorn backend.main:app --host 0.0.0.0 --port 8003 --reload
) else (
    python -m uvicorn backend.main:app --host 0.0.0.0 --port 8003 --reload
)
pause
