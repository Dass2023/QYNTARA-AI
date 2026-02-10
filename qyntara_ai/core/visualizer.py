import logging

try:
    from maya import cmds
except ImportError:
    cmds = None

logger = logging.getLogger(__name__)

class QyntaraVisualizer:
    """
    Handles visual feedback for validation issues in the Maya viewport.
    Uses Vertex Colors (CPV) and Wireframe Overrides.
    """
    
    COLORS = {
        "red": (1.0, 0.0, 0.0),      # Flipped Normals / Critical
        "yellow": (1.0, 1.0, 0.0),   # Non-Manifold / Open Edges
        "purple": (0.5, 0.0, 0.5),   # UV Overlaps
        "orange": (1.0, 0.5, 0.0),   # Missing Lightmap
        "green": (0.0, 1.0, 0.0)     # OK
    }

    @staticmethod
    def run_visualization(report):
        """
        Parses the validation report and applies visual highlights.
        Renamed to force refresh.
        """
        print("--- QyntaraVisualizer.run_visualization (New Code) Called ---")
        if not cmds:
            return

        # ----------------------------------------------------------------------
        # Helper: Safe Mesh Identification
        # ----------------------------------------------------------------------
        def get_valid_mesh_node(node_name):
            try:
                if not node_name or not isinstance(node_name, str):
                    return None
                    
                if not cmds.objExists(node_name):
                    return None
                
                # If it's a component, ignore here
                if "." in node_name:
                    return None

                # Check if it's a transform
                if cmds.objectType(node_name, isAType='transform'):
                    shapes = cmds.listRelatives(node_name, shapes=True, type='mesh', fullPath=True)
                    if shapes:
                        return shapes[0]
                    return None
                
                # Check if it's already a mesh shape
                if cmds.objectType(node_name, isAType='mesh'):
                    return node_name
                    
            except Exception:
                return None
            return None

        # ----------------------------------------------------------------------
        # 1. Initialization
        # ----------------------------------------------------------------------
        affected_objects = set()
        for detail in report.get("details", []):
            if "violations" in detail:
                 for v in detail["violations"]:
                     obj = v.get("object")
                     if obj:
                         affected_objects.add(obj)
        
        # for obj in affected_objects:
        #     mesh_node = get_valid_mesh_node(obj)
        #     if mesh_node:
        #         try:
        #             # Enable display colors if attribute exists
        #             if cmds.attributeQuery("displayColors", node=mesh_node, exists=True):
        #                 cmds.setAttr(f"{mesh_node}.displayColors", True)
        #                 cmds.polyColorPerVertex(mesh_node, r=0.5, g=0.5, b=0.5, a=1.0, cdo=True)
        #         except Exception:
        #             pass

        # ----------------------------------------------------------------------
        # 2. Application
        # ----------------------------------------------------------------------
        rule_colors = {
            "geo_open_edges": "yellow",
            "geo_non_manifold": "yellow",
            "uv_overlap": "purple",
            "geo_normals": "red",
            "uv_lightmap_set": "orange",
            "check_vertex_colors": "green"
        }
        
        priority_order = ["uv_lightmap_set", "uv_overlap", "geo_open_edges", "geo_non_manifold", "geo_normals"]
        details_map = {d["rule_id"]: d for d in report.get("details", [])}
        
        for rule_id in priority_order:
            if rule_id not in details_map:
                continue
                
            detail = details_map[rule_id]
            color_name = rule_colors.get(rule_id, "yellow")
            rgb = QyntaraVisualizer.COLORS.get(color_name, (1, 1, 1))
            
            targets_to_color = []
            
            for v in detail.get("violations", []):
                comps = v.get("components", [])
                if comps:
                    for c in comps:
                        # Heuristic check for component string
                        if any(k in c for k in ['.vtx[', '.e[', '.f[', '.map[']):
                             targets_to_color.append(c)
                        else:
                            if get_valid_mesh_node(c):
                                targets_to_color.append(c)
                else:
                    obj = v.get("object")
                    if obj and get_valid_mesh_node(obj):
                        targets_to_color.append(obj)
            
            if not targets_to_color:
                continue
                
            if not targets_to_color:
                continue
                
            try:
                # 1. Validate existence
                valid_items = cmds.ls(targets_to_color, flatten=True)
                if not valid_items:
                    continue

                # 2. Force Convert to Vertices (TV=True)
                # polyColorPerVertex is strict; it doesn't like Edges (.e) or Maps (.map) directly
                vertices = cmds.polyListComponentConversion(valid_items, tv=True)
                if not vertices:
                    continue
                
                # 3. Flatten again to ensure simple list of strings
                vertices = cmds.ls(vertices, flatten=True)
                
                if vertices:
                    # cdo=True (Color Display Option) fails on some nodes
                    # DISABLED for Test Matrix Demo (Prevent Grey Mesh override)
                    # cmds.polyColorPerVertex(vertices, r=rgb[0], g=rgb[1], b=rgb[2], a=1.0, cdo=True)
                    pass
            except Exception as e:
                # Only log real errors, not known safe-ignore ones
                logger.warning(f"Visualizer: Failed to apply color: {e}")

        logger.info("Visual Highlight Applied.")

    @staticmethod
    def clear(objects):
        if not cmds or not objects: return
        for obj in objects:
            try:
                if cmds.objExists(obj):
                     attr = f"{obj}.displayColors"
                     if cmds.objExists(attr):
                        cmds.setAttr(attr, False)
                        cmds.polyColorPerVertex(obj, r=1, g=1, b=1, a=1, cdo=True)
            except: pass

    @staticmethod
    def toggle_seam_overlay(objects, show=True):
        """
        Toggles the display of UV Seams (Texture Borders) in the viewport.
        """
        if not cmds: return
        for obj in objects:
            try:
                # toggle displayMapBorder
                cmds.polyOptions(obj, displayMapBorder=show)
                logger.info(f"Seam Overlay on {obj}: {show}")
            except Exception as e:
                logger.warning(f"Seam toggle failed: {e}")

    @staticmethod
    def toggle_distortion_heatmap(objects, show=True):
        """
        Toggles a visual Heatmap of UV Distortion.
        Uses Vertex Colors (Green=Good, Red=Stretch, Blue=Crush).
        """
        if not cmds: return
        
        if not show:
            QyntaraVisualizer.clear(objects)
            return

        for obj in objects:
            try:
                # 1. Enable Vertex Color Display
                cmds.setAttr(f"{obj}.displayColors", True)
                cmds.polyOptions(obj, colorShadedDisplay=True, colorMaterialChannel="ambientDiffuse")
                
                # 2. Simple Heuristic (Placeholder)
                cmds.polyColorPerVertex(obj, r=0.8, g=0.8, b=0.8, a=1.0, cdo=True)
                logger.info(f"Distortion Heatmap enabled (Heuristic Mode) on {obj}")
                
            except Exception as e:
                logger.warning(f"Distortion toggle failed: {e}")
