import os
from celery import Celery
from backend.pipeline import QyntaraPipeline
import asyncio

# Initialize Celery
# Usage: celery -A backend.celery_worker.celery_app worker --loglevel=info

broker_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
result_backend = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery(
    "qyntara_worker",
    broker=broker_url,
    backend=result_backend
)

# Global Pipeline instance for the worker process
# This loads models ONCE when the worker starts
pipeline_instance = None

@celery_app.on_after_configure.connect
def setup_initial_tasks(sender, **kwargs):
    pass

@celery_app.worker_process_init.connect
def init_worker(**kwargs):
    global pipeline_instance
    print("[Worker] Initializing Qyntara AI Models on GPU...")
    pipeline_instance = QyntaraPipeline()
    print("[Worker] Models Loaded. Ready for tasks.")

@celery_app.task(name="run_generative_3d_task")
def run_generative_3d_task(prompt, provider="internal", quality="draft"):
    """Async wrapper for text-to-3d generation."""
    # We need to run the async pipeline method in a sync Celery task
    # Using asyncio.run for isolation
    
    async def _run():
        return await pipeline_instance.run_generative_3d(prompt, provider, quality)
        
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # Should not happen in standard Celery worker, but handle just in case
        return loop.run_until_complete(_run())
    else:
        return asyncio.run(_run())

@celery_app.task(name="run_remesh_task")
def run_remesh_task(file_paths, settings):
    """Async wrapper for remeshing."""
    async def _run():
        return await pipeline_instance.run_quad_remeshing(file_paths, settings)
    
    return asyncio.run(_run())
