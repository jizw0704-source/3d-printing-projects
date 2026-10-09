import math
from pathlib import Path

import bpy
from mathutils import Vector

P = Path(__file__).parent
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
s = bpy.context.scene
s.render.engine = "CYCLES"
s.cycles.samples = 36
s.cycles.use_denoising = True
s.render.resolution_x = 1400
s.render.resolution_y = 1100
s.render.resolution_percentage = 100
s.world.use_nodes = True
s.world.node_tree.nodes["Background"].inputs["Color"].default_value = (
    0.75,
    0.75,
    0.75,
    1,
)
s.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.4
s.view_settings.view_transform = "AgX"


def material(name, c, rough=0.45):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    bs.inputs["Base Color"].default_value = (*c, 1)
    bs.inputs["Roughness"].default_value = rough
    return m


body = material("Forest green", (0.10, 0.19, 0.15))
floor = material("Warm pale countertop", (0.79, 0.77, 0.71))
bpy.ops.wm.stl_import(filepath=str(P / "shoehorn-v04.stl"))
o = bpy.context.object
o.rotation_euler.x = math.pi / 2
o.location = (0, 89, 7.5)
o.data.materials.clear()
o.data.materials.append(body)
for poly in o.data.polygons:
    poly.use_smooth = True
bpy.ops.object.shade_smooth_by_angle(angle=math.radians(35))
bpy.ops.mesh.primitive_plane_add(size=1800, location=(0, 0, -0.5))
bpy.context.object.data.materials.append(floor)


def light(loc, energy, size):
    bpy.ops.object.light_add(type="AREA", location=loc)
    a = bpy.context.object
    a.data.energy = energy
    a.data.shape = "DISK"
    a.data.size = size
    a.rotation_euler = (
        (Vector((0, 0, 12)) - a.location).to_track_quat("-Z", "Y").to_euler()
    )


light((100, -200, 500), 2400000, 400)
light((-300, 100, 300), 800000, 350)
light((300, 250, 400), 1500000, 350)
bpy.ops.object.camera_add(location=(240, -350, 450))
cam = bpy.context.object
cam.data.type = "ORTHO"
cam.data.clip_end = 10000
cam.data.ortho_scale = 250
cam.rotation_euler = (
    (Vector((0, 0, 12)) - cam.location).to_track_quat("-Z", "Y").to_euler()
)
s.camera = cam
s.render.image_settings.file_format = "PNG"
s.render.filepath = str(P / "shoehorn-render.png")
bpy.ops.wm.save_as_mainfile(filepath=str(P / "shoehorn-v04.blend"))
bpy.ops.render.render(write_still=True)
cam.location = (160, 180, 175)
cam.data.ortho_scale = 135
cam.rotation_euler = (
    (Vector((0, 54, 9)) - cam.location).to_track_quat("-Z", "Y").to_euler()
)
s.render.resolution_x = 900
s.render.resolution_y = 900
s.render.filepath = str(P / "blade-detail.png")
bpy.ops.render.render(write_still=True)
