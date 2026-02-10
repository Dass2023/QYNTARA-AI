import os
import shutil
import sys
import platform

def install():
    print("--- QYNTARA AI CLIENT INSTALLER ---")
    
    # 1. Locate Source
    current_dir = os.path.dirname(os.path.abspath(__file__))
    source_file = os.path.join(current_dir, "maya", "qyntara_client.py")
    
    if not os.path.exists(source_file):
        print(f"ERROR: Could not find source file at {source_file}")
        return

    # 2. Locate Target (Maya Scripts)
    # Windows: Documents\maya\scripts
    user_home = os.path.expanduser("~")
    maya_scripts_dir = os.path.join(user_home, "Documents", "maya", "scripts")
    
    if not os.path.exists(maya_scripts_dir):
        # Try to make it?
        try:
            os.makedirs(maya_scripts_dir)
        except:
             print(f"WARNING: Could not find or create standard Maya scripts path: {maya_scripts_dir}")
             print("Please select your Maya scripts folder manually.")
             return

    target_file = os.path.join(maya_scripts_dir, "qyntara_client.py")
    
    # 3. Copy
    try:
        shutil.copy2(source_file, target_file)
        print(f"SUCCESS: Copied client to {target_file}")
    except Exception as e:
        print(f"ERROR: Failed to copy file: {e}")
        return

    # 4. Instructions
    print("\n--- INSTALLATION COMPLETE ---")
    print("To launch Qyntara AI in Maya:")
    print("1. Open Autodesk Maya.")
    print("2. Open the Script Editor (Python tab).")
    print("3. Paste and run the following code:")
    print("-" * 40)
    print("import qyntara_client")
    print("try:")
    print("    import importlib")
    print("    importlib.reload(qyntara_client)")
    print("except:")
    print("    reload(qyntara_client)")
    print("qyntara_client.show()")
    print("-" * 40)
    print("You can drag this code to your Shelf to create a button.")

if __name__ == "__main__":
    install()
    input("\nPress Enter to exit...")
