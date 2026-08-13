import maya.cmds as cmds
import sys
import importlib

# 1. Force Relaod Core Modules to get new logic
if "qyntara_ai.core.floorplan_builder" in sys.modules:
    importlib.reload(sys.modules["qyntara_ai.core.floorplan_builder"])
if "qyntara_ai.core.advanced_floorplan_ai" in sys.modules:
    importlib.reload(sys.modules["qyntara_ai.core.advanced_floorplan_ai"])

from qyntara_ai.ui import blueprint_tab
from qyntara_ai.core import advanced_floorplan_ai

# 2. Define the Updated Method
def run_ai_analysis_patched(self):
    print(">>> Running Advanced AI Analysis (Patched V5)...")
    
    # 1. Re-run local build to ensure data is fresh
    wh = self.config_ui.wall_height.value()
    wt = self.config_ui.wall_thickness.value()
    th = self.config_ui.threshold.value() / 255.0
    
    self.architect.build_from_image(
        self.current_image_path,
        threshold=th,
        wall_height=wh,
        wall_thickness=wt
    )
    
    # 2. Retrieve Data from Architect
    clean_lines = self.architect.last_clean_lines
    openings = self.architect.last_openings
    assets = self.architect.last_assets # NEW: Retrieve symbols
    
    if not clean_lines:
        cmds.warning("No walls vector data found. Build walls first?")
        return

    # 3. Initialize Semantic AI
    ai_architect = advanced_floorplan_ai.SemanticArchitect(self.architect.calibration_scale)
    graph = ai_architect.analyze_scene(clean_lines)
    
    # 4. Infer Rooms
    rooms = ai_architect.classify_rooms()
    print(f"AI Classifed {len(rooms)} rooms.")
    
    # 5. Build 3D Semantics (Pass Assets!)
    created = ai_architect.build_rooms_in_maya(
        rooms, 
        wall_height=wh, 
        image_path=self.current_image_path,
        openings=openings,
        assets=assets # PASS DETECTED FURNITURE
    )
    
    cmds.select(created)
    print(f"AI Generation Complete. Created {len(created)} semantic objects.")

# 3. Apply Patch
blueprint_tab.BlueprintWidget.run_ai_analysis = run_ai_analysis_patched
print("Successfully Patched BlueprintWidget.run_ai_analysis with Asset Support.")
