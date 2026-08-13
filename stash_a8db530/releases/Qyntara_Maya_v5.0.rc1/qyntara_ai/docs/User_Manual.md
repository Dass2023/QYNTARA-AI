# Qyntara AI - User Manual

## Introduction
Qyntara AI is your intelligent assistant for validating and repairing 3D scenes in Maya. It helps you catch common issues like open edges, overlapping UVs, and incorrect scaling before you export to game engines or render.

## Getting Started

### Launching the Tool
1. Open Maya.
2. Click the **QValidator** button on your **Qyntara** shelf.
3. If the shelf is missing, run the following in a Python script editor tab:
   ```python
   import qyntara_ai.ui.main_window as gui
   gui.show()
   ```

## Using the Validator
1. **Select Objects**: Select the meshes or groups you want to check. If nothing is selected, the tool will ask to check the entire scene.
2. **Run Validation**: Click the blue **Run Validation** button.
3. **Review Results**:
   - **Green**: Passed.
   - **Orange**: Warning (e.g. Naming convention).
   - **Red**: Error (e.g. Open Edges, UV Overlaps).
4. **See Details**: Click **Show Report** to see a detailed JSON log of every violation.

### Available Checks
Qyntara AI currently supports:
- **Geometry**: Open Edges, Non-Manifold, Lamina Faces, N-gons, **Degenerate Faces** (Zero Area), **Coinciding Meshes**.
- **Transforms**: Incorrect Scale (frozen), **Scene Units** (cm/m verification), **Up-Axis**.
- **UVs**: Overlaps, **UV Bounds** (UDIM range), Flipped UVs.
- **Naming**: Regex-based naming convention.
- **Materials**: Default material usage.

## Auto-Fix (AI)
If issues are found, the **Auto-Fix** button will enable.
1. Click **Auto-Fix**.
2. Qyntara AI will analyze the errors and generate Python scripts to fix them.
3. A dialog will show the proposed scripts.
4. Click **Execute** to run them (Note: Always save your scene before auto-fixing!).

## Configuration
You can toggle specific rules on/off using the checkboxes in the rules list.
