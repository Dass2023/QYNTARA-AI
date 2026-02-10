from .qt_utils import QtWidgets, QtCore, QtGui
import logging

logger = logging.getLogger(__name__)

try:
    from maya import cmds
except ImportError:
    cmds = None

class AlignmentWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(AlignmentWidget, self).__init__(parent)
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
        
        # --- TITLE ---
        lbl_title = QtWidgets.QLabel("Geometry Alignment Tools")
        lbl_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #fff;")
        layout.addWidget(lbl_title)
        

        
        # --- SMART SNAPPING ---
        grp_snap = QtWidgets.QGroupBox("Smart Snapping")
        grp_snap.setStyleSheet("QGroupBox { border: 1px solid #00CEC9; margin-top: 6px; padding-top: 10px; font-weight: bold; }")
        snap_layout = QtWidgets.QVBoxLayout(grp_snap)
        
        self.btn_gap_snap_obj = QtWidgets.QPushButton("Snap Objects Together")
        self.btn_gap_snap_obj.setMinimumHeight(40)
        self.btn_gap_snap_obj.setStyleSheet("background-color: #2ea043; color: white; font-weight: bold;")
        self.btn_gap_snap_obj.clicked.connect(self.run_auto_snap)
        snap_layout.addWidget(self.btn_gap_snap_obj)
        
        lbl_desc = QtWidgets.QLabel("Automatically detects the gap between facing surfaces and snaps them flush.")
        lbl_desc.setStyleSheet("color: #888; font-size: 11px; margin-top: 5px;")
        lbl_desc.setWordWrap(True)
        snap_layout.addWidget(lbl_desc)
        
        layout.addWidget(grp_snap)
        
        # --- AI TRAINING (New) ---
        grp_ai = QtWidgets.QGroupBox("AI Model Training")
        grp_ai.setStyleSheet("QGroupBox { border: 1px solid #d29922; margin-top: 6px; padding-top: 10px; }")
        ai_layout = QtWidgets.QVBoxLayout(grp_ai)
        
        btn_layout = QtWidgets.QHBoxLayout()
        
        self.btn_gen_data = QtWidgets.QPushButton("Generate Dataset")
        self.btn_gen_data.clicked.connect(self.run_generate_data)
        
        self.btn_train = QtWidgets.QPushButton("Train Model")
        self.btn_train.clicked.connect(self.run_training)
        
        btn_layout.addWidget(self.btn_gen_data)
        btn_layout.addWidget(self.btn_train)
        ai_layout.addLayout(btn_layout)
        
        self.lbl_train_status = QtWidgets.QLabel("Status: Idle")
        self.lbl_train_status.setStyleSheet("color: #888; font-size: 10px;")
        ai_layout.addWidget(self.lbl_train_status)
        
        layout.addWidget(grp_ai)


        
        # Spacer
        layout.addStretch()
        
        # Legacy / Manual Tools (Collapsed or moved down)
        # We can hide the old groups if we want a cleaner UI, or keep them below.
        # User asked to "Realign Tap" -> Let's prioritize the AI workflow.

        
        layout.addStretch()
        
    def run_auto_snap(self):
        try:
            from ..core.fixer import QyntaraFixer
            # The logic in fixer.py handles "Object Mode" -> Smart Snap automatically
            result = QyntaraFixer.fix_vertex_snap()
            if result:
                QtWidgets.QMessageBox.information(self, "Success", "Smart Snap applied successfully.")
            else:
                QtWidgets.QMessageBox.warning(self, "Failed", "Could not snap. Ensure two objects are selected.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))


    def run_icp(self):
        try:
             from ..core import alignment
             sel = cmds.ls(sl=True) if cmds else []
             if len(sel) < 2:
                 QtWidgets.QMessageBox.warning(self, "Warning", "Select Source then Target.")
                 return
                 
             # Default to Transform Match
             alignment.align_objects(sel[0], sel[1], method="transforms")
             QtWidgets.QMessageBox.information(self, "Aligned", "Matched Transforms.")
        except Exception as e:
            logger.error(f"Align Error: {e}")

    def run_find_gaps(self):
        try:
             from ..core import alignment
             sel = cmds.ls(sl=True) if cmds else []
             if not sel:
                 QtWidgets.QMessageBox.warning(self, "Warning", "Select objects to check.")
                 return
                 
             gaps = alignment.find_gaps(sel)
             if gaps:
                 cmds.select(gaps)
                 QtWidgets.QMessageBox.warning(self, "Gaps Found", f"Found {len(gaps)} open edges (Selected).")
             else:
                 QtWidgets.QMessageBox.information(self, "Clean", "No open gaps found.")
        except Exception as e:
            logger.error(f"Gap Error: {e}")

    def run_fill_gaps(self, method):
        try:
             from ..core import alignment
             sel = cmds.ls(sl=True) if cmds else []
             if not sel:
                 QtWidgets.QMessageBox.warning(self, "Warning", "Select objects to fill.")
                 return
                 
             result = alignment.fill_gaps(sel, method=method)
             if result:
                 QtWidgets.QMessageBox.information(self, "Success", f"Gap Fill ({method}) applied.")
             else:
                 QtWidgets.QMessageBox.warning(self, "Failed", "Could not fill gaps. Check selection/borders.")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def run_generate_data(self):
        # 1. Check for User Selection (Safe Mode)
        selection = cmds.ls(sl=True, type="transform") if cmds else []
        custom_objects = None
        
        if selection:
            reply = QtWidgets.QMessageBox.question(self, "Generate from Selection", 
                                                 f"Generate training data based on your {len(selection)} selected objects?\n\n"
                                                 "This will NOT delete your scene.\nIt will create temporary variations and export them.",
                                                 QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, 
                                                 QtWidgets.QMessageBox.Yes)
            if reply == QtWidgets.QMessageBox.Yes:
                custom_objects = selection
        
        # 2. If no selection (or user said No), use Procedural Mode (Destructive)
        if not custom_objects:
            selection_warning = "No objects selected. Switching to PROCEDURAL mode."
            reply = QtWidgets.QMessageBox.question(self, "Confirm Procedural Generation", 
                                                 f"{selection_warning}\n\n"
                                                 "This process will CLEAR YOUR CURRENT SCENE to generate synthetic blocks.\n"
                                                 "Are you sure you want to proceed?",
                                                 QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, 
                                                 QtWidgets.QMessageBox.No)
                                                 
            if reply == QtWidgets.QMessageBox.No:
                return

        self.lbl_train_status.setText("Status: Generating Data...")
        QtWidgets.QApplication.processEvents()
        try:
             # run inside Maya
             from ..ai_assist.generate_dataset import DatasetGenerator
             gen = DatasetGenerator()
             
             # Generate!
             gen.generate_batch(10, custom_objects=custom_objects)
             
             self.lbl_train_status.setText("Status: Dataset Ready.")
             QtWidgets.QMessageBox.information(self, "Success", "Generated 10 scene pairs.")
        except Exception as e:
            self.lbl_train_status.setText("Status: Error")
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def run_training(self):
        self.lbl_train_status.setText("Status: Training...")
        QtWidgets.QApplication.processEvents()
        try:
            # Import training logic
            # This might fail if torch not installed, but Mock will take over
            from ..ai_assist import train_model
            # Run
            train_model.run_training()
            self.lbl_train_status.setText("Status: Training Complete.")
            QtWidgets.QMessageBox.information(self, "Success", "Model trained and saved.")
        except Exception as e:
             self.lbl_train_status.setText(f"Status: Train Error: {e}")
             logger.error(f"Training failed: {e}")


