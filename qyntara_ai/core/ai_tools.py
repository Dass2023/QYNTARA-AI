import logging
import math
try:
    from maya import cmds
except ImportError:
    cmds = None

logger = logging.getLogger(__name__)

# --- ANALYTIC STANDARDS LIBRARY (Unit: cm) ---
# Heuristic ranges for common asset types.
# Format: "keyword": {"min_height": x, "max_height": y, "desc": "Object Type"}
ANALYTIC_STANDARDS = {
    # General
    "chair":  {"min_height": 40.0,  "max_height": 130.0, "desc": "Seating Standard"},
    "table":  {"min_height": 60.0,  "max_height": 120.0, "desc": "Surface Standard"},
    "door":   {"min_height": 190.0, "max_height": 240.0, "desc": "Architectural Portal"},
    "human":  {"min_height": 150.0, "max_height": 200.0, "desc": "Character Scale"},
    "wall":   {"min_height": 200.0, "max_height": 400.0, "desc": "Structural Standard"},
    
    # Kitchen & Environment
    "counter": {"min_height": 85.0,  "max_height": 95.0,  "desc": "Kitchen Countertop"},
    "cabinet": {"min_height": 70.0,  "max_height": 220.0, "desc": "Kitchen Cabinet (Base/Tall)"}, 
    # Note: Base cabinets ~85-90, Tall ~200+. Generous range or split keys? 
    # Let's split keys if possible, but for simple matching generic is safer for now.
    
    "fridge":  {"min_height": 170.0, "max_height": 190.0, "desc": "Refrigerator"},
    "stove":   {"min_height": 85.0,  "max_height": 95.0,  "desc": "Cooking Range"},
    "oven":    {"min_height": 85.0,  "max_height": 95.0,  "desc": "Cooking Range"},
    "sink":    {"min_height": 85.0,  "max_height": 95.0,  "desc": "Wash Basin level"},
    "island":  {"min_height": 85.0,  "max_height": 110.0, "desc": "Kitchen Island"},
}

class SemanticGrouper:
    """
    Uses heuristic analysis of object names to group them semantically.
    Example: 'chair_01', 'chair_02' -> Grouped under 'chair_grp'
    """
    @staticmethod
    def execute(objects=None):
        if not objects:
            objects = cmds.ls(sl=True, type="transform")
        
        if not objects:
            logger.warning("No objects selected for Semantic Grouping.")
            return False

        # 1. Tokenize and count prefixes
        # Split by '_' and take the first token as the "category"
        groups_map = {}
        for obj in objects:
            short_name = obj.split("|")[-1]
            # Simple heuristic: Split by underscores or digits
            # e.g. "SM_Chair_01" -> "SM", "Chair", "01" -> We might pick "Chair" if "SM" is too common?
            # For V1, lets just take the prefix before the last underscore or number
            
            # Strategy: "prop_chair_01" -> "prop_chair"
            # Strategy: "chair_01" -> "chair"
            tokens = short_name.split("_")
            if len(tokens) > 1:
                # Remove last token if it's a number (common naming convention)
                if tokens[-1].isdigit():
                    prefix = "_".join(tokens[:-1])
                else:
                    prefix = tokens[0] # Fallback to first token
            else:
                prefix = "misc" 
            
            if prefix not in groups_map:
                groups_map[prefix] = []
            groups_map[prefix].append(obj)
            
        # 2. Create Groups
        created_groups = []
        for prefix, members in groups_map.items():
            if len(members) < 2:
                continue # Don't group single items
            
            grp_name = f"{prefix}_grp"
            if not cmds.objExists(grp_name):
                grp_name = cmds.group(em=True, name=grp_name)
            
            cmds.parent(members, grp_name)
            created_groups.append(grp_name)
            
        logger.info(f"Created {len(created_groups)} semantic groups: {created_groups}")
        return created_groups

class LayoutOptimizer:
    """
    Arranges objects in an organized grid layout.
    Useful for set dressing palettes or cleaning up imports.
    """
    @staticmethod
    def execute(objects=None, spacing=100.0):
        if not objects:
            objects = cmds.ls(sl=True, type="transform")
        
        if not objects:
            logger.warning("No objects selected for Layout Optimization.")
            return False

        count = len(objects)
        cols = math.ceil(math.sqrt(count))
        
        for i, obj in enumerate(objects):
            row = i // cols
            col = i % cols
            
            x = col * spacing
            z = row * spacing
            
            # Reset X and Z, keep Y (or reset Y too?)
            # Let's keep Y to respect ground placement if they are already on ground
            # But zero out rotation? Maybe optional.
            
            cmds.move(x, 0, z, obj, a=True, moveXZ=True) # Move XZ absolute
            
        logger.info(f"Optimized layout for {count} objects.")
        return True

