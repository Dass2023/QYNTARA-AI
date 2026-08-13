from .qt_utils import QtWidgets, QtCore, QtGui
import logging
import math
from ..core import floorplan_builder

logger = logging.getLogger(__name__)

# --- NEW CANVAS CLASS ---
class ScannerCanvas(QtWidgets.QGraphicsView):
    """
    Advanced Interactive Canvas for Blueprint Manipulation.
    Supports: Pan, Zoom, Calibration Clicks, Debug Drawing.
    """
    calibration_points_needed = QtCore.Signal(int)
    calibration_done = QtCore.Signal(float) # Returns pixel distance

    def __init__(self, parent=None):
        super(ScannerCanvas, self).__init__(parent)
        self.scene = QtWidgets.QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30,30,30)))
        
        self.pixmap_item = None
        self.calib_points = []
        self.is_calibrating = False

    def load_image(self, path):
        self.scene.clear()
        pixmap = QtGui.QPixmap(path)
        if pixmap.isNull(): return False
        
        self.pixmap_item = self.scene.addPixmap(pixmap)
        self.scene.setSceneRect(QtCore.QRectF(pixmap.rect()))
        self.fitInView(self.scene.itemsBoundingRect(), QtCore.Qt.KeepAspectRatio)
        return True

    def start_calibration(self):
        self.is_calibrating = True
        self.calib_points = []
        self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        self.setCursor(QtCore.Qt.CrossCursor)

    def mousePressEvent(self, event):
        if self.is_calibrating and event.button() == QtCore.Qt.LeftButton:
            # Map to Scene
            scene_pos = self.mapToScene(event.pos())
            
            # Add Marker
            marker = self.scene.addEllipse(scene_pos.x()-5, scene_pos.y()-5, 10, 10, 
                                           QtGui.QPen(QtCore.Qt.red), QtGui.QBrush(QtCore.Qt.red))
            self.calib_points.append(scene_pos)
            
            if len(self.calib_points) >= 2:
                # Done
                p1 = self.calib_points[0]
                p2 = self.calib_points[1]
                dist = math.sqrt((p2.x()-p1.x())**2 + (p2.y()-p1.y())**2)
                
                # Draw Line
                line = self.scene.addLine(p1.x(), p1.y(), p2.x(), p2.y(), 
                                          QtGui.QPen(QtGui.QColor(0, 255, 0), 2))
                
                self.calibration_done.emit(dist)
                self.is_calibrating = False
                self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
                self.setCursor(QtCore.Qt.ArrowCursor)
        else:
            super(ScannerCanvas, self).mousePressEvent(event)

    def draw_debug_vectors(self, lines):
        # Clear previous debug items
        for item in self.scene.items():
            if hasattr(item, 'is_debug'):
                self.scene.removeItem(item)
                
        pen = QtGui.QPen(QtGui.QColor(0, 255, 0), 3) # Green Thick Line
        pen.setCosmetic(True)
        
        for p1, p2 in lines:
            line_item = self.scene.addLine(p1.x, p1.y, p2.x, p2.y, pen)
            line_item.is_debug = True
            
            # Draw endpoints
            r = 4
            ell = self.scene.addEllipse(p1.x-r, p1.y-r, r*2, r*2, QtGui.QPen(QtCore.Qt.red), QtGui.QBrush(QtCore.Qt.red))
            ell.is_debug = True
            getattr(ell, 'setZValue')(10) # Draw on top
            
            ell2 = self.scene.addEllipse(p2.x-r, p2.y-r, r*2, r*2, QtGui.QPen(QtCore.Qt.red), QtGui.QBrush(QtCore.Qt.red))
            ell2.is_debug = True
            getattr(ell2, 'setZValue')(10)

