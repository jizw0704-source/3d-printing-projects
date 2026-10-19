"""Render the unchanged V13 STL as a black PLA desktop product illustration.

Run with local Blender background Python. No external assets or device access.
"""

import hashlib
import json
import math
import os
from pathlib import Path

import bpy
from mathutils import Vector

P = Path(__file__).parent
SOURCE = P.parent / "v13/massage-comb-v13.stl"
DRAFT = os.environ.get("COMB_RENDER_DRAFT") == "1"
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.render.engine = "CYCLES"
scene.cycles.samples = 24 if DRAFT else 128
scene.cycles.use_denoising = True
scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = 0.025
scene.cycles.max_bounces = 8
scene.render.resolution_x = 1600
scene.render.resolution_y = 1100
scene.render.resolution_percentage = 50 if DRAFT else 100
scene.render.image_settings.file_format = "PNG"
scene.render.image_settings.color_mode = "RGB"
scene.view_settings.view_transform = "AgX"
scene.view_settings.exposure = -0.6
scene.world.use_nodes = True
background = scene.world.node_tree.nodes.get("Background")
background.inputs["Color"].default_value = (0.72, 0.76, 0.83, 1)
background.inputs["Strength"].default_value = 0.25


def material(name, color, roughness):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Metallic"].default_value = 0
    bsdf.inputs["Roughness"].default_value = roughness
    return mat, bsdf


body, bsdf = material("MAT-black_PLA", (0.012, 0.014, 0.015), 0.55)
bsdf.inputs["IOR"].default_value = 1.46
# Shading-only 0.12 mm bands illustrate layer texture, not measured print quality.
nodes, links = body.node_tree.nodes, body.node_tree.links
coord = nodes.new("ShaderNodeTexCoord")
wave = nodes.new("ShaderNodeTexWave")
wave.wave_type = "BANDS"
wave.bands_direction = "Z"
wave.inputs["Scale"].default_value = 1 / (0.00012 * 20)
links.new(coord.outputs["Object"], wave.inputs["Vector"])
bump = nodes.new("ShaderNodeBump")
bump.inputs["Strength"].default_value = 0.16
bump.inputs["Distance"].default_value = 0.000008
links.new(wave.outputs["Fac"], bump.inputs["Height"])
links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
bpy.ops.wm.stl_import(filepath=str(SOURCE))
comb = bpy.context.object
comb.name = "GEO-unchanged_V13_comb"
comb.data.materials.clear()
comb.data.materials.append(body)
# Convert millimetres to metres in vertex coordinates; retain the original mesh.
points = [v.co.copy() for v in comb.data.vertices]
center = Vector(
    tuple((min(p[i] for p in points) + max(p[i] for p in points)) / 2 for i in (0, 1))
    + (min(p.z for p in points),)
)
for v in comb.data.vertices:
    v.co = (v.co - center) * 0.001
for polygon in comb.data.polygons:
    polygon.use_smooth = True
comb.data.update()

wood, wood_bsdf = material("MAT-light_oak", (0.48, 0.32, 0.17), 0.55)
n, l = wood.node_tree.nodes, wood.node_tree.links
tex = n.new("ShaderNodeTexCoord")
mapping = n.new("ShaderNodeVectorMath")
mapping.operation = "MULTIPLY"
mapping.inputs[1].default_value = (8, 750, 30)
noise = n.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value = 1
noise.inputs["Detail"].default_value = 2
ramp = n.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].color = (0.36, 0.23, 0.12, 1)
ramp.color_ramp.elements[1].color = (0.66, 0.48, 0.29, 1)
l.new(tex.outputs["Object"], mapping.inputs[0])
l.new(mapping.outputs[0], noise.inputs["Vector"])
l.new(noise.outputs["Fac"], ramp.inputs["Fac"])
l.new(ramp.outputs["Color"], wood_bsdf.inputs["Base Color"])
bpy.ops.mesh.primitive_plane_add(size=2, location=(0, 0, -0.00005))
bpy.context.object.name = "GEO-oak_surface"
bpy.context.object.data.materials.append(wood)

# A folded neutral cloth behind the subject establishes context without hiding it.
cloth, _ = material("MAT-linen", (0.70, 0.68, 0.62), 0.95)
bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.065, 0.12, 0.006))
towel = bpy.context.object
towel.name = "GEO-folded_linen_context"
towel.dimensions = (0.17, 0.07, 0.012)
towel.rotation_euler.z = math.radians(-9)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bevel = towel.modifiers.new("Soft textile edges", "BEVEL")
bevel.width = 0.005
bevel.segments = 6
towel.data.materials.append(cloth)

target = Vector((0, 0.005, 0.004))
for name, location, energy, size, color in (
    ("window_key", (-0.15, -0.10, 0.25), 2.8, 0.22, (1, 0.93, 0.83)),
    ("soft_fill", (0.18, -0.01, 0.20), 1.2, 0.18, (0.86, 0.92, 1)),
    ("rim", (0.01, 0.20, 0.22), 2.4, 0.15, (1, 0.98, 0.92)),
):
    bpy.ops.object.light_add(type="AREA", location=location)
    light = bpy.context.object
    light.name = f"LGT-{name}"
    light.data.energy, light.data.size, light.data.color = energy, size, color
    light.rotation_euler = (target - light.location).to_track_quat("-Z", "Y").to_euler()

bpy.ops.object.camera_add(location=(0.080, -0.165, 0.205))
cam = bpy.context.object
cam.name = "CAM-desktop_product"
cam.data.lens = 70
cam.data.clip_start = 0.001
cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
cam.data.dof.use_dof = False
cam.data.dof.focus_object = comb
cam.data.dof.aperture_fstop = 11
scene.camera = cam
assert scene.camera is not None
scene.render.filepath = str(P / ("showcase-draft.png" if DRAFT else "showcase-v13.png"))
bpy.ops.render.render(write_still=True)
if not DRAFT:
    report = {
        "image": "showcase-v13.png",
        "classification": "photorealistic CAD render; not a photograph or a print result",
        "source": "../v13/massage-comb-v13.stl",
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "mesh_geometry_changes": "none; millimetres converted to metres and recentered",
        "geometry_modifiers": [m.type for m in comb.modifiers],
        "material": "black PLA appearance; illustrative shading-only layer texture",
        "execution": "local Blender background Python; no MCP backend available",
        "blender_version": bpy.app.version_string,
        "renderer": "Cycles",
        "samples": scene.cycles.samples,
        "dimensions_mm": [float(x * 1000) for x in comb.dimensions],
        "physical_validation": "not performed; printing paused by user",
    }
    (P / "showcase-v13.json").write_text(json.dumps(report, indent=2) + "\n")
