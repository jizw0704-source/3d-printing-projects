# /// script
# requires-python = ">=3.12,<3.13"
# dependencies = ["pillow", "numpy"]
# ///
"""Lay out untouched, matched CAD renders and verify silhouette preservation."""

import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

P = Path(__file__).parent
front = json.loads((P / "front-mask-validation.json").read_text())
side = json.loads((P / "side-mask-validation.json").read_text())
manifest = json.loads((P / "reference_manifest.json").read_text())
assert front["iou"] >= manifest["validation_thresholds"]["front_mask_iou_min"]
assert side["iou"] >= manifest["validation_thresholds"]["side_mask_iou_min"]
for report in (front, side):
    for old, new in zip(report["reference_bbox"][2:], report["render_bbox"][2:]):
        assert abs(new / old - 1) < 0.03
font = ImageFont.load_default(size=30)
small = ImageFont.load_default(size=23)
canvas = Image.new("RGB", (1920, 1500), "#f7f7f7")
draw = ImageDraw.Draw(canvas)
draw.text((40, 30), "V12 / BEFORE", font=font, fill="#101010")
draw.text((1000, 30), "V13 / SOFT ROOT TRANSITION", font=font, fill="#101010")
for row, view in enumerate(("front", "iso")):
    # The SAME crop, pixel scale, lighting and camera are applied to both versions.
    crop = (70, 100, 1130, 780) if view == "front" else (70, 80, 1130, 840)
    y = 90 if row == 0 else 730
    for column, version in enumerate(("v12", "v13")):
        img = Image.open(P / f"{version}-{view}.png").convert("RGB").crop(crop)
        img.thumbnail((920, 650), Image.Resampling.LANCZOS)
        canvas.paste(img, (20 + column * 960 + (920 - img.width) // 2, y))
    draw.text(
        (40, y + (600 if row == 0 else 660)), view.upper(), font=small, fill="#4a4a4a"
    )
draw.text(
    (40, 1444),
    "Actual STL renders / identical cameras, scale, materials and lights / prototype, not a physical photo",
    font=small,
    fill="#4a4a4a",
)
canvas.save(P / "comparison.png")
old = np.array(Image.open(P / "v12-front-mask.png"))[:, :, 3] > 127
new = np.array(Image.open(P / "v13-front-mask.png"))[:, :, 3] > 127
rgb = np.full((*old.shape, 3), 247, dtype=np.uint8)
rgb[old] = (170, 170, 170)
rgb[new] = (60, 65, 63)
rgb[old & ~new] = (160, 44, 44)
Image.fromarray(rgb).save(P / "front-outline-overlay.png")
report = {
    "front_silhouette_iou_vs_v12": front["iou"],
    "side_silhouette_iou_vs_v12": side["iou"],
    "dimensions_preserved_within_3_percent": True,
    "images": ["comparison.png", "front-outline-overlay.png"],
    "method": "source skill silhouette_validator.py on unlit alpha masks; matched fixed orthographic cameras",
    "meaning": "shape preservation only; does not score naturalness, curvature continuity or comfort",
    "visual_review": "front grip/root crease removed by actual local surface fairing; five rounded tooth contacts and grip rear preserved; final appearance awaits user feedback",
}
(P / "visual-review.json").write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
