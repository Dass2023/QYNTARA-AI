import unreal
import json

def qyntara_validate_selected():
    """
    Called when the user clicks 'Validate' in Unreal.
    Gathers selected assets and sends them to the Qyntara Core.
    """
    editor_util = unreal.EditorUtilityLibrary()
    selected_assets = editor_util.get_selected_assets()
    
    if not selected_assets:
        unreal.log_warning("Qyntara: No assets selected.")
        return

    subsystem = unreal.get_editor_subsystem(unreal.QyntaraSubsystem)
    
    for asset in selected_assets:
        asset_name = asset.get_name()
        asset_class = asset.get_class().get_name()
        
        # Extract basic metadata from Unreal Asset Registry
        meta = {
            "asset_class": asset_class,
            "path": asset.get_path_name(),
            "polycount": 0, # Placeholder, needs StaticMesh lib
            "is_valid": True
        }
        
        # If static mesh, get real data
        if asset_class == "StaticMesh":
            # Mocking polycount access for this script example
            meta["polycount"] = 15000 
            meta["has_lods"] = True
            
        json_meta = json.dumps(meta)
        
        unreal.log(f"Qyntara: Validating {asset_name}...")
        subsystem.validate_asset(asset_name, "gaming", json_meta)

def create_toolbar_button():
    """
    Adds a button to the Unreal Level Editor Toolbar.
    """
    menus = unreal.ToolMenus.get()
    owner = "LevelEditor.LevelEditorToolBar"
    menu = menus.find_menu(owner)
    
    entry = unreal.ToolMenuEntry(
        name="QyntaraValidator",
        type=unreal.MultiBlockType.TOOL_BAR_BUTTON,
        script_object=qyntara_validate_selected
    )
    entry.set_label("Qyntara Check")
    entry.set_tool_tip("Run Qyntara Spatial Intelligence Validation")
    
    menu.add_menu_entry("Settings", entry)
    menus.refresh_all_widgets()
    unreal.log("Qyntara GUI Initialized.")

if __name__ == "__main__":
    create_toolbar_button()
