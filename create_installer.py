import os
import shutil
import datetime

# Configuration
SOURCE_ROOT = r"i:/QYNTARA AI"
DIST_ROOT = os.path.join(SOURCE_ROOT, "dist", "qyntara_installer_v10.0")
MAYA_SOURCE = os.path.join(SOURCE_ROOT, "maya", "qyntara_client.py")
BACKEND_SOURCE = os.path.join(SOURCE_ROOT, "backend")
FRONTEND_SOURCE = os.path.join(SOURCE_ROOT, "frontend")

def log(msg):
    print(f"[INSTALLER] {msg}")

def copy_file(src, dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    shutil.copy2(src, dest_folder)
    log(f"Copied {os.path.basename(src)} -> {dest_folder}")

def copy_dir(src, dest, ignore=None):
    if os.path.exists(dest):
        shutil.rmtree(dest)
    shutil.copytree(src, dest, ignore=ignore)
    log(f"Copied directory {src} -> {dest}")

def remove_readonly(func, path, exc_info):
    import stat
    os.chmod(path, stat.S_IWRITE)
    func(path)

def create_installer():
    log("Starting Qyntara AI v10.0 Installer Build...")

    # 1. Clean Dist
    if os.path.exists(DIST_ROOT):
        shutil.rmtree(DIST_ROOT, onerror=remove_readonly)
    os.makedirs(DIST_ROOT)

    # 2. Maya Client (The critical update)
    maya_dest = os.path.join(DIST_ROOT, "scripts", "maya")
    copy_file(MAYA_SOURCE, maya_dest)

    # 3. Backend (Python Core)
    backend_dest = os.path.join(DIST_ROOT, "bin", "backend")
    ignore_filter = shutil.ignore_patterns('__pycache__', '*.pyc', '.pytest_cache', '.venv', '.env*', '.git*', '*.log', '*.tmp', 'node_modules', '.next', '.DS_Store')
    copy_dir(BACKEND_SOURCE, backend_dest, ignore=ignore_filter)

    # 4. Frontend (Source - User would run 'npm install' or we assume pre-build)
    # For this installer, we'll copy the source configs and app folder
    frontend_dest = os.path.join(DIST_ROOT, "bin", "frontend_source")
    copy_dir(os.path.join(FRONTEND_SOURCE, "app"), os.path.join(frontend_dest, "app"), ignore=ignore_filter)
    copy_file(os.path.join(FRONTEND_SOURCE, "package.json"), frontend_dest)
    copy_file(os.path.join(FRONTEND_SOURCE, "next.config.mjs"), frontend_dest)
    
    # 5. Documentation
    docs_dest = os.path.join(DIST_ROOT, "docs")
    os.makedirs(docs_dest)
    with open(os.path.join(docs_dest, "RELEASE_NOTES_v10.0.txt"), "w") as f:
        f.write("QYNTARA AI v10.0 - STRATEGIC INDUSTRY EDITION\n")
        f.write("=============================================\n")
        f.write("- NEW: 12-Industry Strategic Roadmap (Web & Maya)\n")
        f.write("- UPDATED: Maya Client 'qyntara_client.py' with Strategic Command Center\n")
        f.write("- FIXED: Various UI bugs and performance improvements\n")
    
    # 6. Install Script (Mock)
    with open(os.path.join(DIST_ROOT, "install.bat"), "w") as f:
        f.write("@echo off\n")
        f.write("echo Installing Qyntara AI v10.0...\n")
        f.write("echo Copying Maya scripts...\n")
        f.write(r"copy scripts\maya\qyntara_client.py %USERPROFILE%\Documents\maya\scripts\ /Y")
        f.write("\n")
        f.write("echo Installation Complete!\n")
        f.write("pause\n")

    log(f"Build Complete at {DIST_ROOT}")

if __name__ == "__main__":
    create_installer()
