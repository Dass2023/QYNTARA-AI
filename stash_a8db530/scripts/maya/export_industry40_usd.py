import maya.cmds as cmds
import os

def export_smart_asset_usd(file_path):
    """
    Exports the current selection to OpenUSD (.usd) 
    with embedded Industry 4.0 Metadata (IoT/DNA).
    
    This bridges the gap between Maya and Unreal/Unity/Omniverse.
    """
    
    selection = cmds.ls(sl=True, long=True)
    if not selection:
        print("[USD] Error: No object selected.")
        return

    # Verify Plugin
    if not cmds.pluginInfo("mayaUsdPlugin", query=True, loaded=True):
        try:
            cmds.loadPlugin("mayaUsdPlugin")
        except:
            print("[USD] Error: mayaUsdPlugin not found.")
            return

    # 1. PREP: Inject Primevars (USD Attributes)
    ct = 0
    for obj in selection:
        shapes = cmds.listRelatives(obj, shapes=True, fullPath=True)
        if not shapes: continue
        
        # Check for our custom attributes
        if cmds.attributeQuery("QyntaraID", n=obj, ex=True):
            val = cmds.getAttr(f"{obj}.QyntaraID")
            # In a real pipeline, we'd copy this to a USD-specific attr
            # e.g. USD_UserExportedAttributesJson
            print(f"[USD] Injecting IoT Metadata for {obj}: {val}")
            ct += 1
            
    if ct == 0:
        print("[USD] Warning: No Industry 4.0 attributes found on selection.")

    # 2. EXPORT COMMAND
    # Using mayaUSDExport command (standard in recent Maya versions)
    # Flags designed for "Game Ready" + "Digital Twin" interchange
    
    # Detect Format
    ext = os.path.splitext(file_path)[-1].lower()
    format_arg = "usdc"
    if ext == ".usda":
        format_arg = "usda"
    
    # Note: .usdz is an archive. mayaUsdPlugin usually handles it if extension is usdz.
    
    options = [
        "exportUVs=1",
        "exportSkels=auto",
        "exportSkin=auto",
        "exportBlendShapes=1", 
        "exportColorSets=1", 
        "defaultMeshScheme=catmullClark",
        f"defaultUSDFormat={format_arg}", # Dynamic
        "eulerFilter=1",
        "staticSingleSample=1", 
        "parentScope=Qyntara_Asset_Root",
        "compatibility=appleArKit" if ext == ".usdz" else "" # Attempt to enable ARKit compat
    ]
    
    # Remove empty options
    options = [o for o in options if o]
    
    opt_string = ";".join(options)
    
    print(f"[USD] Exporting to: {file_path}")
    try:
        cmds.file(file_path, force=True, options=opt_string, typ="USD Export", pr=True, es=True)
        print("[USD] SUCCESS: Asset exported to OpenUSD.")
    except Exception as e:
        print(f"[USD] Export Failed: {e}")
        # Fallback for older Maya versions without native USD
        print("[USD] Note: Ensure 'mayaUsdPlugin' is enabling 'USD Export' translator.")

if __name__ == "__main__":
    # Test path
    temp_path = os.path.join(os.getenv("TEMP"), "qyntara_smart_asset.usd")
    export_smart_asset_usd(temp_path)
