import subprocess
import time
import requests
import json
import base64

def b64_decode(data):
    padding = '=' * (4 - (len(data) % 4))
    return base64.b64decode(data + padding).decode('utf-8')

print("============================================================")
print("CHECK 2: Start backend with ADMIN_KEY set")
print("============================================================")

proc = subprocess.Popen(
    ["I:\\QYNTARA AI\\test_env_full\\Scripts\\python.exe", "-m", "uvicorn", "backend.main:app", "--port", "8001"],
    env={"ADMIN_KEY": "test1234"},
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

time.sleep(4)

print("Server started in background on port 8001.\n")

print("============================================================")
print("CHECK 3: curl /stats with no token")
print("============================================================")

try:
    resp = requests.get("http://localhost:8001/stats")
    print(f"HTTP Status: {resp.status_code}")
    print(f"Response Body: {resp.text}\n")
except Exception as e:
    print(e)

print("============================================================")
print("CHECK 4: POST /login and decode JWT")
print("============================================================")

try:
    resp_login = requests.post(
        "http://localhost:8001/login",
        json={"admin_key": "test1234"}
    )
    print(f"HTTP Status: {resp_login.status_code}")
    print(f"Raw JSON Response: {resp_login.text}\n")

    if resp_login.status_code == 200:
        token = resp_login.json().get("access_token")
        if token:
            parts = token.split(".")
            if len(parts) >= 2:
                try:
                    header = b64_decode(parts[0])
                    payload = b64_decode(parts[1])
                    print("Decoded JWT Header:")
                    print(json.dumps(json.loads(header), indent=2))
                    print("\nDecoded JWT Payload:")
                    print(json.dumps(json.loads(payload), indent=2))
                except Exception as e:
                    print(f"Failed to decode JWT: {e}")
except Exception as e:
    print(e)

proc.terminate()
stdout, stderr = proc.communicate()
print("============================================================")
print("Server terminated.")
print("STDOUT:")
print(stdout)
print("STDERR:")
print(stderr)
print("============================================================")
