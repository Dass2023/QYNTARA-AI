@echo off
title Qyntara Backend Server
echo Starting Qyntara Backend Server on port 8000...
echo.

:: Ensure we are in the correct directory
cd /d "I:\QYNTARA AI"

:: Run the backend using the test_env_full Python and uvicorn
"I:\QYNTARA AI\test_env_full\Scripts\python.exe" -m uvicorn backend.main:app --port 8000

pause
