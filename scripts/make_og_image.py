import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

IMG_DIR = os.path.join(os.path.dirname(__file__), "..", "images")
SRC = os.path.join(IMG_DIR, "hero-pangpema.jpg")
OUT_JPG = os.path.join(IMG_DIR, "og-image.jpg")
OUT_WEBP = os.path.join(IMG_DIR, "og-image.webp")

W, H = 1200, 630

im = Image.open(SRC).convert("RGB")
# cover-crop to 1200x630
src_w, src_h = im.size
target_ratio = W / H
src_ratio = src_w / src_h
if src_ratio > target_ratio:
    new_w = round(src_h * target_ratio)
    left = (src_w - new_w) // 2
    im = im.crop((left, 0, left + new_w, src_h))
else:
    new_h = round(src_w / target_ratio)
    top = (src_h - new_h) // 2
    im = im.crop((0, top, src_w, top + new_h))
im = im.resize((W, H), Image.LANCZOS)

# darken gradient overlay for text legibility (bottom + left)
overlay = Image.new("L", (W, H), 0)
draw_o = ImageDraw.Draw(overlay)
for y in range(H):
    alpha = int(160 * (y / H) ** 1.3)
    draw_o.line([(0, y), (W, y)], fill=alpha)
dark = Image.new("RGB", (W, H), (10, 14, 20))
im = Image.composite(dark, im, overlay)

draw = ImageDraw.Draw(im)

serif_bold = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
sans = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

f_kicker = ImageFont.truetype(sans, 30)
f_title = ImageFont.truetype(serif_bold, 64)
f_sub = ImageFont.truetype(sans, 30)

saffron = (224, 155, 63)
cream = (245, 240, 230)

x = 64
draw.text((x, 380), "КАНЧЕНДЖАНГА · НЕПАЛ", font=f_kicker, fill=saffron)
draw.text((x, 425), "Пять сокровищ снегов", font=f_title, fill=cream)
draw.text((x, 500), "Трек к Канченджанге", font=f_title, fill=cream)
draw.text((x, 575), "5–20 апреля 2027 · северный базовый лагерь, 5143 м", font=f_sub, fill=(214, 210, 202))

im.save(OUT_JPG, "JPEG", quality=85, optimize=True)
im.save(OUT_WEBP, "WEBP", quality=82)
print("saved", OUT_JPG, os.path.getsize(OUT_JPG)//1024, "KB")
