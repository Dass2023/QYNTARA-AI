
import maya.cmds as cmds

def diagnose_and_force_uv2():
    sel = cmds.ls(sl=True)
    if not sel:
        print("ERROR: Select the object first.")
        return

    obj = sel[0]
    print(f"DIAGNOSING: {obj}")

    # 1. Check Locks
    is_locked = cmds.lockNode(obj, q=True, lock=True)[0]
    print(f"Locked Status: {is_locked}")
    
    # 2. Existing Sets
    sets = cmds.polyUVSet(obj, q=True, allUVSets=True) or []
    print(f"Current Sets: {sets}")
    
    if len(sets) >= 2:
        print(f"  -> UV2 ALREADY EXISTS at index 1: {sets[1]}")
        return

    # 3. Method A: Simple Create
    print("Attempting Method A: polyUVSet(create=True)...")
    try:
        cmds.polyUVSet(obj, create=True, uvSet='uvSet2_MethodA')
        print("  -> Method A SUCCESS.")
    except Exception as e:
        print(f"  -> Method A FAILED: {e}")

    # 4. Method B: Copy
    print("Attempting Method B: polyCopyUV...")
    try:
        base = sets[0] if sets else 'map1'
        cmds.polyCopyUV(obj, uvSetNameInput=base, uvSetName='uvSet2_MethodB', ch=False)
        print("  -> Method B SUCCESS.")
    except Exception as e:
        print(f"  -> Method B FAILED: {e}")

    # 5. Method C: Copy with History
    print("Attempting Method C: polyCopyUV (History=True)...")
    try:
        base = sets[0] if sets else 'map1'
        cmds.polyCopyUV(obj, uvSetNameInput=base, uvSetName='uvSet2_MethodC', ch=True)
        print("  -> Method C SUCCESS.")
    except Exception as e:
        print(f"  -> Method C FAILED: {e}")

    # Final Check
    final_sets = cmds.polyUVSet(obj, q=True, allUVSets=True) or []
    print(f"FINAL SETS: {final_sets}")

diagnose_and_force_uv2()
