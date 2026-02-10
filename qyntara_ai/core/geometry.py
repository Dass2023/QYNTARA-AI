import logging
import math

try:
    from maya import cmds
    import maya.api.OpenMaya as om
except ImportError:
    # ensuring script can be parsed even without maya
    cmds = None
    om = None

logger = logging.getLogger(__name__)

def _is_mesh(obj):
    """Helper to check if object is a valid mesh transform."""
    if not cmds: return False
    if cmds.objectType(obj) == 'transform':
         shapes = cmds.listRelatives(obj, shapes=True, type='mesh')
         return bool(shapes)
    return cmds.objectType(obj) == 'mesh'

def check_open_edges(objects):
    """
    Detects open edges (border edges) using TD-Approved constraint method.
    Prevents false positives on closed meshes (e.g. default Cube).
    """
    violations = []
    if not cmds:
        return violations

    # Ensure clean state before starting
    cmds.select(clear=True)
    cmds.polySelectConstraint(disable=True)

    for obj in objects:
        if not _is_mesh(obj): continue
        
        try:
            # 1. Get Final Visible Shape (No Intermediate 'Orig' shapes)
            shapes = cmds.listRelatives(obj, shapes=True, ni=True) or []
            if not shapes: continue
            shape = shapes[0] # Validate the primary shape

            # 2. Select Border Edges via Constraint
            cmds.select(clear=True)
            cmds.select(shape)
            
            cmds.polySelectConstraint(mode=3, type=0x8000, where=1) # Border Edges
            border_edges = cmds.ls(sl=True, flatten=True)
            
            # 3. Cleanup immediately
            cmds.polySelectConstraint(disable=True)
            cmds.select(clear=True)

            if border_edges:
                violations.append({
                    "object": obj,
                    "issue": "Open Edges",
                    "components": border_edges,
                    "count": len(border_edges)
                })
        except Exception as e:
            # Ensure cleanup on error
            cmds.polySelectConstraint(disable=True)
            # logger.warning(f"Open Edge check failed for {obj}: {e}")
            pass
            
    return violations

def check_non_manifold(objects):
    """
    Detects non-manifold geometry.
    """
    violations = []
    if not cmds:
        return violations

    for obj in objects:
        if not _is_mesh(obj): continue

        try:
            # polyInfo -nmv (non manifold vertices) or -nme (edges)
            nm_vtx = cmds.polyInfo(obj, nmv=True)
            nm_edges = cmds.polyInfo(obj, nme=True)
            
            found = []
            if nm_vtx: found.extend(nm_vtx)
            if nm_edges: found.extend(nm_edges)
            
            if found:
                 violations.append({
                    "object": obj,
                    "issue": "Non-Manifold Geometry",
                    "components": found,
                    "count": len(found)
                })
        except: pass
    return violations

def check_lamina_faces(objects):
    """
    Detects lamina faces (faces sharing all edges).
    """
    violations = []
    if not cmds:
        return violations

    for obj in objects:
        if not _is_mesh(obj): continue
        try:
            lamina = cmds.polyInfo(obj, lf=True)
            if lamina:
                 violations.append({
                    "object": obj,
                    "issue": "Lamina Faces",
                    "components": lamina,
                    "count": len(lamina)
                })
        except: pass
    return violations

