@echo off
cd /d "%~dp0"

echo ============================================================
echo Starting Chilli Plant Detection with Docker Compose...
echo ============================================================

docker compose up --build -d

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Docker failed to start.
    echo Please make sure Docker Desktop is running.
    echo.
    pause
    exit /b %errorlevel%
)

echo.
echo ============================================================
echo Containers started successfully!
echo Waiting for services to initialize...
echo ============================================================
timeout /t 5 /nobreak > nul

echo.
echo Backend API : http://localhost:8000
echo.
echo Opening Swagger documentation...
start "" http://localhost:8000/docs

echo.
echo To view live logs: docker compose logs -f
echo To stop services : run docker-stop.bat
echo ============================================================
pause
