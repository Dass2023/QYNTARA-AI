import shutil
import os
import zipfile

def deploy():
    root = os.getcwd()
    src = os.path.join(root, "qyntara_ai")
    dst = os.path.join(root, "QyntaraAI_Release.zip")
    
    print(f"Zipping {src} to {dst}")
    
    with zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED) as zf:
        for folder, subs, files in os.walk(src):
            if "tests" in folder or "__pycache__" in folder: continue
            for file in files:
                if file.endswith(".pyc"): continue
                abs_path = os.path.join(folder, file)
                rel_path = os.path.relpath(abs_path, root) # qyntara_ai/...
                zf.write(abs_path, rel_path)
                
    if os.path.exists(dst):
        print("SUCCESS: Zip created.")
    else:
        print("ERROR: Zip failed.")

if __name__ == "__main__":
    deploy()
