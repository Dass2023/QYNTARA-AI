"""
Qyntara AI Compute Layer
========================

AI-powered features for material synthesis and mesh optimization.

This is the commercial AI layer built on top  of the open-source Core Engine.

Modules:
    - material_synthesis: Base material generation classes
    - stable_diffusion_materials: Stable Diffusion integration
    - neural_mesh: GNN-based mesh optimization

Author: Dass2023
License: Commercial (requires Pro/Enterprise license)
Version: 5.0.0
"""

__version__ = '5.0.0'

# Check license on import (future feature)
# For now, all AI features are available for testing

from qyntara_ai.material_synthesis import MaterialSynthesizer, GPUWatchdog
from qyntara_ai.stable_diffusion_materials import StableDiffusionMaterialSynthesizer, quick_material
from qyntara_ai.neural_mesh import NeuralMeshOptimizer, FeatureDetector

__all__ = [
    'MaterialSynthesizer',
    'GPUWatchdog',
    'StableDiffusionMaterialSynthesizer',
    'quick_material',
    'NeuralMeshOptimizer',
    'FeatureDetector'
]
