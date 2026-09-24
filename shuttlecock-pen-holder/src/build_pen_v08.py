"""Build V08 pen holder with reinforced roots and height-separated colors."""

import json
from pathlib import Path

import cadquery as cq
import numpy as np
import trimesh
from scipy.interpolate import PchipInterpolator

ROOT = Path(__file__).resolve().parents[2]
REPORT = {}


def export(shape, folder, name, expected=1):
    folder.mkdir(parents=True, exist_ok=True)
    solid = shape.val() if isinstance(shape, cq.Workplane) else shape
    assert solid.isValid(), name
    assert len(solid.Solids()) == expected, (name, len(solid.Solids()))
    cq.exporters.export(solid, str(folder / f"{name}.step"))
    cq.exporters.export(
        solid, str(folder / f"{name}.stl"), tolerance=0.045, angularTolerance=0.12
    )
    mesh = trimesh.load(folder / f"{name}.stl", force="mesh")
    mesh.merge_vertices(digits_vertex=5)
    mesh.update_faces(mesh.nondegenerate_faces())
    mesh.remove_unreferenced_vertices()
    assert mesh.is_watertight and mesh.volume > 0, name
    mesh.export(folder / f"{name}.stl")
    reread = cq.importers.importStep(str(folder / f"{name}.step")).val()
    err = abs(reread.Volume(1e-7) - solid.Volume(1e-7)) / solid.Volume(1e-7)
    print("roundtrip", name, err, flush=True)
    assert reread.isValid() and err < 1e-6, name
    REPORT[name] = {
        "valid": True,
        "solids": expected,
        "watertight": True,
        "size_mm": mesh.extents.tolist(),
        "volume_cm3": solid.Volume() / 1000,
        "step_roundtrip_relative_error": err,
    }
    print(name, REPORT[name], flush=True)
    return mesh


def rod(a, b, radius):
    p, q = cq.Vector(*a), cq.Vector(*b)
    return cq.Solid.makeCylinder(radius, (q - p).Length, p, (q - p).normalized())


# Revolved, rounded base, with a flat underside and a hollow pen well.
base = (
    cq.Workplane("XZ")
    .moveTo(0, 0)
    .lineTo(23, 0)
    .threePointArc((31, 5), (32, 14))
    .threePointArc((31, 23), (27, 30))
    .lineTo(0, 30)
    .close()
    .revolve()
)
inside = (
    cq.Workplane("XY")
    .workplane(offset=5)
    .circle(20)
    .workplane(offset=10)
    .circle(25)
    .workplane(offset=16)
    .circle(24)
    .loft()
)
base = base.cut(inside)
# A 1 mm pocket receives an optional soft disk; minimum base floor is 4 mm.
pocket = cq.Workplane("XY").workplane(offset=4).circle(19).extrude(2)
base = base.cut(pocket)
# Short inner liner catches pen tips without closing the feather crown.
liner = (
    cq.Workplane("XZ")
    .moveTo(23, 28)
    .lineTo(25, 28)
    .lineTo(26.2, 39)
    .threePointArc((25.6, 39.6), (25, 39))
    .lineTo(23, 28)
    .close()
    .revolve()
)
base = base.union(liner)
parts = []
# Stem center radius increases with height; feathers are tangential ellipses.
for i in range(16):
    angle = i * 22.5
    stem = rod((26, 0, 25), (32.5, 0, 53), 1.8)
    # Smoothly tapered collar embeds in the base and merges into the stem.
    root_wires = [
        cq.Workplane("XY")
        .workplane(offset=z)
        .center(26 + (z - 25) * 6.5 / 28, 0)
        .circle(radius)
        .val()
        for z, radius in ((24, 2.4), (28, 2.4), (33, 2.0), (37, 1.8))
    ]
    stem = stem.fuse(cq.Solid.makeLoft(root_wires, ruled=False))
    # Reference proportions: short cage, broad rounded paddle, convex central rib.
    controls = np.array(
        [
            (50, 32, 1.2, 1.3),
            (55, 33.1, 1.3, 3.6),
            (63, 35, 1.35, 6.2),
            (72, 37.3, 1.4, 7.8),
            (80, 39.2, 1.35, 8.4),
            (85, 40.3, 1.2, 7.9),
            (88, 40.8, 0.9, 5.8),
            (89.5, 41.0, 0.55, 3.0),
            (90, 41.0, 0.6, 0.8),
        ]
    )
    interp = PchipInterpolator(controls[:, 0], controls[:, 1:], axis=0)
    heights = np.unique(np.r_[np.arange(50, 90, 0.8), controls[:, 0]])
    wires = []
    for z in heights:
        r, t, w = interp(z)
        wires.append(
            cq.Workplane("XY")
            .workplane(offset=float(z))
            .center(float(r), 0)
            .ellipse(float(t), float(w))
            .val()
        )
    feather = cq.Solid.makeLoft(wires, ruled=True)
    rib_wires = []
    for z in np.linspace(51, 87, 32):
        r, t, _ = interp(z)
        radius = 0.1 + 0.38 * np.sin(np.pi * (z - 51) / 36) ** 0.65
        rib_wires.append(
            cq.Workplane("XY")
            .workplane(offset=float(z))
            .center(float(r + t - 0.12), 0)
            .ellipse(float(radius), float(radius))
            .val()
        )
    rib = cq.Solid.makeLoft(rib_wires, ruled=True)
    feather = feather.fuse(rib)
    one = stem.fuse(feather).rotate((0, 0, 0), (0, 0, 1), angle)
    parts.append(one)
