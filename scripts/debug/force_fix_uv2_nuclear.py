
import maya.cmds as cmds
import maya.mel as mel

def nuclear_fix():
    print("\n--- NUCLEAR UV FIX ---")
    sel = cmds.ls(sl=True)
    if not sel:
        print("ERROR: Select object.")
        return
    obj = sel[0]
    
    # 1. Pre-Clean
    print(f"Target: {obj}")
    print("Step 1: Delete History (Pre-Clean)")
    cmds.delete(obj, ch=True)
    
    # 2. Delete Existing
    sets = cmds.polyUVSet(obj, q=True, allUVSets=True) or []
    print(f"Existing Sets: {sets}")
    
    if 'uvSet2' in sets:
        print("Step 2a: Deleting uvSet2...")
        cmds.polyUVSet(obj, delete=True, uvSet='uvSet2')
        
    if 'Lightmap' in sets:
        print("Step 2b: Deleting Lightmap...")
        cmds.polyUVSet(obj, delete=True, uvSet='Lightmap')

    # 3. Create NEW
    print("Step 3: Creating 'Lightmap' Set...")
    try:
        cmds.polyUVSet(obj, create=True, uvSet='Lightmap')
        print("  -> Created.")
    except Exception as e:
        print(f"  -> CREATE FAILED: {e}")
        # Try copy?
        try:
            print("  -> Trying Copy Fallback...")
            cmds.polyCopyUV(obj, uvSetNameInput='map1', uvSetName='Lightmap', ch=False)
            print("  -> Copy Success.")
        except Exception as e2:
            print(f"  -> COPY FAILED: {e2}")
            return # Fatal

    # 4. Populate
    print("Step 4: Populating (AutoProjection)...")
    try:
        cmds.polyUVSet(obj, currentUVSet=True, uvSet='Lightmap')
        cmds.polyAutoProjection(obj, lm=0, pb=0, ibd=1, cm=0, l=2, sc=1, o=1, ps=0.02, ws=0)
        print("  -> Projected.")
    except Exception as e:
        print(f"  -> PROJECTION FAILED: {e}")

    # 5. Verify
    final_sets = cmds.polyUVSet(obj, q=True, allUVSets=True)
    print(f"Final Sets: {final_sets}")
    count = cmds.polyEvaluate(obj, uv=True, uvSetName='Lightmap')
    print(f"Lightmap Count: {count}")
    
    # 6. Bake History
    print("Step 6: Final Bake...")
    cmds.delete(obj, ch=True)
    
    if count and count > 0:
        print("SUCCESS: Lightmap Created and Populated.")
        cmds.inViewMessage(amg='<hl>Nuclear Fix:</hl> SUCCESS.', pos='midCenter', fade=True)
    else:
        print("FAILURE: Lightmap Empty or Missing.")

nuclear_fix()
