import logging
import os

try:
    from maya import cmds
except ImportError:
    cmds = None

logger = logging.getLogger(__name__)

class BakingAutomation:
    """
    Automates the 'Transfer Maps' process for Scan-to-Asset workflows.
    Bakes Normal and Diffuse (Albedo) maps from a High-Res Scan to a Low-Res Target.
    """
    
    def __init__(self):
        self.output_dir = os.path.join(os.environ.get("USERPROFILE", ""), "Documents", "Qyntara_Bakes")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def bake_textures(self, high_poly, low_poly, map_types=["normal", "diffuse"], size=2048):
        """
        Executes the bake.
        high_poly: The raw scan (Source)
        low_poly: The retopologized mesh (Target)
        """
        if not cmds: 
            logger.warning("Maya cmds not available.")
            return []

        if not cmds.objExists(high_poly) or not cmds.objExists(low_poly):
            logger.error("Source or Target mesh not found.")
            return []
            
        # 1. Ensure Low Poly has UVs
        # For a raw auto-retopo, UVs might be missing. We need smart auto-UVs.
        self._ensure_uvs(low_poly)
        
        baked_files = []
        
        # 2. Setup Transfer Maps (surfaceSampler) args
        # This is complex in Maya commands. We simply wrapping the essential logic.
        
        # Output Name Format: Name_Type.ext
        base_name = low_poly.split("|")[-1].replace(":", "_")
        
        # Common Settings
        # searchMethod: 0=In, 1=Along Normal (Best for cages), 3=Closest to Envelope
        # We use heuristic max search distance.
        bbox = cmds.exactWorldBoundingBox(high_poly)
        diagonal = ((bbox[3]-bbox[0])**2 + (bbox[4]-bbox[1])**2 + (bbox[5]-bbox[2])**2)**0.5
        max_dist = diagonal * 0.05 # 5% of object size search envelope
        
        try:
            for map_type in map_types:
                output_path = os.path.join(self.output_dir, f"{base_name}_{map_type}.jpg")
                
                # Setup specific map flags
                # 'transferAttributes' or 'surfaceSampler'
                # surfaceSampler is preferred for maps.
                
                # Flag mapping for surfaceSampler
                # -mapOutput: type, format, filename
                # Types: normal, diffuse, displacement
                
                map_flag_type = "normal"
                if map_type == "diffuse": map_flag_type = "diffuseRGB"
                
                logger.info(f"Baking {map_type} to {output_path}...")
                
                # Note: surfaceSampler requires the Transfer Maps plugin usually, 
                # but 'transferAttributes' is for geometry. 
                # Ideally we use 'convertLightmap' or Arnold. 
                # But 'surfaceSampler' command is the backend for the Transfer Maps UI.
                
                # Arguments:
                # -target: low_poly
                # -source: high_poly
                # -mapOutput: type name filename
                # -mapWidth / -mapHeight
                # -maxSearchDistance
                
                cmds.surfaceSampler(
                    target=low_poly,
                    source=high_poly,
                    mapOutput=[map_flag_type, "jpg", output_path],
                    mapWidth=size,
                    mapHeight=size,
                    maxSearchDistance=max_dist,
                    mapSpace="tangent", # For normals
                    searchMethod=1 # Along Normal
                )
                
                baked_files.append(output_path)
                
        except Exception as e:
            logger.error(f"Baking failed: {e}")
            
        return baked_files

    def _ensure_uvs(self, obj):
        """ Checks if UVs exist, if not, runs Auto-Unwrap. """
        uv_count = cmds.polyEvaluate(obj, uv=True)
        if uv_count == 0:
            logger.info(f"No UVs on {obj}. Generating Auto-UVs...")
            # Auto-Unwrap 
            cmds.polyAutoProjection(obj, 
                                    layoutMethod=1, # Block Stacking
                                    optimize=1,
                                    percentageSpace=0.2) # Spacing

# Helper
def run_auto_bake(high, low):
    baker = BakingAutomation()
    return baker.bake_textures(high, low)
