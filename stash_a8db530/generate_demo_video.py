
"""
Qyntara AI - V6.0 Feature Demo Generator
Automates the creation of a 'sample video' showcasing:
1. Neural Link (Visual Locator)
2. Generative DNA (Evolved Geometry)
3. 360 Camera Turntable
"""
import maya.cmds as cmds
import maya.mel as mel
import os

def generate_demo():
    print("--- Generating V6.0 Demo Video ---")
    
    # 1. New Scene
    cmds.file(new=True, force=True)
    
    # 2. Setup Assets (Industry 4.0 Base)
    base = cmds.polyCube(n="ASSET-8842-X", w=5, h=2, d=5)[0]
    top = cmds.polyCylinder(n="ASSET-8842-X_Top", r=1, h=2)[0]
    cmds.move(0, 2, 0, top)
    cmds.parent(top, base)
    
    # Material for Base (Dark Tech)
    shd = cmds.shadingNode("blinn", asShader=True, n="Base_Mat")
    cmds.setAttr(shd + ".color", 0.1, 0.1, 0.1, type="double3")
    cmds.select(base)
    cmds.hyperShade(assign=shd)

    # 3. Animate V6.0 Actions
    cmds.playbackOptions(min=1, max=120)
    
    # Frame 1: Initial View
    cmds.currentTime(1)
    
    # Frame 20: Neural Link Activates
    cmds.currentTime(20)
    if not cmds.objExists("Neural_Cortex_Link"):
        loc = cmds.spaceLocator(n="Neural_Cortex_Link")[0]
        cmds.move(0, 8, 0, loc)
        cmds.scale(3, 3, 3, loc)
        cmds.annotate(loc, tx="Neural Uplink: CONNECTED", p=(0, 10, 0))
        cmds.setAttr(loc + ".overrideEnabled", 1)
        cmds.setAttr(loc + ".overrideColor", 14) # Green
        
        # Key Visibility for Pop-in effect
        cmds.setKeyframe(loc, v=0, t=19)
        cmds.setKeyframe(loc, v=1, t=20)
        
    # Frame 60: Evolve Design (Generative Mutation)
    cmds.currentTime(60)
    gen_name = "Evolved_Gen1"
    if not cmds.objExists(gen_name):
        new_obj = cmds.duplicate(base, n=gen_name)[0]
        cmds.move(6, 0, 0, new_obj)
        # Apply Mutation (Smooth + Reduce)
        cmds.polySmooth(new_obj, dv=1)
        cmds.polyReduce(new_obj, p=30)
        
        # Material (Cyan DNA)
        dna_shd = cmds.shadingNode("blinn", asShader=True, n="DNA_Mat")
        cmds.setAttr(dna_shd + ".color", 0, 0.8, 1, type="double3")
        cmds.setAttr(dna_shd + ".transparency", 0.2, 0.2, 0.2, type="double3")
        cmds.select(new_obj)
        cmds.hyperShade(assign=dna_shd)
        
        # Key Visibility
        cmds.setKeyframe(new_obj, v=0, t=59)
        cmds.setKeyframe(new_obj, v=1, t=60)
        
        # Annotate
        ann = cmds.annotate(new_obj, tx="Gen 1: Evolved", p=(6, 5, 0))
        cmds.setKeyframe(ann, v=0, t=59)
        cmds.setKeyframe(ann, v=1, t=60)

    # 4. Camera Turntable
    cam = cmds.camera(centerOfInterest=5, focalLength=35, lensSqueezeRatio=1, cameraScale=1, 
                      horizontalFilmAperture=1.41732, horizontalFilmOffset=0, 
                      verticalFilmAperture=0.94488, verticalFilmOffset=0, 
                      filmFit="Fill", overscan=1, motionBlur=0, shutterAngle=144, 
                      nearClipPlane=0.1, farClipPlane=10000, orthographic=0, 
                      orthographicWidth=30, panZoomEnabled=0, horizontalPan=0, 
                      verticalPan=0, zoom=1)[0]
    cmds.rename(cam, "Demo_Cam")
    cam = "Demo_Cam"
    
    # Position
    cmds.setAttr(cam + ".tx", 0)
    cmds.setAttr(cam + ".ty", 10)
    cmds.setAttr(cam + ".tz", 20)
    cmds.setAttr(cam + ".rx", -15)
    
    # Orbit
    grp = cmds.group(em=True, n="Cam_Grp")
    cmds.parent(cam, grp)
    cmds.setKeyframe(grp, at="ry", v=0, t=1)
    cmds.setKeyframe(grp, at="ry", v=360, t=120)
    
    # 5. Playblast
    # Use Viewport 2.0
    model_panel = cmds.getPanel(type="modelPanel")[0]
    cmds.modelEditor(model_panel, e=True, camera=cam, displayAppearance="smoothShaded", allObjects=False, polymeshes=True, locators=True)
    
    output_path = os.path.join(os.environ["USERPROFILE"], "Desktop", "Qyntara_V6_Demo.avi")
    print(f"Rendering demo to: {output_path}")
    
    try:
        cmds.playblast(filename=output_path, format="avi", viewer=True, 
                       showOrnaments=False, offScreen=True, percent=100, 
                       compression="none", width=1280, height=720, forceOverwrite=True)
        print("[SUCCESS] Demo video generated!")
    except Exception as e:
        print(f"[ERROR] Playblast failed: {e}")
        # Fallback to viewport drive
        for i in range(1, 121):
            cmds.currentTime(i)
            cmds.refresh(cv=True)

if __name__ == "__main__":
    generate_demo()
