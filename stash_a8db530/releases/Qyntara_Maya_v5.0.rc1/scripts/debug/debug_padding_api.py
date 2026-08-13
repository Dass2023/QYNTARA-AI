import maya.api.OpenMaya as om
import maya.cmds as cmds

def debug_padding_api():
    sel = cmds.ls(sl=True, long=True)
    if not sel:
        print("Please select a mesh.")
        return

    obj_name = sel[0]
    print(f"\n--- Debugging Padding (API) for: {obj_name} ---")

    # Get DAG Path
    sl = om.MSelectionList()
    sl.add(obj_name)
    dag_path = sl.getDagPath(0)
    
    # MFnMesh
    fn_mesh = om.MFnMesh(dag_path)
    
    # Get UV Shell IDs (The Magic Function)
    # Returns (shell_count, shell_ids_array)
    # shell_ids_array is a list where index=uvId, value=shellId
    try:
        nb_shells, shell_ids = fn_mesh.getUvShellsIds(uvSet="map1")
        print(f"API Detected Shells: {nb_shells}")
    except Exception as e:
        print(f"API Failure: {e}")
        return

    if nb_shells < 2:
        print("Only 1 shell detected. Padding check N/A.")
        return

    # Get UV Coordinates
    u_array, v_array = fn_mesh.getUVs(uvSet="map1")
    
    # Group UVs by Shell
    # shells[shell_id] = {'u': [], 'v': []}
    shells_data = {}
    
    for i, shell_id in enumerate(shell_ids):
        if shell_id not in shells_data:
            shells_data[shell_id] = {'u': [], 'v': []}
        
        shells_data[shell_id]['u'].append(u_array[i])
        shells_data[shell_id]['v'].append(v_array[i])
        
    print(f"Grouped Data for {len(shells_data)} shells.")
    
    # Calculate AABBs
    shell_boxes = []
    padding_threshold = 0.002
    half_pad = padding_threshold / 2.0
    
    for sid, data in shells_data.items():
        min_u, max_u = min(data['u']), max(data['u'])
        min_v, max_v = min(data['v']), max(data['v'])
        
        shell_boxes.append({
            'id': sid,
            'min_u': min_u, 'max_u': max_u,
            'min_v': min_v, 'max_v': max_v
        })
        # print(f"Shell {sid} BB: [{min_u:.4f}, {max_u:.4f}] x [{min_v:.4f}, {max_v:.4f}]")

    # Check Intersections (Expanded)
    failed = False
    for i in range(len(shell_boxes)):
        for j in range(i + 1, len(shell_boxes)):
            s1 = shell_boxes[i]
            s2 = shell_boxes[j]
            
            # Expand
            u1_min, u1_max = s1['min_u'] - half_pad, s1['max_u'] + half_pad
            v1_min, v1_max = s1['min_v'] - half_pad, s1['max_v'] + half_pad
            
            u2_min, u2_max = s2['min_u'] - half_pad, s2['max_u'] + half_pad
            v2_min, v2_max = s2['min_v'] - half_pad, s2['max_v'] + half_pad
            
            # Intersect?
            intersect_u = (u1_min < u2_max) and (u2_min < u1_max)
            intersect_v = (v1_min < v2_max) and (v2_min < v1_max)
            
            if intersect_u and intersect_v:
                print(f"!!! FAIL: Shell {s1['id']} and {s2['id']} are too close!")
                failed = True
                break
        if failed: break
        
    if failed:
        print("RESULT: PADDING CHECK FAILED (Correct).")
    else:
        print("RESULT: PADDING CHECK PASSED (No overlaps found).")

debug_padding_api()
