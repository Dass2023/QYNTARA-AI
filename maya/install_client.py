import os
import shutil
import sys
import platform

def get_maya_scripts_dir():
    """
    Attempts to find the default Maya scripts directory.
    """
    system = platform.system()
    home = os.path.expanduser("~")
    
    if system == "Windows":
        # Check for Documents/maya/scripts
        base_path = os.path.join(home, "Documents", "maya", "scripts")
        if os.path.exists(base_path):
            return base_path
        
        # Fallback to checking specific versions if generic scripts dir doesn't exist
        # This is less robust but a reasonable fallback
        maya_base = os.path.join(home, "Documents", "maya")
        if os.path.exists(maya_base):
            versions = [d for d in os.listdir(maya_base) if d.isdigit()]
            if versions:
                # Pick the latest version
                latest_version = sorted(versions)[-1]
                return os.path.join(maya_base, latest_version, "scripts")
                
    elif system == "Darwin": # macOS
        base_path = os.path.join(home, "Library", "Preferences", "Autodesk", "maya", "scripts")
        if os.path.exists(base_path): return base_path
        
    elif system == "Linux":
        base_path = os.path.join(home, "maya", "scripts")
        if os.path.exists(base_path): return base_path
        
    return None

def install():
    print("--- QYNTARA AI Client Installer ---")
    
    # Source file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    client_script = os.path.join(current_dir, "qyntara_client.py")
    
    if not os.path.exists(client_script):
        print(f"Error: Could not find 'qyntara_client.py' in {current_dir}")
        return

    # Destination
    dest_dir = get_maya_scripts_dir()
    
    if not dest_dir:
        print("Could not automatically locate Maya scripts directory.")
        dest_dir = input("Please enter the full path to your Maya scripts directory: ").strip()
        if not os.path.exists(dest_dir):
            print("Error: Directory does not exist.")
            return

    print(f"Installing to: {dest_dir}")
    
    try:
        shutil.copy2(client_script, dest_dir)
        print("Success! 'qyntara_client.py' has been copied.")
        print("\nTo launch in Maya (FORCE UPDATE):")
        print("-" * 40)
        print("import qyntara_client")
        print("from importlib import reload")
        print("reload(qyntara_client)")
        print("qyntara_client.show()")
        print("-" * 40)
    except Exception as e:
        print(f"Installation failed: {e}")

if __name__ == "__main__":
    install()
