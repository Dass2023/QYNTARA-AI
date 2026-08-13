
import os

target_file = r"e:\QYNTARA AI\qyntara_ai\ui\blueprint_tab.py"

# New run_ai_analysis method that retrieves openings from memory
new_method = """    def run_ai_analysis(self):
        \"\"\"
        Triggers the Semantic AI Engine (Now with Symbolic Reasoning).
        \"\"\"
        if not self.current_image_path: return
        
        from ..core import advanced_floorplan_ai
        
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        try:
            # 1. Get Lines
            thresh = self.slider_thresh.value() / 100.0
            self.architect.config.threshold = thresh
            
            # Reprocess to ensure Openings are fresh
            self.architect.build_from_image(self.current_image_path) # Just to populate last_openings
            
            clean_lines = self.architect.last_clean_lines
            openings = self.architect.last_openings # DETECTED DOORS!
            
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
    # Truncate
    new_content = "".join(lines[:start_idx]) + new_method
    with open(target_file, "w") as f:
        f.write(new_content)
    print("Success: Patched run_ai_analysis w/ Doors/Furniture.")
else:
    print("Error: Could not find method to patch.")
