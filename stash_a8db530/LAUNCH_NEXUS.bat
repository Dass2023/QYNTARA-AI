@echo off
title Qyntara Nexus - Unified Launcher
color 0b

echo ==================================================
echo      QYNTARA NEXUS - SYSTEM STARTUP
echo ==================================================
echo.

echo [1/3] Starting Backend Server...
start "Qyntara Backend" cmd /c "python \"i:/QYNTARA AI/start_server.py\""
timeout /t 5

echo [2/3] Starting Web Dashboard...
start "Qyntara Frontend" cmd /c "cd /d \"i:/QYNTARA AI/frontend\" && npm run dev"
timeout /t 10

echo [3/3] Opening Browser...
start http://localhost:3000

echo.
echo ==================================================
echo      SYSTEMS OPERATIONAL - ENJOY THE NEXUS
echo ==================================================
timeout /t 5
