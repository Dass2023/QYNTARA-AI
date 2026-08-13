@echo off
cd /d "%~dp0"
echo ==========================================
echo QYNTARA AI - GPU Launcher (Python 3.13) - v2
echo ==========================================
echo Current Directory: %CD%

REM Check for Python 3.13
py -3.13 --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python 3.13 is not installed or not found via 'py' launcher.
    echo Please install Python 3.13 to use GPU acceleration.
    pause
    exit /b
)

echo [INFO] Found Python 3.13.

REM Create venv if not exists
if not exist "venv_gpu" (
    echo [INFO] Creating virtual environment 'venv_gpu'...
    py -3.13 -m venv venv_gpu
)

REM Activate
call "%~dp0venv_gpu\Scripts\activate"

REM Check if torch is installed
python -c "import torch" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Installing PyTorch with CUDA support...
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
    
    echo [INFO] Installing backend dependencies...
    if exist "%~dp0backend\requirements.txt" (
        pip install -r "%~dp0backend\requirements.txt"
    ) else (
        echo [ERROR] "%~dp0backend\requirements.txt" not found!
        pause
        exit /b
    )
)

echo [INFO] Starting Backend on GPU...
REM Uninstall xformers if present to avoid compatibility issues
pip uninstall -y xformers >nul 2>&1

cd /d "%~dp0"
python -m backend.main
pause
