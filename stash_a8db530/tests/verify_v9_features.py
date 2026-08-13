import sys
import os
import asyncio
import json
import logging
import cv2
import numpy as np
import trimesh
from fastapi.testclient import TestClient

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("v9_Verification")

# --- MOCKING MISSING DEPENDENCIES ---
from unittest.mock import MagicMock
sys.modules["nvdiffrast"] = MagicMock()
sys.modules["chromadb"] = MagicMock()
sys.modules["backend.memory.vector_store"] = MagicMock()
# sys.modules["backend.registry"] = MagicMock() # We might need registry for the app to load

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.main import app
from backend.pipeline import QyntaraPipeline
from qyntara_dcc.max.adapter import MaxAdapter
from qyntara_core.datatypes import QMesh

client = TestClient(app)

def create_dummy_image(path):
    # Create a black image with a white square (simulating a room)
    img = np.zeros((500, 500), dtype=np.uint8)
    cv2.rectangle(img, (100, 100), (400, 400), 255, 5) # Walls
    cv2.imwrite(path, img)
    return path

def create_dummy_mesh(path):
    mesh = trimesh.creation.box(extents=(1, 1, 1))
    mesh.export(path)
    return path

def test_industry_5_0():
    logger.info("--- Testing Industry 5.0 (Validation API) ---")
    response = client.get("/api/v1/assets/test_asset_001/validation")
    if response.status_code == 200:
        data = response.json()
        logger.info(f"✅ API Response: {data['report']['status']} (Score: {data['report']['score']})")
    else:
        logger.error(f"❌ API Failed: {response.status_code}")

def test_blueprint_studio():
    logger.info("--- Testing Blueprint Studio (Floorplan Extrusion) ---")
    img_path = "tests/assets/dummy_floorplan.png"
    create_dummy_image(img_path)
    
    with open(img_path, "rb") as f:
        response = client.post(
            "/extrude-floorplan",
            files={"file": ("floorplan.png", f, "image/png")},
            data={"height": 3.0, "pixels_per_meter": 50.0}
        )
    
    if response.status_code == 200:
        res = response.json()
        if os.path.exists(res['mesh_path']):
            logger.info(f"✅ Mesh Generated: {res['mesh_path']}")
        else:
            logger.error("❌ Mesh file not found!")
    else:
        logger.error(f"❌ API Failed: {response.status_code} - {response.text}")

def test_alignment_backend():
    logger.info("--- Testing Alignment Backend ---")
    mesh_path = "tests/assets/cube.obj"
    create_dummy_mesh(mesh_path)
    
    # Test Sync endpoint
    response = client.post(
        "/align",
        json={"source_mesh": mesh_path, "target_mesh": None} # Center only
    )
    
    if response.status_code == 200:
        logger.info("✅ Alignment Endpoint Success")
    else:
        logger.error(f"❌ Alignment Failed: {response.status_code}")

def test_max_adapter_logic():
    logger.info("--- Testing 3ds Max Adapter Logic (Mocked) ---")
    # Simulation (Real max calls would fail outside Max)
    try:
        qmesh = QMesh(
            vertices=np.array([[0,0,0], [1,0,0], [0,1,0]], dtype=np.float32),
            faces=np.array([[0,1,2,-1]], dtype=np.int32),
            name="TestMesh"
        )
        # We can't actually call create_mesh_from_qmesh because 'pymxs' isn't real here,
        # but we can verify the class structure exists
        if hasattr(MaxAdapter, 'create_mesh_from_qmesh'):
            logger.info("✅ MaxAdapter structure valid")
        else:
            logger.error("❌ MaxAdapter missing methods")
    except Exception as e:
        logger.error(f"❌ Adapter Error: {e}")

if __name__ == "__main__":
    os.makedirs("tests/assets", exist_ok=True)
    
    print("\nStarting v9.0 Verification Suite...\n")
    test_industry_5_0()
    test_blueprint_studio()
    test_alignment_backend()
    test_max_adapter_logic()
    print("\nVerification Complete.")
