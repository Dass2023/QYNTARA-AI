import pytest
from maya.industry_mapping import (
    UI_LABEL_TO_INDUSTRY_KEY,
    INDUSTRY_KEY_TO_UI_LABEL,
    get_canonical_key,
    get_ui_label,
    validate_mapping_integrity
)

def test_exact_12_labels_and_keys():
    assert len(UI_LABEL_TO_INDUSTRY_KEY) == 12
    assert len(INDUSTRY_KEY_TO_UI_LABEL) == 12

def test_no_duplicate_keys():
    keys = list(UI_LABEL_TO_INDUSTRY_KEY.values())
    assert len(keys) == len(set(keys))

def test_forward_mapping():
    assert get_canonical_key("Gaming") == "gaming"
    assert get_canonical_key("Film / VFX") == "film"
    assert get_canonical_key("Automotive") == "automotive"
    assert get_canonical_key("Architecture / BIM") == "architecture"
    assert get_canonical_key("Medical") == "medical"
    assert get_canonical_key("Aerospace / Defense") == "aerospace"
    assert get_canonical_key("XR / Metaverse") == "xr"
    assert get_canonical_key("E-Commerce") == "ecommerce"
    assert get_canonical_key("Robotics") == "robotics"
    assert get_canonical_key("Industry 4.0") == "industry4"
    assert get_canonical_key("Industry 5.0") == "industry5"
    assert get_canonical_key("3D Printing") == "printing"

def test_reverse_mapping():
    assert get_ui_label("gaming") == "Gaming"
    assert get_ui_label("film") == "Film / VFX"
    assert get_ui_label("automotive") == "Automotive"
    assert get_ui_label("architecture") == "Architecture / BIM"
    assert get_ui_label("medical") == "Medical"
    assert get_ui_label("aerospace") == "Aerospace / Defense"
    assert get_ui_label("xr") == "XR / Metaverse"
    assert get_ui_label("ecommerce") == "E-Commerce"
    assert get_ui_label("robotics") == "Robotics"
    assert get_ui_label("industry4") == "Industry 4.0"
    assert get_ui_label("industry5") == "Industry 5.0"
    assert get_ui_label("printing") == "3D Printing"

def test_forward_reverse_roundtrip():
    for label, key in UI_LABEL_TO_INDUSTRY_KEY.items():
        # label -> key -> label
        resolved_key = get_canonical_key(label)
        assert resolved_key == key
        assert get_ui_label(resolved_key) == label

def test_reverse_forward_roundtrip():
    for key, label in INDUSTRY_KEY_TO_UI_LABEL.items():
        # key -> label -> key
        resolved_label = get_ui_label(key)
        assert resolved_label == label
        assert get_canonical_key(resolved_label) == key

def test_unknown_label_fails_safely():
    with pytest.raises(KeyError) as exc_info:
        get_canonical_key("Unknown Industry Label")
    assert "Unknown UI industry label" in str(exc_info.value)

def test_unknown_key_fails_safely():
    with pytest.raises(KeyError) as exc_info:
        get_ui_label("unknown_key")
    assert "Unknown canonical industry key" in str(exc_info.value)

def test_validate_mapping_integrity_function():
    assert validate_mapping_integrity() is True

def test_d011_professional_terminology_standardized():
    from maya.qyntara_client import IndustryRoadmapDialog
    from PySide2 import QtWidgets
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    dlg = IndustryRoadmapDialog(None)
    data = dlg.data
    
    assert data["Automotive"]["current"] == "CAD Surface & Sensor Compliance"
    assert data["Aerospace / Defense"]["current"] == "Structural Stress & PMI Verification"
    assert data["Robotics"]["current"] == "Collision Convexity & Kinematics"
    assert data["Industry 4.0"]["current"] == "AAS & IoT Digital Twin Integration"
    assert data["XR / Metaverse"]["future_val"][1][1] == "Refresh Rate Impact: Evaluates 90Hz target frame rate"
    assert data["E-Commerce"]["future_val"][0][1] == "File Size Optimizer: Validates web asset target < 5 MB [Implemented]"

