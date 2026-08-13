import logging
import math
from collections import defaultdict

try:
    from PySide2.QtGui import QImage, QColor
except ImportError:
    try:
        from PySide6.QtGui import QImage, QColor
    except ImportError:
        QImage = None

logger = logging.getLogger(__name__)

class FloorplanConfig:
    """TD CONFIGURATION"""
    def __init__(self):
        self.threshold = 0.5
        self.min_segment_length = 20.0
        self.snap_grid_size = 2.0 # ALIGNMENT FIX
        self.weld_radius = 60.0 
        self.island_ratio = 0.10
        self.wall_height = 320.0 # NEW SPEC: 3.2m
        self.wall_thickness = 15.0 # NEW SPEC: 0.15m

class Vector2:
    def __init__(self, x, y): self.x = x; self.y = y
    def __repr__(self): return f"({self.x:.2f}, {self.y:.2f})"
    def __add__(self, o): return Vector2(self.x + o.x, self.y + o.y)
    def __sub__(self, o): return Vector2(self.x - o.x, self.y - o.y)
    def dist(self, o): return math.sqrt((self.x - o.x)**2 + (self.y - o.y)**2)
    def length(self): return math.sqrt(self.x**2 + self.y**2)

class FloorPlanArchitect:
    def __init__(self):
        self.config = FloorplanConfig()
        self.vectorizer = SmartVectorization(self.config)
        self.calibration_scale = 1.0 
        self.last_clean_lines = []
        self.last_openings = [] 
        self.last_assets = [] 

    def set_scale_from_pixels(self, pixel_dist, real_dist_cm):
        if pixel_dist > 0:
            self.calibration_scale = real_dist_cm / pixel_dist
            logger.info(f"Calibration Set: 1 Pixel = {self.calibration_scale:.4f} cm")

    def build_from_image(self, image_path, threshold=None, wall_height=None, wall_thickness=None):
        if threshold is not None: self.config.threshold = threshold
        if wall_height is not None: self.config.wall_height = wall_height
        if wall_thickness is not None: self.config.wall_thickness = wall_thickness
        
        logger.info(f"Processing Image: {image_path}")
        
        # 1. Vectorize
        raw_lines = self.vectorizer.process_image(image_path) 
        if not raw_lines: return [], f"No walls detected."

        # 2. Bridge Gaps
        bridged_lines = self.vectorizer.bridge_gaps(raw_lines)

        # 3. Openings & Regularize
        self.last_openings = self.vectorizer.detect_openings(bridged_lines)
        regularized = self.vectorizer.regularize_lines(bridged_lines)
        
        # 4. Symbol Recognition
        walls, assets = self.vectorizer.detect_symbols(regularized)
        
        self.last_clean_lines = walls
        self.last_assets = assets 
        
        # 5. Build Walls
        return self._construct_maya_geo(walls, image_path)

    def _construct_maya_geo(self, lines, image_path=None):
        from maya import cmds
        created = []
        grp = "Formatted_FloorPlan_Grp"
        if not cmds.objExists(grp): grp = cmds.group(em=True, name=grp)
        created.append(grp)
        
        # REFERENCE PLANE
        if image_path:
            img = QImage(image_path)
            if not img.isNull():
                w_px, h_px = img.width(), img.height()
                w_cm = w_px * self.calibration_scale
                h_cm = h_px * self.calibration_scale
                
                plane = cmds.polyPlane(w=w_cm, h=h_cm, sx=1, sy=1, ax=(0,1,0), name="Reference_Blueprint_Plane")[0]
                cmds.xform(plane, t=(w_cm/2.0, -25.0, -h_cm/2.0))
                
                mat_name = "Blueprint_Ref_Mat"
                if cmds.objExists(mat_name):
                    mat = mat_name
                    sgs = cmds.listConnections(mat, type="shadingEngine")
                    sg = sgs[0] if sgs else None
                else:
                    mat = cmds.shadingNode("lambert", asShader=True, name=mat_name)
                    sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=mat_name+"SG")
                    cmds.connectAttr(f"{mat}.outColor", f"{sg}.surfaceShader")
                    file_node = cmds.shadingNode("file", asTexture=True)
                    cmds.setAttr(f"{file_node}.fileTextureName", image_path, type="string")
                    cmds.connectAttr(f"{file_node}.outColor", f"{mat}.color")
                    
                if sg:
                     cmds.sets(plane, edit=True, forceElement=sg)
                
                plane = cmds.parent(plane, grp)[0]
                created.append(plane)
        
        line_grp = cmds.group(em=True, name="Walls_Grp", parent=grp)
        h = self.config.wall_height; d = self.config.wall_thickness
        
        wall_nodes = []
        
        for p1, p2 in lines:
            ws_p1 = Vector2(p1.x * self.calibration_scale, p1.y * self.calibration_scale)
            ws_p2 = Vector2(p2.x * self.calibration_scale, p2.y * self.calibration_scale)
            vec = ws_p2 - ws_p1; l = vec.length()
            if l < 5.0: continue 
            mid = Vector2((ws_p1.x + ws_p2.x)*0.5, (ws_p1.y + ws_p2.y)*0.5)
            angle = math.degrees(math.atan2(vec.y, vec.x))
            w = cmds.polyCube(w=l, h=h, d=d, name="Wall_Gen_#")[0]
            cmds.xform(w, t=(mid.x, h/2.0, -mid.y), ro=(0, -angle, 0))
            wall_nodes.append(w)
            
        if wall_nodes:
            cmds.parent(wall_nodes, line_grp)
            if len(wall_nodes) > 1:
                united = cmds.polyUnite(wall_nodes, ch=False, mergeUVSets=1, name="Walls_Main_Geo")[0]
                cmds.delete(united, ch=True)
                try:
                    united = cmds.parent(united, line_grp)[0]
                except: pass
                created.append(united)
            else:
                 created.extend(wall_nodes)
            
        return created, f"Generated Reference Plane & Walls."

