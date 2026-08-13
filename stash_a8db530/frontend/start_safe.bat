
@echo off
echo [DEBUG] Initial Directory: %CD%
pushd "I:\QYNTARA AI\frontend"
echo [DEBUG] Target Directory: %CD%
echo [QYNTARA AI] INITIALIZING SAFE MODE...
echo [INFO] Killing any lingering processes on port 3000...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":3000" ^| find "LISTENING"') do taskkill /f /pid %%a >nul 2>&1
echo [INFO] Killing any lingering processes on port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do taskkill /f /pid %%a >nul 2>&1

echo [INFO] Cleaning compilation cache...
if exist ".next" rmdir /s /q ".next"

echo [INFO] Building for Production (Stable)...
call npm run build
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Build failed! Check console for errors.
    pause
    exit /b %ERRORLEVEL%
)

echo [INFO] Starting Backend Server...
start "Qyntara Backend" cmd /k python ..\start_server.py
timeout /t 5

echo [SUCCESS] Build Complete. Launching Frontend Server...
echo [INFO] Application will be available at http://localhost:3000
echo [INFO] Use CTRL+C to stop.
call npm start
