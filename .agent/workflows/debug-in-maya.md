---
description: Debugging Qyntara AI running inside Maya using VS Code
---

// turbo
1. Ensure `.vscode/launch.json` is configured with "Attach to Maya".
2. Open Maya.
3. Open the **Script Editor** (Windows > General Editors > Script Editor).
4. Go to a **Python** tab.
5. Create or load the debug server script. **The most robust way is to read and execute the file directly**, to avoid conflicts with Maya's internal 'scripts' folder:
```python
import sys
import os

repo_root = r"i:\QYNTARA AI"
debug_script = os.path.join(repo_root, "scripts", "debug", "start_debug_server.py")

if os.path.exists(debug_script):
    with open(debug_script, "r") as f:
        exec(f.read(), globals())
else:
    print(f"Error: Could not find {debug_script}")
```
6. **Execution**:
    - If `debugpy` is missing, the script will print the command to run in your terminal (e.g., `mayapy -m pip install debugpy`). Run that command, restart Maya, and repeat step 5.
    - If successful, it will say **"DEBUG SERVER STARTED"**.
7. **VS Code**:
    - Go to the **Run and Debug** view (Ctrl+Shift+D).
    - Select "**Attach to Maya**".
    - Press **F5**.
8. **Breakpoints**: Set breakpoints in your `qyntara_ai` code (e.g., inside `QyntaraValidator.run_validation`).
9. **Trigger Code**: Run your verification script in Maya (e.g., `scripts/verification/verify_in_maya.py` or the button in your UI).
   - VS Code should hit the breakpoint.
