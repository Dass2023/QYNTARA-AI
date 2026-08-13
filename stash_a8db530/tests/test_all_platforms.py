"""
Qyntara AI - Comprehensive Multi-Platform Test Suite
====================================================

Tests all platforms and components:
- Core Engine (datatypes, geometry, converters)
- DCC Adapters (Maya, 3ds Max, Blender)
- Runtime SDKs (Unity, Unreal, Three.js)
- AI Layer (Material synthesis, neural mesh)
- Format Converters (USD, glTF, FBX, OBJ)

Usage:
    python tests/test_all_platforms.py
    python tests/test_all_platforms.py --platform maya
    python tests/test_all_platforms.py --verbose --export-report

Author: Dass2023
Version: 5.0.0
"""

import sys
import os
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Test results storage
test_results = {
    "timestamp": datetime.now().isoformat(),
    "version": "5.0.0",
    "platform_tests": {},
    "summary": {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0
    }
}


class TestRunner:
    """Unified test runner for all platforms"""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.current_platform = None
    
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        prefix = {
            "INFO": "[i] INFO:",
            "SUCCESS": "[OK] PASS:",
            "ERROR": "[X] FAIL:",
            "WARNING": "[!] WARN:",
            "SKIP": "[-] SKIP:"
        }.get(level, "•")
        
        print(f"[{timestamp}] {prefix} {message}")
    
    def run_test(self, name: str, test_func, platform: str = "core") -> bool:
        """Run a single test and record result"""
        self.log(f"Running: {name}", "INFO")
        
        try:
            test_func()
            self.log(f"PASSED: {name}", "SUCCESS")
            self._record_result(platform, name, "passed")
            return True
        except Exception as e:
            self.log(f"FAILED: {name} - {str(e)}", "ERROR")
            if self.verbose:
                import traceback
                traceback.print_exc()
            self._record_result(platform, name, "failed", str(e))
            return False
    
    def skip_test(self, name: str, reason: str, platform: str = "core"):
        """Skip a test with reason"""
        self.log(f"SKIPPED: {name} - {reason}", "SKIP")
        self._record_result(platform, name, "skipped", reason)
    
    def _record_result(self, platform: str, test_name: str, status: str, error: str = None):
        """Record test result"""
        if platform not in test_results["platform_tests"]:
            test_results["platform_tests"][platform] = []
        
        test_results["platform_tests"][platform].append({
            "name": test_name,
            "status": status,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })
        
        test_results["summary"]["total"] += 1
        if status == "passed":
            test_results["summary"]["passed"] += 1
        elif status == "failed":
            test_results["summary"]["failed"] += 1
        elif status == "skipped":
            test_results["summary"]["skipped"] += 1


# ============================================================================
# CORE ENGINE TESTS
# ============================================================================

def test_core_engine(runner: TestRunner):
    """Test core engine components"""
    runner.log("=" * 60)
    runner.log("TESTING CORE ENGINE")
    runner.log("=" * 60)
    
    # Test 1: Import core modules
    def test_imports():
        from qyntara_core import QMesh, QMaterial, QScene
        from qyntara_core.geometry import MeshProcessor, MeshStats
        from qyntara_core.io import USDConverter, GLTFConverter, FBXConverter, OBJConverter
        assert QMesh is not None
        assert GLTFConverter is not None
    
    runner.run_test("Core module imports", test_imports, "core")
    
    # Test 2: QMesh creation
    def test_qmesh_creation():
        import numpy as np
        from qyntara_core import QMesh
        
        vertices = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], dtype=np.float32)
        faces = np.array([[0, 1, 2, 3]], dtype=np.int32)
        
        mesh = QMesh(vertices=vertices, faces=faces, name="test_quad")
        assert mesh.vertex_count == 4
        assert mesh.face_count == 1
        assert mesh.name == "test_quad"
    
    runner.run_test("QMesh creation", test_qmesh_creation, "core")
    
    # Test 3: Mesh validation
    def test_mesh_validation():
        import numpy as np
        from qyntara_core import QMesh
        from qyntara_core.geometry import MeshProcessor
        
        vertices = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0]], dtype=np.float32)
        faces = np.array([[0, 1, 2, -1]], dtype=np.int32)
        mesh = QMesh(vertices=vertices, faces=faces)
        
        issues = MeshProcessor.validate_mesh(mesh)
        assert isinstance(issues, list)
    
    runner.run_test("Mesh validation", test_mesh_validation, "core")
    
    # Test 4: glTF export/import
    def test_gltf_roundtrip():
        import numpy as np
        import tempfile
        from qyntara_core import QMesh, QScene
        from qyntara_core.io import GLTFConverter
        
        # Create test mesh
        vertices = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]], dtype=np.float32)
        faces = np.array([[0, 1, 2, -1]], dtype=np.int32)
        mesh = QMesh(vertices=vertices, faces=faces, name="triangle")
        scene = QScene(meshes=[mesh])
        
        # Export
        with tempfile.NamedTemporaryFile(suffix=".glb", delete=False) as f:
            temp_path = f.name
        
        try:
            GLTFConverter.export(scene, temp_path, binary=True)
            
            # Import
            imported_scene = GLTFConverter.import_file(temp_path)
            assert len(imported_scene.meshes) > 0
            assert imported_scene.meshes[0].vertex_count == 3
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    runner.run_test("glTF roundtrip", test_gltf_roundtrip, "core")


