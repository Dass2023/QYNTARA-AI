
"""
Qyntara AI - Demo Scene Setup
Creates test assets to verify:
1. Digital Twin Linking (ASSET-8842-X)
2. Validation & Auto-Fix (Bad Geometry)
"""

try:
    import maya.cmds as cmds
except ImportError:
    print("Error: Maya commands not found. Run inside Maya.")
    exit()

def setup_demo():
    print("--- Setting up Qyntara Demo Scene ---")
    
    # 1. create Twin Asset
    twin_name = "ASSET-8842-X"
    if not cmds.objExists(twin_name):
        # Create a simple "Machine"
        base = cmds.polyCube(n=twin_name, w=5, h=2, d=5)[0]
        top = cmds.polyCylinder(n=twin_name + "_Top", r=1, h=2)[0]
        cmds.move(0, 2, 0, top)
        cmds.parent(top, base)
        
        # Add a custom attribute for validation testing
        cmds.addAttr(base, ln="QyntaraID", dt="string")
        cmds.setAttr(base + ".QyntaraID", "TWIN-LINK-ACTIVE", type="string")
        
        print(f"[OK] Created Digital Twin Target: {twin_name}")
    else:
        print(f"[skip] {twin_name} already exists.")

    # 2. Create Bad Geometry (Validation Target)
    bad_geo = "Bad_Geometry_Cube"
    if not cmds.objExists(bad_geo):
        cube = cmds.polyCube(n=bad_geo, w=3, h=3, d=3)[0]
        cmds.move(8, 1.5, 0, cube)
        
        # Create an N-Gon (Delete edge)
        # Assuming default topology: face 1 is front
        # Delete edge between f[1] and f[3]? Maya indexing varies.
        # Just delete random edge to make ngon
        cmds.delete(cube + ".e[1]") 
        
        # Create Open Edge (Delete face)
        cmds.delete(cube + ".f[4]")
        
        print(f"[OK] Created Invalid Geometry: {bad_geo} (Contains N-Gons & Open Edges)")
    else:
        print(f"[skip] {bad_geo} already exists.")

    # 3. Create Scene Hierarchy Mess (For Hierarchy Check)
    grp1 = cmds.group(em=True, n="Empty_Group_01")
    grp2 = cmds.group(em=True, n="Empty_Group_02")
    cmds.parent(grp2, grp1)
    print(f"[OK] Created Empty Groups (Hierarchy Check Target)")

    # Select Everything
    cmds.select(twin_name, bad_geo, grp1)
    
    print("\n--- Demo Scene Ready ---")
    print("1. Open Qyntara UI")
    print("2. 'Industry 4.0' Tab -> Connect Live Stream (Should verify ASSET-8842-X)")
    print("3. 'Validation' Tab -> Validate (Should find N-Gons/Open Edges)")
    print("4. Click 'AUTO-FIX' to repair Bad_Geometry_Cube")

if __name__ == "__main__":
    setup_demo()
