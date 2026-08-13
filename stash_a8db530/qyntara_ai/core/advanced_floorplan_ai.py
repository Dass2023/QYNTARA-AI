import logging
import math
from collections import defaultdict
from .floorplan_builder import Vector2

logger = logging.getLogger(__name__)

class FloorplanNode:
    def __init__(self, x, y, id):
        self.pos = Vector2(x,y)
        self.id = id
        self.neighbors = []

    def __repr__(self): return f"Node_{self.id}({self.pos})"

class FloorplanGraph:
    def __init__(self):
        self.nodes = []
        self.edges = [] 
        self._spatial_map = {} 
        self.node_counter = 0

    def get_or_create_node(self, pos, tolerance=10.0):
        best_node = None
        min_dist = tolerance
        for n in self.nodes:
            d = n.pos.dist(pos)
            if d < min_dist:
                min_dist = d
                best_node = n
        if best_node: return best_node
        new_node = FloorplanNode(pos.x, pos.y, self.node_counter)
        self.node_counter += 1
        self.nodes.append(new_node)
        return new_node

    def add_wall(self, p1, p2):
        n1 = self.get_or_create_node(p1)
        n2 = self.get_or_create_node(p2)
        if n2 not in n1.neighbors:
            self.edges.append((n1, n2))
            n1.neighbors.append(n2)
            n2.neighbors.append(n1)

