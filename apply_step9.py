import os

# --- PATCH 1: industry_40_tab.py ---
tab_file = r"I:\QYNTARA AI\maya\tabs\industry_40_tab.py"
with open(tab_file, "r", encoding="utf-8") as f:
    tab_code = f.read()

# 1. Add Signals to class definition
class_def_old = """class Industry40Tab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Industry40Tab, self).__init__(parent)
        self.init_ui()"""

class_def_new = """class Industry40Tab(QtWidgets.QWidget):
    validation_success = QtCore.Signal(list)
    validation_error = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(Industry40Tab, self).__init__(parent)
        self.validation_success.connect(self.on_validation_success)
        self.validation_error.connect(self.on_validation_error)
        self.init_ui()"""
tab_code = tab_code.replace(class_def_old, class_def_new)

# 2. Replace Pipeline Queue with Validation UI
queue_start = tab_code.find("        # --- 3. PIPELINE QUEUE ---")
timer_start = tab_code.find("        # Timer for Mock Telemetry", queue_start)

if queue_start != -1 and timer_start != -1:
    validation_ui = """        # --- 3. INDUSTRY 4.0 VALIDATION ---
        grp_val = QtWidgets.QGroupBox("Digital Twin Validation")
        grp_val.setStyleSheet(\"\"\"
            QGroupBox { border: 1px solid #00f3ff; margin-top: 20px; padding: 15px 10px 10px 10px; font-weight: bold; color: #00f3ff; border-radius: 4px; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; left: 10px; padding: 0 5px; background-color: #050505; }
        \"\"\")
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
        
"""
    tab_code = tab_code[:queue_start] + validation_ui + tab_code[timer_start:]

# 3. Add run_validation logic at the end
validation_logic = """
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
"""
tab_code += validation_logic

with open(tab_file, "w", encoding="utf-8") as f:
    f.write(tab_code)


# --- PATCH 2: qyntara_client.py ---
client_file = r"I:\QYNTARA AI\maya\qyntara_client.py"
with open(client_file, "r", encoding="utf-8") as f:
    client_code = f.read()

target = """        # Tabs
        self.tabs = QtWidgets.QTabWidget()
        controls_layout.addWidget(self.tabs)
        
        # --- Tab 0: INDUSTRY 5.0 (NEW) ---"""

replacement = """        # Tabs
        self.tabs = QtWidgets.QTabWidget()
        controls_layout.addWidget(self.tabs)

        # --- Tab: INDUSTRY 4.0 (RESTORED) ---
        try:
            from tabs.industry_40_tab import Industry40Tab
            self.tab_industry40 = Industry40Tab()
        except Exception as e:
            # Loud Failure Fallback
            self.tab_industry40 = QtWidgets.QWidget()
            err_layout = QtWidgets.QVBoxLayout(self.tab_industry40)
            err_label = QtWidgets.QLabel(f"CRITICAL ERROR: Failed to load Industry 4.0 Tab.\\n\\n{e}")
            err_label.setStyleSheet("color: #ff3333; font-weight: bold; font-size: 14px;")
            err_layout.addWidget(err_label)
            try:
                import maya.cmds as cmds
                cmds.warning(f"Failed to load Industry 4.0 Tab: {e}")
            except: pass
            
        self.tabs.addTab(self.tab_industry40, "INDUSTRY 4.0")
        
        # --- Tab 0: INDUSTRY 5.0 (NEW) ---"""

if target in client_code:
    client_code = client_code.replace(target, replacement)
    with open(client_file, "w", encoding="utf-8") as f:
        f.write(client_code)
    print("Patched qyntara_client.py successfully.")
else:
    print("Target block not found in qyntara_client.py.")

print("Finished applying patches.")
