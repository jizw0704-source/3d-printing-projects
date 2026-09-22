"""Hello / 14: refined contours and mesh. Prototype only."""

from pathlib import Path
import math
import json
import re
import numpy as np
import cadquery as cq
import trimesh
from shapely.geometry import LineString
import vtk
from vtk.util.numpy_support import vtk_to_numpy
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent


def rounded_box(x, y, z, r):
    return (
        cq.Workplane("XY")
        .box(x, y, z, centered=(True, True, False))
        .edges("|Z")
        .fillet(r)
    )


base = rounded_box(150, 45, 6, 17).edges(">Z").fillet(1.8)
# One continuous hand-drawn cubic path, NOT an Apple font or traced logo.
start = (-58, 9)
segments = [
    ((-54, 11), (-49, 15), (-47, 19)),
    ((-43, 24), (-42, 38), (-47, 37)),
    ((-53, 36), (-53, 18), (-52, 8)),
    ((-50, 16), (-43, 24), (-39, 21)),
    ((-34, 18), (-43, 7), (-34, 8)),
    ((-26, 7), (-17, 16), (-23, 21)),
    ((-28, 26), (-33, 16), (-28, 11)),
    ((-22, 2), (-12, 11), (-7, 19)),
    ((-1, 27), (0, 39), (-5, 37)),
    ((-12, 34), (-15, 15), (-9, 9)),
    ((-4, 3), (5, 12), (11, 22)),
    ((17, 33), (15, 40), (11, 37)),
    ((5, 34), (0, 15), (6, 9)),
    ((11, 3), (21, 10), (26, 18)),
    ((31, 25), (40, 21), (37, 13)),
    ((34, 5), (23, 5), (24, 14)),
    ((24, 21), (32, 25), (38, 22)),
    ((43, 19), (48, 19), (52, 23)),
]
points = [start]
p0 = np.array(start, dtype=float)
for a, b, c in segments:
    p1, p2, p3 = map(lambda p: np.array(p, dtype=float), (a, b, c))
    for t in np.linspace(0, 1, 72)[1:]:
        points.append(
            tuple(
                (1 - t) ** 3 * p0
                + 3 * (1 - t) ** 2 * t * p1
                + 3 * (1 - t) * t * t * p2
                + t**3 * p3
            )
        )
    p0 = p3
outline = (
    LineString(points).buffer(1.85, quad_segs=24).simplify(0.01, preserve_topology=True)
)
assert outline.geom_type == "Polygon" and outline.is_valid


wp = cq.Workplane("XZ").polyline(list(outline.exterior.coords)[:-1]).close()
for ring in outline.interiors:
    wp = wp.polyline(list(ring.coords)[:-1]).close()
hello = wp.extrude(5).translate((0, -11.25, 0))
# Low hidden toe ties the baseline to the base without a full front plate.
toe = (
    cq.Workplane("XY")
    .box(116, 5, 4, centered=(True, True, False))
    .edges("|Z")
    .fillet(0.8)
    .edges(">Z")
    .fillet(0.6)
    .translate((-3, -13.75, 5))
)
hello = hello.union(toe)
# Rounded rear frame; constant 5 mm thickness rather than thick perforated wedge.
rear = (
    cq.Workplane("XZ")
    .center(0, 22)
    .rect(150, 34)
    .extrude(5)
    .edges("|Y")
    .fillet(9)
    .faces("<Y")
    .edges()
    .fillet(0.4)
    .translate((0, 16.25, 0))
)
# Extend the lower frame corners down into the base; keep upper radii.
rear = rear.union(
    cq.Workplane("XY")
    .box(150, 5, 10, centered=(True, True, False))
    .translate((0, 13.75, 4))
)
# True shared-edge honeycomb lattice clipped against an inset rounded frame.
# Cell pitch is derived from a regular hexagon, not a rectangular hole array.
inner = (
    cq.Workplane("XZ")
    .center(0, 22)
    .rect(145.6, 29.6)
    .extrude(8)
    .edges("|Y")
    .fillet(6.8)
    .translate((0, 18, 0))
)
# Keep a continuous side frame after the rear is trimmed to the base footprint.
inner = inner.intersect(rounded_box(142, 37, 60, 13))
cell_radius = 4.25
web = 1.2
hole_radius = cell_radius - web / math.sqrt(3)
holes = []
centres = []
for col in range(-13, 14):
    x = col * 1.5 * cell_radius
    for row in range(-3, 4):
        z = 22 + (row + 0.5 * (col % 2)) * math.sqrt(3) * cell_radius
        if abs(x) > 80 or z < 2 or z > 42:
            continue
        pts = [
            (
                x + hole_radius * math.cos(k * math.pi / 3),
                z + hole_radius * math.sin(k * math.pi / 3),
            )
            for k in range(6)
        ]
        tool = cq.Workplane("XZ").polyline(pts).close().extrude(8).translate((0, 18, 0))
        clipped = tool.intersect(inner)
        if clipped.val().Volume() > 0.01:
            holes.extend(clipped.val().Solids())
            centres.append((x, z))
