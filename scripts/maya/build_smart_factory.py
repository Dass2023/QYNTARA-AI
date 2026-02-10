import maya.cmds as cmds
import math
import random

def build_smart_factory():
    """
    Bio-Digital Twin Architect: "The Future Build"
    Generates a Qyntara Smart Factory Cell (Industry 4.0/5.0 Ready).
    
    Includes:
    1. Smart Floor (Grid detection)
    2. Robotic Arm (Rigged for IK)
    3. Conveyor System (Animated)
    4. IoT Sensors (Metadata injected)
    """
    
    # 0. Initialize Scene
    scene_grp = "Qyntara_Factory_Main"
    if cmds.objExists(scene_grp):
        cmds.delete(scene_grp)
    cmds.group(em=True, n=scene_grp)
    
    print("[Architect] Initializing Smart Factory Protocol...")

    # --- 1. THE SMART FLOOR (Foundation) ---
    floor, _ = cmds.polyPlane(n="Smart_Floor", w=100, h=100, sx=10, sy=10)
    cmds.parent(floor, scene_grp)
    
    # Apply "Grid" Material
    shd_floor = cmds.shadingNode("blinn", asShader=True, n="Mat_Factory_Floor")
    cmds.setAttr(f"{shd_floor}.color", 0.1, 0.1, 0.1, type="double3")
    cmds.setAttr(f"{shd_floor}.reflectivity", 0.3)
    sg_floor = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, n=f"{shd_floor}SG")
    cmds.connectAttr(f"{shd_floor}.outColor", f"{sg_floor}.surfaceShader")
    cmds.sets(floor, forceElement=sg_floor)
    
    # Add Sensors to Floor (IoT)
    cmds.addAttr(floor, ln="MaxLoad_kg", at="double", dv=5000)
    cmds.addAttr(floor, ln="Vibration_Hz", at="double", dv=0.0)

    # --- 2. THE CONVEYOR SYSTEM (Flow) ---
    conveyor_grp = cmds.group(em=True, n="Conveyor_System")
    cmds.parent(conveyor_grp, scene_grp)
    
    belt, _ = cmds.polyCube(n="Conveyor_Belt", w=80, h=1, d=15)
    cmds.move(0, 1, 0, belt)
    cmds.parent(belt, conveyor_grp)
    cmds.setAttr(f"{belt}.translateY", 2)
    
    # Legs
    for x in [-35, 0, 35]:
        leg, _ = cmds.polyCube(n=f"Leg_{x}", w=2, h=4, d=10)
        cmds.move(x, 0, 0, leg)
        cmds.parent(leg, conveyor_grp)

    # --- 3. THE ROBOTIC ARM (The Agent) ---
    arm_grp = cmds.group(em=True, n="Robot_Arm_Base")
    cmds.parent(arm_grp, scene_grp)
    cmds.move(0, 2, 15, arm_grp)
    
    # Base
    base, _ = cmds.polyCylinder(n="Robot_Base", r=4, h=2)
    cmds.parent(base, arm_grp)
    
    # Link 1 (Shoulder)
    link1, _ = cmds.polyCube(n="Link_Shoulder", w=3, h=10, d=3)
    cmds.move(0, 6, 0, link1)
    cmds.parent(link1, base) # Simple hierarchy rig
    
    # Link 2 (Elbow)
    link2, _ = cmds.polyCube(n="Link_Elbow", w=2, h=8, d=2)
    cmds.move(0, 8, 0, link2) # Relative to parent
    cmds.parent(link2, link1)
    
    # End Effector
    claw, _ = cmds.polyCone(n="End_Effector", r=1, h=2)
    cmds.move(0, 5, 0, claw)
    cmds.parent(claw, link2)
    
    # Pose Robot (Forward Kinematics)
    cmds.rotate(0, 45, 0, base)
    cmds.rotate(30, 0, 0, link1)
    cmds.rotate(-60, 0, 0, link2)
    
    # Inject Agent Metadata (Industry 5.0)
    cmds.addAttr(base, ln="AgentID", dt="string")
    cmds.setAttr(f"{base}.AgentID", "COBOT-ALPHA-01", type="string")
    cmds.addAttr(base, ln="Status", dt="string")
    cmds.setAttr(f"{base}.Status", "AWAITING_HUMAN_INPUT", type="string")
    
    # --- 4. HOLOGRAPHIC OVERLAY (XR) ---
    # Create a "Ghost" of the product on the line
    product, _ = cmds.polyCube(n="Product_Holo", w=3, h=3, d=3)
    cmds.move(-20, 4, 0, product)
    cmds.parent(product, scene_grp)
    
    # XR Shader (Transparent Blue)
    shd_xr = cmds.shadingNode("blinn", asShader=True, n="Mat_XR_Holo")
    cmds.setAttr(f"{shd_xr}.color", 0, 0.8, 1, type="double3")
    cmds.setAttr(f"{shd_xr}.transparency", 0.6, 0.6, 0.6, type="double3")
    cmds.setAttr(f"{shd_xr}.glowIntensity", 0.2)
    sg_xr = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, n=f"{shd_xr}SG")
    cmds.connectAttr(f"{shd_xr}.outColor", f"{sg_xr}.surfaceShader")
    cmds.sets(product, forceElement=sg_xr)
    
    # Animation (Product moving on conveyor)
    cmds.setKeyframe(product, at="translateX", v=-30, t=1)
    cmds.setKeyframe(product, at="translateX", v=30, t=100)
    
    # --- 5. VISION CAMERA ---
    cam = cmds.camera(n="XR_View_Cam")[0]
    cmds.move(0, 20, 40, cam)
    cmds.viewFit(cam, all=True)
    cmds.lookThru(cam)
    
    print("[Architect] Smart Factory Generated.")
    print("Layer 1: Physical (Floor, Robot)")
    print("Layer 2: Digital (Holographic Product)")
    print("Layer 3: Metadata (IoT Attributes injected)")

if __name__ == "__main__":
    build_smart_factory()
