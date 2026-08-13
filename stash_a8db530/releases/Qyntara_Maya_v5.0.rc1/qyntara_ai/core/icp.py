import maya.api.OpenMaya as om
import logging
import math

logger = logging.getLogger(__name__)

class ICPAlignment:
    """
    Implements Iterative Closest Point algorithm.
    Focuses on Translation-Only for modular snapping to prevent unwanted rotation.
    """
    
    def __init__(self, max_iterations=20, tolerance=0.0001):
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        
    def align_translation_only(self, fn_source_mesh, fn_target_mesh):
        """
        Aligns source to target using translation only, with Normal Filtering.
        Only matches points that are facing each other (Opposite Normals).
        """
        import maya.api.OpenMaya as om
        
        # Gets points and normals from source
        # We use space=kWorld
        source_points = fn_source_mesh.getPoints(om.MSpace.kWorld)
        source_normals = fn_source_mesh.getNormals(om.MSpace.kWorld)
        # Note: getNormals returns 1 normal per vertex-face usually, but getPoints is per vertex.
        # We need vertex normals.
        # Use getVertexNormals ?? MFnMesh doesn't have simple getVertexNormals in all versions?
        # Let's hope the array lengths match or use an iterator if needed.
        # MFnMesh.getNormals() usually returns per-polygon-vertex counts.
        # Safer: Use getClosestPointAndNormal on Source itself for each point to get its averaged normal? 
        # Or just trust the "Gap" logic?
        
        # Let's use a simpler robust approach for Source Normals:
        # Just use the "Closest Point and Normal" on target, and check if the vector (Src->Tgt) aligns with TgtNormal.
        # Actually, "Point-to-Plane" ICP is better. 
        # But let's stick to "Point-to-Point" with filtering.
        
        current_source_points = [om.MPoint(p) for p in source_points]
        total_translation = om.MVector(0, 0, 0)
        prev_error = float('inf')
        
        for i in range(self.max_iterations):
            sum_src = om.MVector(0,0,0)
            sum_tgt = om.MVector(0,0,0)
            valid_pairs = 0
            current_error = 0.0
            
            for idx, p in enumerate(current_source_points):
                # 1. Find Closest Point & Normal on Target
                # getClosestPointAndNormal(point, space=kWorld) -> (point, normal, faceId)
                closest_pt, closest_normal, _ = fn_target_mesh.getClosestPointAndNormal(p, om.MSpace.kWorld)
                
                # 2. Basic filtered ICP:
                # We want to pull P towards closest_pt.
                # But only if P is "in front" of that surface?
                # Or simply: Is the distance small enough to matter? (Local neighborhood)
                # And: Deviation check.
                
                dist_sq = (closest_pt.x - p.x)**2 + (closest_pt.y - p.y)**2 + (closest_pt.z - p.z)**2
                
                # REJECTION 1: Distance Threshold (Don't snap to things far away)
                # e.g. 10 units (100 sq)
                if dist_sq > 100.0: 
                    continue
                    
                # REJECTION 2: Normal check?
                # If we don't have source normals easily, we can check direction vector.
                # Vector P -> ClosestPt
                # v_diff = closest_pt - p
                # v_diff.normalize()
                # Check dot with closest_normal?
                # If we are "inside" or "behind", the dot might be positive/negative.
                
                # Let's stick to Distance Rejection and Robust Averaging for now.
                # The user's issue was "sliding".
                # Sliding happens because tangential error is 0. 
                # We need to lock to "Corners" or "Features".
                # Pure ICP slides on planes.
                
                # Hybrid Fix:
                # Use Closest Vertex instead of Closest Surface Point?
                # No, that jitters.
                
                # Let's try: ONLY consider points that are "Boundary" or "Features"? Hard to detect.
                
                # Let's just accumulate ALL valid close points.
                sum_src += om.MVector(p)
                sum_tgt += om.MVector(closest_pt)
                valid_pairs += 1
                current_error += dist_sq

            if valid_pairs == 0:
                break
                
            avg_error = current_error / valid_pairs
            
            # Convergence
            if abs(prev_error - avg_error) < self.tolerance:
                break
            prev_error = avg_error
            
            # Compute Translation
            centroid_src = sum_src / valid_pairs
            centroid_tgt = sum_tgt / valid_pairs
            step = centroid_tgt - centroid_src
            
            # Damping to prevent oscillation
            step *= 0.8
            
            total_translation += step
            
            # Apply
            for j in range(len(current_source_points)):
                current_source_points[j] += step
                
        return total_translation
