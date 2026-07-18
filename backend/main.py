from fastapi import FastAPI, HTTPException, Header, Depends, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
import uvicorn, json, os, shutil, trimesh
from backend.models import *
from backend.pipeline import QyntaraPipeline
from backend.analytics import AnalyticsService
from backend.intent.agent import QyntaraAgent

import pathlib
app = FastAPI(title="QYNTARA AI", version="1.0.0")
_data_dir = pathlib.Path(__file__).parent / "data"
os.makedirs(_data_dir / "uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory=str(_data_dir)), name="static")

from dotenv import load_dotenv
load_dotenv()

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.security import verify_token, create_access_token, Role
from pydantic import BaseModel

ADMIN_KEY = os.getenv("ADMIN_KEY")
if not ADMIN_KEY:
    raise RuntimeError("CRITICAL: ADMIN_KEY environment variable is not set. Refusing to start server.")

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload

class LoginRequest(BaseModel):
    api_key: str

@app.post("/login")
async def login(request: LoginRequest):
    if request.api_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    token = create_access_token(data={"sub": "admin"}, role=Role.ADMIN, tenant_id="local")
    return {"access_token": token, "token_type": "bearer"}

# --- Qyntara Core Imports (Phase 11) ---
from backend.qyntara_core.base import AssetContext
from backend.qyntara_core.gaming_validator import GamingValidator
from backend.qyntara_core.medical_validator import MedicalValidator
from backend.qyntara_core.film_validator import FilmValidator
from backend.qyntara_core.automotive_validator import AutomotiveValidator
from backend.qyntara_core.architecture_validator import ArchitectureValidator
from backend.qyntara_core.aerospace_validator import AerospaceValidator
from backend.qyntara_core.xr_validator import XRValidator
from backend.qyntara_core.ecommerce_validator import EcommerceValidator
from backend.qyntara_core.robotics_validator import RoboticsValidator
from backend.qyntara_core.industry4_validator import Industry4Validator
from backend.qyntara_core.industry5_validator import Industry5Validator
from backend.qyntara_core.printing_validator import PrintingValidator
from backend.qyntara_core.omniverse_validator import OmniverseValidator
from backend.qyntara_core.vector_db import VectorDB

# --- Core Validator Registry ---
VALIDATORS = {
    "gaming": GamingValidator(),
    "medical": MedicalValidator(),
    "film": FilmValidator(),
    "automotive": AutomotiveValidator(),
    "architecture": ArchitectureValidator(),
    "aerospace": AerospaceValidator(),
    "xr": XRValidator(),
    "ecommerce": EcommerceValidator(),
    "robotics": RoboticsValidator(),
    "industry4": Industry4Validator(),
    "industry5": Industry5Validator(),
    "printing": PrintingValidator(),
    "omniverse": OmniverseValidator()
}

# --- Vector DB Initialization ---
vector_db = VectorDB()

@app.on_event("startup")
async def startup_event():
    # Pre-populate Vector DB with some diversity for demo
    print("Initializing Vector Database...")
    vector_db.add_asset("Stock_Cube", {"polycount": 12, "bbox_diagonal": 1.73, "is_manifold": True})
    vector_db.add_asset("Stock_Sphere", {"polycount": 5000, "bbox_diagonal": 1.0, "is_manifold": True})
    vector_db.add_asset("V8_Engine_v1", {"polycount": 150000, "bbox_diagonal": 12.0, "industry_context": "automotive"})
    vector_db.add_asset("Aero_Wing_L", {"polycount": 45000, "bbox_diagonal": 25.0, "stress_concentrators": 0})
    print(f"Vector DB Ready. Index Size: {vector_db.get_count()}")

class ValidationRequest(BaseModel):
    industry: str
    metadata: Dict[str, Any]

@app.post("/validate/core", dependencies=[Depends(get_current_user)])
async def unique_validation_endpoint(request: ValidationRequest):
    """
    Unified entry point for the Spatial Intelligence OS.
    Routes validation requests to the appropriate industry core.
    """
    if request.industry not in VALIDATORS:
        raise HTTPException(status_code=404, detail=f"Validator for '{request.industry}' not implemented.")
    
    validator = VALIDATORS[request.industry]
    
    # Context Construction
    ctx = AssetContext(
        file_path="virtual",
        asset_type="metadata_proxy",
        metadata=request.metadata
    )
    
    results = validator.validate(ctx)
    return {"status": "success", "industry": request.industry, "results": results}

pipeline = QyntaraPipeline()
analytics = AnalyticsService()


@app.get("/stats", dependencies=[Depends(get_current_user)])
def stats(): return analytics.get_stats()


# --- AI Intelligence Endpoints (Phase 3) ---

class SeamGPTRequest(BaseModel):
    mesh_path: str

@app.post("/ai/seam-gpt", dependencies=[Depends(get_current_user)])
async def ai_seam_gpt(req: SeamGPTRequest):
    return await pipeline.run_seam_gpt(req.mesh_path)

class PredictRequest(BaseModel):
    polycount: int
    has_ngons: bool

@app.post("/ai/predict", dependencies=[Depends(get_current_user)])
async def ai_predict(req: PredictRequest):
    return await pipeline.run_predictive_check(req.dict())

class PhysicsRequest(BaseModel):
    material_name: str

@app.post("/ai/physics", dependencies=[Depends(get_current_user)])
async def ai_physics(req: PhysicsRequest):
    return pipeline.get_material_physics(req.material_name)

from backend.tasks.pipeline_tasks import process_pipeline_task
from celery.result import AsyncResult
from backend.tasks.celery_app import celery_app

@app.post("/execute", dependencies=[Depends(get_current_user)])
async def execute(request: PipelineRequest):
    try:
        analytics.track_job(request.dict())
        task = process_pipeline_task.delay(request.dict())
        return {"task_id": task.id, "status": "queued"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tasks/{task_id}", dependencies=[Depends(get_current_user)])
def get_task_status(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    if result.state == "PENDING":
        return {"status": "queued", "task_id": task_id}
    elif result.state == "PROGRESS":
        return {"status": "running", "task_id": task_id, "meta": result.info}
    elif result.state == "SUCCESS":
        return {"status": "done", "task_id": task_id, "result": result.get()}
    elif result.state == "FAILURE":
        return {"status": "failed", "task_id": task_id, "error": str(result.info)}
    elif result.state == "REVOKED":
        return {"status": "cancelled", "task_id": task_id}
    else:
        return {"status": result.state, "task_id": task_id}

@app.post("/tasks/{task_id}/cancel", dependencies=[Depends(get_current_user)])
def cancel_task(task_id: str):
    # Set cancel flag in redis for graceful termination by the worker
    import redis
    import os
    r = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
    r.setex(f"cancel_{task_id}", 3600, "1")
    
    # Also revoke it in Celery so it doesn't start if it's still queued
    celery_app.control.revoke(task_id, terminate=False)
    return {"status": "cancelled", "task_id": task_id}

@app.post("/upload", dependencies=[Depends(get_current_user)])
async def upload_file(file: UploadFile = File(...)):
    path = f"backend/data/uploads/{file.filename}"
    with open(path, "wb") as f: shutil.copyfileobj(file.file, f)
    return {"filename": file.filename, "path": path}

agent = QyntaraAgent(pipeline)

@app.get("/library", dependencies=[Depends(get_current_user)])
async def get_library():
    data_dir = "backend/data"
    files = []
    if os.path.exists(data_dir):
        for f in os.listdir(data_dir):
            if f.endswith(('.obj', '.glb', '.png', '.jpg', '.dxf', '.usda')):
                path = os.path.join(data_dir, f)
                stats = os.stat(path)
                files.append({
                    "name": f,
                    "size": stats.st_size,
                    "created": stats.st_ctime,
                    "type": f.split('.')[-1],
                    "url": f"http://localhost:8000/static/{f}"
                })
    # Sort by newest first
    files.sort(key=lambda x: x['created'], reverse=True)
    return {"files": files}

# ═══════════════════════════════════════════════════════════════════════════════
# MESH OPTIMIZATION ENDPOINTS (Simplygon-class)
# ═══════════════════════════════════════════════════════════════════════════════

class OptimizeRequest(BaseModel):
    mesh_path: str
    mode: str = "reduce"  # reduce, lod, cull
    settings: Dict[str, Any] = Field(default_factory=dict)

@app.post("/optimize", dependencies=[Depends(get_current_user)])
async def optimize_mesh(request: OptimizeRequest):
    """Standalone mesh optimization: triangle reduction, LOD generation, or geometry culling."""
    try:
        from backend.generative.mesh_optimizer import MeshOptimizer
        
        optimizer = MeshOptimizer()
        mesh = trimesh.load(request.mesh_path)
        if isinstance(mesh, trimesh.Scene):
            mesh = trimesh.util.concatenate(list(mesh.geometry.values()))
        
        if request.mode == "reduce":
            result = optimizer.reduce_triangles(mesh, request.settings)
            if result.status == "OK" and result.output_mesh:
                out_path = request.mesh_path.replace(".obj", "_reduced.obj")
                result.output_mesh.export(out_path)
                return {
                    "status": "OK",
                    "mesh_path": out_path,
                    "original_count": result.original_count,
                    "reduced_count": result.reduced_count,
                    "reduction_ratio": result.reduction_ratio,
                    "quality_score": result.quality_score,
                    "hausdorff_distance": result.hausdorff_distance,
                    "processing_time_ms": result.processing_time_ms
                }
            return {"status": "ERROR", "message": result.message}
        
        elif request.mode == "lod":
            result = optimizer.generate_lods(request.mesh_path, request.settings)
            if result.status == "OK":
                return {
                    "status": "OK",
                    "levels": [{"level": l.level, "triangle_count": l.triangle_count,
                               "vertex_count": l.vertex_count, "reduction_ratio": l.reduction_ratio,
                               "file_path": l.file_path, "quality_score": l.quality_score
                              } for l in result.levels],
                    "file_paths": result.file_paths,
                    "source_triangle_count": result.source_triangle_count,
                    "processing_time_ms": result.total_processing_time_ms
                }
            return {"status": "ERROR", "message": result.message}
        
        elif request.mode == "cull":
            result = optimizer.cull_geometry(mesh, request.settings)
            if result.status == "OK" and result.output_mesh:
                out_path = request.mesh_path.replace(".obj", "_culled.obj")
                result.output_mesh.export(out_path)
                return {
                    "status": "OK",
                    "mesh_path": out_path,
                    "original_count": result.original_count,
                    "culled_count": result.culled_count,
                    "faces_removed": result.faces_removed,
                    "processing_time_ms": result.processing_time_ms
                }
            return {"status": "ERROR", "message": result.message}
        
        else:
            return {"status": "ERROR", "message": f"Unknown mode: {request.mode}"}
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import trimesh
    uvicorn.run(app, host="0.0.0.0", port=8000)
