"""Render missing gallery images from unchanged V13 and V08 STL geometry.

Run with Blender background Python; -- --draft renders a quick review image.
"""

import hashlib
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".gallery-cache"
CACHE.mkdir(exist_ok=True)
DRAFT = "--draft" in sys.argv


def setup(width, height):
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 24 if DRAFT else 96
    scene.cycles.use_denoising = True
    scene.cycles.use_adaptive_sampling = True
    scene.cycles.adaptive_threshold = 0.025
    scene.cycles.max_bounces = 8
    scene.render.resolution_x, scene.render.resolution_y = width, height
    scene.render.resolution_percentage = 50 if DRAFT else 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.exposure = -0.5
    scene.world.use_nodes = True
    scene.world.node_tree.nodes.get("Background").inputs[
        "Strength"
    ].default_value = 0.35
    return scene


def mat(name, color, roughness=0.5, metallic=0):
    result = bpy.data.materials.new(name)
    result.use_nodes = True
    bsdf = result.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    return result


def mesh(path, material):
    bpy.ops.wm.stl_import(filepath=str(path))
    obj = bpy.context.object
    for v in obj.data.vertices:
        v.co *= 0.001
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    obj.data.materials.clear()
    obj.data.materials.append(material)
    obj.data.update()
    return obj


