import maya.cmds as cmds
import maya.api.OpenMaya as om2
import math

try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ImportError:
    from PySide6 import QtWidgets, QtCore, QtGui

# --- Styling ---
NEON_CYAN = "#00f3ff"
NEON_PURPLE = "#bc13fe"
NEON_GREEN = "#00ff9d"
BG_DARK = "rgba(20, 20, 25, 200)"

class UniversalPanel(QtWidgets.QFrame):
    def __init__(self, title, parent=None):
        super(UniversalPanel, self).__init__(parent)
        self.setStyleSheet(f"""
            UniversalPanel {{
                background-color: {BG_DARK};
                border: 1px solid #444;
                border-radius: 6px;
                margin-top: 4px;
            }}
            QLabel#Title {{
                font-weight: bold;
                color: {NEON_CYAN};
                font-size: 11px;
                padding: 4px;
            }}
            QGroupBox {{
                border: 1px solid #555;
                margin-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                padding: 0 5px;
                color: #ccc;
            }}
        """)
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(6, 6, 6, 6)
        self.main_layout.setSpacing(4)
        
        if title:
            self.title_lbl = QtWidgets.QLabel(title)
            self.title_lbl.setObjectName("Title")
            self.main_layout.addWidget(self.title_lbl)

# --- 1. UV Mode Selector ---
class UVModeSelector(QtWidgets.QWidget):
    modeChanged = QtCore.Signal(str) 

    def __init__(self, parent=None):
        super(UVModeSelector, self).__init__(parent)
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        
        self.group = QtWidgets.QButtonGroup(self)
        self.btns = {}
        
        modes = [
            ("AUTO UV", "auto"),
            ("UDIM UV", "udim"),
            ("LIGHTMAP", "lightmap"),
            ("SEAM GPT (AI)", "seam_gpt"), # Future AI
            ("PACK ONLY", "pack")
        ]
        
        for label, id_ in modes:
            btn = QtWidgets.QPushButton(label)
            btn.setCheckable(True)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #222; border: 1px solid #444; padding: 10px; font-weight: bold;
                }}
                QPushButton:checked {{
                    background-color: {NEON_CYAN}; color: black; border: 1px solid {NEON_CYAN};
                }}
            """)
            layout.addWidget(btn)
            self.group.addButton(btn)
            self.btns[id_] = btn
            btn.clicked.connect(lambda _, x=id_: self.modeChanged.emit(x))
            
        self.btns["auto"].setChecked(True)

# --- 2. Asset Profile ---
class AssetProfilePanel(UniversalPanel):
    def __init__(self, parent=None):
        super(AssetProfilePanel, self).__init__("ASSET PROFILE", parent)
        self.combo = QtWidgets.QComboBox()
        self.combo.addItems([
            "Character (Organic)", 
            "Prop (Hard Surface)", 
            "Environment (Modular)", 
            "Vehicle (Hybrid)",
            "Foliage (Leaf)",
            "Scan / Photogrammetry"
        ])
        self.main_layout.addWidget(self.combo)

# --- 3. Texel Density ---
class TexelDensityPanel(UniversalPanel):
    def __init__(self, parent=None):
        super(TexelDensityPanel, self).__init__("TEXEL DENSITY", parent)
        
        grid = QtWidgets.QGridLayout()
        grid.addWidget(QtWidgets.QLabel("Target (px/m):"), 0, 0)
        
        self.spin_density = QtWidgets.QSpinBox()
        self.spin_density.setRange(1, 4096)
        self.spin_density.setValue(512)
        grid.addWidget(self.spin_density, 0, 1)
        
        self.chk_normalize = QtWidgets.QCheckBox("Normalize Density")
        self.chk_normalize.setChecked(True)
        self.chk_lock = QtWidgets.QCheckBox("Lock Scale (UDIMs)")
        
        grid.addWidget(self.chk_normalize, 1, 0, 1, 2)
        grid.addWidget(self.chk_lock, 2, 0, 1, 2)
        
        self.prio_combo = QtWidgets.QComboBox()
        self.prio_combo.addItems(["High", "Medium", "Low"])
        grid.addWidget(QtWidgets.QLabel("Priority:"), 3, 0)
        grid.addWidget(self.prio_combo, 3, 1)
        
        self.main_layout.addLayout(grid)

# --- 4. Seam Intelligence ---
class SeamPanel(UniversalPanel):
    def __init__(self, parent=None):
        super(SeamPanel, self).__init__("SEAM STRATEGY", parent)
        
        self.strategy_combo = QtWidgets.QComboBox()
        self.strategy_combo.addItems(["AI Auto", "Hard Edge", "Angle Based", "Material Borders"])
        self.main_layout.addWidget(self.strategy_combo)
        
        self.angle_sl = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.angle_sl.setRange(0, 90)
        self.angle_sl.setValue(45)
        self.main_layout.addWidget(QtWidgets.QLabel("Angle Threshold:"))
        self.main_layout.addWidget(self.angle_sl)
        
        toggles = ["Detect Cylinders", "Preserve Symmetry", "Avoid Face Seams"]
        for t in toggles:
            self.main_layout.addWidget(QtWidgets.QCheckBox(t))

# --- 5. Packing Logic ---
class PackingPanel(UniversalPanel):
    def __init__(self, parent=None):
        super(PackingPanel, self).__init__("PACKING LOGIC", parent)
        
        self.pack_mode = QtWidgets.QComboBox()
        self.pack_mode.addItems(["By Object", "By Material", "By UDIM"])
        self.main_layout.addWidget(self.pack_mode)
        
        form = QtWidgets.QFormLayout()
        self.pad_shell = QtWidgets.QSpinBox()
        self.pad_shell.setValue(4)
        self.pad_tile = QtWidgets.QSpinBox()
        self.pad_tile.setValue(8)
        
        form.addRow("Shell Pad:", self.pad_shell)
        form.addRow("Tile Pad:", self.pad_tile)
        self.main_layout.addLayout(form)
        
        self.chk_rot = QtWidgets.QCheckBox("Rotate Shells")
        self.chk_rot.setChecked(True)
        self.main_layout.addWidget(self.chk_rot)
        
        # Add missing res_combo
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(QtWidgets.QLabel("Resolution:"))
        self.res_combo = QtWidgets.QComboBox()
        self.res_combo.addItems(["1024", "2048", "4096", "8192"])
        self.res_combo.setCurrentText("2048")
        hbox.addWidget(self.res_combo)
        self.main_layout.addLayout(hbox)

# --- 6. UDIM System ---
class UDIMPanel(UniversalPanel):
    def __init__(self, parent=None):
        super(UDIMPanel, self).__init__("UDIM CONFIG", parent)
        form = QtWidgets.QFormLayout()
        self.start_tile = QtWidgets.QSpinBox()
        self.start_tile.setRange(1001, 1099)
        self.start_tile.setValue(1001)
        self.max_tiles = QtWidgets.QSpinBox()
        self.max_tiles.setValue(4)
        
        form.addRow("Start Tile:", self.start_tile)
        form.addRow("Max Tiles:", self.max_tiles)
        self.main_layout.addLayout(form)
        
        self.chk_merge = QtWidgets.QCheckBox("Merge on Export")
        self.main_layout.addWidget(self.chk_merge)

# --- 7. Lightmap System ---
class LightmapPanel(UniversalPanel):
    def __init__(self, parent=None):
        super(LightmapPanel, self).__init__("LIGHTMAP SETTINGS", parent)
        
        self.engine_combo = QtWidgets.QComboBox()
        self.engine_combo.addItems(["Unreal Engine 5", "Unity", "Godot"])
        self.main_layout.addWidget(self.engine_combo)
        
        self.chk_no_overlap = QtWidgets.QCheckBox("Enforce No Overlap")
        self.chk_no_overlap.setChecked(True)
        self.chk_uv2 = QtWidgets.QCheckBox("Auto Generate UV1")
        self.chk_uv2.setChecked(True)
        
        self.main_layout.addWidget(self.chk_no_overlap)
        self.main_layout.addWidget(self.chk_uv2)
        
        # Add missing res_combo
        hbox = QtWidgets.QHBoxLayout()
        hbox.addWidget(QtWidgets.QLabel("Target Res:"))
        self.res_combo = QtWidgets.QComboBox()
        self.res_combo.addItems(["64", "128", "256", "512", "1024", "2048"])
        self.res_combo.setCurrentText("512")
        hbox.addWidget(self.res_combo)
        self.main_layout.addLayout(hbox)

# --- 8. Automation & Batch ---
class AutomationPanel(UniversalPanel):
    def __init__(self, parent=None):
        super(AutomationPanel, self).__init__("BATCH SCOPE", parent)
        
        hbox = QtWidgets.QHBoxLayout()
        self.rb_sel = QtWidgets.QRadioButton("Selected")
        self.rb_sel.setChecked(True)
        self.rb_all = QtWidgets.QRadioButton("Scene")
        hbox.addWidget(self.rb_sel)
        hbox.addWidget(self.rb_all)
        self.main_layout.addLayout(hbox)
        
        self.chk_filter = QtWidgets.QCheckBox("Filter by Visible")
        self.chk_filter.setChecked(True)
        self.main_layout.addWidget(self.chk_filter)

# --- 9. Validation ---
class UVValidationPanel(UniversalPanel):
    def __init__(self, parent=None):
        super(UVValidationPanel, self).__init__("UV HEALTH", parent)
        
        self.btn_scan = QtWidgets.QPushButton("SCAN UV ISSUES")
        self.btn_scan.setStyleSheet("background-color: #333; color: white;")
        self.main_layout.addWidget(self.btn_scan)
        
        self.status_lbl = QtWidgets.QLabel("Status: Unknown")
        self.main_layout.addWidget(self.status_lbl)

# --- 10. Output ---
class OutputPanel(UniversalPanel):
    def __init__(self, parent=None):
        super(OutputPanel, self).__init__("OUTPUT", parent)
        self.chk_replace = QtWidgets.QRadioButton("Replace Existing")
        self.chk_replace.setChecked(True)
        self.chk_new = QtWidgets.QRadioButton("Create New Set")
        self.main_layout.addWidget(self.chk_replace)
        self.main_layout.addWidget(self.chk_new)

# --- Main System ---
class UniversalUVSystem(QtWidgets.QWidget):
    generationRequested = QtCore.Signal(dict)
    validationRequested = QtCore.Signal()

    def __init__(self, parent=None):
        super(UniversalUVSystem, self).__init__(parent)
        
        # Scroll Area
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(container)
        layout.setSpacing(10)
        
        # Initialize Sections
        self.mode_selector = UVModeSelector()
        layout.addWidget(self.mode_selector)
        
        self.sec_profile = AssetProfilePanel()
        layout.addWidget(self.sec_profile)
        
        self.sec_density = TexelDensityPanel()
        layout.addWidget(self.sec_density)
        
        self.sec_seam = SeamPanel()
        layout.addWidget(self.sec_seam)
        
        self.sec_pack = PackingPanel()
        layout.addWidget(self.sec_pack)
        
        self.sec_udim = UDIMPanel()
        layout.addWidget(self.sec_udim)
        self.sec_udim.hide() # Hidden by default
        
        self.sec_lightmap = LightmapPanel()
        layout.addWidget(self.sec_lightmap)
        self.sec_lightmap.hide() # Hidden by default
        
        self.sec_auto = AutomationPanel()
        layout.addWidget(self.sec_auto)
        
        self.sec_val = UVValidationPanel()
        layout.addWidget(self.sec_val)
        
        self.sec_out = OutputPanel()
        layout.addWidget(self.sec_out)
        
        layout.addStretch()
        
        # Footer
        footer = QtWidgets.QHBoxLayout()
        self.btn_preview = QtWidgets.QPushButton("PREVIEW")
        self.btn_gen = QtWidgets.QPushButton("GENERATE UVs")
        self.btn_gen.setStyleSheet(f"background-color: {NEON_GREEN}; color: black; font-weight: bold; padding: 15px; font-size: 14px;")
        
        footer.addWidget(self.btn_preview)
        footer.addWidget(self.btn_gen)
        
        top_layout = QtWidgets.QVBoxLayout(self)
        scroll.setWidget(container)
        top_layout.addWidget(scroll)
        top_layout.addLayout(footer)
        
        # Connect Signals
        self.mode_selector.modeChanged.connect(self.on_mode_changed)
        self.btn_gen.clicked.connect(self.run_generation)
        self.sec_val.btn_scan.clicked.connect(lambda: self.validationRequested.emit())
        
    def on_mode_changed(self, mode):
        # Toggle panels based on mode
        self.sec_udim.setVisible(mode == "udim")
        self.sec_lightmap.setVisible(mode == "lightmap")
        
        if mode == "auto":
            self.sec_seam.show()
            self.sec_pack.show()
        elif mode == "pack":
            self.sec_seam.hide()
            self.sec_pack.show()
            
    generationRequested = QtCore.Signal(dict)

    def get_settings(self):
        """Retrieve current UI settings."""
        settings = {
            "profile": self.sec_profile.combo.currentText(),
            "seam_strategy": self.sec_seam.strategy_combo.currentText(),
            "texel_density": self.sec_density.spin_density.value(),
            "start_tile": self.sec_udim.start_tile.value(),
            "lightmap_resolution": int(self.sec_lightmap.res_combo.currentText()),
            "priority": self.sec_density.prio_combo.currentText().lower(),
            "pack_resolution": int(self.sec_pack.res_combo.currentText()),
            "validation_fix": True,
            "mode": "auto"
        }
        if self.mode_selector.btns["udim"].isChecked(): settings["mode"] = "udim"
        elif self.mode_selector.btns["lightmap"].isChecked(): settings["mode"] = "lightmap"
        elif self.mode_selector.btns["pack"].isChecked(): settings["mode"] = "pack"
        elif self.mode_selector.btns.get("seam_gpt") and self.mode_selector.btns["seam_gpt"].isChecked(): settings["mode"] = "seam_gpt"
        return settings

    def run_generation(self):
        # Gather Settings
        settings = self.get_settings()
        print(f"Emitting Gen Request: {settings}")
        self.generationRequested.emit(settings)
