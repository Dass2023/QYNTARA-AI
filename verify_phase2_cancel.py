import requests
import time
import json
import subprocess
import os

API_URL = "http://localhost:8003"
ADMIN_KEY = "test1234"

def get_token():
    print("Logging in...")
    resp = requests.post(f"{API_URL}/login", json={"api_key": ADMIN_KEY})
    if resp.status_code == 200:
        return resp.json()["access_token"]
    raise Exception(f"Login failed: {resp.text}")

def main():
    print("============================================================")
    print("PHASE 2 CANCEL VERIFICATION")
    print("============================================================")

    # 1. Start Server and Worker
    print("Starting backend and celery worker...")
    env = os.environ.copy()
    env["ADMIN_KEY"] = "local_dev_key_qyntara_123!"
    env["SECRET_KEY"] = "test_secret"
    env["REDIS_URL"] = "redis://localhost:6379/0"
    env["QDRANT_URL"] = ":memory:"

    # Start Redis explicitly
    redis_proc = subprocess.Popen(
        [".\\Redis\\redis-server.exe"],
        cwd="I:\\QYNTARA AI",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(2) # Give redis a moment to start

    backend_proc = subprocess.Popen(
        ["I:\\QYNTARA AI\\test_env_phase2\\Scripts\\python.exe", "-m", "uvicorn", "backend.main:app", "--port", "8003"],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    worker_proc = subprocess.Popen(
        ["I:\\QYNTARA AI\\test_env_phase2\\Scripts\\celery.exe", "-A", "backend.tasks.celery_app", "worker", "--loglevel=info", "--concurrency=1", "--pool=solo"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd="I:\\QYNTARA AI"
    )

    time.sleep(8) # Wait for startup
    print("Waiting for backend to become available...")
    for _ in range(10):
        try:
            requests.get(f"{API_URL}/stats")
            break
        except requests.exceptions.ConnectionError:
            time.sleep(2)
            
    headers = {}
    try:
        # Login
        print("Logging in...")
        login_resp = requests.post(f"{API_URL}/login", json={"api_key": "local_dev_key_qyntara_123!"})
        if login_resp.status_code == 200:
            headers["Authorization"] = f"Bearer {login_resp.json()['access_token']}"
        else:
            print(f"Login failed ({login_resp.status_code}): {login_resp.text}")
            print("Proceeding anyway to test auth rejection...")

        # Task 1: Long running
        payload = {
            "tasks": ["sleep_test"],
            "meshes": ["backend/data/sample_cube.obj"],
            "materials": [],
            "validation_profile": "GENERIC"
        }

        print("\n--- Submitting Task 1 (Expected to be cancelled) ---")
        t1_resp = requests.post(f"{API_URL}/execute", json=payload, headers=headers)
        if t1_resp.status_code != 200:
            print(f"Error on execute: {t1_resp.text}")
        t1_id = t1_resp.json()["task_id"]
        print(f"Task 1 ID: {t1_id}")
        
        print("Waiting 3 seconds to let worker pick it up...")
        time.sleep(3)
        
        status1 = requests.get(f"{API_URL}/tasks/{t1_id}", headers=headers).json()
        print(f"Task 1 Status before cancel: {status1}")

        print(f"\n--- Cancelling Task 1 ---")
        cancel_resp = requests.post(f"{API_URL}/tasks/{t1_id}/cancel", headers=headers)
        print(f"Cancel Response: {cancel_resp.json()}")

        print("\n--- Submitting Task 2 immediately after cancel ---")
        payload2 = {
            "tasks": ["validate"],
            "meshes": ["backend/data/sample_cube.obj"],
            "materials": [],
            "validation_profile": "GENERIC"
        }
        t2_resp = requests.post(f"{API_URL}/execute", json=payload2, headers=headers)
        t2_id = t2_resp.json()["task_id"]
        print(f"Task 2 ID: {t2_id}")

        print("Polling Task 2 until completion (max 60s)...")
        for i in range(60):
            status2 = requests.get(f"{API_URL}/tasks/{t2_id}", headers=headers).json()
            state = status2.get("status")
            print(f"  Poll {i+1}: state={state}")
            if state in ["done", "failed", "cancelled"]:
                break
            time.sleep(1)

        print("\nCleaning up...")
        backend_proc.terminate()
        worker_proc.terminate()
        redis_proc.terminate()
        
        stdout, _ = worker_proc.communicate()
        print("\nWorker Logs:")
        for line in stdout.splitlines():
            if "revoke" in line.lower() or "received task" in line.lower() or "succeeded" in line.lower() or "term" in line.lower():
                print(line)

        backend_proc.wait()
        redis_proc.wait()
        
    except Exception as e:
        print(f"Test failed: {e}")
        worker_proc.terminate()
        backend_proc.terminate()
        redis_proc.terminate()

    print("============================================================")
    print("TEST FINISHED")
    print("============================================================")

if __name__ == "__main__":
    main()
