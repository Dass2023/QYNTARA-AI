"""
QYNTARA NEXUS VALIDATION SYSTEM
Validation Contracts & Scope Resolution
---------------------------------------
This module strictly defines the ValidationResult data structure
to guarantee a trustworthy, deterministic verification output, eliminating
false positives caused by loose boolean/list returns.
"""
import time
from enum import Enum

try:
    from maya import cmds
except ImportError:
    cmds = None

class ValidationStatus(Enum):
    PASS = "PASS"        # Mathematically proven clean.
    FAIL = "FAIL"        # Proven violation of the rule.
    WARNING = "WARNING"  # Technically valid, but risky/sub-optimal.
    ERROR = "ERROR"      # Execution failed/crashed during analysis.
    SKIPPED = "SKIPPED"  # Rule deliberately bypassed.

class ValidationSeverity(Enum):
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"

class ValidationResult:
    """
    The immutable contract that every validation rule MUST return.
    """
    def __init__(self, rule_id, rule_name, category, severity=ValidationSeverity.CRITICAL):
        self.rule_id = rule_id
        self.rule_name = rule_name
        self.category = category
        self.severity = severity
        
        # Core State
        self.status = ValidationStatus.ERROR 
        self.scope = []
        self.object_names = []
        self.message = "Execution Failed / Uninitialized"
        
        # Forensic Data
        self.details = []
        self.actual_value = None
        self.expected_value = None
        self.evidence = []
        
        # Telemetry
        self.execution_time_ms = 0.0
        self.timestamp = time.time()
        self.maya_version = str(cmds.about(version=True)) if cmds else "Unknown"

    def mark_pass(self, scope, message="Valid.", execution_time=0.0):
        self.status = ValidationStatus.PASS
        self.scope = scope
        self.message = message
        self.execution_time_ms = execution_time
        return self

    def mark_fail(self, scope, failed_objects, evidence, expected, actual, message="Rule Violation Detected", execution_time=0.0):
        self.status = ValidationStatus.FAIL
        self.scope = scope
        self.object_names = failed_objects
        self.evidence = evidence
        self.expected_value = expected
        self.actual_value = actual
        self.message = message
        self.execution_time_ms = execution_time
        return self
        
    def mark_error(self, scope, error_msg, execution_time=0.0):
        self.status = ValidationStatus.ERROR
        self.scope = scope
        self.message = f"EXECUTION CRASH: {error_msg}"
        self.execution_time_ms = execution_time
        return self

    def to_dict(self):
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "status": self.status.value,
            "severity": self.severity.value,
            "failed_count": len(self.object_names),
            "affected_objects": self.object_names,
            "evidence": self.evidence,
            "message": self.message,
            "execution_time_ms": self.execution_time_ms
        }

class ScopeResolver:
    """
    Ensures safe, deterministic scope parsing for validation rules,
    preventing False Negatives caused by arbitrary component selections.
    """
    @staticmethod
    def resolve_to_transforms(raw_selection=None):
        if not cmds:
            return []
            
        if raw_selection is None:
            raw_selection = cmds.ls(sl=True, long=True) or []
            
        if not raw_selection:
            # Fallback to entire scene meshes
            meshes = cmds.ls(type='mesh', long=True) or []
            if not meshes:
                return []
            return list(set(cmds.listRelatives(meshes, parent=True, fullPath=True) or []))
            
        resolved = set()
        for item in raw_selection:
            # If component (e.g. pCube1.f[0])
            if "." in item:
                parent = item.split(".")[0]
                if cmds.nodeType(parent) == "transform":
                    resolved.add(parent)
                else:
                    parents = cmds.listRelatives(parent, parent=True, fullPath=True)
                    if parents: resolved.add(parents[0])
            else:
                # If shape
                if cmds.nodeType(item) in ["mesh", "nurbsCurve"]:
                    parents = cmds.listRelatives(item, parent=True, fullPath=True)
                    if parents: resolved.add(parents[0])
                elif cmds.nodeType(item) == "transform":
                    resolved.add(item)
                    
        return list(resolved)
