
import maya.cmds as cmds
import sys
import os

# Add local path to import qyntara_ai
sys.path.append(os.getcwd())

try:
    from qyntara_ai.core import geometry
except ImportError:
    print("Could not import qyntara_ai.core.geometry")
    sys.exit(1)

def setup_scene():
    cmds.file(new=True, force=True)
    
    # 1. Zero Area Face Case
    # Create a plane, scale one face to 0
    cube = cmds.polyCube(n="ZeroAreaTest")[0]
    cmds.scale(0, 0, 0, f"{cube}.f[0]") # Make face 0 zero area
    
    # 2. Zero Length Edge Case
    # Create a plane, merge two verts
    plane = cmds.polyPlane(n="ZeroLengthTest", sx=1, sy=1)[0]
    # Merge vtx 1 and 2
    cmds.select(f"{plane}.vtx[1]", f"{plane}.vtx[2]")
    cmds.polyMergeVertex(d=0.1) # This creates a zero length edge effectively or removes it?
    # Actually polyMergeVertex REMOVES the edge. 
    # To have a zero length edge we need to position them on top of each other but NOT merge.
    
    plane2 = cmds.polyPlane(n="ZeroLengthTest2", sx=1, sy=1)[0]
    pos = cmds.xform(f"{plane2}.vtx[1]", q=True, ws=True, t=True)
    cmds.move(pos[0], pos[1], pos[2], f"{plane2}.vtx[2]", ws=True) # Move vtx2 to vtx1
    
    return cube, plane2

def test_rules():
    cube, plane = setup_scene()
    
    print("\n--- Testing Zero Area Faces ---")
    res_area = geometry.check_zero_area_faces([cube])
    if res_area:
        print(f"PASS: Detected {len(res_area[0]['components'])} zero area faces on {cube}")
        print(res_area)
    else:
        print(f"FAIL: Did NOT detect zero area faces on {cube}")

    print("\n--- Testing Zero Length Edges ---")
    res_length = geometry.check_zero_length_edges([plane])
    if res_length:
        print(f"PASS: Detected {len(res_length[0]['components'])} zero length edges on {plane}")
        print(res_length)
    else:
        print(f"FAIL: Did NOT detect zero length edges on {plane}")

if __name__ == "__main__":
    try:
        test_rules()
    except Exception as e:
        print(f"ERROR: {e}")
