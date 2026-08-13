# Qyntara AI - Installation & Quick Start Guide

## 📦 **Installation**

### Prerequisites
- **Python 3.8+**
- **pip** (Python package manager)
- **Git** (optional, for cloning repository)

### Core Engine Installation

```bash
# Clone repository
git clone https://github.com/Dass2023/Qyntara-AI.git
cd Qyntara-AI

# Install core dependencies
pip install -e .

# Install optional dependencies
pip install -e ".[usd]"      # OpenUSD support
pip install -e ".[scipy]"    # Advanced geometry processing
pip install -e ".[all]"      # Everything (recommended)
```

### AI Compute Layer (v5.0 - Optional)

```bash
# Install Stable Diffusion dependencies
pip install diffusers transformers accelerate safetensors torch torchvision

# Note: Requires CUDA-capable GPU for reasonable performance
# CPU mode works but is 10-50x slower
```

---

## 🚀 **Quick Start - Maya**

### 1. Test Installation

```python
# In Maya Script Editor (Python)
import sys
sys.path.insert(0, r"i:\QYNTARA AI")

from qyntara_dcc.maya import MayaAdapter
from qyntara_core.geometry import MeshProcessor

print("✅ Qyntara Core Engine ready!")
```

### 2. Run Comprehensive Test

```python
# In Maya Script Editor
exec(open(r"i:\QYNTARA AI\tests\test_maya_comprehensive.py").read())
```

**Expected Output**:
- 10/10 tests passed
- Exports created in `C:\temp\`
- New mesh created in scene

### 3. Basic Workflow

```python
from qyntara_dcc.maya import MayaAdapter
from qyntara_core.geometry import MeshProcessor
from qyntara_core.io import GLTFConverter

# 1. Extract mesh
qmesh = MayaAdapter.get_selected_mesh()

# 2. Process
centered = MeshProcessor.center_mesh(qmesh)
scaled = MeshProcessor.scale_mesh(centered, scale=0.5)

# 3. Validate
issues = MeshProcessor.validate_mesh(scaled)
print(f"Issues found: {len(issues)}")

# 4. Export
from qyntara_core import QScene
scene = QScene(meshes=[scaled])
GLTFConverter.export(scene, "C:/exports/model.glb", binary=True)

# 5. Create in Maya
MayaAdapter.create_mesh_from_qmesh(scaled, name="processed_mesh")
```

---

## 🎮 **Quick Start - Unity**

### 1. Install Package

```bash
# Copy Unity SDK to your project
cp -r "i:\QYNTARA AI\unity_sdk" "YourUnityProject\Packages\com.qyntara.runtime"
```

Or via Unity Package Manager:
- Window → Package Manager → + → Add package from disk
- Select `package.json` from `unity_sdk` folder

### 2. Import GLB at Runtime

```csharp
using Qyntara.Runtime;
using UnityEngine;

public class QyntaraTest : MonoBehaviour
{
    void Start()
    {
        // Import GLB file
        string glbPath = "Assets/Models/character.glb";
        GameObject imported = QMeshImporter.ImportGLB(glbPath);
        
        if (imported != null)
        {
            Debug.Log($"✅ Imported: {imported.name}");
            
            // Position in scene
            imported.transform.position = Vector3.zero;
        }
    }
}
```

### 3. Process Meshes

```csharp
using Qyntara.Runtime;

// Get mesh from GameObject
MeshFilter meshFilter = GetComponent<MeshFilter>();
Mesh mesh = meshFilter.mesh;

// Validate
var issues = UnityMeshProcessor.ValidateMesh(mesh);
Debug.Log($"Found {issues.Count} issues");

// Center and scale
UnityMeshProcessor.CenterMesh(mesh);
UnityMeshProcessor.ScaleMesh(mesh, 0.5f);
```

---

## 🤖 **Quick Start - AI Material Synthesis**

### Text-to-PBR Material

```python
from qyntara_ai.stable_diffusion_materials import StableDiffusionMaterialSynthesizer

# Initialize (first run downloads models ~4GB)
synth = StableDiffusionMaterialSynthesizer(device="cuda")

# Generate material
material = synth.text_to_pbr(
    prompt="polished gold metal with fine scratches",
    resolution=1024,
    quality="balanced",
    output_dir="C:/materials/gold"
)