rear = rear.cut(cq.Compound.makeCompound(holes))
rear_lattice_volume = rear.val().Volume()
# Three short rear braces: hidden on the back, not a solid sloping wall.
for x in (-48, 0, 48):
    brace = (
        cq.Workplane("YZ")
        .polyline([(16, 5), (20, 5), (16, 26)])
        .close()
        .extrude(2, both=True)
        .translate((x, 0, 0))
    )
    rear = rear.union(brace)
# The top fillet insets the base top outline by 1.8 mm on each side.
# Trim the entire rear to that footprint so no lower corners overhang.
support_envelope = rounded_box(146.4, 41.4, 60, 15.2)
rear = rear.intersect(support_envelope)
assert rear.cut(support_envelope).val().Volume() < 1e-6
# Low external front gussets reinforce the toe without narrowing the slot.
for x in (-48, -8, 28):
    gusset = (
        cq.Workplane("YZ")
        .polyline([(-16, 5), (-19.5, 5), (-16, 8.5)])
        .close()
        .extrude(2, both=True)
        .translate((x, 0, 0))
    )
    hello = hello.union(gusset)
body = base.union(hello).union(rear)
slot_probe = (
    cq.Workplane("XY")
    .box(110, 22.498, 40, centered=(True, True, False))
    .translate((0, 0, 6.01))
)
assert body.intersect(slot_probe).val().Volume() < 1e-6
for x in (-56, 56):
    for y in (-15, 15):
        body = body.cut(cq.Workplane("XY").center(x, y).circle(5).extrude(0.8))
assert body.val().isValid() and len(body.val().Solids()) == 1
report = {
    "status": "visual/geometry prototype; no physical fit, strength, thermal or slicing validation",
    "nominal_base_mm": [150, 45, 6],
    "bare_slot_mm": 22.5,
    "pad_each_side_mm": 3,
    "padded_clearance_mm": 16.5,
    "hello_contact_fillet_mm": 0,
    "hello_contact_protection": "3 mm separate soft pad; full perimeter fillet rejected by validation",
    "rear_top_contact_fillet_mm": 0.4,
    "rear_holes_including_boundary_cells": len(centres),
    "honeycomb_web_mm": web,
    "frame_width_mm": 2.2,
    "cell_radius_mm": cell_radius,
    "script_stroke_mm": 3.7,
    "rear_wall_mm": 5,
    "rear_width_mm": rear.val().BoundingBox().xlen,
    "models": {},
}
# Short gauge uses the same slot, wall thickness, base, and padded contact height.
gauge = rounded_box(30, 45, 6, 3).edges(">Z").fillet(1)
for side in (-1, 1):
    wall = (
        cq.Workplane("XY")
        .box(30, 5, 24, centered=(True, True, False))
        .edges("|Z")
        .fillet(0.35)
        .edges(">Z")
        .fillet(0.35)
        .translate((0, side * 13.75, 5))
    )
    gauge = gauge.union(wall)
assert gauge.val().isValid() and len(gauge.val().Solids()) == 1
# Perforations are cut before rear braces; braces can intentionally cross a few apertures.
for name, obj in [("stand-v14", body), ("fit-gauge-v14", gauge)]:
    shape = obj.val()
    cq.exporters.export(obj, str(OUT / f"{name}.step"))
    cq.exporters.export(
        obj, str(OUT / f"{name}.stl"), tolerance=0.01, angularTolerance=0.025
    )
    other = cq.importers.importStep(str(OUT / f"{name}.step")).val()
    volume = shape.Volume()
    err = abs(other.Volume() - volume) / volume
    assert other.isValid() and len(other.Solids()) == 1 and err < 1e-4
    mesh = trimesh.load_mesh(OUT / f"{name}.stl")
    mesh.update_faces(mesh.nondegenerate_faces())
    mesh.merge_vertices(digits_vertex=5)
    mesh.update_faces(mesh.nondegenerate_faces())
    assert mesh.is_watertight and mesh.is_volume
    mesh.export(OUT / f"{name}.stl")
    check = trimesh.load_mesh(OUT / f"{name}.stl")
    assert check.is_watertight and check.is_volume
    bb = shape.BoundingBox()
    report["models"][name] = {
        "valid": True,
        "single_solid": True,
        "watertight": True,
        "step_volume_error": err,
        "volume_cm3": volume / 1000,
        "size_mm": [bb.xlen, bb.ylen, bb.zlen],
    }


