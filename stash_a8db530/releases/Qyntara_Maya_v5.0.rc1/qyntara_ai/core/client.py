import requests
import time
import json
import os
import logging

logger = logging.getLogger(__name__)

class QyntaraClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def submit_job(self, file_path, rules_config=None):
        """
        Uploads the file at file_path to the validation server.
        Returns job_id or None.
        """
        url = f"{self.base_url}/validate/"
        
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return None
            
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f)}
                data = {'rules_config': json.dumps(rules_config or {})}
                
                response = requests.post(url, files=files, data=data)
                response.raise_for_status()
                return response.json().get("job_id")
        except Exception as e:
            logger.error(f"Failed to submit job: {e}")
            return None

    def get_job_status(self, job_id):
        """
        Gets current status of a job.
        """
        url = f"{self.base_url}/jobs/{job_id}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            return None
            
    def poll_result(self, job_id, interval=1.0, timeout=60):
        """
        Blocking poll for result.
        Returns the finished job data (including report) or None.
        """
        start = time.time()
        while (time.time() - start) < timeout:
            status_data = self.get_job_status(job_id)
            if not status_data:
                return None
                
            state = status_data.get("status")
            if state == "completed":
                return status_data
            elif state == "failed":
                logger.error(f"Job failed: {status_data.get('error')}")
                return status_data
                
            time.sleep(interval)
            
        logger.error("Job timed out polling.")
        return None