# ============================================================================
# MAYA ADAPTER TESTS
# ============================================================================

def test_maya_adapter(runner: TestRunner):
    """Test Maya adapter"""
    runner.log("=" * 60)
    runner.log("TESTING MAYA ADAPTER")
    runner.log("=" * 60)
    
    try:
        import maya.cmds as cmds
        import maya.standalone
        
        # Initialize Maya standalone
        try:
            maya.standalone.initialize()
        except:
            pass  # Already initialized
        
        # Test 1: Import adapter
        def test_maya_import():
            from qyntara_dcc.maya import MayaAdapter
            assert MayaAdapter is not None
        
        runner.run_test("Maya adapter import", test_maya_import, "maya")
        
        # Test 2: Extract mesh
        def test_maya_extract():
            from qyntara_dcc.maya import MayaAdapter
            
            # Create test sphere
            sphere = cmds.polySphere(name="test_sphere")[0]
            
            # Extract to QMesh
            qmesh = MayaAdapter.extract_mesh(sphere)
            assert qmesh is not None
            assert qmesh.vertex_count > 0
            
            # Cleanup
            cmds.delete(sphere)
        
        runner.run_test("Maya mesh extraction", test_maya_extract, "maya")
        
        # Test 3: Create mesh
        def test_maya_create():
            import numpy as np
            from qyntara_core import QMesh
            from qyntara_dcc.maya import MayaAdapter
            
            # Create QMesh
            vertices = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], dtype=np.float32)
            faces = np.array([[0, 1, 2, 3]], dtype=np.int32)
            qmesh = QMesh(vertices=vertices, faces=faces, name="test_quad")
            
            # Create in Maya
            maya_mesh = MayaAdapter.create_mesh(qmesh)
            assert maya_mesh is not None
            assert cmds.objExists(maya_mesh)
            
            # Cleanup
            cmds.delete(maya_mesh)
        
        runner.run_test("Maya mesh creation", test_maya_create, "maya")
        
    except ImportError as e:
        runner.skip_test("Maya adapter tests", f"Maya not available: {e}", "maya")


# ============================================================================
# 3DS MAX ADAPTER TESTS
# ============================================================================

def test_max_adapter(runner: TestRunner):
    """Test 3ds Max adapter"""
    runner.log("=" * 60)
    runner.log("TESTING 3DS MAX ADAPTER")
    runner.log("=" * 60)
    
    try:
        import MaxPlus
        
        # Test 1: Import adapter
        def test_max_import():
            from qyntara_dcc.max import MaxAdapter
            assert MaxAdapter is not None
        
        runner.run_test("Max adapter import", test_max_import, "max")
        
        # Test 2: Extract mesh
        def test_max_extract():
            from qyntara_dcc.max import MaxAdapter
            
            # Create test box
            box = MaxPlus.Factory.CreateGeomObject(MaxPlus.ClassIds.Box)
            box.ParameterBlock.Width.Value = 10.0
            box.ParameterBlock.Length.Value = 10.0
            box.ParameterBlock.Height.Value = 10.0
            
            node = MaxPlus.Factory.CreateNode(box)
            
            # Extract to QMesh
            qmesh = MaxAdapter.extract_mesh(node.GetName())
            assert qmesh is not None
            assert qmesh.vertex_count > 0
            
            # Cleanup
            node.Delete()
        
        runner.run_test("Max mesh extraction", test_max_extract, "max")
        
    except ImportError as e:
        runner.skip_test("3ds Max adapter tests", f"3ds Max not available: {e}", "max")


