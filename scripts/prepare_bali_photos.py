#!/usr/bin/env python3
"""Подготовка фотографий для лендинга «Соль. Рис. Тишина.».

Берёт исходники из scripts/bali-originals/, кадрирует, выравнивает горизонт,
приводит к единой цветокоррекции и раскладывает в bali/images/
в четырёх файлах на кадр: jpg/webp × десктоп/мобильный.

Цветокоррекция по ТЗ: мягкий контраст, тёплый свет, естественная зелень.
Никакой перенасыщенности — зелёный специально притушен, потому что
исходники с открытых фотостоков обычно перекручены по Vibrance.

Запуск: python3 scripts/prepare_bali_photos.py
"""

import os
import pathlib

from PIL import Image, ImageEnhance, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "scripts" / "bali-originals"
OUT = ROOT / "bali" / "images"

# name: (исходник, соотношение сторон, ширина десктоп, ширина мобильная,
#        фокус кропа по x и y в долях, поворот в градусах)
SHOTS = {
    "hero-ocean":      ("gilimeno-0.jpg",  (21, 9), 1920, 1100, (0.50, 0.68), 0.0),
    "chapter-sol":     ("uluwatu-2.jpg",   (3, 4),   900,  600, (0.28, 0.70), -1.1),
    "chapter-ris":     ("jatiluwih-1.jpg", (3, 4),   900,  600, (0.42, 0.52), 0.0),
    "chapter-tishina": ("gilimeno-3.jpg",  (3, 4),   900,  600, (0.45, 0.50), 0.0),
    "chapter-sanur":   ("sanur-3.jpg",     (3, 4),   900,  600, (0.55, 0.70), 0.0),
    "batur":           ("batur-1.jpg",     (16, 7), 2000, 1000, (0.50, 0.55), 0.0),
}

# Грейд
WARM_R = 1.022        # тёплый свет
WARM_B = 0.982
GREEN_CALM = 0.86     # насыщенность зелени вниз
SATURATION = 0.94     # общая насыщенность чуть вниз
CONTRAST = 1.04       # мягкий контраст
SHADOW_LIFT = 8       # приподнятые тени, плёночный характер


def crop_to(im, ratio, focus):
    """Кроп под соотношение сторон с заданной точкой интереса."""
    target = ratio[0] / ratio[1]
    w, h = im.size
    current = w / h
    if current > target:
        new_w = int(round(h * target))
        max_x = w - new_w
        x = min(max(int(round(w * focus[0] - new_w / 2)), 0), max_x)
        box = (x, 0, x + new_w, h)
    else:
        new_h = int(round(w / target))
        max_y = h - new_h
        y = min(max(int(round(h * focus[1] - new_h / 2)), 0), max_y)
        box = (0, y, w, y + new_h)
    return im.crop(box)


def grade(im):
    im = im.convert("RGB")

    # Тёплый баланс и спокойная зелень
    r, g, b = im.split()
    r = r.point(lambda v: min(255, int(v * WARM_R)))
    b = b.point(lambda v: int(v * WARM_B))
    im = Image.merge("RGB", (r, g, b))

    grey = im.convert("L").convert("RGB")
    im = Image.blend(im, grey, 1 - SATURATION)

    # Зелёный канал тянем к серому сильнее остальных
    r, g, b = im.split()
    _, g_grey, _ = grey.split()
    g = Image.blend(g, g_grey, 1 - GREEN_CALM)
    im = Image.merge("RGB", (r, g, b))

    im = ImageEnhance.Contrast(im).enhance(CONTRAST)

    # Приподнятые тени: чёрная точка уходит от нуля
    im = im.point(lambda v: int(SHADOW_LIFT + v * (255 - SHADOW_LIFT) / 255))

    im = im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=70, threshold=3))
    return im


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, (src, ratio, w_desktop, w_mobile, focus, angle) in SHOTS.items():
        path = SRC / src
        if not path.exists():
            print("НЕТ ИСХОДНИКА", src)
            continue

        im = Image.open(path).convert("RGB")
        if angle:
            # Поворот с последующим кропом краёв, чтобы не осталось пустых углов
            im = im.rotate(angle, resample=Image.BICUBIC, expand=False)
            inset = int(max(im.size) * abs(angle) / 55)
            im = im.crop((inset, inset, im.width - inset, im.height - inset))

        im = crop_to(im, ratio, focus)
        im = grade(im)

        for suffix, target_w in (("", w_desktop), ("-m", w_mobile)):
            h = round(im.height * target_w / im.width)
            resized = im.resize((target_w, h), Image.LANCZOS)
            jpg = OUT / f"{name}{suffix}.jpg"
            webp = OUT / f"{name}{suffix}.webp"
            # Широкие кадры смотрят с дистанции — там качество можно опустить,
            # первый экран не должен тянуть за собой полмегабайта.
            wide = target_w > 1400
            resized.save(jpg, "JPEG", quality=70 if wide else 80,
                         optimize=True, progressive=True)
            resized.save(webp, "WEBP", quality=66 if wide else 78, method=6)
            print(f"{name}{suffix}: {resized.size[0]}×{resized.size[1]}  "
                  f"{jpg.stat().st_size // 1024}KB jpg / {webp.stat().st_size // 1024}KB webp")


if __name__ == "__main__":
    build()
