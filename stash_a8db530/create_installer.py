import os
import shutil
import sys
from datetime import datetime

VERSION = "v9.1_PRO"
ROOT_DIR = r"i:\QYNTARA AI"
DIST_DIR = os.path.join(ROOT_DIR, "dist", f"qyntara_nexus_installer_{VERSION}")

def copy_tree(src, dst):
    if not os.path.exists(src):
        print(f"[WARN] Source not found: {src}")
        return
    try:
        shutil.copytree(src, dst, dirs_exist_ok=True, ignore=shutil.ignore_patterns('__pycache__', '.git', 'node_modules', '*.pyc'))
        print(f"[OK] Copied {os.path.basename(src)}")
    except Exception as e:
        print(f"[ERR] Failed to copy {src}: {e}")

def create_installer():
    print(f"--- CREATING INSTALLER {VERSION} ---")
    
    # 1. Clean / Create Dist
    if os.path.exists(DIST_DIR):
        try:
            shutil.rmtree(DIST_DIR)
        except:
            print("[WARN] Could not fully clean dist dir (files might be in use).")
    
    os.makedirs(DIST_DIR, exist_ok=True)
    os.makedirs(os.path.join(DIST_DIR, "bin"), exist_ok=True)
    os.makedirs(os.path.join(DIST_DIR, "scripts"), exist_ok=True)
    os.makedirs(os.path.join(DIST_DIR, "docs"), exist_ok=True)
    os.makedirs(os.path.join(DIST_DIR, "adapters"), exist_ok=True)

    # 2. Copy Maya Core
    copy_tree(os.path.join(ROOT_DIR, "qyntara_ai"), os.path.join(DIST_DIR, "scripts", "qyntara_ai"))
    copy_tree(os.path.join(ROOT_DIR, "scripts", "maya"), os.path.join(DIST_DIR, "scripts", "maya"))

    # 3. Copy Backend
    copy_tree(os.path.join(ROOT_DIR, "backend"), os.path.join(DIST_DIR, "bin", "backend"))
    
    # 4. Copy Web Frontend (Build or Source for now)
    # Ideally checking for .next build, but copying source for dev-mode dist
    copy_tree(os.path.join(ROOT_DIR, "frontend"), os.path.join(DIST_DIR, "bin", "frontend"))

    # 5. Copy Multi-DCC Adapters
    adapters = {
        "unity": os.path.join(ROOT_DIR, "unity_sdk"),
        "unreal": os.path.join(ROOT_DIR, "unreal_plugin"),
        "threejs": os.path.join(ROOT_DIR, "threejs_sdk"),
        "blender": os.path.join(ROOT_DIR, "qyntara_dcc", "blender"),
        "max": os.path.join(ROOT_DIR, "qyntara_dcc", "max"),
        "maya_plugin": os.path.join(ROOT_DIR, "maya") 
    }
    
    for name, path in adapters.items():
        copy_tree(path, os.path.join(DIST_DIR, "adapters", name))

    # 6. Create Setup Script (Bat)
    setup_bat = f"""@echo off
title Qyntara Nexus Installer {VERSION}
color 0b
echo ==================================================
echo      QYNTARA NEXUS - INSTALLER {VERSION}
echo ==================================================
echo.
echo [1] Installing Maya Module...
echo     Target: %USERPROFILE%\\Documents\\maya\\scripts
xcopy /E /I /Y "%~dp0scripts\\qyntara_ai" "%USERPROFILE%\\Documents\\maya\\scripts\\qyntara_ai"
xcopy /E /I /Y "%~dp0scripts\\maya" "%USERPROFILE%\\Documents\\maya\\scripts"
echo.
echo [2] Installing Backend...
echo     (Skipped: Running from Portable Bin)
echo.
echo [3] Installing Adapters (Unity/Unreal/Blender)...
echo     Check the "adapters" folder for plugins.
echo.
echo [SUCCESS] Installation Complete.
echo.
echo To Launch in Maya:
echo   import launch_in_maya
echo   launch_in_maya.launch()
echo.
pause
"""
    with open(os.path.join(DIST_DIR, "setup.bat"), "w") as f:
        f.write(setup_bat)

    # 7. Create README
    readme = f"""
# Qyntara Nexus - Distribution {VERSION}

## Contents
1. **Core**: Fully validated backend (12 Industries).
2. **Web**: Next.js Dashboard v9.1.
3. **Maya**: Advanced UI with Future Roadmap.
4. **Adapters**:
    - Unity SDK
    - Unreal Plugin
    - Three.js SDK
    - Blender Add-on
    - 3ds Max Script

## Installation
Run `setup.bat` to install Maya scripts.
For other DCCs, verify the `adapters/` folder.
    """
    with open(os.path.join(DIST_DIR, "docs", "README.txt"), "w") as f:
        f.write(readme)

    print(f"\n[DONE] Installer created at:\n{DIST_DIR}")

if __name__ == "__main__":
    create_installer()
