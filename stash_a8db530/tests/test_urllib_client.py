import urllib.request
import urllib.parse
import urllib.error
import json
import os

API_URL = "http://localhost:8000"

def test_stats():
    print("Testing /stats...")
    try:
        with urllib.request.urlopen(f"{API_URL}/stats", timeout=2) as response:
            print(f"Stats Status: {response.status}")
            print(response.read().decode('utf-8'))
    except Exception as e:
        print(f"Stats Failed: {e}")

def test_upload_and_execute():
    print("\nTesting Upload & Execute...")
    # Create dummy file
    with open("test_urllib.obj", "w") as f:
        f.write("v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3")
        
    try:
        # Upload
        url = f"{API_URL}/upload"
        boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
        data = []
        data.append(f'--{boundary}')
        data.append(f'Content-Disposition: form-data; name="file"; filename="test_urllib.obj"')
        data.append('Content-Type: application/octet-stream')
        data.append('')
        
        with open("test_urllib.obj", 'rb') as f:
            file_content = f.read()
            
        body = b'\r\n'.join([x.encode('utf-8') for x in data])
        body += b'\r\n' + file_content + b'\r\n'
        body += f'--{boundary}--\r\n'.encode('utf-8')
        
        req = urllib.request.Request(url, data=body)
        req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
        
        server_path = None
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            server_path = result.get("path")
            print(f"Upload Path: {server_path}")
            
        if server_path:
            # Execute
            payload = {
                "meshes": [server_path],
                "materials": [],
                "tasks": ["validate", "uv", "lightmapuv", "dual_uv"],
                "engineTarget": "unreal",
                "remesh_settings": {},
                "generative_settings": {"prompt": "test", "provider": "internal"}
            }
            
            req = urllib.request.Request(f"{API_URL}/execute")
            req.add_header('Content-Type', 'application/json')
            jsondata = json.dumps(payload).encode('utf-8')
            req.add_header('Content-Length', len(jsondata))
            
            # Note: passing data to urlopen makes it a POST
            with urllib.request.urlopen(req, data=jsondata) as response:
                print(f"Execute Status: {response.status}")
                print(response.read().decode('utf-8'))

    except Exception as e:
        print(f"Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_stats()
    test_upload_and_execute()
