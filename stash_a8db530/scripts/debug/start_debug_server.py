"""
Script to start a debug server in Maya using debugpy.
Copy and paste this entire script into the Maya Script Editor (Python Tab) and run it.

It will:
1. Check if 'debugpy' is installed.
2. If not, it will tell you the command to install it.
3. If installed, it will start the debug server on port 5678.
"""
import sys
import os

def install_debugpy_setup():
    try:
        import debugpy
    except ImportError:
        print("="*60)
        print("MISSING DEPENDENCY: debugpy")
        print("="*60)
        print("To verify/debug code in Maya from VS Code, you need 'debugpy'.")
        print("Please run the following command in your terminal/command prompt:")
        print("")
        
        # Try to find mayapy path
        mayapy_path = os.path.join(os.path.dirname(sys.executable), "mayapy.exe")
        if not os.path.exists(mayapy_path):
            mayapy_path = "mayapy" # Fallback to global alias
            
        print(f'"{mayapy_path}" -m pip install debugpy')
        print("")
        print("After installing, run this script again.")
        print("="*60)
        return

    # Check if already running
    try:
        # If we are already attached, this might verify it? 
        # debugpy doesn't have a simple "is_running" check that is public api, 
        # but we can try to configure.
        debugpy.configure(python="python") 
        
        # Start listener
        # This will error if port is in use (e.g. already running)
        debugpy.listen(("0.0.0.0", 5678))
        print("="*60)
        print("DEBUG SERVER STARTED")
        print("="*60)
        print("1. Go to VS Code")
        print("2. Go to 'Run and Debug' (Ctrl+Shift+D)")
        print("3. Select 'Attach to Maya'")
        print("4. Press F5")
        print("="*60)
        
    except RuntimeError as e:
        if "Address already in use" in str(e) or "already listening" in str(e).lower():
            print("Debug server is ALREADY RUNNING on port 5678.")
            print("You can attach VS Code now.")
        else:
            print(f"Error starting debug server: {e}")
            # It might be that it's already listening from a previous session
            print("Assuming server is active. Try attaching VS Code.")

if __name__ == "__main__":
    install_debugpy_setup()
