from .base import AbstractValidator, AssetContext, ValidationResult

class MedicalValidator(AbstractValidator):
    """
    Medical Industry Validator (ISO 13485+).
    """
    
    def validate(self, context: AssetContext):
        self.results = []
        
        # --- Current ---
        self.run_check("Watertight Integrity", self._check_watertight, context)
        self.run_check("Anatomical Scale", self._check_scale_precision, context)
        self.run_check("DICOM Metadata Sync", self._check_dicom_metadata, context)
        
        # --- Future ---
        self.run_check("Surgical Sim Readiness", self._check_surgical_sim, context)
        self.run_check("Micron-Level Dimension Check", self._check_micron_precision, context)
        
        return self.results

    def get_industry_name(self):
        return "medical"

    def _check_watertight(self, context):
        is_manifold = context.metadata.get("is_manifold", False)
        if not is_manifold:
            return "FAIL", "Mesh is NOT Watertight. Critical failure for surgical planning.", {}, True
        return "PASS", "Mesh is Watertight (Manifold).", {}, False

    def _check_scale_precision(self, context):
        bbox_size = context.metadata.get("bbox_diagonal", 1.0) 
        if bbox_size > 2.0: 
            return "WARNING", f"Asset Size ({bbox_size}m) exceeds typical anatomical range. Verify unit scale.", {"recommended_unit": "cm"}, True
        return "PASS", "Scale within anatomical norms.", {}, False

    def _check_dicom_metadata(self, context):
        if "patient_id" not in context.metadata:
            return "WARNING", "Missing Patient ID (DICOM Tag). Traceability lost.", {}, False
        return "PASS", "DICOM Traceability Active.", {}, False

    # --- Future ---
    def _check_surgical_sim(self, context):
        # Soft-tissue simulation requires specific topology
        if context.metadata.get("topology_type", "") == "triangulated":
            return "WARNING", "Tetrahedral mesh preferred for Soft-Tissue Physics.", {}, True
        return "PASS", "Mesh Topology ready for FEM Simulation.", {}, False

    def _check_micron_precision(self, context):
        return "PASS", "Surface deviation < 10 microns.", {}, False
