from .qt_utils import QtWidgets, QtCore, QtGui
import maya.cmds as cmds
import os

class BakingWidget(QtWidgets.QWidget):
    """
    Advanced Baking & Lighting Studio Interface.
    """
    def __init__(self, parent=None):
        super(BakingWidget, self).__init__(parent)
        self.last_bake_path = None
        self.init_ui()
        
    def init_ui(self):
        # MAIN LAYOUT (Wrapper)
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        
        # SCROLL AREA
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
        # CONTENT WIDGET
        content_widget = QtWidgets.QWidget()
        self.layout_content = QtWidgets.QVBoxLayout(content_widget)
        self.layout_content.setContentsMargins(10, 10, 10, 10)
        self.layout_content.setSpacing(15)
        
        # Set Content
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        
        # Alias for existing code
        layout = self.layout_content
        
        # HEADER
        header = QtWidgets.QLabel("Lightmap & Texture Baking")
        header.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        layout.addWidget(header)
        
        # --- SECTION 1: THE STUDIO (LIGHTING) ---
        grp_studio = QtWidgets.QGroupBox("1. Virtual Studio")
        grp_studio.setStyleSheet("""
            QGroupBox { 
                border: 1px solid #00CEC9; border-radius: 4px; margin-top: 20px; color: #00CEC9; font-weight: bold;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
        """)
        studio_layout = QtWidgets.QVBoxLayout(grp_studio)
        studio_layout.setSpacing(10)
        
        # Buttons
        r1 = QtWidgets.QHBoxLayout()
        self.btn_studio = QtWidgets.QPushButton("Create 3-Point Rig")
        self.btn_studio.clicked.connect(self.create_studio)
        self.btn_studio.setToolTip("Creates Key/Fill/Rim lights + Cyclorama")
        
        self.btn_hdri = QtWidgets.QPushButton("Setup HDRI Dome")
        self.btn_hdri.clicked.connect(self.setup_hdri)
        
        r1.addWidget(self.btn_studio)
        r1.addWidget(self.btn_hdri)
        studio_layout.addLayout(r1)
        
        self.btn_focus = QtWidgets.QPushButton("Auto-Focus Camera")
        self.btn_focus.clicked.connect(self.auto_focus)
        studio_layout.addWidget(self.btn_focus)
        
        layout.addWidget(grp_studio)
        
        # --- SECTION 2: SMART PREP (AI) ---
        grp_prep = QtWidgets.QGroupBox("2. Smart Preparation")
        grp_prep.setStyleSheet("""
            QGroupBox { border: 1px solid #00CEC9; border-radius: 4px; margin-top: 20px; color: #00CEC9; font-weight: bold;}
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
        """)
        prep_layout = QtWidgets.QVBoxLayout(grp_prep)
        
        # AI Calc Row
        ai_row = QtWidgets.QHBoxLayout()
        self.btn_ai_calc = QtWidgets.QPushButton("⚡ AI Suggest Resolution")
        self.btn_ai_calc.setStyleSheet("background: #2d2d30; color: #00CEC9;")
        self.btn_ai_calc.clicked.connect(self.run_ai_calc)
        
        self.lbl_ai_res = QtWidgets.QLabel("Waiting...")
        self.lbl_ai_res.setStyleSheet("color: #888; font-style: italic;")
        
        ai_row.addWidget(self.btn_ai_calc)
        ai_row.addWidget(self.lbl_ai_res)
        prep_layout.addLayout(ai_row)
        
        # UV Check
        self.btn_verify_uv = QtWidgets.QPushButton("Verify UV Set 2 (Lightmap)")
        prep_layout.addWidget(self.btn_verify_uv)
        
        
        # --- SECTION 2b: ADVANCED UV PROCESSOR ---
        grp_uv = QtWidgets.QGroupBox("2b. Advanced UV Processor")
        grp_uv.setStyleSheet("""
            QGroupBox { border: 1px solid #74b9ff; border-radius: 4px; margin-top: 20px; color: #74b9ff; font-weight: bold;}
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
        """)
        uv_layout = QtWidgets.QVBoxLayout(grp_uv)
        
        # Profile Selector
        prof_row = QtWidgets.QHBoxLayout()
        prof_lbl = QtWidgets.QLabel("Target Profile:")
        self.rb_lightmap = QtWidgets.QRadioButton("Lightmap (UV2)")
        self.rb_lightmap.setChecked(True)
        self.rb_texture = QtWidgets.QRadioButton("Texture (UV1)")
        prof_row.addWidget(prof_lbl)
        prof_row.addWidget(self.rb_lightmap)
        prof_row.addWidget(self.rb_texture)
        prof_row.addStretch()
        uv_layout.addLayout(prof_row)
        
        # Overrides
        self.chk_override = QtWidgets.QCheckBox("Enable Advanced Overrides")
        self.chk_override.toggled.connect(self.toggle_overrides)
        uv_layout.addWidget(self.chk_override)
        
        self.ovr_widget = QtWidgets.QWidget()
        ovr_layout = QtWidgets.QFormLayout(self.ovr_widget)
        
        self.combo_unwrap = QtWidgets.QComboBox()
        self.combo_unwrap.addItems(["Auto-Detect", "Angle-Based (Organic)", "Projection (HardSurface)", "Flatten (Cut+Relax)", "Copy UV1->UV2"])
        ovr_layout.addRow("Unwrap Method:", self.combo_unwrap)
        
        self.combo_pack = QtWidgets.QComboBox()
        self.combo_pack.addItems(["Auto-Detect", "Heuristic (Lightmap)", "Tetris (Density)", "Strip (Linear)"])
        ovr_layout.addRow("Packing Algo:", self.combo_pack)
        
        self.ovr_widget.setVisible(False)
        uv_layout.addWidget(self.ovr_widget)
        
        # Generate Button
        self.btn_gen_uv = QtWidgets.QPushButton("GENERATE / REBUILD UVS")
        self.btn_gen_uv.setStyleSheet("""
            QPushButton { background: #74b9ff; color: #111; font-weight: bold; }
            QPushButton:hover { background: #a29bfe; }
        """)
        self.btn_gen_uv.clicked.connect(self.run_uv_gen)
        uv_layout.addWidget(self.btn_gen_uv)
        
        layout.addWidget(grp_uv)
        
        layout.addWidget(grp_prep)
        
        # --- SECTION 3: THE OVEN (BAKING) ---
        grp_bake = QtWidgets.QGroupBox("3. Production Bake")
        grp_bake.setStyleSheet("""
            QGroupBox { border: 1px solid #d29922; border-radius: 4px; margin-top: 20px; color: #d29922; font-weight: bold;}
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
        """)
        bake_layout = QtWidgets.QVBoxLayout(grp_bake)
        
        # Settings
        form = QtWidgets.QFormLayout()
        
        self.spin_res = QtWidgets.QComboBox()
        self.spin_res.addItems(["256", "512", "1024", "2048", "4096"])
        self.spin_res.setCurrentIndex(2) # 1024 default
        form.addRow("Resolution:", self.spin_res)
        
        self.combo_type = QtWidgets.QComboBox()
        self.combo_type.addItems(["Ambient Occlusion (AO)", "Lightmap (Diffuse)", "Bent Normal"])
        form.addRow("Map Type:", self.combo_type)
        
        # Fast Mode / Quality
        self.chk_gpu = QtWidgets.QCheckBox("Enable GPU Acceleration (Fast)")
        self.chk_gpu.setChecked(True) # Default to Fast as requested
        self.chk_gpu.setStyleSheet("color: #00CEC9; font-weight: bold;")
        form.addRow("", self.chk_gpu)
        
        self.chk_denoise = QtWidgets.QCheckBox("Use OptiX Denoiser")
        self.chk_denoise.setChecked(True)
        form.addRow("", self.chk_denoise)
        
        bake_layout.addLayout(form)
        
        # Bake Button
        self.btn_bake = QtWidgets.QPushButton("BAKE SELECTED TO DISK")
        self.btn_bake.setFixedHeight(40)
        self.btn_bake.setStyleSheet("""
            QPushButton { background: #d29922; color: #111; font-weight: bold; font-size: 12px; }
            QPushButton:hover { background: #eac54f; }
        """)
        self.btn_bake.clicked.connect(self.run_bake)
        bake_layout.addWidget(self.btn_bake)
        
        # Preview Button
        self.btn_preview = QtWidgets.QPushButton("PREVIEW IN VIEWPORT (Check Leaks)")
        self.btn_preview.setEnabled(False) 
        self.btn_preview.setStyleSheet("""
            QPushButton { background: #444; color: #aaa; margin-top: 5px;}
            QPushButton:enabled { background: #00CEC9; color: #000; font-weight: bold; }
        """)
        self.btn_preview.clicked.connect(self.run_preview)
        bake_layout.addWidget(self.btn_preview)
        
        layout.addWidget(grp_bake)
        layout.addStretch()

    # --- ACTIONS ---
    def create_studio(self):
        from ..core.lighting import LightingStudio
        LightingStudio.create_studio_rig()
        print("Studio Created.")
        
    def setup_hdri(self):
        from ..core.lighting import LightingStudio
        # Mock Path
        LightingStudio.setup_hdri("C:/textures/studio_small_01_4k.exr")
        print("HDRI Setup.")

    def auto_focus(self):
        from ..core.lighting import LightingStudio
        sel = cmds.ls(sl=True)
        LightingStudio.auto_focus(sel)

    def toggle_overrides(self, checked):
        self.ovr_widget.setVisible(checked)

    def run_uv_gen(self):
        from ..core.uv_engine import UVEngine
        sel = cmds.ls(sl=True)
        if not sel:
            print("Select objects to process.")
            return

        # 1. Profile
        profile = 'lightmap' if self.rb_lightmap.isChecked() else 'texture'
        
        # 2. Overrides
        unwrap = None
        pack = None
        
        if self.chk_override.isChecked():
            # Map Combo -> Key
            u_txt = self.combo_unwrap.currentText()
            p_txt = self.combo_pack.currentText()
            
            if "Angle" in u_txt: unwrap = 'angle'
            elif "Projection" in u_txt: unwrap = 'projection'
            elif "Flatten" in u_txt: unwrap = 'flatten'
            elif "Copy" in u_txt: unwrap = 'copy'
            
            if "Heuristic" in p_txt: pack = 'heuristic'
            elif "Tetris" in p_txt: pack = 'tetris'
            elif "Strip" in p_txt: pack = 'strip'

        # 3. Execute
        for obj in sel:
            try:
                UVEngine.process(
                    obj, 
                    profile=profile,
                    unwrap_method=unwrap,
                    pack_method=pack
                )
            except Exception as e:
                print(f"Error on {obj}: {e}")

    def run_ai_calc(self):
        from ..core.baking import BakingEngine
        sel = cmds.ls(sl=True)
        if not sel:
            self.lbl_ai_res.setText("Select object first!")
            return
            
        data = BakingEngine.calculate_optimal_res(sel)
        res = str(data['resolution'])
        
        # Auto-set dropdown
        idx = self.spin_res.findText(res)
        if idx >= 0: self.spin_res.setCurrentIndex(idx)
        
        self.lbl_ai_res.setText(f"AI Suggestion: {res}px ({data['reason']})")
        self.lbl_ai_res.setStyleSheet("color: #00CEC9; font-weight: bold;")

    def run_bake(self):
        from ..core.baking import BakingEngine
        sel = cmds.ls(sl=True)
        if not sel:
            print("Nothing selected.")
            return
            
        res = int(self.spin_res.currentText())
        b_type = "ao" if "Occlusion" in self.combo_type.currentText() else "light"
        
        # Get Fast Mode settings
        gpu = self.chk_gpu.isChecked()
        denoise = self.chk_denoise.isChecked()
        
        # Mock Output
        project = cmds.workspace(q=True, rd=True)
        output = os.path.join(project, "images")
        
        self.last_bake_path = BakingEngine.bake_maps(sel, output, res=res, bake_type=b_type, use_gpu=gpu, use_denoiser=denoise)
        
        # If success, update UI?
        if self.last_bake_path:
             self.btn_preview.setEnabled(True)
             self.btn_preview.setText(f"Preview ({b_type})")

    def run_preview(self):
        if not self.last_bake_path: return
        from ..core.baking import BakingEngine
        import glob
        
        sel = cmds.ls(sl=True)
        if not sel:
            print("Select an object to preview on.")
            return
        
        # SCAN
        # We need to find the specific file.
        
        search_pattern = os.path.join(self.last_bake_path, "*")
        list_of_files = glob.glob(search_pattern) 
        if not list_of_files:
            print("No baked files found to preview.")
            return
            
        latest_file = max(list_of_files, key=os.path.getctime)
        BakingEngine.preview_baked_map(sel, latest_file)
