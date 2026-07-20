import os
from PIL import Image, ImageOps

SRC_DIR = os.path.join(os.path.dirname(__file__), "originals")
OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "images")

# name -> (max_width_desktop, max_width_mobile)
SIZES = {
    "hero-pangpema.jpg": (1920, 900),
    "jannu-north-face.jpg": (1600, 800),
    "ghunsa-village.jpg": (1600, 800),
    "rhododendron-1.jpg": (1600, 800),
    "rhododendron-2.jpg": (1600, 800),
    "ilam-tea-garden.jpg": (1600, 800),
    "kanchenjunga-trek.jpg": (1600, 800),
    "glacier-kanchenjunga.jpg": (1920, 900),
    "conservation-area.jpg": (1600, 800),
    "kumbhakarna-view.jpg": (1600, 800),
    "sunset-peaks.jpg": (1920, 900),
    "ilya.jpg": (800, 480),
    "andrey.jpg": (800, 480),
    "golden-sunrise.jpg": (1920, 900),
    "burning-mountain.jpg": (1920, 900),
}

for fname, (w_desktop, w_mobile) in SIZES.items():
    path = os.path.join(SRC_DIR, fname)
    if not os.path.exists(path):
        print("MISSING", fname)
        continue
    im = Image.open(path)
    im = ImageOps.exif_transpose(im)
    im = im.convert("RGB")
    base, _ = os.path.splitext(fname)

    for suffix, target_w in (("", w_desktop), ("-m", w_mobile)):
        w, h = im.size
        if w > target_w:
            new_h = round(h * target_w / w)
            resized = im.resize((target_w, new_h), Image.LANCZOS)
        else:
            resized = im
        jpg_path = os.path.join(OUT_DIR, f"{base}{suffix}.jpg")
        webp_path = os.path.join(OUT_DIR, f"{base}{suffix}.webp")
        resized.save(jpg_path, "JPEG", quality=78, optimize=True)
        resized.save(webp_path, "WEBP", quality=76, method=6)
        print(f"{base}{suffix}: {resized.size} -> {os.path.getsize(jpg_path)//1024}KB jpg, {os.path.getsize(webp_path)//1024}KB webp")
