@echo off
setlocal
cd /d "%~dp0"
call conda activate npk_ui
if errorlevel 1 (
 echo npk_ui not detected. In Anaconda Prompt run: conda create -n npk_ui python=3.10 -y
 pause
 exit /b 1
)
python -m pip install -r requirements.txt
if errorlevel 1 (echo Installation failed.& pause & exit /b 1)
echo Dependencies installed. Double-click START_WINDOWS.bat.
pause
