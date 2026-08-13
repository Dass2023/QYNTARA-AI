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
        self._raw_registry = {
            "check_open_edges": getattr(geometry, "check_open_edges", None),
            "check_non_manifold": getattr(geometry, "check_non_manifold", None),
            "check_lamina_faces": getattr(geometry, "check_lamina_faces", None),
            "check_ngons": getattr(geometry, "check_ngons", None),
            "check_coinciding_geometry": getattr(geometry, "check_coinciding_geometry", None),
            "check_scale": getattr(transforms, "check_scale", None),
            "check_uv_overlaps": getattr(uv, "check_uv_overlaps", None),
            "check_uv_bounds": getattr(uv, "check_uv_bounds", None),
            "check_lod_group": getattr(scene, "check_lod_group", None),
            "check_material_usage_limit": getattr(materials, "check_material_usage_limit", None),
            "check_texture_size": getattr(materials, "check_texture_size", None),
            "check_max_joints": getattr(animation, "check_max_joints", None),
            "check_strict_quads": getattr(geometry, "check_strict_quads", None),
            "check_udim_tiles": getattr(uv, "check_udim_tiles", None),
            "check_scene_units": getattr(scene, "check_scene_units", None),
            "check_up_axis": getattr(scene, "check_up_axis", None),
            "check_hierarchy": getattr(scene, "check_hierarchy", None),
            "check_unused_nodes": getattr(scene, "check_unused_nodes", None),
            "check_scene_pollution": getattr(scene, "check_scene_pollution", None),
            "check_clean_outliner": getattr(scene, "check_clean_outliner", None),
            "check_naming_convention": getattr(naming, "check_naming_convention", None),
            "check_collision_naming": getattr(naming, "check_collision_naming", None),
            "check_scan_outliers": getattr(geometry, "check_scan_outliers", None),
            "check_concave_faces": getattr(geometry, "check_concave_faces", None),
            "check_default_material": getattr(materials, "check_default_material", None),
            "check_poles": getattr(geometry, "check_poles", None),
            "check_construction_history": getattr(geometry, "check_construction_history", None),
            "check_gaps": getattr(geometry, "check_gaps", None),
            "check_proximity_gaps": getattr(geometry, "check_proximity_gaps", None),
            "check_floating_geometry": getattr(geometry, "check_floating_geometry", None),
            "check_leaks": getattr(geometry, "check_light_leaks", None),
            "check_missing_bevels": getattr(geometry, "check_missing_bevels", None),
            "check_shadow_terminator": getattr(geometry, "check_shadow_terminator", None),
            "check_normals": getattr(geometry, "check_normals", None),
            "check_polycount": getattr(geometry, "check_polycount", None),
            "check_pivot_center": getattr(transforms, "check_pivot_center", None),
            "check_multi_materials": getattr(materials, "check_multi_materials", None),
            "check_vertex_colors": getattr(geometry, "check_vertex_colors", None),
            "check_internal_faces": getattr(geometry, "check_internal_faces", None),
            "check_watertight": getattr(geometry, "check_watertight", None),
            "check_zero_area_faces": getattr(geometry, "check_zero_area_faces", None),
            "check_zero_length_edges": getattr(geometry, "check_zero_length_edges", None),
            "check_uv_exists": getattr(uv, "check_uv_exists", None),
            "check_flipped_uvs": getattr(uv, "check_flipped_uvs", None),
            "check_texel_density": getattr(uv, "check_texel_density", None),
            "check_inverted_normals": getattr(geometry, "check_inverted_normals", None),
            "check_hard_edges": getattr(geometry, "check_hard_edges", None),
            "check_zero_area_uvs": getattr(uv, "check_zero_area_uvs", None),
            "check_triangulated": getattr(geometry, "check_triangulated", None),
            "check_frozen_transforms": getattr(transforms, "check_frozen_transforms", None),
            "check_negative_scale": getattr(transforms, "check_negative_scale", None),
            "check_missing_shader": getattr(materials, "check_missing_shader", None),
            "check_shader_naming": getattr(materials, "check_shader_naming", None),
            "check_complex_nodes": getattr(materials, "check_complex_nodes", None),
            "check_skin_weights": getattr(animation, "check_skin_weights", None),
            "check_animation_baked": getattr(animation, "check_animation_baked", None),
            "check_root_motion": getattr(animation, "check_root_motion", None),
            "check_constraints": getattr(animation, "check_constraints", None),
            "check_uv2_exists": getattr(baking, "check_uv2_exists", None),
            "check_uv2_validity": getattr(baking, "check_uv2_validity", None),
            "check_padding": getattr(baking, "check_padding", None),
            "check_light_leakage": getattr(baking, "check_light_leakage", None),
            "check_seams": getattr(baking, "check_seams", None),
            "check_texture_continuity": getattr(uv, "check_texture_continuity", None),
        }
        
        # Expose a public registry that dynamically wraps functions
        class RegistryWrapper:
            def __init__(self, raw_reg):
                self.raw_reg = raw_reg
            def __contains__(self, key):
                return key in self.raw_reg
            def __getitem__(self, key):
                return self.wrap(key)
                
            def wrap(self, func_name):
                func = self.raw_reg.get(func_name)
                if not func: return None
                
                # Import the formal contract here to avoid cyclic issues
                import sys
                try:
                    sys.path.append(r"i:\QYNTARA AI\maya")
                    from validation_contracts import ValidationResult, ValidationSeverity
                except ImportError:
                    pass
                
                def wrapper(scope_list=None):
                    import time
                    start = time.time()
                    try:
                        res = func(scope_list) if scope_list is not None else func()
                    except Exception as e:
                        # Produce a formal ERROR result
                        err_res = ValidationResult(func_name, func_name, "Legacy")
                        return err_res.mark_error(scope_list, str(e), (time.time()-start)*1000.0)
                        
                    # Build success/fail result
                    vr = ValidationResult(func_name, func_name, "Legacy")
                    
                    if not res: # Empty list = Passed!
                        return vr.mark_pass(scope_list, "Valid.", (time.time()-start)*1000.0)
                        
                    # It failed. Parse the old format into the new format.
                    failed_objs = []
                    evidence = []
                    for r in res:
                        if isinstance(r, dict):
                            failed_objs.append(r.get("object", "Unknown"))
                            evidence.append(r.get("issue", "Violation"))
                        else:
                            failed_objs.append(str(r))
                            
                    return vr.mark_fail(scope_list, list(set(failed_objs)), evidence, None, None, "Legacy Violation", (time.time()-start)*1000.0)
                
                return wrapper
                
        self.registry = RegistryWrapper(self._raw_registry)

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
                report["details"].append({
                    "rule_id": rule_id,
                    "rule_label": rule["label"],
                    "severity": "error",
                    "violations": [{"object": "GLOBAL", "issue": f"Validation Crashed: {str(e)}", "action": "Contact TD", "count": 1}],
                    "status": "FAILED"
                })
                report["summary"]["errors"] += 1
                report["summary"]["failed"] += 1
                
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
