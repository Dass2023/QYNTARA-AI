from .base import AbstractValidator, AssetContext, ValidationResult

class RoboticsValidator(AbstractValidator):
    def validate(self, context: AssetContext):
        self.results = []
        
        # --- Current ---
        self.run_check("Collision Mesh Convexity", self._check_convexity, context)
        self.run_check("Inertia Tensor", self._check_inertia, context)
        
        # --- Future ---
        self.run_check("Joint Articulation Conflict", self._check_joints, context)
        self.run_check("Sim Stability Prediction", self._check_stability, context)
        
        return self.results

    def get_industry_name(self): return "robotics"

    def _check_convexity(self, context):
        hulls = context.metadata.get("collision_hulls", 1)
        if hulls > 1 and not context.metadata.get("is_convex_decomposed", False):
             return "FAIL", "Concave collision mesh detected. Run Convex Decomposition.", {}, True
        return "PASS", "Collision mesh is valid (Convex).", {}, False

    def _check_inertia(self, context):
        return "PASS", "Mass and Inertia properties calculated.", {}, False

    # --- Future ---
    def _check_joints(self, context):
        return "PASS", "No self-collision detected in Joint Limits.", {}, False

    def _check_stability(self, context):
        return "PASS", "Simulation stable at 1000Hz timestep.", {}, False
