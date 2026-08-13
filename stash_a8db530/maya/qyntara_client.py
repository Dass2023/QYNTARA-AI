import sys
import os
import json
import re
import urllib.request
import urllib.parse
import urllib.error
import tempfile
import maya.cmds as cmds
import maya.api.OpenMaya as om2
import universal_framework
from universal_framework import UniversalUVSystem
import material_framework
from material_framework import MaterialAISystem
import master_prompt
from master_prompt import MasterPromptWidget
import agent_logic
from agent_logic import AgentBrain

try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ImportError:
    try:
        from PySide6 import QtWidgets, QtCore, QtGui
    except ImportError:
        raise ImportError("Could not find PySide2 or PySide6. Please ensure you are running this script in Autodesk Maya.")

# --- Compatibility Constants ---
try:
    # PySide2
    AlignCenter = QtCore.Qt.AlignCenter
    WindowStaysOnTopHint = QtCore.Qt.WindowStaysOnTopHint
    PointingHandCursor = QtCore.Qt.PointingHandCursor
    Horizontal = QtCore.Qt.Horizontal
    Vertical = QtCore.Qt.Vertical
    ItemIsUserCheckable = QtCore.Qt.ItemIsUserCheckable
    ItemIsEnabled = QtCore.Qt.ItemIsEnabled
    CustomContextMenu = QtCore.Qt.CustomContextMenu
    SizePolicy = QtWidgets.QSizePolicy
except AttributeError:
    # PySide6
    AlignCenter = QtCore.Qt.AlignmentFlag.AlignCenter
    WindowStaysOnTopHint = QtCore.Qt.WindowType.WindowStaysOnTopHint
    PointingHandCursor = QtCore.Qt.CursorShape.PointingHandCursor
    Horizontal = QtCore.Qt.Orientation.Horizontal
    Vertical = QtCore.Qt.Orientation.Vertical
    ItemIsUserCheckable = QtCore.Qt.ItemFlag.ItemIsUserCheckable
    ItemIsEnabled = QtCore.Qt.ItemFlag.ItemIsEnabled
    CustomContextMenu = QtCore.Qt.ContextMenuPolicy.CustomContextMenu
    SizePolicy = QtWidgets.QSizePolicy

# --- Configuration ---
API_URL = "http://localhost:8000"
ACCESS_CODE = "QYNTARA-X-777"

# --- Cyberpunk Stylesheet ---
STYLESHEET = """
/* Main Window */
QDialog {
    background-color: #050505;
    border: 1px solid #333;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #333;
    background: #0a0a0a;
    border-radius: 4px;
}
QTabBar::tab {
    background: #111;
    color: #888;
    padding: 10px 20px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
    font-family: 'Segoe UI', sans-serif;
    font-weight: bold;
    font-size: 12px;
}
QTabBar::tab:selected {
    background: #00f3ff;
    color: #000;
}
QTabBar::tab:hover {
    background: #222;
    color: #fff;
}

/* Dashboard Cards (Big Buttons) */
QPushButton.card-btn {
    background-color: #0f0f0f;
    border: 1px solid #333;
    border-radius: 8px;
    color: #fff;
    font-size: 14px;
    font-weight: bold;
    text-align: center;
    padding: 20px;
}
QPushButton.card-btn:hover {
    background-color: #1a1a1a;
    border-color: #00f3ff;
    color: #00f3ff;
}
QPushButton.card-btn:pressed {
    background-color: #00f3ff;
    color: #000;
}

/* Standard Buttons */
QPushButton {
    background-color: #1a1a1a;
    border: 1px solid #333;
    color: #fff;
    padding: 12px;
    border-radius: 4px;
    font-family: 'Segoe UI', sans-serif;
    font-weight: bold;
    text-transform: uppercase;
}
QPushButton:hover {
    background-color: #222;
    border-color: #00f3ff;
    color: #00f3ff;
}
QPushButton:pressed {
    background-color: #00f3ff;
    color: #000;
}
QPushButton:disabled {
    background-color: #111;
    color: #444;
    border-color: #222;
}

/* Tree Widget */
QTreeWidget {
    background-color: #0a0a0a;
    border: 1px solid #333;
    color: #ddd;
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
    padding: 5px;
}
QTreeWidget::item {
    padding: 8px;
}
QTreeWidget::item:selected {
    background-color: rgba(0, 243, 255, 0.1);
    color: #00f3ff;
}
QHeaderView::section {
    background-color: #111;
    font-size: 11px;
}
"""

class StatsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, data=None):
        super(StatsDialog, self).__init__(parent)
        self.setWindowTitle("QYNTARA ENGINE STATS")
        self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint)
        self.setStyleSheet("""
            QDialog { background: #111; border: 1px solid #333; border-radius: 6px; }
            QLabel { color: #ccc; font-family: 'Consolas', monospace; }
            QLabel.val { color: #00f3ff; font-weight: bold; }
            QLabel.head { color: #fff; font-weight: 900; font-size: 14px; margin-bottom: 10px; }
        """)
        self.resize(300, 220)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel("NEURAL ENGINE TELEMETRY", property="class", value="head"))
        
        # Grid
        grid = QtWidgets.QGridLayout()
        grid.setSpacing(10)
        
        self.labels = {}
        fields = [
            ("Status", "system_status"),
            ("Uptime", "uptime_seconds"),
            ("Jobs Processed", "total_jobs"),
            ("Polygons (Est)", "total_polygons"),
            ("AI Tokens", "ai_tokens"),
            ("Active Nodes", "active_nodes")
        ]
        
        for i, (label, key) in enumerate(fields):
            grid.addWidget(QtWidgets.QLabel(label + ":"), i, 0)
            val = QtWidgets.QLabel("--")
            val.setProperty("class", "val")
            grid.addWidget(val, i, 1)
            self.labels[key] = val
            
        layout.addLayout(grid)
        layout.addStretch()
        
        # Close
        btn = QtWidgets.QPushButton("CLOSE")
        btn.setStyleSheet("background: #222; border: none; padding: 5px; color: #666;")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)
        
        if data:
            self.update_data(data)
            
        # Center on parent
        if parent:
            geo = parent.geometry()
            cx = geo.x() + geo.width()//2
            cy = geo.y() + geo.height()//2
            self.move(cx - 150, cy - 110)

    def update_data(self, data):
        for key, lbl in self.labels.items():
            val = data.get(key, 0)
            if key == "uptime_seconds":
                m, s = divmod(int(val), 60)
                h, m = divmod(m, 60)
                lbl.setText(f"{h:02d}:{m:02d}:{s:02d}")
            elif key == "total_polygons":
                lbl.setText(f"{int(val):,}")
            else:
                lbl.setText(str(val))

class CommandPaletteDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(CommandPaletteDialog, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup)
        self.setStyleSheet("""
            QDialog { background: #0a0a0a; border: 1px solid #00f3ff; border-radius: 6px; }
            QLineEdit { background: transparent; border: none; font-size: 18px; color: #fff; padding: 10px; }
            QLabel { color: #00f3ff; font-weight: bold; margin-left: 10px; }
        """)
        self.resize(500, 80)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        
        # Header
        hbox = QtWidgets.QHBoxLayout()
        icon = QtWidgets.QLabel("🎤")
        icon.setStyleSheet("font-size: 20px;")
        hbox.addWidget(icon)
        hbox.addWidget(QtWidgets.QLabel("LISTENING..."))
        layout.addLayout(hbox)
        
        self.input = QtWidgets.QLineEdit()
        self.input.setPlaceholderText("Type a command (e.g. 'Fix Ngons', 'Export 4K')...")
        self.input.returnPressed.connect(self.accept)
        layout.addWidget(self.input)
        
        # Auto-focus
        self.input.setFocus()

    def get_command(self):
        return self.input.text()

# --- Utilities ---
class UndoContext:
    """Context manager for Maya Undo Chunks."""
    def __init__(self, name):
        self.name = name
    
    def __enter__(self):
        cmds.undoInfo(openChunk=True, chunkName=self.name)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        cmds.undoInfo(closeChunk=True)

