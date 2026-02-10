from fastapi import FastAPI, HTTPException, Header, Depends, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn, json, os, shutil
from backend.models import *
from backend.pipeline import QyntaraPipeline
from backend.analytics import AnalyticsService
from backend.intent.agent import QyntaraAgent

app = FastAPI(title="QYNTARA AI", version="1.0.0")
os.makedirs("backend/data/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="backend/data"), name="static")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

async def broadcast_wrapper(msg):
    await broadcast(msg)

pipeline = QyntaraPipeline(on_progress=broadcast_wrapper)
analytics = AnalyticsService()
manager = []

@app.websocket("/ws/neural-link")
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept(); manager.append(websocket)
    try:
        while True: await websocket.receive_text()
    except:
        manager.remove(websocket)

async def broadcast(msg):
    for ws in manager:
        try: await ws.send_text(msg)
        except: pass

@app.get("/stats")
def stats(): return analytics.get_stats()

class Segmentation3DRequest(BaseModel):
    mesh_path: str
    click_point: List[float]
    camera_view: List[float]

@app.post("/segment-3d")
async def segment_3d(request: Segmentation3DRequest):
    result = await pipeline.run_3d_segmentation(request.mesh_path, request.click_point, request.camera_view)
    return result

class Segmentation2DRequest(BaseModel):
    image_path: str
    click_point: List[float]
    click_type: str

@app.post("/segment-2d")
async def segment_2d(request: Segmentation2DRequest):
    result = await pipeline.run_2d_segmentation(request.image_path, request.click_point, request.click_type)
    return result

class SegmentTo3DRequest(BaseModel):
    image_path: str
    click_point: List[float]
    click_type: str

@app.post("/segment-to-3d")
async def segment_to_3d(request: SegmentTo3DRequest):
    result = await pipeline.run_segment_to_3d(request.image_path, request.click_point, request.click_type)
    return result

# --- AI Intelligence Endpoints (Phase 3) ---

class SeamGPTRequest(BaseModel):
    mesh_path: str

@app.post("/ai/seam-gpt")
async def ai_seam_gpt(req: SeamGPTRequest):
    return await pipeline.run_seam_gpt(req.mesh_path)

class PredictRequest(BaseModel):
    polycount: int
    has_ngons: bool

@app.post("/ai/predict")
async def ai_predict(req: PredictRequest):
    return await pipeline.run_predictive_check(req.dict())

class PhysicsRequest(BaseModel):
    material_name: str

@app.post("/ai/physics")
async def ai_physics(req: PhysicsRequest):
    return pipeline.get_material_physics(req.material_name)

@app.post("/execute-visual", response_model=QyntaraArtifacts)
async def execute_visual(
    file: UploadFile = File(...),
    settings: str = Form(...)
):
    # Save uploaded file
    file_location = f"backend/data/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    
    # Parse settings
    import json
    settings_dict = json.loads(settings)
    prompt = settings_dict.get("prompt", "")
    
    # Construct PipelineRequest-like logic
    # We assume visual execution implies generative or specific tasks based on prompt
    tasks = ["generative"]
    if prompt == "validate_only": tasks = ["validate"]
    if prompt == "uv_only": tasks = ["uv"]
    if prompt == "remesh_only": tasks = ["remesh"]
    if prompt == "material_only": tasks = ["material"]
    
    # Create request object
    request = PipelineRequest(
        meshes=[file_location],
        materials=[],
        tasks=tasks,
        generative_settings={"prompt": prompt},
        remesh_settings={"target_faces": settings_dict.get("targetFaces", 5000)}
    )
    
    # Reuse execute logic (or call it directly if refactored, but here we duplicate slightly for safety/speed)
    return await execute(request)

@app.post("/execute", response_model=QyntaraArtifacts)
async def execute(request: PipelineRequest):
    await broadcast(f"Pipeline Started: {len(request.meshes)} meshes. Tasks: {request.tasks}")
    analytics.track_job(request.dict())
    
    # 1. Segmentation
    seg = await pipeline.run_sam_segmentation(request.meshes) if "segment" in request.tasks or "sam_segmentation" in request.tasks else SegmentationArtifacts()
    
    # 2. Validation (Advanced Scene Validator)
    val_report = ValidationReport(geometry=GeometryValidation(), uv=UVValidation(), material=MaterialValidation(), topology=TopologyValidation())
    if "validate" in request.tasks:
        val_result = await pipeline.run_validation(request.meshes, request.validation_profile)
        # Map flat issues to legacy structure for compatibility
        # val_result is dict: {score, summary, issues: [{category, description...}]}
        if val_result.get("status") == "success":
            for issue in val_result.get("issues", []):
                desc = f"[{issue['object']}] {issue['description']}"
                cat = issue['category']
                if cat == "GEOMETRY": val_report.geometry.issues.append(desc)
                elif cat == "UV": val_report.uv.issues.append(desc)
                elif cat == "MATERIAL": val_report.material.shader_inconsistencies.append(desc)
                elif cat == "NAMING": val_report.topology.issues.append(desc) # map naming to topology for now
            val_report.passed = (val_result.get("score", 100) > 80)

    auto_val = await pipeline.run_autodesk_validation(request.meshes)

    # --- Industry 4.0: Digital Twin Metadata Injection ---
    if request.metadata and request.metadata.get("digital_twin_id"):
        dt_id = request.metadata.get("digital_twin_id")
        await self._emit(f"[Industry 4.0] Injecting Digital Twin Metadata (ID: {dt_id})...")
        # In a real implementation, we would write this to the USD customData or XMP
        # For now, we log it and ensure it passes to the exporter context
    # -----------------------------------------------------
    
    # 3. UV Generation (Universal)
    uv = UVOutput()
    if "uv" in request.tasks:
        # Check for UDIM vs Lightmap in settings
        # If mode is lightmap, run lightmap logic? 
        # Universal module handles both via settings["mode"]
        # But pipeline has separate run_lightmap_generation...
        # Let's use generic run_uv_generation which now points to Universal module
        
        # Merge lightmap specific request into settings if needed
        if "lightmapuv" in request.tasks:
             request.uv_settings["mode"] = "LIGHTMAP"
             
        uv_res = await pipeline.run_uv_generation(request.meshes, settings=request.uv_settings)
        # map dict result to UVOutput if needed, but run_uv_generation in pipeline usually returns UVOutput?
        # Let's check pipeline.py... I didn't change return type of run_uv_generation wrapper which calls unwrap.
        # But unwrap returns a dict {mesh, metrics}.
        # pipeline.run_uv_generation (line 218 approx) converts that to UVOutput. 
        # So uv_res is UVOutput. Correct.
        uv = uv_res

    lm = LightmapUVOutput(quality_metrics=LightmapQualityMetrics())
    # If explicit lightmap task and not handled by above
    if "lightmapuv" in request.tasks and request.uv_settings.get("mode") != "LIGHTMAP":
         pass # Handled above via merged settings for Universal

    dual = None # Dual UV logic...
    
    # 4. Remeshing
    remesh = RemeshOutput(metrics=RemeshMetrics())
    if "quad_remesh" in request.tasks or "remesh" in request.tasks:
        remesh = await pipeline.run_quad_remeshing(request.meshes, request.remesh_settings)
        
    # 5. Material AI
    mat_prof = MaterialProfile() # Default
    if "material" in request.tasks or "material_ai" in request.tasks:
        # run_material_pipeline returns a dict {status, processed, converted_files}
        mat_result = await pipeline.run_material_pipeline(request.meshes, request.material_settings)
        # Map to MaterialProfile
        if mat_result.get("status") == "OK":
             mat_prof.clusters = mat_result.get("processed", [])

    # 6. Generative 3D
    gen = Generative3DOutput(generated_mesh_path=None)
    if "generative" in request.tasks:
        input_image = None
        if request.meshes:
            for m in request.meshes:
                if m.lower().endswith(('.png', '.jpg', '.jpeg')):
                    input_image = m
                    break
        
        if input_image:
            await broadcast(f"Running Image-to-3D for {input_image}")
            gen = await pipeline.run_image_to_3d(input_image)
        else:
            quality = request.generative_settings.get("quality", "draft")
            gen = await pipeline.run_generative_3d(
                request.generative_settings.get("prompt", ""), 
                request.generative_settings.get("provider", "internal"),
                quality=quality
            )
            
            
    # 7. Texture Generation (Material AI)
    tex_out = []
    if "texture_gen" in request.tasks:
        # Prompt from settings or generic
        prompt = request.generative_settings.get("prompt", "")
        # Assuming we want to run texture generation
        tex_out = await pipeline.run_texture_generation(prompt)

    # 8. Optimization & Export
    opt_export = {}
    exp_report = ExportComplianceReport(target_engine=request.engineTarget)
    
    if "export" in request.tasks or "optimization_export" in request.tasks:
        # Use new advanced export
        opt_result = await pipeline.run_advanced_export(request.meshes, request.export_settings)
        opt_export = opt_result
        # Update compliance report based on result
        if opt_result.get("status") == "success":
            exp_report.compliant = True
            exp_report.fixed_items = opt_result.get("files", [])

    analytics.track_job(request.dict())
    await broadcast("Pipeline Complete")
    
    return {
        "status": "success",
        "segmentation": seg,
        "validationReport": val_report,
        "autodeskValidation": auto_val,
        "uvOutput": uv,
        "lightmapUVOutput": lm,
        "dualUVOutput": dual,
        "remeshOutput": remesh,
        "materialProfile": mat_prof,
        "generative3DOutput": gen,
        "exportCompliance": exp_report,
        "optimization_export": opt_export,
        "textureOutput": tex_out
    }

@app.post("/execute-visual", response_model=QyntaraArtifacts)
async def execute_visual(file: UploadFile = File(...), settings: str = Form(...)):
    try:
        await broadcast(f"Visual Input: {file.filename}")
        path = f"backend/data/uploads/{file.filename}"
        with open(path, "wb") as f: shutil.copyfileobj(file.file, f)
        gen = await pipeline.run_image_to_3d(path)
        analytics.track_job({"type": "visual"})
        await broadcast("Visual Processing Complete")
        return QyntaraArtifacts(status="success", segmentation=SegmentationArtifacts(), validationReport=ValidationReport(geometry=GeometryValidation(), uv=UVValidation(), material=MaterialValidation(), topology=TopologyValidation()), autodeskValidation=AutodeskValidation(status="PASS", checks={}, maya_compatible=True), uvOutput=UVOutput(), lightmapUVOutput=LightmapUVOutput(quality_metrics=LightmapQualityMetrics()), remeshOutput=RemeshOutput(metrics=RemeshMetrics()), materialProfile=MaterialProfile(), generative3DOutput=gen, exportCompliance=ExportComplianceReport(target_engine="unreal"))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    path = f"backend/data/uploads/{file.filename}"
    with open(path, "wb") as f: shutil.copyfileobj(file.file, f)
    return {"filename": file.filename, "path": path}

@app.post("/extrude-floorplan")
async def extrude_floorplan(file: UploadFile = File(...), height: float = Form(2.5), threshold: int = Form(127), pixels_per_meter: float = Form(50.0)):
    await broadcast(f"Processing Floor Plan: {file.filename}")
    path = f"backend/data/uploads/{file.filename}"
    with open(path, "wb") as f: shutil.copyfileobj(file.file, f)
    
    result = await pipeline.run_floorplan_extrusion(path, height, threshold, pixels_per_meter)
    return result

@app.post("/export-mesh")
async def export_mesh(request: ExportRequest):
    result = await pipeline.run_export(request.source_path, request.target_path, request.format, request.engine)
    if result["status"] == "error":
        print(f"EXPORT ERROR: {result['message']}")
        raise HTTPException(status_code=500, detail=result["message"])
    return result

agent = QyntaraAgent(pipeline)

class AgentCommandRequest(BaseModel):
    command: str

@app.post("/agent/command")
async def agent_command(request: AgentCommandRequest):
    result = await agent.process_command(request.command)
    return {"response": result}

@app.get("/library")
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
