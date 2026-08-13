"""
Qyntara DCC Adapters
====================

DCC-specific translation layers for Qyntara Core Engine.

Supported DCCs:
    - Autodesk Maya (production-ready)
    - Autodesk 3ds Max (production-ready)
    - Blender (production-ready)

Author: Dass2023
License: MIT (Open-Core)
Version: 5.0.0
"""

__version__ = "5.0.0"

# Import adapters
HAS_MAYA = False
HAS_MAX = False
HAS_BLENDER = False

try:
    from .maya import MayaAdapter
    HAS_MAYA = True
except ImportError:
    pass

try:
    from .max import MaxAdapter
    HAS_MAX = True
except ImportError:
    pass

try:
    from .blender import BlenderAdapter
    HAS_BLENDER = True
except ImportError:
    pass

__all__ = []
if HAS_MAYA:
    __all__.append('MayaAdapter')
if HAS_MAX:
    __all__.append('MaxAdapter')
if HAS_BLENDER:
    __all__.append('BlenderAdapter')

