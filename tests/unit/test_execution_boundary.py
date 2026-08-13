import pytest
from unittest.mock import patch, MagicMock

from maya.execution_boundary import UndoChunk, MayaCommandRunner, MayaExecutionError

def test_undo_chunk_success():
    mock_cmds = MagicMock()
    with patch('maya.execution_boundary.cmds', mock_cmds):
        with UndoChunk("TestChunk"):
            pass
        
    mock_cmds.undoInfo.assert_any_call(openChunk=True, chunkName="TestChunk")
    mock_cmds.undoInfo.assert_any_call(closeChunk=True)

def test_undo_chunk_exception():
    mock_cmds = MagicMock()
    with patch('maya.execution_boundary.cmds', mock_cmds):
        try:
            with UndoChunk("TestChunk"):
                raise ValueError("Oops")
        except ValueError:
            pass
            
    mock_cmds.undoInfo.assert_any_call(openChunk=True, chunkName="TestChunk")
    mock_cmds.undoInfo.assert_any_call(closeChunk=True)

def test_runner_success():
    def success_op():
        return "result"
    
    result = MayaCommandRunner.execute(success_op)
    assert result == "result"

def test_runner_maya_error():
    def failure_op():
        raise RuntimeError("Maya failed")
    
    with pytest.raises(MayaExecutionError) as exc:
        MayaCommandRunner.execute(failure_op)
        
    assert "Maya failed" in str(exc.value)

def test_runner_other_error():
    def other_failure():
        raise TypeError("Bad type")
        
    # Should not be wrapped by MayaExecutionError
    with pytest.raises(TypeError):
        MayaCommandRunner.execute(other_failure)
