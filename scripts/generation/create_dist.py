import os
import shutil
import zipfile

def create_dist():
    print("--- Creating Release Package ---")
    
    dist_dir = "dist"
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)
    
    # Files to copy
    files = [
        "README.md",
        "USER_GUIDE.md",
        "install_client.py",
        "run_with_gpu.bat",
        "docker-compose.yml"
    ]
    
    # Artifacts (Docs)
    brain_dir = r"C:\Users\91991\.gemini\antigravity\brain\3604eba8-30b5-4cf5-b9fa-d05fa76a61dc"
    artifacts = ["RELEASE_NOTES.md", "FUTURE_AI_ROADMAP.md"]
    for art in artifacts:
        src = os.path.join(brain_dir, art)
        if os.path.exists(src):
            shutil.copy2(src, dist_dir)
            print(f"Copied artifact {art}")
    
    for f in files:
        if os.path.exists(f):
            shutil.copy2(f, dist_dir)
            print(f"Copied {f}")
        else:
            print(f"Warning: {f} not found")
            
    # Copy Maya Plugin folder
    if os.path.exists("maya"):
        shutil.copytree("maya", os.path.join(dist_dir, "maya"))
        
    # Copy Backend folder (Ignore cache/venv)
    if os.path.exists("backend"):
        shutil.copytree("backend", os.path.join(dist_dir, "backend"), ignore=shutil.ignore_patterns('__pycache__', 'venv', '*.pyc'))
        
    # Create Zip
    print("Zipping package...")
    zip_name = "Qyntara_AI_v1.0_Release"
    shutil.make_archive(zip_name, 'zip', dist_dir)
    shutil.move(f"{zip_name}.zip", dist_dir)
    
    print(f"\nPackage created in: {os.path.abspath(dist_dir)}")

if __name__ == "__main__":
    create_dist()
