import json
from pathlib import Path

import trimesh

p = Path(__file__).parent
r = {}
for f in p.glob("*.stl"):
    m = trimesh.load(f)
    # OCC sphere tessellation may emit isolated zero-area triangles at poles.
    # Remove only faces with exactly zero area before testing the closed mesh.
    m.update_faces(m.area_faces > 0.0)
    m.merge_vertices(digits_vertex=5)
    r[f.stem] = {
        "watertight": bool(m.is_watertight),
        "positive_volume": bool(m.volume > 0),
        "components": len(m.split()),
    }
    assert m.is_watertight and m.volume > 0, f
    m.export(f)
    reloaded = trimesh.load(f)
    assert reloaded.is_watertight and reloaded.volume > 0, f
(p / "mesh-checks.json").write_text(json.dumps(r, indent=2))
print("All meshes passed watertight and positive-volume checks.")