def check_gaps(objects, tolerance=0.1):
    """
    Detects small gaps (distance < tolerance) between border edges of separate objects.
    Useful for ensuring modular kits snap together perfectly.
    """
    violations = []
    if not cmds or not om or len(objects) < 2: return violations
    
    # Filter only meshes
    meshes = [o for o in objects if _is_mesh(o)]
    if len(meshes) < 2: return violations
    
    import itertools
    
    # 1. Get Border Points for each object
    border_cloud = {} # obj -> [MPoint, MPoint...]
    
    for obj in meshes:
        try:
            sel = om.MSelectionList()
            sel.add(obj)
            dag_path = sel.getDagPath(0)
            
            it_edge = om.MItMeshEdge(dag_path)
            points = []
            
            while not it_edge.isDone():
                if it_edge.onBoundary():
                     # Get connected vertices positions
                     # 0 and 1 are indices of vertices
                     p0 = it_edge.point(0, om.MSpace.kWorld)
                     p1 = it_edge.point(1, om.MSpace.kWorld)
                     points.append(p0)
                     points.append(p1)
                it_edge.next()
            
            if points:
                border_cloud[obj] = points
        except: pass
        
    # 2. Check distances between clouds
    # This is O(N*M) so filtering by bounding box first is wise, but for now we do naive check
    # optimization: we create a spatial kd-tree or just simple pair check
    
    for o1, o2 in itertools.combinations(border_cloud.keys(), 2):
        cloud1 = border_cloud[o1]
        cloud2 = border_cloud[o2]
        
        found_gap = False
        min_dist_found = 9999.0
        
        # Super naive check: find ANY pair of border points that are close but not touching
        # "Touching" means dist < 0.001 (Micro)
        # "Gap" means 0.001 < dist < tolerance
        
        for p1 in cloud1:
            for p2 in cloud2:
                 d = p1.distanceTo(p2)
                 if 0.001 < d < tolerance:
                     found_gap = True
                     min_dist_found = min(min_dist_found, d)
                     # Optimization: Break early if one gap found? 
                     # Yes, we just flag the object pair.
                     break
            if found_gap: break
            
        if found_gap:
             violations.append({
                "object": f"{o1} <-> {o2}",
                "issue": f"Visible Gap {min_dist_found:.4f} (Border)",
                "components": [o1, o2],
                "action": "Snap/Weld",
                "count": 1
            })
            
    return violations

def _get_mesh_bounding_box(obj):
    # exactWorldBoundingBox gives (xmin, ymin, zmin, xmax, ymax, zmax)
    return cmds.exactWorldBoundingBox(obj)

def _nearly_equal(a, b, tolerance=0.01):
    return abs(a - b) < tolerance

def check_proximity_gaps(objects, tolerance=0.01):
    """
    Detects gaps between separate objects that are 'almost' touching.
    Also checks for Grid Alignment (Pivot on 10cm grid).
    """
    violations = []
    if not cmds: return violations
    
    # Filter for meshes only for proximity check
    meshes = [o for o in objects if _is_mesh(o)]
    if not meshes: return violations

    # 1. Grid Snapping Check (10cm grid)
    GRID_SIZE = 10.0
    for obj in meshes:
        try:
            p = cmds.xform(obj, q=True, ws=True, rp=True) # rotate pivot match
            # Check x, y, z
            if not p: continue
            
            # Simple check: distance to nearest grid point
            dx = round(p[0]/GRID_SIZE)*GRID_SIZE - p[0]
            dy = round(p[1]/GRID_SIZE)*GRID_SIZE - p[1]
            dz = round(p[2]/GRID_SIZE)*GRID_SIZE - p[2]
            dist = (dx**2 + dy**2 + dz**2)**0.5
            
            if dist > 0.001: 
                 violations.append({
                    "object": obj,
                    "issue": f"Off Grid ({dist:.2f} units)",
                    "action": "Snap to Grid",
                    "count": 1
                 })
        except: pass

    # 2. Border Gap Logic (Merged)
    # Check for micro-gaps between borders
    gap_violations = check_gaps(objects, tolerance=0.1)
    if gap_violations:
        violations.extend(gap_violations)
        
    return violations

def check_ngons(objects):
    """
    Detects N-gons (faces with more than 4 edges).
    """
    violations = []
    if not cmds:
        return violations

    for obj in objects:
        if not _is_mesh(obj): continue
        try:
            # DEBUG
            # print(f"DEBUG: Checking {obj} for N-gons...")
            
            # Force Face Selection Mode
            cmds.select(f"{obj}.f[:]")
            cmds.polySelectConstraint(mode=3, type=8, size=3) # size=3 includes n-gons
            ngons = cmds.ls(sl=True, flatten=True, long=True) or []
            cmds.polySelectConstraint(disable=True)
            
            # if ngons: print(f"DEBUG: Found {len(ngons)} N-gons")
            
            if ngons:
                 violations.append({
                    "object": obj,
                    "issue": "N-gons Detected",
                    "components": ngons,
                    "count": len(ngons)
                })
        except Exception as e:
            # logger.warning(f"Failed to check ngons for {obj}: {e}")
            if cmds:
                cmds.polySelectConstraint(disable=True)
                
    return violations

