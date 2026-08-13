"""
Qyntara AI - Industry Validation Presets
12 industry-specific rule sets for 3D asset validation.

Standards Referenced:
  - Khronos Asset Creation Guidelines 2.0 (Gaming/XR)
  - OpenUSD Core Specification 1.0 (Film/VFX)
  - ISO 23247 / IEC 63278 (Industry 4.0 Digital Twin)
  - AS9100D / DO-178C (Aerospace)
  - FDA QMSR / ISO 13485 (Medical)
  - ISO/ASTM 52900 (3D Printing)
  - IFC 4.3 / LEED v4.1 (Architecture)
  - Shopify AR / Khronos 3D Commerce (E-Commerce)
  - URDF/SDF / Isaac Sim USD (Robotics)
  - EU Green Deal (Industry 5.0 Sustainability)
"""

# ──────────────────────────────────────────────────────────────
# Severity levels:  0 = Info,  1 = Warning,  2 = Error
# ──────────────────────────────────────────────────────────────

# Helper to build a rule entry
def _r(enabled=True, severity=2):
    return {"enabled": enabled, "severity": severity}


# ══════════════════════════════════════════════════════════════
#  Master list of ALL check IDs (used to build per-industry
#  presets by toggling enabled/disabled).
# ══════════════════════════════════════════════════════════════

ALL_CHECKS = [
    # --- Core (existing) ---
    "check_ngons", "check_triangles", "check_poles",
    "check_non_manifold", "check_lamina_faces", "check_zero_area",
    "check_hard_edges", "check_zero_length_edges", "check_missing_uvs",
    "check_history", "check_transforms", "check_layers", "check_shaders",
    "check_names", "check_trailing_numbers", "check_shape_names",
    "check_namespaces",

    # --- Gaming ---
    "check_poly_budget", "check_lod_chain", "check_draw_call_estimate",
    "check_texture_power_of_two", "check_texture_density",
    "check_degenerate_tris", "check_vertex_color_unused",
    "check_bone_count", "check_animation_fps", "check_collision_mesh",

    # --- Film / VFX ---
    "check_usd_compliance", "check_subdiv_ready", "check_render_normals",
    "check_material_assignments", "check_texture_resolution_film",
    "check_naming_convention_film", "check_world_scale",
    "check_hidden_geometry",

    # --- Automotive ---
    "check_digital_twin_ready", "check_simready_metadata",
    "check_cad_tolerance", "check_material_physical_props",
    "check_assembly_hierarchy", "check_weld_lines",
    "check_surface_continuity", "check_aerodynamic_mesh",

    # --- Architecture / BIM ---
    "check_real_world_scale", "check_bim_metadata",
    "check_floor_plan_valid", "check_wall_thickness_arch",
    "check_window_door_frames", "check_sustainability_leed",
    "check_daylight_mesh",

    # --- Medical ---
    "check_watertight_medical", "check_dimensional_accuracy",
    "check_dicom_metadata", "check_biocompatible_material",
    "check_sterilization_ready", "check_anatomical_orientation",
    "check_implant_wall_thickness",

    # --- Aerospace / Defense ---
    "check_master_model_integrity", "check_mesh_sensitivity",
    "check_pmi_data", "check_traceability_id",
    "check_classification_marking", "check_flight_safety_critical",
    "check_material_certification", "check_tolerance_stack",

    # --- XR / Metaverse ---
    "check_xr_file_size", "check_xr_draw_calls",
    "check_xr_triangle_budget", "check_xr_texture_memory",
    "check_gltf_compliance", "check_usdz_compliance",
    "check_pbr_materials", "check_realworld_scale_xr",
    "check_ktx2_textures",

    # --- E-Commerce ---
    "check_ecommerce_file_size", "check_ecommerce_poly_count",
    "check_product_accuracy", "check_texture_quality_ecom",
    "check_uv_no_overlap_ecom", "check_soft_hard_product",

    # --- Robotics ---
    "check_urdf_compatible", "check_collision_simplified",
    "check_inertia_properties", "check_joint_structure",
    "check_sensor_mounting", "check_physics_scale",
    "check_convex_decomposition",

    # --- Industry 4.0 ---
    "check_iot_metadata", "check_aas_compliance",
    "check_iot_polygon_limit", "check_streaming_ready",
    "check_predictive_maintenance", "check_plc_integration",

    # --- Industry 5.0 ---
    "check_carbon_footprint", "check_recyclability",
    "check_energy_consumption", "check_lifecycle_stage",
    "check_human_centric_design", "check_circular_economy",

    # --- 3D Printing ---
    "check_printable_watertight", "check_min_wall_thickness",
    "check_overhang_angles", "check_support_structures",
    "check_print_orientation", "check_intersecting_faces",
    "check_stl_errors", "check_print_resolution",
]


