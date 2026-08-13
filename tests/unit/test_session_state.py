import pytest
from maya.session_state import SessionState

def test_session_state_defaults():
    state = SessionState()
    assert state.uv_settings == {}
    assert state.last_result_path is None

def test_session_state_updates():
    state = SessionState()
    state.uv_settings = {"mode": "auto", "resolution": 1024}
    state.last_result_path = "/path/to/result.obj"
    
    assert state.uv_settings["mode"] == "auto"
    assert state.uv_settings["resolution"] == 1024
    assert state.last_result_path == "/path/to/result.obj"

def test_session_state_independent():
    state1 = SessionState()
    state2 = SessionState()
    
    state1.uv_settings["mode"] = "manual"
    state2.uv_settings["mode"] = "auto"
    
    assert state1.uv_settings["mode"] == "manual"
    assert state2.uv_settings["mode"] == "auto"