def check_zero_area_faces(objects, min_area=0.0001):
    """Detects faces with near-zero area using OpenMaya API."""
    violations = []
    if not om: return violations
    
    for obj in objects:
        if not _is_mesh(obj): continue
        try:
            # Get DAG Path
            sel = om.MSelectionList()
            sel.add(obj)
            dag_path = sel.getDagPath(0)
            
            it_poly = om.MItMeshPolygon(dag_path)
            bad_faces = []
            
            while not it_poly.isDone():
                area = it_poly.getArea()
                if area < min_area:
                    # Note: OpenMaya returns 0-based index. Maya cmds expects .f[i]
                    bad_faces.append(f"{obj}.f[{it_poly.index()}]")
                it_poly.next()
            
            if bad_faces:
                violations.append({
                    "object": obj,
                    "issue": "Zero Area Faces",
                    "components": bad_faces,
                    "action": "Cleanup / Merge",
                    "count": len(bad_faces)
                })
        except Exception as e:
            logger.error(f"Zero Area check failed for {obj}: {e}")
            pass
    return violations

def check_zero_length_edges(objects, min_length=0.0001):
    """Detects zero length edges using OpenMaya API."""
    violations = []
    if not om: return violations
    
    for obj in objects:
        if not _is_mesh(obj): continue
        try:
            sel = om.MSelectionList()
            sel.add(obj)
            dag_path = sel.getDagPath(0)
            
            it_edge = om.MItMeshEdge(dag_path)
            bad_edges = []
            
            while not it_edge.isDone():
                length = it_edge.length() 
                if length < min_length:
                    bad_edges.append(f"{obj}.e[{it_edge.index()}]")
                it_edge.next()
            
            if bad_edges:
                 violations.append({
                    "object": obj,
                    "issue": "Zero Length Edges",
                    "components": bad_edges,
                    "action": "Cleanup / Delete",
                    "count": len(bad_edges)
                 })
        except Exception as e:
            logger.error(f"Zero Length check failed for {obj}: {e}")
            pass
    return violations

def check_normals(objects):
    """
    Detects normal issues:
    1. Checks for Locked Normals (Custom normals) which might be unintentional.
    """
    violations = []
    if not cmds: return violations
    
    for obj in objects:
        if not _is_mesh(obj): continue
        try:
            # Replicating previous behavior for Locked Normals
            res = cmds.polyNormalPerVertex(f"{obj}.vtx[:]", q=True, freezeNormal=True)
            if res and any(res):
                 violations.append({
                    "object": obj,
                    "issue": "Locked Normals Detected",
                    "components": [], # Too many to list usually
                    "action": "Unlock Normals",
                    "count": sum(res)
                 })
        except: pass
    return violations

def check_inverted_normals(objects):
    """Checks for inverted normals (Opposite flag)."""
    violations = []
    if not cmds: return violations
    
    for obj in objects:
        if not _is_mesh(obj): continue
        try:
             # Check 'opposite' attribute on SHAPE
             shapes = cmds.listRelatives(obj, s=True, fullPath=True)
             if shapes:
                 opp = cmds.getAttr(f"{shapes[0]}.opposite")
                 if opp:
                     violations.append({
                        "object": obj,
                        "issue": "Inverted Normals (Opposite Flag)",
                        "components": [],
                        "action": "Conform / Reverse",
                        "count": 1
                     })
        except: pass
    return violations

