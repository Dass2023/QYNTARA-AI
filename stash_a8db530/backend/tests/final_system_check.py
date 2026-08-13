import subprocess
import sys
import os
import time

def run_test(script_name):
    print(f"\n[EXEC] Running Test: {script_name}...")
    start_time = time.time()
    result = subprocess.run([sys.executable, script_name], capture_output=True, text=True)
    duration = time.time() - start_time
    
    if result.returncode == 0:
        print(f"[PASS] ({duration:.2f}s)")
        return True, result.stdout
    else:
        print(f"[FAIL] ({duration:.2f}s)")
        print("--- Output ---")
        print(result.stdout)
        print("--- Error ---")
        print(result.stderr)
        return False, result.stderr

def main():
    print("========================================")
    print("   QYNTARA AI: FINAL SYSTEM CHECK")
    print("   Target: Start-to-End Verification")
    print("========================================")
    
    base_path = os.path.join("backend", "tests")
    
    # 1. Validation Logic (Future Rules)
    v_pass, v_log = run_test(os.path.join(base_path, "test_future_validation.py"))
    
    # 2. Auto-Fix Logic (Fixit)
    f_pass, f_log = run_test(os.path.join(base_path, "test_fixit.py"))
    
    print("\n========================================")
    print("   FINAL VERIFICATION REPORT")
    print("========================================")
    
    all_passed = v_pass and f_pass
    
    print(f"1. Validation Rules (12 Industries): {'[PASS]' if v_pass else '[FAIL]'}")
    print(f"2. Auto-Repair Engine (Fixit):       {'[PASS]' if f_pass else '[FAIL]'}")
    
    if all_passed:
        print("\n*** SYSTEM STATUS: GREEN (Ready for Launch) ***")
        sys.exit(0)
    else:
        print("\n!!! SYSTEM STATUS: RED (Verification Failed) !!!")
        sys.exit(1)

if __name__ == "__main__":
    main()
