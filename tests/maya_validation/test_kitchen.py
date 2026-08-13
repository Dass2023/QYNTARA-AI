import maya.cmds as cmds
import qyntara_ai.core.ai_tools as ai_tools
import importlib
importlib.reload(ai_tools)

def test_kitchen_environment():
    print("--- Setting up Test Environment ---")
    cmds.file(new=True, force=True)
    
    # 1. Create Incorrect Objects
    # Counter: Too low (50cm)
    c = cmds.polyCube(n="Kitchen_Counter_01", w=60, h=50, d=60)[0]
    cmds.move(0, 25, 0, c) # Sit on ground
    
    # Cabinet: Too tall (300cm)
    cab = cmds.polyCube(n="Kitchen_Cabinet_Tall_01", w=60, h=300, d=60)[0]
    cmds.move(100, 150, 0, cab)
    
    # Chair: Correct (50cm)
    ch = cmds.polyCube(n="Dining_Chair_01", w=40, h=50, d=40)[0]
    cmds.move(-100, 25, 0, ch)
    
    # Select all
    cmds.select([c, cab, ch])
    
    print("Objects Created:")
    print(f"- {c}: Height 50cm (Expected ~90cm)")
    print(f"- {cab}: Height 300cm (Expected ~210cm max)")
    print(f"- {ch}: Height 50cm (Correct)")
    
    # 2. Run Analysis
    print("\n--- Running Scene Analysis ---")
    report = ai_tools.SceneAnalyzer.execute()
    print("REPORT RAW HTML:")
    print(report.replace("<br>", "\n"))
    
    # 3. Run Auto-Fix
    print("\n--- Running Auto-Fix ---")
    fix_report = ai_tools.SceneAnalyzer.fix_deviations()
    print("FIX REPORT RAW HTML:")
    print(fix_report.replace("<br>", "\n"))
    
    # 4. Verify Fix
    print("\n--- Verifying Results ---")
    h_c = ai_tools.SceneAnalyzer.get_world_dimensions(c)[1]
    h_cab = ai_tools.SceneAnalyzer.get_world_dimensions(cab)[1]
    
    print(f"Counter Final Height: {h_c:.1f}cm (Target: 90.0)")
    print(f"Cabinet Final Height: {h_cab:.1f}cm (Target: 145.0 avg)") # (70+220)/2 = 145
    
    if abs(h_c - 90.0) < 1.0:
        print("SUCCESS: Counter fixed correctly.")
    else:
        print("FAILURE: Counter height mismatch.")

if __name__ == "__main__":
    test_kitchen_environment()
