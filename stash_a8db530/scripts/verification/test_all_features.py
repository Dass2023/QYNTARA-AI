import subprocess
import os
import sys

def run_script(path):
    print(f"\n>>> Running: {os.path.basename(path)}")
    try:
        # We use the same python interpreter
        result = subprocess.run([sys.executable, path], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"--- [PASS] {os.path.basename(path)} ---")
            # print(result.stdout)
            return True
        else:
            print(f"--- [FAIL] {os.path.basename(path)} ---")
            print(result.stdout)
            print(result.stderr)
            return False
    except Exception as e:
        print(f"--- [ERROR] {e} ---")
        return False

def test_all():
    print("================================================================")
    print(" QYNTARA AI: COMPREHENSIVE SYSTEM-WIDE VERIFICATION (TEST ALL)")
    print("================================================================")
    
    scripts = [
        "i:/QYNTARA AI/scripts/verification/verify_complete_system.py",
        "i:/QYNTARA AI/scripts/verification/verify_all_tabs.py",
        "i:/QYNTARA AI/scripts/verification/verify_phase6_hardening.py",
        "i:/QYNTARA AI/scripts/verification/verify_backend_logic.py"
    ]
    
    results = []
    for s in scripts:
        if not os.path.exists(s):
            print(f"[SKIP] Script not found: {s}")
            continue
        results.append(run_script(s))
        
    print("\n================================================================")
    print(" FINAL SUMMARY")
    print("================================================================")
    passed = results.count(True)
    total = len(results)
    print(f" PASSED: {passed}/{total}")
    
    if passed == total:
        print("\n [STATUS] ALL SYSTEMS GO. QYNTARA IS PRODUCTION READY.")
    else:
        print("\n [STATUS] ISSUES DETECTED. CHECK FAILURES ABOVE.")
    print("================================================================")

if __name__ == "__main__":
    test_all()
