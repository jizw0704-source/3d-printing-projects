"""Render the unchanged V14 STL in a sage finish for the README."""

from pathlib import Path
import vtk
from vtk.util.numpy_support import vtk_to_numpy
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
BG = (245, 244, 239)
SAGE = (0.43, 0.58, 0.51)


def render(size, position, scale):
    reader = vtk.vtkSTLReader()
    reader.SetFileName(str(ROOT / "stand-v14.stl"))
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputConnection(reader.GetOutputPort())
    normals.SetFeatureAngle(40)
    normals.ConsistencyOn()
    normals.AutoOrientNormalsOn()
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(normals.GetOutputPort())
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    prop = actor.GetProperty()
    prop.SetColor(*SAGE)
    prop.SetInterpolationToPhong()
    prop.SetAmbient(0.24)
    prop.SetDiffuse(0.76)
    prop.SetSpecular(0.28)
    prop.SetSpecularPower(40)
    scene = vtk.vtkRenderer()
    scene.SetBackground(*(c / 255 for c in BG))
    scene.AddActor(actor)
    scene.AutomaticLightCreationOff()
    for pos, intensity in [((-100, -180, 220), 0.9), ((130, 100, 170), 0.7)]:
        light = vtk.vtkLight()
        light.SetLightTypeToSceneLight()
        light.SetPosition(*pos)
        light.SetFocalPoint(0, 0, 12)
        light.SetIntensity(intensity)
        scene.AddLight(light)
    camera = scene.GetActiveCamera()
    camera.SetPosition(*position)
    camera.SetFocalPoint(0, 0, 17)
    camera.SetViewUp(0, 0, 1)
    camera.ParallelProjectionOn()
    camera.SetParallelScale(scale)
    window = vtk.vtkRenderWindow()
    window.SetOffScreenRendering(1)
    window.SetMultiSamples(8)
    window.SetSize(*size)
    window.AddRenderer(scene)
    window.Render()
    capture = vtk.vtkWindowToImageFilter()
    capture.SetInput(window)
    capture.ReadFrontBufferOff()
    capture.Update()
    pixels = vtk_to_numpy(capture.GetOutput().GetPointData().GetScalars())
    result = Image.fromarray(pixels.reshape(size[1], size[0], 3)[::-1].copy())
    window.Finalize()
    return result


def font(size):
    for path in [
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


canvas = Image.new("RGB", (1800, 1200), BG)
canvas.paste(render((1700, 720), (95, -280, 150), 40), (50, 130))
canvas.paste(render((780, 340), (-95, 280, 135), 42), (990, 810))
draw = ImageDraw.Draw(canvas)
draw.text((90, 50), "hello.", font=font(86), fill="#263d34")
draw.text((1210, 85), "DESIGN 1.0 / SAGE", font=font(28), fill="#526b5c")
draw.line((90, 845, 1710, 845), fill="#d9ded5", width=2)
draw.text((90, 885), "A quieter place for your MacBook.", font=font(34), fill="#263d34")
draw.text(
    (90, 944),
    "Open script. Fine honeycomb. One continuous body.",
    font=font(23),
    fill="#657168",
)
draw.text((90, 994), "150 x 45 mm base  /  22.5 mm slot", font=font(25), fill="#526b5c")
draw.text(
    (90, 1130),
    "Actual Design 1.0 geometry. Concept finish only. Physical validation pending.",
    font=font(21),
    fill="#707a71",
)
draw.text((1370, 1110), "REAR VIEW", font=font(19), fill="#657168")
output = ROOT / "showcase-v14.png"
canvas.save(output, optimize=True)
print(output)