class SemanticArchitect:
    def __init__(self, calibration_scale=1.0):
        self.graph = FloorplanGraph()
        self.scale = calibration_scale
        
    def analyze_scene(self, lines):
        logger.info(f"AI Analysis Started: Reading {len(lines)} wall segments...")
        self.graph = FloorplanGraph()
        for p1, p2 in lines:
            self.graph.add_wall(p1, p2)
        return self.graph

    def classify_rooms(self):
        adj = defaultdict(list)
        node_map = {n.id: n for n in self.graph.nodes}
        for n1, n2 in self.graph.edges:
            adj[n1.id].append(n2.id); adj[n2.id].append(n1.id)
            
        directed_edges = set()
        for u, v in self.graph.edges:
            directed_edges.add((u.id, v.id)); directed_edges.add((v.id, u.id))
            
        found_faces = [] 
        processed_edges = set()
        
        for u_id, v_id in directed_edges:
            if (u_id, v_id) in processed_edges: continue
            path = [u_id]; curr = v_id; start = u_id; steps = 0
            while curr != start and steps < 50:
                path.append(curr)
                if len(path) < 2: break
                prev = path[-2]
                neighbors = adj[curr]
                if len(neighbors) < 2: path = []; break
                
                p_prev = node_map[prev].pos
                p_curr = node_map[curr].pos
                vec_in = p_curr - p_prev
                angle_in = math.atan2(vec_in.y, vec_in.x)
                
                best_next = None
                min_angle_diff = 2 * math.pi + 1.0 
                for n_next in neighbors:
                    if n_next == prev: continue
                    p_next = node_map[n_next].pos
                    vec_out = p_next - p_curr
                    angle_out = math.atan2(vec_out.y, vec_out.x)
                    diff = (angle_out - angle_in) % (2 * math.pi)
                    if diff < min_angle_diff: min_angle_diff = diff; best_next = n_next
                if best_next is None: path = []; break
                curr = best_next; steps += 1
            
            if curr == start and len(path) > 2:
                path.append(start); found_faces.append(path)
                for i in range(len(path)-1): processed_edges.add((path[i], path[i+1]))
                    
        room_data = []
        for face_nodes_ids in found_faces:
            nodes = [node_map[nid] for nid in face_nodes_ids]
            area = 0.0
            for i in range(len(nodes)-1):
                area += nodes[i].pos.x * nodes[i+1].pos.y
                area -= nodes[i+1].pos.x * nodes[i].pos.y
            area = abs(area) * 0.5
            if area > 2000:
                center = self._calc_centroid(nodes)
                room_data.append({"type": "Room", "area": area, "nodes": nodes, "center": center})
        return room_data

    def build_rooms_in_maya(self, rooms, floor_thickness=20.0, wall_height=300.0, create_ceiling=True, create_labels=True, image_path=None, openings=None, assets=None):
        from maya import cmds
        created = []
        
        # HIERARCHY FIX
        main_grp = "Formatted_FloorPlan_Grp"
        if not cmds.objExists(main_grp):
            main_grp_node = cmds.group(em=True, name=main_grp)
        else:
            main_grp_node = main_grp

        grp_name = "AI_Generated_Rooms_Grp"
        if not cmds.objExists(grp_name): 
            grp = cmds.group(em=True, name=grp_name)
            try: cmds.parent(grp, main_grp_node)
            except: pass
        else: 
            grp = grp_name
            try:
                parents = cmds.listRelatives(grp, parent=True)
                if not parents or parents[0] != main_grp_node:
                    cmds.parent(grp, main_grp_node)
            except: pass
            
        mat_node, shading_grp = None, None
        if image_path:
            # Re-use or create projection material
            mat_name = "Blueprint_Projection_Mat"
            if cmds.objExists(mat_name):
                mat_node = mat_name
                sgs = cmds.listConnections(mat_node, type="shadingEngine")
                if sgs: shading_grp = sgs[0]
            else:
                mat_node = cmds.shadingNode("lambert", asShader=True, name=mat_name)
                shading_grp = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=mat_name+"SG")
                cmds.connectAttr(f"{mat_node}.outColor", f"{shading_grp}.surfaceShader")
                file_node = cmds.shadingNode("file", asTexture=True)
                cmds.setAttr(f"{file_node}.fileTextureName", image_path, type="string")
                cmds.connectAttr(f"{file_node}.outColor", f"{mat_node}.color")
                
        # 0. Build Openings (Doors)
        if openings:
            door_grp_name = "AI_Generated_Doors_Grp"
            if cmds.objExists(door_grp_name): cmds.delete(door_grp_name)
            
            door_grp = cmds.group(em=True, name=door_grp_name)
            cmds.parent(door_grp, grp)
            created.append(door_grp)
            for i, op in enumerate(openings):
                pos = op['pos']
                width = op['width'] * self.scale
                rot_y = 90 if op.get('vertical', False) else 0
                door = cmds.polyCube(w=width, h=210.0, d=15.0, name=f"Door_Proxy_{i}")[0]
                cmds.xform(door, t=(pos.x * self.scale, 105.0, -pos.y * self.scale), ro=(0, rot_y, 0))
                cmds.parent(door, door_grp)
                
        # 0.5. Build Recognized Assets (NEW!) (Geometric AI)
        if assets:
            asset_grp_name = "AI_Recognized_Furniture_Grp"
            if cmds.objExists(asset_grp_name): cmds.delete(asset_grp_name)
            
            asset_grp = cmds.group(em=True, name=asset_grp_name)
            cmds.parent(asset_grp, grp)
            created.append(asset_grp)
            
            for i, asset in enumerate(assets):
                atype = asset['type']
                w = asset['width'] * self.scale
                # In 2D, width/height is X/Z.
                # In 3D, depth is Z. Height is Y.
                d_ws = asset['height'] * self.scale 
                
                px = asset['pos'].x * self.scale
                pz = -asset['pos'].y * self.scale
                
                name = f"Detected_{atype}_{i}"
                if atype == "Table":
                    # Simple Table (Cylinder top)
                    obj = cmds.polyCylinder(r=min(w,d_ws)/2.0, h=75.0, name=name)[0]
                    cmds.xform(obj, t=(px, 37.5, pz))
                elif atype == "Bed":
                    # Bed (Low Cube)
                    obj = cmds.polyCube(w=w, h=50.0, d=d_ws, name=name)[0]
                    cmds.xform(obj, t=(px, 25.0, pz))
                else:
                    # Misc Box (Unknown but detected)
                    obj = cmds.polyCube(w=w, h=30.0, d=d_ws, name=name)[0]
                    cmds.xform(obj, t=(px, 15.0, pz))
                    
                cmds.parent(obj, asset_grp)
                logger.info(f"AI Detected {atype} at {px}, {pz}")
                
        # 1. Build Rooms
        classifier = RoomClassifier()
        for i, room in enumerate(rooms):
            nodes = room["nodes"]
            points = [(n.pos.x * self.scale, 0.0, -n.pos.y * self.scale) for n in nodes]
            points.append(points[0]) 
            curve = cmds.curve(d=1, p=points, name=f"RoomCurve_{i}")
            
            area_px = room["area"]
            area_cm2 = area_px * (self.scale ** 2)
            area_sqft = area_cm2 * 0.00107639
            
            room_type = classifier.classify(room["area"], len(nodes))
            label_text = f"{room_type}\n{area_sqft:.1f} sq ft"
            
            try:
                surf = cmds.planarSrf(curve, polygon=0)[0]
                tess = cmds.nurbsToPoly(surf, format=1, polygonType=1, f=0)[0]
                cmds.polyExtrudeFacet(tess, localTranslateZ=-floor_thickness, keepFacesTogether=True)
                floor_mesh = cmds.rename(tess, f"Room_{i+1}_Floor_{room_type}")
                cmds.parent(floor_mesh, grp)
                created.append(floor_mesh)
                if shading_grp:
                    cmds.sets(floor_mesh, edit=True, forceElement=shading_grp)
                    cmds.polyProjection(floor_mesh + ".f[:]", type="Planar", md="y")

                if create_ceiling:
                    ceil = cmds.duplicate(floor_mesh, name=f"Room_{i+1}_Ceiling")[0]
                    cmds.xform(ceil, r=True, t=(0, wall_height, 0))
                    cmds.sets(ceil, edit=True, forceElement="initialShadingGroup")
                    cmds.parent(ceil, grp); created.append(ceil)

                if create_labels:
                    cx, cz = room["center"].x * self.scale, -room["center"].y * self.scale
                    txt = cmds.textCurves(t=label_text, font="Arial", ch=False)[0]
                    cmds.xform(txt, cp=True)
                    cmds.xform(txt, t=(cx, wall_height/2.0, cz), s=(1.5,1.5,1.5), ro=(90,0,0))
                    cmds.rename(txt, f"Room_{i+1}_Label")
                    cmds.parent(txt, grp); created.append(txt)
                    
                # NOTE: We now rely on Real Asset Detection for furniture
                # But we can keep contextual placement as a fallback if needed.
                # Removing hardcoded "Desk" placement to let the AI Detector shine.
                
                cmds.delete(curve, surf)
            except Exception as e:
                logger.warning(f"Failed room {i}: {e}")
                if cmds.objExists(curve): cmds.delete(curve)
        return created

    def _calc_centroid(self, nodes):
        if not nodes: return Vector2(0,0)
        sx = sum(n.pos.x for n in nodes); sy = sum(n.pos.y for n in nodes)
        count = len(nodes)
        return Vector2(sx/count, sy/count)

class RoomClassifier:
    """Symbolic AI for inferring Room Type."""
    def classify(self, area, num_corners):
        # Heuristics
        if area < 30000: return "Store"
        elif area < 100000: return "Office"
        elif area < 300000: return "Meet"
        elif area < 800000:
             if num_corners > 6: return "L-Hall"
             return "Conf"
        else: return "Open"
