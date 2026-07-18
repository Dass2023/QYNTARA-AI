import asyncio
from backend.tasks.celery_app import celery_app
from backend.pipeline import QyntaraPipeline
from backend.analytics import AnalyticsService
from backend.models import *

def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)

@celery_app.task(bind=True)
def process_pipeline_task(self, request_dict: dict) -> dict:
    request = PipelineRequest(**request_dict)
    
    async def celery_progress(msg: str):
        self.update_state(state="PROGRESS", meta={"message": msg})
        
    pipeline = QyntaraPipeline(on_progress=celery_progress)
    analytics = AnalyticsService()
    
    async def _run():
        analytics.track_job(request.dict())
        
        if "sleep_test" in request.tasks:
            import time
            import redis
            import os
            r = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
            for i in range(10):
                if r.get(f"cancel_{self.request.id}"):
                    await celery_progress("Task cancelled by user.")
                    raise Exception("Task was cancelled")
                await celery_progress(f"Sleeping {i}/10...")
                time.sleep(1)
        
        # 1. Segmentation
        seg = await pipeline.run_sam_segmentation(request.meshes) if "segment" in request.tasks or "sam_segmentation" in request.tasks else SegmentationArtifacts()
        
        # 2. Validation
        val_report = ValidationReport(geometry=GeometryValidation(), uv=UVValidation(), material=MaterialValidation(), topology=TopologyValidation())
        if "validate" in request.tasks:
            val_result = await pipeline.run_validation(request.meshes, request.validation_profile)
            if val_result.get("status") == "success":
                for issue in val_result.get("issues", []):
                    desc = f"[{issue['object']}] {issue['description']}"
                    cat = issue['category']
                    if cat == "GEOMETRY": val_report.geometry.issues.append(desc)
                    elif cat == "UV": val_report.uv.issues.append(desc)
                    elif cat == "MATERIAL": val_report.material.shader_inconsistencies.append(desc)
                    elif cat == "NAMING": val_report.topology.issues.append(desc)
                val_report.passed = (val_result.get("score", 100) > 80)
                
        auto_val = await pipeline.run_autodesk_validation(request.meshes)
        
        # 3. UV Generation
        uv = UVOutput()
        if "uv" in request.tasks:
            if "lightmapuv" in request.tasks:
                request.uv_settings["mode"] = "LIGHTMAP"
            uv = await pipeline.run_uv_generation(request.meshes, settings=request.uv_settings)
            
        lm = LightmapUVOutput()
        dual = None
        
        # 4. Remeshing
        remesh = RemeshOutput(metrics=RemeshMetrics())
        if "quad_remesh" in request.tasks or "remesh" in request.tasks:
            remesh = await pipeline.run_quad_remeshing(request.meshes, request.remesh_settings)
            
        # 4b. LOD Generation
        lod = None
        if "lod" in request.tasks or "optimize" in request.tasks:
            try:
                from backend.generative.mesh_optimizer import MeshOptimizer
                optimizer = MeshOptimizer()
                lod_result = optimizer.generate_lods(request.meshes[0] if request.meshes else "backend/data/sample_cube.obj", request.optimize_settings)
                if lod_result.status == "OK":
                    lod = LODChainOutput(
                        status="OK",
                        message=lod_result.message,
                        levels=[LODLevelOutput(**{
                            "level": l.level, "triangle_count": l.triangle_count,
                            "vertex_count": l.vertex_count, "reduction_ratio": l.reduction_ratio,
                            "file_path": l.file_path, "screen_size": l.screen_size,
                            "quality_score": l.quality_score, "error_metric": l.error_metric
                        }) for l in lod_result.levels],
                        total_processing_time_ms=lod_result.total_processing_time_ms,
                        source_triangle_count=lod_result.source_triangle_count,
                        file_paths=lod_result.file_paths
                    )
            except Exception as e:
                print(f"[LOD] Generation failed: {e}")
                
        # 5. Material AI
        mat_prof = MaterialProfile()
        if "material" in request.tasks or "material_ai" in request.tasks:
            mat_result = await pipeline.run_material_pipeline(request.meshes, request.material_settings)
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
                gen = await pipeline.run_image_to_3d(input_image)
            else:
                quality = request.generative_settings.get("quality", "draft")
                gen = await pipeline.run_generative_3d(
                    request.generative_settings.get("prompt", ""), 
                    request.generative_settings.get("provider", "internal"),
                    quality=quality
                )
                
        # 7. Texture Generation
        tex_out = None
        if "texture_gen" in request.tasks:
            prompt = request.generative_settings.get("prompt", "")
            tex_out = await pipeline.run_texture_generation(prompt)
            
        # 8. Optimization & Export
        opt_export = {}
        exp_report = ExportComplianceReport(target_engine=request.engineTarget)
        if "export" in request.tasks or "optimization_export" in request.tasks:
            opt_result = await pipeline.run_advanced_export(request.meshes, request.export_settings)
            opt_export = opt_result
            if opt_result.get("status") == "success":
                exp_report.compliant = True
                exp_report.fixed_items = opt_result.get("files", [])
                
        analytics.track_job(request.dict())
        
        artifacts = QyntaraArtifacts(
            status="success",
            segmentation=seg,
            validationReport=val_report,
            autodeskValidation=auto_val,
            uvOutput=uv,
            lightmapUVOutput=lm,
            dualUVOutput=dual,
            remeshOutput=remesh,
            lodOutput=lod,
            materialProfile=mat_prof,
            generative3DOutput=gen,
            exportCompliance=exp_report,
            optimization_export=opt_export,
            textureOutput=tex_out
        )
        # Ensure it's purely json serializable
        return artifacts.model_dump()
        
    return run_async(_run())
