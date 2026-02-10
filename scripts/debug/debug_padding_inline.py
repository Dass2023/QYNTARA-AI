
import maya.cmds as cmds

def debug_check_padding():
    selection = cmds.ls(sl=True, long=True)
    if not selection:
        print("Please select the mesh first.")
        return

    obj = selection[0]
    print(f"Checking Padding for: {obj}")

    padding_threshold = 0.002
    
    # 1. Get UVs
    all_uvs = cmds.ls(f"{obj}.map[:]", flatten=True)
    if not all_uvs:
        print("No UVs found.")
        return

    remaining_uvs = set(all_uvs)
    shells = []
    
    loop_limit = 200
    
    print(f"Total UVs: {len(all_uvs)}")
    
    while remaining_uvs and len(shells) < loop_limit:
        seed = next(iter(remaining_uvs))
        
        cmds.select(seed)
        cmds.polySelectBorderShell(0)
        shell_uvs = cmds.ls(sl=True, flatten=True)
        
        if not shell_uvs:
            remaining_uvs.discard(seed)
            continue

        for u in shell_uvs:
            if u in remaining_uvs:
                remaining_uvs.remove(u)
        
        us = cmds.polyEditUV(shell_uvs, q=True, u=True)
        vs = cmds.polyEditUV(shell_uvs, q=True, v=True)
        
        if not us or not vs: continue
        
        shells.append({
            'min_u': min(us), 'max_u': max(us),
            'min_v': min(vs), 'max_v': max(vs)
        })

    print(f"Found {len(shells)} shells.")
    
    # Check
    half_pad = padding_threshold / 2.0
    issues = 0
    
    for i in range(len(shells)):
        for j in range(i + 1, len(shells)):
            s1 = shells[i]
            s2 = shells[j]
            
            u1_min, u1_max = s1['min_u'] - half_pad, s1['max_u'] + half_pad
            v1_min, v1_max = s1['min_v'] - half_pad, s1['max_v'] + half_pad
            
            u2_min, u2_max = s2['min_u'] - half_pad, s2['max_u'] + half_pad
            v2_min, v2_max = s2['min_v'] - half_pad, s2['max_v'] + half_pad
            
            intersect_u = (u1_min < u2_max) and (u2_min < u1_max)
            intersect_v = (v1_min < v2_max) and (v2_min < v1_max)
            
            if intersect_u and intersect_v:
                print(f"FAIL: Shell {i} and {j} are touching/overlapping!")
                issues += 1
                
    if issues == 0:
        print("RESULT: PASS (No padding issues found)")
    else:
        print(f"RESULT: FAIL ({issues} conflicts found)")
        
debug_check_padding()
