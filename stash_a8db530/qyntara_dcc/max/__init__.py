"""
Qyntara DCC Adapters - 3ds Max Integration
==========================================

3ds Max-specific integration for Qyntara Core Engine.

Author: Dass2023
License: MIT (Open-Core)
Version: 5.0.0
"""

from .adapter import MaxAdapter, export_selected_mesh, import_mesh

__all__ = [
    'MaxAdapter',
    'export_selected_mesh',
    'import_mesh',
]
