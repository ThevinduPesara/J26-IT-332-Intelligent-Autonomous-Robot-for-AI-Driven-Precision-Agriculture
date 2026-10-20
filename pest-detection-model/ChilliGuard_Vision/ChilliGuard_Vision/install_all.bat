@echo off
set PYTHON=C:\Users\LENOVO\anaconda3\envs\torch_gpu\python.exe

"%PYTHON%" -m pip install -r "%~dp0backend\requirements.txt"
"%PYTHON%" -m pip install -r "%~dp0frontend\requirements.txt"

echo.
echo Installation complete.
pause
