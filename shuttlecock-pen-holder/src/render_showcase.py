"""Render a two-view V08 CAD presentation; no generated or photographed geometry."""

from pathlib import Path

import vtk
from PIL import Image, ImageDraw, ImageFont
from vtk.util.numpy_support import vtk_to_numpy

ROOT = Path(__file__).resolve().parents[1]
BG = (246, 245, 240)
INK = (54, 66, 59)
MUTED = (102, 117, 106)


def render(position):
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(*(v / 255 for v in BG))
    for part, color in [
        ("white", (0.93, 0.925, 0.89)),
        ("black", (0.075, 0.082, 0.077)),
    ]:
        reader = vtk.vtkSTLReader()
        reader.SetFileName(str(ROOT / f"v08/shuttlecock-v08-{part}.stl"))
        normals = vtk.vtkPolyDataNormals()
        normals.SetInputConnection(reader.GetOutputPort())
        normals.SetFeatureAngle(55)
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(normals.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        prop = actor.GetProperty()
        prop.SetColor(*color)
        prop.SetAmbient(0.30)
        prop.SetDiffuse(0.70)
        prop.SetSpecular(0.12)
        prop.SetSpecularPower(25)
        prop.SetInterpolationToPhong()
        renderer.AddActor(actor)
    camera = renderer.GetActiveCamera()
    camera.SetPosition(*position)
    camera.SetFocalPoint(0, 0, 45)
    camera.SetViewUp(0, 0, 1)
    camera.ParallelProjectionOn()
    camera.SetParallelScale(62)
    win = vtk.vtkRenderWindow()
    win.SetOffScreenRendering(1)
    win.SetSize(840, 840)
    win.SetMultiSamples(8)
    win.AddRenderer(renderer)
    win.Render()
    grab = vtk.vtkWindowToImageFilter()
    grab.SetInput(win)
    grab.ReadFrontBufferOff()
    grab.Update()
    data = vtk_to_numpy(grab.GetOutput().GetPointData().GetScalars())
    result = Image.fromarray(data.reshape(840, 840, 3)[::-1].copy())
    win.Finalize()
    return result


def font(size):
    candidates = [
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default(size=size)


canvas = Image.new("RGB", (1920, 1320), "white")
canvas.paste(Image.new("RGB", (1876, 1248), BG), (22, 20))
canvas.paste(render((0, -260, 65)), (100, 230))
canvas.paste(render((155, -240, 160)), (980, 230))
draw = ImageDraw.Draw(canvas)
draw.text((110, 70), "shuttlecock / 08", font=font(60), fill=INK)
draw.text((1280, 98), "16 FEATHERS / TWO COLORS", font=font(27), fill=MUTED)
draw.text(
    (110, 1140),
    "90 mm tall   /   83.4 mm max diameter   /   white + black PLA",
    font=font(30),
    fill=MUTED,
)
draw.text(
    (110, 1195),
    "CAD render, not a photograph. First print in progress; physical performance not yet verified.",
    font=font(23),
    fill=MUTED,
)
canvas.save(ROOT / "assets/showcase-v08.png")
print(ROOT / "assets/showcase-v08.png")
