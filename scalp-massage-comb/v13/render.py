"""Render the two actual meshes with locked cameras, lights and scale."""

import json
import math
from pathlib import Path

import bpy
from mathutils import Vector

P = Path(__file__).parent
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
s = bpy.context.scene
s.render.engine = "CYCLES"
s.cycles.samples = 32
s.cycles.use_denoising = True
s.cycles.use_adaptive_sampling = True
s.cycles.adaptive_threshold = 0.04
s.render.resolution_x = 1200
s.render.resolution_y = 900
s.render.resolution_percentage = 100
s.render.image_settings.file_format = "PNG"
s.render.image_settings.color_mode = "RGBA"
s.view_settings.view_transform = "AgX"
s.view_settings.exposure = -1.0
s.world.use_nodes = True
nodes = s.world.node_tree.nodes
nodes.clear()
bg = nodes.new("ShaderNodeBackground")
bg.inputs["Color"].default_value = (0.75, 0.75, 0.75, 1)
bg.inputs["Strength"].default_value = 0.5
out = nodes.new("ShaderNodeOutputWorld")
s.world.node_tree.links.new(bg.outputs["Background"], out.inputs["Surface"])


def material(name, color, roughness):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = roughness
    return m


body = material("MAT-neutral_graphite", (0.24, 0.27, 0.26), 0.48)
floor = material("MAT-neutral_floor", (0.82, 0.82, 0.80), 0.8)
objects = {}
for version in ("v12", "v13"):
    source = P.parent / version / f"massage-comb-{version}.stl"
    bpy.ops.wm.stl_import(filepath=str(source))
    obj = bpy.context.object
    obj.name = f"GEO-massage_comb_{version}"
    obj.data.materials.clear()
    obj.data.materials.append(body)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))
    obj.hide_render = True
    objects[version] = obj
bpy.ops.mesh.primitive_plane_add(size=1800, location=(0, 0, -0.5))
plane = bpy.context.object
plane.name = "GEO-ground"
plane.data.materials.append(floor)
for name, location, energy, size in (
    ("key", (-100, -120, 210), 1400000, 140),
    ("fill", (150, -20, 140), 600000, 160),
    ("rim", (0, 140, 160), 900000, 130),
):
    bpy.ops.object.light_add(type="AREA", location=location)
    light = bpy.context.object
    light.name = f"LGT-{name}"
    light.data.energy = energy
    light.data.shape = "DISK"
    light.data.size = size
    light.rotation_euler = (
        (Vector((0, 30, 5)) - light.location).to_track_quat("-Z", "Y").to_euler()
    )
bpy.ops.object.camera_add()
cam = bpy.context.object
cam.name = "CAM-locked_comparison"
cam.data.type = "ORTHO"
cam.data.clip_end = 10000
cam.data.ortho_scale = 114
s.camera = cam
views = {
    "front": ((0, 30, 260), (0, 30, 0)),
    "iso": ((75, -100, 180), (0, 30, 5)),
    "side": ((250, 30, 8), (0, 30, 8)),
}
metadata = {"engine": "CYCLES", "samples": 32, "views": views, "meshes": {}}
for name, obj in objects.items():
    metadata["meshes"][name] = {
        "vertices": len(obj.data.vertices),
        "polygons": len(obj.data.polygons),
        "dimensions_mm": list(obj.dimensions),
        "modifiers": [m.type for m in obj.modifiers],
    }
    obj.hide_render = False
    for view in ("front", "iso"):
        loc, target = views[view]
        cam.location = loc
        cam.rotation_euler = (
            (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
        )
        s.render.filepath = str(P / f"{name}-{view}.png")
        assert s.camera is not None
        bpy.ops.render.render(write_still=True)
    obj.hide_render = True
# Unlit, material-independent masks: actual silhouettes, no shadows or framing tricks.
mask = bpy.data.materials.new("MAT-silhouette")
mask.use_nodes = True
n = mask.node_tree.nodes
n.clear()
emission = n.new("ShaderNodeEmission")
emission.inputs["Color"].default_value = (1, 1, 1, 1)
out = n.new("ShaderNodeOutputMaterial")
mask.node_tree.links.new(emission.outputs[0], out.inputs["Surface"])
s.view_layers[0].material_override = mask
s.render.film_transparent = True
plane.hide_render = True
s.cycles.samples = 4
s.cycles.use_denoising = False
for name, obj in objects.items():
    obj.hide_render = False
    for view in ("front", "side"):
        loc, target = views[view]
        cam.location = loc
        cam.rotation_euler = (
            (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
        )
        s.render.filepath = str(P / f"{name}-{view}-mask.png")
        bpy.ops.render.render(write_still=True)
    obj.hide_render = True
s.view_layers[0].material_override = None
s.render.film_transparent = False
plane.hide_render = False
objects["v13"].hide_render = False
cam.location = views["iso"][0]
cam.rotation_euler = (
    (Vector(views["iso"][1]) - cam.location).to_track_quat("-Z", "Y").to_euler()
)
s.cycles.samples = 32
s.cycles.use_denoising = True
bpy.ops.wm.save_as_mainfile(filepath=str(P / "massage-comb-v13.blend"))
(P / "render-settings.json").write_text(json.dumps(metadata, indent=2))
print("Rendered actual V12/V13 meshes; cameras, lighting, scale and material locked.")
