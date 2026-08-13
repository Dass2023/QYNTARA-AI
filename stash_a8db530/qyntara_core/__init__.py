"""
Qyntara Core Engine
==================

DCC-Agnostic 3D Asset Pipeline Infrastructure

This is the stable core (Layer 1) that ALL platforms depend on.
API contract is frozen and guaranteed for 5+ years.

Platforms supported:
    - Autodesk Maya
    - Autodesk 3ds Max  
    - Blender
    - Unity (via C# SDK)
    - Unreal Engine (via C++ plugin)
    - Three.js (WebGPU)
    - SceneKit (visionOS)

Author: Dass2023
Website: https://github.com/Dass2023/Qyntara-AI
License: MIT (Open-Core)
Version: 5.0.0
"""

__version__ = "5.0.0"
__author__ = "Dass2023"
__license__ = "MIT"

# Stable API exports - NEVER change these for backward compatibility
from .datatypes import (
    QMesh,
    QMaterial,
    QCamera,
    QLight,
    QScene,
    TopologyType
)

from .geometry import (
    MeshProcessor,
    MeshStats
)

__all__ = [
    # Data types
    'QMesh',
    'QMaterial',
    'QCamera',
    'QLight',
    'QScene',
    'TopologyType',
    
    # Processing
    'MeshProcessor',
    'MeshStats',
    
    # Version info
    '__version__',
    '__author__',
    '__license__',
]


def get_version() -> str:
    """Get Qyntara Core Engine version"""
    return __version__


def check_compatibility(required_version: str) -> bool:
    """
    Check if current version is compatible with required version.
    
    Args:
        required_version: Minimum required version (e.g., "5.0.0")
    
    Returns:
        True if compatible
    
    Example:
        >>> from qyntara_core import check_compatibility
        >>> if not check_compatibility("5.0.0"):
        ...     raise RuntimeError("Qyntara Core 5.0.0+ required")
    """
    from packaging import version
    return version.parse(__version__) >= version.parse(required_version)
