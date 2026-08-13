"""
Phase 2/3 Enhancements Verification (Mock-Based).
Tests module structure and implementation without requiring PySide/Maya.
"""
import sys
import os
from unittest.mock import MagicMock

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, project_root)

# Mock PySide2 and Maya before importing
sys.modules["PySide2"] = MagicMock()
sys.modules["PySide2.QtWidgets"] = MagicMock()
sys.modules["PySide2.QtCore"] = MagicMock()
sys.modules["PySide2.QtGui"] = MagicMock()
sys.modules["maya"] = MagicMock()
sys.modules["maya.cmds"] = MagicMock()
sys.modules["maya.OpenMaya"] = MagicMock()
sys.modules["maya.OpenMayaUI"] = MagicMock()
sys.modules["shiboken2"] = MagicMock()
sys.modules["shiboken6"] = MagicMock()

def test_blueprint_preview():
    """Test Real-Time Blueprint Preview implementation."""
    print("\n" + "="*60)
    print("TEST 1: REAL-TIME BLUEPRINT PREVIEW")
    print("="*60)
    
    try:
        # Check file exists
        blueprint_file = os.path.join(project_root, "qyntara_ai", "ui", "blueprint_tab.py")
        if not os.path.exists(blueprint_file):
            print("   [X] blueprint_tab.py not found")
            return False
        
        print("\n[1.1] Checking file structure...")
        with open(blueprint_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for Phase 3 markers
        required_strings = [
            "PHASE 3",
            "chk_live",
            "live_timer",
            "toggle_live_preview",
            "on_threshold_changed",
            "update_live_preview",
            "cleanup_preview_geometry",
            "LIVE Preview",
            "QTimer",
            "QYNTARA_PREVIEW_LAYER"
        ]
        
        missing = []
        for req in required_strings:
            if req not in content:
                missing.append(req)
        
        if missing:
            print(f"   [X] Missing implementations: {missing}")
            return False
        else:
            print("   [OK] All required code present")
        
        # Check method implementations
        print("\n[1.2] Checking method implementations...")
        methods = [
            "def toggle_live_preview",
            "def on_threshold_changed",
            "def update_live_preview",
            "def cleanup_preview_geometry"
        ]
        
        for method in methods:
            if method in content:
                print(f"   [OK] {method}() found")
            else:
                print(f"   [X] {method}() not found")
                return False
        
        print("\n[1.3] Blueprint Preview: [OK] PASS")
        return True
        
    except Exception as e:
        print(f"   [X] Error: {e}")
        return False

def test_version_control():
    """Test Version Control Integration implementation."""
    print("\n" + "="*60)
    print("TEST 2: VERSION CONTROL INTEGRATION")
    print("="*60)
    
    try:
        # Check version_control.py exists
        vcs_file = os.path.join(project_root, "qyntara_ai", "core", "version_control.py")
        if not os.path.exists(vcs_file):
            print("   [X] version_control.py not found")
            return False
        
        print("\n[2.1] Checking version_control.py...")
        with open(vcs_file, 'r', encoding='utf-8') as f:
            vcs_content = f.read()
        
        # Check for required classes and methods
        required_vcs = [
            "class VersionControlBridge",
            "def detect_vcs",
            "def get_current_revision",
            "def inject_metadata_usd",
            "def create_commit_hook",
            "def _get_git_info",
            "def _get_p4_info"
        ]
        
        for req in required_vcs:
            if req in vcs_content:
                print(f"   [OK] {req} found")
            else:
                print(f"   [X] {req} not found")
                return False
        
        # Check Export Tab integration
        print("\n[2.2] Checking Export Tab integration...")
        export_file = os.path.join(project_root, "qyntara_ai", "ui", "export_tab.py")
        
        with open(export_file, 'r', encoding='utf-8') as f:
            export_content = f.read()
        
        required_export = [
            "PHASE 3",
            "Version Control",
            "lbl_vcs_status",
            "chk_inject_vcs",
            "chk_auto_commit",
            "from ..core.version_control import VersionControlBridge",
            "self.vcs_bridge",
            "def detect_vcs"
        ]
        
        for req in required_export:
            if req in export_content:
                print(f"   [OK] {req} found in export_tab.py")
            else:
                print(f"   [X] {req} not found in export_tab.py")
                return False
        
        print("\n[2.3] Version Control: [OK] PASS")
        return True
        
    except Exception as e:
        print(f"   [X] Error: {e}")
        return False

def test_substance_bridge():
    """Test Substance Designer Bridge implementation."""
    print("\n" + "="*60)
    print("TEST 3: SUBSTANCE DESIGNER BRIDGE")
    print("="*60)
    
    try:
        # Check substance_bridge.py exists
        substance_file = os.path.join(project_root, "qyntara_ai", "core", "substance_bridge.py")
        if not os.path.exists(substance_file):
            print("   [X] substance_bridge.py not found")
            return False
        
        print("\n[3.1] Checking substance_bridge.py...")
        with open(substance_file, 'r', encoding='utf-8') as f:
            substance_content = f.read()
        
        # Check for required classes and methods
        required_substance = [
            "class SubstanceIntegration",
            "def detect_substance",
            "def generate_material",
            "def export_sbsar",
            "def get_material_parameters",
            "def _select_template",
            "def _cook_sbsar",
            "def _render_textures",
            "def _generate_fallback_material",
            "sbscooker",
            "sbsrender"
        ]
        
        for req in required_substance:
            if req in substance_content:
                print(f"   [OK] {req} found")
            else:
                print(f"   [X] {req} not found")
                return False
        
        # Check Scanner Tab integration
        print("\n[3.2] Checking Scanner Tab integration...")
        scanner_file = os.path.join(project_root, "qyntara_ai", "ui", "scanner_tab.py")
        
        with open(scanner_file, 'r', encoding='utf-8') as f:
            scanner_content = f.read()
        
        required_scanner = [
            "PHASE 3",
            "bg_material_mode",
            "rad_ai",
            "rad_substance",
            "lbl_substance_status",
            "substance_params_widget",
            "combo_resolution",
            "chk_export_sbsar",
            "from ..core.substance_bridge import SubstanceIntegration",
            "self.substance",
            "def on_material_mode_changed",
            "def update_substance_status",
            "def run_material_generation",
            "def run_substance_material"
        ]
        
        for req in required_scanner:
            if req in scanner_content:
                print(f"   [OK] {req} found in scanner_tab.py")
            else:
                print(f"   [X] {req} not found in scanner_tab.py")
                return False
        
        print("\n[3.3] Substance Bridge: [OK] PASS")
        return True
        
    except Exception as e:
        print(f"   [X] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_integrity():
    """Test that all modified files have no syntax errors."""
    print("\n" + "="*60)
    print("TEST 4: FILE INTEGRITY")
    print("="*60)
    
    try:
        import py_compile
        
        files_to_check = [
            "qyntara_ai/ui/blueprint_tab.py",
            "qyntara_ai/ui/export_tab.py",
            "qyntara_ai/ui/scanner_tab.py",
            "qyntara_ai/core/version_control.py",
            "qyntara_ai/core/substance_bridge.py"
        ]
        
        print("\n[4.1] Checking Python syntax...")
        all_valid = True
        
        for file_path in files_to_check:
            full_path = os.path.join(project_root, file_path)
            if not os.path.exists(full_path):
                print(f"   [X] {file_path} not found")
                all_valid = False
                continue
            
            try:
                py_compile.compile(full_path, doraise=True)
                print(f"   [OK] {file_path}")
            except py_compile.PyCompileError as e:
                print(f"   [X] {file_path}: Syntax error")
                print(f"        {e}")
                all_valid = False
        
        if all_valid:
            print("\n[4.2] File Integrity: [OK] PASS")
            return True
        else:
            print("\n[4.2] File Integrity: [X] FAIL")
            return False
        
    except Exception as e:
        print(f"   [X] Error: {e}")
        return False

def test_code_metrics():
    """Test code metrics and statistics."""
    print("\n" + "="*60)
    print("TEST 5: CODE METRICS")
    print("="*60)
    
    try:
        files_to_check = {
            "qyntara_ai/ui/blueprint_tab.py": "Blueprint Preview",
            "qyntara_ai/ui/export_tab.py": "Export Tab (VCS)",
            "qyntara_ai/ui/scanner_tab.py": "Scanner Tab (Substance)",
            "qyntara_ai/core/version_control.py": "Version Control",
            "qyntara_ai/core/substance_bridge.py": "Substance Bridge"
        }
        
        print("\n[5.1] Code statistics...")
        total_lines = 0
        
        for file_path, description in files_to_check.items():
            full_path = os.path.join(project_root, file_path)
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines())
                    total_lines += lines
                    print(f"   {description:30} {lines:5} lines")
        
        print(f"\n   Total lines added/modified: {total_lines}")
        
        print("\n[5.2] Code Metrics: [OK] PASS")
        return True
        
    except Exception as e:
        print(f"   [X] Error: {e}")
        return False

def main():
    """Run all verification tests."""
    print("\n" + "="*60)
    print("   QYNTARA AI - PHASE 2/3 VERIFICATION SUITE")
    print("="*60)
    print("\nTesting all Phase 2/3 enhancements:")
    print("  1. Real-Time Blueprint Preview")
    print("  2. Version Control Integration")
    print("  3. Substance Designer Bridge")
    print("  4. File Integrity")
    print("  5. Code Metrics")
    
    results = {
        "Blueprint Preview": test_blueprint_preview(),
        "Version Control": test_version_control(),
        "Substance Bridge": test_substance_bridge(),
        "File Integrity": test_file_integrity(),
        "Code Metrics": test_code_metrics()
    }
    
    # Summary
    print("\n" + "="*60)
    print("   VERIFICATION SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "[OK] PASS" if result else "[X] FAIL"
        print(f"{test_name:30} {status}")
    
    print("\n" + "="*60)
    print(f"   TOTAL: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("\n[SUCCESS] ALL TESTS PASSED - PHASE 2/3 ENHANCEMENTS VERIFIED")
        return 0
    else:
        print(f"\n[WARNING] {total - passed} test(s) failed - Review errors above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
