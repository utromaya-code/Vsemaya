#!/usr/bin/env python3
"""Подготовка фотографий для лендинга «Соль. Рис. Тишина.».

Все кадры страницы — съёмка команды и фотографии объектов, где группа живёт.
Исходники лежат в scripts/bali-originals/, скрипт кадрирует их, приводит к
общему тону и раскладывает в bali/images/ по четыре файла на кадр:
jpg и webp, десктопный и мобильный размер.

Запуск: python3 scripts/prepare_bali_photos.py
"""

import pathlib

from PIL import Image, ImageEnhance, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "scripts" / "bali-originals"
OUT = ROOT / "bali" / "images"

# ratio — соотношение сторон кропа, w / wm — ширина десктопной и мобильной
# версии, focus — точка, вокруг которой режется кадр (доли ширины и высоты).
SHOTS = {
    # Первый экран: закат у воды. Узкий вариант — для телефона, фигура по центру.
    "hero":       dict(src="vita-shore.jpg", ratio=(3, 2), w=1280, wm=960, focus=(0.50, 0.50), grade="team"),
    "hero-tall":  dict(src="vita-shore.jpg", ratio=(4, 5), w=680,  wm=680, focus=(0.52, 0.50), grade="team"),

    # Манифест и практики
    "manifesto":      dict(src="hands-palosanto.jpg", ratio=(4, 5), w=900, wm=640, focus=(0.50, 0.56), grade="team"),
    "practice-body":  dict(src="back-mono.jpg",       ratio=(4, 5), w=760, wm=640, focus=(0.46, 0.50), grade="mono"),
    "practice-sound": dict(src="vita-bowl.jpg",       ratio=(4, 5), w=820, wm=640, focus=(0.45, 0.42), grade="team"),

    # Ведущие
    "ilya":     dict(src="ilya-namaste.jpg",  ratio=(4, 5), w=900, wm=640, focus=(0.52, 0.40), grade="team"),
    "vita":     dict(src="vita-portrait.jpg", ratio=(4, 5), w=900, wm=640, focus=(0.50, 0.42), grade="team"),
    "lab-ilya": dict(src="ilya-taiji.jpg",    ratio=(3, 4), w=900, wm=640, focus=(0.50, 0.46), grade="pair-warm"),
    "lab-vita": dict(src="vita-move.jpg",     ratio=(3, 4), w=820, wm=640, focus=(0.50, 0.50), grade="pair-cool"),
    "andrey":   dict(src="andrey-src.jpg",    ratio=(4, 5), w=480, wm=480, focus=(0.50, 0.45), grade="team"),

    # Где живём
    "ubud-fog":           dict(src="ubud-fog.jpg",           ratio=(16, 7), w=1280, wm=900, focus=(0.50, 0.55), grade="hotel"),
    "stay-ubud-dusk":     dict(src="stay-ubud-dusk.jpg",     ratio=(3, 2),  w=1280, wm=900, focus=(0.50, 0.50), grade="hotel"),
    "stay-ubud-shala":    dict(src="stay-ubud-shala.jpg",    ratio=(4, 3),  w=900,  wm=650, focus=(0.50, 0.52), grade="hotel"),
    "stay-ubud-room":     dict(src="stay-ubud-room.jpg",     ratio=(4, 3),  w=900,  wm=650, focus=(0.50, 0.50), grade="hotel"),
    "stay-meno-night":    dict(src="stay-meno-night.jpg",    ratio=(3, 2),  w=1080, wm=900, focus=(0.50, 0.50), grade="hotel"),
    "stay-meno-pavilion": dict(src="stay-meno-pavilion.jpg", ratio=(4, 3),  w=800,  wm=650, focus=(0.50, 0.50), grade="hotel"),
    "stay-meno-room":     dict(src="stay-meno-room.jpg",     ratio=(4, 3),  w=800,  wm=650, focus=(0.50, 0.50), grade="hotel"),
}

PROFILES = {
    # Съёмка команды: авторский грейд уже есть, только сводим к общему тону
    "team": dict(warm_r=1.012, warm_b=0.992, green=0.95, sat=0.98, contrast=1.02, sharpen=40),
    # Две половины пары сняты в разное время суток — уводим обе к общему тону
    "pair-warm": dict(warm_r=1.005, warm_b=1.005, green=0.88, sat=0.80, contrast=1.03, sharpen=40),
    "pair-cool": dict(warm_r=1.045, warm_b=0.975, green=0.92, sat=0.86, contrast=1.02, sharpen=40),
    # Гостиничные кадры обычно пересвечены и перекручены по HDR
    "hotel": dict(warm_r=1.01, warm_b=0.995, green=0.84, sat=0.86, contrast=0.98, sharpen=50),
    # Чёрно-белое греть нельзя — уйдёт в сепию
    "mono": dict(warm_r=1.0, warm_b=1.0, green=1.0, sat=1.0, contrast=1.0, sharpen=40),
}


def crop_to(im, ratio, focus):
    """Кроп под соотношение сторон вокруг точки интереса."""
    target = ratio[0] / ratio[1]
    w, h = im.size
    if w / h > target:
        new_w = round(h * target)
        x = min(max(round(w * focus[0] - new_w / 2), 0), w - new_w)
        return im.crop((x, 0, x + new_w, h))
    new_h = round(w / target)
    y = min(max(round(h * focus[1] - new_h / 2), 0), h - new_h)
    return im.crop((0, y, w, y + new_h))


def grade(im, profile):
    pr = PROFILES[profile]
    im = im.convert("RGB")

    r, g, b = im.split()
    r = r.point(lambda v: min(255, int(v * pr["warm_r"])))
    b = b.point(lambda v: min(255, int(v * pr["warm_b"])))
    im = Image.merge("RGB", (r, g, b))

    grey = im.convert("L").convert("RGB")
    im = Image.blend(im, grey, 1 - pr["sat"])

    r, g, b = im.split()
    g = Image.blend(g, grey.split()[1], 1 - pr["green"])
    im = Image.merge("RGB", (r, g, b))

    im = ImageEnhance.Contrast(im).enhance(pr["contrast"])
    return im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=pr["sharpen"], threshold=3))


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, spec in SHOTS.items():
        path = SRC / spec["src"]
        if not path.exists():
            print("НЕТ ИСХОДНИКА", spec["src"])
            continue

        im = crop_to(Image.open(path).convert("RGB"), spec["ratio"], spec["focus"])
        im = grade(im, spec["grade"])

        for suffix, target_w in (("", spec["w"]), ("-m", spec["wm"])):
            target_w = min(target_w, im.width)
            resized = im.resize((target_w, round(im.height * target_w / im.width)), Image.LANCZOS)
            jpg, webp = OUT / f"{name}{suffix}.jpg", OUT / f"{name}{suffix}.webp"
            resized.save(jpg, "JPEG", quality=80, optimize=True, progressive=True)
            resized.save(webp, "WEBP", quality=78, method=6)
            print(f"{name}{suffix}: {resized.size[0]}×{resized.size[1]}  "
                  f"{jpg.stat().st_size // 1024}KB jpg / {webp.stat().st_size // 1024}KB webp")


if __name__ == "__main__":
    build()
