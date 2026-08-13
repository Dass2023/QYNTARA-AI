
# --- UV Set Manager Tools ---

def _gathe_mesh_shapes(objects):
    """Helper to get mesh shapes from selection or objects."""
    if not cmds: return []
    shapes = []
    for obj in objects:
        if cmds.objectType(obj) == 'transform':
            s = cmds.listRelatives(obj, s=True, ni=True, type='mesh')
            if s: shapes.extend(s)
        elif cmds.objectType(obj) == 'mesh':
            shapes.append(obj)
    return list(set(shapes))

def get_uv_sets(mesh):
    return cmds.polyUVSet(mesh, q=True, allUVSets=True) or []

def get_current_uv_set(mesh):
    res = cmds.polyUVSet(mesh, q=True, currentUVSet=True)
    return res[0] if res else None

def move_uv_set(objects, direction='up'):
    """
    Moves the current UV set up or down in the list.
    Direction: 'up' or 'down'
    """
    if not cmds: return
    shapes = _gathe_mesh_shapes(objects)
    
    for mesh in shapes:
        uv_sets = get_uv_sets(mesh)
        current_uv = get_current_uv_set(mesh)
        if not current_uv or current_uv not in uv_sets: continue

        index = uv_sets.index(current_uv)
        # In Maya's list, 'map1' is index 0. 
        # "Moving Up" usually means moving towards index 0 (top of list)? 
        # Or moving to higher index? 
        # The user provided script: swap_index = index - 1 if direction == 'up' else index + 1
        # So 'up' = lower index.
        
        swap_index = index - 1 if direction == 'up' else index + 1
        
        # Check bounds
        if swap_index < 0 or swap_index >= len(uv_sets): continue

        target_uv = uv_sets[swap_index]
        temp_uv = "__temp_uv__"
        
        # Safety cleanup
        if temp_uv in uv_sets:
            cmds.polyUVSet(mesh, delete=True, uvSet=temp_uv)

        try:
            # Swap logic using copy
            cmds.polyUVSet(mesh, create=True, uvSet=temp_uv)
            cmds.polyCopyUV(mesh, uvSetNameInput=current_uv, uvSetName=temp_uv, ch=False)
            cmds.polyCopyUV(mesh, uvSetNameInput=target_uv, uvSetName=current_uv, ch=False)
            cmds.polyCopyUV(mesh, uvSetNameInput=temp_uv, uvSetName=target_uv, ch=False)
            
            # Renaming to maintain names at new indices is tricky because renaming changes the name at the index.
            # Actually, standard Maya "Reorder" isn't exposed easily for UV sets without this swap dance.
            # The User's script renames them to swap names? 
            # User script:
            # cmds.polyUVSet(mesh, rename=True, uvSet=current_uv, newUVSet="__swapA__")
            # cmds.polyUVSet(mesh, rename=True, uvSet=target_uv, newUVSet=current_uv)
            # cmds.polyUVSet(mesh, rename=True, uvSet="__swapA__", newUVSet=target_uv)
            
            # This effectively swaps the NAMES and the CONTENT. 
            # So the set at index X gets name Y and content Y.
            
            cmds.polyUVSet(mesh, rename=True, uvSet=current_uv, newUVSet="__swapA__")
            cmds.polyUVSet(mesh, rename=True, uvSet=target_uv, newUVSet=current_uv)
            cmds.polyUVSet(mesh, rename=True, uvSet="__swapA__", newUVSet=target_uv)

            cmds.polyUVSet(mesh, delete=True, uvSet=temp_uv)
            
            # Restore selection
            cmds.polyUVSet(mesh, currentUVSet=True, uvSet=current_uv)
            
        except Exception as e:
            logger.error(f"Failed to move UV set on {mesh}: {e}")
            if cmds.objExists(f"{mesh}.uvSet[{temp_uv}]"):
                 cmds.polyUVSet(mesh, delete=True, uvSet=temp_uv)

def switch_uv_set_index(objects, index):
    if not cmds: return
    shapes = _gathe_mesh_shapes(objects)
    for mesh in shapes:
        uv_sets = get_uv_sets(mesh)
        if index < len(uv_sets):
            cmds.polyUVSet(mesh, currentUVSet=True, uvSet=uv_sets[index])

