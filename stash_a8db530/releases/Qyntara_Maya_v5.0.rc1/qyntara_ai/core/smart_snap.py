import maya.api.OpenMaya as om
import maya.cmds as cmds
import math
import logging

logger = logging.getLogger(__name__)

class SmartGapSnapper:
    """
    Simulates 'AI' perception to find and close significant gaps between objects.
    Uses 'Directional Probing' to ignore incidental contact (like floor) 
    and focus on the structural gap (like wall-to-doorframe).
    """

    def __init__(self, src_dag, tgt_dag):
        self.src_dag = src_dag
        self.tgt_dag = tgt_dag
        self.fn_src = om.MFnMesh(src_dag)
        self.fn_tgt = om.MFnMesh(tgt_dag)

    def snap(self):
        """
        Uses Raycasting from Source Faces to find the actual gap distance.
        This handles complex shapes (L-shapes) where BBox centers are misleading.
        """
        # 1. Setup Intersection Params
        accel_params = self.fn_tgt.autoUniformGridParams()
        
        # 2. Iterate Source Faces
        iter_poly = om.MItMeshPolygon(self.src_dag)
        
        candidates = []
        
        while not iter_poly.isDone():
            # Get Center & Normal
            center = iter_poly.center(om.MSpace.kWorld)
            normal = om.MVector()
            # getNormal depends on API version somewhat, usually getNormal(space)
            # API 2.0: getNormal(space) -> MVector
            try:
                normal = iter_poly.getNormal(om.MSpace.kWorld)
            except:
                iter_poly.next()
                continue
                
            # 3. Raycast towards Normal (Front)
            # We want to see if this face is "looking at" the target.
            # closestIntersection(raySource, rayDirection, space, maxParam, testBothDirections) -> ...
            
            # Signature:
            # float or (hitPoint, hitRayParam, hitFace, hitTriangle, hitBary1, hitBary2)
            # We need hitRayParam (Distance)
            
            hit_point = om.MPoint()
            # maxParam = 100.0 (Search limit)
            MAX_DIST = 500.0
            
            hit = self.fn_tgt.closestIntersection(
                om.MFloatPoint(center),
                om.MFloatVector(normal),
                om.MSpace.kWorld,
                MAX_DIST,
                False # testBothDirections
            )
            
            # Hit result is usually (hitPoint, hitRayParam, hitFace, hitTriangle, hitBary1, hitBary2) OR None
            # In some python bindings it returns None if no hit, or a tuple.
            
            if hit:
                hit_param = hit[1] # Distance
                
                # Filter: Small gaps only? 
                # If distance is > 0.001 (not touching)
                if 0.001 < hit_param < MAX_DIST:
                    candidates.append((hit_param, normal))
            
            iter_poly.next()
            
        if not candidates:
            # Try Backfaces? (Raycast -Normal)
            # Sometimes geometry is flipped or we are "inside".
            # For now, if no hits, return None.
            return None
            
        # 4. Find "Consensus" Gap
        # We might have many hits. We want the "Main" gap.
        # We group by Normal Direction (approx) and Distance.
        
        # Simple logic: Find simplest grouping.
        # Most faces pointing in X will have similar dist.
        
        best_vec = om.MVector(0,0,0)
        max_votes = 0
        
        # Quantize normals and distances
        bins = {}
        
        for dist, norm in candidates:
            # Key: Normal(rounded)
            nx = round(norm.x, 1)
            ny = round(norm.y, 1) # Ignore Y (floors)? 
            nz = round(norm.z, 1)
            
            # Ignore Up/Down rays (Floor/Ceiling)?
            # User usually snaps walls/doors (Horizontal).
            if abs(ny) > 0.9: continue 
            
            key = (nx, ny, nz)
            
            if key not in bins:
                bins[key] = []
            bins[key].append(dist)
            
        # Find bin with most hits
        best_key = None
        for k, dists in bins.items():
            if len(dists) > max_votes:
                max_votes = len(dists)
                best_key = k
                
        if best_key:
            # Average distance in this bin
            common_dists = bins[best_key]
            avg_dist = sum(common_dists) / len(common_dists)
            
            # Reconstruct Vector
            direction = om.MVector(best_key[0], best_key[1], best_key[2])
            direction.normalize()
            
            best_vec = direction * avg_dist
            
            logger.info(f"AI Raycast detected gap: {avg_dist:.4f} units along {direction}")
            return best_vec
            
        return None
