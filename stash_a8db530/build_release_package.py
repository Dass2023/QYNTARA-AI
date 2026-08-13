
"""
Qyntara AI - Release Builder (v5.0.0-rc1)
Generates distribution packages for deployment.

Outputs:
1. dist/qyntara_core-5.0.0-py3-none-any.whl (Python Package)
2. releases/Qyntara_Maya_Plugin_v5.0.0.zip (Maya Integration)
3. releases/Qyntara_Unreal_Plugin_v5.0.0.zip (Unreal Plugin)
"""
import os
import shutil
import zipfile
import subprocess
import time

def build_wheel():
    print("[BUILD] Building Python Wheel...")
    if os.path.exists("setup.py"):
        subprocess.check_call(["python", "setup.py", "sdist", "bdist_wheel"])
    else:
        print("[ERROR] setup.py not found.")

def zip_directory(source_dir, output_filename, archive_root_name=None):
    print(f"[ZIP] Packaging {source_dir} -> {output_filename}...")
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Calculate relative path
                rel_path = os.path.relpath(file_path, os.path.dirname(source_dir))
                # Rename root folder if needed
                if archive_root_name:
                    # Strip original root and prepend new name
                    # logic: source_dir/foo/bar -> archive_root_name/foo/bar
                    pass # complicated, just zip whatever's inside
                
                zipf.write(file_path, os.path.relpath(file_path, os.path.join(source_dir, "..")))

def build_maya_package():
    os.makedirs("releases", exist_ok=True)
    
    # Needs: qyntara_ai (package), scripts/maya (scripts), userSetup.py (if exists)
    pkg_name = "releases/Qyntara_Maya_v5.0.rc1.zip"
    
    print(f"[BUILD] Creating Maya Plugin Package: {pkg_name}")
    with zipfile.ZipFile(pkg_name, 'w', zipfile.ZIP_DEFLATED) as z:
        # Add Core Package
        for root, dirs, files in os.walk("qyntara_ai"):
            for file in files:
                if "__pycache__" in root: continue
                if file.endswith(".pyc"): continue
                z.write(os.path.join(root, file))
                
        # Add Scripts
        for root, dirs, files in os.walk("scripts"):
            for file in files:
                if "__pycache__" in root: continue
                z.write(os.path.join(root, file))
                
        # Add Install Guide
        if os.path.exists("QUICKSTART.md"):
            z.write("QUICKSTART.md")

