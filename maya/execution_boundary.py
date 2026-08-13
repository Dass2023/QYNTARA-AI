try:
    import maya.cmds as cmds
except ImportError:
    cmds = None

class MayaExecutionError(Exception):
    """Raised when a Maya command fails unexpectedly."""
    pass

class UndoChunk:
    """
    Context manager to safely encapsulate Maya operations in an undo chunk.
    Ensures the chunk is closed even if an exception occurs.
    """
    def __init__(self, name="QyntaraOperation"):
        self.name = name

    def __enter__(self):
        if cmds:
            cmds.undoInfo(openChunk=True, chunkName=self.name)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if cmds:
            cmds.undoInfo(closeChunk=True)
        # Do not swallow exceptions
        return False

class MayaCommandRunner:
    """
    Centralized execution boundary for Maya operations.
    Translates raw Maya RuntimeError into a structured MayaExecutionError.
    Does not swallow exceptions.
    """
    @staticmethod
    def execute(func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except RuntimeError as e:
            # Maya throws RuntimeError for most command failures
            raise MayaExecutionError(f"Maya operation failed: {str(e)}") from e