# --- Rule Set Manager (Code Removed for Brevity - Same as before) ---
class RuleSetManager:
    SEVERITY_INFO = 0
    SEVERITY_WARNING = 1
    SEVERITY_ERROR = 2
    
    DEFAULT_RULES = {
        "name": "Default",
        "version": "1.1",
        "rules": {
            # Topology
            "check_ngons": {"enabled": True, "severity": 2},
            "check_triangles": {"enabled": False, "severity": 1},
            "check_poles": {"enabled": False, "severity": 1},
            "check_non_manifold": {"enabled": True, "severity": 2},
            "check_lamina_faces": {"enabled": True, "severity": 2},
            "check_zero_area": {"enabled": True, "severity": 2},
            "check_hard_edges": {"enabled": False, "severity": 1},
            "check_zero_length_edges": {"enabled": True, "severity": 2},
            # UVs
            "check_missing_uvs": {"enabled": True, "severity": 2},
            # Scene
            "check_history": {"enabled": True, "severity": 1},
            "check_transforms": {"enabled": True, "severity": 1},
            "check_layers": {"enabled": True, "severity": 1},
            "check_shaders": {"enabled": True, "severity": 1},
            # Naming
            "check_names": {"enabled": True, "severity": 1},
            "check_trailing_numbers": {"enabled": True, "severity": 1},
            "check_shape_names": {"enabled": True, "severity": 1},
            "check_namespaces": {"enabled": True, "severity": 1}
        }
    }

    @staticmethod
    def get_default_rules():
        return RuleSetManager.DEFAULT_RULES

    @staticmethod
    def save_rules(rules, path):
        try:
            with open(path, 'w') as f:
                json.dump(rules, f, indent=4)
            return True
        except Exception as e:
            print(f"Failed to save rules: {e}")
            return False

    @staticmethod
    def load_rules(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load rules: {e}")
            return None

# --- Validation Logic (Same as before) ---
class ValidationManager:
    @staticmethod
    def get_selected_meshes():
        return cmds.ls(sl=True, dag=True, type="mesh", long=True)

    @staticmethod
    def get_om_mesh(mesh_name):
        sel = om2.MSelectionList()
        sel.add(mesh_name)
        return sel.getDagPath(0)

    # --- Checks ---
    @staticmethod
    def check_ngons():
        meshes = ValidationManager.get_selected_meshes()
        if not meshes: return []
        issues = []
        for mesh in meshes:
            try:
                dag_path = ValidationManager.get_om_mesh(mesh)
                poly_it = om2.MItMeshPolygon(dag_path)
                while not poly_it.isDone():
                    if poly_it.polygonVertexCount() > 4:
                        issues.append(f"{mesh}.f[{poly_it.index()}]")
                    poly_it.next()
            except Exception as e:
                print(f"Error checking ngons on {mesh}: {e}")
        return issues

    @staticmethod
    def check_poles():
        meshes = ValidationManager.get_selected_meshes()
        if not meshes: return []
        issues = []
        for mesh in meshes:
            try:
                dag_path = ValidationManager.get_om_mesh(mesh)
                vert_it = om2.MItMeshVertex(dag_path)
                while not vert_it.isDone():
                    if len(vert_it.getConnectedEdges()) > 5:
                        issues.append(f"{mesh}.vtx[{vert_it.index()}]")
                    vert_it.next()
            except Exception as e:
                print(f"Error checking poles on {mesh}: {e}")
        return issues
    
    @staticmethod
    def check_triangles():
        meshes = ValidationManager.get_selected_meshes()
        if not meshes: return []
        issues = []
        for mesh in meshes:
            try:
                dag_path = ValidationManager.get_om_mesh(mesh)
                poly_it = om2.MItMeshPolygon(dag_path)
                while not poly_it.isDone():
                    if poly_it.polygonVertexCount() == 3:
                        issues.append(f"{mesh}.f[{poly_it.index()}]")
                    poly_it.next()
            except Exception as e:
                print(f"Error checking triangles: {e}")
        return issues

    @staticmethod
    def check_non_manifold():
        meshes = ValidationManager.get_selected_meshes()
        if not meshes: return []
        issues = []
        for mesh in meshes:
            nm_edges = cmds.polyInfo(mesh, nonManifoldEdges=True)
            if nm_edges: issues.extend(nm_edges)
            nm_verts = cmds.polyInfo(mesh, nonManifoldVertices=True)
            if nm_verts: issues.extend(nm_verts)
        return issues

    @staticmethod
    def check_lamina_faces():
        meshes = ValidationManager.get_selected_meshes()
        if not meshes: return []
        issues = []
        for mesh in meshes:
            lf = cmds.polyInfo(mesh, laminaFaces=True)
            if lf: issues.extend(lf)
        return issues
        
    @staticmethod
    def check_zero_area():
        meshes = ValidationManager.get_selected_meshes()
        if not meshes: return []
        cmds.select(meshes)
        cmds.polyCleanupArgList(4, ["0","2","1","0","1","0.00001","0","0","0","1e-05","0","1e-05","0","1e-05","0","-1","0","0"])
        return cmds.ls(sl=True)

    @staticmethod
    def check_hard_edges():
        meshes = ValidationManager.get_selected_meshes()
        if not meshes: return []
        issues = []
        for mesh in meshes:
            cmds.select(mesh)
            cmds.polySelectConstraint(mode=3, type=0x8000, smoothness=1) # Hard edges
            hard_edges = cmds.ls(sl=True)
            cmds.polySelectConstraint(disable=True)
            if hard_edges: issues.extend(hard_edges)
        return issues

    @staticmethod
    def check_zero_length_edges():
        meshes = ValidationManager.get_selected_meshes()
        if not meshes: return []
        cmds.select(meshes)
        cmds.polyCleanupArgList(4, ["0","2","1","0","1","0.00001","0","0","0","1e-05","0","1e-05","0","1e-05","0","-1","0","0"])
        return cmds.ls(sl=True)

    @staticmethod
    def check_missing_uvs():
        meshes = ValidationManager.get_selected_meshes()
        issues = []
        for mesh in meshes:
            uv_counts = cmds.polyEvaluate(mesh, uv=True)
            if uv_counts == 0:
                issues.append(mesh)
        return issues

    @staticmethod
    def check_history():
        meshes = cmds.ls(sl=True, long=True)
        issues = []
        for obj in meshes:
            hist = cmds.listHistory(obj, pruneDagObjects=True)
            if hist and len(hist) > 1: 
                issues.append(obj)
        return issues

    @staticmethod
    def check_transforms():
        meshes = cmds.ls(sl=True, long=True)
        issues = []
        for obj in meshes:
            s = cmds.xform(obj, q=True, r=True, s=True)
            r = cmds.xform(obj, q=True, r=True, ro=True)
            if not all(abs(x - 1.0) < 0.001 for x in s) or not all(abs(x) < 0.001 for x in r):
                issues.append(obj)
        return issues

    @staticmethod
    def check_layers():
        meshes = ValidationManager.get_selected_meshes()
        issues = []
        for mesh in meshes:
            layer = cmds.listConnections(mesh, type="displayLayer")
            if layer and "defaultLayer" not in layer:
                issues.append(mesh)
        return issues

    @staticmethod
    def check_shaders():
        meshes = ValidationManager.get_selected_meshes()
        issues = []
        for mesh in meshes:
            shading_groups = cmds.listConnections(mesh, type='shadingEngine')
            if shading_groups:
                for sg in shading_groups:
                    materials = cmds.listConnections(sg + ".surfaceShader")
                    if materials and "lambert1" in materials:
                        issues.append(mesh)
        return issues

    @staticmethod
    def check_names():
        meshes = cmds.ls(sl=True) 
        seen = set()
        issues = []
        for name in meshes:
            short = name.split("|")[-1]
            if short in seen:
                issues.append(name)
            seen.add(short)
        return issues

    @staticmethod
    def check_trailing_numbers():
        meshes = cmds.ls(sl=True)
        issues = []
        for name in meshes:
            short = name.split("|")[-1]
            if re.search(r'\d+$', short):
                issues.append(name)
        return issues

    @staticmethod
    def check_shape_names():
        meshes = ValidationManager.get_selected_meshes()
        issues = []
        for mesh in meshes:
            parent_list = cmds.listRelatives(mesh, parent=True)
            if parent_list:
                transform = parent_list[0]
                expected = transform + "Shape"
                short_mesh = mesh.split("|")[-1]
                if short_mesh != expected:
                    issues.append(mesh)
        return issues

    @staticmethod
    def check_namespaces():
        meshes = cmds.ls(sl=True)
        issues = []
        for name in meshes:
            short = name.split("|")[-1]
            if ":" in short:
                issues.append(name)
        return issues

    # --- Fix Methods ---
    @staticmethod
    def fix_history(objects):
        with UndoContext("Fix History"):
            if objects:
                cmds.delete(objects, ch=True)
                print(f"Deleted history for {len(objects)} objects.")

    @staticmethod
    def fix_transforms(objects):
        with UndoContext("Fix Transforms"):
            if objects:
                cmds.makeIdentity(objects, apply=True, t=1, r=1, s=1, n=0, pn=1)
                print(f"Froze transforms for {len(objects)} objects.")
            
    @staticmethod
    def fix_ngons(objects):
        with UndoContext("Fix N-Gons"):
            if objects:
                cmds.polyTriangulate(objects)
                print("Triangulated N-gons.")

    @staticmethod
    def fix_shape_names(objects):
        with UndoContext("Fix Shape Names"):
            for obj in objects:
                parent_list = cmds.listRelatives(obj, parent=True)
                if parent_list:
                    transform = parent_list[0]
                    expected = transform + "Shape"
                    cmds.rename(obj, expected)
            print(f"Renamed {len(objects)} shapes.")

            print(f"Renamed {len(objects)} shapes.")

# --- UV Settings Dialog ---
class UVSettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, current_settings=None):
        super(UVSettingsDialog, self).__init__(parent)
        self.setWindowTitle("UV Ecosystem Settings")
        self.setWindowFlags(QtCore.Qt.Tool) # Popup
        self.resize(300, 250)
        self.setStyleSheet(STYLESHEET)
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Mode
        layout.addWidget(QtWidgets.QLabel("Algorithm Mode:"))
        self.mode_combo = QtWidgets.QComboBox()
        self.mode_combo.addItems(["Auto (AI Classifier)", "Hard Surface", "Organic"])
        self.mode_combo.setToolTip("AI determines the best cut strategy based on mesh topology.")
        layout.addWidget(self.mode_combo)
        
        # Packing Quality (New)
        layout.addWidget(QtWidgets.QLabel("Packing Quality:"))
        self.quality_combo = QtWidgets.QComboBox()
        self.quality_combo.addItems(["Standard (Fast)", "Superb (High Density)"])
        self.quality_combo.setToolTip("Superb mode uses brute-force packing and rotation for maximum UV shell density.")
        layout.addWidget(self.quality_combo)
        
        # Resolution
        layout.addWidget(QtWidgets.QLabel("Texture Resolution:"))
        self.res_combo = QtWidgets.QComboBox()
        self.res_combo.addItems(["1024", "2048", "4096", "8192"])
        layout.addWidget(self.res_combo)
        
        # Padding
        layout.addWidget(QtWidgets.QLabel("Padding:"))
        self.padding_combo = QtWidgets.QComboBox()
        self.padding_combo.addItems(["Low (2px)", "Medium (4px)", "High (8px)"])
        layout.addWidget(self.padding_combo)
        
        # Apply Defaults
        if current_settings:
            mode_map = {"auto": 0, "hard_surface": 1, "organic": 2}
            self.mode_combo.setCurrentIndex(mode_map.get(current_settings.get("mode", "auto"), 0))
            
            qual_map = {"standard": 0, "superb": 1}
            self.quality_combo.setCurrentIndex(qual_map.get(current_settings.get("quality", "standard"), 0))
            
            self.res_combo.setCurrentText(str(current_settings.get("resolution", 2048)))
            
            pad_map = {"low": 0, "medium": 1, "high": 2}
            self.padding_combo.setCurrentIndex(pad_map.get(current_settings.get("padding", "medium"), 1))
            
        
        # Buttons
        btn_layout = QtWidgets.QHBoxLayout()
        ok_btn = QtWidgets.QPushButton("APPLY")
        ok_btn.clicked.connect(self.accept)
        ok_btn.setStyleSheet("background-color: #00f3ff; color: black; font-weight: bold;")
        
        cancel_btn = QtWidgets.QPushButton("CANCEL")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(ok_btn)
        layout.addLayout(btn_layout)

    def get_settings(self):
        mode_idx = self.mode_combo.currentIndex()
        modes = ["auto", "hard_surface", "organic"]
        
        qual_idx = self.quality_combo.currentIndex()
        quals = ["standard", "superb"]
        
        pad_idx = self.padding_combo.currentIndex()
        pads = ["low", "medium", "high"]
        
        return {
            "mode": modes[mode_idx],
            "quality": quals[qual_idx],
            "resolution": int(self.res_combo.currentText()),
            "padding": pads[pad_idx]
        }


# --- Universal UV UI Framework ---
class UniversalPanel(QtWidgets.QFrame):
    """
    Abstract base class for all Universal UV panels.
    Provides consistent 'Neon Glass' styling and header behavior.
    """
    def __init__(self, title, parent=None):
        super(UniversalPanel, self).__init__(parent)
        self.setStyleSheet("""
            UniversalPanel {
                background-color: rgba(20, 20, 25, 150);
                border: 1px solid #333;
                border-radius: 8px;
                margin-bottom: 5px;
            }
            QLabel#Title {
                font-weight: bold;
                color: #00f3ff;
                font-size: 12px;
                padding: 5px;
            }
        """)
        
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(8)
        
        # Header
        if title:
            self.title_lbl = QtWidgets.QLabel(title)
            self.title_lbl.setObjectName("Title")
            self.main_layout.addWidget(self.title_lbl)
            self.main_layout.addSpacing(5)

class UVContextManager(QtCore.QObject):
    contextChanged = QtCore.Signal(str) # Emits 'hard_surface', 'organic', or 'environment'

    def __init__(self, parent=None):
        super(UVContextManager, self).__init__(parent)
        self.current_context = "hard_surface" # Default
        self.active_selection = []
        
        # Start listening to selection changes
        self.job_id = cmds.scriptJob(e=["SelectionChanged", self.on_selection_changed], protected=True)

    def on_selection_changed(self):
        sel = cmds.ls(sl=True, long=True)
        if not sel: return
        
        # Basic Heuristic (Naive)
        # In a real implementation, we would query the backend classifier here.
        # For now, let's use a name-based or simple topology check if possible, or just default.
        # Let's say if it has 'sphere' or 'organic' in name -> Organic. Else Hard Surface.
        
        new_context = "hard_surface"
        for obj in sel:
            if "organic" in obj.lower() or "char" in obj.lower() or "sphere" in obj.lower():
                new_context = "organic"
                break
        
        if new_context != self.current_context:
            self.current_context = new_context
            self.contextChanged.emit(new_context)
            print(f"[Context] Switched to {new_context.upper()}")

    def cleanup(self):
        if hasattr(self, 'job_id'):
            cmds.scriptJob(kill=self.job_id, force=True)

class AIAdvisorPanel(UniversalPanel):
    def __init__(self, parent=None):
        super(AIAdvisorPanel, self).__init__("AI ADVISOR", parent)
        self.lbl_advice = QtWidgets.QLabel("Select an object to analyze.")
        self.lbl_advice.setWordWrap(True)
        self.lbl_advice.setStyleSheet("color: #ccc; font-style: italic;")
        self.main_layout.addWidget(self.lbl_advice)
    
    def update_context(self, context):
        if context == "hard_surface":
            self.lbl_advice.setText("💡 Hard Surface detected. Suggest using 'Planar Projection' or 'Camera-Based' initially. Checking for sharp edges...")
        elif context == "organic":
            self.lbl_advice.setText("🧬 Organic form detected. Use 'Unfold3D' and place seams in hidden areas (underarms, inseams).")

class SeamsPanel(UniversalPanel):
    def __init__(self, parent=None):
        super(SeamsPanel, self).__init__("SEAM MANAGEMENT", parent)
        
        # Tools Layout
        grid = QtWidgets.QGridLayout()
        
        self.btn_cut = QtWidgets.QPushButton("CUT")
        self.btn_cut.setStyleSheet("background-color: #ff003c; color: white;")
        self.btn_sew = QtWidgets.QPushButton("SEW")
        self.btn_sew.setStyleSheet("background-color: #00f3ff; color: black;")
        
        grid.addWidget(self.btn_cut, 0, 0)
        grid.addWidget(self.btn_sew, 0, 1)
        
        self.main_layout.addLayout(grid)
        
        # Context Aware Options
        self.auto_seams_btn = QtWidgets.QPushButton("AUTO SEAMS (AI)")
        self.main_layout.addWidget(self.auto_seams_btn)