def check_hard_edges(objects):
    """
    Detects if 100% of edges are hard (or soft). 
    Actually, usually checks for "All Hard" (Faceted).
    """
    violations = []
    if not cmds: return violations
    
    for obj in objects:
        if not _is_mesh(obj): continue
        try:
            # Select all edges
            cmds.select(obj)
            cmds.polySelectConstraint(mode=3, type=0x8000, smoothness=0) # Hard
            # Only count logic, component list not needed for logic check but nice to have
            hard_edges = cmds.ls(sl=True, flatten=True, long=True) or []
            
            cmds.polySelectConstraint(disable=True)
            
            edge_count = cmds.polyEvaluate(obj, edge=True)
            
            # If ALL edges are hard (Ratio ~ 1.0)
            if edge_count > 0 and len(hard_edges) == edge_count:
                violations.append({
                    "object": obj,
                    "issue": "Hard Edges (Faceted)",
                    "components": [], 
                    "action": "Soften Edges",
                    "count": len(hard_edges)
                 })
            else:
                 # Check ratio. If > 90% hard, it's faceted.
                 # If it has SOME hard edges (<90%), it's likely Custom Normals / Bevels / Weighted Normals.
                 # We should PASS these for Game Profiles.
                 if len(hard_edges) > (edge_count * 0.9):
                     violations.append({
                        "object": obj,
                        "issue": "Mostly Hard Edges (Faceted?)",
                        "components": hard_edges,
                        "action": "Soften Edges",
                        "count": len(hard_edges)
                     })
                 # Else: Mixed Soft/Hard is VALID for games.
        except: pass
    return violations



def check_triangulated(objects):
    """Checks if mesh is NOT fully triangulated (contains Quads or N-gons)."""
    violations = []
    if not cmds: return violations
    
    for obj in objects:
        if not _is_mesh(obj): continue
        
        try:
            # Force Face Selection
            cmds.select(f"{obj}.f[:]")
            
            # 1. Check Quads (Size=2)
            cmds.polySelectConstraint(mode=3, type=8, size=2)
            quads = cmds.ls(sl=True, flatten=True) or []
            cmds.polySelectConstraint(disable=True)
            
            # 2. Check N-gons (Size=3)
            # Need to re-select all faces first because constraint filtered them
            cmds.select(f"{obj}.f[:]")
            cmds.polySelectConstraint(mode=3, type=8, size=3)
            ngons = cmds.ls(sl=True, flatten=True) or []
            cmds.polySelectConstraint(disable=True)
            
            non_tris = quads + ngons
            
            if non_tris:
                violations.append({
                    "object": obj,
                    "issue": "Not Triangulated (Contains Quads/N-gons)",
                    "components": non_tris,
                    "action": "Triangulate",
                    "count": len(non_tris)
                })
        except: pass
            
    return violations

def check_coinciding_geometry(objects, tolerance=0.1):
    """Checks for hard intersections (clashes)."""
    violations = []
    if not cmds or len(objects) < 2: return violations

    import itertools
    # 1. Broad Phase: Bounding Box
    bbs = {}
    for obj in objects:
        bbs[obj] = cmds.xform(obj, q=True, bb=True, ws=True)
        
    overlapping_pairs = []
    for o1, o2 in itertools.combinations(objects, 2):
        b1 = bbs[o1]
        b2 = bbs[o2]
        if (b1[3] >= b2[0] and b1[0] <= b2[3] and  # x
            b1[4] >= b2[1] and b1[1] <= b2[4] and  # y
            b1[5] >= b2[2] and b1[2] <= b2[5]):    # z
            overlapping_pairs.append((o1, o2))
            
    if not overlapping_pairs: return violations
    
    for o1, o2 in overlapping_pairs:
        violations.append({
            "object": f"{o1} (intersects) {o2}",
            "issue": "Mesh Intersection / Clash",
            "components": [o1, o2],
            "action": "Move/Separate",
            "count": 1
        })

def check_floating_geometry(objects, min_volume_ratio=0.05):
    """Detects small, isolated objects (debris)."""
    violations = []
    if not cmds or not objects: return violations
    
    volumes = {}
    for obj in objects:
        bb = cmds.xform(obj, q=True, bb=True, ws=True)
        w = bb[3] - bb[0]
        h = bb[4] - bb[1]
        d = bb[5] - bb[2]
        vol = w * h * d
        if vol == 0: vol = 0.0001
        volumes[obj] = vol
        
    if not volumes:
        return violations

    avg_vol = sum(volumes.values()) / len(volumes)
    threshold = avg_vol * min_volume_ratio
    
    for obj, vol in volumes.items():
        if vol < threshold:
             # Logic change: Even parented objects can be debris if they are tiny mesh chunks
             # We just flag them.
             violations.append({
                "object": obj,
                "issue": "Floating / Small Geometry (Debris?)",
                "components": [],
                "action": "Inspect/Delete",
                "count": 1
            })
    return violations

