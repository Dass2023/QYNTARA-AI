@echo off
echo [QYNTARA NEXUS] INSTALLER INITIALIZED...
echo.

echo 1. Installing Backend Dependencies...
cd backend
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Backend installation failed!
    pause
    exit /b %ERRORLEVEL%
)
cd ..

echo.
echo 2. Installing Frontend Dependencies...
cd frontend
call npm install --legacy-peer-deps
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Frontend installation failed!
    pause
    exit /b %ERRORLEVEL%
)
cd ..

echo.
echo [SUCCESS] Qyntara Nexus v9.1 Installed Successfully!
echo Run 'frontend\start_safe.bat' to launch the system.
pause
