import shutil
import os
import zipfile

def package_plugin():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # E:/QYNTARA AI/qyntara_ai
    root_dir = os.path.dirname(base_dir) # E:/QYNTARA AI
    
    output_filename = os.path.join(root_dir, "QyntaraAI_Release.zip")
    
    print(f"Packaging Qyntara AI from {base_dir}...")
    
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(base_dir):
            # Exclude tests, pycache, git
            if "tests" in root or "__pycache__" in root or ".git" in root:
                continue
                
            for file in files:
                if file.endswith(".pyc") or file.endswith(".pyo"):
                    continue
                    
                file_path = os.path.join(root, file)
                # Archive name should be relative to parent of qyntara_ai (e.g. qyntara_ai/init.py)
                arcname = os.path.relpath(file_path, root_dir)
                zipf.write(file_path, arcname)
                
    print(f"Package created: {output_filename}")

import sys

if __name__ == "__main__":
    try:
        package_plugin()
    except Exception as e:
        print(f"Error: {e}")
    sys.stdout.flush()