def render_view(camera_position):
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(245 / 255, 245 / 255, 247 / 255)
    # Neutral single-material preview: no unsupported multi-material promise.
    objects = [
        (base, (0.26, 0.27, 0.29)),
        (hello, (0.26, 0.27, 0.29)),
        (rear, (0.26, 0.27, 0.29)),
    ]
    for obj, color in objects:
        if not obj.vals() or not isinstance(obj.val(), cq.Shape):
            continue
        vertices, faces = obj.val().tessellate(0.01, 0.025)
        points = vtk.vtkPoints()
        for vertex in vertices:
            points.InsertNextPoint(*vertex.toTuple())
        cells = vtk.vtkCellArray()
        for face in faces:
            cells.InsertNextCell(3, face)
        poly = vtk.vtkPolyData()
        poly.SetPoints(points)
        poly.SetPolys(cells)
        clean = vtk.vtkCleanPolyData()
        clean.SetInputData(poly)
        normals = vtk.vtkPolyDataNormals()
        normals.SetInputConnection(clean.GetOutputPort())
        normals.ConsistencyOn()
        normals.AutoOrientNormalsOn()
        normals.SetFeatureAngle(45)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(normals.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(*color)
        actor.GetProperty().SetInterpolationToPhong()
        actor.GetProperty().SetAmbient(0.3)
        actor.GetProperty().SetDiffuse(0.7)
        actor.GetProperty().SetSpecular(0.2)
        actor.GetProperty().SetSpecularPower(35)
        renderer.AddActor(actor)
    camera = renderer.GetActiveCamera()
    camera.SetPosition(*camera_position)
    camera.SetFocalPoint(0, 0, 16)
    camera.SetViewUp(0, 0, 1)
    camera.ParallelProjectionOn()
    camera.SetParallelScale(57)
    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(1)
    window.SetSize(1200, 800)
    window.AddRenderer(renderer)
    window.Render()
    capture = vtk.vtkWindowToImageFilter()
    capture.SetInput(window)
    capture.ReadFrontBufferOff()
    capture.Update()
    result = (
        vtk_to_numpy(capture.GetOutput().GetPointData().GetScalars())
        .reshape(800, 1200, 3)[::-1]
        .copy()
    )
    window.Finalize()
    return result


fig = plt.figure(figsize=(15, 9), facecolor="#f5f5f7")
fig.text(0.05, 0.94, "hello / Design 1.0", fontsize=32, weight="bold", color="#202124")
fig.text(
    0.05,
    0.89,
    "Open handwritten front. Dense honeycomb rear. One continuous printed body.",
    fontsize=12,
    color="#68686b",
)
for rect, camera, title in [
    ([0.03, 0.46, 0.46, 0.36], (30, -310, 90), "FRONT / connected script"),
    ([0.51, 0.46, 0.46, 0.36], (-100, 270, 135), "REAR / dense honeycomb + braces"),
    ([0.25, 0.10, 0.5, 0.34], (200, -260, 200), "THREE-QUARTER / single slot"),
]:
    ax = fig.add_axes(rect)
    ax.imshow(render_view(camera))
    ax.axis("off")
    ax.set_title(title, y=-0.02, fontsize=11, color="#55555a")
fig.text(
    0.05,
    0.035,
    "Actual CAD geometry — custom lettering, not an official Apple font. Physical validation pending.",
    fontsize=10,
    color="#77777b",
)
fig.savefig(OUT / "preview-v14.png", dpi=160, facecolor=fig.get_facecolor())
(OUT / "validation.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))

# Reuse the established interactive viewer with the newly exported mesh.
template = (OUT / "viewer-template.html").read_text()
mesh = trimesh.load_mesh(OUT / "stand-v14.stl")
data = json.dumps(
    {"v": mesh.vertices.round(5).tolist(), "f": mesh.faces.tolist()},
    separators=(",", ":"),
)
template = re.sub(
    r'(<script type="application/json" id="stand-six-data">).*?(</script>)',
    lambda match: match[1] + data + match[2],
    template,
    flags=re.DOTALL,
)
template = (
    template.replace("hello / 06", "hello / Design 1.0")
    .replace("160 × 70 mm", "150 × 45 mm")
    .replace("第六版", "Design 1.0")
)
(OUT / "viewer.html").write_text(template)