def check_light_leaks(objects, tolerance=1.0):
    """Detects potential light leaks (Open borders not covered)."""
    violations = []
    if not cmds or not objects: return violations
    
    bbs = {}
    for obj in objects:
        bbs[obj] = cmds.xform(obj, q=True, bb=True, ws=True)
        
    for obj in objects:
        cmds.select(obj)
        cmds.polySelectConstraint(mode=3, type=0x8000, where=1) 
        borders = cmds.ls(sl=True, flatten=True)
        cmds.polySelectConstraint(disable=True)
        
        if not borders: continue
            
        leaking_edges = []
        other_objects = [o for o in objects if o != obj]
        if not other_objects:
            if borders:
                violations.append({
                    "object": obj,
                    "issue": "Open Borders / Light Leak Risk",
                    "components": borders,
                    "action": "Cap/Seal",
                    "count": len(borders)
                })
            continue

        for edge in borders:
            eb = cmds.xform(edge, q=True, bb=True, ws=True)
            is_covered = False
            for other in other_objects:
                ob = bbs[other]
                if (eb[3] >= ob[0]-tolerance and eb[0] <= ob[3]+tolerance and
                    eb[4] >= ob[1]-tolerance and eb[1] <= ob[4]+tolerance and
                    eb[5] >= ob[2]-tolerance and eb[2] <= ob[5]+tolerance):
                    is_covered = True
                    break
            
            if not is_covered:
                leaking_edges.append(edge)
                
        if leaking_edges:
            violations.append({
                "object": obj,
                "issue": "Unsealed Edges / Light Leak",
                "components": leaking_edges,
                "action": "Bridge/Cover",
                "count": len(leaking_edges)
            })



def check_lightmap_uvs(objects, lightmap_index=1):
    """Checks for secondary UV set (Lightmap)."""
    violations = []
    if not cmds or not objects: return violations
    
    for obj in objects:
        uv_sets = cmds.polyUVSet(obj, query=True, allUVSets=True)
        # Debug print
        print(f"DEBUG_UV2: {obj} sets: {uv_sets}")
        
        if not uv_sets:
            violations.append({
                "object": obj,
                "issue": "No UV Sets found",
                "components": [],
                "action": "Create UVs",
                "count": 1
            })
            continue
            
        if len(uv_sets) <= lightmap_index:
             violations.append({
                "object": obj,
                "issue": f"Missing Lightmap UV Set (Set {lightmap_index+1})",
                "components": [],
                "action": "Create UV Set",
                "count": 1
            })
        else:
            lightmap_set = uv_sets[lightmap_index]
            num_uvs = cmds.polyEvaluate(obj, uv=True, uvSetName=lightmap_set)
            if num_uvs == 0:
                violations.append({
                    "object": obj,
                    "issue": f"Lightmap UV Set '{lightmap_set}' is empty",
                    "components": [],
                    "action": "Unwrap/Copy",
                    "count": 1
                })
    return violations

def check_strict_quads(objects):
    """
    Strictly enforces Quads-Only topology (No Triangles, No N-gons).
    Common requirement for VFX / Subdivision pipelines.
    """
    violations = []
    if not cmds: return violations
    
    for obj in objects:
        if not _is_mesh(obj): continue
        
        try:
            # Check for Triangles
            cmds.select(obj)
            # topology=1 is Triangles
            cmds.polySelectConstraint(mode=3, type=0x0008, topology=1) 
            tris = cmds.ls(sl=True, flatten=True)
            cmds.polySelectConstraint(disable=True)
            
            if tris:
                 violations.append({
                    "object": obj,
                    "issue": f"Triangles Found ({len(tris)})",
                    "info": "Mesh is not strictly Quads.",
                    "action": "Quadrangulate"
                })
        except: pass
            
    return violations

