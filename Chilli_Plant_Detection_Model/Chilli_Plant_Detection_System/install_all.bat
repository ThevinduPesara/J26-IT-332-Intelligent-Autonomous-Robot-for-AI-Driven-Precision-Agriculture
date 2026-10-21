@echo off
set PYTHON=python

echo ============================================================
echo Installing Chilli Plant Detection backend packages...
echo ============================================================
"%PYTHON%" -m pip install -r "%~dp0backend\requirements.txt"

echo.
echo Installation complete.
pause
