from .qt_utils import QtWidgets, QtCore, QtGui, get_maya_window
from . import style
import webbrowser
import maya.OpenMayaUI as omui
try:
    from shiboken6 import wrapInstance
except ImportError:
    from shiboken import wrapInstance

import importlib
from ..core import validator, fixer, visualizer, llm_assistant

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class RuleWidget(QtWidgets.QFrame):
    fixRequested = QtCore.Signal(str) 

    def __init__(self, rule_data, parent=None):
        super(RuleWidget, self).__init__(parent)
        self.rule_data = rule_data
        self.setObjectName("ruleItem")
        
        # Context Menu
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.checkbox = QtWidgets.QCheckBox()
        self.checkbox.setChecked(rule_data.get("enabled", True))
        layout.addWidget(self.checkbox)
        
        text_layout = QtWidgets.QVBoxLayout()
        text_layout.setSpacing(2)
        
        header_row = QtWidgets.QHBoxLayout()
        self.lbl_name = QtWidgets.QLabel(f"<b>{rule_data['label']}</b>")
        self.lbl_name.setStyleSheet("font-size: 13px; color: #fff;")
        header_row.addWidget(self.lbl_name)
        header_row.addStretch()
        text_layout.addLayout(header_row)
        
        self.lbl_desc = QtWidgets.QLabel(rule_data.get("description", ""))
        self.lbl_desc.setStyleSheet("color: #888; font-size: 11px;")
        text_layout.addWidget(self.lbl_desc)
        
        layout.addLayout(text_layout)
        layout.addStretch()
        
        self.lbl_status = QtWidgets.QLabel("READY")
        self.lbl_status.setStyleSheet("color: #666; font-weight: bold; background: #2d2d30; padding: 4px 8px; border-radius: 4px;")
        layout.addWidget(self.lbl_status)

    def show_context_menu(self, pos):
        menu = QtWidgets.QMenu(self)
        fix_action = menu.addAction("Auto-Fix Issue")
        fix_action.triggered.connect(lambda: self.fixRequested.emit(self.rule_data['id']))
        menu.exec_(self.mapToGlobal(pos))
        
    def update_visuals(self, new_data):
        """Updates the widget based on new rule data (e.g. changed severity)."""
        self.rule_data.update(new_data)
        
        # Update Enabled State
        enabled = self.rule_data.get("enabled", True)
        self.checkbox.setChecked(enabled)
        self.setVisible(enabled) # Or just disable interaction? 
        # Hiding them entirely might be cleaner for "Profiles".
        
        # Start "Ready" State with correct severity hints if we wanted.
        severity = self.rule_data.get("severity", "error")
        # Maybe show an icon for severity?
        # For now, just ensuring it's enabled/visible is good.

    def set_status(self, violation_count, severity):
        if violation_count > 0:
            self.lbl_status.setText(f"{violation_count} ISSUES")
            color = "#ff5555" if severity == "error" else "#d29922"
            self.lbl_status.setStyleSheet(f"color: #fff; background: {color}; font-weight: bold; padding: 4px 8px; border-radius: 4px;")
            
            # Update frame style
            if severity == "error":
                self.setObjectName("ruleItemError")
            else:
                self.setObjectName("ruleItemWarning")
        else:
            self.lbl_status.setText("PASS")
            self.lbl_status.setStyleSheet("color: #fff; background: #2ea043; font-weight: bold; padding: 4px 8px; border-radius: 4px;")
            self.setObjectName("ruleItemPass")
            
        # Trigger stylesheet update
        self.style().unpolish(self)
        self.style().polish(self)
    
    def reset(self):
        self.lbl_status.setText("READY")
        self.lbl_status.setStyleSheet("color: #666; font-weight: bold; background: #2d2d30; padding: 4px 8px; border-radius: 4px;")
        self.setObjectName("ruleItem")
        self.style().unpolish(self)
        self.style().polish(self)

class DashboardHeader(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super(DashboardHeader, self).__init__(parent)
        # Gradient Background for Header - "Creative High Professional"
        self.setStyleSheet("""
            DashboardHeader {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #111, stop:1 #222);
                border-bottom: 2px solid #00CEC9;
            }
        """)
        
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20) # More whitespace
        layout.setSpacing(20)
        
        # 1. Icon (Left) - Perfectly centered vertically
        import os
        base_path = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base_path, 'resources', 'icon_brand.png')
        type_path = os.path.join(base_path, 'resources', 'type_brand.png')
        
        if os.path.exists(icon_path):
            icon_lbl = QtWidgets.QLabel()
            pix_icon = QtGui.QPixmap(icon_path)
            # Icon Size: 64px - Standard for standard app headers
            pix_icon = pix_icon.scaledToHeight(64, QtCore.Qt.SmoothTransformation)
            icon_lbl.setPixmap(pix_icon)
            icon_lbl.setAlignment(QtCore.Qt.AlignVCenter)
            layout.addWidget(icon_lbl)
        
        # 2. Typography & Subtitle Container
        brand_layout = QtWidgets.QVBoxLayout()
        brand_layout.setSpacing(4)
        brand_layout.setContentsMargins(0, 5, 0, 5) # Slight adjustment for alignment
        brand_layout.setAlignment(QtCore.Qt.AlignVCenter)
        
        if os.path.exists(type_path):
            type_lbl = QtWidgets.QLabel()
            pix_type = QtGui.QPixmap(type_path)
            # Text Size: 32px height relative to 64px icon looks balanced
            pix_type = pix_type.scaledToHeight(32, QtCore.Qt.SmoothTransformation)
            type_lbl.setPixmap(pix_type)
            type_lbl.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)
            brand_layout.addWidget(type_lbl)
        else:
             # Fallback
            ttl = QtWidgets.QLabel("QYNTARA AI")
            ttl.setObjectName("headerTitle")
            brand_layout.addWidget(ttl)

        # Subtitle - "Tagline" style
        sub = QtWidgets.QLabel("3D PRODUCTION SOLUTIONS")
        sub.setStyleSheet("""
            color: #00CEC9; 
            font-family: 'Segoe UI', sans-serif;
            font-size: 10px; 
            font-weight: 700; 
            letter-spacing: 3px;
            text-transform: uppercase;
        """)
        sub.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
        brand_layout.addWidget(sub)
        
        layout.addLayout(brand_layout)
        layout.addStretch()
        
        # 3. Health Widget (Right Side - Minimalist Pill Design)
        health_container = QtWidgets.QFrame()
        health_container.setStyleSheet("""
            background-color: rgba(0, 206, 201, 0.1);
            border: 1px solid rgba(0, 206, 201, 0.3);
            border-radius: 20px;
            padding: 5px 15px;
        """)
        health_layout = QtWidgets.QHBoxLayout(health_container)
        health_layout.setContentsMargins(10, 5, 10, 5)
        health_layout.setSpacing(10)
        
        lbl_status_text = QtWidgets.QLabel("SYSTEM OPTIMAL")
        lbl_status_text.setStyleSheet("color: #00CEC9; font-size: 10px; font-weight: bold; letter-spacing: 1px;") 
        
        self.lbl_health = QtWidgets.QLabel("100%")
        self.lbl_health.setObjectName("metricLabel")
        self.lbl_health.setStyleSheet("color: #fff; font-size: 18px; font-weight: bold;") 
        self.lbl_health.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        
        health_layout.addWidget(lbl_status_text)
        health_layout.addWidget(self.lbl_health)
        
        layout.addWidget(health_container)

    def set_health(self, percent):
        self.lbl_health.setText(f"{percent}%")
        if percent == 100:
            self.lbl_health.setStyleSheet("color: #2ea043; font-size: 32px; font-weight: bold;") 
        elif percent > 70:
            self.lbl_health.setStyleSheet("color: #d29922; font-size: 32px; font-weight: bold;")
        else:
            self.lbl_health.setStyleSheet("color: #f85149; font-size: 32px; font-weight: bold;")



