@echo off
cd /d "%~dp0backend"
"C:\Users\LENOVO\anaconda3\envs\torch_gpu\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8000
pause
