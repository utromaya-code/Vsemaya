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

# Antique White — тот же, что фон страницы: зазор в развороте должен исчезать
MILK = (237, 231, 219)

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
    "practice-move":  dict(src="back-mono.jpg",      ratio=(3, 4),  w=900,  wm=600, focus=(0.46, 0.50), grade="mono"),
    "practice-sound": dict(src="vita-bowl.jpg",      ratio=(3, 4),  w=820,  wm=600, focus=(0.45, 0.45), grade="team"),
    "practice-shore": dict(src="vita-shore.jpg",     ratio=(16, 7), w=1280, wm=900, focus=(0.50, 0.52), grade="team"),
    "rhythm-hands":   dict(src="hands-palosanto.jpg", ratio=(3, 4), w=900,  wm=600, focus=(0.50, 0.55), grade="team"),
    # Чёрно-белый кадр греть нельзя — уйдёт в сепию
    "andrey":         dict(src="andrey-src.jpg",     ratio=(4, 3),  w=800,  wm=600, focus=(0.50, 0.50), grade="team"),
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
    # Разворот: половины сняты в разное время суток, поэтому обе уводятся
    # к общему приглушённому тону — иначе тёплый день спорит с синим часом
    "pair-warm": dict(warm_r=1.005, warm_b=1.005, green=0.88,
                      sat=0.80, contrast=1.03, lift=4, sharpen=40),
    "pair-cool": dict(warm_r=1.045, warm_b=0.975, green=0.92,
                      sat=0.86, contrast=1.02, lift=0, sharpen=40),
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


# Разворот для блока лабораторий: два кадра рядом, снятые в одном месте.
# Никакого монтажа «как будто вдвоём» — просто два реальных снимка на одном листе.
DIPTYCHS = {
    "lab-pair": dict(
        left=dict(src="ilya-taiji.jpg", focus=(0.50, 0.46), grade="pair-warm"),
        right=dict(src="vita-move.jpg", focus=(0.50, 0.50), grade="pair-cool"),
        ratio=(3, 4), panel_w=900, w=1840, wm=1100, gap=0.022,
    ),
}


def build_diptychs():
    """Склейка двух кадров с зазором цвета страницы между ними."""
    for name, spec in DIPTYCHS.items():
        panels = []
        for side in ("left", "right"):
            path = SRC / spec[side]["src"]
            if not path.exists():
                print("НЕТ ИСХОДНИКА", spec[side]["src"])
                break
            im = Image.open(path).convert("RGB")
            im = crop_to(im, spec["ratio"], spec[side]["focus"])
            im = grade(im, spec[side].get("grade", "team"))
            pw = spec["panel_w"]
            ph = round(im.height * pw / im.width)
            panels.append(im.resize((pw, ph), Image.LANCZOS))
        else:
            h = min(p.height for p in panels)
            panels = [p.crop((0, 0, p.width, h)) for p in panels]
            gap = round(panels[0].width * spec["gap"])
            sheet = Image.new("RGB", (panels[0].width * 2 + gap, h), MILK)
            sheet.paste(panels[0], (0, 0))
            sheet.paste(panels[1], (panels[0].width + gap, 0))

            for suffix, target_w in (("", spec["w"]), ("-m", spec["wm"])):
                target_w = min(target_w, sheet.width)
                hh = round(sheet.height * target_w / sheet.width)
                out = sheet.resize((target_w, hh), Image.LANCZOS)
                jpg = OUT / f"{name}{suffix}.jpg"
                webp = OUT / f"{name}{suffix}.webp"
                out.save(jpg, "JPEG", quality=78, optimize=True, progressive=True)
                out.save(webp, "WEBP", quality=74, method=6)
                print(f"{name}{suffix}: {out.size[0]}×{out.size[1]}  "
                      f"{jpg.stat().st_size // 1024}KB jpg / {webp.stat().st_size // 1024}KB webp")


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    build_diptychs()
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
