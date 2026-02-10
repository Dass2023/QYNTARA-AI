
import maya.cmds as cmds

def debug_scope():
    print("--- DEBUG SELECTION SCOPE ---")
    
    # 1. Transforms
    transforms = cmds.ls(type="transform")
    print(f"Transforms found: {len(transforms)}")
    
    # 2. Joints
    joints = cmds.ls(type="joint")
    print(f"Joints found: {len(joints)}")
    
    # 3. Intersection
    intersect = set(transforms) & set(joints)
    print(f"Joints inside Transforms list: {len(intersect)}")
    
    # Check specific invalid assets
    root_invalid = "INVALID_anim_root_motion"
    if cmds.objExists(root_invalid):
        if root_invalid in transforms:
             print(f"FAIL: {root_invalid} (Joint) IS in transform list.")
        else:
             print(f"SUCCESS DISTINCTION: {root_invalid} (Joint) is NOT in transform list.")
             
    padding_invalid = "INVALID_bake_padding"
    # Find full path logic might obscure checking, just check existence in list
    found_padding = any(padding_invalid in t for t in transforms)
    print(f"Padding Object in Transforms: {found_padding}")

debug_scope()
