import urllib.request
import urllib.error
import json
import os

API_URL = "http://localhost:8000"

# 1. Read admin key from .env
env_file = r"I:\QYNTARA AI\.env"
admin_key = None
if os.path.exists(env_file):
    with open(env_file, "r") as f:
        for line in f:
            if line.startswith("ADMIN_KEY="):
                admin_key = line.strip().split("=")[1].strip('"').strip("'")
                break

if not admin_key:
    admin_key = "qyntara-ai-admin-key-2026" # Fallback guess

print(f"Using ADMIN_KEY: {admin_key}")

# 2. Login
login_data = json.dumps({"api_key": admin_key}).encode("utf-8")
req = urllib.request.Request(f"{API_URL}/login", data=login_data, headers={"Content-Type": "application/json"})
try:
    with urllib.request.urlopen(req) as response:
        login_resp = json.loads(response.read().decode())
        token = login_resp.get("access_token")
        print(f"Logged in successfully. Token: {token[:10]}...")
except Exception as e:
    print(f"Login failed: {e}")
    exit(1)

# 3. Call /validate/core
payload = {"polycount": 100000, "has_lods": True, "shader_instructions": 300}
data_bytes = json.dumps({"industry": "gaming", "metadata": payload}).encode("utf-8")
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}

print("Headers:", headers)
req = urllib.request.Request(f"{API_URL}/validate/core", data=data_bytes, headers=headers)
try:
    with urllib.request.urlopen(req) as response:
        resp_body = response.read().decode()
        print("Response 200 OK:")
        print(resp_body)
except urllib.error.HTTPError as e:
    print(f"HTTPError {e.code}: {e.read().decode()}")
except Exception as e:
    print(f"Other Error: {e}")
