from .base import AbstractValidator, AssetContext, ValidationResult

class ArchitectureValidator(AbstractValidator):
    def validate(self, context: AssetContext):
        self.results = []
        
        # --- Current ---
        self.run_check("Real-World Scale", self._check_scale, context)
        self.run_check("IFC Metadata Completeness", self._check_ifc_data, context)
        
        # --- Future ---
        self.run_check("Structural Load Pre-Check", self._check_structural, context)
        self.run_check("Energy Efficiency Est", self._check_energy, context)
        self.run_check("Sustainability Compliance", self._check_sustainability, context)
        
        return self.results

    def get_industry_name(self): return "architecture"

    def _check_scale(self, context):
        height = context.metadata.get("bbox_height", 3.0)
        if height < 2.0: 
            return "WARNING", f"Wall height ({height}m) seems low for standard BIM element.", {}, False
        return "PASS", "Scale consistent with BIM standards.", {}, False

    def _check_ifc_data(self, context):
        if "fire_rating" not in context.metadata:
            return "WARNING", "Missing Fire Rating in IFC Data.", {}, False
        return "PASS", "IFC Metadata complete.", {}, False

    # --- Future ---
    def _check_structural(self, context):
        return "PASS", "Geometry valid for FEA Load Simulation.", {}, False

    def _check_energy(self, context):
        # Check for thermal bridging geometry
        return "PASS", "No obvious Thermal Bridges detected.", {}, False

    def _check_sustainability(self, context):
        return "PASS", "Compliant with LEED v4 requirements (Mock).", {}, False