class BlueprintWidget(QtWidgets.QWidget):
    """
    Blueprint Studio Tab.
    Dedicated interface for Image-to-3D Wall workflow.
    """
    def __init__(self, parent=None):
        super(BlueprintWidget, self).__init__(parent)
        self.architect = floorplan_builder.FloorPlanArchitect()
        self.current_image_path = None
        self.init_ui()
        
    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        
        # Header
        h_frame = QtWidgets.QFrame()
        h_frame.setStyleSheet("background: #252526; border-bottom: 1px solid #333;")
        h_layout = QtWidgets.QHBoxLayout(h_frame)
        h_layout.addWidget(QtWidgets.QLabel("<b>BLUEPRINT STUDIO</b>"))
        
        self.btn_load_img = QtWidgets.QPushButton("Load Blueprint")
        self.btn_load_img.setStyleSheet("background: #444; color: white; padding: 4px;")
        self.btn_load_img.clicked.connect(self.load_blueprint)
        h_layout.addWidget(self.btn_load_img)
        
        self.btn_calibrate = QtWidgets.QPushButton("Calibrate Scale")
        self.btn_calibrate.setStyleSheet("background: #d19a66; color: black; padding: 4px;")
        self.btn_calibrate.clicked.connect(self.start_calibration)
        self.btn_calibrate.setEnabled(False)
        h_layout.addWidget(self.btn_calibrate)

        # TD DEBUG BUTTON
        self.btn_preview = QtWidgets.QPushButton("Preview Graph")
        self.btn_preview.setStyleSheet("background: #5A5A5A; color: white; padding: 4px;")
        self.btn_preview.clicked.connect(self.run_vector_preview)
        h_layout.addWidget(self.btn_preview)
        
        layout.addWidget(h_frame)
        
        # Canvas
        self.canvas = ScannerCanvas()
        self.canvas.calibration_done.connect(self.on_calibration_finished)
        layout.addWidget(self.canvas)
        
        # Controls
        c_frame = QtWidgets.QFrame()
        c_frame.setStyleSheet("background: #2D2D2D; border-top: 1px solid #333;")
        c_layout = QtWidgets.QHBoxLayout(c_frame)
        
        c_layout.addWidget(QtWidgets.QLabel("Threshold:"))
        self.slider_thresh = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider_thresh.setRange(1, 99)
        self.slider_thresh.setValue(50)
        c_layout.addWidget(self.slider_thresh)
        
        # PHASE 3: Live Preview Toggle
        self.chk_live = QtWidgets.QCheckBox("🔴 LIVE Preview")
        self.chk_live.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        self.chk_live.setToolTip("Real-time 3D preview as you adjust threshold (Experimental)")
        self.chk_live.toggled.connect(self.toggle_live_preview)
        c_layout.addWidget(self.chk_live)
        
        c_layout.addWidget(QtWidgets.QLabel("Wall Height (cm):"))
        self.spin_height = QtWidgets.QSpinBox()
        self.spin_height.setRange(100, 1000)
        self.spin_height.setValue(300)
        c_layout.addWidget(self.spin_height)
        
        self.btn_build_3d = QtWidgets.QPushButton("BUILD 3D WALLS")
        self.btn_build_3d.setStyleSheet("background: #00acc1; color: white; font-weight: bold; padding: 6px;")
        self.btn_build_3d.clicked.connect(self.run_floorplan_build)
        self.btn_build_3d.setEnabled(False)
        c_layout.addWidget(self.btn_build_3d)
        
        self.btn_ai_analysis = QtWidgets.QPushButton("RUN DEEP AI ANALYSIS (BETA)")
        self.btn_ai_analysis.setStyleSheet("background: #9c27b0; color: white; font-weight: bold; padding: 6px;")
        self.btn_ai_analysis.clicked.connect(self.run_ai_analysis)
        self.btn_ai_analysis.setEnabled(False)
        c_layout.addWidget(self.btn_ai_analysis)
        
        layout.addWidget(c_frame)
        
        # PHASE 3: Live Preview Timer (Debounce)
        self.live_timer = QtCore.QTimer()
        self.live_timer.setSingleShot(True)
        self.live_timer.timeout.connect(self.update_live_preview)
        self.preview_layer = None  # Maya display layer for preview geometry

    def load_blueprint(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Floorplan", "", "Images (*.png *.jpg *.jpeg)")
        if path:
            if self.canvas.load_image(path):
                self.current_image_path = path
                self.btn_calibrate.setEnabled(True)
                self.btn_build_3d.setEnabled(True)
                self.btn_ai_analysis.setEnabled(True)
    
    def start_calibration(self):
        QtWidgets.QMessageBox.information(self, "Calibrate", "Click TWO points on the blueprint that represent a known distance.")
        self.canvas.start_calibration()
        
    def on_calibration_finished(self, pixel_dist):
        real_dist, ok = QtWidgets.QInputDialog.getDouble(self, "Real World Distance", 
                                                         f"Pixel Distance: {pixel_dist:.1f}\nEnter Real Distance (cm):", 
                                                         300, 1, 10000, 1)
        if ok:
            self.architect.set_scale_from_pixels(pixel_dist, real_dist)
            QtWidgets.QMessageBox.information(self, "Calibrated", f"Scale Set.\n1 Pixel = {self.architect.calibration_scale:.2f} cm")

    def run_floorplan_build(self):
        if not self.current_image_path: return
        
        thresh = self.slider_thresh.value() / 100.0
        height = self.spin_height.value()
        
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        try:
            # Updates Global Config internally
            nodes, msg = self.architect.build_from_image(self.current_image_path, threshold=thresh, wall_height=height)
            if nodes:
                 from maya import cmds
                 cmds.select(nodes)
                 cmds.viewFit()
            QtWidgets.QApplication.restoreOverrideCursor()
            QtWidgets.QMessageBox.information(self, "Build Complete", msg)
        except Exception as e:
            QtWidgets.QApplication.restoreOverrideCursor()
            logging.error(f"Build Failed: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def run_vector_preview(self):
        """Standardized Debug Preview."""
        if not self.current_image_path: return
        
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        try:
            # 1. Update Config from UI
            thresh = self.slider_thresh.value() / 100.0
            self.architect.config.threshold = thresh
            
            # 2. Run Vectorization Steps Manually (Mirroring Core)
            raw = self.architect.vectorizer.process_image(self.current_image_path)
            # openings = self.architect.vectorizer.detect_openings(raw) # Optional debug
            clean = self.architect.vectorizer.regularize_lines(raw)
            islands = self.architect.vectorizer.filter_islands(clean)
            final = self.architect.vectorizer.prune_dead_ends(islands)
            
            # 3. Draw on Canvas
            self.canvas.draw_debug_vectors(final)
            
            QtWidgets.QApplication.restoreOverrideCursor()
            QtWidgets.QMessageBox.information(self, "Preview", f"Visualizing {len(final)} Wall Segments.\\nGreen = Wall, Red = Vertex.")
            
        except Exception as e:
            QtWidgets.QApplication.restoreOverrideCursor()
            QtWidgets.QMessageBox.critical(self, "Error", str(e))

    def run_ai_analysis(self):
        """
        Triggers the Semantic AI Engine (Now with Symbolic Reasoning).
        """
        if not self.current_image_path: return
        
        from ..core import advanced_floorplan_ai
        
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        try:
            # 1. Get Lines
            thresh = self.slider_thresh.value() / 100.0
            self.architect.config.threshold = thresh
            
            # Reprocess to ensure Openings are fresh
            # The build_from_image now populates last_clean_lines and last_openings
            self.architect.build_from_image(self.current_image_path) 
            
            clean_lines = self.architect.last_clean_lines
            openings = self.architect.last_openings
            
            # 2. Run AI Analysis
            ai_architect = advanced_floorplan_ai.SemanticArchitect(self.architect.calibration_scale)
            graph = ai_architect.analyze_scene(clean_lines)
            
            # 3. Detect Rooms
            rooms = ai_architect.classify_rooms()
            
            QtWidgets.QApplication.restoreOverrideCursor()
            
            reply = QtWidgets.QMessageBox.question(self, "Deep AI Analysis", 
                                                 "Semantic Analysis Complete.\\n"
                                                 f"- {len(rooms)} Rooms Classified\\n"
                                                 f"- {len(openings)} Doors Identified\\n\\n"
                                                 "Generate Full Environment?\\n(Floors, Ceilings, Labels, Doors, Furniture)",
                                                 QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                                                 
            if reply == QtWidgets.QMessageBox.Yes:
                QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
                wh = self.spin_height.value()
                
                created = ai_architect.build_rooms_in_maya(
                    rooms, 
                    wall_height=wh, 
                    create_ceiling=True, 
                    create_labels=True,
                    image_path=self.current_image_path,
                    openings=openings # PASS THE DOORS
                )
                
                QtWidgets.QApplication.restoreOverrideCursor()
                
                if created:
                    from maya import cmds
                    cmds.select(created)
                    QtWidgets.QMessageBox.information(self, "Success", f"AI Generated {len(created)} Assets.\\nIncluding Doors & Furniture.")
            
        except Exception as e:
            QtWidgets.QApplication.restoreOverrideCursor()
            logging.error(f"AI Error: {e}")
            QtWidgets.QMessageBox.critical(self, "AI Error", str(e))

    # --- PHASE 3: LIVE PREVIEW METHODS ---
    def toggle_live_preview(self, enabled):
        """Enable/Disable live preview mode."""
        if enabled:
            self.chk_live.setText("🟢 LIVE Preview")
            self.chk_live.setStyleSheet("color: #00ff9d; font-weight: bold;")
            # Connect slider to live update
            self.slider_thresh.valueChanged.connect(self.on_threshold_changed)
            self.spin_height.valueChanged.connect(self.on_threshold_changed)
        else:
            self.chk_live.setText("🔴 LIVE Preview")
            self.chk_live.setStyleSheet("color: #ff6b6b; font-weight: bold;")
            # Disconnect slider
            try:
                self.slider_thresh.valueChanged.disconnect(self.on_threshold_changed)
                self.spin_height.valueChanged.disconnect(self.on_threshold_changed)
            except:
                pass
            # Cleanup preview geometry
            self.cleanup_preview_geometry()
    
    def on_threshold_changed(self, value):
        """Debounced handler for slider changes."""
        if self.chk_live.isChecked() and self.current_image_path:
            # Restart timer (debounce)
            self.live_timer.start(500)  # 500ms delay
    
    def update_live_preview(self):
        """Generate preview geometry in Maya (non-destructive)."""
        if not self.current_image_path:
            return
            
        try:
            from maya import cmds
            
            # 1. Cleanup old preview
            self.cleanup_preview_geometry()
            
            # 2. Get current settings
            thresh = self.slider_thresh.value() / 100.0
            height = self.spin_height.value()
            
            # 3. Run vectorization (no Maya geometry yet)
            self.architect.config.threshold = thresh
            raw = self.architect.vectorizer.process_image(self.current_image_path)
            clean = self.architect.vectorizer.regularize_lines(raw)
            islands = self.architect.vectorizer.filter_islands(clean)
            final = self.architect.vectorizer.prune_dead_ends(islands)
            
            # 4. Create temporary preview geometry
            preview_nodes = []
            for line in final:
                # Convert to Maya coordinates
                p1 = line[0]
                p2 = line[1]
                
                # Scale to real-world
                scale = self.architect.calibration_scale if self.architect.calibration_scale > 0 else 1.0
                x1, z1 = p1.x * scale, p1.y * scale
                x2, z2 = p2.x * scale, p2.y * scale
                
                # Create cube for wall segment
                wall = cmds.polyCube(w=5, h=height, d=abs(z2-z1) if abs(z2-z1) > 1 else abs(x2-x1), name="PREVIEW_wall")[0]
                
                # Position
                mid_x = (x1 + x2) / 2.0
                mid_z = (z1 + z2) / 2.0
                cmds.move(mid_x, height/2.0, mid_z, wall, absolute=True)
                
                # Rotate if needed
                import math
                angle = math.degrees(math.atan2(z2-z1, x2-x1))
                cmds.rotate(0, angle, 0, wall, absolute=True)
                
                preview_nodes.append(wall)
            
            # 5. Create/Update Display Layer
            if not self.preview_layer or not cmds.objExists(self.preview_layer):
                self.preview_layer = cmds.createDisplayLayer(name="QYNTARA_PREVIEW_LAYER", empty=True)
                cmds.setAttr(f"{self.preview_layer}.displayType", 2)  # Reference mode
                cmds.setAttr(f"{self.preview_layer}.color", 17)  # Yellow
            
            # Add to layer
            if preview_nodes:
                cmds.editDisplayLayerMembers(self.preview_layer, *preview_nodes)
            
            print(f"[Live Preview] Generated {len(preview_nodes)} wall segments")
            
        except Exception as e:
            logging.error(f"Live Preview Error: {e}")
    
    def cleanup_preview_geometry(self):
        """Remove all preview geometry from Maya scene."""
        try:
            from maya import cmds
            
            # Delete all objects starting with PREVIEW_
            preview_objs = cmds.ls("PREVIEW_*", long=True)
            if preview_objs:
                cmds.delete(preview_objs)
            
            # Delete preview layer
            if self.preview_layer and cmds.objExists(self.preview_layer):
                cmds.delete(self.preview_layer)
                self.preview_layer = None
                
        except Exception as e:
            logging.error(f"Cleanup Error: {e}")
