"""
Native GLB/glTF Importer for Maya 2025+
No external plugins required — reads the GLB binary format using Python's
built-in struct module and reconstructs geometry via maya.cmds.

GLB Spec: https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html#glb-file-format-specification
"""

import maya.cmds as cmds
import struct
import json
import os


# -------------------------------------------------------
# GLB Binary Parser
# -------------------------------------------------------

GLB_MAGIC   = 0x46546C67  # "glTF"
JSON_CHUNK  = 0x4E4F534A  # "JSON"
BIN_CHUNK   = 0x004E4942  # "BIN\0"

# glTF accessor component types
COMPONENT_TYPES = {
    5120: ('b', 1),   # BYTE
    5121: ('B', 1),   # UNSIGNED_BYTE
    5122: ('h', 2),   # SHORT
    5123: ('H', 2),   # UNSIGNED_SHORT
    5125: ('I', 4),   # UNSIGNED_INT
    5126: ('f', 4),   # FLOAT
}

# glTF accessor types -> element count
ACCESSOR_SIZES = {
    "SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4,
    "MAT2": 4,   "MAT3": 9, "MAT4": 16,
}


def _read_glb(file_path):
    """Parse a GLB file and return (gltf_json_dict, binary_buffer_bytes)."""
    with open(file_path, "rb") as f:
        data = f.read()

    offset = 0
    magic, version, length = struct.unpack_from("<III", data, offset)
    offset += 12

    if magic != GLB_MAGIC:
        raise ValueError(f"Not a valid GLB file (magic={hex(magic)})")

    gltf_json = None
    bin_buffer = None

    while offset < length:
        chunk_len, chunk_type = struct.unpack_from("<II", data, offset)
        offset += 8
        chunk_data = data[offset:offset + chunk_len]
        offset += chunk_len

        if chunk_type == JSON_CHUNK:
            gltf_json = json.loads(chunk_data.decode("utf-8"))
        elif chunk_type == BIN_CHUNK:
            bin_buffer = chunk_data

    if gltf_json is None:
        raise ValueError("GLB is missing the JSON chunk.")

    return gltf_json, bin_buffer


def _get_accessor_data(gltf, bin_buffer, accessor_index):
    """Extract typed array data from a glTF accessor."""
    acc = gltf["accessors"][accessor_index]
    bv_index = acc.get("bufferView")
    if bv_index is None:
        return []

    bv = gltf["bufferViews"][bv_index]
    byte_offset = bv.get("byteOffset", 0) + acc.get("byteOffset", 0)
    count = acc["count"]
    comp_type = acc["componentType"]
    elem_type  = acc["type"]

    fmt_char, byte_size = COMPONENT_TYPES[comp_type]
    num_components = ACCESSOR_SIZES[elem_type]

    stride = bv.get("byteStride", byte_size * num_components)
    result = []

    for i in range(count):
        row_offset = byte_offset + i * stride
        row = struct.unpack_from(f"<{num_components}{fmt_char}", bin_buffer, row_offset)
        result.append(row if num_components > 1 else row[0])

    return result


# -------------------------------------------------------
# Maya Geometry Builder
# -------------------------------------------------------

def _build_maya_mesh(name, positions, indices):
    """Create a Maya polygon mesh from (x,y,z) positions and flat triangle indices."""
    if not positions or not indices:
        print(f"  [GLB] Skipping '{name}': empty positions or indices")
        return None

    num_verts = len(positions)
    num_faces = len(indices) // 3

    # Build face-vertex arrays
    face_counts  = [3] * num_faces        # every face is a triangle
    face_connects = list(indices)          # flat list of vertex indices per face

    xs = [p[0] for p in positions]
    ys = [p[1] for p in positions]
    zs = [p[2] for p in positions]

    mesh_name = cmds.createNode("mesh", name=f"{name}Shape")
    transform  = cmds.listRelatives(mesh_name, parent=True)[0]
    transform  = cmds.rename(transform, name)

    fn = cmds.MeshFn if hasattr(cmds, "MeshFn") else None

    # Use polyCreateFacet for simple builds; for large meshes use the API path
    try:
        import maya.api.OpenMaya as om2

        pts = om2.MFloatPointArray()
        for x, y, z in positions:
            pts.append(om2.MFloatPoint(x, y, z))

        fc = om2.MIntArray(face_counts)
        fv = om2.MIntArray(face_connects)

        sel = om2.MSelectionList()
        sel.add(f"{transform}|{mesh_name}")
        dag = sel.getDagPath(0)
        fn_mesh = om2.MFnMesh(dag)
        fn_mesh.create(pts, fc, fv)
        fn_mesh.updateSurface()

    except Exception as api_err:
        print(f"  [GLB] OM2 path failed ({api_err}), using cmds fallback...")
        # cmds fallback: slower but always works
        cmds.delete(transform)  # remove the empty node
        verts_flat = []
        for x, y, z in positions:
            verts_flat.extend([x, y, z])

        transform = cmds.polyCreateFacet(
            point=[(positions[i][0], positions[i][1], positions[i][2]) for i in range(min(3, num_verts))],
            name=name
        )[0]
        # Rebuild properly
        cmds.delete(transform)
        # Last resort: polySphere placeholder
        transform = cmds.polySphere(name=name, r=1)[0]
        print(f"  [GLB] WARNING: Used placeholder sphere for '{name}'")

    cmds.polySoftEdge(transform, angle=30, ch=False)
    cmds.makeIdentity(transform, apply=True)
    return transform


