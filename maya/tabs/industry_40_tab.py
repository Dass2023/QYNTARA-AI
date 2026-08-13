try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ImportError:
    from PySide6 import QtWidgets, QtCore, QtGui
import logging

logger = logging.getLogger(__name__)

class Industry40Tab(QtWidgets.QWidget):
    validation_success = QtCore.Signal(list)
    validation_error = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(Industry40Tab, self).__init__(parent)
        self.validation_success.connect(self.on_validation_success)
        self.validation_error.connect(self.on_validation_error)
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
        
        lbl_sub = QtWidgets.QLabel("DEMO MODE :: SIMULATED SENSOR FEED")
        lbl_sub.setStyleSheet("color: #ff9900; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        layout.addWidget(lbl_sub)
        
        # --- 1. DIGITAL TWIN SYNC ---
        grp_twin = QtWidgets.QGroupBox("Digital Twin Link")
        grp_twin.setStyleSheet("""
            QGroupBox { border: 1px solid #ff9900; margin-top: 20px; padding: 15px 10px 10px 10px; font-weight: bold; color: #ff9900; border-radius: 4px; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; left: 10px; padding: 0 5px; background-color: #050505; }
        """)
        twin_layout = QtWidgets.QVBoxLayout(grp_twin)
        
        row_id = QtWidgets.QHBoxLayout()
        lbl_asset = QtWidgets.QLabel("ASSET ID")
        lbl_asset.setStyleSheet("color: #aaa; font-size: 11px; letter-spacing: 1px;")
        row_id.addWidget(lbl_asset)
        
        self.txt_id = QtWidgets.QLineEdit("ASSET-8842-X")
        self.txt_id.setStyleSheet("""
            QLineEdit {
                background: #111; 
                color: #fff; 
                padding: 8px 12px; 
                border: 1px solid #333;
                border-radius: 4px;
                font-family: 'Consolas', monospace;
                font-size: 13px;
                letter-spacing: 2px;
            }
            QLineEdit:focus {
                border: 1px solid #ff9900;
                background: #1a1505;
            }
        """)
        row_id.addWidget(self.txt_id)
        
        # New: Get Selected Button
        self.btn_get_sel = QtWidgets.QPushButton("✜ GET SELECTED")
        self.btn_get_sel.setStyleSheet("""
            QPushButton { 
                background: #222;
                color: #00f3ff; 
                font-weight: bold; 
                padding: 8px 12px;
                border: 1px solid #00f3ff;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: rgba(0, 243, 255, 0.1);
                color: #fff;
            }
        """)
        self.btn_get_sel.clicked.connect(self.get_selected_asset)
        row_id.addWidget(self.btn_get_sel)
        
        self.btn_sync = QtWidgets.QPushButton("⚡ CONNECT LIVE STREAM")
        self.btn_sync.setCheckable(True)
        self.btn_sync.setStyleSheet("""
            QPushButton { 
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2a2a2a, stop:1 #1a1a1a);
                color: #aaa; 
                font-weight: 800; 
                padding: 10px 20px;
                border: 1px solid #444;
                border-radius: 4px;
                font-size: 12px;
                letter-spacing: 1px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #333, stop:1 #222);
                border: 1px solid #ff9900;
                color: #fff;
            }
            QPushButton:checked { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff9900, stop:1 #ff6600);
                color: #000; 
                border: 1px solid #fff;
            }
        """)
        self.btn_sync.toggled.connect(self.toggle_sync)
        row_id.addWidget(self.btn_sync)
        twin_layout.addLayout(row_id)
        
        # Telemetry Labels
        self.lbl_telemetry = QtWidgets.QLabel("TELEMETRY :: DISCONNECTED")
        self.lbl_telemetry.setStyleSheet("""
            color: #555; 
            font-family: 'Consolas', monospace; 
            font-size: 11px; 
            letter-spacing: 1px;
            padding: 5px;
            background: rgba(0,0,0,0.5);
            border-radius: 4px;
        """)
        twin_layout.addWidget(self.lbl_telemetry)
        
        layout.addWidget(grp_twin)
        
        # --- 2. CONNECTED MACHINES (IoT Matrix) ---
        grp_iot = QtWidgets.QGroupBox("Connected Machines")
        grp_iot.setStyleSheet("""
            QGroupBox { border: 1px solid #00aaff; margin-top: 20px; padding: 15px 10px 10px 10px; font-weight: bold; color: #00aaff; border-radius: 4px; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; left: 10px; padding: 0 5px; background-color: #050505; }
        """)
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
            
            # Determine Color Theme based on status
            if status in ["PRINTING", "RENDERING"]:
                 col = "#00ff9d" # Neon Green
                 bg_glow = "rgba(0, 255, 157, 0.05)"
                 border = "rgba(0, 255, 157, 0.3)"
            elif status == "IDLE":
                 col = "#ffcc00" # Warning Yellow
                 bg_glow = "rgba(255, 204, 0, 0.05)"
                 border = "rgba(255, 204, 0, 0.3)"
            else:
                 col = "#ff3333" # Error Red
                 bg_glow = "rgba(255, 51, 51, 0.05)"
                 border = "rgba(255, 51, 51, 0.3)"

            frame.setStyleSheet(f"""
                QFrame {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {bg_glow}, stop:1 #111);
                    border: 1px solid {border}; 
                    border-radius: 6px;
                }}
            """)
            f_layout = QtWidgets.QVBoxLayout(frame)
            f_layout.setContentsMargins(12, 12, 12, 12)
            
            lbl_name = QtWidgets.QLabel(f"⚙ {name}")
            lbl_name.setStyleSheet("font-weight: 900; color: #fff; font-size: 13px; letter-spacing: 1px; border: none; background: transparent;")
            f_layout.addWidget(lbl_name)
            
            lbl_status = QtWidgets.QLabel(f"STATUS :: {status}")
            lbl_status.setStyleSheet(f"color: {col}; font-family: 'Consolas', monospace; font-size: 10px; font-weight: bold; letter-spacing: 1px; border: none; background: transparent;")
            f_layout.addWidget(lbl_status)
            
            prog = QtWidgets.QProgressBar()
            prog.setValue(load)
            prog.setFixedHeight(4)
            prog.setTextVisible(False)
            prog.setStyleSheet(f"""
                QProgressBar {{
                    border: none;
                    background: #222;
                    border-radius: 2px;
                }}
                QProgressBar::chunk {{ 
                    background: {col}; 
                    border-radius: 2px;
                }}
            """)
            f_layout.addWidget(prog)
            
            # 2x2 Grid
            iot_layout.addWidget(frame, i // 2, i % 2)
            
        layout.addWidget(grp_iot)
        
        # --- 3. INDUSTRY 4.0 VALIDATION ---
        grp_val = QtWidgets.QGroupBox("Digital Twin Validation")
        grp_val.setStyleSheet("""
            QGroupBox { border: 1px solid #00f3ff; margin-top: 20px; padding: 15px 10px 10px 10px; font-weight: bold; color: #00f3ff; border-radius: 4px; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; left: 10px; padding: 0 5px; background-color: #050505; }
        """)
        val_layout = QtWidgets.QVBoxLayout(grp_val)
        
        self.btn_validate = QtWidgets.QPushButton("RUN INDUSTRY 4.0 VALIDATION")
        self.btn_validate.setStyleSheet("background-color: #00f3ff; color: #000; font-weight: bold; padding: 10px;")
        self.btn_validate.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.btn_validate.clicked.connect(self.run_validation)
        val_layout.addWidget(self.btn_validate)
        
        self.list_results = QtWidgets.QListWidget()
        self.list_results.setFixedHeight(120)
        self.list_results.setStyleSheet("background: #0a0a0c; border: 1px solid #333; color: #fff; font-family: monospace; padding: 5px;")
        val_layout.addWidget(self.list_results)
        
        layout.addWidget(grp_val)
        
        layout.addStretch()
        
        # Timer for Mock Telemetry
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_telemetry)
        
    def get_selected_asset(self):
        try:
            import maya.cmds as cmds
            sel = cmds.ls(sl=True)
            if sel:
                # Use the short name of the first selected object
                short_name = sel[0].split('|')[-1]
                self.txt_id.setText(short_name)
                # Auto-check the sync button if user desires a fast flow
                # self.btn_sync.setChecked(True) 
            else:
                QtWidgets.QMessageBox.information(self, "Selection Empty", "Please select a 3D asset in the Maya viewport first.")
        except ImportError:
            logger.warning("Maya cmds not found. Cannot get selection.")
            self.txt_id.setText("MOCK-SELECTION-001")

    def toggle_sync(self, checked):
        asset_id = self.txt_id.text()
        
        # Connect to Digital Twin Core
        try:
            # Dynamic import to avoid errors if running outside Maya
            import digital_twin_core as dt_core
            core = dt_core.core
            
            if checked:
                success = core.connect_live_stream(asset_id)
                if success:
                    self.btn_sync.setText("🔴 LIVE LINK ACTIVE")
                    self.lbl_telemetry.setText("TELEMETRY :: STREAMING (120Hz) [OK]")
                    self.lbl_telemetry.setStyleSheet("""
                        color: #00ff9d; 
                        font-family: 'Consolas', monospace; 
                        font-size: 11px; 
                        letter-spacing: 1px;
                        padding: 5px;
                        background: rgba(0, 255, 157, 0.05);
                        border-radius: 4px;
                        border: 1px solid rgba(0, 255, 157, 0.2);
                    """)
                    self.timer.start(500) # Faster update
                else:
                    self.btn_sync.setChecked(False) # Revert
                    self.lbl_telemetry.setText("TELEMETRY :: ERROR - ASSET NOT FOUND")
                    self.lbl_telemetry.setStyleSheet("color: #ff3333; font-family: 'Consolas', monospace; font-size: 11px; padding: 5px;")
                    QtWidgets.QMessageBox.warning(self, "Link Failed", f"Could not find asset '{asset_id}' in scene.")
            else:
                core.disconnect_stream()
                self.btn_sync.setText("⚡ CONNECT LIVE STREAM")
                self.lbl_telemetry.setText("TELEMETRY :: DISCONNECTED")
                self.lbl_telemetry.setStyleSheet("color: #555; font-family: 'Consolas', monospace; font-size: 11px; padding: 5px; background: rgba(0,0,0,0.5); border-radius: 4px;")
                self.timer.stop()
                
        except ImportError:
            # Fallback for testing outside Maya
            logger.warning("DigitalTwinCore not found (running externally?)")
            if checked:
               self.btn_sync.setText("🔴 LIVE LINK (MOCK)")
               self.lbl_telemetry.setText("TELEMETRY :: LOCAL SIMULATION")
               self.lbl_telemetry.setStyleSheet("""
                        color: #ff9900; 
                        font-family: 'Consolas', monospace; 
                        font-size: 11px; 
                        letter-spacing: 1px;
                        padding: 5px;
                        background: rgba(255, 153, 0, 0.05);
                        border-radius: 4px;
                        border: 1px solid rgba(255, 153, 0, 0.2);
                    """)
               self.timer.start(1000)
            else:
               self.btn_sync.setText("⚡ CONNECT LIVE STREAM")
               self.lbl_telemetry.setText("TELEMETRY :: DISCONNECTED")
               self.lbl_telemetry.setStyleSheet("color: #555; font-family: 'Consolas', monospace; font-size: 11px; padding: 5px; background: rgba(0,0,0,0.5); border-radius: 4px;")
               self.timer.stop()

    def update_telemetry(self):
        import random
        # Simulate sensor data
        temp = 60 + random.random() * 10
        rpm = 2400 + random.randint(-100, 100)
        
        # Update text
        self.lbl_telemetry.setText(f"SIMULATED TELEMETRY :: TEMP: {temp:.1f}C | RPM: {rpm} | VIB: NORMAL")
        
        # If in Maya, we could also drive a specialized attribute here
        # e.g. cmds.setAttr("Smart_Floor.Vibration_Hz", rpm)

    def run_validation(self):
        self.btn_validate.setText("VALIDATING...")
        self.btn_validate.setEnabled(False)
        self.list_results.clear()
        
        import threading
        import json
        import urllib.error
        
        def worker():
            try:
                import qyntara_client as qc
                if not hasattr(qc, "qyntara_ui") or not qc.qyntara_ui:
                    self.validation_error.emit("Client UI instance not found. Cannot authenticate request.")
                    return

                payload = {
                    "uuid": self.txt_id.text(),
                    "is_sensor": True, 
                    "telemetry_unit": "celsius", 
                    "update_rate_ms": 100, 
                    "supported_protocols": ["OPC UA", "MQTT"]
                }
                data_bytes = json.dumps({"industry": "industry4", "metadata": payload}).encode("utf-8")
                
                resp_body, status = qc.qyntara_ui._authed_request(
                    f"{qc.API_URL}/validate/core", 
                    data=data_bytes, 
                    headers={"Content-Type": "application/json"},
                    timeout=5
                )
                
                data = json.loads(resp_body)
                results = data.get("results", [])
                self.validation_success.emit(results)
                
            except urllib.error.HTTPError as e:
                err_body = e.read().decode('utf-8')
                self.validation_error.emit(f"HTTP {e.code}: {err_body}")
            except Exception as e:
                self.validation_error.emit(str(e))
                
        threading.Thread(target=worker, daemon=True).start()

    @QtCore.Slot(list)
    def on_validation_success(self, results):
        self.btn_validate.setText("RUN INDUSTRY 4.0 VALIDATION")
        self.btn_validate.setEnabled(True)
        for res in results:
            try:
                status, msg = res[0], res[1]
            except Exception:
                status, msg = "INFO", str(res)
            item = QtWidgets.QListWidgetItem(f"[{status}] {msg}")
            color = "#ff3333" if status == "FAIL" else "#ffc800" if status == "WARNING" else "#00ff9d"
            item.setForeground(QtGui.QBrush(QtGui.QColor(color)))
            self.list_results.addItem(item)
            
    @QtCore.Slot(str)
    def on_validation_error(self, err):
        self.btn_validate.setText("RUN INDUSTRY 4.0 VALIDATION")
        self.btn_validate.setEnabled(True)
        item = QtWidgets.QListWidgetItem(f"[ERROR] API failed: {err}")
        item.setForeground(QtGui.QBrush(QtGui.QColor("#ff3333")))
        self.list_results.addItem(item)
