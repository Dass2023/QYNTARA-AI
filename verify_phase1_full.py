"""
Full Phase 1 Auth Verification — verify_phase1_full.py
Runs all 4 Phase 1 checks against a real uvicorn server in a fully installed environment.
No mocks or stubs.
"""
import sys, os, time, json, threading, subprocess, base64
import requests

# Config
TEST_ADMIN_KEY = "phase1-full-verification-key"
TEST_SECRET    = "phase1-full-test-secret"
PORT  = 8766
BASE  = f"http://localhost:{PORT}"
SEP   = "=" * 60

os.environ["ADMIN_KEY"] = TEST_ADMIN_KEY
os.environ["SECRET_KEY"] = TEST_SECRET
sys.path.insert(0, os.getcwd())

# ─────────────────────────────────────────────────────────────────────────────
# CHECK 1 — RuntimeError when ADMIN_KEY is absent
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{SEP}")
print("CHECK 1: RuntimeError when ADMIN_KEY is not set")
print(SEP)

env_no_key = {k: v for k, v in os.environ.items() if k != "ADMIN_KEY"}
env_no_key["PYTHONPATH"] = os.getcwd()

check1_script = """
import sys, os
import dotenv
dotenv.load_dotenv = lambda *a, **kw: False
import backend.main
"""

with open("temp_check1.py", "w") as f:
    f.write(check1_script)

result = subprocess.run(
    [sys.executable, "temp_check1.py"],
    capture_output=True, text=True, cwd=os.getcwd(), env=env_no_key
)
stderr = result.stderr.strip()

if result.returncode != 0 and "RuntimeError" in stderr and "ADMIN_KEY" in stderr:
    print("RuntimeError lines from stderr:")
    for l in stderr.splitlines():
        print(f"  {l}")
    print("CHECK 1 PASSED")
else:
    print(f"CHECK 1 FAILED")
    print(f"Return code: {result.returncode}")
    print(f"Full stderr:\n{stderr}")

os.remove("temp_check1.py")

# ─────────────────────────────────────────────────────────────────────────────
# Start Server for Checks 2, 3, 4
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{SEP}")
print("Starting real uvicorn server...")
import backend.main as _m
import uvicorn
app = _m.app

cfg = uvicorn.Config(app, host="127.0.0.1", port=PORT, log_level="error")
server = uvicorn.Server(cfg)
threading.Thread(target=server.run, daemon=True).start()

for _ in range(30):
    try:
        requests.get(f"{BASE}/stats", timeout=1)
        break
    except Exception:
        time.sleep(1)
else:
    print("FATAL: server did not start"); sys.exit(1)

# ─────────────────────────────────────────────────────────────────────────────
# CHECK 2 — Server boots with ADMIN_KEY set
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{SEP}")
print("CHECK 2: Server boots with ADMIN_KEY set")
print(SEP)

r = requests.get(f"{BASE}/stats", timeout=5)
print(f"HTTP Status : {r.status_code}")
if r.status_code in (200, 401, 403, 422):
    print("CHECK 2 PASSED")
else:
    print(f"CHECK 2 FAILED")

# ─────────────────────────────────────────────────────────────────────────────
# CHECK 3 — GET /stats with NO token -> 401
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{SEP}")
print("CHECK 3: GET /stats with no Bearer token -> expect 401")
print(SEP)

r = requests.get(f"{BASE}/stats", timeout=5)
print(f"HTTP Status : {r.status_code}")
print(f"Response    : {r.text}")

if r.status_code == 401:
    print("CHECK 3 PASSED")
else:
    print(f"CHECK 3 FAILED")

# ─────────────────────────────────────────────────────────────────────────────
# CHECK 4 — POST /login -> real JWT -> GET /stats 200
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{SEP}")
print("CHECK 4: POST /login -> real JWT -> GET /stats 200")
print(SEP)

r = requests.post(f"{BASE}/login", json={"api_key": TEST_ADMIN_KEY}, timeout=5)
print(f"HTTP Status : {r.status_code}")
print(f"Raw token   : {r.text}")

if r.status_code == 200:
    token = r.json()["access_token"]
    parts = token.split(".")
    
    def b64dec(s):
        s += "=" * (-len(s) % 4)
        return json.loads(base64.urlsafe_b64decode(s))
        
    print(f"\nJWT Header  : {json.dumps(b64dec(parts[0]), indent=2)}")
    print(f"JWT Payload : {json.dumps(b64dec(parts[1]), indent=2)}")

    r2 = requests.get(f"{BASE}/stats", headers={"Authorization": f"Bearer {token}"}, timeout=5)
    print(f"\nGET /stats with token:")
    print(f"HTTP Status : {r2.status_code}")
    print(f"Response    : {r2.text}")

    if r2.status_code == 200:
        print("CHECK 4 PASSED")
    else:
        print(f"CHECK 4 FAILED")
else:
    print(f"CHECK 4 FAILED")

print(f"\n{SEP}")
print("Phase 1 verification complete.")
print(SEP)
server.should_exit = True
time.sleep(1)
