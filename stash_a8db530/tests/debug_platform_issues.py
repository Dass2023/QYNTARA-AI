"""
Qyntara AI - Platform Debugging Utility
=======================================

Diagnoses platform-specific issues and provides troubleshooting guidance.

Usage:
    python tests/debug_platform_issues.py
    python tests/debug_platform_issues.py --platform maya
    python tests/debug_platform_issues.py --check-all

Author: Dass2023
Version: 5.0.0
"""

import sys
import os
import platform
import subprocess
from pathlib import Path
from typing import Dict, List

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class PlatformDebugger:
    """Debug platform-specific issues"""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.info = []
    
    def log_issue(self, message: str):
        """Log an issue"""
        self.issues.append(message)
        print(f"[X] ISSUE: {message}")
    
    def log_warning(self, message: str):
        """Log a warning"""
        self.warnings.append(message)
        print(f"[!] WARNING: {message}")
    
    def log_info(self, message: str):
        """Log info"""
        self.info.append(message)
        print(f"[i] INFO: {message}")
    
    def check_python_environment(self):
        """Check Python environment"""
        print("\n" + "=" * 60)
        print("PYTHON ENVIRONMENT")
        print("=" * 60)
        
        # Python version
        py_version = sys.version
        self.log_info(f"Python version: {py_version}")
        
        major, minor = sys.version_info[:2]
        if major < 3 or (major == 3 and minor < 8):
            self.log_warning(f"Python {major}.{minor} detected. Qyntara requires Python 3.8+")
        
        # Platform
        self.log_info(f"Platform: {platform.system()} {platform.release()}")
        self.log_info(f"Architecture: {platform.machine()}")
        
        # Virtual environment
        in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        if in_venv:
            self.log_info(f"Virtual environment: {sys.prefix}")
        else:
            self.log_warning("Not running in a virtual environment")
    
    def check_dependencies(self):
        """Check required dependencies"""
        print("\n" + "=" * 60)
        print("DEPENDENCIES")
        print("=" * 60)
        
        required = {
            "numpy": "1.19.0",
            "packaging": "20.0"
        }
        
        optional = {
            "torch": "2.0.0",
            "diffusers": "0.20.0",
            "transformers": "4.30.0",
            "usd-core": "22.11"
        }
        
        # Check required
        for package, min_version in required.items():
            try:
                mod = __import__(package)
                version = getattr(mod, '__version__', 'unknown')
                self.log_info(f"[OK] {package}: {version}")
            except ImportError:
                self.log_issue(f"Required package missing: {package} (>= {min_version})")
        
        # Check optional
        for package, min_version in optional.items():
            try:
                if package == "usd-core":
                    package_import = "pxr"
                else:
                    package_import = package
                
                mod = __import__(package_import)
                version = getattr(mod, '__version__', 'unknown')
                self.log_info(f"[OK] {package}: {version}")
            except ImportError:
                self.log_warning(f"Optional package missing: {package} (>= {min_version})")
    
    def check_gpu(self):
        """Check GPU availability"""
        print("\n" + "=" * 60)
        print("GPU STATUS")
        print("=" * 60)
        
        # Check PyTorch CUDA
        try:
            import torch
            if torch.cuda.is_available():
                self.log_info(f"✅ CUDA available: {torch.cuda.get_device_name(0)}")
                self.log_info(f"   CUDA version: {torch.version.cuda}")
                self.log_info(f"   GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
            else:
                self.log_warning("CUDA not available. AI features will run on CPU (slower)")
        except ImportError:
            self.log_warning("PyTorch not installed. AI features not available")
        
        # Check Metal (macOS)
        if platform.system() == "Darwin":
            try:
                import torch
                if torch.backends.mps.is_available():
                    self.log_info("✅ Metal (MPS) available for GPU acceleration")
                else:
                    self.log_warning("Metal (MPS) not available")
            except:
                pass
    
    def check_maya(self):
        """Check Maya environment"""
        print("\n" + "=" * 60)
        print("MAYA ENVIRONMENT")
        print("=" * 60)
        
        try:
            import maya.cmds as cmds
            import maya.standalone
            
            self.log_info("✅ Maya Python API available")
            
            # Try to initialize standalone
            try:
                maya.standalone.initialize()
                self.log_info("✅ Maya standalone initialized")
                
                # Check Maya version
                version = cmds.about(version=True)
                self.log_info(f"   Maya version: {version}")
            except:
                self.log_warning("Maya standalone already initialized or not available")
            
            # Check adapter
            try:
                from qyntara_dcc.maya import MayaAdapter
                self.log_info("✅ Qyntara Maya adapter loaded")
            except ImportError as e:
                self.log_issue(f"Failed to load Maya adapter: {e}")
        
        except ImportError:
            self.log_warning("Maya not available (expected if not running in Maya)")
    
    def check_max(self):
        """Check 3ds Max environment"""
        print("\n" + "=" * 60)
        print("3DS MAX ENVIRONMENT")
        print("=" * 60)
        
        try:
            import MaxPlus
            self.log_info("✅ 3ds Max Python API available")
            
            # Check adapter
            try:
                from qyntara_dcc.max import MaxAdapter
                self.log_info("✅ Qyntara Max adapter loaded")
            except ImportError as e:
                self.log_issue(f"Failed to load Max adapter: {e}")
        
        except ImportError:
            self.log_warning("3ds Max not available (expected if not running in Max)")
    
    def check_blender(self):
        """Check Blender environment"""
        print("\n" + "=" * 60)
        print("BLENDER ENVIRONMENT")
        print("=" * 60)
        
        try:
            import bpy
            self.log_info("✅ Blender Python API available")
            
            # Check Blender version
            version = bpy.app.version_string
            self.log_info(f"   Blender version: {version}")
            
            # Check adapter
            try:
                from qyntara_dcc.blender import BlenderAdapter
                self.log_info("✅ Qyntara Blender adapter loaded")
            except ImportError as e:
                self.log_issue(f"Failed to load Blender adapter: {e}")
        
        except ImportError:
            self.log_warning("Blender not available (expected if not running in Blender)")
    
    def check_core_engine(self):
        """Check core engine"""
        print("\n" + "=" * 60)
        print("CORE ENGINE")
        print("=" * 60)
        
        try:
            from qyntara_core import QMesh, QMaterial, QScene
            self.log_info("✅ Core datatypes loaded")
        except ImportError as e:
            self.log_issue(f"Failed to load core datatypes: {e}")
        
        try:
            from qyntara_core.geometry import MeshProcessor, MeshStats
            self.log_info("✅ Geometry processing loaded")
        except ImportError as e:
            self.log_issue(f"Failed to load geometry processing: {e}")
        
        try:
            from qyntara_core.io import USDConverter, GLTFConverter, FBXConverter, OBJConverter
            self.log_info("✅ Format converters loaded")
        except ImportError as e:
            self.log_issue(f"Failed to load format converters: {e}")
    
    def check_ai_layer(self):
        """Check AI compute layer"""
        print("\n" + "=" * 60)
        print("AI COMPUTE LAYER")
        print("=" * 60)
        
        try:
            from qyntara_ai import MaterialSynthesizer, GPUWatchdog
            self.log_info("✅ AI base classes loaded")
        except ImportError as e:
            self.log_issue(f"Failed to load AI base classes: {e}")
        
        try:
            from qyntara_ai.stable_diffusion_materials import StableDiffusionMaterialSynthesizer
            self.log_info("✅ Stable Diffusion integration loaded")
        except ImportError as e:
            self.log_warning(f"Stable Diffusion not available: {e}")
        
        try:
            from qyntara_ai.neural_mesh import NeuralMeshOptimizer
            self.log_info("✅ Neural mesh optimization loaded")
        except ImportError as e:
            self.log_warning(f"Neural mesh optimization not available: {e}")
    
    def print_summary(self):
        """Print diagnostic summary"""
        print("\n" + "=" * 60)
        print("DIAGNOSTIC SUMMARY")
        print("=" * 60)
        print(f"Issues:   {len(self.issues)}")
        print(f"Warnings: {len(self.warnings)}")
        print(f"Info:     {len(self.info)}")
        print("=" * 60)
        
        if self.issues:
            print("\n❌ CRITICAL ISSUES:")
            for issue in self.issues:
                print(f"  • {issue}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        if not self.issues and not self.warnings:
            print("\n✅ NO ISSUES DETECTED")
        
        print("\n" + "=" * 60)
        print("TROUBLESHOOTING TIPS")
        print("=" * 60)
        
        if self.issues or self.warnings:
            print("\n1. Install missing dependencies:")
            print("   pip install -e \".[all]\"")
            print("\n2. For AI features, install PyTorch:")
            print("   pip install torch torchvision torchaudio")
            print("\n3. For USD support:")
            print("   pip install usd-core")
            print("\n4. Run tests to verify:")
            print("   python tests/test_all_platforms.py")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Qyntara AI Platform Debugger")
    parser.add_argument("--platform", choices=["maya", "max", "blender", "all"],
                       help="Specific platform to check")
    parser.add_argument("--check-all", action="store_true",
                       help="Check all platforms and components")
    
    args = parser.parse_args()
    
    debugger = PlatformDebugger()
    
    print("\n" + "=" * 60)
    print("QYNTARA AI - PLATFORM DEBUGGER v5.0.0")
    print("=" * 60)
    
    # Always check basics
    debugger.check_python_environment()
    debugger.check_dependencies()
    debugger.check_gpu()
    debugger.check_core_engine()
    debugger.check_ai_layer()
    
    # Platform-specific checks
    if args.check_all or args.platform in ["maya", "all", None]:
        debugger.check_maya()
    
    if args.check_all or args.platform in ["max", "all", None]:
        debugger.check_max()
    
    if args.check_all or args.platform in ["blender", "all", None]:
        debugger.check_blender()
    
    # Print summary
    debugger.print_summary()


if __name__ == "__main__":
    main()
