import logging

try:
    from maya import cmds
except ImportError:
    cmds = None

logger = logging.getLogger(__name__)

def check_scale(objects, expected=(1.0, 1.0, 1.0), tolerance=0.001):
    """
    Checks if objects have the expected scale.
    """
    violations = []
    if not cmds:
        return violations

    for obj in objects:
        scale = cmds.xform(obj, q=True, s=True, r=True) # relative scale
        if not scale:
            continue
            
        dx = abs(scale[0] - expected[0])
        dy = abs(scale[1] - expected[1])
        dz = abs(scale[2] - expected[2])
        
        if dx > tolerance or dy > tolerance or dz > tolerance:
            violations.append({
                "object": obj,
                "issue": "Incorrect Scale",
                "current_value": scale,
                "expected": expected
            })
    return violations

def check_pivot_center(objects, tolerance=0.001):
    """
    Checks if object pivot is at world origin (0,0,0).
    Useful for props that should be exported at origin.
    """
    violations = []
    if not cmds: return violations
    
    for obj in objects:
        rp = cmds.xform(obj, q=True, ws=True, rp=True)
        dist = (rp[0]**2 + rp[1]**2 + rp[2]**2)**0.5
        
        if dist > tolerance:
             violations.append({
                "object": obj,
                "issue": f"Pivot not at Origin (Offset: {dist:.2f})",
                "current_value": rp,
                "action": "Center to Origin / Reset",
                "count": 1
            })
    return violations

def check_frozen_transforms(objects, tolerance=0.001):
    """
    Checks if transforms are frozen (Translate=0,0,0; Rotate=0,0,0; Scale=1,1,1).
    Note: We typically only check Rotate and Scale for 'frozen'. Translate depends on position.
    But 'Frozen Transforms' usually implies identity matrix relative to parent if it's a prop at origin.
    Let's check Rotate and Scale specifically.
    """
    violations = []
    if not cmds: return violations
    
    for obj in objects:
        translation = cmds.xform(obj, q=True, t=True, os=True)
        rotation = cmds.xform(obj, q=True, ro=True, os=True)
        scale = cmds.xform(obj, q=True, s=True, r=True)
        
        # Check Translate
        if any(abs(t) > tolerance for t in translation):
            violations.append({
                "object": obj,
                "issue": "Non-Zero Translation (Not Frozen)",
                "current_value": f"Trans {translation}",
                "action": "Freeze Transformations",
                "count": 1
            })
            continue # Don't report twice

        # Check Rotate
        if any(abs(r) > tolerance for r in rotation):
            violations.append({
                "object": obj,
                "issue": "Non-Zero Rotation (Not Frozen)",
                "current_value": f"Rot {rotation}",
                "action": "Freeze Transformations",
                "count": 1
            })
            continue # Don't report twice
            
        # Check Scale (Separate from check_scale which might check for specific size? No, usually 1.0)
        if any(abs(s - 1.0) > tolerance for s in scale):
             violations.append({
                "object": obj,
                "issue": "Non-Unit Scale (Not Frozen)",
                "current_value": f"Scl {scale}",
                "action": "Freeze Transformations",
                "count": 1
            })
            
    return violations

def check_negative_scale(objects):
    """Checks for negative scale values."""
    violations = []
    if not cmds: return violations
    
    for obj in objects:
        scale = cmds.xform(obj, q=True, s=True, r=True)
        if any(s < 0 for s in scale):
             violations.append({
                "object": obj,
                "issue": "Negative Scale Detected",
                "current_value": scale,
                "action": "Freeze / Reset Scale",
                "count": 1
            })
    return violations

# --- Fixer Functions ---

def fix_transform_zero(objects):
    """Auto-fix: Freeze Transforms."""
    if not cmds: return
    for obj in objects:
        try: cmds.makeIdentity(obj, apply=True, t=1, r=1, s=1, n=0, pn=1)
        except: pass

def fix_reset_scale(objects):
    """Auto-fix: Reset Scale to 1,1,1 (Freeze)."""
    if not cmds: return
    for obj in objects:
        try:
             # Just freeze scale
             cmds.makeIdentity(obj, apply=True, s=1, n=0, pn=1)
        except: pass