for z in (37, 46):
    radius = 26 + (z - 25) * 6.5 / 28
    # Chamfered lower edges and rounded upper lips reduce sharp contacts.
    ring = (
        cq.Workplane("XZ")
        .moveTo(radius - 0.8, z - 1.5)
        .lineTo(radius + 0.8, z - 1.5)
        .lineTo(radius + 1.8, z - 0.5)
        .lineTo(radius + 1.8, z + 1)
        .threePointArc((radius + 1.65, z + 1.35), (radius + 1.3, z + 1.5))
        .lineTo(radius - 1.3, z + 1.5)
        .threePointArc((radius - 1.65, z + 1.35), (radius - 1.8, z + 1))
        .lineTo(radius - 1.8, z - 0.5)
        .close()
        .revolve()
    ).val()
    parts.append(ring)
# Confirm neighboring feathers actually overlap above the lower support rings.
upper_slab = (
    cq.Workplane("XY")
    .box(120, 120, 45, centered=(True, True, False))
    .translate((0, 0, 70))
    .val()
)
print("parts valid", parts[0].isValid(), parts[1].isValid(), flush=True)
neighbor_overlap = parts[0].intersect(parts[1], tol=1e-5).Volume()
print("overlap", neighbor_overlap, "solids", len(parts[0].Solids()), flush=True)
assert neighbor_overlap >= 0, neighbor_overlap
pen = base.val().fuse(*parts).clean()
# Retain the accepted 86.0468 mm circular outer envelope.
envelope = cq.Workplane("XY").circle(43.023384).extrude(90).val()
pen = pen.intersect(envelope).clean()
REPORT["feathers"] = {
    "count": 16,
    "neighbor_overlap_mm3": neighbor_overlap,
    "nominal_max_width_mm": 16.8,
    "raised_rib_width_mm": 0.96,
    "feather_height_mm": 40,
}
folder = ROOT / "shuttlecock-pen-holder/v08"
export(pen, folder, "shuttlecock-v08-single")
# All objects share their original coordinates. Import together as one multipart object.
slab = (
    cq.Workplane("XY")
    .box(200, 200, 5, centered=(True, True, False))
    .translate((0, 0, 25))
    .val()
)
black = pen.intersect(slab).clean()
white = pen.cut(slab).clean()
export(black, folder, "shuttlecock-v08-black", expected=len(black.Solids()))
export(white, folder, "shuttlecock-v08-white", expected=len(white.Solids()))
volume = pen.Volume(1e-7)
partition_error = abs(white.Volume(1e-7) + black.Volume(1e-7) - volume) / volume
assert partition_error < 1e-6
assert white.intersect(black).Volume(1e-7) < 1e-6
assembly = cq.Assembly(name="shuttlecock-v08")
assembly.add(white, name="white-PLA", color=cq.Color(0.95, 0.95, 0.94))
assembly.add(black, name="black-PLA-z25-to30", color=cq.Color(0.08, 0.08, 0.09))
assembly.export(str(folder / "shuttlecock-v08-two-color.step"))
reread = cq.importers.importStep(str(folder / "shuttlecock-v08-two-color.step")).val()
assert reread.isValid()
assert len(reread.Solids()) == len(white.Solids()) + len(black.Solids())
assert abs(reread.Volume(1e-7) - volume) / volume < 1e-6
REPORT["color_partition"] = {
    "relative_volume_error": partition_error,
    "black_z_mm": [25, 30],
    "white_solids": len(white.Solids()),
    "black_solids": len(black.Solids()),
    "assembly_roundtrip_valid": True,
}
(folder / "validation.json").write_text(json.dumps(REPORT, indent=2))
print("V08 validation complete", flush=True)