def build_unreal_package():
    os.makedirs("releases", exist_ok=True)
    pkg_name = "releases/Qyntara_Unreal_Plugin_v5.0.rc1.zip"
    
    print(f"[BUILD] Creating Unreal Plugin Package: {pkg_name}")
    with zipfile.ZipFile(pkg_name, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk("unreal_plugin"):
            for file in files:
                if "__pycache__" in root: continue
                # Write to zip, but strip "unreal_plugin" root -> create "QyntaraRuntime" root inside zip
                # Standard Unreal plugin structure: Plugins/QyntaraRuntime/...
                rel_path = os.path.relpath(os.path.join(root, file), "unreal_plugin")
                z.write(os.path.join(root, file), os.path.join("QyntaraRuntime", rel_path))

def build_unity_package():
    os.makedirs("releases", exist_ok=True)
    pkg_name = "releases/Qyntara_Unity_Package_v5.0.rc1.zip"
    
    print(f"[BUILD] Creating Unity SDK Package: {pkg_name}")
    with zipfile.ZipFile(pkg_name, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk("unity_sdk"):
            for file in files:
                if "__pycache__" in root: continue
                # Write to zip
                rel_path = os.path.relpath(os.path.join(root, file), "unity_sdk")
                z.write(os.path.join(root, file), os.path.join("com.qyntara.runtime", rel_path))

                rel_path = os.path.relpath(os.path.join(root, file), "unity_sdk")
                z.write(os.path.join(root, file), os.path.join("com.qyntara.runtime", rel_path))

def build_blender_addon():
    os.makedirs("releases", exist_ok=True)
    pkg_name = "releases/Qyntara_Blender_Addon_v5.0.rc1.zip"
    
    print(f"[BUILD] Creating Blender Addon: {pkg_name}")
    # Source: qyntara_dcc/blender
    source = os.path.join("qyntara_dcc", "blender")
    if os.path.exists(source):
        with zipfile.ZipFile(pkg_name, 'w', zipfile.ZIP_DEFLATED) as z:
            for root, dirs, files in os.walk(source):
                for file in files:
                    if "__pycache__" in root: continue
                    rel_path = os.path.relpath(os.path.join(root, file), source)
                    z.write(os.path.join(root, file), os.path.join("qyntara_blender", rel_path))
    else:
        print("[WARN] Blender source not found.")

def build_max_addon():
    os.makedirs("releases", exist_ok=True)
    pkg_name = "releases/Qyntara_Max_Script_v5.0.rc1.zip"
    
    print(f"[BUILD] Creating 3ds Max Script: {pkg_name}")
    # Source: qyntara_dcc/max
    source = os.path.join("qyntara_dcc", "max")
    if os.path.exists(source):
        with zipfile.ZipFile(pkg_name, 'w', zipfile.ZIP_DEFLATED) as z:
            for root, dirs, files in os.walk(source):
                for file in files:
                    if "__pycache__" in root: continue
                    rel_path = os.path.relpath(os.path.join(root, file), source)
                    z.write(os.path.join(root, file), os.path.join("qyntara_max", rel_path))
    else:
        print("[WARN] Max source not found.")

def build_threejs_sdk():
    os.makedirs("releases", exist_ok=True)
    pkg_name = "releases/Qyntara_ThreeJS_SDK_v5.0.rc1.zip"
    
    print(f"[BUILD] Creating Three.js SDK: {pkg_name}")
    # Source: threejs_sdk
    source = "threejs_sdk"
    if os.path.exists(source):
        with zipfile.ZipFile(pkg_name, 'w', zipfile.ZIP_DEFLATED) as z:
            for root, dirs, files in os.walk(source):
                for file in files:
                    if "node_modules" in root: continue
                    if "dist" in root: continue # maybe include dist?
                    rel_path = os.path.relpath(os.path.join(root, file), source)
                    z.write(os.path.join(root, file), os.path.join("qyntara-threejs", rel_path))

def build_master_suite():
    os.makedirs("releases", exist_ok=True)
    pkg_name = "releases/Qyntara_AI_Suite_v5.0_COMPLETE.zip"
    
    print(f"[BUILD] Creating MASTER SUITE: {pkg_name}")
    with zipfile.ZipFile(pkg_name, 'w', zipfile.ZIP_DEFLATED) as z:
        # Add all other zips in releases/
        for root, dirs, files in os.walk("releases"):
            for file in files:
                if file.endswith(".zip") and "COMPLETE" not in file:
                    z.write(os.path.join(root, file), file)
        
        # Add Python Whl from dist/
        if os.path.exists("dist"):
            for file in os.listdir("dist"):
                if file.endswith(".whl"):
                    z.write(os.path.join("dist", file), os.path.join("python_libs", file))
                    
        # Add Docs
        if os.path.exists("USER_MANUAL.md"): z.write("USER_MANUAL.md")
        if os.path.exists("CONNECTIVITY_GUIDE.md"): z.write("CONNECTIVITY_GUIDE.md")

def main():
    start = time.time()
    print("=== Qyntara AI Release Builder ===")
    
    # FORCE ROOT DIRECTORY (Fix for Maya Execution Context)
    project_root = r"i:\QYNTARA AI"
    if os.path.exists(project_root):
        os.chdir(project_root)
        print(f"[SETUP] Changed working directory to: {project_root}")
    else:
        print(f"[ERROR] Project root not found: {project_root}")
        return

    # 1. Verification
    if not os.path.exists("qyntara_ai"):
        print("[ERROR] Run from project root.")
        return

    # 2. Build Python Package
    try:
        build_wheel()
    except Exception as e:
        print(f"[WARN] Wheel build failed (requires setuptools/wheel): {e}")

    # 3. Build Maya Package
    build_maya_package()
    
    # 4. Build Unreal Package
    build_unreal_package()
    
    # 5. Build Unity Package
    build_unity_package()
    
    # 6. Build Blender/Max/ThreeJS
    build_blender_addon()
    build_max_addon()
    build_threejs_sdk()
    
    # 7. Build Master Suite (All-In-One)
    build_master_suite()
    
    print(f"=== Build Complete in {time.time()-start:.2f}s ===")
    print(f"Find releases in: {os.path.abspath('releases')}")
    print(f"Find wheels in:   {os.path.abspath('dist')}")

if __name__ == "__main__":
    main()
