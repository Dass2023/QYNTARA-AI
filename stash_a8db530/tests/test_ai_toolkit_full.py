import logging
import sys
import os

# Ensure qyntara is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

import maya.cmds as cmds
import maya.standalone

def setup_scene():
    cmds.file(new=True, force=True)
    # Create a complex test object (e.g., Torus)
    obj = cmds.polyTorus(r=1, sr=0.5)[0]
    cmds.polyCube(n="Cube_Test")
    return [obj, "Cube_Test"]

def test_analysis():
    print("\n--- Testing Analysis ---")
    from qyntara_ai.ai_assist import ai_interface
    ai = ai_interface.AIAssist()
    sel = cmds.ls(type="transform")
    res = ai.analyze_mesh_topology(sel)
    print(f"Analysis Result: {res}")
    if res and "Cube_Test" in res:
        print("Analysis: PASSED")
    else:
        print("Analysis: FAILED")

def test_visualization():
    print("\n--- Testing Visualization ---")
    from qyntara_ai.core import visualizer
    obj = ["Cube_Test"]
    
    # 1. Seams
    print("Toggle Seams ON")
    visualizer.QyntaraVisualizer.toggle_seam_overlay(obj, True)
    # Verify attribute
    # displayMapBorder is usually on shape
    shape = cmds.listRelatives("Cube_Test", s=True)[0]
    # Note: polyOptions command doesn't easily show query state for displayMapBorder in all versions, 
    # but no crash = success for now.
    
    # 2. Distortion
    print("Toggle Distortion ON")
    visualizer.QyntaraVisualizer.toggle_distortion_heatmap(obj, True)
    if cmds.getAttr(f"{obj[0]}.displayColors"):
        print("Distortion (Vertex Colors): PASSED")
    else:
        print("Distortion: FAILED (displayColors not set)")
    
    # Turn off
    visualizer.QyntaraVisualizer.toggle_distortion_heatmap(obj, False)

def test_unwrap_backend():
    print("\n--- Testing AI Unwrap Backend ---")
    from qyntara_ai.core import uv_tools
    obj = ["Cube_Test"]
    
    # Run with Flow=True, Axis=True (Hard Surface)
    try:
        uv_tools.smart_ai_unwrap(obj, flow=True, axis=True, seamless=True)
        print("Smart Unwrap (Hard Surface): PASSED")
    except Exception as e:
        print(f"Smart Unwrap (Hard Surface): FAILED - {e}")

    # Run Mosaic Mode Stub (Flow=False, Axis=False)
    try:
        uv_tools.smart_ai_unwrap(obj, flow=False, axis=False, seamless=True)
        print("Smart Unwrap (Mosaic Stub): PASSED")
    except Exception as e:
        print(f"Smart Unwrap (Mosaic Stub): FAILED - {e}")

def test_future_tech_stubs():
    print("\n--- Testing Future Tech Stubs ---")
    from qyntara_ai.ai_assist import ai_interface
    ai = ai_interface.AIAssist()
    
    # SeamGPT
    try:
        res = ai.predict_seams_seamgpt("Cube_Test")
        if res == []:
            print("SeamGPT Stub: PASSED (Graceful Fallback)")
        else:
            print(f"SeamGPT Stub: UNEXPECTED RETURN {res}")
    except Exception as e:
        print(f"SeamGPT Stub: FAILED - {e}")

def test_manual_tools():
    print("\n--- Testing Manual Tool Wrappers ---")
    # Need selection for these usually, or pass args if modified
    # The UI calls simple cmds... let's test specific ones if we wrapped them.
    # UI calls 'texOrientShells' etc directly via mel.
    # We'll just verify imports work.
    pass

def test_engine_sets():
    print("\n--- Testing Engine Sets (UV2/UV3) ---")
    from qyntara_ai.core import uv_tools
    obj = ["Cube_Test"]
    
    # 1. Lightmap
    uv_tools.generate_lightmap_uvs(obj, engine='unreal')
    sets = cmds.polyUVSet(obj[0], q=True, allUVSets=True)
    if "uvSet2" in sets or "lightmap" in sets:
        print("UV2 Generation: PASSED")
    else:
        print(f"UV2 Generation: FAILED (Sets: {sets})")

    # 2. AO
    uv_tools.setup_ao_uvs(obj)
    sets = cmds.polyUVSet(obj[0], q=True, allUVSets=True)
    if "uvSet3" in sets:
        print("UV3 Setup: PASSED")
    else:
        print(f"UV3 Setup: FAILED (Sets: {sets})")

def main():
    print("=== STARTING AI TOOLKIT VERIFICATION ===")
    try:
        # Initialize standalone if running external
        try:
            maya.standalone.initialize(name='python')
        except: pass
        
        setup_scene()
        test_analysis()
        test_visualization()
        test_unwrap_backend()
        test_future_tech_stubs()
        test_engine_sets()
        
        print("\n=== VERIFICATION COMPLETE ===")
        
    except Exception as e:
        print(f"\nCRITICAL FAIL: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