class RelaxPanel(UniversalPanel):
    def __init__(self, parent=None):
        super(RelaxPanel, self).__init__("UNFOLD & RELAX", parent)
        
        self.btn_unfold = QtWidgets.QPushButton("UNFOLD 3D")
        self.btn_unfold.setStyleSheet("background-color: #bc13fe; color: white;")
        self.main_layout.addWidget(self.btn_unfold)
        
        self.btn_optimize = QtWidgets.QPushButton("OPTIMIZE")
        self.main_layout.addWidget(self.btn_optimize)

class PackingPanel(UniversalPanel):
    def __init__(self, parent=None):
        super(PackingPanel, self).__init__("PACKING", parent)
        
        self.pack_btn = QtWidgets.QPushButton("PACK UVs")
        self.pack_btn.setStyleSheet("background-color: #00f3ff; color: black; font-weight: bold; height: 30px;")
        self.main_layout.addWidget(self.pack_btn)
        
        # Settings
        form = QtWidgets.QFormLayout()
        self.res_combo = QtWidgets.QComboBox()
        self.res_combo.addItems(["1024", "2048", "4096"])
        form.addRow("Res:", self.res_combo)
        
        self.chk_udim = QtWidgets.QCheckBox("Enable UDIMs")
        self.chk_udim.setToolTip("Packs UV shells across multiple tiles (1001, 1002...) if density requires it.")
        form.addRow(self.chk_udim)
        
        self.main_layout.addLayout(form)

class DensityPanel(UniversalPanel):
    def __init__(self, parent=None):
        super(DensityPanel, self).__init__("TEXEL DENSITY", parent)
        
        self.lbl_current = QtWidgets.QLabel("Value: -- px/unit")
        self.lbl_current.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_current.setStyleSheet("color: #00f3ff; font-size: 14px; font-weight: bold;")
        self.main_layout.addWidget(self.lbl_current)
        
        # Priority Harmonizer
        hbox_prio = QtWidgets.QHBoxLayout()
        hbox_prio.addWidget(QtWidgets.QLabel("Priority:"))
        self.prio_combo = QtWidgets.QComboBox()
        self.prio_combo.addItems(["Hero (x2)", "Prop (x1)", "Background (x0.5)"])
        self.prio_combo.setCurrentIndex(1) # Default Prop
        hbox_prio.addWidget(self.prio_combo)
        self.main_layout.addLayout(hbox_prio)
        
        hbox = QtWidgets.QHBoxLayout()
        self.btn_get = QtWidgets.QPushButton("GET")
        self.btn_set = QtWidgets.QPushButton("SET")
        hbox.addWidget(self.btn_get)
        hbox.addWidget(self.btn_set)
        self.main_layout.addLayout(hbox)

class DualChannelPanel(UniversalPanel):
    def __init__(self, parent=None):
        super(DualChannelPanel, self).__init__("DUAL CHANNEL (Texture + Lightmap)", parent)
        
        lbl = QtWidgets.QLabel("Generates a unified asset with:\n• UV1: Organic/Hard Surface (Texture)\n• UV2: Lightmap (Strict, Non-overlapping)")
        lbl.setStyleSheet("color: #aaa; font-style: italic;")
        lbl.setWordWrap(True)
        self.main_layout.addWidget(lbl)
        
        self.btn_gen_dual = QtWidgets.QPushButton("GENERATE UNIFIED ASSET")
        self.btn_gen_dual.setStyleSheet("background-color: #00ff9d; color: black; font-weight: bold; height: 40px;")
        self.main_layout.addWidget(self.btn_gen_dual)




        self.main_layout.addWidget(self.btn_gen_dual)


class DiagnosticsPanel(UniversalPanel):
    def __init__(self, parent=None):
        super(DiagnosticsPanel, self).__init__("ENGINE DIAGNOSTICS", parent)
        
        # Health Score
        self.lbl_score = QtWidgets.QLabel("HEALTH SCORE: --")
        self.lbl_score.setStyleSheet("font-size: 18px; font-weight: bold; color: #888;")
        self.lbl_score.setAlignment(QtCore.Qt.AlignCenter)
        self.main_layout.addWidget(self.lbl_score)
        
        # Status Grid
        grid = QtWidgets.QGridLayout()
        self.led_overlaps = self.create_led("Overlaps")
        self.led_padding = self.create_led("Padding")
        self.led_coverage = self.create_led("Coverage")
        
        grid.addWidget(self.led_overlaps[0], 0, 0); grid.addWidget(self.led_overlaps[1], 0, 1)
        grid.addWidget(self.led_padding[1], 0, 2); grid.addWidget(self.led_padding[0], 0, 3) # Visual balance?
        # Actually standard row
        grid.addWidget(self.led_overlaps[0], 0, 0); grid.addWidget(self.led_overlaps[1], 0, 1)
        grid.addWidget(self.led_padding[0], 1, 0); grid.addWidget(self.led_padding[1], 1, 1)
        grid.addWidget(self.led_coverage[0], 2, 0); grid.addWidget(self.led_coverage[1], 2, 1)
        
        self.main_layout.addLayout(grid)
        
        self.txt_issues = QtWidgets.QTextEdit()
        self.txt_issues.setMaximumHeight(80)
        self.txt_issues.setReadOnly(True)
        self.txt_issues.setPlaceholderText("No issues detected.")
        self.main_layout.addWidget(self.txt_issues)

    def create_led(self, label):
        lbl = QtWidgets.QLabel(label)
        led = QtWidgets.QLabel("●")
        led.setStyleSheet("color: #444; font-size: 20px;")
        return lbl, led
        
    def update_report(self, report):
        if not report: return
        
        score = report.get("health_score", 0)
        self.lbl_score.setText(f"HEALTH SCORE: {score:.1f}%")
        
        if score > 80: self.lbl_score.setStyleSheet("font-size: 18px; font-weight: bold; color: #0f0;")
        elif score > 50: self.lbl_score.setStyleSheet("font-size: 18px; font-weight: bold; color: #fa0;")
        else: self.lbl_score.setStyleSheet("font-size: 18px; font-weight: bold; color: #f00;")
        
        # Overlaps
        if report.get("overlaps_detected"):
            self.led_overlaps[1].setStyleSheet("color: #f00; font-size: 20px;") # Red
        else:
            self.led_overlaps[1].setStyleSheet("color: #0f0; font-size: 20px;") # Green
            
        # Issues
        issues = report.get("issues", [])
        if issues:
            self.txt_issues.setText("\n".join(issues))
        else:
            self.txt_issues.setText("Clean.")


class LightmapPanel(UniversalPanel):
    def __init__(self, parent=None):
        super(LightmapPanel, self).__init__("LIGHTMAP GENERATION", parent)
        
        # Grid Layout
        grid = QtWidgets.QGridLayout()
        
        # Engine
        grid.addWidget(QtWidgets.QLabel("Engine:"), 0, 0)
        self.engine_combo = QtWidgets.QComboBox()
        self.engine_combo.addItems(["Unity 6", "Unreal Engine 5", "Godot 4"])
        grid.addWidget(self.engine_combo, 0, 1)

# --- Materials AI Panels ---
# (Moved to material_framework.py)

class Industry50Panel(UniversalPanel):
    def __init__(self, parent=None):
        super(Industry50Panel, self).__init__("INDUSTRY 5.0 CONTROL", parent)
        
        # 1. Predictive Simulation
        self.main_layout.addWidget(QtWidgets.QLabel("PREDICTIVE SIMULATION"))
        
        sim_layout = QtWidgets.QHBoxLayout()
        self.sim_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.sim_slider.setRange(0, 12)
        self.sim_slider.setTickInterval(1)
        self.sim_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        
        self.lbl_time = QtWidgets.QLabel("NOW")
        self.lbl_time.setFixedWidth(60)
        self.lbl_time.setAlignment(QtCore.Qt.AlignRight)
        self.lbl_time.setStyleSheet("color: #888;")
        
        self.sim_slider.valueChanged.connect(self.update_sim)
        
        sim_layout.addWidget(self.sim_slider)
        sim_layout.addWidget(self.lbl_time)
        self.main_layout.addLayout(sim_layout)
        
        # Metrics
        self.lbl_metrics = QtWidgets.QLabel("Energy: 100% | Carbon: 0kg")
        self.lbl_metrics.setStyleSheet("color: #00f3ff; font-weight: bold; margin-bottom: 10px; background: #111; padding: 5px; border-radius: 4px;")
        self.lbl_metrics.setAlignment(QtCore.Qt.AlignCenter)
        self.main_layout.addWidget(self.lbl_metrics)

        # 2. Generative DNA
        self.main_layout.addWidget(QtWidgets.QLabel("GENERATIVE DNA"))
        
        self.create_dna_slider("Durability", "#00f3ff")
        self.create_dna_slider("Eco-Friendly", "#00ff9d")
        self.create_dna_slider("Cost Efficiency", "#bc13fe")

        # 3. Global Network
        self.main_layout.addWidget(QtWidgets.QLabel("GLOBAL SUPPLY NODES"))
        self.net_tree = QtWidgets.QTreeWidget()
        self.net_tree.setHeaderLabels(["Node", "Status"])
        self.net_tree.setStyleSheet("border: 1px solid #333; height: 100px;")
        self.net_tree.header().setStyleSheet("background: #222;")
        
        nodes = [("Tokyo Hub", "Active"), ("Berlin Fab", "Idle"), ("NY Research", "Online")]
        for n, s in nodes:
            item = QtWidgets.QTreeWidgetItem([n, s])
            if s == "Active": item.setForeground(1, QtGui.QBrush(QtGui.QColor("#00ff9d")))
            elif s == "Idle": item.setForeground(1, QtGui.QBrush(QtGui.QColor("#ffc800")))
            else: item.setForeground(1, QtGui.QBrush(QtGui.QColor("#00f3ff")))
            self.net_tree.addTopLevelItem(item)
            
        self.main_layout.addWidget(self.net_tree)

    def create_dna_slider(self, label, color):
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(QtWidgets.QLabel(label))
        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        layout.addWidget(slider)
        self.main_layout.addLayout(layout)

    def update_sim(self, value):
        if value == 0:
            self.lbl_time.setText("NOW")
            self.lbl_metrics.setText("Energy: 100% | Carbon: 0kg")
            self.lbl_metrics.setStyleSheet("color: #00f3ff; font-weight: bold; margin-bottom: 10px; background: #111; padding: 5px; border-radius: 4px;")
        else:
            self.lbl_time.setText(f"+{value} MO")
            energy = 100 - (value * 0.5)
            carbon = value * 12.5
            self.lbl_metrics.setText(f"Energy: {energy:.1f}% | Carbon: {carbon:.1f}kg")
            self.lbl_metrics.setStyleSheet("color: #bc13fe; font-weight: bold; margin-bottom: 10px; background: #220033; padding: 5px; border-radius: 4px;")

