@echo off
title AgriBot AI Engine - Master Terminator
color 0C

echo ===============================================================================
echo     STOPPING ALL 4 AGRIBOT AI MODEL SERVERS (Ports 8000, 8001, 8002, 8003)
echo ===============================================================================
echo.

:: 1. Terminate processes listening on AI Model ports
echo Stopping listening ports...
powershell -Command ^
  "$ports = @(8000, 8001, 8002, 8003); " ^
  "foreach ($p in $ports) { " ^
  "    $conns = Get-NetTCPConnection -LocalPort $p -ErrorAction SilentlyContinue; " ^
  "    if ($conns) { " ^
  "        foreach ($c in $conns) { " ^
  "            $procId = $c.OwningProcess; " ^
  "            if ($procId -and $procId -ne 0) { " ^
  "                Write-Host \"[STOPPING] Killing Process ID $procId on Port $p...\"; " ^
  "                Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue; " ^
  "            } " ^
  "        } " ^
  "    } else { " ^
  "        Write-Host \"[CLEAN] Port $p is already free.\"; " ^
  "    } " ^
  "}"

:: 2. Close titled Command Prompt windows
taskkill /F /FI "WINDOWTITLE eq Model 1: Chilli Plant Detection*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq Model 2: NPK Mix Model*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq Model 3: Pest Detection*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq Model 4: Seed Dispensing*" >nul 2>&1

echo.
echo ===============================================================================
echo     ALL 4 AI MODEL SERVERS HAVE BEEN SAFELY SHUT DOWN!
echo ===============================================================================
echo.
pause
