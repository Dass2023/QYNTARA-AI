
import os

target_file = r"e:\QYNTARA AI\qyntara_ai\ui\blueprint_tab.py"

new_method = """    def run_ai_analysis(self):
        \"\"\"
        Triggers the Semantic AI Engine.
        \"\"\"
        if not self.current_image_path: return
        
        from ..core import advanced_floorplan_ai
        
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        try:
            # 1. Get Lines from Vectorizer (using Aggressive Solver)
            thresh = self.slider_thresh.value() / 100.0
            raw_lines = self.architect.vectorizer.process_image(self.current_image_path, threshold=thresh, min_len=20)
            clean_lines = self.architect.vectorizer.regularize_lines(raw_lines)
            
            # 2. Run AI
            ai_architect = advanced_floorplan_ai.SemanticArchitect(self.architect.calibration_scale)
            graph = ai_architect.analyze_scene(clean_lines)
            
            # 3. Detect Rooms
            rooms = ai_architect.classify_rooms()
            room_count = len(rooms)
            nodes_count = len(graph.nodes)
            
            QtWidgets.QApplication.restoreOverrideCursor()
            
            # 4. Ask to Build
            reply = QtWidgets.QMessageBox.question(self, "Deep AI Analysis", 
                                                 f"Semantic Analysis Complete.\\n\\n"
                                                 f"- {nodes_count} Graph Nodes\\n"
                                                 f"- {room_count} Enclosed Rooms Detected\\n\\n"
                                                 f"Generate Full Room Geometry?\\n"
                                                 f"(Floors, Ceilings, & Labels)",
                                                 QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
                                                 
            if reply == QtWidgets.QMessageBox.Yes:
                QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
                # Pass wall_height from spinner
                wh = self.spin_height.value()
                created = ai_architect.build_rooms_in_maya(rooms, wall_height=wh, create_ceiling=True, create_labels=True)
                
                QtWidgets.QApplication.restoreOverrideCursor()
                
                if created:
                    from maya import cmds
                    cmds.select(created)
                    QtWidgets.QMessageBox.information(self, "Success", f"Generated {len(created)} 3D Elements (Floors/Ceilings/Labels).")
            
        except Exception as e:
            QtWidgets.QApplication.restoreOverrideCursor()
            logging.error(f"AI Error: {e}")
            QtWidgets.QMessageBox.critical(self, "AI Error", str(e))
"""

# Read file
with open(target_file, "r") as f:
    lines = f.readlines()

# Find start of existing method
start_idx = -1
for i, line in enumerate(lines):
    if "def run_ai_analysis(self):" in line:
        start_idx = i
        break

if start_idx != -1:
    # Truncate file at start_idx and append new method
    new_content = "".join(lines[:start_idx]) + new_method
    with open(target_file, "w") as f:
        f.write(new_content)
    print("Success: Patched run_ai_analysis w/ Labels.")
else:
    print("Error: Could not find method to patch.")
