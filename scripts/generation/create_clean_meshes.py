import maya.cmds as cmds

def setup_clean_meshes():
    """
    Creates a scene with 'Clean' meshes that should PASS Qyntara AI validation.
    Satisfies: Geometry, Transforms, UVs, Materials, Naming, and Hierarchy rules.
    """
    print("--- Generating Clean Mesh Dataset ---")
    cmds.file(new=True, force=True)
    
    clean_objects = []

    # 1. Setup Environment (Scene Rules)
    cmds.currentUnit(linear='cm')
    cmds.upAxis(axis='y')

    # 2. Create Common Material (Avoid mat_default error)
    if not cmds.objExists("M_Clean_Mat"):
        shader = cmds.shadingNode("standardSurface", asShader=True, name="M_Clean_Mat")
        sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="M_Clean_MatSG")
        cmds.connectAttr(f"{shader}.outColor", f"{sg}.surfaceShader")
    else:
        sg = "M_Clean_MatSG"

    # --- Mesh 1: Clean Cube ---
    # Purpose: Basic Geometry Check
    p1 = cmds.polyCube(name="temp_cube", w=2, h=2, d=2)[0]
    # Naming Convention: GEO_Name_GEO
    p1 = cmds.rename(p1, "GEO_CleanCube_GEO")
    
    # Position (Move then Freeze)
    cmds.move(0, 1, 0, p1) # Sitting on grid
    cmds.makeIdentity(p1, apply=True, t=1, r=1, s=1, n=0, pn=1) # Freeze Transforms
    
    # Material
    cmds.sets(p1, forceElement=sg)
    
    # History
    cmds.delete(p1, ch=True)
    
    clean_objects.append(p1)

    # --- Mesh 2: Clean Sphere (UV Check) ---
    # Purpose: UVs and Smooth Geometry
    p2 = cmds.polySphere(name="temp_sphere", r=1.5, sx=20, sy=20)[0]
    p2 = cmds.rename(p2, "GEO_CleanSphere_GEO")
    
    cmds.move(5, 1.5, 0, p2)
    cmds.makeIdentity(p2, apply=True, t=1, r=1, s=1, n=0, pn=1)
    
    # Ensure UVs are good (Primitives usually match, but ensure range 0-1)
    # layout UVs to be safe
    # cmds.u3dLayout(p2) # u3dLayout might not be loaded. Use polyAutoProjection or simplified layout
    # Sphere UVs are usually 0-1.
    
    cmds.sets(p2, forceElement=sg)
    cmds.delete(p2, ch=True)
    clean_objects.append(p2)

    # --- Mesh 3: Clean Cylinder (Hard/Soft Edge Check) ---
    # Purpose: Normals
    p3 = cmds.polyCylinder(name="temp_cyl", r=1, h=3)[0]
    p3 = cmds.rename(p3, "GEO_CleanCylinder_GEO")
    
    cmds.move(10, 1.5, 0, p3)
    
    # Soften Edges (Angle 30 is standard)
    cmds.polySoftEdge(p3, angle=30, ch=False)
    
    cmds.makeIdentity(p3, apply=True, t=1, r=1, s=1, n=0, pn=1)
    cmds.sets(p3, forceElement=sg)
    cmds.delete(p3, ch=True)
    clean_objects.append(p3)

    # --- Mesh 4: Complex Torus (Polycount/Topology) ---
    p4 = cmds.polyTorus(name="temp_torus", r=1, sr=0.3)[0]
    p4 = cmds.rename(p4, "GEO_CleanTorus_GEO")
    
    cmds.move(15, 0.5, 0, p4)
    cmds.makeIdentity(p4, apply=True, t=1, r=1, s=1, n=0, pn=1)
    cmds.sets(p4, forceElement=sg)
    cmds.delete(p4, ch=True)
    clean_objects.append(p4)

    # 3. Hierarchy Check
    # All objects must be under a root or logical group
    # Not just world children
    root_grp = cmds.group(em=True, name="World_Grp")
    cmds.parent(clean_objects, root_grp)

    # Select all for viewing
    cmds.select(clean_objects)
    print(f"Created {len(clean_objects)} VALID/CLEAN meshes.")
    return clean_objects

if __name__ == "__main__":
    setup_clean_meshes()
