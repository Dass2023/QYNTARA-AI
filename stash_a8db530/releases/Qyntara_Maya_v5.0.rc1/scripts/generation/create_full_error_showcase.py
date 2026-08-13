import maya.cmds as cmds
import random

def setup_full_error_showcase():
    """
    Creates a SINGLE representative mesh for EVERY validation rule in Qyntara AI.
    Used to visually verify that every rule correctly detects its specific error.
    Layout is linear with sufficient spacing.
    """
    print("--- Generating Full Error Showcase (One of Each) ---")
    cmds.file(new=True, force=True)
    
    # Setup global state to trigger scene errors
    cmds.currentUnit(linear='m') # Wrong unit
    cmds.upAxis(axis='z')        # Wrong axis

    showcase_objects = []
    
    # Layout configuration
    ROW_LENGTH = 5
    SPACING_X = 2.0  # 2 Meters gap
    SPACING_Z = 2.0
    
    # Create Base Material for uniformity
    base_sg = "initialShadingGroup" # Default
    try:
        if not cmds.objExists("M_Base"):
            shd = cmds.shadingNode("standardSurface", asShader=True, name="M_Base")
            cmds.setAttr(f"{shd}.baseColor", 0.5, 0.5, 0.5, type="double3") # Neutral Grey
            base_sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="M_BaseSG")
            cmds.connectAttr(f"{shd}.outColor", f"{base_sg}.surfaceShader")
        else:
            base_sg = "M_BaseSG"
    except: pass

    def add_object(obj, label="", use_base_mat=True):
        """Helper to position object in a grid layout."""
        idx = len(showcase_objects)
        row = idx // ROW_LENGTH
        col = idx % ROW_LENGTH
        
        tx = col * SPACING_X
        tz = row * SPACING_Z
        
        cmds.move(tx, 0, tz, obj, ws=True)
        
        if use_base_mat:
            try: cmds.sets(obj, forceElement=base_sg)
            except: pass
            
        showcase_objects.append(obj)

    # =========================================================================
    # 1. GEOMETRY
    # =========================================================================
    
    # Rule: geo_open_edges
    p = cmds.polyCylinder(name="ERR_OpenEdges", r=0.5, h=1, sx=12)[0]
    cmds.delete(f"{p}.f[12:23]") # Top cap
    add_object(p)

    # Rule: geo_non_manifold
    p = cmds.polyCube(name="ERR_NonManifold", w=1, h=1, d=1)[0]
    # Extrude internal face
    cmds.polyExtrudeEdge(f"{p}.e[1]", ltz=0.2, ls=(0.5, 0.5, 0))
    add_object(p)

    # Rule: geo_lamina_faces
    p = cmds.polyPlane(name="ERR_LaminaBase", w=1, h=1, sx=1, sy=1)[0]
    p2 = cmds.polyPlane(name="ERR_LaminaDup", w=1, h=1, sx=1, sy=1)[0]
    p = cmds.polyUnite(p, p2, ch=False, name="ERR_LaminaFaces")[0]
    cmds.polyMergeVertex(p, d=0.01) 
    add_object(p)

    # Rule: geo_ngons
    p = cmds.polyPlane(name="ERR_NGons", w=1, h=1, sx=2, sy=1)[0]
    cmds.delete(f"{p}.e[4]") 
    add_object(p)

    # Rule: geo_zero_area
    p = cmds.polyPlane(name="ERR_ZeroArea", w=1, h=1, sx=1, sy=1)[0]
    pos = cmds.pointPosition(f"{p}.vtx[1]")
    cmds.move(pos[0], pos[1], pos[2], f"{p}.vtx[3]", ws=True)
    add_object(p)
    
    # Rule: geo_hard_edges
    p = cmds.polySphere(name="ERR_HardEdges", r=0.5, sx=12, sy=12)[0]
    cmds.polySoftEdge(p, angle=0)
    add_object(p)

    # Rule: geo_history (Non-Deformer)
    p = cmds.polyCube(name="ERR_History", w=1, h=1, d=1)[0]
    cmds.polyExtrudeFacet(f"{p}.f[1]", ltz=0.5)
    add_object(p)

    # Rule: render_terminator
    p = cmds.polySphere(name="ERR_Terminator", r=0.5, sx=12, sy=12)[0] # Low poly
    cmds.polySoftEdge(p, angle=180) 
    add_object(p)

    # =========================================================================
    # 2. TRANSFORMS
    # =========================================================================

    # Rule: xform_frozen (Rotation/Translation)
    p = cmds.polyCube(name="ERR_Unfrozen", w=1, h=1, d=1)[0]
    add_object(p) 
    cmds.rotate(0, 45, 0, p)
    cmds.move(0, 0.5, 0, p, r=True)

    # Rule: xform_scale (Non-Unit)
    p = cmds.polyCube(name="ERR_BadScale", w=1, h=1, d=1)[0]
    cmds.scale(1, 2, 1, p)
    add_object(p)

    # Rule: xform_negative_scale
    p = cmds.polyCone(name="ERR_NegScale", r=0.5, h=1)[0]
    cmds.scale(-1, 1, 1, p)
    add_object(p)

    # Rule: check_pivot_center
    p = cmds.polyCube(name="ERR_OffsetPivot", w=1, h=1, d=1)[0]
    add_object(p) # Placed at grid pos
    # Object is at (TX, 0, TZ). Pivot is at (TX, 0, TZ).
    # This triggers error because Pivot != (0,0,0).

    # =========================================================================
    # 3. UVS
    # =========================================================================

    # Rule: uv_missing
    p = cmds.polyCube(name="ERR_NoUVs", w=1, h=1, d=1)[0]
    try: cmds.polyUVSet(p, delete=True, uvSet='map1')
    except: pass
    add_object(p)

    # Rule: uv_overlap
    p = cmds.polySphere(name="ERR_UVOverlap", r=0.5)[0]
    cmds.polyEditUV(f"{p}.map[:]", scaleU=0, scaleV=0)
    add_object(p)

    # Rule: uv_flipped
    p = cmds.polyPlane(name="ERR_UVFlipped", w=1, h=1)[0]
    cmds.polyEditUV(f"{p}.map[:]", scaleU=-1, pivotU=0.5)
    add_object(p)

    # Rule: uv_bounds
    p = cmds.polyPlane(name="ERR_UVBounds", w=1, h=1)[0]
    cmds.polyEditUV(f"{p}.map[:]", u=2.0)
    add_object(p)

    # Rule: uv_lightmap_set
    p = cmds.polyCube(name="ERR_NoLightmap", w=1, h=1, d=1)[0]
    add_object(p)

    # =========================================================================
    # 4. MATERIALS
    # =========================================================================

    # Rule: mat_default
    p = cmds.polyCube(name="ERR_DefaultMat", w=1, h=1, d=1)[0]
    # Explicitly assign Lambert1 to FAIL
    cmds.sets(p, forceElement='initialShadingGroup')
    add_object(p, use_base_mat=False)

    # Rule: mat_missing
    p = cmds.polyCube(name="ERR_MissingMat", w=1, h=1, d=1)[0]
    empty_sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="EmptySG")
    cmds.sets(p, forceElement=empty_sg)
    add_object(p, use_base_mat=False)

    # Rule: mat_naming
    p = cmds.polyCube(name="ERR_MatNaming", w=1, h=1, d=1)[0]
    bad_mat = cmds.shadingNode("blinn", asShader=True, name="WrongNameMaterial")
    bad_sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="WrongNameSG")
    cmds.connectAttr(f"{bad_mat}.outColor", f"{bad_sg}.surfaceShader")
    cmds.sets(p, forceElement=bad_sg)
    add_object(p, use_base_mat=False)

    # =========================================================================
    # 5. NAMING
    # =========================================================================

    # Rule: check_naming_convention
    p = cmds.polyCube(name="bad_naming_convention", w=1, h=1, d=1)[0]
    add_object(p)
    
    # Select all
    cmds.select(showcase_objects)
    
    print(f"DONE: Generated {len(showcase_objects)} standardized error meshes.")
    return showcase_objects

if __name__ == "__main__":
    setup_full_error_showcase()