def check_poles(objects, max_valency=5):
    """Detects E-Poles (>5 edges)."""
    violations = []
    if not om: return violations
    
    for obj in objects:
        if not _is_mesh(obj): continue
        try:
            sel = om.MSelectionList()
            sel.add(obj)
            dag_path = sel.getDagPath(0)
            
            it_vert = om.MItMeshVertex(dag_path)
            bad_verts = []
            
            while not it_vert.isDone():
                valency = len(it_vert.getConnectedEdges())
                if valency > max_valency:
                    bad_verts.append(f"{obj}.vtx[{it_vert.index()}]")
                it_vert.next()
                
            if bad_verts:
                violations.append({
                    "object": obj,
                    "issue": f"Complex Poles (>{max_valency} edges)",
                    "components": bad_verts,
                    "count": len(bad_verts)
                })
        except Exception as e:
            logger.error(f"Pole check failed for {obj}: {e}")
            
    return violations

def check_construction_history(objects):
    """Detects non-deformer construction history."""
    violations = []
    if not cmds: return violations
        
    for obj in objects:
        hist = cmds.listHistory(obj, pruneDagObjects=True) or []
        dangerous_nodes = []
        for node in hist:
            ntype = cmds.nodeType(node)
            if ntype.startswith("poly"):
                dangerous_nodes.append(node)
                
        if dangerous_nodes:
             violations.append({
                "object": obj,
                "issue": f"Unfrozen History ({len(dangerous_nodes)} nodes)",
                "action": "Delete History",
                "count": len(dangerous_nodes)
             })
    return violations

def check_shadow_terminator(objects):
    """Detects terminator risk (Smooth shading + >45deg angle)."""
    violations = []
    if not cmds or not objects: return violations
    
    for obj in objects:
        cmds.select(obj)
        cmds.polySelectConstraint(mode=3, type=0x8000, smoothness=2)
        soft_edges = cmds.ls(sl=True, flatten=True)
        cmds.polySelectConstraint(disable=True)
        
        if not soft_edges: continue
        
        cmds.select(soft_edges)
        cmds.polySelectConstraint(mode=3, type=0x8000, angle=True, anglebound=[45, 180])
        risky_edges = cmds.ls(sl=True, flatten=True)
        cmds.polySelectConstraint(disable=True)
        
        if risky_edges:
            violations.append({
                "object": obj,
                "issue": "Shadow Terminator Risk",
                "components": risky_edges,
                "action": "Harden Edge/Bevel",
                "count": len(risky_edges)
            })
    return violations

def check_polycount(objects, max=50000):
    """Checks polycount."""
    violations = []
    if not cmds: return violations
    
    for obj in objects:
        try:
            count = cmds.polyEvaluate(obj, face=True)
            if count > max:
                violations.append({
                    "object": obj,
                    "issue": f"High Polycount ({count} > {max})",
                    "components": [],
                    "action": "Reduce/Optimize",
                    "count": count
                })
        except: pass
    return violations

def check_vertex_colors(objects):
    """Checks if vertex colors are missing."""
    violations = []
    if not cmds: return violations
    
    for obj in objects:
        color_sets = cmds.polyColorSet(obj, query=True, allColorSets=True)
        if not color_sets:
            violations.append({
                "object": obj,
                "issue": "Missing Vertex Colors",
                "components": [],
                "action": "Apply Default Color",
                "count": 1
            })
    return violations

def check_concave_faces(objects):
    """
    Detects concave faces (faces with > 180 deg internal angle).
    These often triangulate badly in game engines.
    """
    violations = []
    if not cmds: return violations
    
    for obj in objects:
        if not _is_mesh(obj): continue
        try:
             # Maya 2023+ has polyRetopo check? No.
             # Use selection constraint 'concavity' if available?
             # polySelectConstraint -mode 3 -type 8 -convexity 1 (Concave)
             
             cmds.select(obj)
             # convexity=1 means Concave.
             cmds.polySelectConstraint(mode=3, type=8, convexity=1) 
             concave = cmds.ls(sl=True, flatten=True)
             cmds.polySelectConstraint(disable=True)
             
             if concave:
                 violations.append({
                    "object": obj,
                    "issue": "Concave Faces Detected",
                    "components": concave,
                    "action": "Triangulate/Split",
                    "count": len(concave)
                })
        except: pass
    return violations

