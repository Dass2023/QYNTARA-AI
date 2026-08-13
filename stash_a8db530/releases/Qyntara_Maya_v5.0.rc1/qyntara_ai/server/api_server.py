import sys
import os

# Vendor path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
vendor_path = os.path.join(os.path.dirname(current_dir), "vendor")
if vendor_path not in sys.path:
    sys.path.insert(0, vendor_path)

try:
    from fastapi import FastAPI, HTTPException, UploadFile, File, Form
    app = FastAPI(title="Qyntara AI API")
except ImportError:
    # Fallback for environments where fastapi is not installed (e.g. Maya)
    FastAPI = object
    HTTPException = Exception 
    UploadFile = object
    File = object
    Form = object
    app = None
    print("Warning: fastapi not found. Qyntara Server functionality disabled.")

# Redis connection
try:
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    r = redis.Redis(host=redis_host, port=6379, db=0)
except Exception:
    r = None

# from fastapi import UploadFile, File, Form
import shutil
# import os

@app.post("/validate/")
async def submit_validation(file: UploadFile = File(...), rules_config: str = Form(default="{}")):
    if not r:
        raise HTTPException(status_code=500, detail="Redis not available")
    
    job_id = str(uuid.uuid4())
    
    # Save uploaded file
    temp_dir = "/tmp/qyntara_uploads"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, f"{job_id}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    job_data = {
        "id": job_id,
        "file_path": file_path,
        "status": "queued",
        "rules_config": json.loads(rules_config)
    }
    
    # Store job status
    r.set(f"job:{job_id}", json.dumps(job_data))
    
    # Push to queue
    r.rpush("qyntara_queue", job_id)
    
    return {"job_id": job_id, "status": "queued"}

@app.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    if not r:
        raise HTTPException(status_code=500, detail="Redis not available")
    
    data = r.get(f"job:{job_id}")
    if not data:
        raise HTTPException(status_code=404, detail="Job not found")
        
    return json.loads(data)
