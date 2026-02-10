import maya.cmds as cmds
import random

def create_demo_scene():
    """
    Generates a 3-stage demonstration of the Qyntara Lifecycle:
    1. Raw Input (Before)
    2. Validated & IoT Linked (Industry 4.0)
    3. Evolved/Aged (Industry 5.0)
    """
    
    # 0. Cleanup
    if cmds.objExists("Qyntara_Demo_Grp"):
        cmds.delete("Qyntara_Demo_Grp")
    
    main_grp = cmds.group(em=True, n="Qyntara_Demo_Grp")
    
    # --- STAGE 1: RAW INPUT (The "Before") ---
    # Representative of a raw scan or unoptimized sculpt
    # High poly, noisy, bad placement
    raw_transform, raw_shape = cmds.polySphere(n="Raw_Asset_Input", r=10, sx=50, sy=50)
    cmds.move(-25, 0, 0, raw_transform)
    cmds.parent(raw_transform, main_grp)
    
    # Make it look "raw" (random vertex noise)
    vtx_count = cmds.polyEvaluate(raw_transform, v=True)
    for i in range(0, vtx_count, 5): # Scramble every 5th vertex slightly
        x = random.uniform(-0.5, 0.5)
        y = random.uniform(-0.5, 0.5)
        z = random.uniform(-0.5, 0.5)
        cmds.move(x, y, z, f"{raw_transform}.vtx[{i}]", r=True)
    
    # Label
    lbl1 = cmds.textCurves(t="1. RAW INPUT", f="Arial", ch=False)[0]
    cmds.move(-30, 15, 0, lbl1)
    cmds.scale(5, 5, 5, lbl1)
    cmds.parent(lbl1, main_grp)

    # --- STAGE 2: INDUSTRY 4.0 (The "Now") ---
    # Validated, Optimized, IoT Linked
    # Clean topology, specific color, IoT metadata
    valid_transform, _ = cmds.polySphere(n="Smart_Asset_4_0", r=10, sx=20, sy=20)
    cmds.move(0, 0, 0, valid_transform)
    cmds.parent(valid_transform, main_grp)
    
    # Apply "Validated" Material (Green/Cyber)
    shd = cmds.shadingNode("blinn", asShader=True, n="Qyntara_Valid_Mat")
    cmds.setAttr(f"{shd}.color", 0, 1, 0.8, type="double3") # Cyan/Green
    cmds.setAttr(f"{shd}.incandescence", 0, 0.2, 0.2, type="double3")
    sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, n=f"{shd}SG")
    cmds.connectAttr(f"{shd}.outColor", f"{sg}.surfaceShader")
    cmds.sets(valid_transform, forceElement=sg)
    
    # Add IoT Data (Industry 4.0)
    if not cmds.attributeQuery("QyntaraID", n=valid_transform, ex=True):
        cmds.addAttr(valid_transform, longName="QyntaraID", dataType="string")
        cmds.setAttr(f"{valid_transform}.QyntaraID", "ASSET-8842-X", type="string")
    
    if not cmds.attributeQuery("LiveStatus", n=valid_transform, ex=True):
        cmds.addAttr(valid_transform, longName="LiveStatus", dataType="string")
        cmds.setAttr(f"{valid_transform}.LiveStatus", "ONLINE", type="string")

    # Label
    lbl2 = cmds.textCurves(t="2. SMART FACTORY", f="Arial", ch=False)[0]
    cmds.move(-5, 15, 0, lbl2)
    cmds.scale(5, 5, 5, lbl2)
    cmds.parent(lbl2, main_grp)

    # --- STAGE 3: INDUSTRY 5.0 (The "Future") ---
    # Predicted, Evolved, Aged
    # Morphed shape based on "stress", Purple/Evolved color
    future_transform, _ = cmds.polySphere(n="Evolved_Asset_5_0", r=10, sx=20, sy=20)
    cmds.move(25, 0, 0, future_transform)
    cmds.parent(future_transform, main_grp)
    
    # Deform to show "Evolution" (Lattice or soft mod)
    # We'll just scale it anisotropically to show "Optimization"
    cmds.scale(0.8, 1.2, 0.8, future_transform)
    
    # Apply "Future" Material (Toxic Purple)
    shd_fut = cmds.shadingNode("blinn", asShader=True, n="Qyntara_Future_Mat")
    cmds.setAttr(f"{shd_fut}.color", 0.8, 0, 1, type="double3") # Purple
    cmds.setAttr(f"{shd_fut}.transparency", 0.5, 0.5, 0.5, type="double3") # Holographic
    cmds.setAttr(f"{shd_fut}.incandescence", 0.4, 0, 0.5, type="double3")
    sg_fut = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, n=f"{shd_fut}SG")
    cmds.connectAttr(f"{shd_fut}.outColor", f"{sg_fut}.surfaceShader")
    cmds.sets(future_transform, forceElement=sg_fut)

    # Label
    lbl3 = cmds.textCurves(t="3. PREDICTED FUTURE", f="Arial", ch=False)[0]
    cmds.move(20, 15, 0, lbl3)
    cmds.scale(5, 5, 5, lbl3)
    cmds.parent(lbl3, main_grp)
    
    # Select all for framing
    cmds.select(main_grp)
    cmds.viewFit()
    cmds.select(clear=True)
    
    print("[Qyntara] Demo Scene Generated.")
    print("1. Raw: Unoptimized input.")
    print("2. Smart: Validated & IoT Linked.")
    print("3. Future: Predicted evolution.")

if __name__ == "__main__":
    create_demo_scene()
