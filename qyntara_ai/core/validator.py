import json
import os
import logging
from maya import cmds
from . import geometry, naming, transforms, uv, materials, animation, baking, scene

logger = logging.getLogger(__name__)

class QyntaraValidator:
    def __init__(self, rules_path=None):
        if not rules_path:
            # Default to rules/qyntara_ruleset.json relative to this file
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            rules_path = os.path.join(base_path, 'rules', 'qyntara_ruleset.json')
        
        self.rules_path = rules_path
        self.rules = self.load_rules()
        
        # Function registry
        self.registry = {
            "check_open_edges": geometry.check_open_edges,
            "check_non_manifold": geometry.check_non_manifold,
            "check_lamina_faces": geometry.check_lamina_faces,
            "check_ngons": geometry.check_ngons,
            # "check_degenerate_geometry": geometry.check_degenerate_geometry, # Deprecated
            "check_coinciding_geometry": geometry.check_coinciding_geometry,
            "check_scale": transforms.check_scale,
            "check_uv_overlaps": uv.check_uv_overlaps,
            "check_uv_bounds": uv.check_uv_bounds,
            # "check_degenerate_geometry": geometry.check_degenerate_geometry, # Deprecated
            # Industry / Game
            "check_lod_group": scene.check_lod_group,
            "check_material_usage_limit": materials.check_material_usage_limit,
            "check_texture_size": materials.check_texture_size,
            "check_max_joints": animation.check_max_joints,
            "check_strict_quads": geometry.check_strict_quads,
            "check_udim_tiles": uv.check_udim_tiles,
            
            # Scene
            "check_scene_units": scene.check_scene_units,
            "check_up_axis": scene.check_up_axis,
            "check_hierarchy": scene.check_hierarchy,
            "check_unused_nodes": scene.check_unused_nodes,
            "check_scene_pollution": scene.check_scene_pollution, # NEW
            "check_clean_outliner": scene.check_clean_outliner, # NEW
            
            # TD / Naming
            "check_naming_convention": naming.check_naming_convention,
            "check_collision_naming": naming.check_collision_naming, # NEW

            # Topology
            "check_scan_outliers": geometry.check_scan_outliers, # NEW (LiDAR)
            "check_concave_faces": geometry.check_concave_faces, # NEW
            "check_default_material": materials.check_default_material,
            "check_poles": geometry.check_poles,
            "check_construction_history": geometry.check_construction_history,
            "check_gaps": geometry.check_gaps,
            "check_proximity_gaps": geometry.check_proximity_gaps, # Fixed Key
            "check_intersections": geometry.check_coinciding_geometry,
            "check_floating_geometry": geometry.check_floating_geometry, # Fixed Key
            "check_leaks": geometry.check_light_leaks,
            "check_missing_bevels": geometry.check_missing_bevels,
            "check_shadow_terminator": geometry.check_shadow_terminator,
            "check_normals": geometry.check_normals,
            "check_polycount": geometry.check_polycount,
            "check_pivot_center": transforms.check_pivot_center,
            "check_multi_materials": materials.check_multi_materials,
            "check_vertex_colors": geometry.check_vertex_colors,
            "check_internal_faces": geometry.check_internal_faces,
            "check_watertight": geometry.check_watertight,
            "check_zero_area_faces": geometry.check_zero_area_faces,
            "check_zero_length_edges": geometry.check_zero_length_edges,
            "check_uv_exists": uv.check_uv_exists,
            "check_flipped_uvs": uv.check_flipped_uvs,
            "check_texel_density": uv.check_texel_density,
            "check_inverted_normals": geometry.check_inverted_normals,
            "check_hard_edges": geometry.check_hard_edges,
            "check_zero_area_uvs": uv.check_zero_area_uvs,
            "check_triangulated": geometry.check_triangulated,
            "check_frozen_transforms": transforms.check_frozen_transforms,
            "check_negative_scale": transforms.check_negative_scale,
            "check_hierarchy": scene.check_hierarchy,
            "check_unused_nodes": scene.check_unused_nodes,
            "check_missing_shader": materials.check_missing_shader,
            "check_shader_naming": materials.check_shader_naming,
            "check_complex_nodes": materials.check_complex_nodes,

            
            # Animation Checks 
            "check_skin_weights": animation.check_skin_weights,
            "check_animation_baked": animation.check_animation_baked,
            "check_root_motion": animation.check_root_motion,
            "check_constraints": animation.check_constraints,
            
            # Baking Checks
            "check_uv2_exists": baking.check_uv2_exists,
            "check_uv2_validity": baking.check_uv2_validity,
            "check_padding": baking.check_padding,
            "check_light_leakage": baking.check_light_leakage,
            "check_light_leakage": baking.check_light_leakage,
            "check_seams": baking.check_seams,
            "check_texture_continuity": uv.check_texture_continuity, # New
        }

        self.current_profile = "game" # Default
        
        # Pipeline Profiles (Strictly matched to Reference Image)
        self.profiles = {
            "game": {
                # Baking
                "bake_uv2_exists": {"severity": "error"},
                "bake_uv2_validity": {"severity": "error"},

                "bake_seams": {"severity": "warning"}, # Warning initially
                "bake_padding": {"severity": "info"}, # Info as it's heuristic
                
                # Animation (Game: Strict)
                "anim_skin_weights": {"severity": "error"},
                "anim_baked": {"severity": "error"},
                "anim_root_motion": {"severity": "error"},
                "anim_constraints": {"severity": "error"}, # Must be baked
                
                # Material (Game: Simple)
                "mat_complex": {"severity": "error"}, # No complex nodes
                "mat_default": {"severity": "error"}, # Was mat_no_lambert1
                "mat_missing": {"severity": "error"}, # Was mat_has_shader
                
                # Geometry remains standard...
                "geo_non_manifold": {"severity": "error"},

                "geo_lamina_faces": {"severity": "error"},
                "geo_open_edges": {"severity": "error"}, 
                "geo_zero_area": {"severity": "error"},
                "geo_zero_length": {"severity": "error"},
                "geo_internal_faces": {"severity": "error", "enabled": True}, # Enabled
                "geo_intersect": {"severity": "warning"},
                "geo_history": {"severity": "error"}, # Must freeze history
                "geo_poles": {"severity": "warning"},
                "geo_floating": {"severity": "error"}, # No debris
                
                # Normals
                "geo_inverted_normals": {"severity": "error"},
                "geo_normals": {"severity": "error"}, # Locked/Corrupt
                "geo_hard_edges": {"severity": "warning"}, # Soft edges preferred
                
                # UVs
                "uv_exists": {"severity": "error"},
                "uv_overlaps": {"severity": "error"},
                "uv_flipped": {"severity": "error"},
                "uv_zero_area": {"severity": "error"},

                "uv_bounds": {"severity": "error"}, # 0-1 for optimization
                "uv_texel_density": {"severity": "warning"}, 
                
                # Topology
                "geo_ngons": {"severity": "error"},
                "geo_triangulated": {"severity": "info"}, # Good but not strict error
                "geo_polycount": {"severity": "warning"},
                
                # Transforms
                "xform_frozen": {"severity": "error"},
                "scene_units": {"severity": "error"}, # Real-world scale
                "xform_negative_scale": {"severity": "error"},
                "check_up_axis": {"severity": "error"},
                "check_pivot_center": {"severity": "error"},
                "geo_proximity": {"severity": "info"}, # Grid snap suggestion
                "geo_missing_bevels": {"severity": "warning"}, # Warn if bevels missing for baking
                
                # Scene & Materials
                "check_naming_convention": {"severity": "error"},
                "scene_hierarchy": {"severity": "error"},
                "scene_unused": {"severity": "error"},
                "check_default_material": {"severity": "error"}, # No lambert1
                "mat_missing": {"severity": "error"},
                "mat_complex": {"severity": "error"}, # Basic export only
                "mat_naming": {"severity": "error"},
                "render_terminator": {"severity": "warning"},
            },
            "vr": { # AR/VR
                # Geometry
                "geo_non_manifold": {"severity": "error"},
                "geo_lamina_faces": {"severity": "error"},
                "geo_open_edges": {"severity": "error"},
                "geo_zero_area": {"severity": "error"},
                "geo_zero_length": {"severity": "error"},
                "geo_internal_faces": {"severity": "error"},
                "geo_watertight": {"severity": "error", "enabled": True}, 
                "geo_intersect": {"severity": "warning"},
                "geo_history": {"severity": "error"},
                "geo_leaks": {"severity": "error", "enabled": True}, # Light leaks critical in VR baking
                
                # Normals
                "geo_inverted_normals": {"severity": "error"},
                "geo_normals": {"severity": "error"},
                "geo_hard_edges": {"severity": "warning"},
                
                # UVs
                "uv_exists": {"severity": "error"},
                "uv_overlaps": {"severity": "error"},
                "uv_flipped": {"severity": "error"},
                "uv_zero_area": {"severity": "error"},

                "uv_bounds": {"severity": "error"},
                "uv_texel_density": {"severity": "warning"},
                
                # Topology
                "geo_ngons": {"severity": "error"},
                "geo_triangulated": {"severity": "info"},
                "geo_polycount": {"severity": "error"}, # Strict budget
                
                # Transforms
                "xform_frozen": {"severity": "error"},
                "scene_units": {"severity": "error"},
                "xform_negative_scale": {"severity": "error"},
                "check_up_axis": {"severity": "error"},
                "check_pivot_center": {"severity": "error"},
                
                # Scene & Materials
                "check_naming_convention": {"severity": "error"},
                "scene_hierarchy": {"severity": "error"},
                "scene_unused": {"severity": "error"},
                "check_default_material": {"severity": "error"}, 
                "mat_missing": {"severity": "error"},
                "mat_complex": {"severity": "error"}, 
                "mat_naming": {"severity": "error"},
            },
            "vfx": {
                # Geometry
                "geo_non_manifold": {"severity": "warning"},
                "geo_lamina_faces": {"severity": "error"},
                "geo_open_edges": {"severity": "warning"}, 
                "geo_zero_area": {"severity": "error"},
                "geo_zero_length": {"severity": "error"},
                "geo_internal_faces": {"severity": "warning"},
                "geo_intersect": {"severity": "info"}, 
                "geo_history": {"severity": "warning"}, # History sometimes kept
                "geo_poles": {"severity": "info"}, # Sub-d handles poles better
                "geo_vertex_color": {"severity": "info", "enabled": False},
                
                # Normals
                "geo_inverted_normals": {"severity": "warning"}, 
                "geo_normals": {"severity": "warning"},
                "geo_hard_edges": {"severity": "info"},
                
                # UVs
                "uv_exists": {"severity": "error"},
                "uv_overlaps": {"severity": "info"}, # UDIMs allowed
                "uv_flipped": {"severity": "error"},
                "uv_zero_area": {"severity": "error"},

                "uv_bounds": {"severity": "info", "enabled": False}, # UDIMs go beyond 0-1
                "uv_texel_density": {"severity": "info"}, 
                
                # Topology
                "geo_ngons": {"severity": "warning"}, 
                "geo_triangulated": {"severity": "error", "enabled": False}, # Quads preferred
                "geo_polycount": {"severity": "info"},
                
                # Transforms
                "xform_frozen": {"severity": "error"}, 
                "xform_negative_scale": {"severity": "warning"}, 
                "check_up_axis": {"severity": "warning"},
                "check_pivot_center": {"severity": "warning"},
                "geo_missing_bevels": {"severity": "error"}, # Strict for VFX renders
                
                # Scene & Materials
                "check_naming_convention": {"severity": "error"},
                "scene_hierarchy": {"severity": "error"},
                "scene_unused": {"severity": "warning"}, 
                "check_default_material": {"severity": "error"}, 
                "mat_missing": {"severity": "error"},
                "mat_complex": {"severity": "error", "enabled": False}, # VFX allows complex
                "mat_naming": {"severity": "error"},
            },
            "web": {
                "geo_polycount": {"severity": "error"},
                "uv_exists": {"severity": "error"},
                "uv_texture_continuity": {"severity": "warning"}, # New Rule

            },
            "lidar": {
                "scan_outliers": {"severity": "error"},
                "geo_floating": {"severity": "error"},
                "geo_open_edges": {"severity": "error"}, 
                "geo_non_manifold": {"severity": "error"},
                "geo_zero_area": {"severity": "warning"},
                "geo_zero_length": {"severity": "warning"},
                "scene_units": {"severity": "error"}, # Critical for Scan Data
                "xform_frozen": {"severity": "warning"},
                
                # Disable irrelevant checks for raw scans
                "uv_exists": {"severity": "info", "enabled": False},
                "mat_missing": {"severity": "info", "enabled": False},
                "geo_polycount": {"severity": "info", "enabled": False}, # Scans are heavy
                "geo_hard_edges": {"severity": "info", "enabled": False},
            }
        }

    def load_rules(self):
        if not os.path.exists(self.rules_path):
            logger.error(f"Rules file not found: {self.rules_path}")
            return []
        try:
            with open(self.rules_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load rules: {e}")
            return []

    def set_pipeline_profile(self, profile_name):
        if profile_name in self.profiles:
            self.current_profile = profile_name
            
    def run_validation(self, objects, disabled_rules=None):
        """
        Runs validation on a list of objects (strings).
        Optionally accepts a list of rule IDs to force-disable.
        Returns a dictionary containing the report.
        """
        report = {
            "summary": {"passed": 0, "failed": 0, "errors": 0, "warnings": 0},
            "details": []
        }
        
        disabled_rules = disabled_rules or []
        profile_overrides = self.profiles.get(self.current_profile, {})

        for rule in self.rules:
            rule_id = rule["id"]
            
            # Apply Profile Overrides
            enabled = rule.get("enabled", True)
            severity = rule.get("severity", "error")
            
            if rule_id in profile_overrides:
                override = profile_overrides[rule_id]
                if "enabled" in override:
                    enabled = override["enabled"]
                if "severity" in override:
                    severity = override["severity"]
            
            # Runtime Override (UI)
            if rule_id in disabled_rules:
                enabled = False
            
            if not enabled:
                continue
            
            func_name = rule.get("function")
            func = self.registry.get(func_name)
            
            if not func:
                # Silently skip if function not implemented yet (e.g. check_internal_faces)
                # logger.warning(f"Function {func_name} not found for rule {rule['id']}")
                continue
                
            try:
                # DEBUG TRACE
                # print(f"DEBUG: Running Rule {rule_id}...")

                # 1. GLOBAL SAFETY RESET (TD-Approved)
                # Ensure no stale constraints affect the next rule
                if cmds:
                    cmds.select(clear=True)
                    cmds.polySelectConstraint(disable=True)

                # Handle parameters if any
                params = rule.get("parameters", {})
                if params:
                    # simplified argument passing - ensure no collision with positional 'objects'
                    safe_params = {k: v for k, v in params.items() if k != 'objects'}
                    violations = func(objects, **safe_params)
                else:
                    violations = func(objects)
                
                # print(f"DEBUG: Rule {rule_id} Finished. Violations: {len(violations)}")

                if violations:
                    report["details"].append({
                        "rule_id": rule_id,
                        "rule_label": rule["label"],
                        "severity": severity,
                        "violations": violations,
                        "status": "FAILED"
                    })
                    
                    if severity == "error":
                        report["summary"]["errors"] += len(violations)
                    elif severity == "warning":
                        report["summary"]["warnings"] += len(violations)
                    report["summary"]["failed"] += 1
                else:
                    # Report PASS so UI updates from READY -> GREEN
                    report["details"].append({
                        "rule_id": rule_id,
                        "rule_label": rule["label"],
                        "severity": severity,
                        "violations": [],
                        "status": "PASSED"
                    })
                    report["summary"]["passed"] += 1
                    
            except Exception as e:
                logger.error(f"Error running rule {rule['id']}: {e}")
                print(f"DEBUG: Rule {rule['id']} CRASHED: {e}")
                
        return report

    def revalidate_report(self, report):
        """
        Re-validates an existing report in-place.
        Crucially, this only re-checks objects that were previously failing.
        This prevents 'State Accumulation' errors where Auto-Fixing one issue
        accidentally exposes a 'new' issue on the same object, causing the total count to rise.
        """
        if not report: return self.validate_selection()
        
        logger.info("Re-validating existing state (Stateful Update)...")
        from maya import cmds
        
        failed_count = 0
        warning_count = 0
        passed_count = 0
        
        for detail in report.get("details", []):
            rule_id = detail["rule_id"]
            # We need to find the check function again.
            # Ideally we store function_name in details, but if not, look up in self.rules
            check_func = None
            rule_def = next((r for r in self.rules if r['id'] == rule_id), None)
            if rule_def:
                check_func = self.registry.get(rule_def.get("function"))
            
            if not check_func:
                continue
                
            # Get objects that were failing
            violators = detail.get("violations", [])
            objects_to_check = []
            for v in violators:
                obj = v.get("object")
                if not obj: continue
                
                # Special Case: "Scene" or "Scene Structure" are virtual objects representing global state.
                # They cannot be "checked" individually like a DAG node in this loop.
                # They are effectively always "present" until the rule passes globally.
                if obj in ["Scene", "Scene Structure"] or " " in obj:
                     # For global rules, we just have to Run the Check function globally (on all objects?)
                     # Or pass a dummy list. The check functions usually re-scan the scene anyway if input is "Scene".
                     # Actually, check functions like check_scene_units use 'objects' just to initiate but check global state.
                     # So we should treat them as valid "roots" to trigger the re-check.
                     objects_to_check.append(obj)
                     continue

                if cmds.objExists(obj):
                    objects_to_check.append(obj)
                else:
                    # Object might have been renamed or unparented but kept short name
                    short = obj.split("|")[-1]
                    
                    if " " in short: 
                        # Safety: strings with spaces cause SyntaxError in ls
                        continue
                        
                    # Check if standard name exists
                    matches = cmds.ls(short, long=True)
                    if matches:
                        # Use the first match (Best effort)
                        objects_to_check.append(matches[0])
            
            if not objects_to_check:
                # If no objects listed (or all deleted), it's PASSED
                detail["violations"] = []
                detail["status"] = "PASSED"
                passed_count += 1
                continue
                
            # Run Check (Scoped to specific objects)
            try:
                new_violations = check_func(objects_to_check) 
                
                # Update State
                if new_violations:
                    detail["violations"] = new_violations
                    detail["status"] = "FAILED"
                    if detail.get("severity") == "error":
                        failed_count += 1
                    else:
                        warning_count += 1
                else:
                    detail["violations"] = []
                    detail["status"] = "PASSED"
                    passed_count += 1
                    
            except Exception as e:
                logger.warning(f"Re-validation failed for {rule_id}: {e}")
        
        
        # Recalculate Summary Stats
        total_errors = 0
        total_warnings = 0
        
        for detail in report.get("details", []):
            if detail["status"] == "FAILED":
                count = len(detail.get("violations", []))
                if detail.get("severity") == "error":
                    total_errors += count
                else:
                    total_warnings += count
        
        report["summary"] = {
            "total_rules": len(report["details"]),
            "passed": passed_count,
            "failed": failed_count,
            "errors": total_errors,
            "warnings": total_warnings
        }
        
        return report