class SmartVectorization:
    def __init__(self, config): self.cfg = config

    def process_image(self, path):
        if not QImage: return []
        img = QImage(path); w, h = img.width(), img.height()
        thresh = int(self.cfg.threshold * 255); segments = []
        step = 6; min_l = self.cfg.min_segment_length
        for y in range(0, h, step):
            sx = -1
            for x in range(0, w, 2):
                wall = QColor(img.pixel(x,y)).value() < thresh
                if wall and sx == -1: sx = x
                elif not wall and sx != -1:
                    if (x - sx) > min_l: segments.append((Vector2(sx, y), Vector2(x, y)))
                    sx = -1
        for x in range(0, w, step):
            sy = -1
            for y in range(0, h, 2):
                wall = QColor(img.pixel(x,y)).value() < thresh
                if wall and sy == -1: sy = y
                elif not wall and sy != -1:
                    if (y - sy) > min_l: segments.append((Vector2(x, sy), Vector2(x, y)))
                    sy = -1
        return segments

    def bridge_gaps(self, segments):
        out = segments[:]
        horiz, vert = defaultdict(list), defaultdict(list)
        snap = self.cfg.snap_grid_size # Use Config
        for p1, p2 in segments:
            dx, dy = abs(p2.x - p1.x), abs(p2.y - p1.y)
            if dx > dy: horiz[round(p1.y/snap)*snap].append(sorted([p1.x, p2.x]))
            else: vert[round(p1.x/snap)*snap].append(sorted([p1.y, p2.y]))
        def bridge(buckets, is_v=False):
            new_segs = []
            for axis, intervals in buckets.items():
                intervals.sort()
                for i in range(len(intervals)-1):
                    curr_end = intervals[i][1]
                    next_start = intervals[i+1][0]
                    gap = next_start - curr_end
                    if 0 < gap < 80.0:
                        p1 = Vector2(axis, curr_end) if is_v else Vector2(curr_end, axis)
                        p2 = Vector2(axis, next_start) if is_v else Vector2(next_start, axis)
                        new_segs.append((p1, p2))
            return new_segs
        out.extend(bridge(horiz)); out.extend(bridge(vert, True))
        return out

    def detect_openings(self, segments):
        openings = []
        horiz, vert = defaultdict(list), defaultdict(list)
        snap = self.cfg.snap_grid_size # Use Config
        for p1, p2 in segments:
            dx, dy = abs(p2.x - p1.x), abs(p2.y - p1.y)
            if dx > dy: horiz[round(p1.y/snap)*snap].append(sorted([p1.x, p2.x]))
            else: vert[round(p1.x/snap)*snap].append(sorted([p1.y, p2.y]))
        def scan(buckets, is_v=False):
            found = []
            for axis, intervals in buckets.items():
                intervals.sort()
                if not intervals: continue
                ce = intervals[0][1]
                for ns, ne in intervals[1:]:
                    gap = ns - ce
                    if 25.0 < gap < 100.0:
                        mid = ce + gap*0.5
                        pos = Vector2(axis, mid) if is_v else Vector2(mid, axis)
                        found.append({'pos': pos, 'width': gap, 'vertical': is_v})
                    if ne > ce: ce = ne
            return found
        openings.extend(scan(horiz)); openings.extend(scan(vert, True))
        return openings

    def regularize_lines(self, segments):
        ortho = []
        snap = self.cfg.snap_grid_size
        for p1, p2 in segments:
            dx, dy = abs(p2.x - p1.x), abs(p2.y - p1.y)
            if dx > dy: y = round(((p1.y+p2.y)*0.5)/snap)*snap; ortho.append([Vector2(p1.x, y), Vector2(p2.x, y)])
            else: x = round(((p1.x+p2.x)*0.5)/snap)*snap; ortho.append([Vector2(x, p1.y), Vector2(x, p2.y)])
        points = []; lines_m = []
        for l in ortho:
            v1, v2 = Vector2(l[0].x, l[0].y), Vector2(l[1].x, l[1].y)
            lines_m.append([v1, v2]); points.extend([v1, v2])
        clusters = []
        r = self.cfg.weld_radius
        for p in points:
            found = None
            for c in clusters:
                if p.dist(c['c']) < r: found = c; break
            if found:
                found['m'].append(p)
                n = len(found['m'])
                found['c'] = Vector2(sum(m.x for m in found['m'])/n, sum(m.y for m in found['m'])/n)
            else: clusters.append({'c': Vector2(p.x, p.y), 'm': [p]})
        for c in clusters:
            for m in c['m']: m.x, m.y = c['c'].x, c['c'].y
        final = []
        for p1, p2 in lines_m:
            if p1.dist(p2) < 10.0: continue
            if abs(p2.x-p1.x) > abs(p2.y-p1.y): final.append((Vector2(p1.x, (p1.y+p2.y)*0.5), Vector2(p2.x, (p1.y+p2.y)*0.5)))
            else: final.append((Vector2((p1.x+p2.x)*0.5, p1.y), Vector2((p1.x+p2.x)*0.5, p2.y)))
        return final

    def detect_symbols(self, lines):
        if not lines: return [], []
        adj = defaultdict(list)
        for i, (p1, p2) in enumerate(lines):
            u, v = (int(p1.x), int(p1.y)), (int(p2.x), int(p2.y))
            l = p1.dist(p2)
            adj[u].append((v, l, i)); adj[v].append((u, l, i))
        visited = set(); comps = []
        for start in list(adj.keys()):
            if start in visited: continue
            c = {'l': set(), 'len': 0.0, 'nodes': set()}; q = [start]; visited.add(start)
            c['nodes'].add(start)
            while q:
                curr = q.pop(0)
                for n, l, idx in adj[curr]:
                    if idx not in c['l']: c['l'].add(idx); c['len'] += l
                    if n not in visited: visited.add(n); q.append(n); c['nodes'].add(n)
            comps.append(c)
            
        if not comps: return [], []
        comps.sort(key=lambda x: x['len'], reverse=True)
        max_l = comps[0]['len'] if comps else 1.0
        
        walls = []
        assets = []
        
        for c in comps:
            if (c['len'] / max_l) > self.cfg.island_ratio:
                for idx in c['l']: walls.append(lines[idx])
                continue
            
            xs = [n[0] for n in c['nodes']]
            ys = [n[1] for n in c['nodes']]
            if not xs or not ys: continue
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            w, h = max_x - min_x, max_y - min_y
            if w < 5.0 or h < 5.0: continue
            
            center = Vector2((min_x+max_x)*0.5, (min_y+max_y)*0.5)
            aspect = w / h if h > 0.1 else 1.0
            area = w * h
            
            asset_type = "Unknown"
            if 0.8 < aspect < 1.2 and area < 8000:
                asset_type = "Table"
            elif (aspect > 1.4 or aspect < 0.7) and area > 6000:
                asset_type = "Bed" 
            else:
                asset_type = "Misc"
                
            assets.append({
                'type': asset_type, 'pos': center, 
                'width': w, 'height': h, 'rotation': 0
            })
            
        return walls, assets