class SceneAnalyzer:
    """
    Evaluates model proportions, scaling accuracy, and detects deviations.
    Benchmarks against analytic standards.
    """
    @staticmethod
    def get_world_dimensions(obj):
        # returns (width, height, depth)
        bbox = cmds.exactWorldBoundingBox(obj)
        width = abs(bbox[3] - bbox[0])
        height = abs(bbox[4] - bbox[1])
        depth = abs(bbox[5] - bbox[2])
        return width, height, depth

    @staticmethod
    def execute(objects=None):
        if not objects:
            objects = cmds.ls(sl=True, type="transform")
        
        if not objects:
            return "No objects selected for analysis."

        issues = []
        benchmarks = []
        
        for obj in objects:
            # 1. Scale Checking (Existing)
            scale = cmds.getAttr(f"{obj}.scale")[0]
            if abs(scale[0] - scale[1]) > 0.001 or abs(scale[1] - scale[2]) > 0.001:
                issues.append(f"- {obj}: Non-uniform scale detected {scale}")
            
            if any(abs(s - 1.0) > 0.001 for s in scale):
                issues.append(f"- {obj}: Unfrozen scale (not 1.0)")

            # 2. Analytic Benchmarking (New)
            obj_name_lower = obj.lower()
            detected_category = None
            
            # Simple keyword matching against standards
            for key, std in ANALYTIC_STANDARDS.items():
                if key in obj_name_lower:
                    detected_category = key
                    w, h, d = SceneAnalyzer.get_world_dimensions(obj)
                    
                    # Check Height Deviation
                    min_h = std["min_height"]
                    max_h = std["max_height"]
                    
                    if h < min_h or h > max_h:
                        # --- SOLUTION GENERATION ---
                        target_h = (min_h + max_h) / 2.0
                        ratio = target_h / h if h > 0 else 1.0
                        
                        warning = f"- {obj} ({std['desc']}): Height {h:.1f}cm deviates from standard [{min_h}-{max_h}cm]."
                        solution = f"  -> Solution: Scale Y by approx <b>{ratio:.2f}x</b> to reach ~{target_h:.0f}cm."
                        
                        issues.append(warning + "<br>" + solution)
                    else:
                        benchmarks.append(f"- {obj}: Verified as {std['desc']} (Height: {h:.1f}cm).")
                    break

        if not issues:
            success_msg = ("<b>Scene Analysis Complete</b><br><br>"
                           "All selected models follow analytic standards and principled scaling rules.<br>"
                           "<i>Proportions: Unified and coherent.</i>")
            if benchmarks:
                success_msg += "<br><br><b>Benchmarks Passed:</b><br>" + "<br>".join(benchmarks[:5])
            return success_msg
        
        report = "<b>Scene Analysis Findings (Deviations & Solutions):</b><br><br>"
        report += "Benchmarked against Kitchen & Environment standards:<br><br>"
        report += "<br><br>".join(issues[:10]) # double line break for readability with solutions
        
        return report

    @staticmethod
    def fix_deviations(objects=None):
        """
        Automatically applies scaling fixes to objects deviating from standards.
        Scales UNIFORMLY to match the mean of the target range.
        """
        if not objects:
            objects = cmds.ls(sl=True, type="transform")
        
        if not objects:
            return "No objects selected to fix."
            
        fixed_count = 0
        log = []
        
        for obj in objects:
            obj_name_lower = obj.lower()
            
            for key, std in ANALYTIC_STANDARDS.items():
                if key in obj_name_lower:
                    w, h, d = SceneAnalyzer.get_world_dimensions(obj)
                    min_h = std["min_height"]
                    max_h = std["max_height"]
                    
                    if h < min_h or h > max_h:
                        # Calculate Fix
                        target_h = (min_h + max_h) / 2.0
                        ratio = target_h / h if h > 0 else 1.0
                        
                        # Apply Uniform Scale
                        # We use relative scaling to adjust the existing scale
                        cmds.scale(ratio, ratio, ratio, obj, relative=True)
                        
                        fixed_count += 1
                        log.append(f"Fixed {obj}: Scaled by {ratio:.2f}x to reach {target_h:.1f}cm.")
                    break
        
        if fixed_count == 0:
            return "No deviations found to fix."
            
        return f"<b>Auto-Fix Complete</b><br>Corrected {fixed_count} objects.<br><br>" + "<br>".join(log)
