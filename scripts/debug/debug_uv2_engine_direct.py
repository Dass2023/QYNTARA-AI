
import logging
from maya import cmds
from qyntara_ai.core import uv_engine

# Setup Logging
logging.basicConfig(level=logging.INFO)
uv_engine.logger.setLevel(logging.INFO)

def run_debug():
    print("--- STARTING UV ENGINE DEBUG ---")
    
    sel = cmds.ls(sl=True)
    if not sel:
        print("Please select an object.")
        return
        
    obj = sel[0]
    print(f"Object: {obj}")
    
    # 1. Clean Slate (Delete uvSet2 if exists)
    try:
        if 'uvSet2' in (cmds.polyUVSet(obj, q=True, allUVSets=True) or []):
            print("Deleting existing uvSet2...")
            cmds.polyUVSet(obj, delete=True, uvSet='uvSet2')
    except: pass
    
    # 2. Run Engine
    print("Invoking UVEngine.process(profile='lightmap')...")
    try:
        uv_engine.UVEngine.process(obj, profile='lightmap')
        print("Engine finished.")
    except Exception as e:
        print(f"ENGINE CRASHED: {e}")
        import traceback
        traceback.print_exc()
        
    # 3. Verify
    all_sets = cmds.polyUVSet(obj, q=True, allUVSets=True) or []
    print(f"Final Sets: {all_sets}")
    
    if len(all_sets) < 2:
        print("FAILURE: System has < 2 sets.")
    else:
        # Check counts
        uv_count = 0
        try:
            uvs = cmds.polyUVSet(obj, q=True, uvs=True, uvSet=all_sets[1])
            if uvs: uv_count = len(uvs)
        except: pass
        print(f"Set 2 ({all_sets[1]}) count: {uv_count}")
        
        if uv_count > 0:
            print("SUCCESS: UV2 Generated and Populated.")
        else:
            print("FAILURE: UV2 Exists but is EMPTY.")

run_debug()