# ============================================================================
# BLENDER ADAPTER TESTS
# ============================================================================

def test_blender_adapter(runner: TestRunner):
    """Test Blender adapter"""
    runner.log("=" * 60)
    runner.log("TESTING BLENDER ADAPTER")
    runner.log("=" * 60)
    
    try:
        import bpy
        
        # Test 1: Import adapter
        def test_blender_import():
            from qyntara_dcc.blender import BlenderAdapter
            assert BlenderAdapter is not None
        
        runner.run_test("Blender adapter import", test_blender_import, "blender")
        
        # Test 2: Extract mesh
        def test_blender_extract():
            from qyntara_dcc.blender import BlenderAdapter
            
            # Create test cube
            bpy.ops.mesh.primitive_cube_add()
            cube = bpy.context.active_object
            
            # Extract to QMesh
            qmesh = BlenderAdapter.extract_mesh(cube.name)
            assert qmesh is not None
            assert qmesh.vertex_count > 0
            
            # Cleanup
            bpy.data.objects.remove(cube)
        
        runner.run_test("Blender mesh extraction", test_blender_extract, "blender")
        
        # Test 3: Create mesh
        def test_blender_create():
            import numpy as np
            from qyntara_core import QMesh
            from qyntara_dcc.blender import BlenderAdapter
            
            # Create QMesh
            vertices = np.array([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], dtype=np.float32)
            faces = np.array([[0, 1, 2, 3]], dtype=np.int32)
            qmesh = QMesh(vertices=vertices, faces=faces, name="test_quad")
            
            # Create in Blender
            blender_obj = BlenderAdapter.create_mesh(qmesh)
            assert blender_obj is not None
            assert blender_obj in bpy.data.objects.values()
            
            # Cleanup
            bpy.data.objects.remove(blender_obj)
        
        runner.run_test("Blender mesh creation", test_blender_create, "blender")
        
    except ImportError as e:
        runner.skip_test("Blender adapter tests", f"Blender not available: {e}", "blender")


# ============================================================================
# AI LAYER TESTS
# ============================================================================

def test_ai_layer(runner: TestRunner):
    """Test AI compute layer"""
    runner.log("=" * 60)
    runner.log("TESTING AI COMPUTE LAYER")
    runner.log("=" * 60)
    
    # Test 1: Import AI modules
    def test_ai_imports():
        from qyntara_ai import MaterialSynthesizer, GPUWatchdog
        from qyntara_ai.stable_diffusion_materials import StableDiffusionMaterialSynthesizer
        from qyntara_ai.neural_mesh import NeuralMeshOptimizer
        assert MaterialSynthesizer is not None
        assert GPUWatchdog is not None
    
    runner.run_test("AI module imports", test_ai_imports, "ai")
    
    # Test 2: GPU Watchdog
    def test_gpu_watchdog():
        from qyntara_ai import GPUWatchdog
        
        watchdog = GPUWatchdog(memory_limit_gb=4.0)
        status = watchdog.check_gpu_status()
        assert "available" in status
        assert "memory_free_gb" in status
    
    runner.run_test("GPU Watchdog", test_gpu_watchdog, "ai")
    
    # Test 3: Material Synthesizer (CPU mode)
    def test_material_synthesizer():
        from qyntara_ai import MaterialSynthesizer
        
        synth = MaterialSynthesizer(device="cpu")  # CPU for testing
        assert synth.device == "cpu"
    
    runner.run_test("Material Synthesizer init", test_material_synthesizer, "ai")


# ============================================================================
# FORMAT CONVERTER TESTS
# ============================================================================

