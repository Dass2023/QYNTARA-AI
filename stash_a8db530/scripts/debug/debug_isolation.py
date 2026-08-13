
import maya.cmds as cmds
import sys
import logging

# Ensure paths
if "e:/QYNTARA AI" not in sys.path:
    sys.path.append("e:/QYNTARA AI")

try:
    from qyntara_ai.core import baking, animation, geometry
    import maya.api.OpenMaya as om
except ImportError as e:
    print(f"Import Error: {e}")

def run_debug():
    print("\n--- DEBUGGING ISOLATION ---")
    
    # 1. PADDING CHECK
    obj = "GRP_bake_padding|INVALID_bake_padding"
    if cmds.objExists(obj):
        print(f"\nChecking Padding on {obj}...")
        try:
            # Force verify API logic here locally if needed
            res = baking.check_padding([obj])
            print(f"Result: {len(res)} violations.")
            if res:
                print(f"Violation: {res[0]}")
            else:
                # Debug internal
                sl = om.MSelectionList()
                sl.add(obj)
                dag = sl.getDagPath(0)
                fn = om.MFnMesh(dag)
                nb, ids = fn.getUvShellsIds(uvSet="map1")
                print(f"DEBUG Internal: Shells={nb}")
        except Exception as e:
            print(f"Error checking padding: {e}")
    else:
        print(f"Object {obj} not found!")

    # 2. ROOT MOTION
    obj = "GRP_anim_root_motion|INVALID_anim_root_motion"
    if cmds.objExists(obj):
        print(f"\nChecking Root Motion on {obj}...")
        res = animation.check_root_motion([obj])
        print(f"Result: {len(res)} violations.")
    else:
        # Try finding it loosely
        ls = cmds.ls("*INVALID_anim_root_motion*", r=True)
        if ls:
             print(f"\nChecking Root Motion on {ls[0]}...")
             res = animation.check_root_motion(ls)
             print(f"Result: {len(res)} violations.")
        else:
             print(f"Root Motion Obj not found.")

    # 3. BAKED ANIM
    obj = "GRP_anim_baked|INVALID_anim_baked"
    if cmds.objExists(obj):
         print(f"\nChecking Baked Anim on {obj}...")
         # Need to ensure it's treated as a Joint or Transform
         res = animation.check_animation_baked([obj])
         print(f"Result: {len(res)} violations.")

run_debug()
