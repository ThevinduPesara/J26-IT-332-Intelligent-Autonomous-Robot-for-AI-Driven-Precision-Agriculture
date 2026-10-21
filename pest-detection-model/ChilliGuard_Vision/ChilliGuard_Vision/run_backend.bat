@echo off
cd /d "%~dp0backend"
if exist "C:\Users\LENOVO\anaconda3\envs\torch_gpu\python.exe" (
    "C:\Users\LENOVO\anaconda3\envs\torch_gpu\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
) else (
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
)
pause
