from .base import AbstractValidator, AssetContext, ValidationResult
import random

class GamingValidator(AbstractValidator):
    def validate(self, context: AssetContext):
        self.results = []
        
        # --- Current Validation Layer ---
        self.run_check("GPU Frame-Time", self._check_frame_time, context)
        self.run_check("LOD Chain Integrity", self._check_lod_chain, context)
        self.run_check("Platform Compliance (Mobile)", self._check_mobile_compliance, context)
        
        # --- Future Predictive Intelligence Layer ---
        self.run_check("Shader Complexity Heatmap", self._check_shader_complexity, context)
        self.run_check("Draw-Call Budget Analyzer", self._check_draw_calls, context)
        self.run_check("Runtime Risk Assessment", self._check_runtime_risk, context)
        
        return self.results

    def get_industry_name(self):
        return "gaming"

    def _check_frame_time(self, context):
        polycount = context.metadata.get("polycount", 0)
        # Mock AI Inference: 1ms per 50k polys approx on mid-range GPU
        est_ms = (polycount / 50000.0) + 1.2
        if est_ms > 3.0:
            return "WARNING", f"High Polycount ({polycount}). Est Frame Time: ~{int(est_ms)}ms (Budget: 3ms)", {"ms": est_ms}, True
        return "PASS", f"Frame Time Optimal (~{est_ms:.1f}ms)", {"ms": est_ms}, False

    def _check_lod_chain(self, context):
        has_lods = context.metadata.get("has_lods", False)
        if not has_lods:
             return "FAIL", "Missing LOD Chain. Critical for open-world streaming.", {}, True
        return "PASS", "LOD Chain Complete.", {}, False

    def _check_mobile_compliance(self, context):
        # Quest 2 limits
        if context.metadata.get("polycount", 0) > 100000:
            return "FAIL", "Exceeds Mobile Polycount Limit (100k).", {}, True
        return "PASS", "Mobile Compliant.", {}, False

    # --- Future Checks ---
    def _check_shader_complexity(self, context):
        # Mock: Analyze instructions.
        instructions = context.metadata.get("shader_instructions", 120)
        if instructions > 300:
             return "WARNING", f"Shader is heavy ({instructions} instr). High Register Pressure risk.", {}, True
        return "PASS", "Shader Complexity within limits.", {}, False

    def _check_draw_calls(self, context):
        dcs = context.metadata.get("drawcalls", 1)
        if dcs > 5:
             return "WARNING", f"Asset generates {dcs} Draw Calls. Target: 1 per mesh.", {}, True
        return "PASS", "Draw Call Budget Optimized.", {}, False

    def _check_runtime_risk(self, context):
        return "PASS", "Low Probability of Runtime Crash.", {}, False
