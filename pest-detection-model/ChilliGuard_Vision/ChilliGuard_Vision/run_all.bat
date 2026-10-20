@echo off
start "ChilliGuard Backend" cmd /k call "%~dp0run_backend.bat"
timeout /t 4 /nobreak >nul
start "ChilliGuard Frontend" cmd /k call "%~dp0run_frontend.bat"
