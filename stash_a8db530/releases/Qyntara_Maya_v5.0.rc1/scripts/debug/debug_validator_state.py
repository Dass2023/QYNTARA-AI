
import maya.cmds as cmds

def debug_object_state():
    sel = cmds.ls(sl=True, long=True)
    if not sel:
        print("Please select the object.")
        return

    obj = sel[0]
    print(f"\n--- DEBUG STATUS FOR: {obj} ---")
    
    # 1. Check Transform
    print(f"Transform: {obj}")
    
    # 2. Check All Shapes
    shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
    print(f"Shapes Found: {len(shapes)}")
    
    for s in shapes:
        is_inter = cmds.getAttr(f"{s}.intermediateObject")
        print(f"\n  SHAPE: {s}")
        print(f"    - Intermediate (History): {is_inter}")
        
        # Check UV Sets on THIS SPECIFIC SHAPE
        sets = cmds.polyUVSet(s, q=True, allUVSets=True) or []
        print(f"    - UV Sets: {sets}")
        
        # Check UV Count for 'Lightmap' if it exists
        if 'Lightmap' in sets:
            count = cmds.polyEvaluate(s, uv=True, uvSetName='Lightmap')
            print(f"    - 'Lightmap' UV Count: {count}")
        elif 'uvSet2' in sets:
             count = cmds.polyEvaluate(s, uv=True, uvSetName='uvSet2')
             print(f"    - 'uvSet2' UV Count: {count}")

    print("\n--- END DEBUG ---")

debug_object_state()