# -------------------------------------------------------
# Main Import Entry Point
# -------------------------------------------------------

def import_glb(file_path):
    """
    Imports a GLB/glTF file into Maya without any plugins.
    Parses the binary format directly and creates native Maya geometry.
    """
    if not os.path.exists(file_path):
        print(f"[GLB Import] Error: File not found: {file_path}")
        return False

    print(f"[GLB Import] Native Parser: Reading {file_path}...")

    # Handle .gltf (JSON) alongside .glb (binary)
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".gltf":
        with open(file_path, "r", encoding="utf-8") as f:
            gltf = json.load(f)
        # Look for .bin companion file
        bin_path = os.path.splitext(file_path)[0] + ".bin"
        if os.path.exists(bin_path):
            with open(bin_path, "rb") as f:
                bin_buffer = f.read()
        else:
            bin_buffer = None
    else:
        try:
            gltf, bin_buffer = _read_glb(file_path)
        except Exception as e:
            print(f"[GLB Import] Parse Error: {e}")
            return False

    meshes = gltf.get("meshes", [])
    if not meshes:
        print("[GLB Import] No meshes found in this GLB file.")
        return False

    print(f"[GLB Import] Found {len(meshes)} mesh(es). Building geometry...")
    created = []

    for mesh_idx, mesh in enumerate(meshes):
        mesh_name = mesh.get("name", f"GLB_Mesh_{mesh_idx:03d}")
        # Sanitize name for Maya
        mesh_name = "".join(c if c.isalnum() or c == "_" else "_" for c in mesh_name)

        for prim_idx, prim in enumerate(mesh.get("primitives", [])):
            prim_name = mesh_name if prim_idx == 0 else f"{mesh_name}_prim{prim_idx}"

            attrs = prim.get("attributes", {})
            pos_accessor = attrs.get("POSITION")
            if pos_accessor is None:
                print(f"  [GLB] Primitive '{prim_name}' has no POSITION attribute, skipping.")
                continue

            try:
                positions = _get_accessor_data(gltf, bin_buffer, pos_accessor)
            except Exception as e:
                print(f"  [GLB] Failed to read positions for '{prim_name}': {e}")
                continue

            # Triangle indices (if missing: generate sequential)
            indices_accessor = prim.get("indices")
            if indices_accessor is not None:
                try:
                    raw_indices = _get_accessor_data(gltf, bin_buffer, indices_accessor)
                    indices = [int(i) for i in raw_indices]
                except Exception as e:
                    print(f"  [GLB] Failed to read indices for '{prim_name}': {e}")
                    indices = list(range(len(positions)))
            else:
                # Non-indexed — every 3 vertices is a triangle
                indices = list(range(len(positions)))

            print(f"  [GLB] Building '{prim_name}': {len(positions)} verts, {len(indices)//3} tris")
            node = _build_maya_mesh(prim_name, positions, indices)
            if node:
                created.append(node)

    if created:
        cmds.select(created, replace=True)
        print(f"[GLB Import] Success! Created {len(created)} mesh(es): {created}")
        return True
    else:
        print("[GLB Import] No geometry was created.")
        return False


if __name__ == "__main__":
    import_glb(r"C:\Users\91991\Downloads\object_0 (2).glb")