def add_new_uv_set(objects):
    if not cmds: return
    shapes = _gathe_mesh_shapes(objects)
    for mesh in shapes:
        existing_sets = get_uv_sets(mesh)
        base_name = "uvSet"
        i = 1
        while f"{base_name}{i}" in existing_sets:
            i += 1
        new_uv = f"{base_name}{i}"
        
        current_uv = get_current_uv_set(mesh)
        cmds.polyUVSet(mesh, create=True, uvSet=new_uv)
        if current_uv:
            cmds.polyCopyUV(mesh, uvSetNameInput=current_uv, uvSetName=new_uv, ch=False)
        cmds.polyUVSet(mesh, currentUVSet=True, uvSet=new_uv)

def delete_current_uv_set(objects):
    if not cmds: return
    shapes = _gathe_mesh_shapes(objects)
    for mesh in shapes:
        uv_sets = get_uv_sets(mesh)
        if len(uv_sets) <= 1: 
            logger.warning(f"Cannot delete the last UV set on {mesh}")
            continue
            
        current_uv = get_current_uv_set(mesh)
        cmds.polyUVSet(mesh, delete=True, uvSet=current_uv)
        
        # Set to first available
        remaining = get_uv_sets(mesh)
        if remaining:
            cmds.polyUVSet(mesh, currentUVSet=True, uvSet=remaining[0])

def rename_current_uv_set(objects, new_name):
    if not cmds: return
    shapes = _gathe_mesh_shapes(objects)
    for mesh in shapes:
        current_uv = get_current_uv_set(mesh)
        if not current_uv: continue
        
        if new_name in get_uv_sets(mesh):
            logger.warning(f"UV set '{new_name}' already exists on {mesh}")
            continue
            
        cmds.polyUVSet(mesh, rename=True, uvSet=current_uv, newUVSet=new_name)

def duplicate_current_uv_set(objects):
    if not cmds: return
    shapes = _gathe_mesh_shapes(objects)
    for mesh in shapes:
        uv_sets = get_uv_sets(mesh)
        current_uv = get_current_uv_set(mesh)
        if not current_uv: continue
        
        base = f"{current_uv}_copy"
        i = 1
        while f"{base}{i}" in uv_sets:
            i += 1
        new_uv = f"{base}{i}"
        
        cmds.polyUVSet(mesh, create=True, uvSet=new_uv)
        cmds.polyCopyUV(mesh, uvSetNameInput=current_uv, uvSetName=new_uv, ch=False)
        cmds.polyUVSet(mesh, currentUVSet=True, uvSet=new_uv)

def copy_uvs_to_others(source, targets):
    """
    Copies current UV set from source mesh to target meshes.
    Should handle topological mismatches by matching vertex IDs or map1? 
    The user script uses 'polyCopyUV' which usually requires identical topology 
    OR assumes transfer.
    User Script: cmds.polyCopyUV(ss=source_shape, ds=target_shape, ...)
    This copies the UVs.
    """
    if not cmds: return
    
    # Get source shape
    source_shapes = _gathe_mesh_shapes([source])
    if not source_shapes: return
    src_shape = source_shapes[0]
    
    src_uv = get_current_uv_set(src_shape)
    if not src_uv: return

    target_shapes = _gathe_mesh_shapes(targets)
    
    for tgt in target_shapes:
        if tgt == src_shape: continue
        try:
            tgt_uvs = get_uv_sets(tgt)
            # Create if missing
            if src_uv not in tgt_uvs:
                cmds.polyUVSet(tgt, create=True, uvSet=src_uv)
            
            # Copy
            cmds.polyCopyUV(src_shape, tgt, uvSetNameInput=src_uv, uvSetName=src_uv, ch=False)
            cmds.polyUVSet(tgt, currentUVSet=True, uvSet=src_uv)
            logger.info(f"Copied UVs from {src_shape} to {tgt}")
        except Exception as e:
            logger.warning(f"Failed to copy UVs to {tgt}: {e}")