def check_degenerate_uvs(objects, tolerance=0.000001):
    """
    Detects faces with degenerate (zero area) UVs.
    """
    violations = []
    if not om or not cmds: return violations

    for obj in objects:
        if not _is_mesh(obj): continue
        try:
            sel = om.MSelectionList()
            sel.add(obj)
            dag_path = sel.getDagPath(0)
            
            it_poly = om.MItMeshPolygon(dag_path)
            degenerate_faces = []
            
            while not it_poly.isDone():
                if it_poly.hasUVs():
                     # Check area
                     area = it_poly.getUVArea()
                     if area < tolerance:
                         degenerate_faces.append(f"{obj}.f[{it_poly.index()}]")
                it_poly.next()
                
            if degenerate_faces:
                violations.append({
                    "object": obj,
                    "issue": "Degenerate UVs (Zero Area)",
                    "components": degenerate_faces,
                    "action": "Fix UVs",
                    "count": len(degenerate_faces)
                })
        except: pass
    return violations

def check_internal_faces(objects):
    """
    Detects internal faces (faces inside the mesh volume).
    Uses Maya's visibility selection constraint.
    """
    violations = []
    if not cmds: return violations
    
    for obj in objects:
        if not _is_mesh(obj): continue
        
        try:
            cmds.select(obj)
            # Visibility=2 selects 'inside' faces (hidden by backface culling technically, but effectively internal)
            # Actually mode=3 (Components), type=0x0008 (Face), visibility=2 (Hidden)
            cmds.polySelectConstraint(mode=3, type=0x0008, visibility=2)
            internal = cmds.ls(sl=True, flatten=True)
            cmds.polySelectConstraint(disable=True)
            
            if internal:
                 violations.append({
                    "object": obj,
                    "issue": "Internal Faces Detected",
                    "components": internal,
                    "action": "Delete Internal",
                    "count": len(internal)
                })
        except: 
            if cmds: cmds.polySelectConstraint(disable=True)
            
    return violations

def check_watertight(objects):
    """Reuses Open Edges check for watertightness."""
    violations = []
    if not cmds: return violations
    
    raw_violations = check_open_edges(objects)
    for v in raw_violations:
        violations.append({
            "object": v["object"],
            "issue": "Not Watertight (Holes)",
            "components": v["components"],
            "action": "Cap/Bridge",
            "count": v["count"]
        })
    return violations

def check_missing_bevels(objects, angle_threshold=85.0):
    """
    Detects 'Razor Sharp' edges (Angle > threshold) that should likely be beveled 
    for realistic baking/rendering.
    Usually checks for Geometric Angle, regardless of Soft/Hard status, 
    though Hard Edges are the most common culprits.
    """
    violations = []
    if not cmds or not objects: return violations
    
    for obj in objects:
        if not _is_mesh(obj): continue
        try:
            # 1. Select All Edges
            cmds.select(obj)
            
            # 2. Filter by Geometric Angle (e.g. > 85 degrees)
            # This finds edges forming a sharp corner
            cmds.polySelectConstraint(mode=3, type=0x8000, angle=True, anglebound=[angle_threshold, 180])
            sharp_edges = cmds.ls(sl=True, flatten=True)
            cmds.polySelectConstraint(disable=True)
            
            if sharp_edges:
                violations.append({
                    "object": obj,
                    "issue": f"Missing Bevels (Sharp Edges > {angle_threshold}deg)",
                    "components": sharp_edges,
                    "action": "Bevel Edges",
                    "count": len(sharp_edges)
                })
        except Exception as e:
            # logger.warning(f"Bevel check failed for {obj}: {e}")
            pass
            
    return violations

    return violations



