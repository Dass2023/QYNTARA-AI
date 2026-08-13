import maya.cmds as cmds
import maya.api.OpenMaya as om2
import json

try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ImportError:
    from PySide6 import QtWidgets, QtCore, QtGui

# --- Styling (Matching Universal Framework) ---
NEON_CYAN = "#00f3ff"
NEON_PURPLE = "#bc13fe"
NEON_GREEN = "#00ff9d"
NEON_RED = "#ff003c"
BG_DARK = "rgba(20, 20, 25, 200)"

class MaterialPanel(QtWidgets.QFrame):
    def __init__(self, title, parent=None):
        super(MaterialPanel, self).__init__(parent)
        self.setStyleSheet(f"""
            MaterialPanel {{
                background-color: {BG_DARK};
                border: 1px solid #444;
                border-radius: 6px;
                margin-top: 4px;
            }}
            QLabel#Title {{
                font-weight: bold;
                color: {NEON_PURPLE}; /* Purple for Material AI */
                font-size: 11px;
                padding: 4px;
            }}
            QGroupBox {{ margin-top: 10px; border: 1px solid #555; }}
            QGroupBox::title {{ color: #ccc; subcontrol-origin: margin; left: 5px; }}
        """)
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(6, 6, 6, 6)
        self.main_layout.setSpacing(4)
        
        if title:
            self.title_lbl = QtWidgets.QLabel(title)
            self.title_lbl.setObjectName("Title")
            self.main_layout.addWidget(self.title_lbl)

# --- 1. Universal Material Scanner ---
class ScannerPanel(MaterialPanel):
    def __init__(self, parent=None):
        super(ScannerPanel, self).__init__("UNIVERSAL SCANNNER", parent)
        
        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setFixedHeight(80)
        self.list_widget.setStyleSheet("background-color: #111; color: #aaa; border: none;")
        self.main_layout.addWidget(self.list_widget)
        
        self.status = QtWidgets.QLabel("Status: Idle")
        self.status.setStyleSheet("color: #666; font-style: italic;")
        self.main_layout.addWidget(self.status)
        
        self.btn_scan = QtWidgets.QPushButton("SCAN SCENE")
        self.btn_scan.setStyleSheet(f"background-color: {NEON_CYAN}; color: black; font-weight: bold;")
        self.btn_scan.clicked.connect(self.scan_scene)
        self.list_widget.itemDoubleClicked.connect(self.select_shader_objects)
        self.main_layout.addWidget(self.btn_scan)

    def scan_scene(self):
        self.list_widget.clear()
        # Find all shading engines
        se_nodes = cmds.ls(type="shadingEngine")
        shaders = []
        
        for se in se_nodes:
            if se == "initialParticleSE" or se == "initialShadingGroup": continue
            
            # Find surface shader connection
            conns = cmds.listConnections(se + ".surfaceShader")
            if conns:
                shader = conns[0]
                shader_type = cmds.objectType(shader)
                
                # Count objects
                objs = cmds.sets(se, q=True)
                count = len(objs) if objs else 0
                
                item_text = f"{shader} ({shader_type}) - [{count} objs]"
                item = QtWidgets.QListWidgetItem(item_text)
                # Store shader name for selection
                item.setData(QtCore.Qt.UserRole, shader) 
                
                self.list_widget.addItem(item)
                shaders.append(shader)
        
        self.status.setText(f"Active Materials: {len(shaders)}")

    def select_shader_objects(self, item):
        shader = item.data(QtCore.Qt.UserRole)
        if shader:
            try:
                cmds.hyperShade(objects=shader)
                count = len(cmds.ls(sl=True))
                print(f"Selected {count} objects for {shader}")
            except Exception as e:
                print(f"Selection failed: {e}")

# --- 2. AI Material Swapper ---
class SwapperPanel(MaterialPanel):
    def __init__(self, parent=None):
        super(SwapperPanel, self).__init__("AI MATERIAL SWAPPER", parent)
        
        grid = QtWidgets.QGridLayout()
        grid.addWidget(QtWidgets.QLabel("Find:"), 0, 0)
        self.txt_find = QtWidgets.QLineEdit()
        self.txt_find.setPlaceholderText("Name Pattern (e.g. *plastic*)")
        grid.addWidget(self.txt_find, 0, 1)
        
        grid.addWidget(QtWidgets.QLabel("Replace With:"), 1, 0)
        self.combo_target = QtWidgets.QComboBox()
        self.combo_target.addItems(["PBR Plastic", "PBR Metal", "PBR Glass", "PBR Matte"])
        grid.addWidget(self.combo_target, 1, 1)
        
        self.main_layout.addLayout(grid)
        
        self.btn_swap = QtWidgets.QPushButton("SWAP ALL")
        self.btn_swap.setStyleSheet("background-color: #333; color: white;")
        self.main_layout.addWidget(self.btn_swap)

