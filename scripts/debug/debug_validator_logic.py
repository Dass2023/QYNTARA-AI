import maya.cmds as cmds

def debug_ngons():
    obj = "INVALID_geo_ngons"
    if not cmds.objExists(obj):
        print(f"MISSING: {obj}")
        return

    print(f"\n--- Debugging {obj} ---")
    cmds.select(obj)
    # Replicating geometry.check_ngons logic
    cmds.polySelectConstraint(mode=3, type=8, size=3)
    sl = cmds.ls(sl=True, flatten=True)
    print(f"Constraint Selection (N-gons): {sl}")
    cmds.polySelectConstraint(disable=True)
    
    # Check if manually converting helps
    cmds.select(f"{obj}.f[:]")
    cmds.polySelectConstraint(mode=3, type=8, size=3)
    sl2 = cmds.ls(sl=True, flatten=True)
    print(f"Explicit Face Selection (N-gons): {sl2}")
    cmds.polySelectConstraint(disable=True)

def debug_normals():
    obj = "INVALID_geo_normals"
    if not cmds.objExists(obj): return

    print(f"\n--- Debugging {obj} ---")
    verts = cmds.polyListComponentConversion(obj, tv=True)
    locked = cmds.polyNormalPerVertex(verts, q=True, freezeNormal=True)
    print(f"Locked Normals Found: {any(locked) if locked else 'None'}")
    
def debug_zero_area():
    obj = "INVALID_geo_zero_area"
    if not cmds.objExists(obj): return
    print(f"\n--- Debugging {obj} ---")
    areas = cmds.polyEvaluate(obj, fa=True)
    print(f"Face Areas: {areas}")
    zero = [a for a in areas if a < 0.0001]
    print(f"Zero Area Count: {len(zero)}")

def debug_floating():
    obj = "INVALID_geo_floating"
    if not cmds.objExists(obj): return
    print(f"\n--- Debugging {obj} ---")
    # Floating logic depends on 'avg_vol' of ALL objects. 
    # Let's check volume of this one.
    bb = cmds.xform(obj, q=True, bb=True, ws=True)
    vol = (bb[3]-bb[0])*(bb[4]-bb[1])*(bb[5]-bb[2])
    print(f"Volume: {vol}")
    
    # Check debris
    shapes = cmds.listRelatives(obj, c=True)
    # Wait, generator parents a 'bit' to 'i'.
    # Does check_floating recurse? No, check_floating iterates 'objects' list.
    # The 'bit' is a separate transform if parented? Yes.
    # Does 'objects' list contain children?
    # Usually validator needs flattened list.
    children = cmds.listRelatives(obj, c=True, type='transform')
    print(f"Children: {children}")
    if children:
        bb2 = cmds.xform(children[0], q=True, bb=True, ws=True)
        vol2 = (bb2[3]-bb2[0])*(bb2[4]-bb2[1])*(bb2[5]-bb2[2])
        print(f"Child Volume: {vol2}")

debug_ngons()
debug_normals()
debug_zero_area()
debug_floating()
