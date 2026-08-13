import psutil
import sys

print("Searching for process on port 8000...")
found = False
for proc in psutil.process_iter(['pid', 'name']):
    try:
        for conn in proc.connections(kind='inet'):
            if conn.laddr.port == 8000:
                print(f"Found {proc.info['name']} (PID: {proc.info['pid']})")
                proc.kill()
                print("Process killed.")
                found = True
                break
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass
    if found:
        break

if not found:
    print("No process found on port 8000.")
