import os
import sys
import platform

def get_maya_module_path():
    """
    Returns the default Maya module path for the user.
    """
    home = os.path.expanduser("~")
    if platform.system() == "Windows":
        return os.path.join(home, "Documents", "maya", "modules")
    elif platform.system() == "Darwin":
        return os.path.join(home, "Library", "Preferences", "Autodesk", "maya", "modules")
    else:
        return os.path.join(home, "maya", "modules")

def install():
    print("Installing Qyntara AI Plugin...")
    
    # Current path is inside install/ folder
    # We want the root of the package
    current_dir = os.path.dirname(os.path.abspath(__file__))
    package_root = os.path.dirname(current_dir) # qyntara_ai
    
    # We actually want the parent of qyntara_ai to be in PYTHONPATH?
    # No, typically modules add the path TO the module.
    # If the structure is QYNTARA AI/qyntara_ai
    # We probably want to add "E:/QYNTARA AI" to PYTHONPATH so "import qyntara_ai" works.
    # OR we make the module root E:/QYNTARA AI/qyntara_ai and verify init.
    
    # Let's assume the module definition points to "E:/QYNTARA AI" so Python picks up "qyntara_ai" package.
    root_path = os.path.dirname(package_root) # E:/QYNTARA AI/
    
    module_path = get_maya_module_path()
    if not os.path.exists(module_path):
        os.makedirs(module_path)
        
    mod_file = os.path.join(module_path, "QyntaraAI.mod")
    
    # MOD Format: + QyntaraAI 1.0 <PATH>
    # [r] scripts: <PATH>/scripts (if we had a scripts folder, but we are pure python package)
    # We can add PYTHONPATH
    
    # To run "import qyntara_ai", the parent folder of "qyntara_ai" must be valid.
    # So we point the module to root_path.
    
    content = f"+ QyntaraAI 1.0 {root_path}\n"
    content += "PYTHONPATH +:= .\n" 
    # The "." relative to module root (root_path) is where qyntara_ai folder lives.
    
    try:
        with open(mod_file, "w") as f:
            f.write(content)
        print(f"Successfully created module file at {mod_file}")
        print(f"Plugin configured to load from {root_path}")
    except Exception as e:
        print(f"Failed to install: {e}")

if __name__ == "__main__":
    install()
