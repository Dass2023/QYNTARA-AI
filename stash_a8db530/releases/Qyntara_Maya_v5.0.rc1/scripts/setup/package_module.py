
import os
import shutil
import glob

def package_plugin():
    # Paths
    source_root = r"e:\QYNTARA AI"
    dist_root = os.path.join(source_root, "Qyntara_Distribution")
    
    module_name = "QyntaraAI"
    module_dir = os.path.join(dist_root, "modules", module_name)
    scripts_dir = os.path.join(module_dir, "scripts")
    
    # 1. Clean Distribution Directory
    if os.path.exists(dist_root):
        print(f"Cleaning {dist_root} ...")
        shutil.rmtree(dist_root)
    os.makedirs(scripts_dir)
    
    # 2. Copy Source Code (qyntara_ai)
    # We copy the entire package into scripts/qyntara_ai
    pkg_source = os.path.join(source_root, "qyntara_ai")
    pkg_dest = os.path.join(scripts_dir, "qyntara_ai")
    
    print(f"Copying {pkg_source} -> {pkg_dest}")
    
    # helper to ignore patterns
    ignore_func = shutil.ignore_patterns("__pycache__", "*.pyc", "*.log", ".git*", "dataset", "dataset_massive")
    shutil.copytree(pkg_source, pkg_dest, ignore=ignore_func)
    
    # 3. Create .mod file
    mod_content = f"+ {module_name} 2.0 ./modules/{module_name}\nscripts: scripts\n"
    mod_path = os.path.join(dist_root, f"{module_name}.mod")
    
    with open(mod_path, 'w') as f:
        f.write(mod_content)
    print(f"Created Module File: {mod_path}")
    
    # 4. Create README / Install Guide
    readme_path = os.path.join(dist_root, "INSTALL_GUIDE.txt")
    with open(readme_path, 'w') as f:
        f.write("Qyntara AI Installation Guide v2.0\n")
        f.write("==================================\n\n")
        f.write("1. Copy the 'QyntaraAI.mod' file to your Maya modules folder:\n")
        f.write("   Windows: Documents\\maya\\modules\\\n")
        f.write("   (Create the 'modules' folder if it doesn't exist)\n\n")
        f.write("2. Copy the 'modules' folder to the SAME location.\n")
        f.write("   So you have:\n")
        f.write("   Documents/maya/modules/QyntaraAI.mod\n")
        f.write("   Documents/maya/modules/modules/QyntaraAI/...\n\n")
        f.write("3. Restart Maya.\n\n")
        f.write("4. Run in Python Script Editor:\n")
        f.write("   import qyntara_ai.ui.main_window as gui\n")
        f.write("   gui.show()\n")
        
    print(f"Created README: {readme_path}")
    
    print("Packaging Complete!")

if __name__ == "__main__":
    package_plugin()
