import json
from pathlib import Path

import cadquery as cq
import trimesh

ROOT = Path(__file__).resolve().parents[1] / "models" / "v06"
ROOT.mkdir(parents=True, exist_ok=True)


def capsule(a, b, radius):
    p, q = cq.Vector(*a), cq.Vector(*b)
    axis = q - p
    rod = cq.Solid.makeCylinder(radius, axis.Length, p, axis.normalized())
    ends = [cq.Workplane("XY").sphere(radius).val().translate(v) for v in (p, q)]
    return cq.Workplane("XY").newObject([rod.fuse(*ends)])


shape = capsule((0, -55, 7), (0, 49, 7), 7)
for y, w in [(26, 25), (-10, 27)]:
    for sign in (-1, 1):
        start = (0, y - 10, 7)
        middle = (sign * w * 0.54, y - 7, 7)
        end = (sign * w, y + 3, 7)
        path = (
            cq.Workplane("XY")
            .moveTo(0, y - 10)
            .threePointArc((middle[0], middle[1]), (end[0], end[1]))
            .wire()
            .val()
            .translate((0, 0, 7))
        )
        tangent = path.Edges()[0].tangentAt(0)
        plane = cq.Plane(origin=start, normal=tangent)
        rib = cq.Workplane(plane).circle(6).sweep(cq.Workplane("XY").newObject([path]))
        for point in (start, end):
            rib = rib.union(cq.Workplane("XY").sphere(6).translate(point))
        shape = shape.union(rib)
root_edges = [
    e
    for e in shape.val().Edges()
    if e.geomType() == "BSPLINE" and abs(e.Center().x) < 8
]
shape = shape.newObject(root_edges).fillet(2.0)
for sign in (-1, 1):
    shape = shape.union(capsule((0, -52, 7), (sign * 23, -65, 7), 7))
head = cq.Workplane("XY").center(0, 57).circle(15).circle(5).extrude(14)
head = head.edges().fillet(2)
shape = shape.union(head)
shape = shape.cut(
    cq.Workplane("XY").center(0, 57).circle(5).extrude(18).translate((0, 0, -2))
)
# Machine a common flat back, 4 mm above the previous tangent plane.
shape = shape.intersect(
    cq.Workplane("XY")
    .box(200, 200, 30, centered=(True, True, False))
    .translate((0, 0, 4))
).translate((0, 0, -4))
blank = shape


def with_slot(base, throat):
    # Smooth spline cheeks and true circular pocket, aligned with tail axis.
    pocket = cq.Workplane("XY").center(-3, 0).circle(2.7).extrude(20)
    opening = (
        cq.Workplane("XY")
        .moveTo(-3, -throat / 2)
        .lineTo(0, -throat / 2)
        .spline([(3, -throat / 2 - 0.3), (7, -3.5), (12, -4)], includeCurrent=True)
        .lineTo(12, 4)
        .spline([(7, 3.5), (3, throat / 2 + 0.3), (0, throat / 2)], includeCurrent=True)
        .lineTo(-3, throat / 2)
        .close()
        .extrude(20)
    )
    cutter = (
        pocket.union(opening)
        .rotate((0, 0, 0), (0, 0, 1), -29.475889)
        .translate((23, -65, -2))
    )
    result = base.cut(cutter).cut(cutter.mirror("YZ"))
    # Round upper slot contact edges; leave the common bed face flat.
    edges = [
        e
        for e in result.val().Edges()
        if abs(e.Center().x) > 16
        and e.Center().y < -59
        and e.Center().z > 1
        and e.geomType() == "BSPLINE"
    ]
    result = result.newObject(edges).fillet(0.3)
    return result


shape = with_slot(blank, 3.6)
for width in (3.2, 3.6, 4.0):
    sample = with_slot(blank, width).intersect(
        cq.Workplane("XY")
        .box(28, 30, 20, centered=(False, False, False))
        .translate((8, -80, 0))
    )
    assert sample.val().isValid() and len(sample.solids().vals()) == 1
    tag = f"tail-gauge-{width:.1f}"
    cq.exporters.export(sample, str(ROOT / (tag + ".step")))
    cq.exporters.export(
        sample, str(ROOT / (tag + ".stl")), tolerance=0.035, angularTolerance=0.1
    )
assert shape.val().isValid() and len(shape.solids().vals()) == 1
cq.exporters.export(shape, str(ROOT / "fishbone-v06.step"))
cq.exporters.export(
    shape, str(ROOT / "fishbone-v06.stl"), tolerance=0.035, angularTolerance=0.1
)
mesh = trimesh.load(ROOT / "fishbone-v06.stl", force="mesh")
mesh.merge_vertices(digits_vertex=5)
mesh.update_faces(mesh.nondegenerate_faces())
mesh.remove_unreferenced_vertices()
assert mesh.is_watertight and mesh.volume > 0
mesh.export(ROOT / "fishbone-v06.stl")
back = cq.importers.importStep(str(ROOT / "fishbone-v06.step"))
err = abs(back.val().Volume() - shape.val().Volume()) / shape.val().Volume()
assert err < 1e-6
(ROOT / "validation.json").write_text(
    json.dumps(
        {
            "valid_single_solid": True,
            "watertight": True,
            "size_mm": mesh.extents.tolist(),
            "volume_cm3": shape.val().Volume() / 1000,
            "step_roundtrip_relative_error": err,
            "status": "concept; cable capacity, bending radius, hook fit, slicing and physical strength not validated",
        },
        indent=2,
    )
)
