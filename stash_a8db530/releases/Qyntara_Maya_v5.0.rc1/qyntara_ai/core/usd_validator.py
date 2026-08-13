import logging
import os

try:
    from pxr import Usd, UsdGeom, UsdShade, Sdf
    USD_AVAILABLE = True
except ImportError:
    USD_AVAILABLE = False

logger = logging.getLogger(__name__)

class USDValidator:
    """
    Validates Universal Scene Description (.usd, .usdz, .usda) files directly.
    Bypasses Maya Import for speed.
    """
    
    def __init__(self):
        pass

    def validate_file(self, file_path):
        """
        Opens a USD stage and runs checks.
        Returns a list of issues.
        """
        issues = []
        if not USD_AVAILABLE:
            issues.append({"severity": "Error", "message": "USD Libraries (pxr) not found in this Maya environment."})
            return issues

        if not os.path.exists(file_path):
            issues.append({"severity": "Error", "message": f"File not found: {file_path}"})
            return issues

        try:
            # Open Stage
            stage = Usd.Stage.Open(file_path)
            if not stage:
                issues.append({"severity": "Error", "message": "Could not open USD Stage (Corrupt or Invalid)."})
                return issues

            # Traverse Prims
            count = 0
            for prim in stage.Traverse():
                count += 1
                
                # Rule 1: Empty Prims (Zombie Nodes)
                if not prim.GetTypeName(): 
                    # Usually 'Def' or 'Over' without type is okay for hierarchy, but check leaf
                    pass 

                # Rule 2: Geometry Checks
                if prim.IsA(UsdGeom.Mesh):
                    # Check Material Binding
                    binding_api = UsdShade.MaterialBindingAPI(prim)
                    mat = binding_api.ComputeBoundMaterial()[0]
                    if not mat:
                        issues.append({
                            "severity": "Warning", 
                            "message": f"Mesh missing material: {prim.GetPath()}",
                            "object": str(prim.GetPath())
                        })
                        
                    # Check Subsets (Face assignments)
                    # (Advanced check omitted for prototype)

            issues.append({"severity": "Info", "message": f"Scanned {count} Prims in USD Stage."})
            
        except Exception as e:
            issues.append({"severity": "Critical", "message": f"USD Validation Crashed: {e}"})
            
        return issues

    def mock_validate(self, file_path):
        """ Fallback for when pxr is missing but we want to show UI flow. """
        return [
            {"severity": "Info", "message": f"Simulated check for {os.path.basename(file_path)}"},
            {"severity": "Warning", "message": "/World/Geo/Chair01 has no material binding."},
            {"severity": "Pass", "message": "Schema Validation OK."}
        ]
