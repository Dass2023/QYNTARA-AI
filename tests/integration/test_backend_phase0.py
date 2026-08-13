from fastapi.testclient import TestClient
from backend.main import app
import os
import uuid

client = TestClient(app)

def get_token():
    # Attempt login to get JWT
    from backend.main import ADMIN_KEY
    resp = client.post("/login", json={"api_key": ADMIN_KEY})
    assert resp.status_code == 200
    return resp.json()["access_token"]

def test_unauthenticated_upload():
    # P0-005: Ensure missing auth rejects
    resp = client.post("/upload", files={"file": ("test.txt", b"hello")})
    assert resp.status_code == 401

def test_authenticated_upload():
    # P0-005: Ensure valid auth accepts
    token = get_token()
    resp = client.post("/upload", headers={"Authorization": f"Bearer {token}"}, files={"file": ("test.txt", b"hello")})
    assert resp.status_code == 200
    assert "test.txt" in resp.json()["filename"]

def test_path_traversal_upload():
    # P0-006: Path traversal check
    token = get_token()
    # Malicious filename
    resp = client.post("/upload", headers={"Authorization": f"Bearer {token}"}, files={"file": ("../../../windows/system32/cmd.exe", b"hack")})
    assert resp.status_code == 200
    # The basename should strip the traversal dots
    assert resp.json()["filename"].endswith("cmd.exe")
    assert not resp.json()["filename"].startswith("../")

def test_library_auth():
    # P0-005: Library auth checks
    resp = client.get("/library")
    assert resp.status_code == 401
    
    token = get_token()
    resp2 = client.get("/library", headers={"Authorization": f"Bearer {token}"})
    assert resp2.status_code == 200

if __name__ == "__main__":
    try:
        test_unauthenticated_upload()
        print("PASS: Unauthenticated upload rejected.")
        test_authenticated_upload()
        print("PASS: Authenticated upload successful.")
        test_path_traversal_upload()
        print("PASS: Path traversal neutralized via basename.")
        test_library_auth()
        print("PASS: Library authentication enforced.")
        print("ALL TESTS PASSED.")
    except AssertionError as e:
        import traceback
        traceback.print_exc()
        print("TEST FAILED")