print(f"Material created: {material.name}")
print(f"Base color: {material.base_color}")
print(f"Normal map: {material.normal_map}")
```

### Photo-to-PBR

```python
# Convert photo to PBR textures
material = synth.photo_to_pbr(
    photo_path="wood_sample.jpg",
    resolution=1024,
    output_dir="C:/materials/wood_pbr"
)
```

### Use in Maya

```python
from qyntara_dcc.maya import MayaAdapter
from qyntara_ai.stable_diffusion_materials import quick_material

# Generate material
mat = quick_material("rusty metal", output_dir="C:/temp/rust")

# Apply to selected mesh
import maya.cmds as cmds
selected = cmds.ls(selection=True)[0]

# Create shader
shader = cmds.shadingNode('aiStandardSurface', asShader=True, name="rust_shader")
cmds.setAttr(f"{shader}.baseColor", type="string", mat.base_color)
cmds.setAttr(f"{shader}.metalness", mat.metallic)
cmds.setAttr(f"{shader}.specularRoughness", mat.roughness)

# Assign to mesh
cmds.select(selected)
cmds.hyperShade(assign=shader)
```

---

## 🧪 **Running Tests**

### Unit Tests

```bash
cd "i:\QYNTARA AI"
pytest tests/test_core.py -v --cov=qyntara_core
```

**Expected**: 23/23 tests passed

### Maya Production Test

```python
# In Maya Script Editor
exec(open(r"i:\QYNTARA AI\tests\test_maya_comprehensive.py").read())
```

**Expected**: 10/10 tests passed

---

## 📁 **Project Structure**

```
i:\QYNTARA AI\
├── qyntara_core/              # Core Engine (Layer 1 - Stable)
│   ├── datatypes.py           # QMesh, QMaterial, QScene
│   ├── geometry.py            # MeshProcessor, MeshStats
│   └── io/                    # USD, glTF converters
│
├── qyntara_dcc/               # DCC Adapters
│   ├── maya/                  # Maya adapter
│   ├── max/                   # 3ds Max adapter
│   └── blender/               # Blender adapter
│
├── qyntara_ai/                # AI Compute Layer (Layer 2)
│   ├── material_synthesis.py          # Base classes
│   ├── stable_diffusion_materials.py  # SD integration
│   └── neural_mesh.py                 # GNN optimization
│
├── unity_sdk/                 # Unity Runtime SDK
│   ├── QyntaraRuntime.cs     # Main SDK
│   └── package.json           # Unity package manifest
│
├── tests/                     # Test suite
│   ├── test_core.py                   # Unit tests
│   ├── test_maya_production.py        # Maya basic test
│   └── test_maya_comprehensive.py     # Maya full test
│
└── README.md                  # Documentation
```

---

## 🔧 **Troubleshooting**

### "ModuleNotFoundError: No module named 'qyntara_core'"

**Solution**: Add to Python path
```python
import sys
sys.path.insert(0, r"i:\QYNTARA AI")
```

### "CUDA out of memory" (Stable Diffusion)

**Solutions**:
1. Reduce resolution: `resolution=512` instead of `1024`
2. Enable attention slicing (already enabled by default)
3. Use CPU mode: `device="cpu"` (slower)
4. Close other GPU applications

### Unity "Package errors"

**Solution**: Ensure Newtonsoft.Json is installed
- Window → Package Manager → Search "Newtonsoft Json"
- Or add to `manifest.json`: `"com.unity.nuget.newtonsoft-json": "3.0.2"`

### Maya "OpenMaya" errors

**Solution**: Use `maya.cmds` fallback or update to Maya 2017+
```python
# Check Maya version
import maya.cmds as cmds
print(cmds.about(version=True))
```

---

## 📚 **Next Steps**

1. **Explore Examples**: Read `walkthrough_core_engine_v5.md`
2. **Advanced Features**: Review `MASTER_STRATEGIC_PLAN.md`
3. **Join Community**: Discord (coming soon)
4. **Contribute**: GitHub pull requests welcome

---

## 🆘 **Support**

- **Documentation**: `i:\QYNTARA AI\README.md`
- **Issues**: GitHub Issues
- **Email**: dass2023@qyntara.ai

---

**Last Updated**: February 11, 2026  
**Version**: 5.0.0-beta1
