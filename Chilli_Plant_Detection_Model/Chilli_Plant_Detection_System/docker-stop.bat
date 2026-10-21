@echo off
cd /d "%~dp0"

echo ============================================================
echo Stopping Chilli Plant Detection Docker Containers...
echo ============================================================

docker compose down

echo.
echo Containers stopped successfully.
pause
