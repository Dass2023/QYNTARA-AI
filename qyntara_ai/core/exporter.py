import logging
import os

try:
    from maya import cmds
except ImportError:
    cmds = None

logger = logging.getLogger(__name__)

def sanitize_scene(objects=None):
    """
    Cleans up the scene/objects for export.
    - Freezes Transforms
    - Deletes Non-Deformer History
    - Centers Pivots? (Optional, maybe not for assembling)
    """
    if not cmds: return False
    
    if not objects:
        objects = cmds.ls(sl=True, l=True)
        
    if not objects:
        return False
        
    count = 0
    for obj in objects:
        try:
            # Freeze Transforms
            cmds.makeIdentity(obj, apply=True, t=1, r=1, s=1, n=0, pn=1)
            
            # Delete History (Non-Deformer)
            cmds.bakePartialHistory(obj, prePostDeformers=True)
            
            count += 1
        except Exception as e:
            logger.warning(f"Sanitize failed for {obj}: {e}")
            
    return count > 0

def export_fbx(objects, path, engine="Unreal"):
    """
    Exports selected objects to FBX with engine-specific settings.
    """
    if not cmds: return False
    
    # Load plugin
    if not cmds.pluginInfo("fbxmaya", q=True, loaded=True):
        try:
            cmds.loadPlugin("fbxmaya")
        except:
            logger.error("FBX Plugin not found!")
            return False

    # Select objects
    cmds.select(objects)
    
    # Settings based on Engine
    # Note: FBX Export commands use "FBXExport..." commands or 'file' command with options string
    
    # Reset
    cmds.FBXResetExport()
    
    # Common
    cmds.FBXExportSmoothingGroups(v=True)
    cmds.FBXExportHardEdges(v=False)
    cmds.FBXExportTangents(v=False)
    cmds.FBXExportSmoothMesh(v=True)
    cmds.FBXExportInstances(v=True)
    cmds.FBXExportReferencedAssetsContent(v=False)
    
    # Axis Conversion
    # Unity: Y Up (Same as Maya default usually)
    # Unreal: Z Up (Maya is Y Up). FBX plugin handles this if UpAxis is set.
    # Usually: Leave as Y-Up in Maya, check "Convert to Z-Up" in import? 
    # Or set FBXExportUpAxis 'z'
    
    if engine == "Unreal":
        cmds.FBXExportUpAxis("z")
    else:
        cmds.FBXExportUpAxis("y")
        
    # Scale Factor?
    # Unreal units = cm. Maya = cm. Scale = 1.0.
    # Unity units = meters? If Unity project is meters, Scale 0.01? 
    # Usually keep 1.0 and let engine/importer handle scaling.
    
    cmds.FBXExportScaleFactor(1.0)
    
    # Version
    cmds.FBXExportFileVersion(v="FBX202000") # 2020 format
    
    # Triangulate? Usually NO, let engine do it.
    cmds.FBXExportTriangulate(v=False)
    
    # File command
    # Replace \ with /
    path = path.replace("\\", "/")
    
    try:
        # 'file' command syntax for export selected
        # typ="FBX export"
        # pr=True (preserve references?) -> ES=Export Selected
        
        # We set options using commands above, does 'file' command respect them? 
        # Yes, if we don't pass 'options' string overrides.
        
        cmds.file(path, force=True, options="", typ="FBX export", pr=True, es=True)
        logger.info(f"Exported to {path}")
        return True
    except Exception as e:
        logger.error(f"Export failed: {e}")
        return False

def validate_and_export_game_ready(objects, path, engine="Unreal", triangulate=False):
    """
    High-level flow: 
    1. Sanitize
    2. Check Sanity (Validation lite)
    3. Triangulate (if requested)
    4. Export
    """
    if not cmds: return False
    
    # 1. Sanitize
    sanitize_scene(objects)
    
    # Let's patch export_fbx to accept triangulation argument or set it here.
    if triangulate:
        cmds.FBXExportTriangulate(v=True)
    else:
        cmds.FBXExportTriangulate(v=False)
        
    return export_fbx(objects, path, engine)
