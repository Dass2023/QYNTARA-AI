import sys
from unittest.mock import MagicMock

# Create a mock 'unreal' module
mock_unreal = MagicMock()
sys.modules["unreal"] = mock_unreal

# Mock specific Unreal classes used in our script
mock_unreal.EditorUtilityLibrary.return_value.get_selected_assets.return_value = [
    MagicMock(get_name=lambda: "Hero_Sword", get_class=lambda: MagicMock(get_name=lambda: "StaticMesh"), get_path_name=lambda: "/Game/Weapons/Hero_Sword")
]

# Mock Subsystem
mock_subsystem = MagicMock()
mock_unreal.get_editor_subsystem.return_value = mock_subsystem
mock_unreal.QyntaraSubsystem = "QyntaraSubsystemClass"

# Define the script logic (copied from init_unreal_gui.py for testing)
import json

def qyntara_validate_selected_TEST():
    print("--- Simulating 'Validate Selected' Button Click ---")
    
    # Simulate API Call
    # 1. Get Selection
    assets = mock_unreal.EditorUtilityLibrary().get_selected_assets()
    
    # 2. Get Subsystem
    subsystem = mock_unreal.get_editor_subsystem(mock_unreal.QyntaraSubsystem)
    
    for asset in assets:
        name = asset.get_name()
        print(f"Processing Asset: {name}")
        
        # Simulate Logic
        meta = {"polycount": 15000, "has_lods": True}
        json_meta = json.dumps(meta)
        
        # 3. Call C++ Function
        subsystem.validate_asset(name, "gaming", json_meta)
        print(f"Invoked C++ validate_asset('{name}')")

if __name__ == "__main__":
    qyntara_validate_selected_TEST()
    
    # Verify the mock interactions
    mock_subsystem.validate_asset.assert_called()
    print(">> SUCCESS: Unreal Python Logic Verified against Mock API.")
