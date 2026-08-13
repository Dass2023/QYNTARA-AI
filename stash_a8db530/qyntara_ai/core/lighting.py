import maya.cmds as cmds
import logging
import math

logger = logging.getLogger(__name__)

class LightingStudio:
    """
    Advanced Lighting Setup Engine (TD Level).
    Handles automated creation of studio environments and HDRI setups.
    """
    
    @staticmethod
    def create_studio_rig(intensity=1.0, scale=1.0):
        """
        Creates a classic 3-Point Light Setup (Key, Fill, Rim).
        Uses Arnold Area Lights if available, falls back to Maya Spot/Area.
        """
        renderer = cmds.getAttr("defaultRenderGlobals.currentRenderer")
        use_arnold = (renderer == "arnold")
        
        rig_group = cmds.group(em=True, name="Studio_Light_Rig")
        
        # 1. Key Light (The Main Source)
        key = LightingStudio._create_light(use_arnold, "Key_Light")
        cmds.setAttr(f"{key[0]}.t", 200 * scale, 200 * scale, 200 * scale)
        cmds.setAttr(f"{key[0]}.r", -45, 45, 0)
        LightingStudio._set_intensity(key[1], intensity * 1000, use_arnold) # Arnold uses higher values
        LightingStudio._set_color(key[1], (1.0, 0.95, 0.9)) # Warm
        
        # 2. Fill Light (The Softener)
        fill = LightingStudio._create_light(use_arnold, "Fill_Light")
        cmds.setAttr(f"{fill[0]}.t", -150 * scale, 100 * scale, 200 * scale)
        cmds.setAttr(f"{fill[0]}.r", -30, -45, 0)
        LightingStudio._set_intensity(fill[1], intensity * 300, use_arnold)
        LightingStudio._set_color(fill[1], (0.8, 0.85, 1.0)) # Cool
        
        # 3. Rim Light (The Separator)
        rim = LightingStudio._create_light(use_arnold, "Rim_Light")
        cmds.setAttr(f"{rim[0]}.t", 0, 200 * scale, -250 * scale)
        cmds.setAttr(f"{rim[0]}.r", -160, 0, 180)
        LightingStudio._set_intensity(rim[1], intensity * 800, use_arnold)
        LightingStudio._set_color(rim[1], (1.0, 1.0, 1.0))
        
        # Grouping
        cmds.parent([key[0], fill[0], rim[0]], rig_group)
        
        # Create Cyclorama (Infinity Background)
        cyc = cmds.polyPlane(w=1000*scale, h=1000*scale, sx=10, sy=10, name="Studio_Cyc")[0]
        # Bend the back
        cmds.select(f"{cyc}.vtx[99:109]", f"{cyc}.vtx[110:120]") # Approximate selection for back rows
        cmds.move(0, 500*scale, 0, r=True, os=True, wd=True)
        # Smooth
        cmds.polySmooth(cyc, dv=2)
        cmds.setAttr(f"{cyc}.t", 0, 0, -100*scale)
        cmds.parent(cyc, rig_group)
        
        return rig_group

    @staticmethod
    def setup_hdri(path):
        """
        Creates an HDRI Dome Light.
        """
        # Try Arnold SkyDome
        try:
            import mtoa.utils as mutils
            light = mutils.createLocator("aiSkyDomeLight", asLight=True)
            shape = cmds.listRelatives(light[0], shapes=True)[0]
            
            cmds.setAttr(f"{shape}.format", 2) # Lat-long
            
            # Connect File
            file_node = cmds.shadingNode('file', asTexture=True, isColorManaged=True)
            cmds.setAttr(f"{file_node}.fileTextureName", path, type="string")
            cmds.connectAttr(f"{file_node}.outColor", f"{shape}.color")
            
            return light[0]
        except ImportError:
            logger.warning("Arnold MtoA not found. Using standard generated dome.")
            # Fallback (Simple Sphere)
            dome = cmds.polySphere(r=1000, sx=30, sy=30, n="HDRI_Dome")[0]
            cmds.setAttr(f"{dome}.reverse", 1) # Flip Normals inside
            return dome

    @staticmethod
    def _create_light(use_arnold, name):
        """Helper to create agnostic lights."""
        if use_arnold:
            try:
                import mtoa.utils as mutils
                # MtoA usually returns [transform, shape] or just transform
                light = mutils.createLocator("aiAreaLight", asLight=True)
                cmds.rename(light[0], name)
                shape = cmds.listRelatives(name, shapes=True)[0]
                return [name, shape]
            except:
                pass
        
        # Fallback
        light = cmds.shadingNode('areaLight', asLight=True)
        transform = cmds.listRelatives(light, parent=True)[0]
        cmds.rename(transform, name)
        return [name, light]

    @staticmethod
    def _set_intensity(shape, val, use_arnold):
        if use_arnold:
            cmds.setAttr(f"{shape}.intensity", val / 100.0) # Arnold scales differently
            cmds.setAttr(f"{shape}.exposure", 10) # Base exposure
        else:
            cmds.setAttr(f"{shape}.intensity", val)

    @staticmethod
    def _set_color(shape, rgb):
        cmds.setAttr(f"{shape}.color", rgb[0], rgb[1], rgb[2], type="double3")

    @staticmethod
    def auto_focus(selection):
        """Snaps the active view to the selection ( Framing )."""
        if selection:
            cmds.select(selection)
            cmds.viewFit(animate=True)
