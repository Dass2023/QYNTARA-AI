import requests
import json
import time

URL = "http://localhost:8008/search/similar"

def test_api():
    print("--- Testing Geometric Search API ---")
    
    # query: "Cube-like"
    payload = {
        "metadata": {"polycount": 12, "bbox_diagonal": 1.74, "bbox_height": 1.0},
        "k": 3
    }
    
    try:
        start = time.time()
        res = requests.post(URL, json=payload, timeout=2)
        duration = (time.time() - start) * 1000
        
        if res.status_code == 200:
            data = res.json()
            matches = data["top_matches"]
            top_id = matches[0]["asset_id"]
            score = matches[0]["similarity"]
            
            print(f"Query: Cube -> Top Match: {top_id} (Score: {score:.4f})")
            print(f"Latency: {duration:.1f}ms")
            
            if "Stock_Cube" in top_id:
                print(">> SUCCESS: API correctly returned Stock_Cube.")
            else:
                 print(f">> FAIL: Expected Stock_Cube, got {top_id}")
        else:
            print(f">> FAIL: HTTP {res.status_code}")
            
    except Exception as e:
        print(f">> ERROR: {e}")

if __name__ == "__main__":
    # Wait for server to boot
    time.sleep(2) 
    test_api()
