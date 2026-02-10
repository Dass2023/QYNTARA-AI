from .qt_utils import QtWidgets, QtCore, QtGui
from ..core import uv_tools, uv, visualizer, baking
from ..ai_assist import ai_interface
import logging

logger = logging.getLogger(__name__)

try:
    from maya import cmds
except ImportError:
    cmds = None

except ImportError:
    cmds = None

class CollapsibleBox(QtWidgets.QWidget):
    def __init__(self, title="", parent=None):
        super(CollapsibleBox, self).__init__(parent)
        self.toggle_button = QtWidgets.QToolButton(text=f"> {title}", checkable=True, checked=True)
        self.toggle_button.setStyleSheet("QToolButton { border: none; font-weight: bold; color: #00CEC9; background-color: #333; text-align: left; padding: 5px; }")
        self.toggle_button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(QtCore.Qt.RightArrow)
        self.toggle_button.toggled.connect(self.on_toggled)
        
        self.content_area = QtWidgets.QWidget()
        self.content_area.setMaximumHeight(10000)
        self.content_area.setMinimumHeight(0)
        
        # Determine Title for state management
        self._title = title

        lay = QtWidgets.QVBoxLayout(self)
        lay.setSpacing(0)
        lay.setContentsMargins(0,0,0,0)
        lay.addWidget(self.toggle_button)
        lay.addWidget(self.content_area)
        
        # Animation? No, keep it simple first.
        
    def on_toggled(self, checked):
        # Rotate logic or text logic
        # Using built-in arrow type if supported, or text.
        # If using text:
        arrow = "v" if checked else ">"
        self.toggle_button.setText(f"{arrow} {self._title}")
        self.toggle_button.setArrowType(QtCore.Qt.DownArrow if checked else QtCore.Qt.RightArrow)
        self.content_area.setVisible(checked)

    def setContentLayout(self, layout):
        self.content_area.setLayout(layout)

class UVToolsWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(UVToolsWidget, self).__init__(parent)
        self.ai = ai_interface.AIAssist()
        self.init_ui()
        
    def init_ui(self):
        # MAIN LAYOUT (Wrapper)
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        
        # SCROLL AREA
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff) # Only Vertical needed
        
        # CONTENT WIDGET
        content_widget = QtWidgets.QWidget()
        self.layout_content = QtWidgets.QVBoxLayout(content_widget)
        self.layout_content.setContentsMargins(10, 10, 10, 10)
        self.layout_content.setSpacing(15)
        
        # Set Content
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        
        # --- POPULATE UI (Use self.layout_content instead of layout) ---
        layout = self.layout_content 
        
        lbl_title = QtWidgets.QLabel("UV Toolkit")
        lbl_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #fff;")
        layout.addWidget(lbl_title)
        
        # --- CHECKS ---
        grp_check = CollapsibleBox("Validation")
        chk_content = QtWidgets.QWidget()
        chk_layout = QtWidgets.QVBoxLayout(chk_content)
        
        self.btn_check_overlaps = QtWidgets.QPushButton("Check Overlaps")
        self.btn_check_overlaps.clicked.connect(self.run_overlap_check)
        chk_layout.addWidget(self.btn_check_overlaps)
        
        self.btn_check_bounds = QtWidgets.QPushButton("Check 0-1 Bounds")
        self.btn_check_bounds.clicked.connect(self.run_bounds_check)
        chk_layout.addWidget(self.btn_check_bounds)
        
        grp_check.setContentLayout(chk_layout)
        layout.addWidget(grp_check)

        # --- UV SET MANAGER ---
        grp_manager = CollapsibleBox("UV Set Manager")
        manager_content = QtWidgets.QWidget()
        manager_layout = QtWidgets.QVBoxLayout(manager_content)
        manager_layout.setSpacing(5)

        # Switch Index
        row_idx = QtWidgets.QHBoxLayout()
        for i in range(3):
            btn = QtWidgets.QPushButton(f"UV Channel {i+1}")
            # Fix: signal might send 0 args, so we make the first arg optional
            btn.clicked.connect(lambda checked=False, x=i: self.run_switch_uv_index(x))
            row_idx.addWidget(btn)
        manager_layout.addLayout(row_idx)

        # Reorder
        row_move = QtWidgets.QHBoxLayout()
        btn_up = QtWidgets.QPushButton("Move Up")
        btn_up.clicked.connect(lambda: self.run_move_uv('up'))
        btn_down = QtWidgets.QPushButton("Move Down")
        btn_down.clicked.connect(lambda: self.run_move_uv('down'))
        row_move.addWidget(btn_up)
        row_move.addWidget(btn_down)
        manager_layout.addLayout(row_move)

        # CRUD
        row_crud = QtWidgets.QHBoxLayout()
        btn_add = QtWidgets.QPushButton("Add New")
        btn_add.clicked.connect(self.run_add_uv)
        btn_del = QtWidgets.QPushButton("Delete Current")
        btn_del.clicked.connect(self.run_delete_uv)
        row_crud.addWidget(btn_add)
        row_crud.addWidget(btn_del)
        manager_layout.addLayout(row_crud)

        row_crud2 = QtWidgets.QHBoxLayout()
        btn_ren = QtWidgets.QPushButton("Rename")
        btn_ren.clicked.connect(self.run_rename_uv)
        btn_dup = QtWidgets.QPushButton("Duplicate")
        btn_dup.clicked.connect(self.run_duplicate_uv)
        row_crud2.addWidget(btn_ren)
        row_crud2.addWidget(btn_dup)
        manager_layout.addLayout(row_crud2)

        # Copy
        btn_copy = QtWidgets.QPushButton("Copy UVs (1st to Rest)")
        btn_copy.setFixedHeight(30)
        btn_copy.clicked.connect(self.run_copy_uvs)
        manager_layout.addWidget(btn_copy)
        
        grp_manager.setContentLayout(manager_layout)
        layout.addWidget(grp_manager)

        # --- MATERIALS ---
        grp_mat = CollapsibleBox("Material Utilities")
        mat_content = QtWidgets.QWidget()
        mat_layout = QtWidgets.QHBoxLayout(mat_content)
        
        self.btn_checker = QtWidgets.QPushButton("Apply Checker")
        self.btn_checker.clicked.connect(self.run_apply_checker)
        mat_layout.addWidget(self.btn_checker)
        
        self.btn_reset_mat = QtWidgets.QPushButton("Reset Material")
        self.btn_reset_mat.clicked.connect(self.run_reset_material)
        mat_layout.addWidget(self.btn_reset_mat)
        
        grp_mat.setContentLayout(mat_layout)
        layout.addWidget(grp_mat)
        
        # --- AI TOOLKIT (Integrated) ---
        grp_ai = CollapsibleBox("AI Auto-Unwrap Toolkit")
        ai_content = QtWidgets.QWidget()
        ai_layout = QtWidgets.QVBoxLayout(ai_content)
        ai_layout.setSpacing(8)

        # 1. ANALYSIS
        ai_layout.addWidget(QtWidgets.QLabel("<b>1. Analysis & Seams</b>"))
        ana_row = QtWidgets.QHBoxLayout()
        self.lbl_ai_type = QtWidgets.QLabel("Type: Unknown")
        self.lbl_ai_type.setStyleSheet("color: #888;")
        ana_row.addWidget(self.lbl_ai_type)
        btn_ana = QtWidgets.QPushButton("Analyze")
        btn_ana.clicked.connect(self.run_ai_analysis)
        ana_row.addWidget(btn_ana)
        ai_layout.addLayout(ana_row)
        
        # Seam Viz
        vis_row = QtWidgets.QHBoxLayout()
        self.chk_viz_seam = QtWidgets.QCheckBox("Seams")
        self.chk_viz_seam.toggled.connect(self.run_toggle_seams)
        self.chk_viz_distort = QtWidgets.QCheckBox("Distortion")
        self.chk_viz_distort.toggled.connect(self.run_toggle_distort)
        vis_row.addWidget(self.chk_viz_seam)
        vis_row.addWidget(self.chk_viz_distort)
        ai_layout.addLayout(vis_row)

        ai_layout.addWidget(self.create_line())

        # 2. AUTO UNWRAP
        ai_layout.addWidget(QtWidgets.QLabel("<b>2. Primary Unwrap</b>"))
        
        # Options
        opt_grid = QtWidgets.QGridLayout()
        self.chk_flow = QtWidgets.QCheckBox("Mesh Flow")
        self.chk_flow.setChecked(True)
        self.chk_axis = QtWidgets.QCheckBox("Axis Align")
        self.chk_axis.setChecked(True)
        self.chk_seamless = QtWidgets.QCheckBox("Seamless")
        opt_grid.addWidget(self.chk_flow, 0, 0)
        opt_grid.addWidget(self.chk_axis, 0, 1)
        opt_grid.addWidget(self.chk_seamless, 1, 0)
        ai_layout.addLayout(opt_grid)

        self.btn_auto_unwrap = QtWidgets.QPushButton("RUN AI UNWRAP")
        self.btn_auto_unwrap.setStyleSheet("background-color: #007acc; color: white; font-weight: bold; padding: 6px;")
        self.btn_auto_unwrap.clicked.connect(self.run_auto_unwrap_ai)
        ai_layout.addWidget(self.btn_auto_unwrap)

        # Manual Tools
        man_layout = QtWidgets.QHBoxLayout()
        btn_fix_o = QtWidgets.QPushButton("Fix Orient")
        btn_fix_o.clicked.connect(self.run_fix_orient)
        btn_sew = QtWidgets.QPushButton("Sew")
        btn_sew.clicked.connect(self.run_sew)
        btn_cut = QtWidgets.QPushButton("Cut")
        btn_cut.clicked.connect(self.run_cut)
        man_layout.addWidget(btn_fix_o)
        man_layout.addWidget(btn_sew)
        man_layout.addWidget(btn_cut)
        ai_layout.addLayout(man_layout)
        
        ai_layout.addWidget(self.create_line())

        # 3. ADVANCED SETS
        ai_layout.addWidget(QtWidgets.QLabel("<b>3. Engine Sets</b>"))
        
        # UV2 Lightmap
        lm_row = QtWidgets.QHBoxLayout()
        self.rb_ue = QtWidgets.QRadioButton("UE")
        self.rb_ue.setChecked(True)
        self.rb_unity = QtWidgets.QRadioButton("Unity")
        lm_row.addWidget(self.rb_ue)
        lm_row.addWidget(self.rb_unity)
        btn_lm = QtWidgets.QPushButton("Gen Lightmap UV2")
        btn_lm.clicked.connect(self.run_gen_lightmap)
        lm_row.addWidget(btn_lm)
        ai_layout.addLayout(lm_row)
        
        # UV3 AO
        ao_row = QtWidgets.QHBoxLayout()
        btn_ao = QtWidgets.QPushButton("Setup AO UV3")
        btn_ao.clicked.connect(self.run_ao_setup)
        ao_row.addWidget(btn_ao)
        
        btn_promote = QtWidgets.QPushButton("Promote UV3")
        btn_promote.clicked.connect(self.run_promote_uv3)
        ao_row.addWidget(btn_promote)
        
        btn_bake = QtWidgets.QPushButton("Bake AO")
        btn_bake.clicked.connect(self.run_bake_ao)
        ao_row.addWidget(btn_bake)
        
        ai_layout.addLayout(ao_row)
        
        ai_layout.addWidget(self.create_line())

        # 4. LAYOUT & PACKING
        ai_layout.addWidget(QtWidgets.QLabel("<b>4. Layout & Packing</b>"))
        
        # Row 1: Settings
        sett_row = QtWidgets.QHBoxLayout()
        
        # Resolution
        self.combo_res = QtWidgets.QComboBox()
        self.combo_res.addItems(["256", "512", "1024", "2048", "4096"])
        self.combo_res.setCurrentIndex(2) # 1024 default
        sett_row.addWidget(QtWidgets.QLabel("Map Size:"))
        sett_row.addWidget(self.combo_res)
        
        # Padding (Pixels)
        self.spin_pad = QtWidgets.QSpinBox()
        self.spin_pad.setRange(0, 128)
        self.spin_pad.setValue(4) # Default 4 pixels (TD Standard)
        self.spin_pad.setSuffix(" px")
        sett_row.addWidget(QtWidgets.QLabel("Padding:"))
        sett_row.addWidget(self.spin_pad)
        
        ai_layout.addLayout(sett_row)
        
        # Row 2: Options
        opt_row = QtWidgets.QHBoxLayout()
        self.chk_rot90 = QtWidgets.QCheckBox("Rotate 90° (Rectilinear)")
        self.chk_rot90.setChecked(True)
        opt_row.addWidget(self.chk_rot90)
        ai_layout.addLayout(opt_row)

        # Row 3: Buttons
        pack_row = QtWidgets.QHBoxLayout()
        btn_pack = QtWidgets.QPushButton("Layout")
        btn_pack.setStyleSheet("font-weight: bold; background-color: #444; height: 30px;")
        btn_pack.clicked.connect(self.run_pack_final)
        
        btn_val_pack = QtWidgets.QPushButton("Validate")
        btn_val_pack.clicked.connect(self.run_validate_pack)
        
        pack_row.addWidget(btn_pack)
        pack_row.addWidget(btn_val_pack)
        ai_layout.addLayout(pack_row)
        
        grp_ai.setContentLayout(ai_layout)
        layout.addWidget(grp_ai)
        
        # --- DENSITY ---
        grp_dent = CollapsibleBox("Texel Density")
        dent_content = QtWidgets.QWidget()
        dent_layout = QtWidgets.QHBoxLayout(dent_content)
        
        self.spin_density = QtWidgets.QDoubleSpinBox()
        self.spin_density.setRange(0.1, 1000.0)
        self.spin_density.setValue(10.24) # 1024px / 100cm = 10.24 px/cm
        self.spin_density.setSuffix(" px/cm")
        dent_layout.addWidget(self.spin_density)
        
        self.btn_set_density = QtWidgets.QPushButton("Set Density")
        self.btn_set_density.clicked.connect(self.run_set_density)
        dent_layout.addWidget(self.btn_set_density)
        
        grp_dent.setContentLayout(dent_layout)
        layout.addWidget(grp_dent)
        layout.addStretch()

    def create_line(self):
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Sunken)
        line.setStyleSheet("background-color: #444;")
        return line

    def run_overlap_check(self):
        try:
            from ..core import uv_tools
            # Get selection
            sel = cmds.ls(sl=True) if cmds else []
            if not sel:
                QtWidgets.QMessageBox.warning(self, "Warning", "Please select objects.")
                return

            violations = uv_tools.check_overlaps(sel)
            if violations:
                count = sum(v['count'] for v in violations)
                QtWidgets.QMessageBox.warning(self, "Overlaps Found", f"Found {count} overlapping components in {len(violations)} objects.")
                # Select them?
                # The check might select components.
            else:
                QtWidgets.QMessageBox.information(self, "UV Check", "No Overlaps Detected.")
        except Exception as e:
            logger.error(f"Error: {e}")

    def run_bounds_check(self):
        try:
            from ..core import uv_tools
            sel = cmds.ls(sl=True) if cmds else []
            if not sel:
                QtWidgets.QMessageBox.warning(self, "Warning", "Please select objects.")
                return

            violations = uv_tools.check_bounds(sel)
            if violations:
                msg = "\n".join([f"{v['object']}: {v['issue']}" for v in violations])
                QtWidgets.QMessageBox.warning(self, "Bounds Issues", f"Found issues:\n{msg}")
            else:
                QtWidgets.QMessageBox.information(self, "UV Check", "All UVs within 0-1 range.")
        except Exception as e:
             logger.error(f"Error: {e}")

    def run_auto_unwrap(self):
        try:
            from ..core import uv_tools
            sel = cmds.ls(sl=True) if cmds else []
            if not sel:
                QtWidgets.QMessageBox.warning(self, "Warning", "Please select objects.")
                return
                
            # Use new Top-Level AI Unwrap
            result = uv_tools.smart_ai_unwrap(sel)
            if result:
                QtWidgets.QMessageBox.information(self, "Success", "Smart AI Unwrap Completed.")
            else:
                QtWidgets.QMessageBox.warning(self, "Failed", "Unwrap failed or nothing to process.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def run_set_density(self):
        try:
            from ..core import uv_tools
            sel = cmds.ls(sl=True) if cmds else []
            if not sel:
                QtWidgets.QMessageBox.warning(self, "Warning", "Please select objects.")
                return
            
            val = self.spin_density.value()
            result = uv_tools.set_texel_density(sel, density=val)
            if result:
                 QtWidgets.QMessageBox.information(self, "Success", f"Density set to {val} px/cm")
            else:
                 QtWidgets.QMessageBox.warning(self, "Info", "Could not set density (Unfold3D required).")
        except Exception as e:
             QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def run_apply_checker(self):
        try:
            from ..core import materials
            sel = cmds.ls(sl=True) if cmds else []
            if not sel:
                QtWidgets.QMessageBox.warning(self, "Warning", "Please select objects.")
                return
            
            materials.assign_checker_material(sel)
            self.log_msg("Applied Qyntara Checker Material.")
            
        except Exception as e:
            logger.error(f"Error: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def run_reset_material(self):
        try:
            from ..core import materials
            sel = cmds.ls(sl=True) if cmds else []
            if not sel:
                QtWidgets.QMessageBox.warning(self, "Warning", "Please select objects.")
                return
                
            materials.assign_default_material(sel)
            self.log_msg("Reset to Default Material.")
            
        except Exception as e:
             logger.error(f"Error: {e}")
             QtWidgets.QMessageBox.critical(self, "Error", str(e))

    # --- UV SET MANAGER SLOTS ---
    def _get_selection(self):
        # Return full paths to ensure uniqueness and proper handling by ls commands
        return cmds.ls(sl=True, long=True) if cmds else []

    def run_switch_uv_index(self, index):
        try:
            from ..core import uv_tools
            uv_tools.switch_uv_set_index(self._get_selection(), index)
            self.log_msg(f"Switched to UV Channel {index+1}")
        except Exception as e:
            logger.error(f"Switch failed: {e}")

    def run_move_uv(self, direction):
        try:
            from ..core import uv_tools
            uv_tools.move_uv_set(self._get_selection(), direction)
            self.log_msg(f"Moved UV set {direction}")
        except Exception as e:
            logger.error(f"Move failed: {e}")

    def run_add_uv(self):
        try:
            from ..core import uv_tools
            uv_tools.add_new_uv_set(self._get_selection())
            self.log_msg("Added new UV set")
        except Exception as e:
            logger.error(f"Add failed: {e}")

    def run_delete_uv(self):
        try:
            from ..core import uv_tools
            uv_tools.delete_current_uv_set(self._get_selection())
            self.log_msg("Deleted current UV set")
        except Exception as e:
            logger.error(f"Delete failed: {e}")

    def run_rename_uv(self):
        from ..core import uv_tools
        try:
            sel = self._get_selection()
            if not sel: return
            
            text, ok = QtWidgets.QInputDialog.getText(self, "Rename UV Set", "New UV Set Name:")
            if ok and text:
                uv_tools.rename_current_uv_set(sel, text)
                self.log_msg(f"Renamed UV set to {text}")
        except Exception as e:
            logger.error(f"Rename failed: {e}")

    def run_duplicate_uv(self):
        try:
            from ..core import uv_tools
            uv_tools.duplicate_current_uv_set(self._get_selection())
            self.log_msg("Duplicated UV set")
        except Exception as e:
            logger.error(f"Duplicate failed: {e}")

    def run_copy_uvs(self):
        try:
            from ..core import uv_tools
            sel = self._get_selection()
            if len(sel) < 2:
                QtWidgets.QMessageBox.warning(self, "Warning", "Select Source then Targets (2+ objects)")
                return
            
            source = sel[0]
            targets = sel[1:]
            uv_tools.copy_uvs_to_others(source, targets)
            self.log_msg(f"Copied UVs from {source} to {len(targets)} objects")
        except Exception as e:
            logger.error(f"Copy failed: {e}")

    def log_msg(self, msg):
        # Helper to log to parent if possible, or print
        try:
            parent = self.window()
            if hasattr(parent, 'log'):
                parent.log(msg)
        except: pass

    # --- AI TOOLKIT HANDLERS ---
    def run_ai_analysis(self):
        try:
            sel = self._get_selection()
            if not sel: return
            res = self.ai.analyze_mesh_topology(sel)
            if res:
                first = list(res.values())[0]
                self.lbl_ai_type.setText(f"Type: {first['type']}")
                if first['warnings']:
                    self.log_msg(f"Analysis: {len(first['warnings'])} warnings detected.")
                else:
                    self.log_msg("Analysis: Clean Topology.")
        except Exception as e: logger.error(e)

    def run_toggle_seams(self, checked):
        sel = self._get_selection()
        if sel: visualizer.QyntaraVisualizer.toggle_seam_overlay(sel, checked)
        
    def run_toggle_distort(self, checked):
        sel = self._get_selection()
        if sel: visualizer.QyntaraVisualizer.toggle_distortion_heatmap(sel, checked)

    def run_auto_unwrap_ai(self):
        try:
            sel = self._get_selection()
            if not sel: return
            # Gather params
            res = uv_tools.smart_ai_unwrap(
                sel,
                flow=self.chk_flow.isChecked(),
                axis=self.chk_axis.isChecked(),
                seamless=self.chk_seamless.isChecked()
            )
            self.log_msg("AI Unwrap Completed.")
        except Exception as e:
            logger.error(f"AI Unwrap Error: {e}")
            
    def run_gen_lightmap(self):
        sel = self._get_selection()
        if not sel: return
        eng = "unreal" if self.rb_ue.isChecked() else "unity"
        uv_tools.generate_lightmap_uvs(sel, engine=eng)
        self.log_msg(f"Generated UV2 ({eng})")

    def run_ao_setup(self):
        sel = self._get_selection()
        if sel: 
            uv_tools.setup_ao_uvs(sel)
            self.log_msg("Setup 'AO' UV Set (UV3)")

    def run_promote_uv3(self):
        sel = self._get_selection()
        if sel:
            # Promote "AO" set to Primary
            uv_tools.promote_uv_to_primary(sel, "AO")
            self.log_msg("Promoted 'AO' set to Primary")

    def run_bake_ao(self):
        sel = self._get_selection()
        if sel:
            baking.bake_ao_map(sel, "AO")
            self.log_msg("Bake Process Initiated for 'AO'...")

    def run_pack_final(self):
        try:
            sel = self._get_selection()
            if sel:
                # Get settings from UI
                pixels = self.spin_pad.value()
                res = int(self.combo_res.currentText())
                rotate = self.chk_rot90.isChecked()
                
                # Convert Pixels to UV Ratio (0-1)
                # padding_ratio = pixels / resolution
                padding_ratio = pixels / float(res)

                # Use our new robust "Orient & Pack" function
                uv_tools.pack_uvs_rectilinear(sel, spacing=padding_ratio, resolution=res, rotate=rotate)
                
                mode_str = "Rectilinear" if rotate else "Standard"
                self.log_msg(f"Layout Complete ({mode_str}, Pad={pixels}px @ {res})")
        except Exception as e:
            self.log_msg(f"Layout Error: {e}")

    def run_validate_pack(self):
         sel = self._get_selection()
         if sel:
             res = uv_tools.validate_packing(sel)
             self.log_msg(f"Pack Validation: {res.get('status','?')}")

    # --- MANUAL TOOLS ---
    def run_fix_orient(self):
        try: 
            import maya.mel as mel
            mel.eval("texOrientShells")
        except: pass

    def run_sew(self):
        if cmds: cmds.polyMapSew(ch=False)

    def run_cut(self):
        if cmds: cmds.polyMapCut(ch=False)