def _base_disabled():
    """Return dict with every check disabled."""
    return {c: _r(False, 1) for c in ALL_CHECKS}


def _enable(base, checks, severity=2):
    """Enable a list of checks in `base` at given severity."""
    for c in checks:
        base[c] = _r(True, severity)
    return base


# ══════════════════════════════════════════════════════════════
#  CORE CHECKS (always enabled in every preset)
# ══════════════════════════════════════════════════════════════
CORE_CHECKS = [
    "check_ngons", "check_non_manifold", "check_lamina_faces",
    "check_zero_area", "check_zero_length_edges", "check_names",
]


# ══════════════════════════════════════════════════════════════
#  PRESET DEFINITIONS
# ══════════════════════════════════════════════════════════════

def build_gaming_preset():
    r = _base_disabled()
    _enable(r, CORE_CHECKS, 2)
    _enable(r, [
        "check_triangles", "check_poles", "check_hard_edges",
        "check_missing_uvs", "check_history", "check_transforms",
        "check_poly_budget", "check_lod_chain", "check_draw_call_estimate",
        "check_texture_power_of_two", "check_texture_density",
        "check_degenerate_tris", "check_vertex_color_unused",
        "check_bone_count", "check_animation_fps", "check_collision_mesh",
    ], 2)
    _enable(r, ["check_trailing_numbers", "check_shape_names"], 1)
    return {
        "name": "Gaming",
        "version": "2.0",
        "description": "Game-ready assets (Khronos Guidelines 2.0, platform TRCs)",
        "icon": "gamepad",
        "rules": r,
    }


def build_film_vfx_preset():
    r = _base_disabled()
    _enable(r, CORE_CHECKS, 2)
    _enable(r, [
        "check_poles", "check_missing_uvs", "check_history",
        "check_transforms", "check_shaders",
        "check_usd_compliance", "check_subdiv_ready",
        "check_render_normals", "check_material_assignments",
        "check_texture_resolution_film", "check_naming_convention_film",
        "check_world_scale", "check_hidden_geometry",
    ], 2)
    _enable(r, ["check_triangles"], 1)  # tris are warning, not error
    return {
        "name": "Film / VFX",
        "version": "2.0",
        "description": "Render-ready assets (OpenUSD 1.0, studio pipelines)",
        "icon": "film",
        "rules": r,
    }


def build_automotive_preset():
    r = _base_disabled()
    _enable(r, CORE_CHECKS, 2)
    _enable(r, [
        "check_missing_uvs", "check_history", "check_transforms",
        "check_digital_twin_ready", "check_simready_metadata",
        "check_cad_tolerance", "check_material_physical_props",
        "check_assembly_hierarchy", "check_weld_lines",
        "check_surface_continuity", "check_aerodynamic_mesh",
    ], 2)
    _enable(r, ["check_world_scale", "check_real_world_scale"], 2)
    return {
        "name": "Automotive",
        "version": "2.0",
        "description": "Digital twin / simulation (ISO 23247, NVIDIA SimReady)",
        "icon": "car",
        "rules": r,
    }


def build_architecture_preset():
    r = _base_disabled()
    _enable(r, CORE_CHECKS, 2)
    _enable(r, [
        "check_missing_uvs", "check_history", "check_transforms",
        "check_real_world_scale", "check_bim_metadata",
        "check_floor_plan_valid", "check_wall_thickness_arch",
        "check_window_door_frames", "check_sustainability_leed",
        "check_daylight_mesh",
    ], 2)
    _enable(r, ["check_hidden_geometry", "check_world_scale"], 1)
    return {
        "name": "Architecture / BIM",
        "version": "2.0",
        "description": "BIM-compliant assets (IFC 4.3, LEED v4.1)",
        "icon": "building",
        "rules": r,
    }


