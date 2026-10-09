"""Export the actual STL mesh for the dependency-free local WebGL preview."""

from pathlib import Path

import numpy as np
import trimesh

p = Path(__file__).parent
m = trimesh.load(p / "shoehorn-v04.stl")
v = m.vertices[:, [0, 2, 1]].copy()
v[:, 1] -= (m.bounds[0, 2] + m.bounds[1, 2]) / 2
v[:, 2] -= (m.bounds[0, 1] + m.bounds[1, 1]) / 2
n = m.vertex_normals[:, [0, 2, 1]]
data = np.concatenate([v[m.faces], n[m.faces]], axis=2).astype("<f4")
assert np.isfinite(data).all() and len(data) > 0
data.tofile(p / "mesh.bin")
print("Preview exported from the verified STL:", len(m.faces), "triangles")
