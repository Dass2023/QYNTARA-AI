"""
Qyntara AI Blueprint Processor
==============================
Converts 2D Floor Plan images into 3D extruded meshes.
Uses OpenCV for wall detection and Trimesh for extrusion.
"""

import cv2
import numpy as np
import trimesh
import uuid
import os
from shapely.geometry import Polygon
from shapely.ops import unary_union

class BlueprintProcessor:
    def __init__(self, output_dir="backend/data/blueprints"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def process_floorplan(self, image_path: str, wall_height: float = 2.5, px_per_meter: float = 50.0, threshold: int = 127):
        """
        Detects walls in a floor plan image and extrudes them into a 3D mesh.
        Returns: (mesh_path, dxf_path)
        """
        # 1. Load Image
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError(f"Could not load image: {image_path}")

        # 2. Preprocessing (Thresholding)
        _, binary = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY_INV)

        # 3. Detect Contours (Walls)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 4. Create Polygons
        polygons = []
        for cnt in contours:
            if cv2.contourArea(cnt) < 100:  # Noise filter
                continue
            
            # Approximate contour to reduce vertices
            epsilon = 0.005 * cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, epsilon, True)
            
            if len(approx) >= 3:
                # Convert to Shapely Polygon
                points = approx.reshape(-1, 2)
                # Flip Y for 3D coordinate system (Image Y is down, 3D Z is up)
                points[:, 1] = -points[:, 1]
                
                # Scale pixels to meters
                points = points / px_per_meter
                
                try:
                    poly = Polygon(points)
                    if poly.is_valid:
                        polygons.append(poly)
                    else:
                        polygons.append(poly.buffer(0)) # Attempt fix
                except:
                    pass

        if not polygons:
            raise ValueError("No valid walls detected.")

        # 5. Extrude Walls
        scene = trimesh.Scene()
        
        for poly in polygons:
            try:
                # Create 2D Path
                path = trimesh.load_path(poly)
                # Extrude
                mesh = path.extrude(wall_height)
                scene.add_geometry(mesh)
            except Exception as e:
                print(f"Failed to extrude polygon: {e}")

        # 6. Export Results
        job_id = str(uuid.uuid4())[:8]
        mesh_filename = f"floorplan_{job_id}.obj"
        dxf_filename = f"floorplan_{job_id}.dxf"
        
        mesh_path = os.path.join(self.output_dir, mesh_filename)
        dxf_path = os.path.join(self.output_dir, dxf_filename)
        
        # Merge all geometries into one mesh for OBJ export
        full_mesh = trimesh.util.concatenate(list(scene.geometry.values()))
        full_mesh.export(mesh_path)
        
        # Export DXF (2D footprint)
        full_mesh.section(plane_origin=[0,0,wall_height/2], plane_normal=[0,0,1]).export(dxf_path)

        return f"backend/data/blueprints/{mesh_filename}", f"backend/data/blueprints/{dxf_filename}"