def build_medical_preset():
    r = _base_disabled()
    _enable(r, CORE_CHECKS, 2)
    _enable(r, [
        "check_transforms",
        "check_watertight_medical", "check_dimensional_accuracy",
        "check_dicom_metadata", "check_biocompatible_material",
        "check_sterilization_ready", "check_anatomical_orientation",
        "check_implant_wall_thickness",
    ], 2)
    _enable(r, ["check_printable_watertight", "check_min_wall_thickness"], 2)
    return {
        "name": "Medical",
        "version": "2.0",
        "description": "FDA / surgical (ISO 13485, DICOM, FDA QMSR)",
        "icon": "medical",
        "rules": r,
    }


def build_aerospace_preset():
    r = _base_disabled()
    _enable(r, CORE_CHECKS, 2)
    _enable(r, [
        "check_missing_uvs", "check_history", "check_transforms",
        "check_master_model_integrity", "check_mesh_sensitivity",
        "check_pmi_data", "check_traceability_id",
        "check_classification_marking", "check_flight_safety_critical",
        "check_material_certification", "check_tolerance_stack",
    ], 2)
    _enable(r, ["check_world_scale", "check_cad_tolerance"], 2)
    return {
        "name": "Aerospace / Defense",
        "version": "2.0",
        "description": "Flight-critical assets (AS9100D, DO-178C)",
        "icon": "rocket",
        "rules": r,
    }


def build_xr_metaverse_preset():
    r = _base_disabled()
    _enable(r, CORE_CHECKS, 2)
    _enable(r, [
        "check_triangles", "check_missing_uvs", "check_history",
        "check_transforms",
        "check_xr_file_size", "check_xr_draw_calls",
        "check_xr_triangle_budget", "check_xr_texture_memory",
        "check_gltf_compliance", "check_usdz_compliance",
        "check_pbr_materials", "check_realworld_scale_xr",
        "check_ktx2_textures",
    ], 2)
    _enable(r, ["check_degenerate_tris", "check_texture_power_of_two"], 1)
    return {
        "name": "XR / Metaverse",
        "version": "2.0",
        "description": "Immersive assets (glTF 2.0, USDZ, Meta Quest, Apple Vision Pro)",
        "icon": "vr",
        "rules": r,
    }


def build_ecommerce_preset():
    r = _base_disabled()
    _enable(r, CORE_CHECKS, 2)
    _enable(r, [
        "check_missing_uvs", "check_history", "check_transforms",
        "check_ecommerce_file_size", "check_ecommerce_poly_count",
        "check_product_accuracy", "check_texture_quality_ecom",
        "check_uv_no_overlap_ecom", "check_soft_hard_product",
    ], 2)
    _enable(r, ["check_pbr_materials", "check_realworld_scale_xr"], 1)
    return {
        "name": "E-Commerce",
        "version": "2.0",
        "description": "Commerce-ready (Shopify AR, Khronos 3D Commerce)",
        "icon": "cart",
        "rules": r,
    }


def build_robotics_preset():
    r = _base_disabled()
    _enable(r, CORE_CHECKS, 2)
    _enable(r, [
        "check_history", "check_transforms",
        "check_urdf_compatible", "check_collision_simplified",
        "check_inertia_properties", "check_joint_structure",
        "check_sensor_mounting", "check_physics_scale",
        "check_convex_decomposition",
    ], 2)
    _enable(r, ["check_real_world_scale", "check_world_scale"], 2)
    return {
        "name": "Robotics / Simulation",
        "version": "2.0",
        "description": "Sim-ready (ROS URDF/SDF, NVIDIA Isaac Sim, Gazebo)",
        "icon": "robot",
        "rules": r,
    }