def check_scan_outliers(objects, threshold_multiplier=10.0):
    """
    Detects geometric outliers (spikes) common in LiDAR scans.
    Logic: Vertices where ALL connected edges are significantly longer 
    than the mesh's average edge length.
    """
    violations = []
    if not cmds: return violations

    for obj in objects:
        if not _is_mesh(obj): continue
        
        try:
            # 1. Get Average Edge Length (Estimate)
            # Sampling first 1000 edges for speed on dense scans
            edge_count = cmds.polyEvaluate(obj, edge=True)
            if edge_count == 0: continue
            
            # Use polyEvaluate or specific edge queries
            # For exactness we need to iterate. For speed, we might assume density is uniform.
            # Let's try a heuristic: Bounding Box Diagonal / Edge Count? No.
            # Let's use OpenMaya for fast iteration.
            
            if not om: continue
            
            sel = om.MSelectionList()
            sel.add(obj)
            dag_path = sel.getDagPath(0)
            mesh_fn = om.MFnMesh(dag_path)
            
            # Quick Average Calculation (iterating all edges is fast in C++ OpenMaya)
            # But in Python it might be slow for 1M+ points.
            # Strategy: Check Bounding Box? No.
            # Strategy: Just iterate. It's usually fine up to 50k-100k.
            # For LiDAR (1M+), we need to be careful.
            
            # Optimization: Skip if too huge?
            # if edge_count > 200000: ... logic ...
            
            # Let's assume moderate scans for now or accept the hit.
            
            total_len = 0.0
            sample_count = 0
            
            it_edge = om.MItMeshEdge(dag_path)
            
            # Sample every Nth edge to get average if huge
            step = 1
            if edge_count > 50000: step = 10
            if edge_count > 500000: step = 100
            
            current = 0
            while not it_edge.isDone():
                if current % step == 0:
                    total_len += it_edge.length()
                    sample_count += 1
                it_edge.next()
                current += 1
            
            if sample_count == 0: continue
            avg_len = total_len / sample_count
            threshold = avg_len * threshold_multiplier
            
            # 2. Find Spikes
            # Iterate Vertices. Check connected edges.
            it_vert = om.MItMeshVertex(dag_path)
            spikes = []
            
            while not it_vert.isDone():
                # A vertex is a spike if ALL connected edges are long
                # OR if it's just very far from neighbors.
                # Let's check average length of connected edges.
                
                connected_edges = it_vert.getConnectedEdges()
                long_edges = 0
                
                # We need lengths of these specific edges.
                # MItMeshVertex doesn't give edge lengths directly easily without jumping types
                # Use geometry approximation: distance to connected neighbors.
                
                p_center = it_vert.position(om.MSpace.kWorld)
                connected_indices = it_vert.getConnectedVertices()
                
                is_spike = True
                for neighbor_idx in connected_indices:
                     # Get neighbor pos
                     # We need a quick way.
                     # MFnMesh point access
                     p_neighbor = mesh_fn.getPoint(neighbor_idx, om.MSpace.kWorld)
                     dist = p_center.distanceTo(p_neighbor)
                     
                     if dist < threshold:
                         is_spike = False
                         break # Connected to at least one close neighbor -> Not an outlier spike
                
                if is_spike:
                    spikes.append(f"{obj}.vtx[{it_vert.index()}]")
                    
                it_vert.next()
            
            if spikes:
                violations.append({
                    "object": obj,
                    "issue": f"LiDAR Spikes / Outliers ({len(spikes)})",
                    "components": spikes,
                    "action": "Smooth / Delete",
                    "count": len(spikes)
                })
                
        except Exception as e:
            # logger.error(f"Scan outlier check failed: {e}")
            pass
            
    return violations

def check_degenerate_geometry(objects):
    """
    TD-Level Degenerate Geometry Check.
    Combines Zero Area Faces and Zero Length Edges.
    """
    violations = []
    
    # Run sub-checks
    area_violations = check_zero_area_faces(objects)
    length_violations = check_zero_length_edges(objects)
    
    if area_violations:
        violations.extend(area_violations)
    if length_violations:
        violations.extend(length_violations)
        
    return violations
