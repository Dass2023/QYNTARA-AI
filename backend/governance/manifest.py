import json, uuid, time, socket
from datetime import datetime

class ManifestGenerator:
    def generate_manifest(self, job_data: dict, output_path: str):
        m = {
            "id": str(uuid.uuid4()),
            "provenance": {
                "host": socket.gethostname(),
                "time": datetime.utcnow().isoformat()
            },
            "job": job_data
        }
        with open(output_path, 'w') as f:
            json.dump(m, f, indent=4)
        return m
