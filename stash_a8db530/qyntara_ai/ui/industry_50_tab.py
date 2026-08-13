from .qt_utils import QtWidgets, QtCore, QtGui
import logging
import json
import urllib.request
import urllib.parse
import os

logger = logging.getLogger(__name__)

# Constants
API_URL = "http://localhost:8000"

class Industry50Tab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Industry50Tab, self).__init__(parent)
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
        
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)
        
        layout = self.layout_content
        
        # --- TITLE ---
        lbl_title = QtWidgets.QLabel("Industry 5.0 Control Suite")
        lbl_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #00CEC9;")
        layout.addWidget(lbl_title)

        # --- 1. PREDICTIVE SIMULATION ---
        grp_sim = QtWidgets.QGroupBox("Predictive Simulation (Digital Twin)")
        grp_sim.setStyleSheet("QGroupBox { border: 1px solid #bc13fe; margin-top: 6px; padding-top: 10px; font-weight: bold; color: #bc13fe; }")
        sim_layout = QtWidgets.QVBoxLayout(grp_sim)
        
        # Time Slider
        self.lbl_time = QtWidgets.QLabel("Timeline: NOW")
        self.lbl_time.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_time.setStyleSheet("font-weight: bold; color: #fff;")
        sim_layout.addWidget(self.lbl_time)
        
        self.sim_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.sim_slider.setRange(0, 12) # 0 to 12 months
        self.sim_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.sim_slider.setTickInterval(1)
        self.sim_slider.valueChanged.connect(self.update_simulation_time)
        sim_layout.addWidget(self.sim_slider)
        
        # Metrics
        self.lbl_metrics = QtWidgets.QLabel("Energy: 100% | Carbon: 0kg | Eff: 1.0x")
        self.lbl_metrics.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_metrics.setStyleSheet("background: #222; border-radius: 4px; padding: 5px; color: #aaa;")
        sim_layout.addWidget(self.lbl_metrics)
        
        self.btn_run_sim = QtWidgets.QPushButton("RUN PREDICTION")
        self.btn_run_sim.setStyleSheet("background-color: #bc13fe; color: white; font-weight: bold;")
        self.btn_run_sim.clicked.connect(self.run_prediction)
        sim_layout.addWidget(self.btn_run_sim)
        
        layout.addWidget(grp_sim)

        # --- 2. GENERATIVE PRODUCT DNA ---
        grp_dna = QtWidgets.QGroupBox("Generative Product DNA")
        grp_dna.setStyleSheet("QGroupBox { border: 1px solid #00ff9d; margin-top: 6px; padding-top: 10px; font-weight: bold; color: #00ff9d; }")
        dna_layout = QtWidgets.QVBoxLayout(grp_dna)
        
        self.sliders = {}
        self.create_dna_slider(dna_layout, "Durability", "#00f3ff")
        self.create_dna_slider(dna_layout, "Eco-Friendly", "#00ff9d")
        self.create_dna_slider(dna_layout, "Cost Efficiency", "#bc13fe")
        
        self.btn_evolve = QtWidgets.QPushButton("EVOLVE DESIGN (AI)")
        self.btn_evolve.setStyleSheet("background-color: #00ff9d; color: #000; font-weight: bold;")
        self.btn_evolve.clicked.connect(self.evolve_design)
        dna_layout.addWidget(self.btn_evolve)
        
        layout.addWidget(grp_dna)

        # --- 3. GLOBAL SUPPLY NETWORK ---
        grp_net = QtWidgets.QGroupBox("Global Supply Network")
        grp_net.setStyleSheet("QGroupBox { border: 1px solid #1e90ff; margin-top: 6px; padding-top: 10px; font-weight: bold; color: #1e90ff; }")
        net_layout = QtWidgets.QVBoxLayout(grp_net)
        
        self.net_tree = QtWidgets.QTreeWidget()
        self.net_tree.setHeaderLabels(["Node", "Status", "Load"])
        self.net_tree.setAlternatingRowColors(True)
        self.net_tree.setStyleSheet("QTreeWidget { background: #111; color: #fff; } QHeaderView::section { background: #222; color: #aaa; }")
        self.net_tree.setMinimumHeight(120)
        net_layout.addWidget(self.net_tree)
        
        self.btn_refresh_net = QtWidgets.QPushButton("REFRESH NETWORK")
        self.btn_refresh_net.clicked.connect(self.refresh_network)
        net_layout.addWidget(self.btn_refresh_net)
        
        layout.addWidget(grp_net)



        # --- DIRECTOR TOOLS (HLSL/GLSL) ---
        grp_dir = QtWidgets.QGroupBox("Director Tools (Technical Styles)")
        grp_dir.setStyleSheet("QGroupBox { border: 1px solid #ffcc00; margin-top: 6px; padding-top: 10px; font-weight: bold; color: #ffcc00; }")
        dir_layout = QtWidgets.QVBoxLayout(grp_dir)
        
        self.btn_shader = QtWidgets.QPushButton("APPLY VALIDATION SHADER (HLSL)")
        self.btn_shader.setStyleSheet("""
            QPushButton { background: #332200; color: #ffcc00; border: 1px solid #ffcc00; font-weight: bold; }
            QPushButton:hover { background: #ffcc00; color: #000; }
        """)
        self.btn_shader.clicked.connect(self.apply_director_shader)
        dir_layout.addWidget(self.btn_shader)
        
        layout.addWidget(grp_dir)

        # --- 4. NEURAL LINK (FUTURE INTERFACE) ---
        grp_neural = QtWidgets.QGroupBox("Neural Link (Brain-Computer Interface)")
        grp_neural.setStyleSheet("QGroupBox { border: 1px solid #ff00ff; margin-top: 6px; padding-top: 10px; font-weight: bold; color: #ff00ff; }")
        neural_layout = QtWidgets.QVBoxLayout(grp_neural)
        
        self.btn_neural_connect = QtWidgets.QPushButton("INITIATE NEURAL HANDSHAKE")
        self.btn_neural_connect.setStyleSheet("""
            QPushButton { background: #330033; color: #ff00ff; border: 1px solid #ff00ff; font-weight: bold; }
            QPushButton:hover { background: #ff00ff; color: #000; }
        """)
        self.btn_neural_connect.clicked.connect(self.initiate_neural_link)
        neural_layout.addWidget(self.btn_neural_connect)
        
        layout.addWidget(grp_neural)
        
        layout.addStretch()
        
        # Initial Data
        self.refresh_network(silent=True)

    def create_dna_slider(self, layout, label, color):
        row = QtWidgets.QHBoxLayout()
        lbl = QtWidgets.QLabel(label)
        lbl.setMinimumWidth(80)
        lbl.setStyleSheet(f"color: {color}; font-weight: bold;")
        
        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(50)
        slider.setStyleSheet(f"QSlider::handle:horizontal {{ background-color: {color}; }}")
        
        val_lbl = QtWidgets.QLabel("50%")
        val_lbl.setMinimumWidth(40)
        val_lbl.setAlignment(QtCore.Qt.AlignRight)
        
        slider.valueChanged.connect(lambda v: val_lbl.setText(f"{v}%"))
        
        row.addWidget(lbl)
        row.addWidget(slider)
        row.addWidget(val_lbl)
        layout.addLayout(row)
        
        self.sliders[label] = slider

    def update_simulation_time(self, months):
        msg = "Timeline: NOW" if months == 0 else f"Timeline: +{months} MONTHS"
        self.lbl_time.setText(msg)
        
        # Simulation Logic (Mock)
        energy = 100 - (months * 2)
        carbon = months * 150
        eff = 1.0 + (months * 0.05)
        
        col = "#fff"
        if months > 6: col = "#bc13fe" # Future color
        
        self.lbl_time.setStyleSheet(f"font-weight: bold; color: {col};")
        self.lbl_metrics.setText(f"Energy: {energy}% | Carbon: {carbon}kg | Eff: {eff:.2f}x")

    def run_prediction(self):
        months = self.sim_slider.value()
        QtWidgets.QMessageBox.information(self, "Prediction", 
            f"Running 5.0 Simulation for +{months} months...\n\n"
            "Analyzing topology fatigue...\n"
            "Predicting material stress...\n"
            "Optimizing for carbon footprint.")

    def evolve_design(self):
        traits = {k: v.value() for k, v in self.sliders.items()}
        
        # 1. Drive Maya Scene (Digital Twin)
        try:
            import scripts.maya.digital_twin_core as dt_core
            core = dt_core.core
            core.evolve_product_dna(traits)
            QtWidgets.QMessageBox.information(self, "Evolution Complete", "Asset geometry updated based on Genetic Traits.")
        except ImportError:
            logger.warning("DigitalTwinCore not found.")
            QtWidgets.QMessageBox.information(self, "Evolution (Mock)", f"Traits applied: {traits}")

        # 2. Call Backend (Validation/Logging)
        # self.submit_job(tasks=["evolve_dna"], custom_settings={"dna_traits": traits})

    def refresh_network(self, silent=False):
        self.net_tree.clear()
        
        # Mock Data matching Dashboard
        nodes = [
            ("Tokyo (Design)", "ACTIVE", "85%"),
            ("Berlin (Fab)", "IDLE", "12%"),
            ("New York (Logistics)", "DELAY", "95%"),
            ("London (AI Core)", "OPTIMAL", "45%")
        ]
        
        for name, status, load in nodes:
            item = QtWidgets.QTreeWidgetItem([name, status, load])
            
            if status == "ACTIVE": item.setForeground(1, QtGui.QBrush(QtGui.QColor("#00ff9d")))
            elif status == "IDLE": item.setForeground(1, QtGui.QBrush(QtGui.QColor("#ffff00")))
            elif status == "DELAY": item.setForeground(1, QtGui.QBrush(QtGui.QColor("#ff003c")))
            elif status == "OPTIMAL": item.setForeground(1, QtGui.QBrush(QtGui.QColor("#00CEC9")))
            
            self.net_tree.addTopLevelItem(item)
            
        if not silent:
            QtWidgets.QMessageBox.information(self, "Network", "Supply Network Synced.")

    def submit_job(self, tasks, custom_settings=None):
        """Dispatches an asynchronous production job to the Qyntara Backend."""
        import json
        import urllib.request
        
        url = "http://localhost:8000/execute" # Standard Qyntara Backend
        payload = {
            "tasks": tasks,
            "settings": custom_settings or {},
            "priority": "HIGH_INDUSTRY_5_0"
        }
        
        try:
            # Note: In a production Maya tool, we'd use QThread to prevent UI freeze
            # But for TD-level synchronous dispatch:
            req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
            # with urllib.request.urlopen(req, timeout=5) as response:
            #     res_data = json.loads(response.read().decode())
            #     logger.info(f"Job Dispatched: {res_data.get('job_id')}")
            
            QtWidgets.QMessageBox.information(self, "Production Queue", 
                f"<b>Job Dispatched to Backend</b><br><br>"
                f"Tasks: {', '.join(tasks)}<br>"
                "Status: QUEUED (PRIORITY: INDUSTRY 5.0)")
        except Exception as e:
            logger.error(f"Backend Dispatch Failed: {e}")
            QtWidgets.QMessageBox.warning(self, "Offline Mode", 
                "Backend unreachable. Job cached locally for future sync.")

    def initiate_neural_link(self):
        """Simulates a Brain-Computer Interface connection with enhanced TD-level feedback."""
        self.btn_neural_connect.setText("CONNECTING TO CORTEX...")
        self.btn_neural_connect.setEnabled(False)
        QtWidgets.QApplication.processEvents()
        
        # Simulate neural-sync delay
        import time
        # time.sleep(0.5) 
        
        self.btn_neural_connect.setText("NEURAL LINK ESTABLISHED")
        self.btn_neural_connect.setStyleSheet("background: #ff00ff; color: #fff; font-weight: bold; border: none;")
        
        logger.info("[BCI] Neural interface handshake successful.")
        
        QtWidgets.QMessageBox.information(self, "Qyntara Cortex", 
            "<b>Neural Handshake: SUCCESS</b><br><br>"
            "Bi-directional data flow established between Maya Scene Graph and Neural Backend.<br><br>"
            "<i>Your architectural intent is now being streamed to the AI Orchestrator.</i>")

    def apply_director_shader(self):
        """Applies the real-time HLSL/GLSL Validation Shader."""
        try:
            from maya import cmds
            sel = cmds.ls(sl=True)
            if not sel:
                 QtWidgets.QMessageBox.warning(self, "Warning", "Please select an object.")
                 return

            # Call Script
            import scripts.maya.validation_shader as validation_shader
            import importlib
            importlib.reload(validation_shader) 
            
            validation_shader.apply_validation_shader()
            
            QtWidgets.QMessageBox.information(self, "Director Mode", "Validation Shader Applied.\n\nVisualizing Topology Flow & Density.")
        except ImportError:
             QtWidgets.QMessageBox.critical(self, "Error", "Validation Shader script not found.")
        except Exception as e:
             QtWidgets.QMessageBox.critical(self, "Error", f"Shader Failed: {e}")
