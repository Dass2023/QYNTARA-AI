import maya.cmds as cmds
import random

def setup_error_dataset(count=5):
    """
    Creates a large dataset of error-prone meshes for bulk testing.
    'count' determines how many of EACH error type to generate.
    """
    print(f"--- Generating Error Dataset (Count={count}) ---")
    cmds.file(new=True, force=True)
    
    generated_objects = []
    
    # Grid spacing
    SPACING_X = 5
    SPACING_Z = 5
    
    # 1. Open Edges
    print("Generating Open Edges...")
    for i in range(count):
        name = f"ERR_OpenEdges_{i+1}"
        obj = cmds.polyCylinder(name=name, sx=8, sy=1, sz=1)[0]
        cmds.delete(f"{obj}.f[8:15]") # Cap
        cmds.move(i * SPACING_X, 0, 0 * SPACING_Z, obj)
        generated_objects.append(obj)

    # 2. Non-Manifold
    print("Generating Non-Manifold...")
    for i in range(count):
        name = f"ERR_NonManifold_{i+1}"
        obj = cmds.polyCube(name=name, w=2, h=2, d=2)[0]
        # Extrude edge to create N-gon/Non-Manifold
        cmds.polyExtrudeEdge(f"{obj}.e[1]", ltz=1)
        cmds.move(i * SPACING_X, 0, 1 * SPACING_Z, obj)
        generated_objects.append(obj)

    # 3. Lamina Faces
    print("Generating Lamina Faces...")
    for i in range(count):
        name = f"ERR_Lamina_{i+1}"
        # Overlapping faces
        p1 = cmds.polyPlane(name=f"{name}_A", sx=1, sy=1)[0]
        p2 = cmds.polyPlane(name=f"{name}_B", sx=1, sy=1)[0]
        # Same position
        obj = cmds.polyUnite(p1, p2, ch=False, name=name)[0]
        cmds.polyMergeVertex(obj, d=0.01) # Merge verts -> 2 faces sharing 4 edges
        cmds.move(i * SPACING_X, 0, 2 * SPACING_Z, obj)
        generated_objects.append(obj)

    # 4. Zero Area Faces
    print("Generating Zero Area Faces...")
    for i in range(count):
        name = f"ERR_ZeroArea_{i+1}"
        obj = cmds.polyPlane(name=name, sx=1, sy=1)[0]
        pos = cmds.pointPosition(f"{obj}.vtx[1]")
        cmds.move(pos[0], pos[1], pos[2], f"{obj}.vtx[3]", ws=True)
        cmds.move(i * SPACING_X, 0, 3 * SPACING_Z, obj)
        generated_objects.append(obj)
        
    # 5. Unfrozen Transforms
    print("Generating Unfrozen Transforms...")
    for i in range(count):
        name = f"ERR_Transform_{i+1}"
        obj = cmds.polyCube(name=name)[0]
        cmds.move(i * SPACING_X, 0, 4 * SPACING_Z, obj)
        
        # Apply random bad transforms
        cmds.setAttr(f"{obj}.rx", random.uniform(1, 10))
        cmds.setAttr(f"{obj}.sy", 2.0)
        # Add translation offset not in history (just current pos)
        # Note: Move command moves pivot, but 'Frozen' check sees Translate != 0 if pivot is at origin?
        # Typically props should be frozen at 0,0,0 or just checked for Rot/Scale.
        # Our updated rule checks Translation too.
        # But for 'scene arrangement', translation is allowed.
        # Frozen check usually implies "Is this a prop that should be 0,0,0 relative to parent?"
        pass 
        generated_objects.append(obj)

    # 6. N-Gons
    print("Generating N-Gons...")
    for i in range(count):
        name = f"ERR_NGon_{i+1}"
        obj = cmds.polyPlane(name=name, sx=2, sy=1)[0]
        cmds.delete(f"{obj}.e[4]")
        cmds.move(i * SPACING_X, 0, 5 * SPACING_Z, obj)
        generated_objects.append(obj)

    # Group
    grp = cmds.group(generated_objects, name="Bulk_Error_Dataset_Grp")
    cmds.select(generated_objects)
    
    total = len(generated_objects)
    print(f"DONE: Generated {total} meshes ({count} per category).")
    return generated_objects

if __name__ == "__main__":
    setup_error_dataset(5)
