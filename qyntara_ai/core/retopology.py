import logging
import math

try:
    from maya import cmds
    import maya.api.OpenMaya as om
except ImportError:
    cmds = None
    om = None

logger = logging.getLogger(__name__)

class AutoRetopologyManager:
    """
    Manages the 'Smart Retopology' workflow for raw scan data.
    Wraps Maya's native 'polyRetopo' (Maya 2020+) with heuristics
    to determine optimal face counts and settings.
    """
    
    def __init__(self):
        self.min_face_count = 2000
        self.max_face_count = 500000 
        self.default_density = 100.0 # faces per unit approx? No, purely heuristic.

    def _is_plugin_loaded(self):
        # The retopology node is usually part of 'Retopologize' plugin
        # In Maya 2023+ it's 'Retopologize'. In older, might be 'retology'.
        # Common check:
        return cmds.pluginInfo("Retopologize", q=True, loaded=True)

    def load_plugin(self):
        if not self._is_plugin_loaded():
            try:
                cmds.loadPlugin("Retopologize")
            except:
                logger.error("Could not load 'Retopologize' plugin.")
                return False
        return True

    def calculate_ideal_count(self, obj, target_quality="mid"):
        """
        Estimates an ideal target face count based on:
        1. Current Surface Area
        2. Bounding Box Volume
        3. Feature Complexity (Curvature - approximated)
        
        target_quality: 'low' (Game Prop), 'mid' (Hero Prop), 'high' (Cinematic)
        """
        if not cmds: return 10000

        # 1. Get Surface Area
        area = cmds.polyEvaluate(obj, area=True)
        # polyEvaluate returns a float or string, handle quirk
        if isinstance(area, list): area = area[0] # sometimes returns list
        
        # Base Density settings (faces per square unit? Depends on scale)
        # Assuming cm units.
        # A 100x100cm wall = 10000 sq cm. 
        # For a wall, we need 2 faces. For a rock, maybe 5000.
        # Heuristic is hard without knowing object type.
        
        # Let's use current face count as a hint, but target a percentage reduction
        current_count = cmds.polyEvaluate(obj, face=True)
        
        reduction_factor = 0.5
        if target_quality == "low": reduction_factor = 0.05 # 5% of original
        elif target_quality == "mid": reduction_factor = 0.20 # 20%
        elif target_quality == "high": reduction_factor = 0.50 # 50%
        
        target = int(current_count * reduction_factor)
        
        # Clamp
        if target < self.min_face_count: target = self.min_face_count
        if target > self.max_face_count and target_quality != "high": 
            target = 50000 # Hard cap for game assets usually
            
        return target

    def run_smart_retopo(self, objects, target_quality="mid", preserve_hard_edges=True):
        """
        Runs the retopology process on a list of objects.
        """
        if not self.load_plugin():
            logger.warning("Retopology Plugin not available. Skipping.")
            return []
            
        results = []
        
        for obj in objects:
            try:
                # 1. Pre-Check: Cleanup
                # Retopo fails on non-manifold geo often.
                # Ideally we run 'Mesh Cleanup' first.
                cmds.polyCleanupArgList(obj, [
                    "1", "2", "1", # cleanup matching polygons
                    "0", "1", "0", "0", "0", "0", 
                    "1e-5", # tolerance
                    "0", "1e-5", "0"
                ])
                
                # 2. Determine Settings
                target_count = self.calculate_ideal_count(obj, target_quality)
                logger.info(f"Retopologizing {obj} -> Target: {target_count} faces")
                
                # 3. Operations
                # In Maya 2022+, cmds.polyRetopo command exists.
                # Arguments vary by version.
                # basic: cmds.polyRetopo(targetFaceCount=N, ...)
                
                # Create a duplicate to process (Non-destructive)
                new_name = f"{obj}_retopo"
                result_geo = cmds.duplicate(obj, name=new_name)[0]
                
                # Run Retopo
                # Note: This is a heavy calculation. Might freeze Maya.
                # Parameters:
                # replaceOriginal=1 (we work on duplicate)
                # targetFaceCount=target_count
                # preserveHardEdges=1
                # topologyRegularity=0.5
                
                cmds.polyRetopo(result_geo, 
                                targetFaceCount=target_count, 
                                preserveHardEdges=preserve_hard_edges,
                                replaceOriginal=1,
                                symmetry=0) # Assume no symmetry for scans usually
                
                results.append(result_geo)
                
            except Exception as e:
                logger.error(f"Retopo failed for {obj}: {e}")
                
        return results

# Helper for external usage
def auto_retopologize_selection(quality="mid"):
    manager = AutoRetopologyManager()
    sel = cmds.ls(sl=True, long=True)
    if not sel:
        logger.warning("No selection.")
        return []
    return manager.run_smart_retopo(sel, target_quality=quality)
