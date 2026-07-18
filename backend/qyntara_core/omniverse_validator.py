from .base import AbstractValidator, AssetContext, ValidationResult

class OmniverseValidator(AbstractValidator):
    """
    NVIDIA Omniverse / OpenUSD Validator.
    Checks for compliance with Omniverse Kit, Nucleus, and USD standards.
    """
    
    def validate(self, context: AssetContext):
        self.results = []
        
        # --- Core USD Checks ---
        self.run_check("USD Unit Scale Conformity", self._check_unit_scale, context)
        self.run_check("Up-Axis Alignment", self._check_up_axis, context)
        self.run_check("Prim Kind Metadata", self._check_prim_kind, context)
        
        # --- Nucleus Connectivity ---
        self.run_check("Nucleus Server Reachability", self._check_nucleus, context)
        
        # --- Material Compatibility ---
        self.run_check("MDL Material Compliance", self._check_mdl, context)
        
        return self.results

    def get_industry_name(self):
        return "omniverse"

    def _check_unit_scale(self, context):
        # Omniverse standard is meters or centimeters per unit.
        mpu = context.metadata.get("meters_per_unit", None)
        if mpu is None:
             return "WARNING", "Missing 'metersPerUnit' metadata. Simulation may be inaccurate.", {}, True
        
        if mpu not in [0.01, 1.0]:
             return "WARNING", f"Non-standard Unit Scale ({mpu}). Recommend 0.01 (cm) or 1.0 (m).", {}, False
        
        return "PASS", f"Unit Scale Valid ({mpu} m/unit).", {}, False

    def _check_up_axis(self, context):
        # Default is usually Y-Up in Maya/Unity, Z-Up in Unreal/Omniverse (often).
        axis = context.metadata.get("up_axis", "Y")
        if axis == "Z":
             return "PASS", "Z-Up Axis aligned with Engineering/Omniverse default.", {}, False
        return "WARNING", f"Asset is {axis}-Up. Omniverse Physics prefers Z-Up.", {}, True

    def _check_prim_kind(self, context):
        # USD 'kind' (component, subcomponent, assembly)
        kind = context.metadata.get("usd_kind", None)
        if not kind:
             return "WARNING", "Missing USD 'Kind' (e.g., component, assembly). Limits composition.", {}, False
        return "PASS", f"USD Kind set to '{kind}'.", {}, False

    def _check_nucleus(self, context):
        # Mock connection check
        if context.metadata.get("nucleus_connected", False):
            return "PASS", "Omniverse Nucleus Server Connected.", {}, False
        return "WARNING", "Nucleus Server not detected. Asset will be local-only.", {}, False

    def _check_mdl(self, context):
        # Material Definition Language
        shaders = context.metadata.get("shaders", [])
        non_mdl = [s for s in shaders if "mdl" not in s.lower()]
        if non_mdl:
            return "WARNING", f"Found {len(non_mdl)} non-MDL materials. May not render in RTX.", {}, True
        return "PASS", "All materials are MDL-compliant.", {}, False
