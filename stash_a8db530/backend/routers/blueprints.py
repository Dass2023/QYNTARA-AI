from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from backend.blueprints.processor import BlueprintProcessor
import shutil
import os
import uuid

router = APIRouter()
processor = BlueprintProcessor()

@router.post("/extrude-floorplan")
async def extrude_floorplan(
    file: UploadFile = File(...),
    height: float = Form(2.5),
    pixels_per_meter: float = Form(50.0),
    threshold: int = Form(127)
):
    try:
        # Save temp file
        temp_dir = "backend/data/temp"
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, f"{uuid.uuid4()}_{file.filename}")
        
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process
        mesh_path, dxf_path = processor.process_floorplan(
            temp_path, 
            wall_height=height, 
            px_per_meter=pixels_per_meter, 
            threshold=threshold
        )

        return {
            "status": "success",
            "mesh_path": mesh_path,
            "dxf_path": dxf_path
        }

    except Exception as e:
        print(f"Blueprint Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup temp upload if needed, but keeping for debug might be good for now
        pass
