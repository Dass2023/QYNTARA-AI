import logging
import math

try:
    from maya import cmds
    import maya.api.OpenMaya as om
except ImportError:
    cmds = None
    om = None

logger = logging.getLogger(__name__)

def align_objects(source, target, method="transforms"):
    """
    Aligns source object to target object.
    methods:
    - 'transforms': Matches Translation and Rotation.
    - 'center': Aligns Bounding Box Centers (maintains rotation).
    """
    if not cmds: return False
    
    try:
        if method == "transforms":
            # Match Pivot to Pivot
            # xform matches translation and rotation
            # ws=True, ro=True (rotation only?), t=True
            
            # Get specific xform
            t = cmds.xform(target, q=True, ws=True, t=True)
            ro = cmds.xform(target, q=True, ws=True, ro=True)
            
            cmds.xform(source, ws=True, t=t)
            cmds.xform(source, ws=True, ro=ro)
            
            return True
            
        elif method == "center":
            # Get Centers
            # exactWorldBoundingBox
            b1 = cmds.exactWorldBoundingBox(source)
            b2 = cmds.exactWorldBoundingBox(target)
            
            c1 = [(b1[0]+b1[3])/2.0, (b1[1]+b1[4])/2.0, (b1[2]+b1[5])/2.0]
            c2 = [(b2[0]+b2[3])/2.0, (b2[1]+b2[4])/2.0, (b2[2]+b2[5])/2.0]
            
            # Offset
            dx = c2[0] - c1[0]
            dy = c2[1] - c1[1]
            dz = c2[2] - c1[2]
            
            cmds.move(dx, dy, dz, source, r=True, ws=True)
            return True
            
    except Exception as e:
        logger.error(f"Alignment failed: {e}")
        return False
        
    return False

# --- GAP MANAGER ---

def find_gaps(objects, tolerance=0.1):
    """
    Finds open border edges in selected objects.
    Returns list of edge components.
    """
    gaps = []
    if not cmds: return gaps
    
    for obj in objects:
        try:
            # Find border edges
            edges = cmds.polyListComponentConversion(obj, te=True, bo=True)
            if edges:
                edges = cmds.ls(edges, flatten=True)
                if edges:
                    gaps.extend(edges)
        except:
            pass
            
    return gaps



def fill_gaps(objects, method="snap", tolerance=0.1):
    """
    Fills gaps.
    - 'snap': Merges vertices within tolerance (polyMergeVertex) - Best for "seams".
    - 'bridge': Bridges two open edge loops.
    """
    if not cmds: return False
    
    try:
        if len(objects) > 1:
            # If multiple objects, we depend on user having them combined
            # OR we attempt to bridge across them if Maya allows (it typically doesn't without combine)
            # User request: REMOVE Auto-Combine.
            # So we just warn if they are separate diff objects?
            # Actually, we can pass multiple objects to `polyBridgeEdge` if they are components.
            # If they are separate transforms, bridge will fail.
            pass
            
        target_obj = objects[0] 
        # Fallback to operating on selection if components passed

                
        if method == "snap":
            # Merge Border Vertices
            edges = cmds.polyListComponentConversion(target_obj, te=True, bo=True)
            if not edges: 
                logger.warning("No border edges found to snap.")
                return False
            
            verts = cmds.polyListComponentConversion(edges, tv=True)
            if not verts: return False
            
            # Merge with "Distance" tolerance
            cmds.polyMergeVertex(verts, d=tolerance, ch=True)
            logger.info(f"Snapped/Sewn Border Vertices (Tol: {tolerance}).")
            return True
            
        elif method == "bridge":
            # Bridge Open Borders
            edges = cmds.polyListComponentConversion(target_obj, te=True, bo=True)
            if not edges: 
                 logger.warning("No border edges found to bridge.")
                 return False
            
            # Attempt Bridge
            # Note: Bridge fails if edge counts don't match or loops are ambiguous.
            try:
                cmds.polyBridgeEdge(edges, ch=True, divisions=0)
                logger.info("Bridged Open Borders.")
                return True
            except Exception as bridge_err:
                logger.warning(f"Standard Bridge failed: Match edge counts or check normals. ({bridge_err})")
                return False
            
    except Exception as e:
        logger.error(f"Fill Gaps ({method}) failed: {e}")
        return False
        
    return False
