"""
Authoritative single-source-of-truth industry key mapping for Qyntara Nexus.
Bidirectionally maps UI display labels to canonical backend industry keys.
"""

UI_LABEL_TO_INDUSTRY_KEY = {
    "Gaming": "gaming",
    "Film / VFX": "film",
    "Automotive": "automotive",
    "Architecture / BIM": "architecture",
    "Medical": "medical",
    "Aerospace / Defense": "aerospace",
    "XR / Metaverse": "xr",
    "E-Commerce": "ecommerce",
    "Robotics": "robotics",
    "Industry 4.0": "industry4",
    "Industry 5.0": "industry5",
    "3D Printing": "printing",
}

# Derived reverse mapping (guaranteed 1:1 round-trip consistency)
INDUSTRY_KEY_TO_UI_LABEL = {v: k for k, v in UI_LABEL_TO_INDUSTRY_KEY.items()}

def get_canonical_key(ui_label: str) -> str:
    """Resolves UI display label to canonical backend industry key."""
    if ui_label not in UI_LABEL_TO_INDUSTRY_KEY:
        raise KeyError(f"Unknown UI industry label: '{ui_label}'")
    return UI_LABEL_TO_INDUSTRY_KEY[ui_label]

def get_ui_label(canonical_key: str) -> str:
    """Resolves canonical backend industry key to UI display label."""
    if canonical_key not in INDUSTRY_KEY_TO_UI_LABEL:
        raise KeyError(f"Unknown canonical industry key: '{canonical_key}'")
    return INDUSTRY_KEY_TO_UI_LABEL[canonical_key]

def validate_mapping_integrity() -> bool:
    """Validates 1:1 bidirectional invariants for all 12 industries."""
    if len(UI_LABEL_TO_INDUSTRY_KEY) != 12:
        raise ValueError(f"Mapping must contain exactly 12 items, found {len(UI_LABEL_TO_INDUSTRY_KEY)}")
    if len(INDUSTRY_KEY_TO_UI_LABEL) != 12:
        raise ValueError("Mapping keys and values must be strictly unique 1:1 pairs")
    for label, key in UI_LABEL_TO_INDUSTRY_KEY.items():
        if get_ui_label(key) != label:
            raise ValueError(f"Roundtrip failed for label '{label}' -> key '{key}'")
        if get_canonical_key(label) != key:
            raise ValueError(f"Roundtrip failed for key '{key}' -> label '{label}'")
    return True

# Enforce validation on module load
validate_mapping_integrity()
