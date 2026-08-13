"""
Maya Client UI Update - Quality Selector for LRM Integration
Adds quality dropdown to image-to-3D generation workflow

This script adds a quality selector (Draft/High) to the Maya client
for choosing between LRM (fast) and Trellis (quality) generation.
"""

import maya.cmds as cmds

try:
    from PySide2 import QtWidgets, QtCore
except ImportError:
    from PySide6 import QtWidgets, QtCore


def add_quality_selector_to_client():
    """
    Adds quality selector UI to Qyntara client.
    This can be integrated into the main client or run standalone.
    """
    
    # Create quality selector widget
    quality_group = QtWidgets.QGroupBox("Generation Quality")
    quality_group.setStyleSheet("""
        QGroupBox {
            background-color: #0f0f0f;
            border: 1px solid #333;
            border-radius: 6px;
            margin-top: 10px;
            padding: 15px;
            color: #00f3ff;
            font-weight: bold;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
    """)
    
    layout = QtWidgets.QVBoxLayout(quality_group)
    
    # Quality mode selector
    quality_label = QtWidgets.QLabel("Select Quality Mode:")
    quality_label.setStyleSheet("color: #ccc; font-size: 11px;")
    layout.addWidget(quality_label)
    
    quality_combo = QtWidgets.QComboBox()
    quality_combo.addItem("⚡ Draft (Fast - LRM)", "draft")
    quality_combo.addItem("💎 High (Quality - Trellis)", "high")
    quality_combo.setStyleSheet("""
        QComboBox {
            background-color: #1a1a1a;
            border: 1px solid #333;
            color: #fff;
            padding: 8px;
            border-radius: 4px;
            font-size: 12px;
        }
        QComboBox:hover {
            border-color: #00f3ff;
        }
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        QComboBox QAbstractItemView {
            background-color: #1a1a1a;
            color: #fff;
            selection-background-color: #00f3ff;
            selection-color: #000;
        }
    """)
    layout.addWidget(quality_combo)
    
    # Info labels
    info_layout = QtWidgets.QGridLayout()
    info_layout.setSpacing(5)
    
    # Draft info
    draft_label = QtWidgets.QLabel("Draft:")
    draft_label.setStyleSheet("color: #888; font-size: 10px;")
    draft_info = QtWidgets.QLabel("~20s, 200K faces, CPU-based")
    draft_info.setStyleSheet("color: #00f3ff; font-size: 10px;")
    info_layout.addWidget(draft_label, 0, 0)
    info_layout.addWidget(draft_info, 0, 1)
    
    # High info
    high_label = QtWidgets.QLabel("High:")
    high_label.setStyleSheet("color: #888; font-size: 10px;")
    high_info = QtWidgets.QLabel("2-5min, High detail, GPU-based")
    high_info.setStyleSheet("color: #bc13fe; font-size: 10px;")
    info_layout.addWidget(high_label, 1, 0)
    info_layout.addWidget(high_info, 1, 1)
    
    layout.addLayout(info_layout)
    
    return quality_group, quality_combo


def get_quality_setting(quality_combo):
    """Get the selected quality setting from the combo box"""
    return quality_combo.currentData()


# Example integration code for qyntara_client.py:
"""
# Add this to the __init__ method of QyntaraDockable class:

# Quality Selector (add after other UI elements)
self.quality_group, self.quality_combo = add_quality_selector_to_client()
# Add to appropriate layout (e.g., generate tab or vision tab)
# self.generate_layout.addWidget(self.quality_group)

# Modify the image-to-3D submission to include quality:
def submit_image_to_3d(self, image_path):
    quality = get_quality_setting(self.quality_combo)  # "draft" or "high"
    
    # Send to backend with quality parameter
    data = {
        "image_path": image_path,
        "quality": quality
    }
    
    # Make API call to /image-to-3d endpoint
    req = urllib.request.Request(f"{API_URL}/image-to-3d")
    req.add_header('Content-Type', 'application/json')
    req_data = json.dumps(data).encode('utf-8')
    
    with urllib.request.urlopen(req, req_data) as response:
        result = json.loads(response.read().decode('utf-8'))
        mesh_path = result.get('mesh_path')
        # Import mesh into Maya
        cmds.file(mesh_path, i=True)
"""

# Standalone test
if __name__ == "__main__":
    print("[Maya UI Update] Quality selector module loaded")
    print("[Maya UI Update] To integrate:")
    print("  1. Import this module in qyntara_client.py")
    print("  2. Call add_quality_selector_to_client() in UI setup")
    print("  3. Use get_quality_setting() when submitting jobs")
    print("")
    print("[Maya UI Update] Quality modes:")
    print("  - draft: Fast generation using LRM (~20s, CPU)")
    print("  - high: Quality generation using Trellis (2-5min, GPU)")
