from bottle import Bottle, run, static_file, request, response
import json, os, time

app = Bottle()
os.makedirs("backend/data/uploads", exist_ok=True)

# CORS Middleware
@app.hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'PUT, GET, POST, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token, x-qyntara-key'

@app.route('/static/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='backend/data')

import random

@app.get('/stats')
def stats():
    return {
        "uptime_seconds": int(time.time()),
        "total_jobs": 42 + int(time.time() % 10),
        "total_polygons": 150000 + random.randint(0, 5000),
        "ai_tokens": 8000 + random.randint(0, 200),
        "active_nodes": random.randint(1, 5),
        "system_status": "SIMULATION_MODE"
    }

@app.post('/execute')
def execute():
    # Mock response matching QyntaraArtifacts model
    return {
        "status": "success",
        "segmentation": {"object_masks": [], "surface_semantic_zones": []},
        "validationReport": {
            "geometry": {"non_manifold_edges": 0},
            "uv": {"overlaps": 0},
            "material": {"missing_maps": []},
            "topology": {"valence_issues": 0},
            "passed": True
        },
        "autodeskValidation": {"status": "PASS", "checks": {}, "maya_compatible": True},
        "uvOutput": {"unwrap_status": "success", "packing_efficiency": 0.9},
        "lightmapUVOutput": {"uv2_status": "generated", "engine_target": "unity", "quality_metrics": {}},
        "remeshOutput": {"mesh_path": "sample_cube.obj", "metrics": {}},
        "materialProfile": {"classification": "standard"},
        "generative3DOutput": {"generated_mesh_path": "sample_cube.obj"},
        "exportCompliance": {"target_engine": "unity", "compliant": True}
    }

@app.post('/execute-visual')
def execute_visual():
    upload = request.files.get('file')
    filename = "unknown"
    if upload:
        filename = upload.filename
        upload.save(f"backend/data/uploads/{upload.filename}", overwrite=True)
    
    # Simulate processing delay
    time.sleep(1.5)
    
    return {
        "status": "success",
        "segmentation": {
            "detected_objects": ["helmet", "visor", "cables"],
            "confidence": 0.98,
            "style_analysis": "Cyberpunk / High-Tech"
        },
        "validationReport": {"passed": True, "details": "Geometry inferred from visual input."},
        "autodeskValidation": {"status": "PASS", "checks": {"topology": "OK"}, "maya_compatible": True},
        "uvOutput": {"status": "generated"},
        "lightmapUVOutput": {"status": "generated"},
        "remeshOutput": {"status": "completed"},
        "materialProfile": {"type": "PBR", "roughness": 0.4, "metallic": 0.8},
        "generative3DOutput": {"generated_mesh_path": "sample_cube.obj", "source_image": filename},
        "exportCompliance": {"compliant": True}
    }

# Mock WebSocket (not supported in Bottle standard server, frontend will fail gracefully or retry)

if __name__ == '__main__':
    print("Starting Qyntara AI Simulation Backend on port 8000...")
    run(app, host='0.0.0.0', port=8000, quiet=False)
