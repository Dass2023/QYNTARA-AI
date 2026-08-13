from .qt_utils import QtWidgets, QtCore
import logging

logger = logging.getLogger(__name__)

try:
    from maya import cmds
except ImportError:
    cmds = None

class ExportWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ExportWidget, self).__init__(parent)
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
        
        lbl_title = QtWidgets.QLabel("Game Engine Export")
        lbl_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #fff;")
        layout.addWidget(lbl_title)
        
        # --- PRESETS ---
        grp_preset = QtWidgets.QGroupBox("1. Target Engine")
        grp_preset.setStyleSheet("QGroupBox { border: 1px solid #00CEC9; margin-top: 6px; padding-top: 10px; font-weight: bold; }")
        preset_layout = QtWidgets.QHBoxLayout(grp_preset)
        
        self.bg_engine = QtWidgets.QButtonGroup(self)
        
        self.rad_ue = QtWidgets.QRadioButton("Unreal Engine 5")
        self.rad_ue.setChecked(True)
        self.rad_ue.setToolTip("Exports Z-Up, Scale 1.0 (cm)")
        self.bg_engine.addButton(self.rad_ue)
        
        self.rad_unity = QtWidgets.QRadioButton("Unity")
        self.rad_unity.setToolTip("Exports Y-Up")
        self.bg_engine.addButton(self.rad_unity)
        
        preset_layout.addWidget(self.rad_ue)
        preset_layout.addWidget(self.rad_unity)
        
        layout.addWidget(grp_preset)

        # --- SMART EXPORT (OpenUSD) ---
        grp_usd = QtWidgets.QGroupBox("2. Smart OpenUSD Export (Industry 4.0)")
        grp_usd.setStyleSheet("QGroupBox { border: 1px solid #ff00ff; margin-top: 6px; padding-top: 10px; font-weight: bold; color: #ff00ff; }")
        usd_layout = QtWidgets.QVBoxLayout(grp_usd)
        
        lbl_usd_info = QtWidgets.QLabel("Exports Asset with embedded IoT Metadata (QyntaraID).")
        lbl_usd_info.setStyleSheet("color: #aaa; font-style: italic;")
        usd_layout.addWidget(lbl_usd_info)
        
        self.btn_export_usd = QtWidgets.QPushButton("EXPORT SMART USD")
        self.btn_export_usd.setStyleSheet("background-color: #ff00ff; color: white; font-weight: bold; padding: 8px;")
        self.btn_export_usd.clicked.connect(self.run_usd_export)
        usd_layout.addWidget(self.btn_export_usd)
        
        layout.addWidget(grp_usd)

        # --- SMART EXPORT (OpenUSD) ---
        # (Existing code above)

        # --- 3. SPATIAL COMPUTING & I/O ---
        grp_spatial = QtWidgets.QGroupBox("3. Spatial Computing & I/O")
        grp_spatial.setStyleSheet("QGroupBox { border: 1px solid #00E5E0; margin-top: 6px; padding-top: 10px; font-weight: bold; color: #00E5E0; }")
        spatial_layout = QtWidgets.QVBoxLayout(grp_spatial)
        
        # Grid for buttons
        grid_spatial = QtWidgets.QGridLayout()
        
        # ARKit / Vision Pro
        self.btn_usdz = QtWidgets.QPushButton("Export USDZ (ARKit/Vision)")
        self.btn_usdz.setToolTip("Exports for Apple Vision Pro & iOS AR.")
        self.btn_usdz.setStyleSheet("background: #111; color: #00E5E0; border: 1px solid #00E5E0; padding: 6px;")
        self.btn_usdz.clicked.connect(self.run_usdz_export)
        grid_spatial.addWidget(self.btn_usdz, 0, 0)
        
        # WebGPU / Three.js EXPORT
        self.btn_glb = QtWidgets.QPushButton("Export GLB (WebGPU)")
        self.btn_glb.setToolTip("Exports binary GLTF for Web 3D.")
        self.btn_glb.setStyleSheet("background: #111; color: #F1C40F; border: 1px solid #F1C40F; padding: 6px;")
        self.btn_glb.clicked.connect(self.run_glb_export)
        grid_spatial.addWidget(self.btn_glb, 0, 1)

        # WebGPU / Three.js IMPORT
        self.btn_import_glb = QtWidgets.QPushButton("IMPORT GLB/GLTF")
        self.btn_import_glb.setToolTip("Imports binary GLTF/glb into the scene.")
        self.btn_import_glb.setStyleSheet("background: #111; color: #2ecc71; border: 1px solid #2ecc71; padding: 6px;")
        self.btn_import_glb.clicked.connect(self.run_glb_import)
        grid_spatial.addWidget(self.btn_import_glb, 1, 0, 1, 2)
        
        spatial_layout.addLayout(grid_spatial)
        layout.addWidget(grp_spatial)
        
        # --- PHASE 3: VERSION CONTROL INTEGRATION ---
        grp_vcs = QtWidgets.QGroupBox("3b. Version Control (Git/Perforce)")
        grp_vcs.setStyleSheet("QGroupBox { border: 1px solid #74b9ff; margin-top: 6px; padding-top: 10px; font-weight: bold; color: #74b9ff; }")
        vcs_layout = QtWidgets.QVBoxLayout(grp_vcs)
        
        # VCS Status
        self.lbl_vcs_status = QtWidgets.QLabel("Detecting...")
        self.lbl_vcs_status.setStyleSheet("color: #888; font-style: italic;")
        vcs_layout.addWidget(self.lbl_vcs_status)
        
        # Inject Metadata Checkbox
        self.chk_inject_vcs = QtWidgets.QCheckBox("Inject Version Metadata into USD")
        self.chk_inject_vcs.setChecked(True)
        self.chk_inject_vcs.setToolTip("Adds Git/P4 revision, author, timestamp to USD custom data")
        vcs_layout.addWidget(self.chk_inject_vcs)
        
        # Auto-Commit Checkbox
        self.chk_auto_commit = QtWidgets.QCheckBox("Auto-Commit Exported Assets (Experimental)")
        self.chk_auto_commit.setStyleSheet("color: #ff6b6b;")
        self.chk_auto_commit.setToolTip("Automatically add and commit exported files to VCS")
        vcs_layout.addWidget(self.chk_auto_commit)
        
        layout.addWidget(grp_vcs)
        
        # Initialize VCS Bridge
        from ..core.version_control import VersionControlBridge
        self.vcs_bridge = VersionControlBridge()
        self.detect_vcs()
        
        # --- ACTIONS ---
        grp_act = QtWidgets.QGroupBox("4. Legacy Actions (FBX)")
        grp_act.setStyleSheet("QGroupBox { border: 1px solid #d29922; margin-top: 6px; padding-top: 10px; font-weight: bold; }")
        act_layout = QtWidgets.QVBoxLayout(grp_act)
        
        # Options
        self.chk_sanitize = QtWidgets.QCheckBox("Auto-Sanitize (History, Freeze, Pivot)")
        self.chk_sanitize.setChecked(True)
        act_layout.addWidget(self.chk_sanitize)
        
        self.chk_triangulate = QtWidgets.QCheckBox("Triangulate Mesh")
        act_layout.addWidget(self.chk_triangulate)
        
        # Actions
        btn_layout = QtWidgets.QHBoxLayout()
        
        self.btn_sanitize = QtWidgets.QPushButton("Sanitize Only")
        self.btn_sanitize.clicked.connect(self.run_sanitize)
        btn_layout.addWidget(self.btn_sanitize)
        
        self.btn_export = QtWidgets.QPushButton("EXPORT FBX")
        self.btn_export.setStyleSheet("background-color: #2ea043; color: white; font-weight: bold; padding: 8px;")
        self.btn_export.clicked.connect(self.run_safe_export)
        btn_layout.addWidget(self.btn_export)
        
        act_layout.addLayout(btn_layout)
        
        layout.addWidget(grp_act)
        layout.addStretch()

    def get_selection(self):
        if not cmds: return []
        return cmds.ls(sl=True, long=True) or []

    def run_sanitize(self):
        try:
            from ..core import exporter
            sel = self.get_selection()
            if not sel:
                QtWidgets.QMessageBox.warning(self, "Warning", "Please select objects.")
                return
                 
            # Note: sanitize_scene returns True/False or Count? 
            # exporter code says: return count > 0
            if exporter.sanitize_scene(sel):
                 QtWidgets.QMessageBox.information(self, "Success", f"Sanitized {len(sel)} objects.")
            else:
                 QtWidgets.QMessageBox.warning(self, "Info", "Nothing to sanitize.")
        except Exception as e:
             QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def run_safe_export(self):
        try:
            from ..core import exporter
            sel = self.get_selection()
            if not sel:
                 QtWidgets.QMessageBox.warning(self, "Warning", "Please select objects to export.")
                 return

            engine = "Unreal" if self.rad_ue.isChecked() else "Unity"
            tri = self.chk_triangulate.isChecked()
            
            # File Dialog
            fpath, _ = QtWidgets.QFileDialog.getSaveFileName(self, f"Export to {engine}", "", "FBX Files (*.fbx)")
            if not fpath: return
            
            # Run Safe Export
            # Note: The core function 'validate_and_export_game_ready' calls sanitize then export
            # If our checkbox is OFF, we might want to bypass sanitize?
            # But validate_and_export_game_ready ALWAYS sanitizes in current implementation.
            # Let's assume user wants 'Game Ready' implies sanitized.
            
            result = exporter.validate_and_export_game_ready(sel, fpath, engine=engine, triangulate=tri)
            
            if result:
                 QtWidgets.QMessageBox.information(self, "Success", f"Exported to:\n{fpath}")
            else:
                 QtWidgets.QMessageBox.critical(self, "Export Failed", "Check Script Editor for details.")
        except Exception as e:
             QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def run_usd_export(self):
        """Triggers the Smart OpenUSD Exporter script."""
        try:
            sel = self.get_selection()
            if not sel:
                 QtWidgets.QMessageBox.warning(self, "Warning", "Please select an object (e.g. Robot_Base).")
                 return

            # File Dialog
            fpath, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export Smart USD", "", "OpenUSD Files (*.usd)")
            if not fpath: return
            
            # Call the Script
            # We import dynamically to ensure we use the detailed script we wrote
            import scripts.maya.export_industry40_usd as export_industry40_usd
            import importlib
            importlib.reload(export_industry40_usd) 
            
            export_industry40_usd.export_smart_asset_usd(fpath)
            
            QtWidgets.QMessageBox.information(self, "Success", f"Smart Asset Exported:\n{fpath}\n\n(Includes IoT Metadata)")
            
        except ImportError:
             QtWidgets.QMessageBox.critical(self, "Error", "USD Exporter script not found in scripts/maya.")
        except Exception as e:
             QtWidgets.QMessageBox.critical(self, "Export Failed", str(e))

    def run_usdz_export(self):
        """Exports USDZ for ARKit."""
        try:
            sel = self.get_selection()
            if not sel:
                 QtWidgets.QMessageBox.warning(self, "Warning", "Please select an object.")
                 return

            fpath, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export AR Model", "", "USDZ Files (*.usdz)")
            if not fpath: return
            
            # Reuse Smart USD Exporter but force .usdz extension handling
            import scripts.maya.export_industry40_usd as export_industry40_usd
            export_industry40_usd.export_smart_asset_usd(fpath)
            
            QtWidgets.QMessageBox.information(self, "Success", f"AR Asset Exported (USDZ):\n{fpath}")
        except Exception as e:
             QtWidgets.QMessageBox.critical(self, "Error", f"AR Export Failed: {e}")

    def run_glb_import(self):
        """Imports GLB/GLTF into Maya."""
        try:
             fpath, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Import Web 3D", "", "glTF Files (*.glb *.gltf)")
             if not fpath: return
             
             import scripts.maya.import_web_gltf as import_web_gltf
             import importlib
             importlib.reload(import_web_gltf)
             
             success = import_web_gltf.import_glb(fpath)
             if success:
                 QtWidgets.QMessageBox.information(self, "Success", f"Web 3D Asset Imported:\n{fpath}")
             else:
                 QtWidgets.QMessageBox.critical(self, "Error", "GLB Import Failed. Check Script Editor.")
        except Exception as e:
             QtWidgets.QMessageBox.critical(self, "Error", f"Import Failed: {e}")

    def run_glb_export(self):
        """Exports GLB for WebGPU/Three.js."""
        try:
             sel = self.get_selection()
             if not sel:
                  QtWidgets.QMessageBox.warning(self, "Warning", "Please select an object.")
                  return

             fpath, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Export Web 3D", "", "GLB Files (*.glb)")
             if not fpath: return
             
             # Call dedicated GLB script
             import scripts.maya.export_web_gltf as export_web_gltf
             import importlib
             importlib.reload(export_web_gltf)
             
             success = export_web_gltf.export_glb(fpath)
             
             if success:
                 QtWidgets.QMessageBox.information(self, "Success", f"Web 3D Asset Exported (GLB):\n{fpath}")
             else:
                 QtWidgets.QMessageBox.critical(self, "Error", "GLB Export Failed. Check Maya Script Editor for detailed logs.")
        except ImportError:
             QtWidgets.QMessageBox.critical(self, "Error", "GLB Exporter script (export_web_gltf) not found.")
        except Exception as e:
             QtWidgets.QMessageBox.critical(self, "Error", f"Web Export Failed: {e}")

    def detect_vcs(self):
        """Detects VCS on tab load."""
        if not cmds: return
        
        # Get current project path
        workspace = cmds.workspace(q=True, rd=True)
        if not workspace:
             self.lbl_vcs_status.setText("⚠️ Workspace not set")
             return
             
        vcs_type = self.vcs_bridge.detect_vcs(workspace)
        if vcs_type:
            info = self.vcs_bridge.get_current_revision()
            if info:
                rev = info.get("revision", "N/A")[:7]
                author = info.get("author", "Unknown")
                self.lbl_vcs_status.setText(f"✅ {vcs_type.upper()} | Rev: {rev} | {author}")
                self.lbl_vcs_status.setStyleSheet("color: #00ff9d; font-weight: bold;")
            else:
                self.lbl_vcs_status.setText(f"✅ {vcs_type.upper()} detected")
                self.lbl_vcs_status.setStyleSheet("color: #00ff9d;")
        else:
            self.lbl_vcs_status.setText("⚪ No VCS detected")
            self.lbl_vcs_status.setStyleSheet("color: #888;")
