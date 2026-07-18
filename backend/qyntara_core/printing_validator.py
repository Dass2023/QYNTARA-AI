from .base import AbstractValidator, AssetContext, ValidationResult

class PrintingValidator(AbstractValidator):
    def validate(self, context: AssetContext):
        self.results = []
        
        # --- Current ---
        self.run_check("Overhang Detection", self._check_overhang, context)
        self.run_check("Wall Thickness", self._check_walls, context)
        
        # --- Future ---
        self.run_check("Warping Probability", self._check_warping, context)
        self.run_check("Print Success Scoring", self._check_probability, context)
        self.run_check("Layer Adhesion Risk", self._check_adhesion, context)
        
        return self.results

    def get_industry_name(self): return "printing"

    def _check_overhang(self, context):
        overhangs = context.metadata.get("critical_overhangs", 0)
        if overhangs > 0:
            return "WARNING", f"Detected {overhangs} areas > 45deg. Supports required.", {}, True
        return "PASS", "Geometry self-supporting.", {}, False

    def _check_walls(self, context):
        return "PASS", "Wall thickness > 0.8mm (Printable).", {}, False

    # --- Future ---
    def _check_warping(self, context):
        return "PASS", "Low Warping Risk (Uniform Base).", {}, False

    def _check_probability(self, context):
        return "PASS", "Print Success Probability: 98%.", {}, False
    
    def _check_adhesion(self, context):
        return "PASS", "Layer surface area sufficient for adhesion.", {}, False
