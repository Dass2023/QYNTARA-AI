class SessionState:
    """
    Holds the application session state for QyntaraDockable.
    Extracted in Phase 1C to begin decoupling state from UI and Maya.
    """
    def __init__(self):
        self.uv_settings = {}
        self.last_result_path = None
