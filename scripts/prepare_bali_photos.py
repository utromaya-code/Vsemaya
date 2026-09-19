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
    # Ключевые кадры страницы
    "hero-ocean":      dict(src="gilimeno-0.jpg",  ratio=(21, 9), w=1920, wm=1100, focus=(0.50, 0.68)),
    "chapter-sol":     dict(src="uluwatu-2.jpg",   ratio=(3, 4),  w=900,  wm=600,  focus=(0.28, 0.70), angle=-1.1),
    "chapter-ris":     dict(src="jatiluwih-1.jpg", ratio=(3, 4),  w=900,  wm=600,  focus=(0.42, 0.52)),
    "chapter-tishina": dict(src="gilimeno-3.jpg",  ratio=(3, 4),  w=900,  wm=600,  focus=(0.45, 0.50)),
    "chapter-sanur":   dict(src="sanur-3.jpg",     ratio=(3, 4),  w=900,  wm=600,  focus=(0.55, 0.70)),
    "batur":           dict(src="batur-1.jpg",     ratio=(16, 7), w=2000, wm=1000, focus=(0.50, 0.55)),

    # Галерея маршрута
    "g-uluwatu":   dict(src="uluwatu-3.jpg",    ratio=(4, 3), w=1000, wm=640, focus=(0.55, 0.50)),
    "g-kecak":     dict(src="kecak-4.jpg",      ratio=(4, 3), w=1000, wm=640, focus=(0.50, 0.55)),
    "g-offering":  dict(src="offering-0.jpg",   ratio=(4, 3), w=1000, wm=640, focus=(0.50, 0.50)),
    "g-batukaru":  dict(src="batukaru-0.jpg",   ratio=(4, 3), w=1000, wm=640, focus=(0.50, 0.55)),
    "g-jatiluwih": dict(src="jatiluwih-4.jpg",  ratio=(4, 3), w=1000, wm=640, focus=(0.55, 0.55)),
    "g-meno-dusk": dict(src="menosunset-2.jpg", ratio=(4, 3), w=1000, wm=640, focus=(0.50, 0.50)),
    "g-meno-sun":  dict(src="menosunset-3.jpg", ratio=(4, 3), w=1000, wm=640, focus=(0.50, 0.52)),

    # Съёмка команды. Профиль "team": кадры уже обработаны автором, наша задача —
    # только свести их с остальной страницей, а не переделывать.
    "ilya":           dict(src="ilya-namaste.jpg",   ratio=(4, 5),  w=900,  wm=600, focus=(0.52, 0.40), grade="team"),
    "vita":           dict(src="vita-portrait.jpg",  ratio=(4, 5),  w=900,  wm=600, focus=(0.50, 0.42), grade="team"),
    "practice-move":  dict(src="ilya-taiji.jpg",     ratio=(3, 4),  w=900,  wm=600, focus=(0.50, 0.50), grade="team"),
    "practice-sound": dict(src="vita-bowl.jpg",      ratio=(3, 4),  w=820,  wm=600, focus=(0.45, 0.45), grade="team"),
    "practice-shore": dict(src="vita-shore.jpg",     ratio=(16, 7), w=1280, wm=900, focus=(0.50, 0.52), grade="team"),
    "rhythm-hands":   dict(src="hands-palosanto.jpg", ratio=(3, 4), w=900,  wm=600, focus=(0.50, 0.55), grade="team"),
    # Чёрно-белый кадр греть нельзя — уйдёт в сепию
    "andrey":         dict(src="andrey-src.jpg",     ratio=(4, 3),  w=800,  wm=600, focus=(0.50, 0.50), grade="team"),
    "lab-back":       dict(src="back-mono.jpg",      ratio=(3, 2),  w=1100, wm=700, focus=(0.50, 0.50), grade="mono"),
}


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


PROFILES = {
    # Стоковые пейзажи: обычно перекручены по насыщенности, тени глухие
    "landscape": dict(warm_r=1.022, warm_b=0.982, green=0.86,
                      sat=0.94, contrast=1.04, lift=8, sharpen=70),
    # Съёмка команды: авторский грейд уже есть, тени работают на настроение
    "team": dict(warm_r=1.012, warm_b=0.992, green=0.95,
                 sat=0.98, contrast=1.02, lift=0, sharpen=40),
    # Чёрно-белое: только лёгкая резкость, никакого тонирования
    "mono": dict(warm_r=1.0, warm_b=1.0, green=1.0,
                 sat=1.0, contrast=1.0, lift=0, sharpen=40),
}


def grade(im, profile="landscape"):
    pr = PROFILES[profile]
    im = im.convert("RGB")

    # Тёплый баланс и спокойная зелень
    r, g, b = im.split()
    r = r.point(lambda v: min(255, int(v * pr["warm_r"])))
    b = b.point(lambda v: int(v * pr["warm_b"]))
    im = Image.merge("RGB", (r, g, b))

    grey = im.convert("L").convert("RGB")
    im = Image.blend(im, grey, 1 - pr["sat"])

    # Зелёный канал тянем к серому сильнее остальных
    r, g, b = im.split()
    _, g_grey, _ = grey.split()
    g = Image.blend(g, g_grey, 1 - pr["green"])
    im = Image.merge("RGB", (r, g, b))

    im = ImageEnhance.Contrast(im).enhance(pr["contrast"])

    if pr["lift"]:
        # Приподнятые тени: чёрная точка уходит от нуля
        lift = pr["lift"]
        im = im.point(lambda v: int(lift + v * (255 - lift) / 255))

    im = im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=pr["sharpen"], threshold=3))
    return im


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, spec in SHOTS.items():
        path = SRC / spec["src"]
        if not path.exists():
            print("НЕТ ИСХОДНИКА", spec["src"])
            continue

        im = Image.open(path).convert("RGB")
        angle = spec.get("angle", 0.0)
        if angle:
            # Поворот с последующим кропом краёв, чтобы не осталось пустых углов
            im = im.rotate(angle, resample=Image.BICUBIC, expand=False)
            inset = int(max(im.size) * abs(angle) / 55)
            im = im.crop((inset, inset, im.width - inset, im.height - inset))

        im = crop_to(im, spec["ratio"], spec["focus"])
        im = grade(im, spec.get("grade", "landscape"))

        for suffix, target_w in (("", spec["w"]), ("-m", spec["wm"])):
            target_w = min(target_w, im.width)
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
