from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import time

@dataclass
class ValidationResult:
    """Standardized output for any validation check."""
    check_name: str
    status: str  # "PASS", "FAIL", "WARNING"
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    auto_fix_available: bool = False
    execution_time_ms: float = 0.0

@dataclass
class AssetContext:
    """Context for the asset being validated."""
    file_path: str
    asset_type: str = "mesh"  # mesh, scene, texture
    metadata: Dict[str, Any] = field(default_factory=dict)
    geometry_fingerprint: Optional[str] = None

class AbstractValidator(ABC):
    """Base class for all Industry-Specific Validators."""
    
    def __init__(self):
        self.results: List[ValidationResult] = []

    def run_check(self, name: str, check_func, *args, **kwargs):
        """Wrapper to execute a check and measure performance."""
        start = time.perf_counter()
        try:
            status, msg, details, can_fix = check_func(*args, **kwargs)
        except Exception as e:
            status, msg, details, can_fix = "FAIL", f"Exception: {str(e)}", {}, False
        
        duration = (time.perf_counter() - start) * 1000
        
        result = ValidationResult(
            check_name=name,
            status=status,
            message=msg,
            details=details,
            auto_fix_available=can_fix,
            execution_time_ms=duration
        )
        self.results.append(result)
        return result

    @abstractmethod
    def validate(self, context: AssetContext) -> List[ValidationResult]:
        """Main entry point for validation."""
        pass

    @abstractmethod
    def get_industry_name(self) -> str:
        """Returns string ID of the industry (e.g., 'gaming')."""
        pass
