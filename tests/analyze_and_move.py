import os
import shutil

tests_dir = r"i:\QYNTARA AI\tests"
unit_dir = os.path.join(tests_dir, "unit")
integ_dir = os.path.join(tests_dir, "integration")
maya_dir = os.path.join(tests_dir, "maya_validation")

for f in os.listdir(tests_dir):
    if not f.endswith(".py") or f in ["conftest.py", "analyze_and_move.py"]:
        continue
    
    path = os.path.join(tests_dir, f)
    with open(path, "r", encoding="utf-8") as file:
        content = file.read()
    
    # 1. Integration Tests
    if "urllib" in content or "requests" in content or "TestClient" in content or "test_web_payload" in f or "test_ws" in f:
        print(f"Moving {f} to integration")
        shutil.move(path, os.path.join(integ_dir, f))
    # 2. Maya Validation Tests (Expects real Maya, no sys.modules mocking of maya)
    elif "maya.cmds" in content and "sys.modules" not in content and "MagicMock" not in content:
        print(f"Moving {f} to maya_validation")
        shutil.move(path, os.path.join(maya_dir, f))
    # 3. Unit Tests (Mocks Maya or tests pure Python logic)
    else:
        print(f"Moving {f} to unit")
        shutil.move(path, os.path.join(unit_dir, f))

print("Done migrating tests.")
