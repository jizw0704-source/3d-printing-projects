# /// script
# requires-python = ">=3.12,<3.13"
# dependencies = ["trimesh==4.12.2", "numpy", "rtree", "scipy", "networkx"]
# ///
"""Check the actual revised STL, protected geometry, gaps and preview data."""

import hashlib
import json
from pathlib import Path

import numpy as np
import trimesh

P = Path(__file__).parent
path = P / "massage-comb-v13.stl"
mesh = trimesh.load(path, force="mesh")
mesh.update_faces(mesh.area_faces > 1e-12)
mesh.merge_vertices(digits_vertex=5)
assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0
assert len(mesh.split()) == 1
mesh.export(path)
reference_path = P.parent / "v12/massage-comb-v12.stl"
reference = trimesh.load(reference_path, force="mesh")
assert np.all(np.abs(mesh.extents / reference.extents - 1) < 0.03)
section = mesh.section(plane_origin=(0, 18, 0), plane_normal=(0, 1, 0))
assert section is not None
teeth = sorted(section.discrete, key=lambda points: points[:, 0].mean())
assert len(teeth) == 5
x_ranges = [(float(t[:, 0].min()), float(t[:, 0].max())) for t in teeth]
gaps = [x_ranges[i + 1][0] - x_ranges[i][1] for i in range(4)]
assert min(gaps) > 4
# Deterministic distance samples are a bounded numerical check, not a proof of
# exact shape equality. Projection/re-tessellation are explicitly included here.
protected = mesh.vertices[(mesh.vertices[:, 1] <= 20.5) | (mesh.vertices[:, 1] >= 46.5)]
rng = np.random.default_rng(13)
points = protected[
    rng.choice(len(protected), size=min(4000, len(protected)), replace=False)
]
_, distance, _ = trimesh.proximity.closest_point(reference, points)
assert distance.max() < 0.15
assert np.percentile(distance, 95) < 0.06
baseline = reference.vertices[
    (reference.vertices[:, 1] <= 20.5) | (reference.vertices[:, 1] >= 46.5)
]
points_back = baseline[
    rng.choice(len(baseline), size=min(4000, len(baseline)), replace=False)
]
_, distance_back, _ = trimesh.proximity.closest_point(mesh, points_back)
assert distance_back.max() < 0.15
preview = trimesh.graph.smooth_shade(mesh, angle=np.deg2rad(35), facet_minarea=10)
vertices = preview.vertices[preview.faces].copy() - mesh.bounds.mean(axis=0)
normals = preview.vertex_normals[preview.faces]
np.concatenate((vertices, normals), axis=2).astype("<f4").tofile(P / "mesh.bin")
ref_report = json.loads((P.parent / "v12/validation.json").read_text())
fairing = json.loads((P / "surface-fairing.json").read_text())
report = {
    "status": "mesh_checked_awaiting_visual_feedback_not_printed",
    "source_sha256": hashlib.sha256(reference_path.read_bytes()).hexdigest(),
    "stl_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    "method": fairing["method"],
    "dimensions_mm": mesh.extents.tolist(),
    "previous_dimensions_mm": reference.extents.tolist(),
    "volume_mm3": float(mesh.volume),
    "volume_change_fraction_vs_v12": float(mesh.volume / reference.volume - 1),
    "teeth": 5,
    "nominal_tooth_pitch_mm": 18,
    "source_exposed_centerline_length_mm": ref_report["exposed_centerline_length_mm"],
    "length_note": "tooth centerlines/tips retained within sampled mesh approximation; original approximately 20 mm length remains nominal, root surface has changed",
    "separate_teeth_at_y18": len(teeth),
    "gaps_at_y18_mm": gaps,
    "watertight": bool(mesh.is_watertight),
    "winding_consistent": bool(mesh.is_winding_consistent),
    "mesh_components": len(mesh.split()),
    "triangles": len(mesh.faces),
    "protected_mesh_to_source_max_distance_mm": float(distance.max()),
    "protected_mesh_to_source_p95_distance_mm": float(np.percentile(distance, 95)),
    "protected_source_to_mesh_max_distance_mm": float(distance_back.max()),
    "distance_scope": "deterministic samples on tooth contact region Y<=20.5 and grip rear Y>=46.5; not an exhaustive Hausdorff bound",
    "max_root_surface_displacement_mm": fairing["max_fairing_displacement_mm"],
    "step_status": "none: V13 is a locally refined mesh; V12 STEP is not this shape",
    "unverified": [
        "visual acceptance",
        "global curvature continuity",
        "scalp comfort",
        "snagging",
        "durability",
        "slicing and print finish",
    ],
}
(P / "validation.json").write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
