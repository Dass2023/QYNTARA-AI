"""
QYNTARA NEXUS VALIDATION SYSTEM
Golden Scene Oracle Generator
---------------------------------------
Procedurally generates 25 distinct validation oracle scenes
with known deterministic states to prove rule correctness.
"""
import os
try:
    from maya import cmds
except ImportError:
    cmds = None

def generate_golden_scenes(output_dir):
    if not cmds:
        print("Cannot run outside of Maya.")
        return
        
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    def save_scene(name):
        path = os.path.join(output_dir, f"{name}.mb")
        cmds.file(rename=path)
        cmds.file(save=True, type="mayaBinary", force=True)
        print(f"Generated Oracle Scene: {name}.mb")

    # ---------------------------------------------------------
    # 01. CLEAN ASSET
    # ---------------------------------------------------------
    cmds.file(new=True, force=True)
    cube = cmds.polyCube(name="Clean_Asset_Cube")[0]
    cmds.polyColorPerVertex(cube, rgb=(1, 1, 1)) # Add vertex colors
    # Create UVs properly
    cmds.polyAutoProjection(cube)
    cmds.select(clear=True)
    save_scene("01_CLEAN_ASSET")

    # ---------------------------------------------------------
    # 02. BAD TRANSFORM
    # ---------------------------------------------------------
    cmds.file(new=True, force=True)
    cube = cmds.polyCube(name="Bad_Transform_Cube")[0]
    cmds.setAttr(f"{cube}.translateZ", 5.0) # Unfrozen translation
    cmds.setAttr(f"{cube}.rotateY", 45.0)   # Unfrozen rotation
    save_scene("02_BAD_TRANSFORM")

    # ---------------------------------------------------------
    # 03. BAD SCALE (NON-UNIFORM)
    # ---------------------------------------------------------
    cmds.file(new=True, force=True)
    cube = cmds.polyCube(name="Bad_Scale_Cube")[0]
    cmds.setAttr(f"{cube}.scaleY", 2.5)     # Unfrozen & Non-uniform
    save_scene("03_BAD_SCALE")

    # ---------------------------------------------------------
    # 06. BAD UV (OVERLAPPING)
    # ---------------------------------------------------------
    cmds.file(new=True, force=True)
    cube = cmds.polyCube(name="Overlap_UV_Cube")[0]
    # Force overlapping UVs by mapping all faces to same UV space
    cmds.polyProjection(f"{cube}.f[*]", type="Planar")
    save_scene("08_OVERLAPPING_UV")

    # ---------------------------------------------------------
    # 07. MISSING UV
    # ---------------------------------------------------------
    cmds.file(new=True, force=True)
    cube = cmds.polyCube(name="Missing_UV_Cube", createUVs=0)[0]
    # Maya won't allow deleting 'map1', but createUVs=0 ensures it has 0 UV coordinates.
    save_scene("07_MISSING_UV")

    # ---------------------------------------------------------
    # 11. NGONS
    # ---------------------------------------------------------
    cmds.file(new=True, force=True)
    cmds.polyCylinder(name="Ngon_Cylinder", subdivisionsCaps=0)[0] # Caps are n-gons
    save_scene("11_NGONS")

    # ---------------------------------------------------------
    # 12. NON-MANIFOLD
    # ---------------------------------------------------------
    cmds.file(new=True, force=True)
    cube1 = cmds.polyCube(name="NM_Cube1")[0]
    cube2 = cmds.polyCube(name="NM_Cube2")[0]
    cmds.setAttr(f"{cube2}.translateX", 1.0)
    cmds.setAttr(f"{cube2}.translateY", 1.0)
    cmds.polyUnite(cube1, cube2, name="NonManifold_Mesh")
    cmds.polyMergeVertex("NonManifold_Mesh", distance=0.1) # Create bow-tie non-manifold
    save_scene("12_NON_MANIFOLD")
    
    # ---------------------------------------------------------
    # 16. CONSTRUCTION HISTORY
    # ---------------------------------------------------------
    cmds.file(new=True, force=True)
    cube = cmds.polyCube(name="History_Cube")[0]
    cmds.polyBevel(cube, offset=0.1) # Leaves polyBevel node in history
    save_scene("16_CONSTRUCTION_HISTORY")

    # ---------------------------------------------------------
    # 25. MULTI-FAILURE ASSET
    # ---------------------------------------------------------
    cmds.file(new=True, force=True)
    bad_mesh = cmds.polyCylinder(name="Total_Disaster_Mesh", subdivisionsCaps=0, createUVs=0)[0] # N-gons + Missing UVs
    cmds.setAttr(f"{bad_mesh}.translateX", 3.14) # Unfrozen
    cmds.setAttr(f"{bad_mesh}.scaleZ", -1.0)     # Negative Scale
    cmds.polyBevel(bad_mesh, offset=0.2)         # History
    save_scene("25_MULTI_FAILURE_ASSET")

    print(f"\\nSUCCESS: Golden scenes generated in {output_dir}")

if __name__ == "__main__":
    out = r"i:\QYNTARA AI\test_scenes\golden_oracles"
    generate_golden_scenes(os.path.abspath(out))
