import maya.cmds as cmds
import math

def setup_error_meshes():
    """Creates a scene with EVERY supported error type for testing Qyntara AI validation."""
    print("--- Generating Error Mesh Dataset ---")
    cmds.file(new=True, force=True)
    
    generated_objects = []

    # 1. Open Edges (Border)
    # Cylinder with deleted cap (Open border loop)
    # Position: 0,0,0
    p1 = cmds.polyCylinder(name="ERR_OpenEdges", sx=8, sy=1, sz=1)[0]
    cmds.delete(f"{p1}.f[8:15]") # Delete top cap
    cmds.move(0, 0, 0, p1)
    generated_objects.append(p1)

    # 2. Non-Manifold Geometry
    # Extrude edge of a CUBE to create internal face/non-manifold edge
    # Position: 5,0,0
    p2 = cmds.polyCube(name="ERR_NonManifold", w=2, h=2, d=2)[0]
    cmds.move(5, 0, 0, p2)
    # Extrude an edge inward/overlapping
    # Or cleaner non-manifold: A T-junction face
    # Create a plane and extrude an edge from its center?
    # Simpler: Cube with an internal face.
    p2_b = cmds.polyPlane(w=2, h=2, sx=1, sy=1)[0]
    cmds.move(5, 0, 0, p2_b)
    # Extrude edge
    cmds.polyExtrudeEdge(f"{p2_b}.e[1]", ltz=1, ls=(1, 0, 0)) # Create a fin
    # Combine with cube? 
    # Let's stick to the previous reliable method:
    cmds.delete(p2_b)
    cmds.polyExtrudeEdge(f"{p2}.e[1]", ltz=1) # Create fin sticking out
    generated_objects.append(p2)
    
    # 3. Lamina Faces
    # Two faces sharing all edges on top of each other.
    # Position: 10,0,0
    p3 = cmds.polyCube(name="ERR_Lamina", sx=1, sy=1, sz=1)[0]
    extra = cmds.polyPlane(sx=1, sy=1)[0]
    cmds.move(0, 0, 0.5, extra) # Position exactly on front face of cube
    p3 = cmds.polyUnite(p3, extra, ch=False, name="ERR_Lamina")[0]
    cmds.polyMergeVertex(p3, d=0.01) # Merge vertices -> Lamina Face created
    cmds.move(10, 0, 0, p3)
    generated_objects.append(p3)
    
    # 4. Zero Area Face
    # Create triangle, merge 2 verts to collapse it into a line
    # Position: 15,0,0
    p4 = cmds.polyPlane(name="ERR_ZeroArea", sx=1, sy=1)[0]
    cmds.move(15, 0, 0, p4)
    # Collapse vertex 1 to vertex 3
    pos = cmds.pointPosition(f"{p4}.vtx[1]")
    cmds.move(pos[0], pos[1], pos[2], f"{p4}.vtx[3]", ws=True)
    # Don't merge, just keep them coincident = zero area face
    # If merged, it becomes zero length edge?
    generated_objects.append(p4)

    # 5. Locked Normals / Hard Edges
    # Cube with all hard edges + Locked Normals
    # Position: 20,0,0
    p5 = cmds.polyCube(name="ERR_LockedNormals")[0]
    cmds.polySoftEdge(p5, angle=0) # Hard edges
    cmds.polyNormalPerVertex(p5, freezeNormal=True) # Lock them
    cmds.move(20, 0, 0, p5)
    generated_objects.append(p5)

    # 6. Unfrozen Transform & Scale
    # Position: 25,0,0
    p6 = cmds.polyCube(name="ERR_Transform")[0]
    cmds.move(25, 0, 0, p6)
    cmds.setAttr(f"{p6}.tx", 25.5) # Non-Integer translation (Grid Snap issue?)
    cmds.setAttr(f"{p6}.ry", 45)   # Rotation
    cmds.setAttr(f"{p6}.sz", 2.0)  # Scale
    generated_objects.append(p6)

    # 7. No Materials / Default Material
    # Just a cube
    # Position: 30,0,0
    p7 = cmds.polyCube(name="ERR_Material")[0]
    cmds.move(30, 0, 0, p7)
    generated_objects.append(p7)

    # 8. Negative Scale
    # Position: 35,0,0
    p8 = cmds.polyCone(name="ERR_NegScale")[0]
    cmds.move(35, 0, 0, p8)
    cmds.setAttr(f"{p8}.sx", -1)
    generated_objects.append(p8)

    # 9. N-Gons
    # Plane with an edge removed
    # Position: 40,0,0
    p9 = cmds.polyPlane(name="ERR_NGon", sx=2, sy=1)[0] # 2 faces
    cmds.delete(f"{p9}.e[4]") # Delete middle edge -> 1 face with 6 verts
    cmds.move(40, 0, 0, p9)
    generated_objects.append(p9)
    
    # 10. UV Issues (Overlapping)
    # Position: 45,0,0
    p10 = cmds.polySphere(name="ERR_UVOverlap")[0]
    cmds.move(45, 0, 0, p10)
    # Synthetically smash UVs
    cmds.polyEditUV(f"{p10}.map[:]", scaleU=0, scaleV=0, pivotU=0.5, pivotV=0.5) 
    generated_objects.append(p10)

    # Group properly to avoid hierarchy error
    grp = cmds.group(generated_objects, name="Test_Meshes_Grp")

    cmds.select(generated_objects)
    print(f"Created {len(generated_objects)} error meshes.")
    return generated_objects

if __name__ == "__main__":
    setup_error_meshes()
