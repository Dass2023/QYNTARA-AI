import maya.cmds as cmds
import random
import json
import os

try:
    ROOT_DIR = os.path.dirname(__file__)
except NameError:
    ROOT_DIR = "e:/QYNTARA AI"

RULES_PATH = os.path.join(ROOT_DIR, "qyntara_ai/rules/qyntara_ruleset.json")

class TestMatrixGenerator:
    def __init__(self):
        self.cursor_x = 0
        self.cursor_z = 0
        self.spacing_x = 8.0 # Gap between Rule Pairs
        self.spacing_z = 6.0 # Gap between Rows
        self.pair_gap = 2.5  # Gap between Good and Bad
        
    def generate(self):
        print("--- Generating Comprehensive Test Matrix ---")
        cmds.file(new=True, force=True)
        
        # Setup Scene Defaults (Valid State)
        cmds.currentUnit(linear='cm')
        cmds.upAxis(axis='y')
        
        # Create Materials
        self.mat_valid = cmds.shadingNode("blinn", asShader=True, name="M_Valid")
        cmds.setAttr(f"{self.mat_valid}.color", 0.2, 0.8, 0.2, type="double3") # Green
        
        self.mat_invalid = cmds.shadingNode("blinn", asShader=True, name="M_Invalid")
        cmds.setAttr(f"{self.mat_invalid}.color", 0.8, 0.2, 0.2, type="double3") # Red
        
        # Load Rules
        with open(RULES_PATH, 'r') as f:
            self.rules = json.load(f)
            
        for rule in self.rules:
            rule_id = rule['id']
            func_name = f"gen_{rule_id}"
            
            if hasattr(self, func_name):
                print(f"Generating samples for {rule_id}...")
                generator = getattr(self, func_name)
                
                # Create Group
                grp = cmds.group(em=True, name=f"GRP_{rule_id}")
                cmds.move(self.cursor_x, 0, self.cursor_z, grp)
                
                # 3D Label
                try:
                    # simplistic text
                    label = cmds.textCurves(f="Arial", t=rule['label'], ch=False)[0]
                    cmds.xform(label, s=(0.5, 0.5, 0.5))
                    cmds.move(self.cursor_x, 3, self.cursor_z - 1.5, label)
                    cmds.setAttr(f"{label}.overrideEnabled", 1)
                    cmds.setAttr(f"{label}.overrideColor", 17) # Yellow
                    cmds.parent(label, grp)
                except: 
                    pass

                # Generate Pair
                try:
                    valid_obj, invalid_obj = generator()
                    
                    if valid_obj:
                        cmds.move(self.cursor_x, 0, self.cursor_z, valid_obj, ws=True)
                        self.assign_mat(valid_obj, True)
                        cmds.rename(valid_obj, f"VALID_{rule_id}")
                        cmds.parent(f"VALID_{rule_id}", grp)
                        
                    if invalid_obj:
                        cmds.move(self.cursor_x + self.pair_gap, 0, self.cursor_z, invalid_obj, ws=True)
                        self.assign_mat(invalid_obj, False)
                        cmds.rename(invalid_obj, f"INVALID_{rule_id}")
                        cmds.parent(f"INVALID_{rule_id}", grp)
                except Exception as e:
                    print(f"FAILED to generate {rule_id}: {e}")
                
                # Advance Cursor
                self.cursor_x += self.spacing_x
                if self.cursor_x > 40: # Wrap row
                    self.cursor_x = 0
                    self.cursor_z += self.spacing_z
            else:
                print(f"Skipping {rule_id} (No generator implemented)")

    def assign_mat(self, obj, is_valid):
        # 1. Handle Joints/Locators (Override Color)
        if cmds.objectType(obj) == 'joint' or cmds.nodeType(obj) == 'joint':
            # Joints accept drawing overrides, not shaders
            cmds.setAttr(f"{obj}.overrideEnabled", 1)
            cmds.setAttr(f"{obj}.overrideColor", 14 if is_valid else 13) # 14=Green, 13=Red
            return

        # 2. Handle Geometry (Meshes/Nurbs)
        shapes = cmds.listRelatives(obj, shapes=True, fullPath=True)
        if not shapes: return
        
        valid_types = ['mesh', 'nurbsSurface']
        valid_shapes = [s for s in shapes if cmds.objectType(s) in valid_types]
        
        if not valid_shapes:
            return
        
        mat = self.mat_valid if is_valid else self.mat_invalid
        sg_name = f"{mat}SG"
        
        if cmds.objExists(sg_name):
            sg = sg_name
        else:
            sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=sg_name)
            cmds.connectAttr(f"{mat}.outColor", f"{sg}.surfaceShader")
            
        try: 
            # Apply to shapes explicitly to avoid recursion warnings on child constraints
            cmds.sets(valid_shapes, forceElement=sg)
        except: pass

    # ================= GENERATORS =================
    
    # --- GEOMETRY ---
    def gen_geo_open_edges(self):
        v = cmds.polyCube()[0]
        i = cmds.polyCube()[0]; cmds.delete(f"{i}.f[1]")
        return v, i

    def gen_geo_ngons(self):
        v = cmds.polyPlane(sx=2, sy=1)[0]
        i = cmds.polyPlane(sx=2, sy=1)[0]; cmds.delete(f"{i}.e[4]")
        return v, i
        
    def gen_geo_triangulated(self):
        v = cmds.polyCube()[0]; cmds.polyTriangulate(v)
        i = cmds.polyCube()[0]
        return v, i
        
    def gen_geo_non_manifold(self):
        v = cmds.polyCube()[0]
        # Robust Non-Manifold: Extrude an edge to create a "Fin" (3 faces sharing 1 edge)
        i = cmds.polyCube()[0]
        cmds.polyExtrudeEdge(f"{i}.e[9]", ltz=0.5, lty=0.5) 
        return v, i
        
    def gen_geo_lamina_faces(self):
        v = cmds.polyCube()[0]
        i = cmds.polyCube()[0]
        # Duplicate a face in place
        cmds.polyChipOff(f"{i}.f[0]", dup=True, off=0)
        # Merge vertices to create topological sharing
        cmds.polyMergeVertex(i, d=0.001)
        return v, i

    def gen_geo_zero_area(self):
        v = cmds.polyPlane()[0]
        i = cmds.polyPlane(w=1, h=1, sx=1, sy=1)[0] 
        # Scale face to TRUE zero (1e-6)
        cmds.scale(0.000001, 0.000001, 0.000001, f"{i}.vtx[:]")
        return v, i
        
    def gen_geo_zero_length(self):
        v = cmds.polyCube()[0]
        i = cmds.polyCube()[0]
        # Collapse an edge completely
        cmds.polyCollapseEdge(f"{i}.e[0]")
        return v, i
        
    def gen_geo_poles(self):
        v = cmds.polySphere(sx=8, sy=8)[0]
        i = cmds.polySphere(sx=20, sy=20)[0]; cmds.polyPoke(f"{i}.f[0]") # Creates a pole
        return v, i
        
    def gen_geo_history(self):
        v = cmds.polyCube()[0]; cmds.delete(v, ch=True)
        i = cmds.polyCube()[0]; cmds.polyExtrudeFacet(f"{i}.f[0]", ltz=0.5)
        return v, i
        
    def gen_geo_hard_edges(self):
        v = cmds.polySphere()[0]; cmds.polySoftEdge(v, angle=180)
        i = cmds.polySphere()[0]; cmds.polySoftEdge(i, angle=0)
        return v, i
        
    def gen_geo_normals(self):
        v = cmds.polyCube()[0]
        # Explicit Lock
        i = cmds.polyCube()[0]
        cmds.polyNormalPerVertex(f"{i}.vtx[:]", x=0, y=1, z=0) 
        cmds.polyNormalPerVertex(i, freezeNormal=1)
        return v, i
        
    def gen_geo_inverted_normals(self):
        v = cmds.polyCube()[0]
        i = cmds.polyCube()[0]
        s = cmds.listRelatives(i, s=True)[0]
        cmds.setAttr(f"{s}.opposite", 1)
        return v, i

    def gen_geo_vertex_color(self):
        v = cmds.polyCube()[0]; cmds.polyColorPerVertex(v, r=1, g=1, b=1, a=1, cdo=True)
        i = cmds.polyCube()[0] 
        return v, i
        
    def gen_geo_floating(self):
        v = cmds.polyCube()[0]
        i = cmds.polyCube()[0]
        # Tiny floating triangle (Debris)
        bit = cmds.polyPlane(w=0.001, h=0.001, sx=1, sy=1)[0]
        cmds.parent(bit, i) 
        return v, i
        
    def gen_geo_internal_faces(self):
        v = cmds.polyCube(w=3)[0]
        
        # Robust Internal Face:
        # 1. Create 2 cubes side-by-side
        c1 = cmds.polyCube()[0]
        c2 = cmds.polyCube()[0]
        cmds.move(1, 0, 0, c2)
        # 2. Combine and Merge vertices
        i = cmds.polyUnite(c1, c2, ch=False)[0]
        cmds.polyMergeVertex(i, d=0.1)
        # Now the shared face in the middle is "Internal" (connected to >2 faces)
        return v, i
        
    def gen_geo_polycount(self):
        v = cmds.polySphere(sx=20, sy=20)[0]
        i = cmds.polySphere(sx=300, sy=300)[0]
        return v, i
        
    def gen_geo_intersect(self):
        v = cmds.group(em=True, n="No_Intersection")
        c1 = cmds.polyCube()[0]; cmds.move(1.5,0,0,c1); cmds.parent(c1,v)
        c2 = cmds.polyCube()[0]; cmds.move(-1.5,0,0,c2); cmds.parent(c2,v)
        
        i = cmds.group(em=True, n="Intersection")
        ic1 = cmds.polyCube()[0]; cmds.move(0.0,0,0,ic1); cmds.parent(ic1,i)
        ic2 = cmds.polyCube()[0]; cmds.move(0.2,0,0,ic2); cmds.parent(ic2,i) 
        return v, i

    # --- TRANSFORMS ---
    def gen_xform_frozen(self):
        v = cmds.polyCube()[0]; cmds.makeIdentity(v, apply=True, t=1, r=1, s=1)
        i = cmds.polyCube()[0]; cmds.rotate(0, 45, 0, i)
        return v, i
    
    def gen_xform_scale(self):
        v = cmds.polyCube()[0]
        i = cmds.polyCube()[0]; cmds.scale(1, 2, 1, i)
        return v, i
        
    def gen_xform_negative_scale(self):
        v = cmds.polyCube()[0]
        i = cmds.polyCube()[0]; cmds.scale(-1, 1, 1, i)
        return v, i
        
    def gen_check_pivot_center(self):
        v = cmds.polyCube()[0]
        i = cmds.polyCube()[0]; cmds.xform(i, piv=(5,5,5), ws=True)
        return v, i
        
    def gen_scene_hierarchy(self):
        v = cmds.group(em=True, n="Valid_Root"); c = cmds.polyCube()[0]; cmds.parent(c, v)
        i = cmds.polyCube(n="Invalid_Top_Level")[0]
        return v, i
        
    def gen_scene_unused(self):
        v = cmds.polyCube()[0]
        i = cmds.group(em=True, n="Unused_Grp")
        cam = cmds.camera()[0]; cmds.parent(cam, i)
        return v, i
        
    def gen_geo_proximity(self):
        # Grid Snapping + Gap Check
        v = cmds.polyCube()[0] # On grid
        i = cmds.group(em=True, n="Gaps_OffGrid")
        
        # 1. Gap
        c1 = cmds.polyCube()[0]; cmds.move(0.505,0,0,c1); cmds.parent(c1,i) 
        c2 = cmds.polyCube()[0]; cmds.move(-0.5,0,0,c2); cmds.parent(c2,i)
        
        # 2. Off Grid
        c3 = cmds.polyCube()[0]
        cmds.move(10.05, 0, 0, c3) # Expect fail
        cmds.parent(c3, i)
        
        return v, i

    # --- UV ---
    def gen_uv_exists(self):
        v = cmds.polyCube()[0]
        i = cmds.polyCube()[0]; cmds.delete(f"{i}.map[:]") 
        return v, i

    def gen_uv_bounds(self):
        v = cmds.polyPlane()[0]
        i = cmds.polyPlane()[0]; cmds.polyEditUV(f"{i}.map[:]", u=2.0)
        return v, i
        
    def gen_uv_overlap(self):
        v = cmds.polySphere()[0]
        i = cmds.polySphere()[0]
        cmds.polyProjection(f"{i}.f[0:1]", type='Planar', md='y')
        return v, i

    def gen_uv_flipped(self):
        v = cmds.polyPlane()[0]
        i = cmds.polyPlane()[0]; cmds.polyEditUV(f"{i}.map[:]", scaleU=-1, pivotU=0.5)
        return v, i
        
    def gen_uv_zero_area(self):
        v = cmds.polyPlane()[0]
        i = cmds.polyPlane()[0]; cmds.polyEditUV(f"{i}.map[:]", scaleU=0, scaleV=0)
        return v, i
        
    def gen_uv_texel_density(self):
        v = cmds.polyPlane(w=1, h=1)[0]
        i = cmds.polyPlane(w=10, h=10)[0] 
        cmds.polyEditUV(f"{i}.map[:]", scaleU=0.01, scaleV=0.01, pivotU=0.5, pivotV=0.5)
        return v, i

    # --- MATERIALS ---
    def gen_mat_default(self):
        v = cmds.polyCube()[0] 
        i = cmds.polyCube()[0] 
        return v, i

    def gen_mat_naming(self):
        v = cmds.polyCube()[0]
        i = cmds.polyCube()[0]
        return v, i

    def gen_mat_missing(self):
        v = cmds.polyCube()[0]
        i = cmds.polyCube()[0]
        return v, i
        
    def gen_mat_multi_assigned(self):
        v = cmds.polyCube()[0]
        i = cmds.polyCube()[0]
        cmds.sets(f"{i}.f[0]", forceElement="initialShadingGroup")
        return v, i
        
    def gen_mat_complex(self):
        v = cmds.polyCube()[0]
        i = cmds.polyCube()[0]
        s = cmds.shadingNode("lambert", asShader=True)
        sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True)
        cmds.connectAttr(f"{s}.outColor", f"{sg}.surfaceShader")
        r = cmds.shadingNode("ramp", asTexture=True)
        try: cmds.connectAttr(f"{r}.outColor", f"{s}.color")
        except: pass
        cmds.sets(i, forceElement=sg)
        return v, i

    # --- BAKING ---
    def gen_bake_uv2_exists(self):
        v = cmds.polyCube()[0]; cmds.polyUVSet(v, create=True, uvSet='Lightmap'); cmds.polyCopyUV(v, uvi='map1', uvs='Lightmap')
        i = cmds.polyCube()[0]
        return v, i
        
    def gen_bake_uv2_validity(self):
        v = cmds.polyCube()[0]; cmds.polyUVSet(v, create=True, uvSet='Lightmap'); cmds.polyCopyUV(v, uvi='map1', uvs='Lightmap')
        i = cmds.polyCube()[0]; cmds.polyUVSet(i, create=True, uvSet='Lightmap'); cmds.polyCopyUV(i, uvi='map1', uvs='Lightmap')
        cmds.polyUVSet(i, currentUVSet=True, uvSet='Lightmap')
        cmds.polyEditUV(f"{i}.map[:]", u=2.0) 
        cmds.polyUVSet(i, currentUVSet=True, uvSet='map1')
        return v, i
        
    def gen_render_terminator(self):
        # Terminator Risk: Low poly + Smooth Normals + Tangent Light
        # Create Sphere (low)
        v = cmds.polySphere(sx=32, sy=32)[0] # High poly ok
        i = cmds.polySphere(sx=6, sy=6)[0]; # Low Poly
        cmds.polySoftEdge(i, angle=180) # Force Smooth
        return v, i
        
    def gen_bake_padding(self):
        v = cmds.polyCube()[0] 
        
        # INVALID: Create 2 DISTINCT CUBES and Combine them.
        # This guarantees 2 separate UV shells that overlap perfectly (0-1).
        c1 = cmds.polyCube()[0]
        c2 = cmds.polyCube()[0]
        
        # Move c2 slightly in 3D (to see them)
        cmds.move(0.5, 0.5, 0.5, c2)
        
        # Combine
        i = cmds.polyUnite(c1, c2, ch=False)[0]
        
        # Now we have 1 mesh with 2 overlapping shells.
        # Padding distance = 0.
        # Check should fail.
        
        return v, i
        
    def gen_bake_seams(self):
        v = cmds.polyCube()[0] # Hard edges match UV seams
        i = cmds.polyCube()[0]; cmds.polySoftEdge(f"{i}.e[0]", a=0) # Harden edge
        # BUT sew UVs?
        cmds.polyMergeUV(f"{i}.map[:]", d=1.0) # Sew UVs
        return v, i

    # --- NAMING ---
    def gen_check_naming_convention(self):
        v = cmds.polyCube(n="GEO_Box_01_GEO")[0]
        i = cmds.polyCube(n="pCube1")[0]
        return v, i

    # --- ANIMATION ---
    def gen_anim_skin_weights(self):
        # Valid
        v = cmds.polyCube()[0]
        # Create joint, parent to v so it moves with it
        cmds.select(clear=True) # Ensure joint is not parented to previous
        j = cmds.joint(p=(0,0,0))
        cmds.parent(j, v)
        # Skin
        cmds.skinCluster(j, v)
        
        # Invalid
        i = cmds.polyCube()[0]
        cmds.select(clear=True)
        j2 = cmds.joint(p=(0,0,0))
        cmds.parent(j2, i)
        sc = cmds.skinCluster(j2, i)[0]
        # Unnormalized check
        cmds.setAttr(f"{sc}.normalizeWeights", 0)
        # Force a bad weight (0.99 total). 
        cmds.skinPercent(sc, f"{i}.vtx[0]", transformValue=[(j2, 0.99)]) 
        return v, i

    def gen_anim_baked(self):
        v = cmds.polyCube()[0]
        # Valid: Baked on every frame
        cmds.setKeyframe(v, t=1, v=0, at='tx')
        cmds.setKeyframe(v, t=2, v=1, at='tx')
        cmds.setKeyframe(v, t=3, v=2, at='tx')
        
        # Invalid: Sparse keys (Sim not baked)
        i = cmds.polyCube()[0] 
        cmds.setKeyframe(i, t=1, v=0, at='tx')
        cmds.setKeyframe(i, t=10, v=10, at='tx') # Gap > 1.01
        return v, i
        
    def gen_anim_constraints(self):
        v = cmds.polyCube()[0]
        i = cmds.polyCube()[0]
        loc = cmds.spaceLocator()[0]
        cmds.parentConstraint(loc, i)
        return v, i
        
    def gen_anim_root_motion(self):
        # Valid: Root MOVES (Has keys)
        v = cmds.joint(p=(0,0,0), n="Valid_Root_Jnt")
        cmds.setKeyframe(v, t=1, v=0, at='tx')
        cmds.setKeyframe(v, t=10, v=10, at='tx') 
        
        # Invalid: Root STATIC (No keys or 0 distance)
        i = cmds.joint(p=(0,0,0), n="Invalid_Root_Jnt")
        # No keys = Static
        return v, i

if __name__ == "__main__":
    gen = TestMatrixGenerator()
    gen.generate()
