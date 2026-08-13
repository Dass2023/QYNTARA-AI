import maya.cmds as cmds
import random
import json
import os
import shutil

class DatasetGenerator:
    def __init__(self, output_dir=None):
        if not output_dir:
            # Default to qyntara_ai/ai_assist/dataset
            base = os.path.dirname(os.path.abspath(__file__))
            output_dir = os.path.join(base, "dataset")
            
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
    def clear_scene(self):
        cmds.select(all=True)
        cmds.delete()
        
    def create_procedural_layout(self, num_objects=5):
        """
        Creates a simple "snapped" layout using cubes on a 10-unit grid.
        """
        objects = []
        GRID = 10.0
        
        for i in range(num_objects):
            # Create a block (Wall/Floor proxy)
            # Random dimensions snapped to grid-ish sizes
            w = random.choice([10, 20])
            h = random.choice([10, 20])
            d = random.choice([2, 10])
            
            obj = cmds.polyCube(w=w, h=h, d=d, name=f"Block_{i}")[0]
            
            # Snap position to grid
            tx = random.randint(-5, 5) * GRID
            ty = random.randint(0, 2) * GRID # Stack vertically?
            tz = random.randint(-5, 5) * GRID
            
            # Position so it sits ON the grid lines or floor (pivot is center)
            # Move pivot to bottom-center for easier logic? Or just offset.
            # PolyCube pivot is center.
            cmds.move(tx, ty + (h/2.0), tz, obj)
            objects.append(obj)
            
        return objects
    
    def apply_misalignment(self, objects, max_offset=5.0):
        """
        Jitters objects with 6-DOF (Rotation + Translation).
        Returns metadata about the error (inverse transform required).
        """
        meta = []
        misaligned_grp = cmds.group(empty=True, name="Misaligned_Grp")
        
        for obj in objects:
            # Duplicate for misaligned version
            dup = cmds.duplicate(obj, name=f"{obj}_bad")[0]
            cmds.parent(dup, misaligned_grp)
            
            # 1. Random Translation (Gap)
            dx = random.uniform(-max_offset, max_offset)
            dy = random.uniform(-max_offset, max_offset)
            dz = random.uniform(-max_offset, max_offset)
            
            # 2. Random Rotation (Orientation)
            rx = random.uniform(-180, 180)
            ry = random.uniform(-180, 180)
            rz = random.uniform(-180, 180)
            
            # Apply Transform
            # Rotate first (Object Space), then Move (World/Local)
            # This simulates an object being "tossed" into a bad position
            cmds.rotate(rx, ry, rz, dup, os=True, relative=True)
            cmds.move(dx, dy, dz, dup, relative=True)
            
            meta.append({
                "name": obj,
                "misaligned_name": dup,
                "translation_offset": [dx, dy, dz],
                "rotation_offset": [rx, ry, rz], # Euler degrees
                "error_type": "6dof_alignment"
            })
            
        return misaligned_grp, meta

    def generate_batch(self, batch_size=5, custom_objects=None):
        """
        Generates N scene pairs.
        If custom_objects provided, uses them as base instead of procedural blocks.
        """
        print(f"Generating {batch_size} scene pairs...")
        
        # If using custom objects, don't clear scene initially
        if not custom_objects:
             self.clear_scene()
        else:
             print("Using custom selection for training data...")
        
        for i in range(batch_size):
            scene_name = f"scene_{i:03d}"
            scene_dir = os.path.join(self.output_dir, scene_name)
            if os.path.exists(scene_dir):
                shutil.rmtree(scene_dir)
            os.makedirs(scene_dir)
            
            clean_grp = None
            
            # 1. Create Source Geometry
            if custom_objects:
                # Duplicate user objects to a temp clean group so we don't mess up originals
                clean_grp = cmds.group(empty=True, name="Temp_Clean_Grp")
                clones = []
                for obj in custom_objects:
                    d = cmds.duplicate(obj)[0]
                    cmds.parent(d, clean_grp)
                    clones.append(d)
                clean_objs = clones
                # Randomly rotate the clean group to simulate variety? 
                # Ideally yes, but let's keep it simple for now (Gap learning)
            else:
                self.clear_scene() # Ensure empty for procedural
                clean_objs = self.create_procedural_layout(num_objects=random.randint(3, 8))
            
            # Export Snapped (Clean)
            snapped_path = os.path.join(scene_dir, "snapped.obj")
            cmds.select(clean_objs)
            # Ensure objExport is loaded
            if not cmds.pluginInfo("objExport", q=True, loaded=True):
                cmds.loadPlugin("objExport")
            cmds.file(snapped_path, force=True, options="groups=1;ptgroups=1;materials=1;smoothing=1;normals=1", 
                      typ="OBJexport", pr=True, es=True)
            
            # 2. Create Misaligned (Dirty)
            # Apply offset to a COPY of the clean objs
            bad_grp, meta_data = self.apply_misalignment(clean_objs)
            misaligned_path = os.path.join(scene_dir, "misaligned.obj")
            
            # Export Misaligned
            cmds.select(bad_grp)
            cmds.file(misaligned_path, force=True, options="groups=1;ptgroups=1;materials=1;smoothing=1;normals=1", 
                      typ="OBJexport", pr=True, es=True)
            
            # 3. Save Meta
            meta_path = os.path.join(scene_dir, "meta.json")
            with open(meta_path, 'w') as f:
                json.dump({"scene_id": scene_name, "objects": meta_data}, f, indent=2)
            
            # Cleanup Temp Nodes for this iteration
            if clean_grp: cmds.delete(clean_grp) # Deletes clones
            if bad_grp: cmds.delete(bad_grp)
            if not custom_objects: self.clear_scene() # Clean procedural
                
            print(f"Generated {scene_name}")
            
        print(f"Dataset generation complete. Saved to {self.output_dir}")

# Usage for testing in Maya:
# from qyntara_ai.ai_assist.generate_dataset import DatasetGenerator
# gen = DatasetGenerator()
# gen.generate_batch(2)
