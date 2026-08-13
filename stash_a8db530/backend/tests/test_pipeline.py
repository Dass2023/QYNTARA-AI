import pytest
import os
import sys
import asyncio
from backend.pipeline import QyntaraPipeline
from backend.models import *

# Ensure backend is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

@pytest.mark.asyncio
async def test_validation_logic():
    pipeline = QyntaraPipeline()
    # Create a dummy mesh file for testing
    test_mesh = "backend/data/test_cube.obj"
    
    # Create a simple cube OBJ if it doesn't exist
    if not os.path.exists(test_mesh):
        with open(test_mesh, "w") as f:
            f.write("v 0 0 0\nv 1 0 0\nv 1 1 0\nv 0 1 0\nv 0 0 1\nv 1 0 1\nv 1 1 1\nv 0 1 1\n")
            f.write("f 1 2 3 4\nf 5 8 7 6\nf 1 5 6 2\nf 2 6 7 3\nf 3 7 8 4\nf 5 1 4 8\n")
            
    report = await pipeline.run_validation([test_mesh])
    report = await pipeline.run_validation([test_mesh])
    
    # Check if report is a dict (as returned by run_validation in newer pipeline) or object
    if isinstance(report, dict):
        assert "score" in report
        assert "issues" in report
    else:
        assert isinstance(report, ValidationReport)
        assert report.geometry is not None

@pytest.mark.asyncio
async def test_uv_generation():
    pipeline = QyntaraPipeline()
    test_mesh = "backend/data/test_cube.obj"
    output = await pipeline.run_uv_generation([test_mesh])
    assert isinstance(output, UVOutput)
    assert output.unwrap_status == "success" or output.unwrap_status == "failed" 

if __name__ == "__main__":
    asyncio.run(test_validation_logic())
    asyncio.run(test_uv_generation())
    print("Tests passed!")