class CollapsibleCategory(QtWidgets.QWidget):
    def __init__(self, title="", parent=None):
        super(CollapsibleCategory, self).__init__(parent)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 5, 0, 5)
        self.layout.setSpacing(0)

        # Header Button (Clickable Title)
        self.toggle_btn = QtWidgets.QPushButton(f"▼ {title}")
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(True)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                text-align: left; 
                background-color: #2d2d30; 
                color: #ddd; 
                font-weight: bold; 
                font-size: 12px;
                padding: 8px 10px; 
                border: 1px solid #3e3e42;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #3e3e42; }
        """)
        self.toggle_btn.toggled.connect(self.toggle_content)
        self.layout.addWidget(self.toggle_btn)

        # Content Area (Holds Rules)
        self.content_area = QtWidgets.QWidget()
        self.content_layout = QtWidgets.QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(10, 5, 5, 10) # Indent content
        self.content_layout.setSpacing(2)
        self.layout.addWidget(self.content_area)
        
        self.title = title

    def toggle_content(self, checked):
        # In this logic, Checked(True) = Expanded (Matches default)
        self.content_area.setVisible(checked)
        arrow = "▼" if checked else "▶"
        self.toggle_btn.setText(f"{arrow} {self.title}")

    def add_widget(self, widget):
        self.content_layout.addWidget(widget)


class AIMeshNetWidget(QtWidgets.QWidget):
    """
    Experimental Interface for MeshAnomalyNet.
    Allows TD/Artists to run deep learning scans on geometry.
    """
    def __init__(self, parent=None):
        super(AIMeshNetWidget, self).__init__(parent)
        
        self.ai = None # Lazy load
        self.init_ui()
        
    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 1. Header Area
        header = QtWidgets.QLabel("MeshAnomalyNet v0.9 (Beta)")
        header.setStyleSheet("color: #00CEC9; font-size: 16px; font-weight: bold;")
        layout.addWidget(header)
        
        desc = QtWidgets.QLabel(
            "Deep Learning Geometric Analysis.\n"
            "Detects subjective anomalies (topology flow, awkward poles) that rule-based checkers miss."
        )
        desc.setStyleSheet("color: #aaa; font-style: italic;")
        layout.addWidget(desc)
        
        # 2. Control Panel
        control_frame = QtWidgets.QFrame()
        control_frame.setStyleSheet("background: #2d2d30; border-radius: 8px;")
        c_layout = QtWidgets.QHBoxLayout(control_frame)
        
        self.btn_load_model = QtWidgets.QPushButton("Initialize Model")
        self.btn_load_model.clicked.connect(self.load_ai_model)
        self.btn_load_model.setStyleSheet("background: #444; color: #fff; padding: 8px;")
        
        self.btn_scan = QtWidgets.QPushButton("SCAN SELECTION")
        self.btn_scan.clicked.connect(self.run_scan)
        self.btn_scan.setEnabled(False)
        self.btn_scan.setStyleSheet("""
            QPushButton { background: #00CEC9; color: #000; font-weight: bold; padding: 8px; border-radius: 4px; }
            QPushButton:disabled { background: #444; color: #888; }
            QPushButton:hover { background: #00E5E0; }
        """)
        
        c_layout.addWidget(self.btn_load_model)
        c_layout.addWidget(self.btn_scan)
        layout.addWidget(control_frame)
        
        # 3. Results Area
        self.result_console = QtWidgets.QTextEdit()
        self.result_console.setReadOnly(True)
        self.result_console.setStyleSheet("background: #1e1e1e; color: #00FF00; font-family: 'Consolas'; font-size: 11px;")
        layout.addWidget(self.result_console)
        
        # 4. Visualization Controls
        vis_layout = QtWidgets.QHBoxLayout()
        self.btn_sel_bad = QtWidgets.QPushButton("Select Anomalous Vertices")
        self.btn_sel_bad.clicked.connect(self.select_artifacts)
        self.btn_sel_bad.setEnabled(False)
        vis_layout.addWidget(self.btn_sel_bad)
        layout.addLayout(vis_layout)
        
    def load_ai_model(self):
        self.result_console.append("> Initializing Neural Network...")
        try:
            from ..ai_assist.ai_interface import AIAssist
            self.ai = AIAssist()
            self.ai.load_models()
            self.btn_scan.setEnabled(True)
            self.btn_load_model.setText("Model Ready")
            self.btn_load_model.setEnabled(False)
            self.result_console.append("> Model Loaded Successfully.")
            if hasattr(self.ai, 'model'):
                 self.result_console.append(f"> Type: {type(self.ai.model).__name__}")
            else:
                 self.result_console.append("> Type: Heuristic Fallback (No PyTorch)")
        except Exception as e:
            self.result_console.append(f"> ERROR: {e}")

    def run_scan(self):
        if not self.ai: return
        
        from maya import cmds
        sel = cmds.ls(sl=True, long=True)
        if not sel:
            self.result_console.append("> Error: No selection.")
            return
            
        self.result_console.append(f"> Scanning {len(sel)} objects...")
        # Force UI update
        QtWidgets.QApplication.processEvents()
        
        results = self.ai.scan_selection(sel)
        self.last_results = results
        
        count_bad = 0
        for obj, data in results.items():
            score = data.get("score", 0)
            status = data.get("status", "UNKNOWN")
            self.result_console.append(f"[{obj}] Score: {score:.4f} -> {status}")
            
            if status == "ANOMALY_DETECTED":
                count_bad += 1
                
        if count_bad > 0:
             self.btn_sel_bad.setEnabled(True)
             self.result_console.append(f"> Found {count_bad} anomalous objects.")
        else:
             self.result_console.append("> Scan Complete. No anomalies found.")

    def select_artifacts(self):
        if not hasattr(self, 'last_results'): return
        
        from maya import cmds
        all_bad_verts = []
        for obj, data in self.last_results.items():
            heatmap = data.get("heatmap", [])
            for idx in heatmap:
                all_bad_verts.append(f"{obj}.vtx[{idx}]")
                
        if all_bad_verts:
            cmds.select(all_bad_verts)
            self.result_console.append(f"> Selected {len(all_bad_verts)} vertices.")


class QyntaraMainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(QyntaraMainWindow, self).__init__(parent=parent)
        self.setWindowFlags(QtCore.Qt.Window)
        
        self.setWindowTitle("Qyntara AI Validator - v2.1 (Fixed Layout)")
        self.resize(450, 700) # Force Compact Size
        
        
        # Main Layout (Will be initialized in init_ui with Central Widget)
        # main_layout = QtWidgets.QVBoxLayout(self) # REMOVED for QMainWindow

        
        self.validator = validator.QyntaraValidator()
        self.rule_widgets = {}
        self.category_widgets = {} # Store collapsible widgets
        self.last_report = None
        self.is_auto_fixing = False
        self._undo_job_id = None
        self.ai_assistant = llm_assistant.LLMAssistant(self) # New Brain
        
        # Register Undo Callback for Sync via scriptJob (Safer/Simpler than OM2)
        try:
             from maya import cmds
             # Using a stored function reference works with scriptJob
             self._undo_job_id = cmds.scriptJob(
                 event=["Undo", self._on_maya_undo]
             )
        except Exception as e:
             logger.warning(f"Failed to register Undo scriptJob: {e}")

        self.init_ui()
        self.setStyleSheet(style.STYLESHEET)
        
    def init_ui(self):
        # Master Container (Central Widget)
        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QtWidgets.QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0,0,0,0)
        main_layout.setSpacing(0)
        
        # 1. Header Area
        self.header = DashboardHeader()
        main_layout.addWidget(self.header)
        
        # Mode Selection
        mode_container = QtWidgets.QWidget()
        mode_layout = QtWidgets.QVBoxLayout(mode_container)
        mode_layout.setContentsMargins(10, 10, 10, 10)
        mode_layout.setSpacing(8)
        
        # ... Mode Combos ...
        # Row 1
        row1 = QtWidgets.QHBoxLayout()
        lbl_mode = QtWidgets.QLabel("Execution Mode:")
        lbl_mode.setStyleSheet("color: #aaa; min-width: 100px;")
        self.combo_mode = QtWidgets.QComboBox()
        self.combo_mode.addItem("Local Execution (Maya CPU)")
        self.combo_mode.addItem("Remote Execution (Docker GPU)")
        self.combo_mode.setStyleSheet("background: #252526; color: #fff; padding: 4px;")
        row1.addWidget(lbl_mode)
        row1.addWidget(self.combo_mode)
        row1.addStretch()
        mode_layout.addLayout(row1)
        
        # Row 2
        row2 = QtWidgets.QHBoxLayout()
        lbl_pipe = QtWidgets.QLabel("Target Pipeline:")
        lbl_pipe.setStyleSheet("color: #aaa; min-width: 100px;")
        self.combo_pipeline = QtWidgets.QComboBox()
        self.combo_pipeline.addItems(["Game Engine (Unreal/Unity)", "AR / VR / Mobile", "VFX / High-Poly", "Web 3D"])
        self.combo_pipeline.setStyleSheet("background: #252526; color: #00CEC9; padding: 4px; font-weight: bold;")
        self.combo_pipeline.currentIndexChanged.connect(self.update_pipeline_rules)
        row2.addWidget(lbl_pipe)
        row2.addWidget(self.combo_pipeline)
        row2.addStretch()
        mode_layout.addLayout(row2)
        
        main_layout.addWidget(mode_container)
        
        # 2. Main Content Area (Tabs)
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setDocumentMode(True)
        # Using stretch factor 1 here via addWidget overload for VBox
        main_layout.addWidget(self.tabs, 1) 
        
        # --- TAB 0: INDUSTRY 4.0 (NEW) ---
        from .industry_40_tab import Industry40Tab
        self.tab_industry40 = Industry40Tab()
        self.tabs.addTab(self.tab_industry40, "INDUSTRY 4.0")

        # --- TAB 1: INDUSTRY 5.0 ---
        from .industry_50_tab import Industry50Tab
        self.tab_industry50 = Industry50Tab()
        self.tabs.addTab(self.tab_industry50, "INDUSTRY 5.0")
        
        # --- TAB 2: VALIDATION ---
        self.tab_validator = QtWidgets.QWidget()
        val_wrapper = QtWidgets.QVBoxLayout(self.tab_validator)
        val_wrapper.setContentsMargins(0,0,0,0)
        
        self.val_scroll = QtWidgets.QScrollArea()
        self.val_scroll.setWidgetResizable(True)
        self.val_scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        
        self.val_content = QtWidgets.QWidget()
        self.val_layout = QtWidgets.QVBoxLayout(self.val_content)
        self.val_layout.setSpacing(2)
        self.val_layout.setContentsMargins(5,5,5,5)
        # self.val_layout.addStretch() # keep commented
        
        self.val_scroll.setWidget(self.val_content)
        val_wrapper.addWidget(self.val_scroll)
        
        self.tabs.addTab(self.tab_validator, "Validation")
        self.tabs.currentChanged.connect(self.on_tab_changed)

        # Other Tabs
        from .alignment_tab import AlignmentWidget
        self.tab_align = AlignmentWidget()
        self.tabs.addTab(self.tab_align, "Alignment")
        
        from .uv_tab import UVToolsWidget
        self.tab_uv = UVToolsWidget()
        self.tabs.addTab(self.tab_uv, "UVs")

        from .baking_tab import BakingWidget
        self.tab_baking = BakingWidget()
        self.tabs.addTab(self.tab_baking, "Baking")
        
        from .export_tab import ExportWidget
        self.tab_export = ExportWidget()
        self.tabs.addTab(self.tab_export, "Export")

        from .scanner_tab import ScannerWidget
        self.tab_scanner = ScannerWidget()
        self.tabs.addTab(self.tab_scanner, "Scanner")

        from .blueprint_tab import BlueprintWidget
        self.tab_blueprint = BlueprintWidget()
        self.tabs.addTab(self.tab_blueprint, "Blueprint Studio")


        # 3. Footer Area (Buttons + Chat + Log)
        bottom_frame = QtWidgets.QFrame()
        bottom_frame.setObjectName("bottomFrame")
        bottom_layout = QtWidgets.QVBoxLayout(bottom_frame)
        bottom_layout.setContentsMargins(5, 5, 5, 5)

        # 3.1 CONTEXT ACTION BAR (Validation Buttons)
        self.val_action_frame = QtWidgets.QFrame()
        self.val_action_frame.setObjectName("contextActionFrame")
        self.val_action_frame.setStyleSheet("""
            QFrame#contextActionFrame {
                background: #222;
                border: 1px solid #444;
                border-radius: 4px;
                min-height: 40px;
                margin-bottom: 5px;
            }
        """)
        c_layout = QtWidgets.QHBoxLayout(self.val_action_frame)
        c_layout.setContentsMargins(5,5,5,5)
        
        self.btn_load = QtWidgets.QPushButton("LOAD")
        self.btn_load.clicked.connect(self.load_scene)
        self.btn_validate = QtWidgets.QPushButton("VALIDATE") 
        self.btn_validate.clicked.connect(self.run_validation)
        self.btn_fix = QtWidgets.QPushButton("AUTO-FIX")
        self.btn_fix.setObjectName("btn_accent")
        self.btn_fix.clicked.connect(self.auto_fix)
        self.btn_fix.setEnabled(True) # DEBUG: Force Enabled to see if it renders
        self.btn_undo = QtWidgets.QPushButton("UNDO")
        self.btn_undo.setObjectName("btn_warning")
        self.btn_undo.clicked.connect(self.undo_last_fix)
        self.btn_undo.setEnabled(True) # DEBUG: Force Enabled
        self.btn_html_report = QtWidgets.QPushButton("REPORT")
        self.btn_html_report.clicked.connect(self.generate_visual_report)
        self.btn_html_report.setEnabled(True) # DEBUG: Force Enabled
        
        # Styles...
        self.btn_load.setStyleSheet("background: #444; color: white; font-weight: bold;")
        self.btn_validate.setStyleSheet("background: #007acc; color: white; font-weight: bold;")
        self.btn_fix.setStyleSheet("background: #27ae60; color: white; font-weight: bold;")
        self.btn_undo.setStyleSheet("background: #e67e22; color: white; font-weight: bold;")
        self.btn_html_report.setStyleSheet("background: #8e44ad; color: white; font-weight: bold;")

        c_layout.addWidget(self.btn_load)
        c_layout.addWidget(self.btn_validate)
        c_layout.addWidget(self.btn_fix)
        c_layout.addWidget(self.btn_undo)
        c_layout.addWidget(self.btn_html_report)
        
        bottom_layout.addWidget(self.val_action_frame)

        # 3.2 AI Command Bar
        cmd_frame = QtWidgets.QFrame()
        cmd_frame.setStyleSheet("background: #1e1e1e; border-top: 1px solid #333; padding: 2px;")
        cmd_layout = QtWidgets.QHBoxLayout(cmd_frame)
        cmd_layout.setContentsMargins(2, 2, 2, 2)
        
        self.btn_mic = QtWidgets.QPushButton("🎙️")
        self.btn_mic.setToolTip("Voice Command (Push to Talk)")
        self.btn_mic.setCheckable(True)
        self.btn_mic.setStyleSheet("""
            QPushButton {
                background: #2d2d30; 
                color: #00CEC9; 
                border: 1px solid #444; 
                border-radius: 12px;
                font-size: 16px;
                min-width: 30px;
                min-height: 24px;
            }
            QPushButton:checked {
                background: #ff003c;
                color: #fff;
                border: 1px solid #ff003c;
            }
            QPushButton:hover { border: 1px solid #00CEC9; }
        """)
        self.btn_mic.clicked.connect(self.toggle_voice_listen)
        
        self.txt_ai_command = QtWidgets.QLineEdit()
        self.txt_ai_command.setPlaceholderText("Ask Qyntara... (Type or Click Mic)")
        self.txt_ai_command.setStyleSheet("""
            QLineEdit {
                background: #2d2d30; 
                color: #00CEC9; 
                border: 1px solid #444; 
                border-radius: 12px;
                padding: 4px 10px;
                font-family: 'Segoe UI', sans-serif;
            }
            QLineEdit:focus { border: 1px solid #00CEC9; }
        """)
        self.txt_ai_command.returnPressed.connect(self.run_ai_command)
        
        cmd_layout.addWidget(self.btn_mic)
        cmd_layout.addWidget(self.txt_ai_command)
        bottom_layout.addWidget(cmd_frame)

        # 3.3 Log Console
        self.log_console = QtWidgets.QTextEdit()
        self.log_console.setObjectName("logConsole")
        self.log_console.setReadOnly(True)
        self.log_console.setMaximumHeight(80)
        self.log_console.setPlaceholderText("System Ready. Waiting for validation...")
        
        bottom_layout.addWidget(self.log_console)
        
        # Add Footer to Main Layout with stretch 0
        main_layout.addWidget(bottom_frame, 0)

        # No explicit setLayout needed for QMainWindow (uses setCentralWidget)

        self.log("Qyntara AI Initialized.")
        
        
        # Explicit Size Policy for Window
        self.setMinimumSize(450, 600)
        self.resize(500, 750) # Safe Initial Size

        # Populate Rules and Pipeline
        self.populate_rules()
        try:
             self.update_pipeline_rules()
        except:
             pass

    def update_pipeline_rules(self):
        """Updates rule severities based on selected pipeline."""
        pipeline = self.combo_pipeline.currentText()
        if "Game" in pipeline:
            profile = "game"
        elif "AR" in pipeline:
            profile = "vr"
        elif "VFX" in pipeline:
            profile = "vfx"
        else:
            profile = "web"
            
        self.validator.set_pipeline_profile(profile)
        
        # Get effective profile data
        profile_data = self.validator.profiles.get(profile, {})

        for rule_id, widget in self.rule_widgets.items():
            if rule_id in profile_data:
                override = profile_data[rule_id]
                widget.setVisible(override.get("enabled", True))
                if "severity" in override:
                    widget.lbl_desc.setText(f"[{override['severity'].upper()}] " + widget.rule_data.get('description', ''))
            else:
                widget.setVisible(True)
                widget.lbl_desc.setText(widget.rule_data.get('description', ''))

        self.log(f"Switched validation profile to: {pipeline} (Rules Updated)")

    def populate_rules(self):
        self.rule_widgets = {}
        self.category_widgets = {}
        
        # Clear existing (clear self.val_layout instead of scroll_layout)
        if hasattr(self, 'val_layout'):
            # Clear all
            while self.val_layout.count(): 
                 item = self.val_layout.takeAt(0)
                 if item.widget(): item.widget().deleteLater()
        else:
            return
        
        if not self.validator.rules:
             return
        
        # Categories
        categories = {
            "geometry": "Geometry Integrity",
            "transform": "Transforms",
            "scene": "Scene Structure",
            "uv": "UVs",
            "materials": "Materials",
            "naming": "Naming & Structure",
            "animation": "Animation & Rigging",
            "alignment": "Layout & Alignment",
            "baking": "Baking & Texturing"
        }
        
        # Group rules
        grouped_rules = {}
        for safe_key in categories:
            grouped_rules[safe_key] = []
            
        for rule in self.validator.rules:
            cat = rule.get("category", "geometry")
            if cat not in grouped_rules:
                grouped_rules.setdefault(cat, []).append(rule)
            else:
                grouped_rules[cat].append(rule)
                
        # Create Layouts
        for cat_key, cat_label in categories.items():
            rules_in_cat = grouped_rules.get(cat_key, [])
            if not rules_in_cat:
                continue
                
            # Create Collapsible Category
            category_widget = CollapsibleCategory(cat_label)
            # Add to val_layout (Scroll Content) - Use addWidget for simplicity
            self.val_layout.addWidget(category_widget)
            self.category_widgets[cat_key] = category_widget
            
            # Add Rules to Category
            for rule in rules_in_cat:
                w = RuleWidget(rule)
                w.fixRequested.connect(self.handle_single_fix)
                category_widget.add_widget(w)
                self.rule_widgets[rule['id']] = w
        
        # Add stretch at the end to keep items compact at top
        self.val_layout.addStretch()
    
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_console.append(f"[{timestamp}] {message}")
        sb = self.log_console.verticalScrollBar()
        sb.setValue(sb.maximum())

    def on_tab_changed(self, index):
        # Validation tab is index 2 (INDUSTRY 4.0=0, INDUSTRY 5.0=1, Validation=2)
        self.val_action_frame.setVisible(index == 2)

    def load_scene(self):
        try:
            from maya import cmds
            file_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Maya Scene", "", "Maya Files (*.ma *.mb)")
            if file_path:
                cmds.file(file_path, open=True, force=True)
                self.log(f"Scene loaded: {file_path}")
                # Reset UI
                for w in self.rule_widgets.values():
                    w.reset()
                self.header.set_health(100)
        except ImportError:
            self.log("Error: Maya commands not available (Dev Mode).")
        self.update_pipeline_rules()
        self.resize(450, 700) # Reset size on load for good measure using safe height

    def run_validation(self):
        mode = self.combo_mode.currentText()
        if "Remote" in mode:
            self.run_remote_validation()
            return
            
        self.log("Starting LOCAL validation...")
        self.btn_fix.setEnabled(False)
        self.btn_html_report.setEnabled(False)
        
        try:
            from maya import cmds
            selection = cmds.ls(sl=True, long=True) or cmds.ls(type="transform", long=True)
            if not selection:
                 self.log("Warning: No objects found to validate.")
                 return
        except ImportError:
            selection = ["MockObject"]
            
        # Collect Disabled Rules from UI
        disabled_rules = []
        for rule_id, widget in self.rule_widgets.items():
            if not widget.checkbox.isChecked():
                disabled_rules.append(rule_id)
        
        self.log(f"Running validation (Skipping {len(disabled_rules)} disabled rules)...")
        report = self.validator.run_validation(selection, disabled_rules=disabled_rules)
        print("Invoking QyntaraVisualizer...")
        
        # Wrap Visualizer in undo chunk to keep timeline clean
        # Conditional Undo Chunk:
        # If we are inside Auto-Fix, we are ALREADY in a chunk. Don't open a new one.
        # If we are standalone, wrap in chunks.
        use_chunk = not getattr(self, "is_auto_fixing", False) 
        try:
            from maya import cmds
            if use_chunk: cmds.undoInfo(openChunk=True, chunkName="QyntaraValidation")
            visualizer.QyntaraVisualizer.run_visualization(report)
        except Exception: 
            pass
        finally:
            if use_chunk: cmds.undoInfo(closeChunk=True)
            
        self.process_report(report)

    def toggle_voice_listen(self, checked):
        if checked:
            self.txt_ai_command.setPlaceholderText("I'm listening...")
            self.txt_ai_command.setStyleSheet("background: #330000; color: #ff003c; border: 1px solid #ff003c; border-radius: 12px; padding: 4px 10px;")
            self.log("Voice Assist: Listening...")
            QtWidgets.QApplication.processEvents()
            
            # Simulate listening delay
            # In production, this would trigger the audio stream
            QtCore.QTimer.singleShot(2000, self.finish_voice_sim)
        else:
            self.reset_ai_input()

    def finish_voice_sim(self):
        if not self.btn_mic.isChecked(): return
        
        # Mock recognized text
        self.txt_ai_command.setText("Optimize scene for Unreal Engine")
        self.btn_mic.setChecked(False)
        self.reset_ai_input()
        self.log("Voice Assist: Recognized 'Optimize scene for Unreal Engine'")

    def reset_ai_input(self):
        self.txt_ai_command.setPlaceholderText("Ask Qyntara... (Type or Click Mic)")
        self.txt_ai_command.setStyleSheet("""
            QLineEdit {
                background: #2d2d30; 
                color: #00CEC9; 
                border: 1px solid #444; 
                border-radius: 12px;
                padding: 4px 10px;
                font-family: 'Segoe UI', sans-serif;
            }
            QLineEdit:focus { border: 1px solid #00CEC9; }
        """)

    def run_remote_validation(self):
        self.log("Starting REMOTE validation...")
        self.btn_fix.setEnabled(False)
        self.btn_html_report.setEnabled(False)
        
        try:
            from maya import cmds
            import os
            import tempfile
            from ..core.client import QyntaraClient
            
            # 1. Export Selection
            selection = cmds.ls(sl=True, long=True)
            if not selection: 
                self.log("Error: Select objects to send to remote server.")
                return

            temp_path = os.path.join(tempfile.gettempdir(), "remote_job.obj")
            if not cmds.pluginInfo("objExport", q=True, loaded=True):
                cmds.loadPlugin("objExport")
                
            cmds.file(temp_path, force=True, options="groups=1;ptgroups=1;materials=1;smoothing=1;normals=1", typ="OBJexport", pr=True, es=True)
            
            # 2. Convert Pipeline
             # Simple map
            pipeline = self.combo_pipeline.currentText()
            if "Game" in pipeline: p_code = "game"
            elif "VR" in pipeline: p_code = "vr"
            elif "VFX" in pipeline: p_code = "vfx"
            else: p_code = "web"
            
            # 3. Send
            self.log(f"Sending job to server (Pipeline: {p_code})...")
            
            client = QyntaraClient()
            job_id = client.submit_job(temp_path, p_code)
            
            if job_id:
                self.log(f"Job submitted! ID: {job_id}")
            else:
                 self.log("Server Error: could not submit job.")
        except Exception as e:
            self.log(f"Remote Error: {e}")

    def process_report(self, report):
        # Inject Pipeline Info into Report
        pipeline = self.combo_pipeline.currentText()
        if "pipeline" not in report: # Don't overwrite if remote
            report["pipeline"] = pipeline
            
        self.last_report = report
        total_issues = 0
        
        # Reset and Update UI
        for rule_id, widget in self.rule_widgets.items():
            widget.reset()
            
        for detail in report.get("details", []):
            rule_id = detail["rule_id"]
            if rule_id in self.rule_widgets:
                count = len(detail["violations"])
                total_issues += count
                self.rule_widgets[rule_id].set_status(count, detail["severity"])
                if count > 0:
                    self.log(f"FAILED: {detail['rule_label']} ({count} items)")
                else:
                    self.log(f"PASSED: {detail['rule_label']}")
        
        # Calculate health
        health = max(0, 100 - (total_issues * 2)) 
        if total_issues == 0: health = 100
        
        self.header.set_health(health)
        self.btn_html_report.setEnabled(True)
        
        failed = report.get("summary", {}).get("failed", 0)
        if failed > 0:
            self.btn_fix.setEnabled(True)
        else:
            self.btn_fix.setEnabled(False) # Disable if clean

        if total_issues == 0:
             self.log(f"Validation Passed for Pipeline: {pipeline}!")
        else:
             self.log(f"Validation Failed with {total_issues} issues.")

    def run_ai_command(self):
        """Passes text to LLM and shows result."""
        text = self.txt_ai_command.text()
        if not text: return
        
        self.log(f"User: {text}")
        response = self.ai_assistant.process_prompt(text)
        self.log(f"AI: {response}")
        self.txt_ai_command.clear()

    def auto_fix(self):
        """Public entry point with Consolidated Undo Chunk."""
        from maya import cmds
        self.is_auto_fixing = True
        
        # Ensure Undo is Active and has capacity for complex operations
        try:
            if not cmds.undoInfo(q=True, state=True):
                cmds.undoInfo(state=True)
            cmds.undoInfo(infinity=True)
        except: pass

        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        try:
            # Open GLOBAL chunk for both fixes and subsequent validation
            cmds.undoInfo(openChunk=True, chunkName="QyntaraAutoFix")
            self._run_fixes_worker()
        except Exception as e:
            self.log(f"Auto-Fix Error: {e}")
        finally:
            cmds.undoInfo(closeChunk=True)
            self.is_auto_fixing = False
            QtWidgets.QApplication.restoreOverrideCursor()

    def auto_fix_all(self):
        # Alias for legacy calls
        self.auto_fix()

    def _run_fixes_worker(self):
        """Attempts to fix all fixable errors."""
        fixes_applied = 0
        self.log("Starting Auto-Fix...")
        
        from ..core import fixer

        # Define Fixer Map - Order is Critical!
        # 1. Cleanup Topology (Merge, Triangulate)
        # 2. Fix Transforms
        # 3. Fix Normals (Needs clean topo)
        # 4. Fix UVs
        # 5. Cleanup Scene (History)
        
        fix_map = {
            # 1. CLEANUP (Destructive / Removal)
            # Use Shell Filter (fix_cleanup_geometry) for ALL topology garbage
            "geo_lamina_faces": fixer.QyntaraFixer.fix_cleanup_geometry,
            "geo_non_manifold": fixer.QyntaraFixer.fix_cleanup_geometry,
            "geo_zero_area": fixer.QyntaraFixer.fix_cleanup_geometry,
            "geo_zero_length": fixer.QyntaraFixer.fix_cleanup_geometry,
            
            # 2. TOPOLOGY (Constructive / Closure)
            "geo_open_edges": fixer.QyntaraFixer.fix_open_edges,
            "geo_ngons": fixer.QyntaraFixer.fix_ngons,
            "geo_concave": fixer.QyntaraFixer.fix_triangulate,
            "geo_triangulated": fixer.QyntaraFixer.fix_triangulate,
            "geo_watertight": fixer.QyntaraFixer.fix_open_edges, # Alias: Watertightness == No Open Edges

            # Transforms
            "xform_frozen": fixer.QyntaraFixer.fix_freeze_all, 
            "xform_negative_scale": fixer.QyntaraFixer.fix_scale,
            "xform_scale": fixer.QyntaraFixer.fix_scale, # Alias if ID is different
            "check_pivot_center": fixer.QyntaraFixer.fix_pivot_center,
            "scene_units": fixer.QyntaraFixer.fix_scene_units,
            "check_up_axis": fixer.QyntaraFixer.fix_up_axis,
            "geo_proximity": fixer.QyntaraFixer.fix_proximity_gaps,
            
            # Normals (After topo changes)
            "geo_inverted_normals": fixer.QyntaraFixer.fix_reverse_normals,
            "geo_normals": fixer.QyntaraFixer.fix_normals,
            "geo_hard_edges": fixer.QyntaraFixer.fix_hard_edges,
            "render_terminator": fixer.QyntaraFixer.fix_shadow_terminator,
            "geo_poles": fixer.QyntaraFixer.fix_ai_topology,   # AI UPGRADE

            # Materials
            "mat_default": fixer.QyntaraFixer.fix_default_material,
            "mat_complex": fixer.QyntaraFixer.fix_complex_nodes,
            "mat_multi_assigned": fixer.QyntaraFixer.select_components,
            "geo_vertex_color": fixer.QyntaraFixer.fix_vertex_colors,
            "mat_missing": fixer.QyntaraFixer.fix_default_material,
            
            # 2. UVS
            "uv_exists": fixer.QyntaraFixer.fix_uv_exists,
            "uv_flipped": fixer.QyntaraFixer.fix_flipped_uvs,
            "uv_overlap": fixer.QyntaraFixer.fix_uv_overlaps,
            "uv_bounds": fixer.QyntaraFixer.fix_uv_bounds,
            "uv_zero_area": fixer.QyntaraFixer.fix_uv_overlaps, # Reuse layout for zero area
            
            # 3. GEOMETRY CHECKS


            # General/Scene
            "scene_unused": fixer.QyntaraFixer.fix_unused_nodes,
            "scene_hierarchy": fixer.QyntaraFixer.fix_scene_hierarchy,
            # 4. BAKING
            "bake_uv2_exists": fixer.QyntaraFixer.fix_uv2_exists,
            "bake_uv2_validity": fixer.QyntaraFixer.fix_uv2_overlaps,

            "bake_padding": fixer.QyntaraFixer.fix_padding,
            "bake_seams": fixer.QyntaraFixer.fix_seams,
            
            # 5. NEW TD FIXERS
            "geo_polycount": fixer.QyntaraFixer.fix_polycount,
            "geo_all_hard_edges": fixer.QyntaraFixer.fix_hard_edges, # Suggest moving this here or earlier?
            # Actually, let's keep it but ensure fix_history runs AFTER it.
            "uv_texel_density": fixer.QyntaraFixer.fix_texel_density,
            "geo_zero_area": fixer.QyntaraFixer.fix_degenerate_geo,
            "geo_zero_length": fixer.QyntaraFixer.fix_degenerate_geo,
            
            # 6. MISSING / MANUAL HANDOFFS
            "geo_floating": fixer.QyntaraFixer.fix_cleanup_geometry, 
            "geo_internal_faces": fixer.QyntaraFixer.select_components,
            "geo_intersect": fixer.QyntaraFixer.select_components, 
            
            # Animation
            "anim_skin_weights": fixer.QyntaraFixer.select_components,
            "anim_baked": fixer.QyntaraFixer.select_components,
            "anim_root_motion": fixer.QyntaraFixer.select_components,
            
            # 7. NAMING & HIERARCHY & HISTORY (RUN LAST)
            # Critical: Runs last so it doesn't invalidate object paths for other fixers!
            "geo_history": fixer.QyntaraFixer.fix_history, # MOVED HERE (Last step before naming)
            
            "mat_naming": fixer.QyntaraFixer.fix_shader_naming,
            "check_naming_convention": fixer.QyntaraFixer.fix_smart_naming,
            "scene_hierarchy": fixer.QyntaraFixer.fix_scene_hierarchy,
            "anim_constraints": fixer.QyntaraFixer.select_components,
        }
        
        if not self.last_report: return
        
        # Reset Log Cache for this run
        fixer.QyntaraFixer.reset_cache()
        
        # Create a lookup for details
        report_lookup = {d["rule_id"]: d for d in self.last_report.get("details", [])}

        # Iterate strictly in the order defined in fix_map (Priority Order)
        fixed_rules = set()

        # 1. Determine Scope (Selection vs Global)
        from maya import cmds
        current_selection = cmds.ls(sl=True, o=True, long=True) or []
        
        target_scope = set()
        if current_selection:
            target_scope.update(current_selection)
            # Expand scope to include Parents (Transforms) if current selection are Shapes
            # This handles Component Selection -> Shape -> Transform matching
            parents = cmds.listRelatives(current_selection, parent=True, fullPath=True) or []
            target_scope.update(parents)
        
        if target_scope:
            self.log(f"Auto-Fix Context: Selection ({len(target_scope)} nodes/parents)")
        else:
            self.log("Auto-Fix Context: Full Report (Global)")

        # Ensure fix_map covers all auto-fixable rules
        # Update fix_map dynamically if needed or rely on static definition
        # Adding missing keys if not present (simplified edit)
        if "mat_missing" not in fix_map:
             fix_map["mat_missing"] = fixer.QyntaraFixer.fix_default_material

        for rule_id in fix_map: # Preserves insertion order in modern Python
            # CHECK UI STATE: Skip if user unchecked it
            if rule_id in self.rule_widgets:
                if not self.rule_widgets[rule_id].checkbox.isChecked():
                    if rule_id in report_lookup: # Only log if it actually had errors
                        self.log(f"Skipping {rule_id} (Disabled by User)")
                    continue

            if rule_id in report_lookup:
                detail = report_lookup[rule_id]
                
                # Filter violations if selection is active
                if target_scope:
                    # EXEMPT Global Rules from Scope Filtering
                    # These affect the scene, not specific objects, so they should always run.
                    global_rules = ["scene_units", "check_up_axis", "scene_unused", "scene_hierarchy"]
                    
                    if rule_id in global_rules:
                        input_detail = detail # Pass full detail
                    else:
                        original_violations = detail.get("violations", [])
                        filtered_violations = []
                        for v in original_violations:
                            obj = v.get("object")
                            # Check exact long name OR short name match
                            is_match = False
                            if obj in target_scope:
                                is_match = True
                            else:
                                # Robust Check: handle partial paths
                                # If obj is "pCube1" and scope has "|Group|pCube1", match.
                                # If obj is "|Group|pCube1" and scope has "pCube1", match.
                                obj_short = obj.split("|")[-1]
                                for t in target_scope:
                                    t_short = t.split("|")[-1]
                                    if obj_short == t_short:
                                        is_match = True
                                        break
                            
                            if is_match:
                                filtered_violations.append(v)
                        
                        if not filtered_violations:
                            continue
                            
                        # Create a scoped detail object strictly for this fix execution
                        scoped_detail = detail.copy()
                        scoped_detail["violations"] = filtered_violations
                        input_detail = scoped_detail
                else:
                    input_detail = detail

                try:
                    fix_map[rule_id](input_detail)
                    
                    fixes_applied += 1
                    fixed_rules.add(rule_id)
                    self.log(f"Fixed {rule_id}...")
                except Exception as e:
                    self.log(f"Failed to fix {rule_id}: {e}")
        
        
        # STATEFUL RE-VALIDATION
        if fixes_applied > 0:
            # Instead of scanning the whole scene again (which might find 'new' issues),
            # we only re-check the specific objects we tried to fix.
            self.last_report = self.validator.revalidate_report(self.last_report)
            self.process_report(self.last_report)
            visualizer.QyntaraVisualizer.run_visualization(self.last_report)
            
            # --- SMART SELECTION (Post-Fix) ---
            # Check what's left
            remaining_issues = self.last_report.get("details", [])
            open_edge_objects = []
            
            if target_scope:
                 # Check only within scope
                 for d in remaining_issues:
                     if d['rule_id'] == 'geo_open_edges' and d.get('violations'):
                         for v in d['violations']:
                             if v.get('object') in target_scope:
                                 open_edge_objects.append(v['object'])
            else:
                for d in remaining_issues:
                     if d['rule_id'] == 'geo_open_edges' and d.get('violations'):
                         for v in d['violations']:
                             if v.get('object'): open_edge_objects.append(v['object'])
            
            if open_edge_objects:
                # Selecting specific border edges for manual fix
                self.log(f"Auto-Fix Complete. {len(open_edge_objects)} objects still have Open Edges (Manual Fix Required).")
                from ..core import fixer
                fixer.QyntaraFixer.select_border_edges(open_edge_objects)
            else:
                self.log("Auto-Fix Complete.")
                # Restore original selection if it existed, otherwise clear
                if target_scope:
                    # Filter target_scope to valid scene objects
                    valid_sel = [o for o in target_scope if cmds.objExists(o)]
                    # If we have Shapes + Transforms, selecting Shape is usually preferred if it was original
                    # But recovering exact original selection is hard. Selecting Transforms is safe.
                    # Let's filter to just the 'current_selection' list we captured at start
                    original_valid = [o for o in current_selection if cmds.objExists(o)]
                    if original_valid:
                        cmds.select(original_valid)
                    else:
                        cmds.select(valid_sel)
                else:
                    cmds.select(clear=True)
            
            
        else:
            if target_scope:
                self.log("[TIP] No fixes for SELECTED objects.")
                self.log("      Clear selection to auto-fix the remaining Global Errors.")
            else:
                self.log("No auto-fixes available for current errors.")

    def handle_single_fix(self, rule_id):
        """Fixes a specific rule_id triggered by context menu."""
        if not self.last_report:
             self.log("Error: No validation report available.")
             return
             
        # Find detail
        detail = next((d for d in self.last_report.get("details", []) if d["rule_id"] == rule_id), None)
        if not detail:
            self.log(f"No active violations for {rule_id} to fix.")
            return

        from ..core.fixer import QyntaraFixer

        fix_map = {
            "geo_open_edges": QyntaraFixer.fix_open_edges,
            "geo_ngons": QyntaraFixer.fix_ngons,
            "geo_concave": QyntaraFixer.fix_triangulate,
            "geo_lamina_faces": QyntaraFixer.fix_lamina_faces,
            "geo_non_manifold": QyntaraFixer.fix_non_manifold,
            "xform_frozen": QyntaraFixer.fix_freeze_all,
            "xform_negative_scale": QyntaraFixer.fix_scale,
            "mat_missing": QyntaraFixer.fix_default_material,
            "mat_naming": QyntaraFixer.fix_shader_naming,
            "check_default_material": QyntaraFixer.fix_default_material,
            "uv_flipped": QyntaraFixer.fix_flipped_uvs,
            "geo_inverted_normals": QyntaraFixer.fix_reverse_normals,
            "geo_triangulated": QyntaraFixer.fix_triangulate,
            "geo_history": QyntaraFixer.fix_history,
            "geo_hard_edges": QyntaraFixer.fix_hard_edges,
            "shadow_terminator": QyntaraFixer.fix_shadow_terminator,
            "uv_exists": QyntaraFixer.fix_uv_exists,
            "geo_polycount": QyntaraFixer.fix_polycount,
            "uv_texel_density": QyntaraFixer.fix_texel_density,
            "geo_zero_area": QyntaraFixer.fix_degenerate_geo,
            "geo_zero_length": QyntaraFixer.fix_degenerate_geo,
            "check_scene_hierarchy": QyntaraFixer.select_components, # Manual
        }
        
        if rule_id in fix_map:
             try:
                 # Open Undo Chunk manually since decorator no longer handles it
                 from maya import cmds
                 cmds.undoInfo(openChunk=True, chunkName="QyntaraSingleFix")
                 
                 # Fixers expect the Report Entry (detail dictionary)
                 # QyntaraFixer handles parsing objects from it
                 fix_map[rule_id](detail)
                 self.log(f"Fixed {rule_id}. Re-validating...")
                 self.run_validation() # Will open its own chunk if needed (is_auto_fixing is False)
             except Exception as e:
                 self.log(f"Fix failed: {e}")
             finally:
                 cmds.undoInfo(closeChunk=True)
        else:
             self.log(f"No single-click fix available for {rule_id}.")




    def generate_visual_report(self):
        if not self.last_report: return
        self.log("Generating visual report...")
        
        import os
        import tempfile
        import webbrowser
        import maya.cmds as cmds
        import io
        
        temp_dir = tempfile.gettempdir()
        report = self.last_report
        health = self.header.lbl_health.text()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        # HTML Header
        html = f"""
        <html>
        <head>
            <title>Qyntara Validation Report</title>
            <style>
                body {{ font-family: 'Segoe UI', sans-serif; background: #252526; color: #ddd; padding: 20px; }}
                .container {{ max-width: 900px; margin: 0 auto; background: #1e1e1e; padding: 20px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.5); }}
                .header {{ border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }}
                h1 {{ margin: 0; color: #fff; }}
                .health {{ font-size: 32px; font-weight: bold; color: {{ '#2ea043' if '100%' in health else '#d29922' }}; }}
                .rule-card {{ background: #2d2d30; margin-bottom: 20px; border-radius: 6px; overflow: hidden; border: 1px solid #444; }}
                .rule-header {{ padding: 10px 15px; background: #333; display: flex; justify-content: space-between; align-items: center; cursor: pointer; }}
                .rule-title {{ font-weight: bold; font-size: 16px; color: #fff; }}
                .rule-body {{ padding: 15px; display: flex; flex-wrap: wrap; gap: 20px; }}
                .screenshot {{ flex: 1; min-width: 300px; max-width: 400px; }}
                .screenshot img {{ width: 100%; border-radius: 4px; border: 2px solid #f85149; }}
                .details-list {{ flex: 2; min-width: 250px; max-height: 300px; overflow-y: auto; }}
                ul {{ margin: 0; padding-left: 20px; font-family: monospace; font-size: 12px; color: #aaa; }}
                li {{ margin-bottom: 4px; }}
                .badge {{ padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: bold; text-transform: uppercase; }}
                .bg-error {{ background: #f85149; color: #fff; }}
                .bg-warning {{ background: #d29922; color: #000; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div>
                        <h1>Qyntara AI Report</h1>
                        <div style="color: #888; margin-top: 5px;">Generated: {timestamp}</div>
                    </div>
                    <div class="health">{health}</div>
                </div>
        """
        
        # Capture Context Manager (Cleanup)
        initial_selection = cmds.ls(sl=True)
        # Hide Grid and HUD for pro shot
        grid_state = cmds.grid(q=True, toggle=True)
        cmds.grid(toggle=False)
        
        details = report.get("details", [])
        if not details:
            html += "<h2 style='color:#2ea043; text-align:center;'>No Issues Found. Scene Clean.</h2>"
        
        for detail in details:
            rule_id = detail["rule_id"]
            rule_label = detail["rule_label"]
            severity = detail["severity"]
            count = len(detail["violations"])
            
            # --- INTELLIGENT CAPTURE ---
            img_filename = f"qyntara_{rule_id}_{int(datetime.now().timestamp())}.jpg"
            img_path = os.path.join(temp_dir, img_filename)
            
            # Gather targets: Prefer components (faces/edges) over transforms for precision focus
            targets = []
            for v in detail["violations"]:
                if v.get("components"):
                    # v["components"] is a list like ["pCube1.f[0]", ...]
                    # We accept these directly
                    targets.extend(v["components"])
                elif v.get("object") and cmds.objExists(v.get("object")):
                    targets.append(v["object"])
            
            # Limit targets to prevent viewport lag if thousands of components
            # Showing first 100 components is usually enough to identify the "Type" of error area
            capture_targets = targets[:200]
            
            # --- SMART CAPTURE LOGIC ---
            has_screenshot = False
            if capture_targets:
                try:
                    # Determine Capture Mode based on Rule ID
                    is_uv_rule = any(x in rule_id for x in ["uv_", "bake_"])
                    
                    if is_uv_rule:
                        # --- UV EDITOR CAPTURE (Robust) ---
                        print(f"UV CAPTURE DEBUG: Attempting UV capture for {rule_id}")
                        try:
                            uv_panels = cmds.getPanel(type="polyTexturePlacementPanel")
                            qt_panel = uv_panels[0] if uv_panels else "polyTexturePlacementPanel1"
                            if not uv_panels: cmds.TextureViewWindow()
                            
                            # 2. SWITCH UV SET (Critical for Lightmap visibility)
                            # If checking UV2, we MUST force the editor to show UV2
                            target_uv_set = None
                            if "uv2" in rule_id or "lightmap" in rule_label.lower():
                                # Find name of UV2 (Lightmap or uvSet2)
                                # We need a reference object
                                ref_obj = None
                                for t in capture_targets:
                                    t_clean = t.split(".")[0]
                                    if cmds.objExists(t_clean):
                                        ref_obj = t_clean
                                        break
                                
                                if ref_obj:
                                    sets = cmds.polyUVSet(ref_obj, q=True, allUVSets=True) or []
                                    for s in sets:
                                        if s == "Lightmap" or s == "uvSet2":
                                            target_uv_set = s
                                            break
                            
                            if target_uv_set:
                                print(f"UV CAPTURE: Switching to {target_uv_set} on {capture_targets}")
                                # Selecting the object allows polyUVSet to work on selection implication if needed,
                                # but explicit arg is better. However, Maya UI reflects *selection*.
                                # We first select OBJECTS to switch set, then COMPONENTS to frame.
                                
                                # 1. Identify Objects vs Components
                                objs_to_switch = set()
                                for t in capture_targets:
                                    objs_to_switch.add(t.split(".")[0])
                                
                                cmds.select(list(objs_to_switch))
                                for obj in objs_to_switch:
                                     try: cmds.polyUVSet(obj, currentUVSet=target_uv_set)
                                     except: pass
                                     
                                # 2. Select Components for Framing
                                cmds.select(capture_targets) 
                            else:
                                cmds.select(capture_targets)

                            # 3. Focus & Frame
                            print(f"UV CAPTURE DEBUG: Focusing {qt_panel}...")
                            cmds.setFocus(qt_panel)
                            
                            # FORCE Highlight Mode (Component Mode) so green dots/shells are visible
                            cmds.selectType(ocm=True, alc=False)
                            cmds.selectType(ocm=True, polymeshUV=True) 
                            
                            cmds.textureWindow(qt_panel, e=True, frameAll=True) 
                            
                            # 4. Capture UV Panel (Screen Scrape Method)
                            # widget.grab() fails for OpenGL (black image). We must scrape the screen.
                            print("UV CAPTURE DEBUG: Screen Scraping Widget...")
                            
                            ptr = omui.MQtUtil.findControl(qt_panel)
                            if ptr:
                                widget = wrapInstance(int(ptr), QtWidgets.QWidget)
                                if widget:
                                    # Ensure visible and fresh
                                    if widget.isMinimized(): widget.showNormal()
                                    widget.raise_()
                                    QtWidgets.QApplication.processEvents()
                                    cmds.refresh(force=True)
                                    
                                    # Get absolute geometry
                                    rect = widget.geometry()
                                    top_left = widget.mapToGlobal(QtCore.QPoint(0, 0))
                                    
                                    # Grab Screen
                                    screen = None
                                    app = QtWidgets.QApplication.instance()
                                    try:
                                        # PySide6 / Qt5 logic
                                        screen = app.primaryScreen()
                                        pixmap = screen.grabWindow(0, top_left.x(), top_left.y(), rect.width(), rect.height())
                                    except:
                                        # Legacy PySide2 fallback if primaryScreen fails or grabWindow differs
                                        screen = QtGui.QPixmap
                                        pixmap = screen.grabWindow(QtWidgets.QApplication.desktop().winId(), 
                                                                   top_left.x(), top_left.y(), rect.width(), rect.height())
                                    
                                    if not pixmap.isNull():
                                        pixmap.save(img_path, "JPG")
                                        has_screenshot = True
                                        print(f"UV CAPTURE DEBUG: Screen Scrape Success! Saved to {img_path}")
                                    else:
                                         print("UV CAPTURE DEBUG: Screen Scrape returned null.")
                                else:
                                     print("UV CAPTURE DEBUG: Could not wrap widget instance.")
                            else:
                                 print(f"UV CAPTURE DEBUG: MQtUtil could not find control for {qt_panel}")
                            
                            if not has_screenshot:
                                print("UV CAPTURE DEBUG: Fallback triggered.")
                                is_uv_rule = False # Retry with 3D

                        except Exception as uv_err:
                            import traceback
                            traceback.print_exc()
                            print(f"UV Capture Failed (Fallback to 3D): {uv_err}")
                            is_uv_rule = False 

                    if not is_uv_rule:
                        # --- 3D VIEWPORT CAPTURE (Legacy/Geometry) ---
                        
                        # Detect Component vs Object mode
                        first_target = capture_targets[0]
                        is_component = "." in first_target and not first_target.endswith(".shape")
                        
                        if is_component:
                            # COMPONENT MODE (Zoom In)
                            cmds.selectMode(component=True)
                            cmds.selectType(allComponents=True)
                            cmds.select(capture_targets)
                            # hilite parent objects to show components
                            parents = set([t.split(".")[0] for t in capture_targets])
                            cmds.hilite(list(parents))
                            
                            cmds.viewFit(animate=False, fitFactor=0.85)
                            
                        else:
                            # OBJECT MODE (Frame Object)
                            cmds.selectMode(object=True)
                            cmds.select(capture_targets)
                            cmds.viewFit(animate=False, fitFactor=0.85)

                        # 2. Set "Studio Angle" (Consistent 3/4 View)
                        try:
                            cmds.setAttr("persp.rotateX", -30)
                            cmds.setAttr("persp.rotateY", 45)
                            cmds.setAttr("persp.rotateZ", 0)
                        except: pass 
                        
                        # 4. Force Update
                        cmds.refresh(cv=True)
                        
                        # 5. Capture Active View
                        cmds.playblast(frame=cmds.currentTime(q=True), format="image", compression="jpg", 
                                       completeFilename=img_path, showOrnaments=False, viewer=False, 
                                       width=640, height=360, percent=100, offScreen=True)
                        has_screenshot = True
                        
                except Exception as e:
                    print(f"Screenshot failed for {rule_id}: {e}")
            
            # --- APPEND HTML CARD ---
            badge_class = "bg-error" if severity == "error" else "bg-warning"
            
            html += f"""
            <div class="rule-card">
                <div class="rule-header">
                    <span class="rule-title">{rule_label}</span>
                    <span class="badge {badge_class}">{severity} ({count})</span>
                </div>
                <div class="rule-body">
            """
            
            if has_screenshot and os.path.exists(img_path):
                 html += f"""
                    <div class="screenshot">
                        <img src="{img_path}" alt="Issue visual" />
                    </div>
                 """
            
            html += """<div class="details-list"><ul>"""
             
            for i, v in enumerate(detail["violations"]):
                if i > 50:
                    html += f"<li>... and {len(detail['violations'])-50} more.</li>"
                    break
                obj_name = v.get("object", "Unknown").split("|")[-1] 
                issue = v.get("issue", "Check Failed")
                # Clean up component display
                comp_info = ""
                if "components" in v and v["components"]:
                     c_list = v["components"]
                     if len(c_list) > 3:
                         comp_info = f" <span style='color:#888'>[{c_list[0].split('.')[-1]}, ... +{len(c_list)-1}]</span>"
                     else:
                         comp_info = f" <span style='color:#888'>{[c.split('.')[-1] for c in c_list]}</span>"
                
                html += f"<li><b>{obj_name}</b>{comp_info}: {issue}</li>"
                
            html += """</ul></div></div></div>"""
            
        html += """
                <div style="text-align: center; color: #555; margin-top: 30px; font-size: 11px;">
                    Qyntara AI Toolkit v2.0 | TD Edition
                </div>
            </div>
        </body>
        </html>
        """
        
        # Restore State
        cmds.grid(toggle=grid_state)
        if initial_selection: 
            cmds.select(initial_selection)
        else:
            cmds.select(clear=True)
            
        # Save and Open
        report_path = os.path.join(temp_dir, "Qyntara_Visual_Report.html")
        with io.open(report_path, "w", encoding="utf-8") as f:
            f.write(html)
            
        webbrowser.open(report_path)
        self.log(f"Visual Report Generated: {report_path}")

    def reset_ui_state(self):
        """Resets the UI widgets to neutral/ready state."""
        for rule_id, widget in self.rule_widgets.items():
            widget.reset()
            
        self.header.set_health(100)
        self.btn_fix.setEnabled(False) 
        self.log("UI State Reset (Re-validate required).")

    def _on_maya_undo(self, *args):
        """Callback triggered when Maya Undo is executed."""
        # Only reset if window is valid
        try:
            if self.isVisible():
                self.reset_ui_state()
        except: pass

    def run_undo(self):
        """Undos the last operation (Maya Undo)."""
        try:
            from maya import cmds
            cmds.undo()
        except Exception as e:
            self.log(f"Undo Failed: {e}")

    def generate_html_report(self):
        """Generates and opens an HTML report of the validation results."""
        if not self.last_report:
             self.log("No validation data available. Run validation first.")
             return
             
        # Mock HTML generation for now
        self.log("Generating HTML Report...")
        
        summary = self.last_report.get("summary", {})
        failed_count = summary.get("failed", 0)
        total_issues = summary.get("errors", 0) + summary.get("warnings", 0)
        
        self.log(f"Report Summary: {total_issues} issues found ({failed_count} failed checks).")
        
        # Print details to log
        details = self.last_report.get("details", [])
        for detail in details:
            if detail["status"] == "FAILED":
                self.log(f" - {detail['rule_label']}: {len(detail.get('violations', []))} violations")

    def undo_last_fix(self):
        """Undo the last auto-fix operation."""
        self.run_undo()

    def _on_maya_undo(self, *args):
        """Callback triggered when Maya performs an UNDO."""
        try:
            if not self.isVisible(): return
            
            self.log("Undo detected. Re-validating...")
            # We reset UI visual state first
            for rule_id, widget in self.rule_widgets.items():
                widget.reset()
            self.header.set_health(100)
            
            # Then trigger a fresh validation to see what's actually in scene now
            self.run_validation()
        except Exception as e:
            logger.debug(f"Undo callback failed: {e}")

    def closeEvent(self, event):
        from maya import cmds
        if self._undo_job_id and cmds.scriptJob(exists=self._undo_job_id):
            cmds.scriptJob(kill=self._undo_job_id, force=True)
        super(QyntaraMainWindow, self).closeEvent(event)
        # The original code had a duplicate super call and a typo.
        # Keeping the super(Class, self).method(args) style as it was explicitly in the instruction,
        # and removing the redundant second call and typo.


def show():
    parent = get_maya_window()
    win = QyntaraMainWindow(parent)
    win.show()
    return win
