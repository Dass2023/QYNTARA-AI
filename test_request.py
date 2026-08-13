import json
import urllib.request
import urllib.error

API_URL = "http://localhost:8000"
api_key = "PLACEHOLDER_KEY_DO_NOT_USE"

# 1. Login
req = urllib.request.Request(f"{API_URL}/login", data=json.dumps({"api_key": api_key}).encode(), headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req) as resp:
    token = json.loads(resp.read())["access_token"]

# 2. Validate
payload = {
    "uuid": "MOCK-123",
    "is_sensor": True, 
    "telemetry_unit": "celsius", 
    "update_rate_ms": 100, 
    "supported_protocols": ["OPC UA", "MQTT"]
}
data_bytes = json.dumps({"industry": "industry4", "metadata": payload}).encode("utf-8")

req = urllib.request.Request(f"{API_URL}/validate/core", data=data_bytes, headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"})
try:
    with urllib.request.urlopen(req) as resp:
        print(f"Status: {resp.status}")
        print(resp.read().decode())
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
    print(e.read().decode())
