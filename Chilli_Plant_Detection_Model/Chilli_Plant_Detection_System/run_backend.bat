@echo off
set PYTHON=python

cd /d "%~dp0backend"

echo ============================================================
echo Starting Chilli Plant Detection FastAPI Backend
echo API:  http://127.0.0.1:8000
echo Docs: http://127.0.0.1:8000/docs
echo ============================================================

"%PYTHON%" -m uvicorn app.main:app --host 0.0.0.0 --port 8000

pause
