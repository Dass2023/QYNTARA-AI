"""
Phase 27 — World-Best Hybrid Retopology Pipeline Verification
Run this inside Maya's Script Editor (Python tab) to test all 9 stages.
"""
import sys
if "i:/QYNTARA AI" not in sys.path:
    sys.path.insert(0, "i:/QYNTARA AI")

import importlib
import maya.cmds as cmds

# Force-reload updated modules so Maya picks up the new 9-stage code
import qyntara_ai.core.retopology as _retopo_mod
import qyntara_ai.core.quantum_geometry as _qg_mod
importlib.reload(_retopo_mod)
importlib.reload(_qg_mod)

def create_test_mesh():
    """Creates a noisy, high-poly sphere to stress-test the pipeline."""
    cmds.file(new=True, force=True)
    # 1. High-poly sphere (simulates a raw 3D scan)
    sphere = cmds.polySphere(r=5, sx=80, sy=80, name="RawScan_HighPoly")[0]
    
    # 2. Inject surface noise (simulates scanner chatter)
    cmds.select(f"{sphere}.vtx[*]")
    cmds.polyMoveVertex(random=0.1)
    cmds.select(clear=True)
    
    # 3. Add a sharp crease (simulates a hard-surface feature)
    cube = cmds.polyCube(w=3, h=3, d=3, name="HardSurface_Insert")[0]
    cmds.move(0, 5, 0, cube)
    
    print("="*60)
    print("TEST SCENE READY")
    print(f"  Noisy Sphere: {sphere} ({cmds.polyEvaluate(sphere, face=True)} faces)")
    print(f"  Hard-Surface: {cube}")
    print("="*60)
    return sphere, cube

def test_retopo_standard(mesh):
    """Test the standard 9-stage pipeline (no proxy, no symmetry)."""
    print("\n" + "="*60)
    print("TEST 1: Standard 9-Stage Retopology")
    print("="*60)
    cmds.select(mesh, replace=True)
    
    from qyntara_ai.core.retopology import AutoRetopologyManager
    manager = AutoRetopologyManager()
    results = manager.run_smart_retopo(
        objects=[mesh],
        target_quality="mid",
        target_density=2000,
        edge_flow_bias=1.0,
        symmetry_axis=None,
        iterations=2,
        neural_refinement=False,
        use_proxy_sanitation=False
    )
    
    if results:
        new_faces = cmds.polyEvaluate(results[0], face=True)
        print(f"\n[PASS] TEST 1 PASSED: {results[0]} -> {new_faces} faces")
    else:
        print("\n[FAIL] TEST 1 FAILED: No results returned.")
    return results

def test_retopo_with_symmetry(mesh):
    """Test the pipeline with Symmetry DNA enforcement."""
    print("\n" + "="*60)
    print("TEST 2: Symmetry DNA Retopology (X-Axis)")
    print("="*60)
    cmds.select(mesh, replace=True)
    
    from qyntara_ai.core.retopology import AutoRetopologyManager
    manager = AutoRetopologyManager()
    results = manager.run_smart_retopo(
        objects=[mesh],
        target_quality="mid",
        target_density=3000,
        edge_flow_bias=1.5,
        symmetry_axis="x",
        iterations=3,
        neural_refinement=False,
        use_proxy_sanitation=False
    )
    
    if results:
        new_faces = cmds.polyEvaluate(results[0], face=True)
        print(f"\n[PASS] TEST 2 PASSED: {results[0]} -> {new_faces} faces (Symmetry: X)")
    else:
        print("\n[FAIL] TEST 2 FAILED: No results returned.")
    return results

def test_retopo_with_neural(mesh):
    """Test the pipeline with Neural Refinement enabled."""
    print("\n" + "="*60)
    print("TEST 3: Neural-Refined Retopology")
    print("="*60)
    cmds.select(mesh, replace=True)
    
    from qyntara_ai.core.retopology import AutoRetopologyManager
    manager = AutoRetopologyManager()
    results = manager.run_smart_retopo(
        objects=[mesh],
        target_quality="mid",
        target_density=1500,
        edge_flow_bias=2.0,
        symmetry_axis=None,
        iterations=3,
        neural_refinement=True,
        use_proxy_sanitation=False
    )
    
    if results:
        new_faces = cmds.polyEvaluate(results[0], face=True)
        print(f"\n[PASS] TEST 3 PASSED: {results[0]} -> {new_faces} faces (Neural: ON)")
    else:
        print("\n[FAIL] TEST 3 FAILED: No results returned.")
    return results

# --- RUN ALL TESTS ---
if __name__ == "__main__":
    sphere, cube = create_test_mesh()
    
    # Test 1: Standard pipeline
    test_retopo_standard(sphere)
    
    # Test 2: With Symmetry DNA
    test_retopo_with_symmetry(cube)
    
    # Test 3: Neural Refinement (uses sphere duplicate)
    sphere2 = cmds.duplicate(sphere, name="NeuralTest_Sphere")[0]
    cmds.move(15, 0, 0, sphere2)
    test_retopo_with_neural(sphere2)
    
    print("\n" + "="*60)
    print("ALL PHASE 27 VERIFICATION TESTS COMPLETE")
    print("="*60)
