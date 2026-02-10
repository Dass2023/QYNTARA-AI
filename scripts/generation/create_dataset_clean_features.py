import maya.cmds as cmds
import random

def setup_clean_feature_dataset(count=5):
    """
    Creates a dataset of CLEAN meshes that specifically pass the Qyntara Validation categories.
    Each row corresponds to a specific validation category (Geometry, Transforms, UVs, etc.).
    """
    print(f"--- Generating Clean Feature Dataset (Count={count}) ---")
    cmds.file(new=True, force=True)
    
    # Setup Scene Global Rules
    cmds.currentUnit(linear='cm')
    cmds.upAxis(axis='y')
    
    generated_objects = []
    
    # Grid Spacing
    SPACING_X = 6
    SPACING_Z = 8

    # ---------------------------------------------------------
    # 1. GEOMETRY INTEGRITY (Clean, Watertight, Quads)
    # ---------------------------------------------------------
    print("Generating Clean Geometry...")
    for i in range(count):
        # Create a nice quad-based sphere or cylinder
        name = f"GEO_CleanGeo_{i+1:02d}_GEO"
        obj = cmds.polyCylinder(name=name, sx=12, sy=1, sz=1)[0]
        
        # Ensure it has history deleted
        cmds.delete(obj, ch=True)
        # Soften Edges (Passes Hard Edges check)
        cmds.polySoftEdge(obj, angle=30, ch=False)
        # Position
        cmds.move(i * SPACING_X, 2, 0 * SPACING_Z, obj)
        
        # Apply freezing
        cmds.makeIdentity(obj, apply=True, t=1, r=1, s=1, n=0, pn=1)
        
        generated_objects.append(obj)

    # ---------------------------------------------------------
    # 2. TRANSFORMS (Frozen, Pivot Center)
    # ---------------------------------------------------------
    print("Generating Clean Transforms...")
    for i in range(count):
        name = f"GEO_CleanXform_{i+1:02d}_GEO"
        obj = cmds.polyCube(name=name, w=2, h=2, d=2)[0]
        
        # Move it to a position
        # NOTE: For "Frozen Transforms", Translation might be allowed depending on the rule,
        # but Rotation and Scale must be Clean.
        # If strict "Zero Translation" is enforced (as per recent update), we must freeze it at origin
        # OR freeze it in place (so trans becomes 0 relative to parent?). 
        # Actually freezing in place makes Trans=0 but vertices move.
        
        # Let's freeze it.
        cmds.move(i * SPACING_X, 1, 1 * SPACING_Z, obj)
        cmds.makeIdentity(obj, apply=True, t=1, r=1, s=1, n=0, pn=1)
        
        # Pivot is at origin because we froze it.
        # Check Pivot Center rule? 
        # If object is at 10,0,0 and we freeze it -> Pivot is at 0,0,0.
        # Validation checks if Object Pivot is at World Origin?
        # Yes, check_pivot_center checks (rp distance to 0,0,0).
        
        generated_objects.append(obj)

    # ---------------------------------------------------------
    # 3. UVS (Unwrapped, No Overlap, 0-1)
    # ---------------------------------------------------------
    print("Generating Clean UVs...")
    for i in range(count):
        name = f"GEO_CleanUV_{i+1:02d}_GEO"
        # Torus usually has good UVs by default
        obj = cmds.polyTorus(name=name, r=1, sr=0.5)[0]
        
        # Move & Freeze
        cmds.move(i * SPACING_X, 1, 2 * SPACING_Z, obj)
        cmds.makeIdentity(obj, apply=True, t=1, r=1, s=1, n=0, pn=1)
        
        # Force a clean Map 1
        # Automatic Mapping usually ensures no overlap and 0-1 range
        cmds.polyAutoProjection(obj, lm=0, pb=0, ibd=1, cm=0, l=2, sc=1, o=1, p=6, ps=0.2, ws=0)
        
        # Add Lightmap UVs (Set 2) - Passes "Lightmap UVs" check
        cmds.polyUVSet(obj, create=True, uvSet='lightmap')
        cmds.polyUVSet(obj, currentUVSet=True, uvSet='lightmap')
        cmds.polyAutoProjection(obj, lm=0, pb=0, ibd=1, cm=0, l=2, sc=1, o=1, p=6, ps=0.2, ws=0)
        cmds.polyUVSet(obj, currentUVSet=True, uvSet='map1') # Switch back to default
        
        cmds.delete(obj, ch=True)
        generated_objects.append(obj)

    # ---------------------------------------------------------
    # 4. MATERIALS (Correct Naming, No Default)
    # ---------------------------------------------------------
    print("Generating Clean Materials...")
    for i in range(count):
        name = f"GEO_CleanMat_{i+1:02d}_GEO"
        obj = cmds.polySphere(name=name)[0]
        
        # Move & Freeze
        cmds.move(i * SPACING_X, 1, 3 * SPACING_Z, obj)
        cmds.makeIdentity(obj, apply=True, t=1, r=1, s=1, n=0, pn=1)
        
        # Create unique material
        mat_name = f"M_PropMaterial_{i+1:02d}"
        if not cmds.objExists(mat_name):
            shd = cmds.shadingNode("standardSurface", asShader=True, name=mat_name)
            sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=f"{mat_name}SG")
            cmds.connectAttr(f"{shd}.outColor", f"{sg}.surfaceShader")
        else:
            sg = f"{mat_name}SG"
            
        cmds.sets(obj, forceElement=sg)
        
        # Vertex Colors (Passes Vertex Color check)
        cmds.polyColorPerVertex(obj, r=1, g=1, b=1, a=1, cdo=True)
        
        cmds.delete(obj, ch=True)
        generated_objects.append(obj)

    # ---------------------------------------------------------
    # 5. NAMING & HIERARCHY
    # ---------------------------------------------------------
    print("Generating Clean Hierarchy...")
    # These must be grouped
    hierarchy_objects = []
    for i in range(count):
        # Complex Name that follows convention
        name = f"PROPS_SpecialItem_{i+1:03d}_GEO"
        obj = cmds.polyCone(name=name)[0]
        
        cmds.move(i * SPACING_X, 1, 4 * SPACING_Z, obj)
        cmds.makeIdentity(obj, apply=True, t=1, r=1, s=1, n=0, pn=1)
        hierarchy_objects.append(obj)
        generated_objects.append(obj)
        
    # Group them
    cmds.group(hierarchy_objects, name="World_Grp")
    
    # Parent other categories too?
    # Ideally yes, to pass "Scene Hierarchy" check which requires single root.
    # Let's parent EVERYTHING created so far under World_Grp
    # Find objects that aren't already in World_Grp
    remaining = [o for o in generated_objects if o not in hierarchy_objects]
    if remaining:
        cmds.parent(remaining, "World_Grp")

    cmds.select(generated_objects)
    print(f"DONE: Generated {len(generated_objects)} VALID meshes.")
    return generated_objects

if __name__ == "__main__":
    setup_clean_feature_dataset(5)
