import logging
from functools import wraps
try:
    from maya import cmds
except ImportError:
    cmds = None

logger = logging.getLogger(__name__)

# Global flag to prevent nested Maya chunks from crashing the API
_ACTIVE_UNDO_CHUNK = False

def undo_chunk(name="QyntaraAction"):
    """
    Deprecated decorator. Use UndoContext instead.
    """
    if callable(name):
        return name
    else:
        def decorator(func):
            return func
        return decorator

class UndoContext:
    """Context manager for Maya Undo Chunks with nested safety."""
    def __init__(self, name="QyntaraAction"):
        self.name = name
        self.is_nested = False
    
    def __enter__(self):
        global _ACTIVE_UNDO_CHUNK
        if _ACTIVE_UNDO_CHUNK:
            self.is_nested = True
        else:
            _ACTIVE_UNDO_CHUNK = True
            if cmds:
                cmds.undoInfo(openChunk=True, chunkName=self.name)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        global _ACTIVE_UNDO_CHUNK
        if not self.is_nested:
            _ACTIVE_UNDO_CHUNK = False
            if cmds:
                cmds.undoInfo(closeChunk=True)
