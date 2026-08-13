import maya.cmds as cmds
import random

def apply_validation_shader():
    """
    Applies a 'Director Mode' Validation Shader to the selection.
    Uses Maya's hardware shader capabilities (dx11Shader or GLSL) 
    visualize topology flow and density in real-time.
    """
    sel = cmds.ls(sl=True)
    if not sel:
        print("[Shader] Select objects first.")
        return

    # 1. Create Shader Network
    shader_name = "M_Qyntara_Director_Validation"
    sg_name = shader_name + "SG"
    
    if not cmds.objExists(shader_name):
        # We'll use a standard Surface with "Tech" settings as a cross-platform fallback
        # Real HLSL/GLSL in Python is complex without external .fx files.
        # We will simulate the "Heatmap" look using a Ramp + Facing Ratio.
        
        shader = cmds.shadingNode("standardSurface", asShader=True, name=shader_name)
        sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=sg_name)
        cmds.connectAttr(f"{shader}.outColor", f"{sg}.surfaceShader")
        
        # 2. Create "X-Ray" Effect (Facing Ratio)
        # This highlights edges vs center, like an electron microscope
        sampler_info = cmds.shadingNode("samplerInfo", asUtility=True)
        ramp = cmds.shadingNode("ramp", asTexture=True, name="Qyntara_Validation_Ramp")
        
        # Connect Facing Ratio to V Coord
        cmds.connectAttr(f"{sampler_info}.facingRatio", f"{ramp}.vCoord")
        cmds.connectAttr(f"{ramp}.outColor", f"{shader}.baseColor")
        cmds.connectAttr(f"{ramp}.outColor", f"{shader}.emissionColor")
        
        # 3. Configure Ramp Colors (The "Director" Look)
        # 0.0 (Edge/Glancing) -> Cyan (Future)
        # 0.5 (Mid) -> Dark Blue
        # 1.0 (Center) -> Black/Void
        
        # Entry 0: Position 0.0, Color Cyan
        cmds.setAttr(f"{ramp}.colorEntryList[0].position", 0.0)
        cmds.setAttr(f"{ramp}.colorEntryList[0].color", 0, 0.8, 0.8, type="double3")
        
        # Entry 1: Position 0.6, Color Dark Blue
        cmds.setAttr(f"{ramp}.colorEntryList[1].position", 0.6)
        cmds.setAttr(f"{ramp}.colorEntryList[1].color", 0, 0, 0.2, type="double3")
        
        # Entry 2: Position 1.0, Color Black
        cmds.setAttr(f"{ramp}.colorEntryList[2].position", 1.0)
        cmds.setAttr(f"{ramp}.colorEntryList[2].color", 0, 0, 0, type="double3")
        
        # 4. Settings
        cmds.setAttr(f"{shader}.emissionWeight", 0.8) # Self-illuminated
        cmds.setAttr(f"{shader}.specularRoughness", 0.4)
        cmds.setAttr(f"{shader}.baseWeight", 0) # Use primarily emission?
        
        print(f"[Shader] Created Director Shader: {shader_name}")
        
    else:
        sg_name = shader_name + "SG"

    # Assign
    for obj in sel:
        try:
            cmds.sets(obj, forceElement=sg_name)
            # Enable Wireframe on Shaded for full "Tech" look
            cmds.displaySurface(obj, xRay=True) # Optional X-Ray
        except: pass
        
    print("[Shader] Applied Validation Visualization.")

if __name__ == "__main__":
    apply_validation_shader()
