from .qt_utils import QtWidgets, QtCore, QtGui
import logging

logger = logging.getLogger(__name__)

class Industry40Tab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Industry40Tab, self).__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        # MAIN LAYOUT
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        
        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        
        content = QtWidgets.QWidget()
        self.layout_content = QtWidgets.QVBoxLayout(content)
        self.layout_content.setContentsMargins(10, 10, 10, 10)
        self.layout_content.setSpacing(15)
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
        
        layout = self.layout_content
        
        # --- TITLE ---
        lbl = QtWidgets.QLabel("Industry 4.0: Smart Factory (IoT)")
        lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #ff9900;")
        layout.addWidget(lbl)
        
        # --- 1. DIGITAL TWIN SYNC ---
        grp_twin = QtWidgets.QGroupBox("Digital Twin Link")
        grp_twin.setStyleSheet("QGroupBox { border: 1px solid #ff9900; margin-top: 6px; padding-top: 10px; font-weight: bold; color: #ff9900; }")
        twin_layout = QtWidgets.QVBoxLayout(grp_twin)
        
        row_id = QtWidgets.QHBoxLayout()
        row_id.addWidget(QtWidgets.QLabel("Asset ID:"))
        self.txt_id = QtWidgets.QLineEdit("ASSET-8842-X")
        self.txt_id.setStyleSheet("background: #222; color: #fff; padding: 4px;")
        row_id.addWidget(self.txt_id)
        
        self.btn_sync = QtWidgets.QPushButton("CONNECT LIVE STREAM")
        self.btn_sync.setCheckable(True)
        self.btn_sync.setStyleSheet("""
            QPushButton { background: #333; color: #aaa; font-weight: bold; }
            QPushButton:checked { background: #ff9900; color: #000; }
        """)
        self.btn_sync.toggled.connect(self.toggle_sync)
        row_id.addWidget(self.btn_sync)
        twin_layout.addLayout(row_id)
        
        # Telemetry Labels
        self.lbl_telemetry = QtWidgets.QLabel("Telemetry: DISCONNECTED")
        self.lbl_telemetry.setStyleSheet("color: #666; font-family: Consolas;")
        twin_layout.addWidget(self.lbl_telemetry)
        
        layout.addWidget(grp_twin)
        
        # --- 2. CONNECTED MACHINES (IoT Matrix) ---
        grp_iot = QtWidgets.QGroupBox("Connected Machines")
        grp_iot.setStyleSheet("QGroupBox { border: 1px solid #00aaff; margin-top: 6px; padding-top: 10px; font-weight: bold; color: #00aaff; }")
        iot_layout = QtWidgets.QGridLayout(grp_iot)
        
        # Mock Machines
        machines = [
            ("Prusa_XL_01", "PRINTING", 65),
            ("Prusa_XL_02", "IDLE", 0),
            ("CNC_Mill_A", "MAINTENANCE", 0),
            ("Render_Blade_1", "RENDERING", 98)
        ]
        
        for i, (name, status, load) in enumerate(machines):
            frame = QtWidgets.QFrame()
            frame.setStyleSheet(f"background: #1a1a1a; border: 1px solid #333; border-radius: 4px;")
            f_layout = QtWidgets.QVBoxLayout(frame)
            
            lbl_name = QtWidgets.QLabel(name)
            lbl_name.setStyleSheet("font-weight: bold; color: #fff;")
            f_layout.addWidget(lbl_name)
            
            lbl_status = QtWidgets.QLabel(status)
            col = "#00ff00" if status in ["PRINTING", "RENDERING"] else "#ffff00" if status == "IDLE" else "#ff0000"
            lbl_status.setStyleSheet(f"color: {col}; font-size: 10px;")
            f_layout.addWidget(lbl_status)
            
            prog = QtWidgets.QProgressBar()
            prog.setValue(load)
            prog.setFixedHeight(5)
            prog.setTextVisible(False)
            prog.setStyleSheet(f"QProgressBar::chunk {{ background: {col}; }}")
            f_layout.addWidget(prog)
            
            # 2x2 Grid
            iot_layout.addWidget(frame, i // 2, i % 2)
            
        layout.addWidget(grp_iot)
        
        # --- 3. PIPELINE QUEUE ---
        grp_queue = QtWidgets.QGroupBox("Pipeline Automation Queue")
        grp_queue.setStyleSheet("QGroupBox { border: 1px solid #cc00ff; margin-top: 6px; padding-top: 10px; font-weight: bold; color: #cc00ff; }")
        queue_layout = QtWidgets.QVBoxLayout(grp_queue)
        
        self.list_queue = QtWidgets.QListWidget()
        self.list_queue.setFixedHeight(100)
        self.list_queue.setStyleSheet("background: #111; color: #ddd;")
        
        # Mock Queue
        items = [
             "JOB-101: Auto-Retopology (Processing...)",
             "JOB-102: USD Export (Pending)",
             "JOB-103: Texture Baking (Queued)"
        ]
        self.list_queue.addItems(items)
        queue_layout.addWidget(self.list_queue)
        
        layout.addWidget(grp_queue)
        
        layout.addStretch()
        
        # Timer for Mock Telemetry
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_telemetry)
        
    def toggle_sync(self, checked):
        asset_id = self.txt_id.text()
        
        # Connect to Digital Twin Core
        try:
            # Dynamic import to avoid errors if running outside Maya
            import scripts.maya.digital_twin_core as dt_core
            core = dt_core.core
            
            if checked:
                success = core.connect_live_stream(asset_id)
                if success:
                    self.btn_sync.setText("LIVE LINK ACTIVE")
                    self.btn_sync.setStyleSheet("background: #ff9900; color: #000; font-weight: bold;")
                    self.lbl_telemetry.setText("Telemetry: STREAMING (120Hz)...")
                    self.timer.start(500) # Faster update
                else:
                    self.btn_sync.setChecked(False) # Revert
                    self.lbl_telemetry.setText("Telemetry: ERROR - ASSET NOT FOUND")
                    QtWidgets.QMessageBox.warning(self, "Link Failed", f"Could not find asset '{asset_id}' in scene.")
            else:
                core.disconnect_stream()
                self.btn_sync.setText("CONNECT LIVE STREAM")
                self.btn_sync.setStyleSheet("background: #333; color: #aaa; font-weight: bold;")
                self.lbl_telemetry.setText("Telemetry: DISCONNECTED")
                self.timer.stop()
                
        except ImportError:
            # Fallback for testing outside Maya
            logger.warning("DigitalTwinCore not found (running externally?)")
            if checked:
               self.btn_sync.setText("LIVE LINK (MOCK)")
               self.timer.start(1000)
            else:
               self.btn_sync.setText("CONNECT LIVE STREAM")
               self.timer.stop()

    def update_telemetry(self):
        import random
        # Simulate sensor data
        temp = 60 + random.random() * 10
        rpm = 2400 + random.randint(-100, 100)
        
        # Update text
        self.lbl_telemetry.setText(f"Telemetry: Temp: {temp:.1f}C | RPM: {rpm} | Vib: NORMAL")
        
        # If in Maya, we could also drive a specialized attribute here
        # e.g. cmds.setAttr("Smart_Floor.Vibration_Hz", rpm)
