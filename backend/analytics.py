import time

class AnalyticsService:
    def __init__(self):
        self.stats_file = "backend/data/stats.json"
        self.start_time = time.time()
        self.total_jobs = 0
        self.total_polygons = 0
        self.ai_tokens_generated = 0
        self.active_nodes = 1
        self._load_stats()

    def _load_stats(self):
        import json, os
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as f:
                    data = json.load(f)
                    self.total_jobs = data.get("total_jobs", 0)
                    self.total_polygons = data.get("total_polygons", 0)
                    self.ai_tokens_generated = data.get("ai_tokens", 0)
            except Exception as e:
                print(f"Failed to load stats: {e}")

    def _save_stats(self):
        import json
        data = {
            "total_jobs": self.total_jobs,
            "total_polygons": self.total_polygons,
            "ai_tokens": self.ai_tokens_generated
        }
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Failed to save stats: {e}")

    def track_job(self, job_data: dict):
        self.total_jobs += 1
        self.total_polygons += len(job_data.get("meshes", [])) * 5000
        if "generative" in job_data.get("tasks", []):
            self.ai_tokens_generated += 750
        if "sam_segmentation" in job_data.get("tasks", []):
            self.ai_tokens_generated += 200
        self._save_stats()

    def get_stats(self) -> dict:
        return {
            "uptime_seconds": int(time.time() - self.start_time),
            "total_jobs": self.total_jobs,
            "total_polygons": self.total_polygons,
            "ai_tokens": self.ai_tokens_generated,
            "active_nodes": self.active_nodes,
            "system_status": "OPERATIONAL"
        }
