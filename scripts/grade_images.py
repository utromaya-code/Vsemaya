import os
import sys
from PIL import Image, ImageEnhance, ImageFilter

IMG_DIR = os.path.join(os.path.dirname(__file__), "..", "images")

# Единая цветокоррекция: тёплый мягкий тон, чуть выше контраст и насыщенность,
# усиленная резкость (особенно помогает более мягким кадрам).
CONTRAST = 1.08
COLOR = 1.12
SHARPNESS = 1.6
WARM_R = 1.035
WARM_B = 0.965


def grade(im: Image.Image) -> Image.Image:
    im = im.convert("RGB")

    r, g, b = im.split()
    r = r.point(lambda v: min(255, int(v * WARM_R)))
    b = b.point(lambda v: int(v * WARM_B))
    im = Image.merge("RGB", (r, g, b))

    im = ImageEnhance.Contrast(im).enhance(CONTRAST)
    im = ImageEnhance.Color(im).enhance(COLOR)
    im = im.filter(ImageFilter.UnsharpMask(radius=1.4, percent=110, threshold=2))
    im = ImageEnhance.Sharpness(im).enhance(SHARPNESS / 1.6)  # unsharp already applied; light extra crispness
    return im


def process_file(path: str, quality_jpg=82, quality_webp=80):
    im = Image.open(path)
    graded = grade(im)
    graded.save(path, "JPEG", quality=quality_jpg, optimize=True)
    webp_path = os.path.splitext(path)[0] + ".webp"
    graded.save(webp_path, "WEBP", quality=quality_webp, method=6)
    return graded.size


if __name__ == "__main__":
    args = sys.argv[1:]
    test_mode = "--test" in args

    if test_mode:
        samples = ["hero-pangpema.jpg", "lodge-village.jpg", "ilya.jpg", "sunrise-clouds.jpg", "vivid-massif.jpg"]
        out_dir = "/tmp/grade_test"
        os.makedirs(out_dir, exist_ok=True)
        for name in samples:
            path = os.path.join(IMG_DIR, name)
            if not os.path.exists(path):
                print("MISSING", name)
                continue
            im = Image.open(path)
            im.save(os.path.join(out_dir, "before-" + name), "JPEG", quality=88)
            graded = grade(im)
            graded.save(os.path.join(out_dir, "after-" + name), "JPEG", quality=88)
            print("tested", name, graded.size)
    else:
        skip = {"og-image.jpg", "og-image.webp"}
        files = sorted(f for f in os.listdir(IMG_DIR) if f.endswith(".jpg") and f not in skip)
        for fname in files:
            path = os.path.join(IMG_DIR, fname)
            size = process_file(path)
            print("graded", fname, size)
