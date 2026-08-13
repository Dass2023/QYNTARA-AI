# QYNTARA AI (v4.0)

**Universal AI-Driven 3D Asset Automation System**

QYNTARA AI is a production-grade automation platform designed to transform raw inputs (prompts, images, rough 3D scans) into fully optimized, game-ready assets for Unreal Engine, Unity, and Omniverse. It bridges the gap between Generative AI and professional TD pipelines inside Autodesk Maya.

---

## 🌟 Core Modules

### 1. GENERATE AI ASSIST
- **Text-to-3D**: Create assets from natural language.
- **Image-to-3D**: Turn concepts into meshes.
- **Auto Full Pipeline**: One-click generation → game-ready asset chain.

### 2. QUAD REMESH
- **Universal Retopology**: Convert decimated scans/AI meshes to clean quads.
- **Presets**: Game (2k), Film (20k), Hero (50k).

### 3. MATERIALS AI
- **Shader Synthesis**: AI-driven material creation and conversion.
- **Universal Maps**: Generate Normal, Roughness, and Metallic maps from Albedo.
- **Scanner**: Auto-detect and standardize scene materials.

### 4. VALIDATE SCENE
- **TD-Grade QA**: Check for N-Gons, Non-Manifold, UV overlaps, and naming conventions.
- **Auto-Fix**: One-click resolution for common pipeline errors.

### 5. UNIVERSAL UV
- **Auto Seams**: AI-assisted unwrapping.
- **Lightmap Gen**: Dedicated non-overlapping UV setups for engine baking.
- **Dual Channel**: Simultaneous Texture and Lightmap UV generation.

### 6. OPTIMIZATION & EXPORT
- **LOD Chain**: Auto-generate LOD0/1/2.
- **Pivot Logic**: Game-ready pivot placement.
- **Multi-Format**: Export to OBJ, FBX, USD.

---

## 🚀 Installation & Setup

### 1. Backend (GPU Server)
Recommended environment: `venv_gpu` (Python 3.10+, CUDA 12.x).

```powershell
cd backend
# Install dependencies
pip install -r requirements.txt
# Run Server
..\venv_gpu\Scripts\uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend (Web Dashboard)
Dashboard for remote monitoring and asset library.
```powershell
cd frontend
npm install
npm run dev
# Access at http://localhost:3000
```

### 3. Maya Client (Plugin)
Install the dockable UI into Autodesk Maya (2022+).
```powershell
python maya/install_client.py
```
**In Maya (Python Script Editor):**
```python
import qyntara_client
qyntara_client.show()
```

---

## 🎮 Usage Guide

### The 6-Tab Workflow
The Qyntara Client is organized into 6 tabs representing the production stages:

1.  **GENERATE**: Enter a prompt and click "🚀 AUTO FULL PIPELINE".
2.  **REMESH**: Clean up the geometry (or your own scans).
3.  **MATERIALS**: Standardize shaders for your target engine.
4.  **VALIDATE**: Ensure no errors exist (Green status).
5.  **UV**: Generate final UVs and Lightmaps.
6.  **EXPORT**: Package for Unreal/Unity.

### Voice Control
Click the **Microphone** icon in the header and speak naturally:
*   *"Fix N-Gons"*
*   *"Scan Materials"*
*   *"Optimize and Export"*

---

## System Architecture

- **Core**: Python (FastAPI) + Trimesh + PyTorch.
- **Generative**: Shap-E (OpenAI), Trellis (Microsoft), Stable Diffusion.
- **Client**: PySide2/PySide6 (Maya Integration).
- **Web**: React + Next.js + Three.js.

---

*Powered by Qyntara Neural Core*
