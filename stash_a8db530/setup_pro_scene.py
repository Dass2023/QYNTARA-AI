
"""
Qyntara AI - Professional Demo Asset Generator
Creates a 'DRONE-X1 Motor Housing' with complex topology to showcase Validation Features.
Usage:
    import setup_pro_scene
    setup_pro_scene.create_drone_asset()
"""
import maya.cmds as cmds

def create_drone_asset():
    print("--- Generating Professional Demo Asset (Drone Housing) ---")
    
    cmds.file(new=True, force=True)
    
    # 1. Base Housing (Cylinder)
    base = cmds.polyCylinder(r=2, h=1, sx=12, n="Motor_Base")[0]
    cmds.rotate(90, 0, 0, base)
    
    # 2. Main Arm (Cube)
    arm = cmds.polyCube(w=1, h=6, d=1, sx=1, sy=4, n="Arm_Shaft")[0]
    cmds.move(0, 3, 0, arm)
    
    # 3. Boolean Union (Generates N-Gons at intersection)
    # This creates perfect 'test data' for the validator
    result = cmds.polyCBoolOp(base, arm, op=1, n="DRONE-X1_Housing")[0]
    cmds.delete(base, arm) # Cleanup
    
    # 4. Detail Cuts (Boolean Difference)
    cutter = cmds.polyCylinder(r=0.5, h=2, n="Bolt_Hole_Cutter")[0]
    cmds.rotate(90, 0, 0, cutter)
    cmds.move(0, 5, 0, cutter)
    
    final_geo = cmds.polyCBoolOp(result, cutter, op=2, n="DRONE-X1_Housing_Final")[0]
    cmds.delete(cutter)
    
    # 5. Create Intentional Laminas (Overlapping Faces)
    # Duplicate face in place
    cmds.select(final_geo + ".f[0]") # Top face
    dupe = cmds.duplicate(final_geo, n="ERROR_Layer")[0]
    cmds.parent(dupe, final_geo)
    # Actually just duplicate faces
    # Hard to script reliably without specific IDs. 
    # Just selecting a face and extruding with 0 distance creates lamina/non-manifold?
    cmds.polyExtrudeFacet(final_geo + ".f[0]", ltz=0) 
    
    # 6. Assign Material (Sci-Fi Look)
    shd = cmds.shadingNode("blinn", asShader=True, n="Cyber_Alloy")
    cmds.setAttr(shd + ".color", 0.1, 0.15, 0.2, type="double3") # Dark Blue Grey
    cmds.setAttr(shd + ".specularColor", 0.8, 0.9, 1.0, type="double3")
    cmds.setAttr(shd + ".eccentricity", 0.1)
    
    cmds.select(final_geo)
    cmds.hyperShade(assign=shd)
    
    # 7. Rename to Standard Asset ID
    if cmds.objExists("ASSET-8842-X"): cmds.delete("ASSET-8842-X")
    cmds.rename(final_geo, "ASSET-8842-X")

    cmds.viewFit(all=True)
    print("Asset Created: ASSET-8842-X (High-Tech Drone Part)")
    print("Status: CONTAINS VALIDATION ERRORS (Perfect for Demo)")

if __name__ == "__main__":
    create_drone_asset()
