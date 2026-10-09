from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

P = Path(__file__).parent
im = Image.new("RGB", (2100, 1350), "#f7f6f2")
d = ImageDraw.Draw(im)
f = "/System/Library/Fonts/STHeiti Light.ttc"


def t(x, y, text, size=26, color="#293d35"):
    d.text((x, y), text, font=ImageFont.truetype(f, size), fill=color)


def pic(name, x, y, w):
    a = Image.open(P / name)
    a = a.resize((w, round(a.height * w / a.width)), Image.Resampling.LANCZOS)
    im.paste(a, (x, y))


t(55, 35, "小巧鞋拔 / V04", 46)
t(55, 104, "手柄轻收腰，水滴挂孔，直身与脚跟凹弧。", 29)
pic("shoehorn-render.png", 25, 175, 1320)
pic("blade-detail.png", 1390, 190, 660)
t(1410, 900, "宽头弧面细节", 29)
t(1410, 951, "宽头凹弧深约 5 mm", 26)
t(1410, 999, "手柄轻收腰，圆滑水滴孔", 26)
t(
    55,
    1250,
    "约 18 cm 长 × 4.2 cm 最大宽度  ·  三维模型渲染；耐弯折与鞋型适配待实物试用。",
    27,
    "#6f746e",
)
im.save(P / "shoehorn-design-v04.png")
