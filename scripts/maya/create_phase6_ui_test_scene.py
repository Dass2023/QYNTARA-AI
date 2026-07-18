import maya.cmds as cmds

def setup_ui_test_scene():
    print("\n" + "="*50)
    print("🚀 INIT: QYNTARA AI PHASE 6 - UI TEST SETUP")
    print("="*50)

    # Start clean
    cmds.file(new=True, force=True)

    # 1. Rig Test Object
    print("\n[SETUP 1] Preparing Rig Test Object...")
    c1 = cmds.polyCylinder(sy=10, h=10, name="RigTest_Hero_Mesh")[0]
    cmds.move(0, 5, 0)
    cmds.select(clear=True)
    j1 = cmds.joint(p=(0, 0, 0), n="Root")
    j2 = cmds.joint(p=(0, 5, 0), n="Spine")
    j3 = cmds.joint(p=(0, 10, 0), n="Head")
    cmds.select(j3)
    j4 = cmds.joint(p=(-1, 11, 0), n="EarL_Leaf")
    cmds.select(j3)
    j5 = cmds.joint(p=(1, 11, 0), n="EarR_Leaf")
    cmds.skinCluster([j1, j2, j3, j4, j5], c1, tsb=True, mi=4)

    # 2. Vegetation Test Object
    print("[SETUP 2] Preparing Vegetation Test Object...")
    c2 = cmds.polySphere(r=5, name="ForestCanopy_HighPoly")[0]
    cmds.move(15, 5, 0, c2)

    # 3. Impostor Test Object
    print("[SETUP 3] Preparing Impostor Test Object...")
    c3 = cmds.polyTorus(sr=2, name="Detailed_Prop_HighPoly")[0]
    cmds.move(-15, 2, 0, c3)
    cmds.polyColorPerVertex(c3, r=1, g=0, b=0, a=1, cdo=True)
    
    # 4. Aggregation Test Objects
    print("[SETUP 4] Preparing Aggregation Test Architecture...")
    grp = cmds.group(em=True, name="Building_Cluster")
    b1 = cmds.polyCube(w=5, h=20, d=5, name="Skyscraper_A")[0]
    cmds.move(0, 10, -20, b1)
    b2 = cmds.polyCube(w=10, h=5, d=5, name="Base_B")[0]
    cmds.move(0, 2.5, -20, b2)
    cmds.parent([b1, b2], grp)

    print("\n" + "="*50)
    print("✅ TEST SCENE READY!")
    print("To test the new UI:")
    print("1. Open the Qyntara AI UI (Launch Qyntara).")
    print("2. Navigate to the 'Optimization & Export' tab.")
    print("3. Select the object in the scene, and click the corresponding Simplygon AI button!")
    print("="*50)

if __name__ == "__main__":
    setup_ui_test_scene()
