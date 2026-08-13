import os
import sys

def install_qyntara_module():
    """
    detects the user's maya/modules directory and creates a .mod file pointing
    to this repository's 'maya' folder.
    """
    print("🚀 Installing Qyntara AI for Maya...")

    # 1. Determine Target Directory (User Documents/maya/modules)
    # Windows: C:\Users\<User>\Documents\maya\modules
    user_home = os.path.expanduser("~")
    target_dir = os.path.join(user_home, "Documents", "maya", "modules")
    
    if not os.path.exists(target_dir):
        try:
            os.makedirs(target_dir)
            print(f"✅ Created modules directory: {target_dir}")
        except Exception as e:
            print(f"❌ Failed to create directory: {e}")
            return

    # 2. Get Current Repo Path (Location of this script)
    repo_root = os.path.abspath(os.path.dirname(__file__))
    maya_plugin_path = os.path.join(repo_root, "maya")
    
    if not os.path.exists(maya_plugin_path):
        print(f"❌ Error: Could not find 'maya' directory at {maya_plugin_path}")
        return

    # 3. Create .mod File Content
    # Format: + Qyntara 1.0 <PATH_TO_PLUGIN>
    mod_content = f"+ Qyntara 1.0 {maya_plugin_path}\n"
    mod_content += "scripts: .\n" # Add scripts path relative to module root
    mod_content += "icons: icons\n" # Add icons path relative to module root (if exists)

    # 4. Write .mod File
    mod_file_path = os.path.join(target_dir, "Qyntara.mod")
    try:
        with open(mod_file_path, "w") as f:
            f.write(mod_content)
        print(f"✅ Written module file: {mod_file_path}")
        print(f"   Pointing to: {maya_plugin_path}")
    except Exception as e:
        print(f"❌ Failed to write .mod file: {e}")
        return
    
    print("\n✨ Installation Complete!")
    print("Restart Maya to load the Qyntara module.")

if __name__ == "__main__":
    install_qyntara_module()
    try:
        input("\nPress Enter to exit...")
    except:
        pass