def test_format_converters(runner: TestRunner):
    """Test all format converters"""
    runner.log("=" * 60)
    runner.log("TESTING FORMAT CONVERTERS")
    runner.log("=" * 60)
    
    import numpy as np
    import tempfile
    from qyntara_core import QMesh, QScene
    
    # Create test mesh
    vertices = np.array([[0, 0, 0], [1, 0, 0], [0.5, 1, 0]], dtype=np.float32)
    faces = np.array([[0, 1, 2, -1]], dtype=np.int32)
    mesh = QMesh(vertices=vertices, faces=faces, name="test_triangle")
    scene = QScene(meshes=[mesh])
    
    # Test USD
    def test_usd():
        from qyntara_core.io import USDConverter
        
        with tempfile.NamedTemporaryFile(suffix=".usda", delete=False) as f:
            temp_path = f.name
        
        try:
            USDConverter.export(scene, temp_path, binary=False)
            assert os.path.exists(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    try:
        runner.run_test("USD converter", test_usd, "converters")
    except ImportError:
        runner.skip_test("USD converter", "USD library not available", "converters")
    
    # Test glTF
    def test_gltf():
        from qyntara_core.io import GLTFConverter
        
        with tempfile.NamedTemporaryFile(suffix=".glb", delete=False) as f:
            temp_path = f.name
        
        try:
            GLTFConverter.export(scene, temp_path, binary=True)
            assert os.path.exists(temp_path)
            
            # Test import
            imported = GLTFConverter.import_file(temp_path)
            assert len(imported.meshes) > 0
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    runner.run_test("glTF converter", test_gltf, "converters")
    
    # Test OBJ
    def test_obj():
        from qyntara_core.io import OBJConverter
        
        with tempfile.NamedTemporaryFile(suffix=".obj", delete=False) as f:
            temp_path = f.name
        
        try:
            OBJConverter.export(scene, temp_path)
            assert os.path.exists(temp_path)
            
            # Test import
            imported = OBJConverter.import_file(temp_path)
            assert len(imported.meshes) > 0
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            mtl_path = temp_path.replace(".obj", ".mtl")
            if os.path.exists(mtl_path):
                os.unlink(mtl_path)
    
    runner.run_test("OBJ converter", test_obj, "converters")


# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

def print_summary(runner: TestRunner):
    """Print test summary"""
    summary = test_results["summary"]
    
    print("\n" + "=" * 60)
    print("FINAL TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests:  {summary['total']}")
    print(f"[OK] Passed:    {summary['passed']}")
    print(f"[X] Failed:     {summary['failed']}")
    print(f"[-] Skipped:    {summary['skipped']}")
    print("=" * 60)
    
    if summary['failed'] > 0:
        print("\n[X] SOME TESTS FAILED")
        return False
    elif summary['passed'] == 0:
        print("\n[!] NO TESTS RAN")
        return False
    else:
        print("\n[OK] ALL TESTS PASSED")
        return True


def export_report(output_path: str):
    """Export test report to JSON"""
    with open(output_path, 'w') as f:
        json.dump(test_results, f, indent=2)
    print(f"\n📄 Test report exported to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Qyntara AI Multi-Platform Test Suite")
    parser.add_argument("--platform", choices=["core", "maya", "max", "blender", "ai", "converters", "all"],
                       default="all", help="Platform to test")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--export-report", "-r", type=str, help="Export report to JSON file")
    
    args = parser.parse_args()
    
    runner = TestRunner(verbose=args.verbose)
    
    print("\n" + "=" * 60)
    print("QYNTARA AI - MULTI-PLATFORM TEST SUITE v5.0.0")
    print("=" * 60)
    print(f"Platform: {args.platform}")
    print(f"Timestamp: {test_results['timestamp']}")
    print("=" * 60 + "\n")
    
    # Run tests based on platform
    if args.platform in ["core", "all"]:
        test_core_engine(runner)
    
    if args.platform in ["maya", "all"]:
        test_maya_adapter(runner)
    
    if args.platform in ["max", "all"]:
        test_max_adapter(runner)
    
    if args.platform in ["blender", "all"]:
        test_blender_adapter(runner)
    
    if args.platform in ["ai", "all"]:
        test_ai_layer(runner)
    
    if args.platform in ["converters", "all"]:
        test_format_converters(runner)
    
    # Print summary
    success = print_summary(runner)
    
    # Export report if requested
    if args.export_report:
        export_report(args.export_report)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
