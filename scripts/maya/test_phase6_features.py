import maya.cmds as cmds
import sys
import os

def run_phase6_tests():
    print("\n" + "="*50)
    print("🚀 INIT: QYNTARA AI PHASE 6 (SIMPLYGON EQUIVALENT) TEST")
    print("="*50)

    # Add path so we can import qyntara
    repo_path = "i:/QYNTARA AI"
    if repo_path not in sys.path:
        sys.path.insert(0, repo_path)

    from qyntara_ai.core.topology_engine import TopologyEngine

    # Start clean
    cmds.file(new=True, force=True)
    engine = TopologyEngine()

    # -------------------------------------------------------------
    # TEST 1: Rig Optimizer (Bone Culling & Influence Reduction)
    # -------------------------------------------------------------
    print("\n[TEST 1] Rig Optimizer (Bone Culling & Max Influences)")
    c1 = cmds.polyCylinder(sy=10, h=10, name="RigTest_Hero_Mesh")[0]
    cmds.move(0, 5, 0)
    cmds.select(clear=True)
    
    # Create Skeleton
    j1 = cmds.joint(p=(0, 0, 0), n="Root")
    j2 = cmds.joint(p=(0, 5, 0), n="Spine")
    j3 = cmds.joint(p=(0, 10, 0), n="Head")
    # Add fake "Leaf" bones (e.g. hair/fingers that drive poly count up)
    cmds.select(j3)
    j4 = cmds.joint(p=(-1, 11, 0), n="EarL_Leaf")
    cmds.select(j3)
    j5 = cmds.joint(p=(1, 11, 0), n="EarR_Leaf")
    
    # Bind Skin (Max Influences = 4)
    skin_node = cmds.skinCluster([j1, j2, j3, j4, j5], c1, tsb=True, maxInfluences=4)[0]
    print(f"  -> Created test rig with {cmds.skinCluster(skin_node, q=True, maxInfluences=True)} max influences and leaf bones.")
    
    # Run optimization
    cmds.select(c1)
    res = engine.tool_rig_optimization(target_influences=2)
    print(f"  -> RESULT: {res}")
    
    if cmds.objExists(j4) or cmds.objExists(j5):
        print("  -> WARNING: Leaf bones were not culled!")
    else:
        print("  -> SUCCESS: Non-essential Leaf bones culled perfectly.")
        
    print(f"  -> New Max Influences: {cmds.skinCluster(skin_node, q=True, maxInfluences=True)}")

    # -------------------------------------------------------------
    # TEST 2: Vegetation Optimizer (Billboard Cloud)
    # -------------------------------------------------------------
    print("\n[TEST 2] Vegetation Optimizer (Cross-Plane Generation)")
    cmds.select(clear=True)
    
    # Create fake "dense foliage" ball
    c2 = cmds.polySphere(r=5, name="ForestCanopy_HighPoly")[0]
    cmds.move(15, 5, 0, c2)
    
    cmds.select(c2)
    res2 = engine.tool_vegetation_optimization()
    print(f"  -> RESULT: {res2}")
    
    if cmds.objExists("ForestCanopy_HighPoly_FoliageCloud_LOD"):
        print("  -> SUCCESS: Billboard Cloud mesh generated successfully.")
    else:
        print("  -> WARNING: Vegetation Billboard Cloud not generated!")

    # -------------------------------------------------------------
    # TEST 3: Impostor Hub (Billboard & Texture Baking)
    # -------------------------------------------------------------
    print("\n[TEST 3] Impostor Hub (Hardware Viewport Baking)")
    cmds.select(clear=True)
    
    # Create detailed asset
    c3 = cmds.polyTorus(sr=2, name="Detailed_Prop_HighPoly")[0]
    cmds.move(-15, 2, 0, c3)
    cmds.polyColorPerVertex(c3, r=1, g=0, b=0, a=1, cdo=True) # Give it color so it renders
    
    cmds.select(c3)
    res3 = engine.tool_create_billboard(resolution=512)
    print(f"  -> RESULT: {res3}")
    
    if cmds.objExists("Detailed_Prop_HighPoly_Billboard"):
        print("  -> SUCCESS: 2D Billboard plane baked and injected into scene.")
    else:
        print("  -> WARNING: Billboard mesh not created.")

    print("\n" + "="*50)
    print("✅ PHASE 6 TESTS COMPLETE! You can view the generated results in the Viewport.")
    print("="*50)

if __name__ == "__main__":
    run_phase6_tests()