def build_industry40_preset():
    r = _base_disabled()
    _enable(r, CORE_CHECKS, 2)
    _enable(r, [
        "check_history", "check_transforms",
        "check_digital_twin_ready", "check_iot_metadata",
        "check_aas_compliance", "check_iot_polygon_limit",
        "check_streaming_ready", "check_predictive_maintenance",
        "check_plc_integration",
    ], 2)
    _enable(r, ["check_simready_metadata", "check_real_world_scale"], 1)
    return {
        "name": "Industry 4.0",
        "version": "2.0",
        "description": "Smart manufacturing (ISO 23247, IEC 63278 AAS, OPC UA)",
        "icon": "factory",
        "rules": r,
    }


def build_industry50_preset():
    r = _base_disabled()
    _enable(r, CORE_CHECKS, 2)
    _enable(r, [
        "check_history", "check_transforms",
        "check_carbon_footprint", "check_recyclability",
        "check_energy_consumption", "check_lifecycle_stage",
        "check_human_centric_design", "check_circular_economy",
    ], 2)
    _enable(r, [
        "check_digital_twin_ready", "check_sustainability_leed",
    ], 1)
    return {
        "name": "Industry 5.0",
        "version": "2.0",
        "description": "Sustainable manufacturing (EU Green Deal, circular economy)",
        "icon": "leaf",
        "rules": r,
    }


def build_printing3d_preset():
    r = _base_disabled()
    _enable(r, CORE_CHECKS, 2)
    _enable(r, [
        "check_transforms",
        "check_printable_watertight", "check_min_wall_thickness",
        "check_overhang_angles", "check_support_structures",
        "check_print_orientation", "check_intersecting_faces",
        "check_stl_errors", "check_print_resolution",
    ], 2)
    _enable(r, ["check_real_world_scale", "check_world_scale"], 2)
    return {
        "name": "3D Printing",
        "version": "2.0",
        "description": "Print-ready (ISO/ASTM 52900, FDM/SLA/SLS)",
        "icon": "printer",
        "rules": r,
    }


# ══════════════════════════════════════════════════════════════
#  PUBLIC API
# ══════════════════════════════════════════════════════════════

PRESET_BUILDERS = {
    "gaming":        build_gaming_preset,
    "film_vfx":      build_film_vfx_preset,
    "automotive":    build_automotive_preset,
    "architecture":  build_architecture_preset,
    "medical":       build_medical_preset,
    "aerospace":     build_aerospace_preset,
    "xr_metaverse":  build_xr_metaverse_preset,
    "ecommerce":     build_ecommerce_preset,
    "robotics":      build_robotics_preset,
    "industry_40":   build_industry40_preset,
    "industry_50":   build_industry50_preset,
    "printing_3d":   build_printing3d_preset,
}

PRESET_DISPLAY_ORDER = [
    ("gaming",        "Gaming"),
    ("film_vfx",      "Film / VFX"),
    ("automotive",    "Automotive"),
    ("architecture",  "Architecture / BIM"),
    ("medical",       "Medical"),
    ("aerospace",     "Aerospace / Defense"),
    ("xr_metaverse",  "XR / Metaverse"),
    ("ecommerce",     "E-Commerce"),
    ("robotics",      "Robotics / Simulation"),
    ("industry_40",   "Industry 4.0"),
    ("industry_50",   "Industry 5.0"),
    ("printing_3d",   "3D Printing"),
]


def get_preset(name):
    """Return a preset rule set by key name."""
    builder = PRESET_BUILDERS.get(name)
    if builder:
        return builder()
    return None


def get_all_preset_names():
    """Return ordered list of (key, display_name) tuples."""
    return list(PRESET_DISPLAY_ORDER)


def get_preset_count():
    """Total number of presets."""
    return len(PRESET_BUILDERS)


def get_total_check_count():
    """Total unique validation checks across all presets."""
    return len(ALL_CHECKS)


# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"[Presets] {get_preset_count()} industry presets loaded")
    print(f"[Presets] {get_total_check_count()} total validation checks")
    print()
    for key, display in PRESET_DISPLAY_ORDER:
        p = get_preset(key)
        enabled = sum(1 for v in p["rules"].values() if v["enabled"])
        print(f"  {display:25s}  {enabled:3d} checks enabled  |  {p['description']}")
