# /// script
# requires-python = ">=3.12"
# dependencies = ["Pillow==12.3.0"]
# ///
"""Compose V13's two actual-mesh renders into the existing gallery board style."""

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
canvas = Image.new("RGB", (1920, 1280), "white")
canvas.paste(Image.new("RGB", (1876, 1220), (246, 245, 240)), (22, 20))
draw = ImageDraw.Draw(canvas)
font_path = next(
    p
    for p in (
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    )
    if p.exists()
)


def text(position, content, size, color=(54, 66, 59)):
    draw.text(
        position, content, font=ImageFont.truetype(str(font_path), size), fill=color
    )


text((100, 70), "palm comb / 13", 60)
text((1260, 98), "FIVE TEETH / ONE PIECE", 27, (102, 117, 106))
for name, x in (("front", 80), ("iso", 1000)):
    picture = Image.open(ROOT / f".gallery-cache/comb-{name}.png").convert("RGBA")
    picture = picture.resize((840, 720), Image.Resampling.LANCZOS)
    canvas.paste(picture, (x, 235), picture)
text(
    (100, 1075),
    "90.53 x 49.22 x 15.30 mm   /   18 mm pitch   /   approx. 20 mm teeth",
    30,
)
text(
    (100, 1140),
    "Actual V13 mesh render, not a photograph. Physical comfort and durability remain untested.",
    23,
)
canvas.save(ROOT / "scalp-massage-comb/assets/design-v13.png")

source = ROOT / "scalp-massage-comb/v13/massage-comb-v13.stl"
report = {
    "image": "design-v13.png",
    "classification": "two-view actual-mesh design render, not a photograph",
    "version": "V13",
    "source": "../v13/massage-comb-v13.stl",
    "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    "geometry_changes": "none; rendered from STL with unit conversion only",
    "views": ["front", "perspective-like orthographic"],
    "renderer": "local Blender background Cycles; no MCP backend available",
    "composition": "neutral board matching the existing two-view project galleries",
    "physical_validation": "not implied by this image",
}
(ROOT / "scalp-massage-comb/assets/design-v13.json").write_text(
    json.dumps(report, indent=2) + "\n"
)
