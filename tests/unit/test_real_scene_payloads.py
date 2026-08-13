"""
Targeted Unit Tests for D-007 / D-013 Real Scene Payload Telemetry (Zero Randomness)
"""

import pytest
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

MAYA_DIR = os.path.join(PROJECT_ROOT, "maya")
if MAYA_DIR not in sys.path:
    sys.path.insert(0, MAYA_DIR)

from maya.qyntara_client import extract_real_scene_payload

def test_extract_real_scene_payload_gaming():
    payload = extract_real_scene_payload("gaming")
    assert "polycount" in payload
    assert "has_lods" in payload
    assert payload["shader_instructions"] is None
    assert payload["provenance"]["polycount"] == "REAL_MAYA_MEASUREMENT"
    assert payload["provenance"]["shader_instructions"] == "NOT_AVAILABLE"

def test_extract_real_scene_payload_medical():
    payload = extract_real_scene_payload("medical")
    assert "is_manifold" in payload
    assert "bbox_diagonal" in payload
    assert payload["provenance"]["is_manifold"] == "REAL_MAYA_MEASUREMENT"

def test_extract_real_scene_payload_film():
    payload = extract_real_scene_payload("film")
    assert "poles" in payload
    assert payload["provenance"]["poles"] == "REAL_MAYA_MEASUREMENT"

def test_extract_real_scene_payload_printing():
    payload = extract_real_scene_payload("printing")
    assert "critical_overhangs" in payload
    assert payload["provenance"]["critical_overhangs"] == "REAL_MAYA_MEASUREMENT"

def test_all_12_industries_zero_randomness():
    industries = [
        "gaming", "film", "automotive", "architecture", "medical",
        "aerospace", "xr", "ecommerce", "robotics", "industry4",
        "industry5", "printing"
    ]
    for key in industries:
        payload1 = extract_real_scene_payload(key)
        payload2 = extract_real_scene_payload(key)
        # Verify 100% deterministic results across multiple calls
        assert payload1 == payload2, f"Nondeterministic payload detected for industry {key}"
        assert "provenance" in payload1, f"Missing provenance for industry {key}"
