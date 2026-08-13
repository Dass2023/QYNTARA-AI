# Debugging Qyntara AI in Maya

## 1. Quick "Print" Debugging
The simplest way is to check the **Script Editor** (Window > General Editors > Script Editor).
- Ensure `History > Show Stack Trace` is enabled.
- All `logger.info` and `print` statements appear here.

## 2. Reloading Code (Critical!)
Maya caches Python modules. If you change code, simply re-running the button WONT work. You must **reload** the modules.

Use this script in the Maya Python Editor to force a reload:

```python
import sys
import qyntara_ai.ui.main_window
import qyntara_ai.core.validator
import qyntara_ai.core.geometry
# ... add other modules you are editing

from importlib import reload

# Reload core logic first
reload(qyntara_ai.core.geometry)
reload(qyntara_ai.core.validator)

# Reload UI last
reload(qyntara_ai.ui.main_window)

# Re-launch
qyntara_ai.ui.main_window.show()
```

## 3. Visual Studio Code Remote Debugging
To set breakpoints in VS Code and hit them when running in Maya:

### Step A: Install `debugpy` in Maya
You need to install the `debugpy` package into Maya's Python environment.
1. Open Command Prompt as Administrator.
2. Navigate to Maya's `bin` directory (e.g., `C:\Program Files\Autodesk\Maya2024\bin`).
3. Run:
   ```bash
   mayapy -m pip install debugpy
   ```

### Step B: Configure VS Code
1. Open `.vscode/launch.json` in your project.
2. Add this configuration:
   ```json
   {
       "name": "Attach to Maya",
       "type": "python",
       "request": "attach",
       "connect": {
           "host": "localhost",
           "port": 5678
       },
       "pathMappings": [
           {
               "localRoot": "${workspaceFolder}/qyntara_ai",
               "remoteRoot": "E:/QYNTARA AI/qyntara_ai" 
           }
       ]
   }
   ```
   *Note: Ensure `remoteRoot` matches where the plugin is loaded in Maya.*

### Step C: Start Debug Server in Maya
Run this code in Maya **once** per session:
```python
import debugpy
# Allow VS Code to connect
debugpy.configure(python="python")
debugpy.listen(5678)
print("Waiting for debugger attach...")
# debugpy.wait_for_client() # Uncomment if you want to block until attached
```

### Step D: Attach
1. Press F5 in VS Code ("Attach to Maya").
2. Your breakpoints will now trigger!