# --- 3. Universal Shader Converter ---
class ConverterPanel(MaterialPanel):
    def __init__(self, parent=None):
        super(ConverterPanel, self).__init__("UNIVERSAL CONVERTER", parent)
        
        hbox = QtWidgets.QHBoxLayout()
        self.src_fmt = QtWidgets.QComboBox()
        self.src_fmt.addItems(["Arnold", "V-Ray", "Redshift", "USD"])
        self.dst_fmt = QtWidgets.QComboBox()
        self.dst_fmt.addItems(["Unreal (Standard)", "Unity (URP)", "glTF"])
        
        hbox.addWidget(self.src_fmt)
        hbox.addWidget(QtWidgets.QLabel("➜"))
        hbox.addWidget(self.dst_fmt)
        self.main_layout.addLayout(hbox)
        
        chk_layout = QtWidgets.QHBoxLayout()
        chk_layout.addWidget(QtWidgets.QCheckBox("Fix Gamma"))
        chk_layout.addWidget(QtWidgets.QCheckBox("Fix Normal (DX/GL)"))
        self.main_layout.addLayout(chk_layout)
        
        # Future AI: Physics Logic
        self.chk_phys = QtWidgets.QCheckBox("Physics-Aware Values (AI)")
        self.chk_phys.setToolTip("Auto-calculate IOR and Friction based on material name.")
        self.chk_phys.setChecked(True)
        self.main_layout.addWidget(self.chk_phys)
        
        self.btn_convert = QtWidgets.QPushButton("CONVERT SHADERS")
        self.btn_convert.setStyleSheet(f"background-color: {NEON_PURPLE}; color: white; font-weight: bold;")
        self.main_layout.addWidget(self.btn_convert)

# --- 4. AI Texture Generator ---
class TextureGenPanel(MaterialPanel):
    def __init__(self, parent=None):
        super(TextureGenPanel, self).__init__("AI TEXTURE GEN", parent)
        
        self.mode_tabs = QtWidgets.QTabWidget()
        self.mode_tabs.setFixedHeight(120)
        
        # Tab 1: From Prompt
        tab_prompt = QtWidgets.QWidget()
        tp_layout = QtWidgets.QVBoxLayout(tab_prompt)
        self.txt_prompt = QtWidgets.QTextEdit()
        self.txt_prompt.setPlaceholderText("Describe texture (e.g. rusted cyberpunk metal panel)")
        tp_layout.addWidget(self.txt_prompt)
        self.mode_tabs.addTab(tab_prompt, "Prompt")
        
        # Tab 2: From Selection
        tab_sel = QtWidgets.QWidget()
        ts_layout = QtWidgets.QVBoxLayout(tab_sel)
        ts_layout.addWidget(QtWidgets.QLabel("Uses selected object's existing albedo."))
        self.mode_tabs.addTab(tab_sel, "Selection")
        
        self.main_layout.addWidget(self.mode_tabs)
        
        # Output Maps
        maps_layout = QtWidgets.QHBoxLayout()
        for m in ["Alb", "Rough", "Nrm", "Height"]:
            cb = QtWidgets.QCheckBox(m)
            cb.setChecked(True)
            maps_layout.addWidget(cb)
        self.main_layout.addLayout(maps_layout)
        
        self.btn_gen = QtWidgets.QPushButton("GENERATE TEXTURES")
        self.btn_gen.setStyleSheet(f"background-color: {NEON_CYAN}; color: black;")
        self.main_layout.addWidget(self.btn_gen)

# --- 5. Engine Presets ---
class PresetsPanel(MaterialPanel):
    def __init__(self, parent=None):
        super(PresetsPanel, self).__init__("ENGINE PROFILE", parent)
        
        grid = QtWidgets.QGridLayout()
        engines = ["Unreal Nanite", "Unreal Mobile", "Unity HDRP", "Unity URP", "WebGL", "USD Cinematic"]
        
        for i, eng in enumerate(engines):
            btn = QtWidgets.QPushButton(eng)
            btn.setStyleSheet("text-align: left; padding: 5px;")
            grid.addWidget(btn, i // 2, i % 2)
            
        self.main_layout.addLayout(grid)

# --- Main System ---
class MaterialAISystem(QtWidgets.QWidget):
    # Signals to communicate with Main Automation Pipeline
    textureGenRequested = QtCore.Signal(dict)
    conversionRequested = QtCore.Signal(dict)
    
    def __init__(self, parent=None):
        super(MaterialAISystem, self).__init__(parent)
        
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(container)
        layout.setSpacing(10)
        
        self.pnl_scanner = ScannerPanel()
        self.pnl_swapper = SwapperPanel()
        self.pnl_converter = ConverterPanel()
        self.pnl_texgen = TextureGenPanel()
        self.pnl_presets = PresetsPanel()
        
        layout.addWidget(self.pnl_scanner)
        layout.addWidget(self.pnl_swapper)
        layout.addWidget(self.pnl_converter)
        layout.addWidget(self.pnl_texgen)
        layout.addWidget(self.pnl_presets)
        layout.addStretch()
        
        scroll.setWidget(container)
        
        main = QtWidgets.QVBoxLayout(self)
        main.addWidget(scroll)
        
        # Connect internal signals
        self.pnl_texgen.btn_gen.clicked.connect(self.request_texture_gen)
        self.pnl_converter.btn_convert.clicked.connect(self.request_conversion)

    def request_texture_gen(self):
        prompt = self.pnl_texgen.txt_prompt.toPlainText()
        self.textureGenRequested.emit({"prompt": prompt, "type": "texture_gen"})
        
    def request_conversion(self):
        src = self.pnl_converter.src_fmt.currentText()
        dst = self.pnl_converter.dst_fmt.currentText()
        self.conversionRequested.emit({"source": src, "target": dst})
