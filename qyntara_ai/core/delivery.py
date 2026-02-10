import logging
import os
import shutil
import time

logger = logging.getLogger(__name__)

class DeliveryManager:
    """
    Handles the final packaging of the converted scan data.
    """
    
    def __init__(self):
        self.output_root = os.path.join(os.environ.get("USERPROFILE", ""), "Documents", "Qyntara_Exports")
        if not os.path.exists(self.output_root):
            os.makedirs(self.output_root)

    def export_clean_scene(self, objects, name="Converted_Scan"):
        """
        Exports the selected objects to a clean folder structure.
        Returns the path to the exported folder.
        """
        timestamp = int(time.time())
        job_dir = os.path.join(self.output_root, f"{name}_{timestamp}")
        os.makedirs(job_dir)
        
        from maya import cmds
        
        # 1. FBX Export
        fbx_path = os.path.join(job_dir, f"{name}.fbx")
        try:
            cmds.select(objects)
            # Ensure plugin loaded
            if not cmds.pluginInfo("fbxmaya", q=True, loaded=True):
                try: cmds.loadPlugin("fbxmaya")
                except: pass
                
            # Basic FBX export command
            # Using FBXExport command is safer than file -type "FBX export" sometimes, but let's stick to file
            cmds.file(fbx_path, force=True, options="v=0;", typ="FBX export", pr=True, es=True)
            logger.info(f"Exported FBX: {fbx_path}")
        except Exception as e:
            logger.error(f"FBX Export failed: {e}")

        # 2. USD Export (if available)
        usd_path = os.path.join(job_dir, f"{name}.usd")
        if cmds.pluginInfo("mayaUsdPlugin", q=True, loaded=True):
            try:
                cmds.select(objects)
                cmds.file(usd_path, force=True, options="", typ="USD Export", pr=True, es=True)
                logger.info(f"Exported USD: {usd_path}")
            except Exception as e:
                logger.warning(f"USD Export failed: {e}")

        # 3. Report
        report_path = os.path.join(job_dir, "manifest.txt")
        with open(report_path, "w") as f:
            f.write(f"Qyntara AI - Scan Conversion Report\n")
            f.write(f"-----------------------------------\n")
            f.write(f"Date: {time.ctime()}\n")
            f.write(f"Object Count: {len(objects)}\n")
            f.write(f"Objects: {', '.join(objects)}\n")
            
        return job_dir
