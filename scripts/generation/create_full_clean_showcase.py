import maya.cmds as cmds

def setup_full_clean_showcase():
    """
    Creates a SINGLE representative CLEAN mesh for each major validation category.
    This demonstrates the 'Ideal State' that Qyntara AI expects.
    """
    print("--- Generating Full Clean Showcase (Ideal Assets) ---")
    cmds.file(new=True, force=True)
    
    # 1. Setup Scene Rules (Environment)
    # Correct Units (cm) and Up-Axis (Y)
    cmds.currentUnit(linear='cm')
    cmds.upAxis(axis='y')

    showcase_objects = []
    
    # Layout configuration
    X_START = 0
    X_GAP = 10
    cursor_x = X_START

    def add_object(obj):
        """Helper to position object and move cursor."""
        nonlocal cursor_x
        # Move object to cursor
        cmds.move(cursor_x, 2, 0, obj)
        # FREEZE it immediately (Clean Transform is baseline requirement)
        cmds.makeIdentity(obj, apply=True, t=1, r=1, s=1, n=0, pn=1)
        
        showcase_objects.append(obj)
        cursor_x += X_GAP
        return obj

    # Shared Resources
    # Create a Valid Material
    mat_name = "M_StandardProp_Mat"
    if not cmds.objExists(mat_name):
        shd = cmds.shadingNode("standardSurface", asShader=True, name=mat_name)
        sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=f"{mat_name}SG")
        cmds.connectAttr(f"{shd}.outColor", f"{sg}.surfaceShader")
    else:
        sg = f"{mat_name}SG"

    # =========================================================================
    # 1. IDEAL GEOMETRY (Quad-based, Watertight, Soft Edges)
    # =========================================================================
    # A sphere is a good example of clean quads and convexity.
    p1 = cmds.polySphere(name="temp_geo", r=2, sx=16, sy=16)[0]
    p1 = cmds.rename(p1, "GEO_IdealGeometry_GEO")
    
    # Soften Edges (Standard 30 degrees)
    cmds.polySoftEdge(p1, angle=30, ch=False)
    # Delete History
    cmds.delete(p1, ch=True)
    # Assign Material
    cmds.sets(p1, forceElement=sg)
    
    add_object(p1)


    # =========================================================================
    # 2. IDEAL TRANSFORMS (Frozen, Pivot Center)
    # =========================================================================
    # A cube representing a structural prop.
    p2 = cmds.polyCube(name="temp_xform", w=3, h=3, d=3)[0]
    p2 = cmds.rename(p2, "GEO_IdealTransform_GEO")
    
    # Transforms are handled by add_object (Freeze)
    # Ensure Pivot is centered on object (which is at origin relative to freeze)
    cmds.xform(p2, cp=True)
    
    cmds.sets(p2, forceElement=sg)
    add_object(p2)


    # =========================================================================
    # 3. IDEAL UVS (Packed, No Overlap, 0-1 Range, Lightmap Set)
    # =========================================================================
    # A Torus is complex enough to require unwrapping.
    p3 = cmds.polyTorus(name="temp_uv", r=1.5, sr=0.5)[0]
    p3 = cmds.rename(p3, "GEO_IdealUVs_GEO")
    
    # Channel 1: Diffuse UVs
    cmds.polyAutoProjection(p3, lm=0, pb=0, ibd=1, cm=0, l=2, sc=1, o=1, p=6, ps=0.2, ws=0)
    
    # Channel 2: Lightmap UVs (Required for Game Engines)
    cmds.polyUVSet(p3, create=True, uvSet='lightmap')
    cmds.polyUVSet(p3, currentUVSet=True, uvSet='lightmap')
    cmds.polyAutoProjection(p3, lm=0, pb=0, ibd=1, cm=0, l=2, sc=1, o=1, p=6, ps=0.2, ws=0)
    cmds.polyUVSet(p3, currentUVSet=True, uvSet='map1') # Reset
    
    cmds.delete(p3, ch=True)
    cmds.sets(p3, forceElement=sg)
    add_object(p3)


    # =========================================================================
    # 4. IDEAL VERTEX DATA (Vertex Colors, Tangents)
    # =========================================================================
    # A Cone showing vertex painting
    p4 = cmds.polyCone(name="temp_vtx", r=1.5, h=3)[0]
    p4 = cmds.rename(p4, "GEO_IdealVertexData_GEO")
    
    # Apply White Vertex Color (Standard init)
    cmds.polyColorPerVertex(p4, r=1, g=1, b=1, a=1, cdo=True)
    
    cmds.sets(p4, forceElement=sg)
    add_object(p4)
    
    
    # =========================================================================
    # 5. IDEAL NAMING & HIERARCHY
    # =========================================================================
    # Group construction
    # Object name: CATEGORY_Description_SUFFIX
    p5 = cmds.polyCylinder(name="temp_hierarchy", r=1, h=4)[0]
    p5 = cmds.rename(p5, "PROPS_PillarAsset_GEO")
    
    cmds.sets(p5, forceElement=sg)
    add_object(p5)


    # 6. Final Hierarchy Grouping
    # All assets should be under a logical root group, not world
    root_grp = cmds.group(showcase_objects, name="Asset_Collection_Grp")
    
    # center view
    cmds.select(showcase_objects)
    print(f"DONE: Generated {len(showcase_objects)} representative CLEAN meshes.")
    return showcase_objects

if __name__ == "__main__":
    setup_full_clean_showcase()
