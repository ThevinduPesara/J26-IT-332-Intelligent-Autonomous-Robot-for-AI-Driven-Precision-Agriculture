@echo off
cd /d "%~dp0"
call conda activate npk_ui
if errorlevel 1 (
  echo ERROR: conda npk_ui environment unavailable. Start through Anaconda Prompt.
  pause
  exit /b 1
)
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8071
pause
