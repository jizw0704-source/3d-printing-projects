"""Original one-piece shoehorn concept; all dimensions are in millimetres."""

import json
import math
from pathlib import Path

import cadquery as cq
from OCP.Standard import Standard_Failure

P = Path(__file__).parent


def section(z, width, thickness, centre_y, curve):
    # A shallow concave ribbon, with rounded sides rather than sharp edges.
    h = width / 2
    edge = centre_y + curve * h * h
    front = [
        (-h + width * i / 8, centre_y + curve * (-h + width * i / 8) ** 2)
        for i in range(1, 9)
    ]
    back = [
        (h - width * i / 8, centre_y + curve * (h - width * i / 8) ** 2 - thickness)
        for i in range(1, 9)
    ]
    return (
        cq.Workplane("XY")
        .workplane(offset=z)
        .moveTo(-h, edge)
        .spline(front, includeCurrent=True)
        .threePointArc((h + thickness / 2, edge - thickness / 2), (h, edge - thickness))
        .spline(back, includeCurrent=True)
        .threePointArc((-h - thickness / 2, edge - thickness / 2), (-h, edge))
        .close()
        .val()
    )


# Keep the lengthwise centre line straight; deepen only the transverse heel cup.
stations = [
    (0, 2, 2, 0, 0.014),
    (2, 14, 2.2, 0, 0.014),
    (6, 26, 2.4, 0, 0.014),
    (14, 34, 2.7, 0, 0.014),
    (40, 38, 3, 0, 0.014),
    (65, 32, 3.6, 0, 0.011),
    (85, 25, 5, 0, 0.006),
    (100, 18, 7, 0, 0.001),
    (115, 16, 7.5, 0, 0),
    (130, 16, 7.5, 0, 0),
    (149, 20, 7.5, 0, 0),
    (157, 22, 7.5, 0, 0),
    (168, 20, 7, 0, 0),
    (175, 12, 5, 0, 0),
    (178, 2, 2, 0, 0),
]
assert all(station[3] == 0 for station in stations)

body = cq.Solid.makeLoft([section(*v) for v in stations], ruled=False)
wp = cq.Workplane("XY").newObject([body])
# A rounded teardrop points toward the heel cup, along the straight handle.
# Two tangent circular ends give a smooth teardrop with a softly rounded tip.
hole_top_radius = 4.3
hole_tip_radius = 0.65
slope = (hole_top_radius - hole_tip_radius) / (160 - 149.5)
c = math.sqrt(1 - slope**2)
tip = (hole_tip_radius * c, 149.5 - hole_tip_radius * slope)
top = (hole_top_radius * c, 160 - hole_top_radius * slope)
hole = (
    cq.Workplane("XZ")
    .moveTo(*tip)
    .lineTo(*top)
    .threePointArc((0, 164.3), (-top[0], top[1]))
    .lineTo(-tip[0], tip[1])
    .threePointArc((0, 148.85), tip)
    .close()
    .extrude(32, both=True)
)
wp = wp.cut(hole)
assert wp.val().isValid(), "Teardrop cut must leave a valid body"
hole_rim_radius = 0
hole_edges = [
    e
    for e in wp.edges().vals()
    if e.BoundingBox().xmin > -5.5
    and e.BoundingBox().xmax < 5.5
    and e.BoundingBox().zmin > 148
    and e.BoundingBox().zmax < 167
    and e.BoundingBox().ylen < 1
]
for radius in (0.35, 0.2):
    try:
        candidate = wp.newObject(hole_edges).fillet(radius)
        if not candidate.val().isValid():
            continue
        wp = candidate
        hole_rim_radius = radius
        break
    except (ValueError, Standard_Failure):
        continue
shape = wp.val()
assert shape.isValid() and len(shape.Solids()) == 1
cq.exporters.export(wp, str(P / "shoehorn-v04.step"))
cq.exporters.export(
    wp, str(P / "shoehorn-v04.stl"), tolerance=0.05, angularTolerance=0.10
)
rt = cq.importers.importStep(str(P / "shoehorn-v04.step")).val()
err = abs(rt.Volume() - shape.Volume()) / shape.Volume()
assert rt.isValid() and err < 1e-5
b = shape.BoundingBox()
(P / "validation.json").write_text(
    json.dumps(
        {
            "status": "design_concept",
            "solid_valid": True,
            "single_solid": True,
            "step_volume_relative_error": err,
            "dimensions_mm": [b.xlen, b.ylen, b.zlen],
            "hanging_hole": "rounded teardrop",
            "hole_rim_fillet_mm": hole_rim_radius,
            "nominal_hole_length_mm": 15.45,
            "nominal_handle_waist_width_mm": 23.5,
            "longitudinal_centre_line": "straight",
            "heel_cup_depth_at_38mm_section_mm": 0.014 * 19**2,
            "blade_nominal_thickness_mm": [2, 3.6],
            "handle_nominal_thickness_mm": 7.5,
            "parts": 1,
            "unverified": [
                "shoe and heel fit",
                "load and repeated bending",
                "print orientation and finish",
            ],
        },
        indent=2,
    )
)
print(
    "One-piece shoehorn exported. STEP round-trip passed. Size:",
    [round(v, 1) for v in (b.xlen, b.ylen, b.zlen)],
)
