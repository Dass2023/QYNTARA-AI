import sys
import os
import time
import json
import logging
import traceback

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Initialize Maya Standalone
try:
    import maya.standalone
    maya.standalone.initialize(name='python')
    from maya import cmds
except ImportError:
    print("Not running in mayapy or maya not found.")

try:
    import redis
except ImportError:
    print("Redis not installed.")
    sys.exit(1)

from qyntara_ai.core.validator import QyntaraValidator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QyntaraWorker")

def process_job(job_id, r):
    try:
        data_str = r.get(f"job:{job_id}")
        if not data_str:
            logger.error(f"Job data missing for {job_id}")
            return
            
        job_data = json.loads(data_str)
        file_path = job_data.get("file_path")
        
        # Update status
        job_data["status"] = "processing"
        r.set(f"job:{job_id}", json.dumps(job_data))
        
        # Load Scene
        logger.info(f"Opening file: {file_path}")
        if os.path.exists(file_path):
            cmds.file(file_path, open=True, force=True)
        else:
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Run Validation
        validator = QyntaraValidator()
        # Validate all transforms in the scene
        objects = cmds.ls(type="transform", long=True)
        report = validator.run_validation(objects)
        
        # Save results
        job_data["status"] = "completed"
        job_data["report"] = report
        r.set(f"job:{job_id}", json.dumps(job_data))
        logger.info(f"Job {job_id} completed.")
        
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        job_data["status"] = "failed"
        job_data["error"] = str(e)
        job_data["traceback"] = traceback.format_exc()
        if r:
            r.set(f"job:{job_id}", json.dumps(job_data))

def main():
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    r = redis.Redis(host=redis_host, port=6379, db=0)
    logger.info(f"Worker started, connected to {redis_host}...")
    
    while True:
        # Blocking pop
        # qyntara_queue should contain job IDs
        item = r.blpop("qyntara_queue", timeout=5)
        if item:
            queue_name, job_id = item
            job_id = job_id.decode('utf-8')
            logger.info(f"Processing job {job_id}")
            process_job(job_id, r)
        
        # Keep alive check or generic tasks could go here

if __name__ == "__main__":
    main()
