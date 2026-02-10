# Qyntara AI: Future Roadmap & Use Cases

The current Qyntara AI architecture (Maya Client + Dockerized GPU Backend + PyTorch) opens the door to several industry-changing capabilities that go beyond simple validation.

## 1. Smart Scene Assembly & Layout
**Goal**: Assist artists in placing and aligning objects automatically.

*   **AI Auto-Layout**: 
    - Automatically arrange chairs around a table without intersections.
    - Snap books to shelves or appliances to counters using collision heuristics.
*   **Clash Resolution**: 
    - Advanced `geo_intersect` that not only detects but *resolves* clashes by moving objects apart.
*   **Detail Scatter**: 
    - Procedurally place small details (buttons, screws) on surface normals, avoiding "Floating Geometry".

## 5. Light Baking & Engine Integration
**Goal**: "Test before Export" - Simulate Unity/Unreal light baking within Maya.

*   **Bake Readiness Validation (Implemented)**:
    - Checks for Lightmap UVs (Set 2).
    - Checks for Overlapping UVs in Lightmap channel.
*   **Integrated Baker (Future)**:
    - **One-Click Bake**: A "Bake Lightmaps" button that triggers Arnold/Redshift bake-to-texture.
    - **GPU Lightmass Bridge**: Export scene to a headless Unreal instance (via Docker Worker) to bake lightmaps and return textures to Maya.
    - **Preview Mode**: Apply baked lightmaps to a custom "Preview Shader" in Maya viewport.

## 2. Advanced Lighting & Rendering Analysis
*   **Raytraced Light Leak Detection**: 
    - Use the GPU backend (PyTorch/OptiX) to cast rays from inside a "room" mesh.
    - If rays escape to the void (infinity) without hitting geometry, flag as a "Light Leak".
    - More accurate than the current "Unsealed Border" heuristic.
*   **Shadow Terminator Fix (Implemented)**: 
    - Detects smooth shading on sharp angles which causes shadow artifacts.
    - [x] Basic Heuristic (Soft Edges > 45 deg).
    - [ ] Advanced Normal Comparison (Requires OpenMaya).

## 3. Generative 3D Workflows
The current validation model checks for errors. The next phase is **Generation**.
*   **AI Auto-UV Packing**: Instead of just flagging overlaps, train a Reinforcement Learning (RL) agent to pack UVs into the [0,1] space with minimal wasted pixel space, running on the GPU backend.
*   **Neural LOD Generation**: Use `PyTorch3D` on the worker node to intelligently simplify high-poly meshes for game engines (LOD0 -> LOD3) while preserving silhouette better than standard decimation.

## 4. Semantic Asset Search
*   **Feature**: "Find me a chair that looks like *this* one."
*   **Implementation**: Use the **PointNet** architecture (already added in `models.py`) to generate "embedding vectors" for every mesh in your pipeline. Store these in a vector database (e.g., FAISS).
*   **Process**: Artists select a mesh in proper Maya, click "Find Similar", and the backend returns matching assets from the studio's entire history.

## 3. Intelligent Scan cleanup
*   **Feature**: One-click cleanup of Photogrammetry/LiDAR scans.
*   **Implementation**: A segmentation network (3D U-Net) running on the GPU worker can automatically label vertices as "Noise", "Ground", or "Object", and auto-delete the unwanted data.

## 4. Texture & Material AI
*   **Texture De-lighting**: Use a GAN (Generative Adversarial Network) on the backend to remove baked-in shadows from diffuse textures.
*   **Style Transfer**: Apply a standardized "Art Style" to textures using Neural Style Transfer, ensuring consistency across assets from different vendors.

## 5. Natural Language Scene Assembly
*   **Feature**: "Place 50 trees on the terrain but avoid the road."
*   **Implementation**: Integrate an LLM (Llama/GPT) into the backend. The user types a command, and the AI generates the specific `maya.cmds` Python script to execute the task, acting as a "Junior Technical Artist" helper.


## 6. Real-Time Collaboration Link
*   **Feature**: Sync scenes between Maya and Unreal Editor/Omniverse.
*   **Implementation**: Extend the `core/client.py` to use WebSockets. Changes in Maya (validated by Qyntara) are instantly pushed to a game engine session for immediate "in-context" review.

## 7. Next-Gen Validation (Implemented v2.0)
*   **Visual Diagnostics**: Viewport color-coding for errors (Red=Normals, Yellow=Geo, Purple=UVs).
*   **Auto-Fix Suite**: 
    - [x] Fix Zero-Length/Area geometry.
    - [x] Unify & Smooth Normals.
    - [x] Remove Lamina/Non-Manifold geometry.
    - [x] Auto-Snap Vertices (Proximity).
