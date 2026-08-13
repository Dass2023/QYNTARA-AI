import os
import re

dirs = [r"i:\QYNTARA AI\tests\unit", r"i:\QYNTARA AI\tests\integration"]

for d in dirs:
    for f in os.listdir(d):
        if not f.endswith(".py"):
            continue
        path = os.path.join(d, f)
        with open(path, "r", encoding="utf-8") as file:
            content = file.read()
        
        # We need to remove lines doing sys.modules['maya'] or sys.modules["maya"]
        # or maya.cmds etc. Since conftest.py handles it, we can comment them out.
        new_content = re.sub(r'^(.*?sys\.modules\[[\'"]maya(?:.*?)*[\'"]\].*)$', r'# \1', content, flags=re.MULTILINE)
        new_content = re.sub(r'^(.*?sys\.modules\[[\'"]PySide2(?:.*?)*[\'"]\].*)$', r'# \1', new_content, flags=re.MULTILINE)
        new_content = re.sub(r'^(.*?sys\.modules\[[\'"]shiboken\d(?:.*?)*[\'"]\].*)$', r'# \1', new_content, flags=re.MULTILINE)

        if content != new_content:
            with open(path, "w", encoding="utf-8") as file:
                file.write(new_content)
            print(f"Patched {f}")
print("Done patching.")
