import logging
import random

logger = logging.getLogger(__name__)

class AssetLibrary:
    """
    Spawns clean architectural assets to replace scan blobs.
    """
    
    def __init__(self):
        pass
        
    def replace_with_asset(self, source_obj, asset_type):
        """
        Replaces 'source_obj' with a clean asset of 'asset_type'.
        Matches bounding box.
        """
        from maya import cmds
        
        if not cmds.objExists(source_obj): return None
        
        # 1. Get Bounding Box of Scan Blob
        bbox = cmds.xform(source_obj, q=True, bb=True, ws=True) # xmin, ymin, zmin, xmax, ymax, zmax
        xmin, ymin, zmin, xmax, ymax, zmax = bbox
        
        width = xmax - xmin
        height = ymax - ymin
        depth = zmax - zmin
        
        center_x = (xmin + xmax) / 2
        center_y = (ymin + ymax) / 2
        center_z = (zmin + zmax) / 2
        
        # 2. Spawn Asset
        new_obj = None
        asset_name = f"{asset_type}_Clean_{random.randint(100,999)}"
        
        if asset_type == "Door":
            # Create Frame + Door
            # Simple Cube for now
            new_obj = cmds.polyCube(w=width, h=height, d=depth, name=asset_name)[0]
            # Move pivot to bottom if needed, but center match is easier for bbox
            cmds.move(center_x, center_y, center_z, new_obj)
            
            # Visuals: Make it wood color
            self._assign_color(new_obj, (0.6, 0.4, 0.2)) # Brown
            
        elif asset_type == "Window":
            # Glass Pane
            new_obj = cmds.polyCube(w=width, h=height, d=depth*0.2, name=asset_name)[0] # Thinner
            cmds.move(center_x, center_y, center_z, new_obj)
            
            # Visuals: Make it Blue/Glassy
            self._assign_color(new_obj, (0.4, 0.8, 1.0), transparency=0.5) 

        elif asset_type == "Chair":
             # Primitive replacement
             new_obj = cmds.polyCube(w=width, h=height/2, d=depth, name=asset_name)[0]
             cmds.move(center_x, center_y - height/4, center_z, new_obj)
             # Backrest
             back = cmds.polyCube(w=width, h=height/2, d=depth*0.1)[0]
             cmds.move(center_x, center_y + height/4, center_z - depth/2, back)
             cmds.parent(back, new_obj)
             
        elif asset_type == "Wall":
            # Clean plane
            new_obj = cmds.polyCube(w=width, h=height, d=depth, name=asset_name)[0]
            cmds.move(center_x, center_y, center_z, new_obj)
            
        else:
            # Generic Box
            new_obj = cmds.polyCube(w=width, h=height, d=depth, name=asset_name)[0]
            cmds.move(center_x, center_y, center_z, new_obj)

        # 3. Cleanup
        if new_obj:
            logger.info(f"Replaced {source_obj} with {new_obj}")
            # Hide or Delete original?
            # Usually Hide to be safe
            cmds.setAttr(f"{source_obj}.visibility", 0)
            
        return new_obj

    def _assign_color(self, obj, color, transparency=0.0):
        from maya import cmds
        # Quick Lambert
        mat_name = f"Mat_{obj}"
        if not cmds.objExists(mat_name):
            msg = cmds.shadingNode("lambert", asShader=True, name=mat_name)
            cmds.setAttr(f"{msg}.color", color[0], color[1], color[2], type="double3")
            if transparency > 0:
                 cmds.setAttr(f"{msg}.transparency", transparency, transparency, transparency, type="double3")
                 
            sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=mat_name+"SG")
            cmds.connectAttr(f"{msg}.outColor", f"{sg}.surfaceShader")
            cmds.sets(obj, forceElement=sg)
