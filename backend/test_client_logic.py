import requests
import random
import json

def run_cloud_analysis_simulation(industry_key):
    print(f"\n--- Testing Client Logic for: {industry_key} ---")
    
    # --- LOGIC COPIED FROM qyntara_client.py ---
    key = industry_key.lower().split(" ")[0]
    if "film" in industry_key.lower(): key = "film"
    if "xr" in industry_key.lower(): key = "xr"
    if "e-commerce" in industry_key.lower(): key = "ecommerce"
    if "3d" in industry_key.lower(): key = "printing"
    if "4.0" in industry_key.lower(): key = "industry4"
    if "5.0" in industry_key.lower(): key = "industry5"
    if "omniverse" in industry_key.lower(): key = "omniverse"

    payload = {}
    
    if key == "gaming":
        payload = {"polycount": random.randint(50000, 150000), "has_lods": True, "shader_instructions": random.randint(200, 500)}
    elif key == "medical":
        payload = {"is_manifold": True, "bbox_diagonal": 0.15, "topology_type": "triangulated"}
    elif key == "film":
        payload = {"poles": random.choice([3, 5, 8]), "has_circular_ref": False}
    elif key == "automotive":
        payload = {"nurbs_deviation": 0.02, "occludes_sensor": False, "has_metadata_layer": True}
    elif key == "architecture":
        payload = {"bbox_height": 3.5, "fire_rating": "A1"}
    elif key == "aerospace":
        payload = {"stress_concentrators": 0}
    elif key == "xr":
        payload = {"texture_mem_mb": random.randint(30, 80)}
    elif key == "ecommerce":
        payload = {"filesize_mb": 4.2}
    elif key == "robotics":
        payload = {"collision_hulls": 1}
    elif key == "industry4":
        payload = {
            "uuid": "Asset-77-88-99", 
            "node_id": "ns=2;s=Demo.Asset", 
            "ns_uri": "http://qyntara.ai/UA",
            "supported_protocols": ["OPC UA", "MQTT"],
            "is_sensor": True,
            "telemetry_unit": "Celsius",
            "update_rate_ms": 100
        }
    elif key == "industry5":
        payload = {"polycount": 120000}
    elif key == "printing":
        payload = {"critical_overhangs": random.randint(0, 3)}
    elif key == "omniverse":
        payload = {"meters_per_unit": 0.01, "up_axis": "Y", "usd_kind": "component", "nucleus_connected": True}

    print(f"Generated Key: {key}")
    # print(f"Payload: {payload}")

    try:
        url = "http://localhost:8007/validate/core"
        response = requests.post(url, json={"industry": key, "metadata": payload}, timeout=3)
        
        if response.status_code == 200:
            data = response.json()
            # print(json.dumps(data, indent=2))
            if data['status'] == 'success':
                print(">> SUCCESS: Valid Response Received.")
                return True
            else:
                print(f">> FAIL: API Error - {data.get('message')}")
                return False
        else:
            print(f">> FAIL: Status {response.status_code}")
            return False
            
    except Exception as e:
        print(f">> ERROR: {e}")
        return False

if __name__ == "__main__":
    industries = [
        "Gaming (Khronos)", "Medical (ISO)", "Film / VFX", 
        "Automotive", "Architecture", "Aerospace", 
        "XR / Metaverse", "E-Commerce", "Robotics", 
        "Industry 4.0", "Industry 5.0", "3D Printing", 
        "NVIDIA Omniverse"
    ]
    
    all_pass = True
    for ind in industries:
        if not run_cloud_analysis_simulation(ind):
            all_pass = False
            
    if all_pass:
        print("\n\nALL CLIENT SIMULATIONS PASSED.")
    else:
        print("\n\nSOME SIMULATIONS FAILED.")