def light(name, location, target, power, size):
    bpy.ops.object.light_add(type="AREA", location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.energy, obj.data.size = power, size
    obj.rotation_euler = (
        (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()
    )


def camera(location, target, *, ortho=None, lens=65):
    bpy.ops.object.camera_add(location=location)
    cam = bpy.context.object
    cam.name = "CAM-gallery"
    cam.rotation_euler = (
        (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
    )
    cam.data.clip_start = 0.001
    cam.data.lens = lens
    if ortho:
        cam.data.type = "ORTHO"
        cam.data.ortho_scale = ortho
    bpy.context.scene.camera = cam
    return cam


def render(path):
    scene = bpy.context.scene
    assert scene.camera is not None
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


scene = setup(840, 720)
scene.render.film_transparent = True
comb_source = ROOT / "scalp-massage-comb/v13/massage-comb-v13.stl"
comb = mesh(comb_source, mat("MAT-sage_design", (0.12, 0.17, 0.135)))
target = (0, 0.031, 0.006)
light("LGT-key", (-0.10, -0.12, 0.21), target, 1.8, 0.14)
light("LGT-fill", (0.15, -0.02, 0.14), target, 0.7, 0.16)
light("LGT-rim", (0, 0.14, 0.16), target, 1.4, 0.13)
cam = camera((0, 0.031, 0.26), target, ortho=0.115)
render(CACHE / "comb-front.png")
cam.location = (0.075, -0.10, 0.18)
cam.rotation_euler = (Vector(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
render(CACHE / "comb-iso.png")

scene = setup(1600, 1100)
scene.render.film_transparent = False
scene.render.image_settings.color_mode = "RGB"
white = mat("MAT-white_PLA", (0.82, 0.80, 0.74), 0.53)
black = mat("MAT-black_PLA", (0.012, 0.014, 0.015), 0.5)
sources = []
for color, material in (("white", white), ("black", black)):
    source = ROOT / f"shuttlecock-pen-holder/v08/shuttlecock-v08-{color}.stl"
    obj = mesh(source, material)
    obj.name = f"GEO-V08_{color}_unchanged"
    sources.append(
        {
            "path": str(source.relative_to(ROOT)),
            "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "modifiers": [m.type for m in obj.modifiers],
        }
    )

wood = mat("MAT-oak_desktop", (0.53, 0.38, 0.22), 0.58)
nodes, links = wood.node_tree.nodes, wood.node_tree.links
coord = nodes.new("ShaderNodeTexCoord")
scale = nodes.new("ShaderNodeVectorMath")
scale.operation = "MULTIPLY"
scale.inputs[1].default_value = (8, 550, 30)
noise = nodes.new("ShaderNodeTexNoise")
noise.inputs["Scale"].default_value = 1
ramp = nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].color = (0.38, 0.25, 0.14, 1)
ramp.color_ramp.elements[1].color = (0.66, 0.50, 0.32, 1)
links.new(coord.outputs["Object"], scale.inputs[0])
links.new(scale.outputs[0], noise.inputs["Vector"])
links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
links.new(ramp.outputs["Color"], nodes.get("Principled BSDF").inputs["Base Color"])
bpy.ops.mesh.primitive_plane_add(size=3, location=(0, 0, -0.00005))
bpy.context.object.name = "GEO-desktop_context"
bpy.context.object.data.materials.append(wood)

# Pens are illustrative props, sized in metres and contained within the opening.
pen_colors = [(0.56, 0.59, 0.57), (0.85, 0.80, 0.69), (0.09, 0.11, 0.12)]
for i, ((x, y), length, color) in enumerate(
    zip(
        [(-0.011, 0.005), (0, 0.008), (0.011, -0.002)], [0.145, 0.133, 0.15], pen_colors
    )
):
    parent = bpy.data.objects.new(f"PROP-pen_{i}", None)
    bpy.context.collection.objects.link(parent)
    parent.location = (x, y, 0.008)
    parent.rotation_euler = (math.radians(2 - i), math.radians((i - 1) * 4), 0)
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=0.0035, depth=length)
    shaft = bpy.context.object
    shaft.name = f"PROP-pen_{i}_shaft"
    shaft.parent = parent
    shaft.location = (0, 0, length / 2)
    shaft.data.materials.append(mat(f"MAT-pen_{i}", color, 0.38))
    for poly in shaft.data.polygons:
        poly.use_smooth = True
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=0.0035)
    cap = bpy.context.object
    cap.name = f"PROP-pen_{i}_cap"
    cap.parent = parent
    cap.location = (0, 0, length)
    cap.scale.z = 0.4
    cap.data.materials.append(shaft.data.materials[0])
    trim = mat(f"MAT-pen_{i}_metal", (0.55, 0.57, 0.58), 0.3, metallic=1)
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.0034,
        minor_radius=0.00035,
        major_segments=48,
        minor_segments=12,
    )
    ring = bpy.context.object
    ring.name = f"PROP-pen_{i}_cap_ring"
    ring.parent = parent
    ring.location = (0, 0, length - 0.015)
    ring.data.materials.append(trim)
    bpy.ops.mesh.primitive_cube_add(size=1)
    clip = bpy.context.object
    clip.name = f"PROP-pen_{i}_clip"
    clip.dimensions = (0.0015, 0.0012, 0.018)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    clip.parent = parent
    clip.location = (0, -0.004, length - 0.010)
    clip.data.materials.append(trim)
    bevel = clip.modifiers.new("Rounded prop clip", "BEVEL")
    bevel.width = 0.0005
    bevel.segments = 3

target = (0, 0, 0.073)
light("LGT-window", (-0.2, -0.16, 0.33), target, 6, 0.25)
light("LGT-fill", (0.25, -0.10, 0.23), target, 2.5, 0.25)
light("LGT-rim", (0.05, 0.25, 0.30), target, 4.5, 0.20)
camera((0.25, -0.39, 0.27), target, lens=65)
out = ROOT / "shuttlecock-pen-holder/assets/simulated-use-v08.png"
render(CACHE / "pen-use-draft.png" if DRAFT else out)
if not DRAFT:
    report = {
        "classification": "CAD-rendered desktop use illustration; not a photograph",
        "version": "V08",
        "source_meshes": sources,
        "geometry_changes": "none; shared coordinates preserved, millimetres converted to metres",
        "props": "three illustrative pens; no capacity or fit validation implied",
        "renderer": f"local Blender {bpy.app.version_string}, Cycles, 96 samples",
        "mcp_backend": "unavailable; local background execution used",
        "image": out.name,
        "comb_design_source_sha256": hashlib.sha256(
            comb_source.read_bytes()
        ).hexdigest(),
    }
    out.with_suffix(".json").write_text(json.dumps(report, indent=2) + "\n")
