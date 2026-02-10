import requests
import json

def test_library():
    print("--- Testing Library Endpoint ---")
    try:
        res = requests.get("http://localhost:8000/library")
        if res.status_code == 200:
            data = res.json()
            print("SUCCESS: Library endpoint reachable.")
            print(f"Files found: {len(data.get('files', []))}")
            for f in data.get('files', [])[:3]: # Show top 3
                print(f" - {f['name']} ({f['type']})")
        else:
            print(f"FAILED: Status Code {res.status_code}")
            print(res.text)
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    test_library()
