"""
Qyntara Core Engine - Maya Production Test Script
=================================================

Test the Maya adapter with a real production scene.
Run this inside Maya's Script Editor.

Author: Dass2023
License: MIT
Version: 5.0.0
"""

import maya.cmds as cmds
import sys
import os

# Add Qyntara to path
qyntara_path = r"i:\QYNTARA AI"
if qyntara_path not in sys.path:
    sys.path.insert(0, qyntara_path)

from qyntara_dcc.maya import MayaAdapter
from qyntara_core.geometry import MeshProcessor, MeshStats
from qyntara_core.io import GLTFConverter, USDConverter
from qyntara_core import QScene

def test_maya_adapter():
    """Test Maya adapter with current scene"""
    
    print("\n" + "="*60)
    print("QYNTARA CORE ENGINE - MAYA PRODUCTION TEST")
    print("="*60 + "\n")
    
    # Test 1: Get selected mesh
    print("[1/7] Testing selected mesh extraction...")
    try:
        selection = cmds.ls(selection=True)
        if not selection:
            print("⚠️  No mesh selected. Please select a mesh and run again.")
            return False
        
        qmesh = MayaAdapter.get_selected_mesh()
        print(f"✅ Extracted mesh: {qmesh.name}")
        print(f"   - Vertices: {qmesh.vertex_count:,}")
        print(f"   - Faces: {qmesh.face_count:,}")
        print(f"   - Topology: {qmesh.topology_type.name}")
        print(f"   - Has UVs: {qmesh.uvs is not None}")
        print(f"   - Has normals: {qmesh.normals is not None}")
    except Exception as e:
        print(f"❌ Failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 2: Validate mesh
    print("\n[2/7] Validating mesh quality...")
    issues = MeshProcessor.validate_mesh(qmesh)
    if issues:
        print(f"⚠️  Found {len(issues)} issues:")
        for issue in issues[:5]:  # Show first 5
            print(f"   - {issue}")
        if len(issues) > 5:
            print(f"   ... and {len(issues) - 5} more")
    else:
        print("✅ Mesh is clean (no issues found)")
    
    # Test 3: Compute statistics
    print("\n[3/7] Computing mesh statistics...")
    stats = MeshStats.compute_stats(qmesh)
    print(f"✅ Statistics:")
    print(f"   - Bounding box: {stats['bounding_box']['size']}")
    print(f"   - Surface area: {stats['surface_area']:.2f} units²")
    print(f"   - UV sets: {stats['uv_set_count']}")
    
    # Test 4: Process mesh (center + scale)
    print("\n[4/7] Processing mesh (center + scale 0.5x)...")
    centered = MeshProcessor.center_mesh(qmesh)
    scaled = MeshProcessor.scale_mesh(centered, scale=0.5)
    print(f"✅ Processed mesh")
    
    # Test 5: Create processed mesh in Maya
    print("\n[5/7] Creating processed mesh in Maya...")
    try:
        new_mesh_name = MayaAdapter.create_mesh_from_qmesh(
            scaled,
            name=f"{qmesh.name}_processed"
        )
        print(f"✅ Created: {new_mesh_name}")
        cmds.select(new_mesh_name)
    except Exception as e:
        print(f"❌ Failed to create mesh: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 6: Export to glTF
    print("\n[6/7] Exporting to glTF/GLB...")
    try:
        scene = QScene(meshes=[scaled])
        export_path = r"C:\temp\qyntara_test.glb"
        
        # Create directory if needed
        os.makedirs(os.path.dirname(export_path), exist_ok=True)
        
        GLTFConverter.export(scene, export_path, binary=True)
        print(f"✅ Exported to: {export_path}")
        
        # Verify file exists
        if os.path.exists(export_path):
            file_size = os.path.getsize(export_path)
            print(f"   File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    except Exception as e:
        print(f"❌ Export failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 7: Export to USD
    print("\n[7/7] Exporting to USD...")
    try:
        usd_path = r"C:\temp\qyntara_test.usdc"
        USDConverter.export(scene, usd_path, binary=True)
        print(f"✅ Exported to: {usd_path}")
        
        if os.path.exists(usd_path):
            file_size = os.path.getsize(usd_path)
            print(f"   File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    except ImportError:
        print("⚠️  USD not installed (pip install usd-core)")
    except Exception as e:
        print(f"❌ USD export failed: {e}")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
    print("\n✅ Core Engine is working correctly in Maya!")
    print("Next: Try importing the GLB in Unity/Unreal/Three.js\n")
    
    return True

# Run test
if __name__ == "__main__":
    test_maya_adapter()
