import maya.cmds as cmds
import random
import logging

logger = logging.getLogger("QyntaraTwin")

class DigitalTwinController:
    """
    The Nervous System of the Qyntara Smart Factory.
    Connects UI signals to Maya Scene Graph actions.
    """
    
    def __init__(self):
        self.active_links = {}
    
    def connect_live_stream(self, asset_id):
        """
        Visualizes a connection to an IoT Asset.
        """
        print(f"[Twin] Searching for asset: {asset_id}...")
        
        # 1. Find Object (Simplified search)
        # In a real scene we'd search attributes, here we assume naming convention or selection
        target = None
        selection = cmds.ls(sl=True)
        if selection:
            target = selection[0]
        elif cmds.objExists("Robot_Base"): # Fallback to our Smart Factory Arm
            target = "Robot_Base"
            
        if not target:
            logger.warning("No asset found to link!")
            return False
            
        # 2. Visual Feedback (The "Pulse")
        # Add an emission glow or change color
        self._highlight_asset(target, status="ONLINE")
        
        print(f"[Twin] LINK ESTABLISHED: {target} <--> {asset_id}")
        return True

    def disconnect_stream(self):
         # Reset visuals
         pass

    def _highlight_asset(self, node, status="ONLINE"):
        """
        Changes the visual state of an asset/machine.
        """
        # Find shader engine
        shapes = cmds.listRelatives(node, shapes=True) or []
        if not shapes: return
        
        # Simple Logic: Create a new "Status" shader
        shd_name = f"Mat_Status_{status}"
        
        if not cmds.objExists(shd_name):
            shd = cmds.shadingNode("blinn", asShader=True, n=shd_name)
            if status == "ONLINE":
                cmds.setAttr(f"{shd}.color", 0, 1, 0, type="double3") # Green
                cmds.setAttr(f"{shd}.incandescence", 0, 0.5, 0, type="double3")
            elif status == "BUSY":
                cmds.setAttr(f"{shd}.color", 1, 0.5, 0, type="double3") # Orange
            elif status == "ERROR":
                 cmds.setAttr(f"{shd}.color", 1, 0, 0, type="double3") # Red
        else:
            shd = shd_name
            
        # Assign
        cmds.select(node)
        cmds.hyperShade(assign=shd)
        cmds.select(clear=True)

    def trigger_machine_action(self, machine_name, action):
        """
        Drives the animation of the Digital Twin.
        """
        print(f"[Twin] Machine {machine_name} executing {action}...")
        
        if action == "PRINT":
            # Mock: Spin the object or move it
            if cmds.objExists(machine_name):
                self._highlight_asset(machine_name, "BUSY")
                # Add a rudimentary keyframe
                cmds.setKeyframe(machine_name, at="rotateY", v=0, t=cmds.currentTime(q=True))
                cmds.setKeyframe(machine_name, at="rotateY", v=360, t=cmds.currentTime(q=True)+50)

    def evolve_product_dna(self, traits):
        """
        Deforms the product based on DNA traits.
        traits: dict {'durability': 0-100, 'eco': 0-100}
        """
        target = "Product_Holo"
        if not cmds.objExists(target):
            # Try to find it or use selection
            sel = cmds.ls(sl=True)
            target = sel[0] if sel else None
            
        if not target:
            print("[Twin] No Product found to evolve.")
            return

        print(f"[Twin] Evolving {target} with traits: {traits}")
        
        # 1. Eco-Friendly = Thinner / Lighter
        eco_val = traits.get("Eco-Friendly", 50) / 100.0
        # High Eco -> Skinnier (less material)
        scale_factor = 1.0 - (eco_val * 0.4) 
        cmds.setAttr(f"{target}.scaleX", scale_factor)
        cmds.setAttr(f"{target}.scaleZ", scale_factor)
        
        # 2. Durability = Bullier / Bolder Color
        dur_val = traits.get("Durability", 50) / 100.0
        # High Durability -> Blue/Metallic
        # Use vertex color or shader change (Mocked here)
        
        # Visual Pop
        cmds.select(target)
        # Just a visual nudge
        cmds.move(0, 0.5, 0, target, r=True) 
        cmds.move(0, -0.5, 0, target, r=True)
        
        print("[Twin] Evolution Complete.")

# Singleton Instance for imported use
core = DigitalTwinController()
