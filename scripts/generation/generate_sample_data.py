import os
try:
    import trimesh
except ImportError:
    trimesh = None
def create_sample_cube():
    os.makedirs("backend/data", exist_ok=True)
    if not trimesh:
        with open("backend/data/sample_cube.obj", "w") as f:
            f.write("v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3")
        print("Created backend/data/sample_cube.obj (dummy)")
        return
    mesh = trimesh.creation.box(extents=[10, 10, 10])
    mesh.export("backend/data/sample_cube.obj")
    print("Created backend/data/sample_cube.obj")
if __name__ == "__main__":
    create_sample_cube()
