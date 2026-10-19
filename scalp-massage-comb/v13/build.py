"""Locally fair the palm/root band on the actual mesh, preserving the contact teeth.

Run with Blender background Python; STL millimetres stay as millimetres.
This is a mesh refinement, not a newly fitted analytical STEP solid.
"""

import hashlib
import json
from pathlib import Path

import bpy
import numpy as np

P = Path(__file__).parent
SOURCE = P.parent / "v12/massage-comb-v12.stl"
VOXEL_MM = 0.18
SMOOTH_ITERATIONS = 1200
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.ops.wm.stl_import(filepath=str(SOURCE))
source = bpy.context.object
source.name = "GEO-reference_v12"
source.hide_render = True
obj = source.copy()
obj.data = source.data.copy()
obj.name = "GEO-root_fairing_v13"
obj.hide_render = False
obj.hide_set(False)
bpy.context.collection.objects.link(obj)
bpy.ops.object.select_all(action="DESELECT")
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
obj.data.remesh_voxel_size = VOXEL_MM
obj.data.use_remesh_preserve_volume = True
bpy.ops.object.voxel_remesh()
# Preserve the original dimensions outside the surface-refinement band. Project
# the uniformly re-tessellated vertices back to the original triangles first.
projection = obj.modifiers.new("Project reference before local fairing", "SHRINKWRAP")
projection.target = source
projection.wrap_method = "NEAREST_SURFACEPOINT"
projection.wrap_mode = "ON_SURFACE"
bpy.ops.object.modifier_apply(modifier=projection.name)
coords = np.empty(len(obj.data.vertices) * 3, dtype=np.float64)
obj.data.vertices.foreach_get("co", coords)
coords = coords.reshape(-1, 3)


def smoothstep(value):
    u = np.clip(value, 0, 1)
    return u**3 * (10 - 15 * u + 6 * u**2)


# A wide, softly bounded patch: no sudden masking line, and no changes to tips
# Y<=21 mm, the palm rear Y>=46 mm, or the broad flat print-contact surface.
y = coords[:, 1]
z = coords[:, 2]
weight = (
    smoothstep((y - 21) / 5) * smoothstep((46 - y) / 7) * smoothstep((z - 0.8) / 2.5)
)
group = obj.vertex_groups.new(name="Continuous root blend")
for i in np.flatnonzero(weight > 0):
    group.add([int(i)], float(weight[i]), "REPLACE")
modifier = obj.modifiers.new("Fair grip into five roots", "SMOOTH")
modifier.factor = 0.65
modifier.iterations = SMOOTH_ITERATIONS
modifier.vertex_group = group.name
bpy.ops.object.modifier_apply(modifier=modifier.name)
after = np.empty(len(obj.data.vertices) * 3, dtype=np.float64)
obj.data.vertices.foreach_get("co", after)
after = after.reshape(-1, 3)
delta = np.linalg.norm(after - coords, axis=1)
protected = (y <= 21) | (y >= 46) | (z <= 0.8)
assert delta[protected].max() < 1e-6
assert delta.max() > 0.5, "Expected a real surface repair, not display-only smoothing"
assert delta.max() < 4
obj.data.update()
for polygon in obj.data.polygons:
    polygon.use_smooth = True
bpy.ops.object.select_all(action="DESELECT")
obj.select_set(True)
bpy.ops.wm.stl_export(
    filepath=str(P / "massage-comb-v13.stl"), export_selected_objects=True
)
assert (P / "massage-comb-v13.stl").stat().st_size > 10000
source.hide_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(P / "surface-edit.blend"))
report = {
    "source": "V12 STL; source STEP remains in v12 as historical reference only",
    "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    "method": "uniform voxel re-tessellation, nearest-surface projection, weighted local surface fairing",
    "voxel_size_mm": VOXEL_MM,
    "smooth_iterations": SMOOTH_ITERATIONS,
    "working_vertices": len(coords),
    "vertices_in_fairing_band": int((weight > 0).sum()),
    "max_fairing_displacement_mm": float(delta.max()),
    "mean_band_fairing_displacement_mm": float(delta[weight > 0].mean()),
    "max_fairing_displacement_in_protected_region_mm": float(delta[protected].max()),
    "protected_region_definition": "pre-fairing mesh vertices Y<=21 or Y>=46 or Z<=0.8; remeshing tolerance must be checked separately against V12",
    "step_status": "not generated; do not label the older STEP as this revised geometry",
    "status": "candidate_mesh_refinement_requires_validation_and_visual_review",
}
(P / "surface-fairing.json").write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
