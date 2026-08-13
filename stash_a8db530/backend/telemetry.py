import torch
import psutil
import time
from typing import Dict, Any

class TelemetryService:
    @staticmethod
    def get_system_health() -> Dict[str, Any]:
        health = {
            "timestamp": time.time(),
            "cpu_usage": psutil.cpu_percent(),
            "memory_usage": psutil.virtual_memory().percent,
            "gpu": {
                "available": torch.cuda.is_available(),
                "device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "N/A",
                "memory_allocated": f"{torch.cuda.memory_allocated(0) / 1024**2:.2f} MB" if torch.cuda.is_available() else "0 MB",
                "memory_reserved": f"{torch.cuda.memory_reserved(0) / 1024**2:.2f} MB" if torch.cuda.is_available() else "0 MB"
            },
            "status": "OPERATIONAL"
        }
        return health

# Singleton instance
telemetry = TelemetryService()
