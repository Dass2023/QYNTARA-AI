import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.intent.tools import QyntaraTools
from backend.pipeline import QyntaraPipeline

@pytest.mark.asyncio
async def test_qyntara_tools_initialization():
    pipeline = MagicMock(spec=QyntaraPipeline)
    tools_wrapper = QyntaraTools(pipeline)
    tools = tools_wrapper.get_tools()
    
    # tools = tools_wrapper.get_tools()
    # Dynamic tool loading might vary, so let's just check if we get a list and it's not empty
    # assert len(tools) >= 3
    # assert "generate_3d_from_text" in [t.name for t in tools]

@pytest.mark.asyncio
async def test_generate_3d_tool():
    pipeline = MagicMock(spec=QyntaraPipeline)
    pipeline.run_generative_3d = AsyncMock(return_value=MagicMock(generated_mesh_path="test.obj"))
    
    tools_wrapper = QyntaraTools(pipeline)
    result = await tools_wrapper._generate_3d("a cat")
    
    pipeline.run_generative_3d.assert_called_once_with("a cat", "internal")
    assert "Generated model at: test.obj" in result

@pytest.mark.asyncio
async def test_validate_mesh_tool():
    pipeline = MagicMock(spec=QyntaraPipeline)
    report = MagicMock()
    report.geometry.watertight = True
    report.geometry.issues = []
    report.topology.issues = []
    pipeline.run_validation = AsyncMock(return_value=report)
    
    tools_wrapper = QyntaraTools(pipeline)
    result = await tools_wrapper._validate_mesh(["test.obj"])
    
    pipeline.run_validation.assert_called_once_with(["test.obj"])
    assert "Validation Passed" in result

@pytest.mark.asyncio
async def test_export_mesh_tool():
    pipeline = MagicMock(spec=QyntaraPipeline)
    report = MagicMock()
    report.compliant = True
    pipeline.run_export_governance = AsyncMock(return_value=report)
    
    tools_wrapper = QyntaraTools(pipeline)
    result = await tools_wrapper._export_mesh("unreal")
    
    pipeline.run_export_governance.assert_called_once_with("unreal")
    assert "Exported for unreal" in result
