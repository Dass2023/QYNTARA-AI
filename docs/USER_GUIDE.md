# Qyntara AI - User Guide

Welcome to **Qyntara AI**, a next-generation generative AI platform for 3D content creation. This system integrates advanced AI models (SAM, Shap-E) with a modern web interface and Autodesk Maya to streamline your 3D workflow.

## 🚀 Getting Started

### Prerequisites
- **GPU**: NVIDIA RTX 3070 Ti (or equivalent) with CUDA 12.x support.
- **Python**: 3.13.7 (in `venv_gpu`).
- **Node.js**: 18+ (for Frontend).

### Running the Application

1.  **Start the Backend (GPU Enabled)**:
    Open a terminal in `i:\QYNTARA AI` and run:
    ```powershell
    venv_gpu\Scripts\uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
    ```

2.  **Start the Frontend**:
    Open a new terminal in `i:\QYNTARA AI\frontend` and run:
    ```powershell
    npm run dev
    ```

3.  **Access the UI**:
    Open your browser (Chrome recommended) and navigate to: [http://localhost:3000](http://localhost:3000)

---

## 🎨 Features Guide

### 1. Create (Generative AI)
Generate 3D models from text or images.
- **Text-to-3D**: Enter a prompt (e.g., "a futuristic cyberpunk helmet") and click "Generate".
- **Image-to-3D**: Upload a reference image to generate a matching 3D model.
- **Chained Workflows**: Output from generation can be instantly sent to Remesh or UV tabs.

### 2. Inspect (3D Viewer)
Real-time WebGL viewer for your assets.
- **Live Viewport**: Rotate, zoom, and pan around your model.
- **Wireframe Mode**: Inspect topology quality.

### 3. Pipeline Tools (Remesh / UV / Material / Validate)
Access core Qyntara modules from the web.
- **Remesh**: Auto-retopology to target polycounts.
- **UV**: Generate clean UV maps directly in the cloud.
- **Material**: Convert simple colors to PBR materials.
- **Validate**: Run health checks on your generated assets.

### 4. SAM 3D (Segmentation)
Interactive 3D segmentation.
- **Point & Click**: Select parts of the mesh to isolate or label.
- **Export Masks**: Save segmentation masks for texturing.

### 5. Neural Analytics
Real-time telemetry of your AI production.
- **Metrics**: Track Total Polygons, AI Tokens, and Jobs processed.
- **Persistence**: Stats are saved automatically.

### 6. Artifact Library
Browse and manage your generated content.
- **History**: Access all previous jobs and download their outputs.

---

## 🔌 Maya Integration

Qyntara AI connects directly to Autodesk Maya.

### Installation
1.  Run the installer script:
    ```powershell
    python maya/install_client.py
    ```

### Usage in Maya
1.  Open Maya.
2.  Open the **Script Editor** (Python tab).
3.  Run the following code:
    ```python
    import qyntara_client
    qyntara_client.show()
    ```
4.  The **Qyntara Dashboard** will appear.

### ✨ Maya Client Features (v4.0 - Master Spec)

The Qyntara Client has been overhauled into a professional 6-tab production suite.

#### **1. GENERATE AI ASSIST (Tab 1)**
Create 3D assets from text prompts or images.
- **🚀 AUTO FULL PIPELINE**: One-click automation button that runs the entire chain: *Generate → Remesh → UV → Material → Validate → Export*.
- **Style Matrix**: Select from Cyberpunk, Organic, Hard Surface, or Low Poly styles.
- **Quality**: Draft (Fast) or High Fidelity (Slow).

#### **2. QUAD REMESH (Tab 2)**
Universal auto-retopology tool.
- **Presets**: Game (2k), Film (20k), Hero (50k).
- **Target Count**: Slider control for precise polygon budgets.
- **Symmetry**: X/Y/Z axis symmetry support.

#### **3. MATERIALS AI (Tab 3)**
Complete material synthesis and conversion suite.
- **Scanner**: Analyzes scene materials and identifies shader types.
- **Swapper**: Batch convert materials (e.g., "All Standard → Unreal M_Master").
- **Texture Intelligence**: AI Super-Resolution (2x/4x) and PBR Map Generation (Normal/Roughness from Albedo).

#### **4. VALIDATE SCENE (Tab 4)**
TD-Grade Quality Assurance.
- **Engine Profiles**: Check against Unreal, Unity, or Mobile constraints.
- **Heatmap**: Visualize errors directly on the mesh with vertex color overlays.
- **Auto-Fix**: One-click resolution for N-Gons, History, Transforms, and Naming issues.

#### **5. UNIVERSAL UV (Tab 5)**
Next-gen UV unwrapping and packing.
- **Auto Seams**: AI-driven seam placement for organic and hard-surface models.
- **Lightmap Generation**: Dedicated UV2 generation with zero overlap for baking.
- **Dual Channel**: Generate unified assets with Texture UVs (channel 0) and Lightmap UVs (channel 1).

#### **6. OPTIMIZATION & EXPORT (Tab 6)**
Final delivery tools.
- **LOD Generation**: Auto-create LOD0, LOD1, LOD2 chains.
- **Format**: Export as OBJ, FBX, or USD.
- **Move Pivot**: Auto-center pivot to bottom for game engine snapping.

#### **🎤 Voice Command Center**
Click the Microphone icon in the header to control Qyntara with voice.
- "Fix N-Gons"
- "Scan Materials"
- "Check Scene"
- "Optimize and Export"

---

## 🛠️ Troubleshooting

- **Backend won't start?** Ensure you are using `venv_gpu` and that no other process is using port 8000.
- **GPU not detected?** Run `nvidia-smi` to check your driver status.
- **Agent says "Offline"?** Check that your `OPENAI_API_KEY` is set correctly.
- **Image-to-3D output is .ply instead of .glb?** This happens if the NVIDIA CUDA Toolkit is not installed. The system falls back to generating 3D Gaussians (.ply). Install the CUDA Toolkit 11.8 to enable mesh extraction (.glb).

---

*Generated by Qyntara AI Team*