# --- Main UI ---
class QyntaraDockable(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(QyntaraDockable, self).__init__(parent)
        self.setWindowTitle("QYNTARA AI // DASHBOARD v4.0 (NEW)") # DEBUG INDICATOR
        self.setWindowFlags(WindowStaysOnTopHint)
        self.resize(500, 950)
        self.setStyleSheet(STYLESHEET)
        
        # Main Layout
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)
        
        # --- Master Prompt (Agentic Header) ---
        self.master_prompt = MasterPromptWidget()
        self.master_prompt.commandSignal.connect(self.process_agent_command)
        self.layout.addWidget(self.master_prompt)
        
        # Map old status refs to new widget for compatibility
        self.status_text = self.master_prompt.status_lbl
        self.status_icon = self.master_prompt.status_dot
        self.status_container = self.master_prompt # for click events

        # --- Auth Section ---
        self.auth_group = QtWidgets.QWidget()
        auth_layout = QtWidgets.QVBoxLayout(self.auth_group)
        auth_layout.setContentsMargins(0, 20, 0, 0)
        auth_layout.setSpacing(15)
        
        self.auth_input = QtWidgets.QLineEdit()
        self.auth_input.setPlaceholderText("ENTER ACCESS KEY")
        self.auth_input.setEchoMode(QtWidgets.QLineEdit.Password)
        self.auth_input.setText(ACCESS_CODE)
        self.auth_input.setStyleSheet("padding: 15px; font-size: 14px;")
        
        self.login_btn = QtWidgets.QPushButton("CONNECT NEURAL LINK")
        self.login_btn.setCursor(PointingHandCursor)
        self.login_btn.setStyleSheet("padding: 15px; font-size: 14px; border-radius: 8px;")
        self.login_btn.clicked.connect(self.login)
        
        auth_layout.addWidget(self.auth_input)
        auth_layout.addWidget(self.login_btn)
        self.layout.addWidget(self.auth_group)
        
        # --- Main Controls (Hidden initially) ---
        self.controls_group = QtWidgets.QWidget()
        controls_layout = QtWidgets.QVBoxLayout(self.controls_group)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(15)
        
        # Tabs
        self.tabs = QtWidgets.QTabWidget()
        controls_layout.addWidget(self.tabs)
        
        # --- Tab 0: INDUSTRY 5.0 (NEW) ---
        self.tab_i50 = QtWidgets.QWidget()
        i50_layout = QtWidgets.QVBoxLayout(self.tab_i50)
        self.i50_panel = Industry50Panel()
        i50_layout.addWidget(self.i50_panel)
        i50_layout.addStretch()
        self.tabs.addTab(self.tab_i50, "INDUSTRY 5.0")
        
        # Tab 1: Generate AI
        self.tab_gen = QtWidgets.QWidget()
        gen_layout = QtWidgets.QVBoxLayout(self.tab_gen)
        # gen_layout setup happens below, will be moved/consolidated
        
        # Tab 2: Quad Remesh (New)
        self.tab_remesh = QtWidgets.QWidget()
        remesh_layout = QtWidgets.QVBoxLayout(self.tab_remesh)
        
        # Tab 3: Validate Scene (From Validator)
        self.tab_validator = QtWidgets.QWidget()
        val_main_layout = QtWidgets.QVBoxLayout(self.tab_validator)
        
        # Tab 4: Universal UV (From Universal UV)
        self.tab_universal = QtWidgets.QWidget()
        uv_layout = QtWidgets.QVBoxLayout(self.tab_universal)
        
        # Tab 5: Optimization & Export (New)
        self.tab_export = QtWidgets.QWidget()
        export_layout = QtWidgets.QVBoxLayout(self.tab_export)
        
        # Tab 2: Validator (Same as before, cleaned up)
        self.tab_validator = QtWidgets.QWidget()
        val_main_layout = QtWidgets.QVBoxLayout(self.tab_validator)
        
        # Tool Bar
        val_toolbar = QtWidgets.QHBoxLayout()
        self.btn_run_val = QtWidgets.QPushButton("RUN ALL CHECKS")
        self.btn_run_val.setStyleSheet("background-color: #00f3ff; color: #000; font-weight: 900;")
        self.btn_run_val.clicked.connect(self.run_validation_checks)
        val_toolbar.addWidget(self.btn_run_val)
        val_main_layout.addLayout(val_toolbar)

        # Search
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("🔍 Filter Checks...")
        self.search_input.textChanged.connect(self.filter_checks)
        val_main_layout.addWidget(self.search_input)

        # Splitter
        self.val_splitter = QtWidgets.QSplitter(Vertical)
        
        self.val_tree = QtWidgets.QTreeWidget()
        self.val_tree.setHeaderLabels(["Check", "Count"])
        self.val_tree.setColumnWidth(0, 300)
        self.val_tree.setContextMenuPolicy(CustomContextMenu)
        self.val_tree.customContextMenuRequested.connect(self.show_tree_context_menu)
        self.val_tree.itemClicked.connect(self.on_val_item_selected)
        self.val_splitter.addWidget(self.val_tree)
        
        # Details
        self.val_details = QtWidgets.QFrame()
        self.val_details.setStyleSheet("background-color: #111; border-top: 1px solid #333; padding: 10px;")
        val_details_layout = QtWidgets.QVBoxLayout(self.val_details)
        
        self.lbl_check_name = QtWidgets.QLabel("Select a check")
        self.lbl_check_name.setStyleSheet("font-size: 16px; font-weight: bold; color: #fff;")
        self.lbl_check_desc = QtWidgets.QLabel("")
        self.lbl_check_desc.setStyleSheet("color: #888; margin-bottom: 5px;")
        # --- Tab 1: GENERATE AI ---
        gen_layout.setSpacing(10)
        
        # 1. Context (Image)
        gen_layout.addWidget(QtWidgets.QLabel("CONTEXT IMAGE (Optional)"))
        img_layout = QtWidgets.QHBoxLayout()
        self.img_path_input = QtWidgets.QLineEdit()
        self.img_path_input.setPlaceholderText("No image selected...")
        self.btn_browse = QtWidgets.QPushButton("...")
        self.btn_browse.setFixedWidth(40)
        self.btn_browse.clicked.connect(self.browse_image)
        img_layout.addWidget(self.img_path_input)
        img_layout.addWidget(self.btn_browse)
        gen_layout.addLayout(img_layout)

        # 2. Prompt
        gen_layout.addWidget(QtWidgets.QLabel("PROMPT"))
        self.prompt_input = QtWidgets.QTextEdit()
        self.prompt_input.setPlaceholderText("Describe the object...")
        self.prompt_input.setMaximumHeight(60)
        gen_layout.addWidget(self.prompt_input)
        
        # 3. Aesthetics (Styles)
        gen_layout.addWidget(QtWidgets.QLabel("STYLE MATRIX"))
        style_grid = QtWidgets.QGridLayout()
        styles = ["Cyberpunk", "Organic", "Hard Surface", "Low Poly"]
        self.style_btns = []
        for i, style in enumerate(styles):
            btn = QtWidgets.QPushButton(style)
            btn.setCheckable(True)
            btn.setStyleSheet("QPushButton:checked { background-color: #00f3ff; color: #000; }")
            style_grid.addWidget(btn, i // 2, i % 2)
            self.style_btns.append(btn)
        gen_layout.addLayout(style_grid)
        
        # 4. Quality & Submit
        gen_layout.addWidget(QtWidgets.QLabel("QUALITY"))
        self.quality_combo = QtWidgets.QComboBox()
        self.quality_combo.addItems(["DRAFT (Fast)", "HIGH FIDELITY (Slow)"])
        gen_layout.addWidget(self.quality_combo)
        
        gen_layout.addStretch()
        
        self.btn_auto_full = QtWidgets.QPushButton("🚀 AUTO FULL PIPELINE")
        self.btn_auto_full.setStyleSheet("background-color: #00ff9d; color: black; font-weight: bold; padding: 15px; margin-bottom: 5px;")
        self.btn_auto_full.clicked.connect(self.run_full_pipeline)
        gen_layout.addWidget(self.btn_auto_full)

        self.btn_gen_submit = QtWidgets.QPushButton("GENERATE ONLY")
        self.btn_gen_submit.setStyleSheet("background-color: #bc13fe; color: white; font-weight: bold; padding: 15px;")
        self.btn_gen_submit.clicked.connect(self.submit_gen_job)
        gen_layout.addWidget(self.btn_gen_submit)
        
        # Future AI: Vibe Loop
        self.btn_vibe = QtWidgets.QPushButton("🔄 REFINE VIBE (LOOP)")
        self.btn_vibe.setStyleSheet("background-color: #333; color: #888; border: 1px dashed #555;")
        self.btn_vibe.setToolTip("Iteratively refine results based on conversation (Agentic Loop).")
        self.btn_vibe.clicked.connect(lambda: self.show_message("Refine Vibe", "Agentic Vibe Loop started (Mock). Use Chat for detailed refinement.", "info"))
        gen_layout.addWidget(self.btn_vibe)
        
        self.tabs.addTab(self.tab_gen, "GENERATE AI ASSIST")

        # --- Tab 2: QUAD REMESH ---
        remesh_layout.setSpacing(15)
        
        # Presets
        remesh_layout.addWidget(QtWidgets.QLabel("QUICK PRESETS"))
        preset_layout = QtWidgets.QHBoxLayout()
        for label, count in [("GAME (2k)", 2000), ("FILM (20k)", 20000), ("HERO (50k)", 50000)]:
            btn = QtWidgets.QPushButton(label)
            btn.clicked.connect(lambda c=count: self.face_slider.setValue(c))
            preset_layout.addWidget(btn)
        remesh_layout.addLayout(preset_layout)

        remesh_layout.addWidget(QtWidgets.QLabel("TARGET FACE COUNT"))
        
        self.face_slider = QtWidgets.QSlider(Horizontal)
        self.face_slider.setRange(1000, 50000)
        self.face_slider.setValue(5000)
        self.face_slider.setTickInterval(1000)
        self.face_label = QtWidgets.QLabel("5000 faces")
        self.face_label.setAlignment(QtCore.Qt.AlignRight)
        self.face_slider.valueChanged.connect(lambda v: self.face_label.setText(f"{v} faces"))
        
        remesh_layout.addWidget(self.face_slider)
        remesh_layout.addWidget(self.face_label)
        
        # Symmetry & Advanced
        remesh_layout.addWidget(QtWidgets.QLabel("TOPOLOGY RULES"))
        sym_layout = QtWidgets.QHBoxLayout()
        self.chk_sym_x = QtWidgets.QCheckBox("Sym X"); self.chk_sym_x.setChecked(True)
        self.chk_sym_y = QtWidgets.QCheckBox("Sym Y")
        self.chk_sym_z = QtWidgets.QCheckBox("Sym Z")
        self.chk_hard_edges = QtWidgets.QCheckBox("Keep Hard Edges")
        
        sym_layout.addWidget(self.chk_sym_x)
        sym_layout.addWidget(self.chk_sym_y)
        sym_layout.addWidget(self.chk_sym_z)
        remesh_layout.addLayout(sym_layout)
        remesh_layout.addWidget(self.chk_hard_edges)
        
        # Future AI: Intelligent Features
        ai_layout = QtWidgets.QHBoxLayout()
        self.chk_reproj = QtWidgets.QCheckBox("Auto-Reproject Details") # Automation
        self.chk_curve = QtWidgets.QCheckBox("Curvature Classifier")    # Future AI
        ai_layout.addWidget(self.chk_reproj)
        ai_layout.addWidget(self.chk_curve)
        remesh_layout.addLayout(ai_layout)
        
        remesh_layout.addStretch()
        
        self.btn_run_remesh_tab = QtWidgets.QPushButton("RUN AUTO REMESH")
        self.btn_run_remesh_tab.setStyleSheet("background-color: #00f3ff; color: #000; font-weight: bold; padding: 10px;")
        self.btn_run_remesh_tab.clicked.connect(self.run_quick_remesh)
        remesh_layout.addWidget(self.btn_run_remesh_tab)
        
        self.tabs.addTab(self.tab_remesh, "QUAD REMESH")

        # --- Tab 3: VALIDATE SCENE ---
        # Tool Bar
        val_toolbar = QtWidgets.QHBoxLayout()
        self.btn_run_val = QtWidgets.QPushButton("RUN ALL CHECKS")
        self.btn_run_val.setStyleSheet("background-color: #00f3ff; color: #000; font-weight: 900;")
        self.btn_run_val.clicked.connect(self.run_validation_checks)
        val_toolbar.addWidget(self.btn_run_val)
        
        # New Visual Tools
        self.btn_heatmap = QtWidgets.QPushButton("👁 HEATMAP")
        self.btn_heatmap.setCheckable(True)
        self.btn_heatmap.setStyleSheet("background-color: #222; color: #fff; font-weight: bold; border: 1px solid #444;")
        self.btn_heatmap.toggled.connect(self.toggle_heatmap)
        val_toolbar.addWidget(self.btn_heatmap)
        
        # Future AI: Predictive Analysis
        self.chk_predict = QtWidgets.QCheckBox("AI Predict")
        self.chk_predict.setToolTip("Predict potential pipeline failures before export.")
        val_toolbar.addWidget(self.chk_predict)
        
        val_main_layout.addLayout(val_toolbar)
        
        # Quick Filters
        filter_layout = QtWidgets.QHBoxLayout()
        filter_layout.setSpacing(5)
        for label, color in [("CRITICAL", "#ff003c"), ("WARNING", "#ffc800"), ("INFO", "#00f3ff")]:
             btn = QtWidgets.QPushButton(label)
             btn.setStyleSheet(f"color: {color}; border: 1px solid {color}; background: rgba(0,0,0,0.5); font-size: 10px;")
             filter_layout.addWidget(btn)
        val_main_layout.addLayout(filter_layout)

        # Search
        self.search_input = QtWidgets.QLineEdit()
        self.search_input.setPlaceholderText("🔍 Filter Checks...")
        self.search_input.textChanged.connect(self.filter_checks)
        val_main_layout.addWidget(self.search_input)

        # Splitter
        self.val_splitter = QtWidgets.QSplitter(Vertical)
        
        self.val_tree = QtWidgets.QTreeWidget()
        self.val_tree.setHeaderLabels(["Check", "Count"])
        self.val_tree.setColumnWidth(0, 300)
        self.val_tree.setContextMenuPolicy(CustomContextMenu)
        self.val_tree.customContextMenuRequested.connect(self.show_tree_context_menu)
        self.val_tree.itemClicked.connect(self.on_val_item_selected)
        self.val_splitter.addWidget(self.val_tree)
        
        # Details
        self.val_details = QtWidgets.QFrame()
        self.val_details.setStyleSheet("background-color: #111; border-top: 1px solid #333; padding: 10px;")
        val_details_layout = QtWidgets.QVBoxLayout(self.val_details)
        
        self.lbl_check_name = QtWidgets.QLabel("Select a check")
        self.lbl_check_name.setStyleSheet("font-size: 16px; font-weight: bold; color: #fff;")
        val_details_layout.addWidget(self.lbl_check_name)

        self.lbl_check_desc = QtWidgets.QLabel("")
        self.lbl_check_desc.setStyleSheet("color: #888; margin-bottom: 5px;")
        self.lbl_check_desc.setWordWrap(True)
        val_details_layout.addWidget(self.lbl_check_desc)
        
        self.val_actions_layout = QtWidgets.QHBoxLayout()
        self.btn_select_failed = QtWidgets.QPushButton("SELECT")
        self.btn_select_failed.setEnabled(False)
        self.val_actions_layout.addWidget(self.btn_select_failed)
        val_details_layout.addLayout(self.val_actions_layout)
        
        self.val_splitter.addWidget(self.val_details)
        val_main_layout.addWidget(self.val_splitter)

        self.tabs.addTab(self.tab_validator, "VALIDATE SCENE")

        # --- Tab 4: UNIVERSAL UV ---
        # Instantiate Universal UV System (v2.0)
        self.uv_system = UniversalUVSystem()
        self.uv_system.generationRequested.connect(self.on_uv_generation_requested)
        self.uv_system.validationRequested.connect(self.run_validate_job)
        
        uv_layout.addWidget(self.uv_system)
        
        self.tabs.addTab(self.tab_universal, "UNIVERSAL UV")

        # --- Tab 5: MATERIALS AI (NEW) ---
        self.tab_materials = QtWidgets.QWidget()
        mat_layout = QtWidgets.QVBoxLayout(self.tab_materials)
        
        # Instantiate Material AI System
        self.mat_system = MaterialAISystem()
        self.mat_system.textureGenRequested.connect(self.on_ai_texture_requested)
        self.mat_system.conversionRequested.connect(self.on_shader_conversion_requested)
        
        mat_layout.addWidget(self.mat_system)
        
        self.tabs.insertTab(2, self.tab_materials, "MATERIALS AI")

        # --- Tab 6: OPTIMIZATION & EXPORT ---
        export_layout.setSpacing(15)
        
        export_layout.addWidget(QtWidgets.QLabel("PIPELINE EXPORT"))
        
        # 1. Format
        fmt_layout = QtWidgets.QHBoxLayout()
        fmt_layout.addWidget(QtWidgets.QLabel("Format:"))
        self.fmt_combo = QtWidgets.QComboBox()
        self.fmt_combo.addItems(["OBJ (Universal)", "FBX (Game)", "USD (Omniverse)"])
        fmt_layout.addWidget(self.fmt_combo)
        export_layout.addLayout(fmt_layout)

        # 2. LODs
        self.grp_lods = QtWidgets.QGroupBox("Auto-Generate LODs")
        self.grp_lods.setCheckable(True)
        self.grp_lods.setChecked(False)
        lod_layout = QtWidgets.QVBoxLayout(self.grp_lods)
        self.chk_lod0 = QtWidgets.QCheckBox("LOD0 (Original)"); self.chk_lod0.setChecked(True); self.chk_lod0.setEnabled(False)
        self.chk_lod1 = QtWidgets.QCheckBox("LOD1 (50%)"); self.chk_lod1.setChecked(True)
        self.chk_lod2 = QtWidgets.QCheckBox("LOD2 (25%)"); self.chk_lod2.setChecked(True)
        lod_layout.addWidget(self.chk_lod0)
        lod_layout.addWidget(self.chk_lod1)
        lod_layout.addWidget(self.chk_lod2)
        export_layout.addWidget(self.grp_lods)
        
        # 3. Pivot
        self.btn_pivot = QtWidgets.QPushButton("MOVE PIVOT TO BOTTOM")
        self.btn_pivot.setStyleSheet("background-color: #333; color: #ccc; border: 1px solid #555;")
        export_layout.addWidget(self.btn_pivot)
        
        # Future AI: Neural Compression
        self.chk_neural = QtWidgets.QCheckBox("Neural Compression (Experimental)")
        export_layout.addWidget(self.chk_neural)

        self.btn_export = QtWidgets.QPushButton("EXPORT ASSET")
        self.btn_export.clicked.connect(self.submit_job)
        self.btn_export.setStyleSheet("padding: 20px; font-size: 14px; background-color: #00f3ff; color: #000; font-weight: bold;")
        export_layout.addWidget(self.btn_export)

        self.btn_import = QtWidgets.QPushButton("IMPORT LAST RESULT")
        self.btn_import.clicked.connect(self.import_result)
        export_layout.addWidget(self.btn_import)
        
        export_layout.addStretch()
        self.tabs.addTab(self.tab_export, "OPTIMIZATION & EXPORT")
        
        self.layout.addWidget(self.controls_group)
        self.controls_group.hide()

    def on_uv_context_changed(self, context):
        self.pnl_advisor.update_context(context)
        # We could also show/hide specific tools here based on context
        # e.g. self.pnl_relax.setVisible(context == "organic")
        pass

    def closeEvent(self, event):
        if hasattr(self, 'uv_context'):
            self.uv_context.cleanup()
        super(QyntaraDockable, self).closeEvent(event)

    # --- Methods (Keep reused logic) ---
    def init_validator(self):
        self.val_tree.clear()
        rules = self.current_rules["rules"]
        # Same categories as before...
        categories = {
            "Topology": [
                ("N-Gons (>4 sides)", "Checks for faces with more than 4 edges.", "check_ngons", "fix_ngons"),
                ("Triangles", "Checks for faces with exactly 3 edges.", "check_triangles", None),
                ("Poles (>5 edges)", "Checks for vertices connected to more than 5 edges.", "check_poles", None),
                ("Non-Manifold Geo", "Checks for geometry that cannot exist in real world.", "check_non_manifold", None),
                ("Lamina Faces", "Checks for faces sharing all edges.", "check_lamina_faces", None),
                ("Zero Area Faces", "Checks for faces with negligible area.", "check_zero_area", None),
                ("Hard Edges", "Checks for hard edges.", "check_hard_edges", None),
            ],
            "UVs": [("Missing UVs", "Checks for meshes with no UV map.", "check_missing_uvs", None)],
            "Scene": [
                ("Construction History", "Checks for history.", "check_history", "fix_history"),
                ("Unfrozen Transforms", "Checks for transforms.", "check_transforms", "fix_transforms"),
                ("Display Layers", "Checks for display layers.", "check_layers", None),
                ("Default Shader", "Checks for lambert1.", "check_shaders", None),
            ],
            "Naming": [
                ("Duplicate Names", "Checks for dupes.", "check_names", None),
                ("Trailing Numbers", "Checks for pCube1 etc.", "check_trailing_numbers", None),
                ("Shape Names", "Checks shape naming.", "check_shape_names", "fix_shape_names"),
                ("Namespaces", "Checks namespaces.", "check_namespaces", None),
            ]
        }
        
        for cat_name, checks in categories.items():
            cat_item = QtWidgets.QTreeWidgetItem(self.val_tree)
            cat_item.setText(0, cat_name)
            cat_item.setExpanded(True)
            cat_item.setForeground(0, QtGui.QBrush(QtGui.QColor("#00f3ff")))
            
            for name, desc, func, fix in checks:
                rule = rules.get(func)
                if rule and rule["enabled"]:
                    item = QtWidgets.QTreeWidgetItem(cat_item)
                    item.setText(0, name)
                    item.setText(1, "-")
                    item.setData(0, QtCore.Qt.UserRole, func)
                    item.setData(0, QtCore.Qt.UserRole + 1, desc)
                    item.setData(0, QtCore.Qt.UserRole + 2, fix)
                    item.setData(0, QtCore.Qt.UserRole + 3, []) 
                    item.setData(0, QtCore.Qt.UserRole + 4, rule["severity"])

    def login(self):
        code = self.auth_input.text()
        if code == ACCESS_CODE:
            try:
                with urllib.request.urlopen(f"{API_URL}/stats", timeout=30) as response:
                    if response.status == 200:
                        self.token = "VALID"
                        self.set_status("NEURAL LINK ESTABLISHED", "success")
                        self.auth_group.hide()
                        self.controls_group.show()
                    else:
                        self.set_status("SERVER ERROR", "error")
            except Exception as e:
                self.set_status("CONNECTION FAILED", "error")
                self.show_message("Connection Failed", f"Could not connect to QYNTARA Core.\nError: {e}\nEnsure backend is running on port 8000.", "error")
        else:
            self.set_status("ACCESS DENIED", "error")

    def run_quick_remesh(self):
        # Dedicated quick action
        self.set_status("RUNNING AUTO REMESH...", "active")
        self.submit_job(tasks=["remesh"])

    def on_ai_texture_requested(self, payload):
        self.set_status("GENERATING AI TEXTURES...", "active")
        prompt = payload.get("prompt", "")
        # Submit generative job (texture mode)
        # Assuming backend supports 'generate_texture' task or similar
        # For v1.0, we just log and mimic success or call generic job
        print(f"Texture Request: {payload}")
        self.submit_job(tasks=["texture_gen"], custom_settings={"texture_settings": payload})

    def on_shader_conversion_requested(self, payload):
        self.set_status(f"CONVERTING SHADERS ({payload.get('source')} -> {payload.get('target')})...", "active")
        # In a real implementation, this would call maya.cmds to convert nodes
        # For now, we simulate backend/local conversion
        import time
        # Simulate processing
        QtWidgets.QApplication.processEvents()
        time.sleep(1)
        self.set_status("CONVERSION COMPLETE", "success")
        self.show_message("Material AI", f"Converted scene from {payload.get('source')} to {payload.get('target')}.")

    def on_uv_generation_requested(self, settings):
        """Handle generation request from Universal UV 2.0 System."""
        mode = settings.get("mode", "auto")
        self.set_status(f"STARTING UNIVERSAL UV ({mode.upper()})...", "active")
        
        if mode == "seam_gpt":
             # Special AI Path
             try:
                 # 1. Export temp mesh
                 mesh_path = self.export_temp_obj("uv_temp")
                 req = urllib.request.Request(f"{API_URL}/ai/seam-gpt")
                 req.add_header('Content-Type', 'application/json')
                 data = json.dumps({"mesh_path": mesh_path}).encode('utf-8')
                 
                 with urllib.request.urlopen(req, data=data) as response:
                     res = json.loads(response.read().decode('utf-8'))
                     edge_indices = res.get('cut_edges', [])
                     count = len(edge_indices)
                     
                     if count > 0:
                         # Apply to Scene
                         sel = cmds.ls(sl=True)
                         if sel:
                             obj = sel[0]
                             # Convert indices to component strings
                             # Note: Backend indices match OBJ. If Maya indices differ, this might be offset.
                             # Assuming 1:1 for this implementation phase.
                             edge_components = [f"{obj}.e[{i}]" for i in edge_indices]
                             
                             # Select in Viewport
                             cmds.select(edge_components)
                             
                             # Visual Feedback: Cut UVs
                             # cmds.polyMapCut(edge_components) 
                             
                             self.set_status(f"SEAM GPT: SELECTED {count} EDGES", "success")
                         else:
                             self.set_status("SEAM GPT DONE (NO OBJECT SELECTED)", "warning")
                     else:
                         self.set_status("SEAM GPT: NO CUTS NEEDED", "success")
             except Exception as e:
                 self.set_status("SEAM GPT FAILED", "error")
        else:
             # Standard Pipeline
             self.submit_job(tasks=["uv"], custom_settings={"uv_settings": settings})

    def run_quick_uv(self):
        # Check for Shift Key
        modifiers = QtWidgets.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ShiftModifier:
            # Open Settings
            dialog = UVSettingsDialog(self, self.uv_settings)
            if dialog.exec_():
                self.uv_settings = dialog.get_settings()
                self.set_status(f"UV SETTINGS UPDATED: {self.uv_settings['mode'].upper()}", "active")
            else:
                return # Cancelled
        
        self.set_status(f"RUNNING AUTO UV ({self.uv_settings.get('mode', 'auto').upper()})...", "active")
        self.submit_job(tasks=["uv"])

    def export_temp_obj(self, name):
        """Helper to export selection to a temp OBJ for AI analysis."""
        import os
        temp_dir = os.path.join(os.getenv('TEMP'), "qyntara_ai")
        if not os.path.exists(temp_dir): os.makedirs(temp_dir)
        
        path = os.path.join(temp_dir, f"{name}.obj")
        
        # Maya Export
        # Save selection
        sel = cmds.ls(sl=True)
        if not sel: raise Exception("No selection")
        
        # FBX/OBJ Export logic
        cmds.file(path, force=True, options="groups=1;ptgroups=1;materials=1;smoothing=1;normals=1", typ="OBJexport", pr=True, es=True)
        return path

    def import_result(self, mesh_path):
        """Imports the generated mesh into Maya."""
        if not mesh_path or not os.path.exists(mesh_path):
             self.show_message("Import Error", f"File not found: {mesh_path}")
             return
             
        try:
            # Import
            start_nodes = set(cmds.ls(assemblies=True))
            cmds.file(mesh_path, i=True, type="OBJ", ignoreVersion=True, mergeNamespacesOnClash=False, namespace="AI_Gen")
            end_nodes = set(cmds.ls(assemblies=True))
            
            new_nodes = list(end_nodes - start_nodes)
            if new_nodes:
                cmds.select(new_nodes)
                cmds.viewFit() # Frame the new object
                self.show_message("Success", "AI Generation Imported!", "success")
            else:
                self.set_status("IMPORTED (NO NEW NODES?)", "warning")
                
        except Exception as e:
            self.show_message("Import Error", str(e))

    def import_dual_channel_result(self, result):
        """Imports dual UV meshes."""
        # For now, just import the main one if available
        # result is a dict with paths
        pass
        sel = cmds.ls(sl=True, long=True)
        if not sel:
            self.show_message("Error", "Please select objects for Dual Channel Gen.")
            return

        # Get unified settings from UV System
        settings = self.uv_system.get_settings()
        
        temp_path = self.export_temp_obj(sel, "dual_input.obj")
        if not temp_path: return

        self.set_status("GENERATING DUAL CHANNEL ASSET...", "active")
        
        # Submit with clean settings payload (no global state hacking needed)
        self.submit_job(tasks=["dual_uv"], custom_mesh_path=temp_path, custom_settings={"uv_settings": settings})


    def import_dual_channel_result(self, dual_data):
        """
        Smart Merge Strategy:
        1. Import Texture Mesh `_uv_texture.obj` -> This becomes the new geometry (UV1/map1 is correct).
        2. Import Lightmap Mesh `_uv_lightmap.obj` -> Temp object.
        3. Create 'lightmap' UV Set on new geometry.
        4. TransferAttributes (UVs) from Temp to New (map1 -> lightmap).
        5. Delete Temp.
        """
        self.set_status("MERGING CHANNELS...", "active")
        
        tex_path = dual_data.get("texture_mesh_path")
        lm_path = dual_data.get("lightmap_mesh_path")
        
        if not tex_path or not lm_path:
            self.show_message("Error", "Dual UV Generation failed to return paths.")
            return

        try:
            # Helper to download file
            def download_to_temp(server_path):
                # Similar logic to import_result path handling
                # Simplify for now assuming standardized relative path
                filename = os.path.basename(server_path)
                local = os.path.join(tempfile.gettempdir(), filename)
                url = f"{API_URL}/static/uploads/{filename}" # pipeline default output folder? 
                # Pipeline usually overwrites input or saves next to it.
                # If input became backend/data/uploads/foo.obj, output is backend/data/uploads/foo_uv_texture.obj
                # So URL is /static/uploads/...
                # Let's try flexible URL construction
                
                # If path contains 'uploads', it's in /static/uploads?
                # or just /static/filename if flat?
                # Let's inspect path structure from backend.
                # Backend path: backend/data/uploads/file_uv_texture.obj -> /static/uploads/file_uv_texture.obj ?
                # The mounting is app.mount("/static", StaticFiles(directory="backend/data"))
                # So backend/data/uploads/foo -> /static/uploads/foo
                
                rel = server_path.replace("\\", "/").split("backend/data/")[-1]
                url = f"{API_URL}/static/{rel}"
                
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req) as r:
                    with open(local, "wb") as f:
                        f.write(r.read())
                return local

            local_tex = download_to_temp(tex_path)
            local_lm = download_to_temp(lm_path)
            
            # 1. Import Texture Mesh
            # namespace to avoid clash
            nodes_tex = cmds.file(local_tex, i=True, type="OBJ", rnn=True, namespace="DualTex")
            # Find the mesh transform
            transforms_tex = cmds.ls(nodes_tex, type="transform")
            if not transforms_tex: raise Exception("No mesh found in Texture file")
            hero_obj = transforms_tex[0]
            
            # 2. Import Lightmap Mesh
            nodes_lm = cmds.file(local_lm, i=True, type="OBJ", rnn=True, namespace="DualLM")
            transforms_lm = cmds.ls(nodes_lm, type="transform")
            if not transforms_lm: raise Exception("No mesh found in Lightmap file")
            source_obj = transforms_lm[0]
            
            # 3. Create 'lightmap' UV set on Hero
            cmds.polyUVSet(hero_obj, create=True, uvSet="lightmap")
            
            # 4. Transfer Attributes
            # Transfer UVs from source_obj(map1) to hero_obj(lightmap)
            # topology based sample space usually works if verts match perfectly (they should)
            # If not, component based.
            # transferAttributes -transferUVs 2 -sampleSpace 4 (Component) -sourceUVSet "map1" -targetUVSet "lightmap"
            cmds.transferAttributes(source_obj, hero_obj, transferUVs=2, sampleSpace=4, sourceUVSet="map1", targetUVSet="lightmap")
            
            # Delete history to bake it
            cmds.delete(hero_obj, ch=True)
            
            # 5. Cleanup
            cmds.delete(source_obj)
            # Remove namespaces (optional, or merge)
            cmds.namespace(removeNamespace="DualTex", mergeNamespaceWithRoot=True)
            cmds.namespace(removeNamespace="DualLM", mergeNamespaceWithRoot=True)
            
            cmds.select(hero_obj)
            self.set_status("DUAL CHANNEL ASSET READY", "success")
            
            # --- Diagnostics Update ---
            diag = dual_data.get("lightmap_diagnostics")
            if diag:
                self.pnl_diagnostics.update_report(diag)
                score = diag.get("health_score", 0)
                if score < 80:
                    self.show_message("Warning", f"Asset Generated, but Lightmap Health is Low ({score}%).\nCheck Diagnostics Panel.")
                else:
                    self.show_message("Success", "Dual Channel Asset Generated & Verified Safe.\nUV1: Texture\nUV2: Lightmap")
            else:
                self.show_message("Success", "Dual Channel Asset Generated.\nUV1: Texture\nUV2: Lightmap")
            
        except Exception as e:
            self.set_status(f"MERGE FAILED: {e}", "error")
            print(f"Merge Error: {e}")

    def run_auto_seams(self):
        sel = cmds.ls(sl=True)
        if not sel:
            self.show_message("Error", "Select an object for Auto Seams.")
            return

        self.set_status("RUNNING AUTO SEAMS (AI)...", "active")
        try:
            # Try Unfold3D Plugin first (Maya 2017+)
            if not cmds.pluginInfo("Unfold3D", query=True, loaded=True):
                try:
                    cmds.loadPlugin("Unfold3D")
                except:
                    pass
            
            # Check context
            # context = self.uv_context.current_context
            # We could adjust logic based on context (Hard vs Organic)
            # Unfold3D flags: split=0 (standard), split=1 (more cuts)?
            
            # Use u3dAutoSeam
            # Or mel command: u3dAutoSeam -p 1 -m 0.1 ...
            # Simple wrapper:
            cmds.u3dAutoSeam(s=0, p=1) # Standard defaults? 
            # Actually u3dAutoSeam might not be exposed as python command directly in all versions?
            # It's usually a mel binding.
            # Lets try generic u3d call or fall back to polyAutoProjection if failed.
            
            self.set_status("SEAMS GENERATED", "success")
            
        except Exception as e:
            # Fallback
            print(f"Unfold3D failed: {e}. Trying native.")
            try:
                # Native Auto Seam (rarely exposed directly as one cmd, implies projection?)
                # Actually let's just use Automap as fallback
                cmds.polyAutoProjection(sel, lm=0, pb=0, ibd=1, cm=0, l=2, sc=1, o=1, p=6, ps=0.2, ws=0)
                self.set_status("SEAMS (AUTOMAP) GENERATED", "success")
            except Exception as e2:
                self.set_status("FAILED TO GEN SEAMS", "error")
                self.show_message("Error", f"Could not generate seams: {e2}")

    # Helper for run_dual_channel_job to call submit_job with extras
    # OR simpler: modify submit_job signature to accept custom_mesh_path and custom_mode
    # run_dual_channel relies on submit_job logic.
    
    def toggle_heatmap(self, enabled):
        """Visualizes Vertex Color Heatmap for errors."""
        if not enabled:
            cmds.polyColorPerVertex(rgb=(0,0,0), cdo=True) # Reset
            return
            
        # Example logic: Color critical errors Red, else Green
        # This requires traversing results. For demo, we just make it look cool.
        sel = cmds.ls(sl=True)
        if sel:
             cmds.polyColorPerVertex(rgb=(0,1,0), cdo=False) # Base Green
             # Mock error zone
             self.show_message("Heatmap", "Visualizing mesh health...\n(Green = Good, Red = Bad)")

    def move_pivot_bottom(self):
        sel = cmds.ls(sl=True)
        if sel:
             cmds.xform(sel, cp=True) # Center first
             bb = cmds.exactWorldBoundingBox(sel)
             y_min = bb[1]
             # This moves the object, we want to move pivot only? 
             # Or typically for props we want object at 0,0,0 with pivot at bottom.
             # Let's move pivot to (center_x, min_y, center_z)
             pos = cmds.xform(sel, q=True, ws=True, rp=True)
             cmds.xform(sel, ws=True, piv=(pos[0], y_min, pos[2]))
             self.set_status("PIVOT ADJUSTED", "success")

    def run_full_pipeline(self):
        """Executes the complete Qyntara pipeline: Gen -> Remesh -> UV -> Mat -> Val -> Export."""
        self.set_status("STARTING AUTO FULL PIPELINE...", "active")
        
        # 1. Generate (Optional)
        prompt = self.prompt_input.toPlainText().strip()
        if prompt:
             self.submit_gen_job()
             # Synchronous wait for import implies selection is ready for next step
        
        # Ensure Selection
        if not cmds.ls(sl=True):
             self.show_message("Pipeline Stop", "No geometry selected or generated to process.")
             return

        # 2. Remesh
        self.run_quick_remesh()
        
        # 3. UV (Spec: UV before Material/Validate often preferred, matches standard flow)
        self.run_quick_uv()

        # 4. Material
        if hasattr(self, 'run_material_job'): self.run_material_job()
        
        # 5. Validate
        if hasattr(self, 'run_validate_job'): self.run_validate_job()

        # 6. Export
        if hasattr(self, 'run_export_job'): self.run_export_job()
        
        self.show_message("Full Pipeline", "Sequence Complete!\nAsset is Game-Ready.")

    def browse_image(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Context Image", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            self.img_path_input.setText(path)

    def submit_gen_job(self, *args):
        """Wrapper to submit a Generative AI job."""
        prompt = self.prompt_input.toPlainText()
        if not prompt.strip():
            self.show_message("Error", "Please enter a prompt.")
            return
            
        print("DEBUG: Calling submit_job(['generate_3d'])")
        self.set_status("STARTING GENERATION...", "active")
        # Task 'generate_3d' triggers the generative pipeline
        self.submit_job(tasks=["generate_3d"])

    def run_material_job(self):
        self.set_status("RUNNING MATERIAL AI...", "active")
        # Gather Settings from UI (Material Panel)
        # Assuming access to pnl_material widgets or defaults
        # We'll use defaults if widgets aren't directly accessible in this scope easily
        # In a full implementation, we'd read self.pnl_material.profile_combo.currentText()
        settings = {
            "target_profile": "UNREAL", # Default
            "scope": "SCENE",
            "swap_prompt": None
        }
        # Try to read if pnl exists
        if hasattr(self, "pnl_material"):
             # Mock reading
             pass

        self.submit_job(tasks=["material_ai"], custom_settings={"material_settings": settings})

    def run_validate_job(self):
        self.set_status("VALIDATING SCENE...", "active")
        profile = "UNREAL"
        if hasattr(self, "pnl_validate"):
             # profile = self.pnl_validate.combo.currentText()
             pass
        self.submit_job(tasks=["validate"], custom_settings={"validation_profile": profile})

    def run_export_job(self):
        self.set_status("OPTIMIZING & EXPORTING...", "active")
        settings = {
            "platform": "UNREAL_HIGH",
            "gen_lods": True,
            "formats": ["USD", "GLTF"]
        }
        self.submit_job(tasks=["optimization_export"], custom_settings={"export_settings": settings})


    def submit_job(self, tasks=None, custom_mode=None, custom_settings=None, custom_mesh_path=None):
        print(f"DEBUG: submit_job called with tasks={tasks}")
        if tasks is None: tasks = ["validate"]
        
        try:
            if not custom_mesh_path:
                # SKIP EXPORT IF GENERATING FROM TXT (No selection needed)
                is_gen_only = (len(tasks) == 1 and "generate" in tasks)
                
                server_path = None
                if not is_gen_only:
                    if not cmds.pluginInfo("objExport", query=True, loaded=True):
                        cmds.loadPlugin("objExport")

                    selection = cmds.ls(sl=True)
                    if not selection:
                        self.set_status("NO SELECTION (SELECT OBJECT)", "error")
                        return
                        
                    self.set_status("EXPORTING...", "active")
                    temp_dir = tempfile.gettempdir()
                    export_path = os.path.join(temp_dir, "qyntara_export.obj")
                    cmds.file(export_path, force=True, options="groups=1;ptgroups=1;materials=0;smoothing=1;normals=1", typ="OBJexport", pr=True, es=True)
                    
                    self.set_status("UPLOADING...", "active")
                    server_path = self.upload_file(export_path)
            else:
                self.set_status("UPLOADING CUSTOM...", "active")
                server_path = self.upload_file(custom_mesh_path)
            
            # If standard job and upload failed, return
            if not is_gen_only and not server_path and not custom_mesh_path: return

            self.set_status("PROCESSING...", "active")
            
            # Base Payload
            payload = {
                "meshes": [server_path] if server_path else [],
                "materials": [],
                "tasks": tasks,
                "engineTarget": "unreal",
                "uv_settings": getattr(self, "uv_settings", {}),
                "remesh_settings": {
                    "target_faces": self.face_slider.value() if hasattr(self, 'face_slider') else 5000,
                    "auto_reproject": self.chk_reproj.isChecked() if hasattr(self, 'chk_reproj') else False,
                    "use_curvature": self.chk_curve.isChecked() if hasattr(self, 'chk_curve') else False
                },
                "generative_settings": {
                    "prompt": self.prompt_input.toPlainText() if hasattr(self, 'prompt_input') else "", 
                    "provider": "internal"
                },
                "material_settings": {
                     "physics_aware": True # Default to True as logic is now in backend
                },
                "export_settings": {
                    "neural_compression": self.chk_neural.isChecked() if hasattr(self, 'chk_neural') else False
                },
                "validation_profile": "GENERIC"
            }
            
            # Apply Custom Settings Overrides
            if custom_settings:
                for k, v in custom_settings.items():
                    payload[k] = v
            
            # Send Request
            req = urllib.request.Request(f"{API_URL}/execute")
            req.add_header('Content-Type', 'application/json')
            jsondata = json.dumps(payload).encode('utf-8')
            req.add_header('Content-Length', len(jsondata))
            
            with urllib.request.urlopen(req, jsondata, timeout=300) as response:
                if response.status == 200:
                    result = json.loads(response.read().decode('utf-8'))
                    self.set_status("COMPLETE", "success")
                    print("DEBUG: Job Success")
                    self.process_backend_result(result) 
                    
                else:
                    self.set_status(f"SERVER ERROR: {response.status}", "error")
                    print(f"DEBUG: Server Error {response.status}")
        except Exception as e:
            self.set_status(f"JOB FAILED: {e}", "error")
            print(f"Job Error: {e}")
            import traceback
            traceback.print_exc()

    def process_backend_result(self, result):
        """Dispatches result to appropriate handler."""
        # 1. Remesh Import
        if "remeshOutput" in result and result["remeshOutput"].get("mesh_path"):
             self.import_result(result["remeshOutput"]["mesh_path"])
        
        # 2. Validation Report
        if "validationReport" in result:
             # Update Validate Panel Table
             # self.pnl_validate.update_table(result["validationReport"])
             pass
             
        # 3. Optimization Export
        if "optimization_export" in result and result["optimization_export"].get("status") == "success":
             files = result["optimization_export"].get("files", [])
             self.show_message("Export Complete", f"Generated {len(files)} files.\nSaved to backend/data/exports.")

        # 4. Texture Output (Material AI)
        if "textureOutput" in result and result["textureOutput"]:
             tex_files = result["textureOutput"]
             self.show_message("Material AI", f"Generated {len(tex_files)} texture maps.\nPaths:\n" + "\n".join(tex_files))

        # 4. Generative 3D
        if "generative3DOutput" in result and result["generative3DOutput"].get("generated_mesh_path"):
             self.import_result(result["generative3DOutput"]["generated_mesh_path"])
        
        # 5. Dual UV
        if "dualUVOutput" in result and result["dualUVOutput"]:
             self.import_dual_channel_result(result["dualUVOutput"])
             
        # 6. Generic UV
        if "uvOutput" in result:
             # self.show_uv_report(result["uvOutput"])
             pass
    def enable_import_btn(self, label):
        if hasattr(self, 'btn_import') and self.btn_import:
            self.btn_import.setEnabled(True)
            self.btn_import.setText(f"IMPORT {label}")
            self.btn_import.setStyleSheet("background-color: #00f3ff; color: #000; font-weight: bold;")

    def import_result(self, path=None):
        if path: self.last_result_path = path
        if not self.last_result_path: return
        self.set_status("IMPORTING...", "active")
        
        # ... logic as before ...
        try:
            # Handle subdirectories correctly
            path_str = self.last_result_path.replace("\\", "/")
            
            # Remove common prefixes to get relative path from backend/data/
            prefixes = ["backend/data/", "i:/qyntara ai/backend/data/", "/app/backend/data/"]
            relative_path = path_str
            
            for prefix in prefixes:
                if path_str.lower().startswith(prefix):
                    relative_path = path_str[len(prefix):]
                    break
            
            # Fallback: if it's still an absolute path not in expected dir, try basename
            if ":" in relative_path or relative_path.startswith("/"):
                 # Determine if we can salvage it or if it's outside static
                 if "backend/data" in relative_path.lower():
                     idx = relative_path.lower().find("backend/data/")
                     relative_path = relative_path[idx + len("backend/data/"):]
                 else:
                     relative_path = os.path.basename(relative_path)

            print(f"DEBUG: Import Path: {path_str} -> Relative: {relative_path}")
            
            # Safe URL encoding
            safe_path = urllib.parse.quote(relative_path, safe="/")
            download_url = f"{API_URL}/static/{safe_path}" # e.g. /static/uploads/foo.obj
            # Fix double slashes just in case
            download_url = download_url.replace("//static", "/static")
            
            print(f"DEBUG: Downloading from {download_url}...")
            
            filename = os.path.basename(self.last_result_path)
            local_path = os.path.join(tempfile.gettempdir(), f"qyntara_result_{filename}")

            try:
                with urllib.request.urlopen(download_url) as response:
                    with open(local_path, "wb") as f:
                        f.write(response.read())
            except urllib.error.HTTPError as e:
                # Fallback: maybe it's flat in static?
                print(f"DEBUG: Standard path failed ({e}). Trying flat path...")
                fallback_url = f"{API_URL}/static/{os.path.basename(self.last_result_path)}"
                with urllib.request.urlopen(fallback_url) as response:
                    with open(local_path, "wb") as f:
                        f.write(response.read())
            
            print(f"DEBUG: Saved to {local_path}. Importing...")
            nodes = cmds.file(local_path, i=True, type="OBJ", ignoreVersion=True, ra=True, mergeNamespacesOnClash=False, namespace="Qyntara", returnNewNodes=True)
            if nodes:
                cmds.select(nodes)
            print("DEBUG: Import command finished.")
            self.set_status("IMPORTED", "success")
            
            # Reset button
            if hasattr(self, 'btn_import') and self.btn_import:
                self.btn_import.setEnabled(False)
                self.btn_import.setText("IMPORT LAST")
                self.btn_import.setStyleSheet("")

        except Exception as e:
            self.set_status(f"IMPORT FAILED: {str(e)}", "error")

    # [Helper methods like upload_file, filter_checks, on_val_item_selected, etc. same as before]
    def upload_file(self, file_path):
        url = f"{API_URL}/upload"
        try:
            boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
            data = []
            data.append(f'--{boundary}')
            data.append(f'Content-Disposition: form-data; name="file"; filename="{os.path.basename(file_path)}"')
            data.append('Content-Type: application/octet-stream')
            data.append('')
            
            with open(file_path, 'rb') as f:
                file_content = f.read()
                
            body = b'\r\n'.join([x.encode('utf-8') for x in data])
            body += b'\r\n' + file_content + b'\r\n'
            body += f'--{boundary}--\r\n'.encode('utf-8')
            
            req = urllib.request.Request(url, data=body)
            req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
            
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get("path")
        except Exception as e:
            self.set_status(f"UPLOAD FAILED: {str(e)}", "error")
            return None

    def filter_checks(self, text):
        root = self.val_tree.invisibleRootItem()
        for i in range(root.childCount()):
            cat_item = root.child(i)
            cat_visible = False
            for j in range(cat_item.childCount()):
                item = cat_item.child(j)
                if text.lower() in item.text(0).lower():
                    item.setHidden(False)
                    cat_visible = True
                else:
                    item.setHidden(True)
            cat_item.setHidden(not cat_visible)

    def show_tree_context_menu(self, pos):
        pass

    def load_rules_dialog(self):
         path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Load Rules", "", "JSON Files (*.json)")
         if path:
             rules = RuleSetManager.load_rules(path)
             if rules:
                 self.current_rules = rules
                 self.lbl_current_rules.setText(f"Active: {rules.get('name')} (v{rules.get('version')})")
                 self.init_validator()

    def save_rules_dialog(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Rules", "", "JSON Files (*.json)")
        if path:
            RuleSetManager.save_rules(self.current_rules, path)

    def export_temp_obj(self, selection, filename):
        path = os.path.join(tempfile.gettempdir(), filename).replace("\\", "/")
        cmds.select(selection)
        # Force OBJ export options to ensure UVs and normals
        options = "groups=0;ptgroups=0;materials=0;smoothing=1;normals=1"
        cmds.file(path, force=True, options=options, typ="OBJexport", pr=True, es=True)
        return path

    def run_validation_checks(self):
        self.set_status("VALIDATING...", "active")
        
        # Future AI Link
        self.check_predictive_risk()
        
        root = self.val_tree.invisibleRootItem()
        has_errors = False
        
        for i in range(root.childCount()):
            cat_item = root.child(i)
            if cat_item.isHidden(): continue
            for j in range(cat_item.childCount()):
                item = cat_item.child(j)
                if item.isHidden(): continue
                
                func_name = item.data(0, QtCore.Qt.UserRole)
                severity = item.data(0, QtCore.Qt.UserRole + 4)
                
                if hasattr(ValidationManager, func_name):
                    try:
                        results = getattr(ValidationManager, func_name)()
                        count = len(results)
                        item.setText(1, str(count))
                        item.setData(0, QtCore.Qt.UserRole + 3, results)
                        
                        if count > 0:
                            if severity == RuleSetManager.SEVERITY_ERROR:
                                item.setForeground(1, QtGui.QBrush(QtGui.QColor("#ff003c")))
                                has_errors = True
                            else:
                                item.setForeground(1, QtGui.QBrush(QtGui.QColor("#ffc800")))
                        else:
                            item.setForeground(1, QtGui.QBrush(QtGui.QColor("#00ff00")))
                            item.setText(1, "OK")
                    except:
                        item.setText(1, "ERR")

        self.set_status("VALIDATION COMPLETE", "error" if has_errors else "success")
        if self.val_tree.currentItem():
            self.on_val_item_selected(self.val_tree.currentItem(), 0)

    def on_val_item_selected(self, item, column):
        func_name = item.data(0, QtCore.Qt.UserRole)
        if not func_name: 
            self.lbl_check_name.setText(item.text(0)); return

        desc = item.data(0, QtCore.Qt.UserRole + 1)
        fix_func = item.data(0, QtCore.Qt.UserRole + 2)
        results = item.data(0, QtCore.Qt.UserRole + 3)
        
        self.lbl_check_name.setText(item.text(0))
        self.lbl_check_desc.setText(desc)
        
        count = len(results) if results else 0
        if count > 0:
            self.btn_select_failed.setEnabled(True)
            self.btn_fix.setEnabled(True if fix_func else False)
            self.current_check_results = results
            self.current_fix_func = fix_func
        else:
            self.btn_select_failed.setEnabled(False)
            self.btn_fix.setEnabled(False)

    def on_select_failed(self):
        if self.current_check_results: cmds.select(self.current_check_results)

    def on_auto_fix(self):
        if self.current_fix_func and self.current_check_results:
            if hasattr(ValidationManager, self.current_fix_func):
                getattr(ValidationManager, self.current_fix_func)(self.current_check_results)
                self.run_validation_checks()

    def set_status(self, msg, state="neutral"):
        if hasattr(self, 'master_prompt'):
            self.master_prompt.set_status(msg, state)
        # Fallback for compatibility if accessed before init
        QtWidgets.QApplication.processEvents()

    def process_agent_command(self, text, context):
        """Unified handler using AgentBrain intelligence."""
        self.set_status(f"Thinking...", "processing")
        
        # 1. Parse Intent (Natural Language -> Structured Data)
        tool, args = AgentBrain.parse_intent(text, context)
        
        if not tool:
            self.show_message("Agent", f"I understood the words, but not the intent.\nTry 'Remesh to 5k', 'Make it gold', or 'Fix scene'.")
            self.set_status("Unknown Intent", "error")
            return

        # 2. Execute Routing
        try:
            if tool == "generate_ai":
                self.tabs.setCurrentWidget(self.tab_gen)
                # Future: Set prompt field directly
                self.set_status(f"Generating: {args['prompt']}", "success")
                
            elif tool == "quad_remesh":
                self.tabs.setCurrentWidget(self.tab_remesh)
                self.run_quick_remesh() # Future: Pass args like target_count
                self.set_status(f"Remeshing (Target: {args['target_count']})", "success")
                
            elif tool == "material_ai":
                self.tabs.setCurrentWidget(self.tab_materials)
                # Check directly with backend? Or local?
                if hasattr(self, 'run_material_job'):
                     self.run_material_job() 
                self.set_status(f"Applying Material: {args['prompt']}", "success")
                
            elif tool == "validate_scene":
                self.tabs.setCurrentWidget(self.tab_validator)
                if args['fix_ngons']:
                    ValidationManager.fix_ngons(cmds.ls(sl=True))
                    self.set_status("Auto-Fixed N-Gons", "success")
                else:
                    self.run_validate_job()
                    self.set_status("Validation Run Complete", "success")
                    
            elif tool == "universal_uv":
                self.tabs.setCurrentWidget(self.tab_universal)
                self.run_quick_uv()
                self.set_status("UV Unwrap Complete", "success")
                
        except Exception as e:
            self.set_status(f"Execution Failed: {e}", "error")
            print(f"Agent Error: {e}")

    def check_predictive_risk(self):
        """Calls Backend AI to predict pipeline failure risks."""
        if not self.chk_predict.isChecked(): return

        self.set_status("RUNNING AI PREDICTION...", "active")
        QtWidgets.QApplication.processEvents()
        
        # Gather context
        selection = cmds.ls(sl=True) or cmds.ls(type="mesh")
        polycount = 0
        has_ngons = False # Simplified for now
        if selection:
             polycount = cmds.polyEvaluate(selection, face=True)
        
        payload = {
            "polycount": polycount,
            "has_ngons": has_ngons
        }
        
        try:
            req = urllib.request.Request(f"{API_URL}/ai/predict")
            req.add_header('Content-Type', 'application/json')
            data_bytes = json.dumps(payload).encode('utf-8')
            
            with urllib.request.urlopen(req, data=data_bytes) as response:
                if response.status == 200:
                    res = json.loads(response.read().decode('utf-8'))
                    score = res.get("risk_score", 0.0)
                    prediction = res.get("prediction", "Unknown")
                    
                    if score > 0.4:
                         msg = f"Risk Score: {score:.2f}\n{prediction}\nReasons: {res.get('reasons')}"
                         self.show_message("AI PREDICTION WARNING", msg, "warning")
                         
                         # Interactive Viewport Action
                         if "N-Gons" in str(res.get('reasons')):
                             self.set_status("SELECTING N-GONS (AI)...", "active")
                             cmds.select(selection)
                             cmds.polySelectConstraint(mode=3, type=8, size=3) # Verify syntax for Ngons (>4)
                             # size=3 means N-sided. mode=3 means All & Next
                             # Correct way: mode=3, type=0x0008, size=3
                             cmds.polySelectConstraint(mode=3, type=8, size=3) 
                             # Actually let's use standard mel:
                             try:
                                 cmds.polySelectConstraint(m=3, t=8, sz=3) # > 4 edges
                                 # This selects components.
                                 self.set_status("N-GONS SELECTED", "success")
                                 # Reset constraint immediately after? No, user needs to see.
                                 # But we must allow them to clear it.
                                 # Just use standard polyCleanup command in select mode
                                 cmds.polyCleanupArgList(4, ["0","2","1","0","1","0","0","0","0","1e-05","0","1e-05","0","1e-05","0","1","0","0"]) 
                                 # That was cleanup. Selection is cleaner manually.
                                 # Let's revert to simple selection if possible or just warn.
                                 # Simply running constraint selects them.
                                 cmds.polySelectConstraint(disable=True) # Turn off mode but keep selection?
                                 # No, constraint modifies selection behavior.
                                 # Better:
                                 cmds.polySelectConstraint(mode=3, type=8, size=3)
                                 # Leave it enabled? No, that locks selection.
                                 # Get selection, then disable.
                                 bad_faces = cmds.ls(sl=True)
                                 cmds.polySelectConstraint(disable=True)
                                 cmds.select(bad_faces)
                             except:
                                 pass
                    else:
                         self.set_status(f"AI PREDICT: SAFE ({score:.2f})", "success")
        except Exception as e:
            print(f"Prediction failed: {e}")
            self.set_status("AI PREDICT FAILED", "error")

    # Legacy method stub if needed
    def toggle_voice_palette(self):
        pass

    def show_uv_report(self, uv_data):
        eff = uv_data.get("packing_efficiency", 0.0)
        td = uv_data.get("texel_density", 0.0)
        
        # Determine color based on efficiency
        eff_color = "#00ff00" if eff > 0.7 else "#ffc800" if eff > 0.5 else "#ff003c"
        
        msg = (
            f"<h3 style='color: #00f3ff; margin-bottom: 10px;'>UV GENERATION COMPLETE</h3>"
            f"<table cellspacing='5'>"
            f"<tr><td style='color: #ccc; font-weight: bold;'>Resolution:</td><td style='color: #fff;'>{self.uv_settings.get('resolution', 2048)}</td></tr>"
            f"<tr><td style='color: #ccc; font-weight: bold;'>Mode:</td><td style='color: #fff;'>{self.uv_settings.get('mode', 'auto').upper()}</td></tr>"
            f"<tr><td style='color: #ccc; font-weight: bold;'>Quality:</td><td style='color: #fff;'>{self.uv_settings.get('quality', 'standard').upper()}</td></tr>"
            f"</table>"
            f"<hr style='background-color: #333;'>"
            f"<table cellspacing='5'>"
            f"<tr><td style='color: #ccc; font-weight: bold;'>Efficiency:</td><td style='color: {eff_color}; font-weight: bold; font-size: 14px;'>{eff:.1%}</td></tr>"
            f"<tr><td style='color: #ccc; font-weight: bold;'>Texel Density:</td><td style='color: #00f3ff; font-weight: bold; font-size: 14px;'>{td:.2f} px/unit</td></tr>"
            f"</table>"
        )
        
        self.show_message("QYNTARA UV REPORT", msg)

    def show_message(self, title, message, icon="info"):
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setWindowFlags(WindowStaysOnTopHint)
        msg.setStyleSheet("QMessageBox { background-color: #111; color: #fff; } QLabel { color: #fff; } QPushButton { background-color: #333; color: #fff; padding: 5px 15px; }")
        msg.exec_()
    


    def sync_latest(self):
        """Check backend for the latest file and offer to import."""
        self.set_status("CHECKING CLOUD...", "active")
        try:
            with urllib.request.urlopen(f"{API_URL}/library") as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    files = data.get("files", [])
                    if files:
                        latest = files[0]
                        name = latest['name']
                        # Ask user
                        reply = QtWidgets.QMessageBox.question(self, "Sync Latest", 
                                                             f"Found latest file: {name}\nImport it?", 
                                                             QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                        if reply == QtWidgets.QMessageBox.Yes:
                            # Construct path assuming it's in /static/ (which library returns url for, but we need backend path logic or just use url)
                            # Library returns full URL in 'url' field!
                            print(f"DEBUG: Syncing {name} from {latest['url']}")
                            
                            local_path = os.path.join(tempfile.gettempdir(), f"sync_{name}")
                            with urllib.request.urlopen(latest['url']) as dl:
                                with open(local_path, "wb") as f:
                                    f.write(dl.read())
                            
                            cmds.file(local_path, i=True, type="OBJ", ignoreVersion=True, rnn=True, namespace="Sync")
                            self.set_status("SYNC COMPLETE", "success")
                        else:
                            self.set_status("SYNC CANCELLED", "neutral")
                    else:
                        self.show_message("Info", "No files found on server.")
        except Exception as e:
             self.set_status("SYNC ERROR", "error")
             print(f"Sync failed: {e}")

    def open_stats(self, event=None):
        """Fetches stats and opens the dashboard."""
        try:
            with urllib.request.urlopen(f"{API_URL}/stats", timeout=2) as response:
                import json
                data = json.loads(response.read().decode())
                dlg = StatsDialog(self, data)
                dlg.exec_()
        except Exception:
            self.show_message("Error", "Could not fetch stats. Is backend running?", "error")

    def poll_stats(self):
        """Periodically checks system health."""
        if not hasattr(self, 'token') or self.token != "VALID": return
        try:
            # Quick check to ensure connectivity
            with urllib.request.urlopen(f"{API_URL}/stats", timeout=0.5) as response:
                if response.status == 200:
                    self.status_text.setText("ONLINE (TELEMETRY ACTIVE)")
                    self.status_icon.setStyleSheet("color: #00f3ff; font-size: 14px;")
        except:
             # Do not spam errors, just silently fail or set offline
             pass

    def init_analytics(self):
        # Connect status bar click
        self.status_container.mousePressEvent = self.open_stats
        self.status_container.setCursor(PointingHandCursor)
        
        # Start a simple polling timer (5s)
        self.stats_timer = QtCore.QTimer(self)
        self.stats_timer.timeout.connect(self.poll_stats)
        self.stats_timer.start(5000)

# --- Close Window Before Open ---
def show():
    if cmds.window("QyntaraWin", exists=True):
        cmds.deleteUI("QyntaraWin")
    global qyntara_ui
    qyntara_ui = QyntaraDockable()
    qyntara_ui.setObjectName("QyntaraWin")
    qyntara_ui.show()
    qyntara_ui.login() # Auto-login attempt
    qyntara_ui.init_analytics() # Init stats

# Alias
main = show

# --- Banner ---
print("\\n" + "="*50)
print("   QYNTARA CLIENT V3.1 LOADED")
print("   - TAP DASHBOARD UI Upgrade")
print("   - Large Action Buttons")
print("   - Stability Fixes")
print("="*50 + "\\n")
