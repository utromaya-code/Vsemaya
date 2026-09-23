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
    # Обложка: золотой час, Вита с чашей — самый тёплый и светлый кадр съёмки
    "cover":     dict(src="vita-bowl.jpg", ratio=(4, 5), w=853, wm=853, focus=(0.45, 0.42), grade="glow"),

    # Разворот сразу за обложкой: террасы Джатилувих и горы
    "spread":    dict(src="u-jatiluwih-mt.jpg", ratio=(2, 1), w=1920, wm=900, focus=(0.50, 0.50), grade="place",
                      mobile=dict(ratio=(4, 5), focus=(0.62, 0.50))),

    # Манифест и практики
    "manifesto":        dict(src="hands-palosanto.jpg", ratio=(4, 5), w=900, wm=820, focus=(0.50, 0.56), grade="team"),
    "practice-morning": dict(src="ilya-taiji.jpg",      ratio=(4, 5), w=900, wm=820, focus=(0.50, 0.52), grade="glow"),
    "practice-evening": dict(src="vita-shore.jpg",      ratio=(4, 5), w=680, wm=640, focus=(0.52, 0.50), grade="team"),

    # Ведущие
    "ilya":     dict(src="ilya-namaste.jpg",  ratio=(4, 5), w=900, wm=820, focus=(0.52, 0.40), grade="team"),
    "vita":     dict(src="vita-portrait.jpg", ratio=(4, 5), w=900, wm=820, focus=(0.50, 0.42), grade="team"),
    "andrey":   dict(src="andrey-src.jpg",    ratio=(4, 5), w=720, wm=720, focus=(0.50, 0.45), grade="portrait"),

    # Илья и Вита вместе: оба кадра в ч/б — журнальный разворот на тёмном
    "lab-back": dict(src="back-mono.jpg", ratio=(3, 4), w=720, wm=600, focus=(0.46, 0.50), grade="bw"),
    "lab-vita": dict(src="vita-move.jpg", ratio=(3, 4), w=820, wm=600, focus=(0.50, 0.50), grade="bw"),

    # Где живём
    "stay-ubud-villa":    dict(src="stay-ubud-villa.jpg",    ratio=(3, 2), w=1125, wm=900, focus=(0.50, 0.55), grade="hotel"),
    "stay-ubud-shala":    dict(src="stay-ubud-shala.jpg",    ratio=(4, 3), w=900,  wm=650, focus=(0.50, 0.52), grade="hotel"),
    "stay-ubud-room":     dict(src="stay-ubud-room.jpg",     ratio=(4, 3), w=900,  wm=650, focus=(0.50, 0.50), grade="hotel"),
    "stay-meno-night":    dict(src="stay-meno-night.jpg",    ratio=(3, 2), w=1080, wm=900, focus=(0.50, 0.50), grade="hotel"),
    "stay-meno-pavilion": dict(src="stay-meno-pavilion.jpg", ratio=(4, 3), w=800,  wm=650, focus=(0.50, 0.50), grade="hotel"),
    "stay-meno-room":     dict(src="stay-meno-room.jpg",     ratio=(4, 3), w=800,  wm=650, focus=(0.50, 0.50), grade="hotel"),
    "stay-balangan-pool":  dict(src="stay-balangan-pool.jpg",  ratio=(3, 2), w=1280, wm=900, focus=(0.50, 0.55), grade="hotel"),
    "stay-balangan-shala": dict(src="stay-balangan-shala.jpg", ratio=(4, 3), w=900,  wm=650, focus=(0.55, 0.45), grade="hotel"),
    "stay-balangan-room":  dict(src="stay-balangan-room.jpg",  ratio=(4, 3), w=900,  wm=650, focus=(0.50, 0.40), grade="hotel"),

    # ---- Места маршрута: свободные лицензии, авторы — в content.json → photoCredits

    # Второй кадр вступления
    "frangipani-sea": dict(src="x-frangipani-sea.jpg", ratio=(4, 5), w=560, wm=480, focus=(0.58, 0.55), grade="place"),

    # Главы маршрута
    "ch-sol":      dict(src="s-uluwatu-cliff.jpg", ratio=(3, 4), w=720, wm=720, focus=(0.42, 0.50), grade="place"),
    "ch-ris":      dict(src="jatiluwih-4.jpg",     ratio=(3, 4), w=720, wm=720, focus=(0.56, 0.55), grade="place"),
    "ch-tishina":  dict(src="gilimeno-0.jpg",      ratio=(3, 4), w=720, wm=720, focus=(0.40, 0.50), grade="place"),
    "ch-return":   dict(src="n-sanur-jukung.jpg",  ratio=(3, 4), w=720, wm=720, focus=(0.46, 0.55), grade="place"),

    # Лента «Бали в кадрах»: разные пропорции, общая высота задаётся в CSS
    "f-kecak":     dict(src="s-kecak-dance.jpg",  ratio=(4, 5), w=560, wm=560, focus=(0.45, 0.50), grade="place"),
    "f-offering":  dict(src="offering-0.jpg",     ratio=(1, 1), w=620, wm=620, focus=(0.50, 0.50), grade="place"),
    "f-dancer":    dict(src="x-dancer.jpg",       ratio=(4, 5), w=560, wm=560, focus=(0.47, 0.45), grade="place"),
    "f-meno":      dict(src="g-meno-boat.jpg",    ratio=(3, 2), w=840, wm=840, focus=(0.55, 0.55), grade="place"),
    "f-gate":      dict(src="x-gate.jpg",         ratio=(4, 5), w=560, wm=560, focus=(0.48, 0.55), grade="place"),
    "f-jukung":    dict(src="n-jukung.jpg",       ratio=(3, 2), w=840, wm=840, focus=(0.45, 0.60), grade="place"),
    "f-penjor":    dict(src="x-penjor.jpg",       ratio=(4, 5), w=560, wm=560, focus=(0.50, 0.35), grade="place"),
    "f-coconut":   dict(src="x-coconut.jpg",      ratio=(1, 1), w=620, wm=620, focus=(0.50, 0.40), grade="place"),
    "f-jungle":    dict(src="u-swing.jpg",        ratio=(4, 5), w=540, wm=540, focus=(0.55, 0.50), grade="place"),
    "f-uluwatu":   dict(src="uluwatu-3.jpg",      ratio=(3, 2), w=840, wm=840, focus=(0.50, 0.50), grade="place"),
    "f-batukaru":  dict(src="batukaru-0.jpg",     ratio=(1, 1), w=620, wm=620, focus=(0.50, 0.55), grade="place"),

    # Разрывы во всю ширину
    "break-batur": dict(src="b-batur-pano.jpg",     ratio=(21, 9), w=1920, wm=900, focus=(0.55, 0.45), grade="place",
                        mobile=dict(ratio=(4, 5), focus=(0.62, 0.45))),
    "break-gili":  dict(src="g-meno-turq.jpg",      ratio=(21, 9), w=1920, wm=900, focus=(0.50, 0.78), grade="place",
                        mobile=dict(ratio=(4, 5), focus=(0.55, 0.50))),

    # Программа: кадр на каждый день
    "d1":  dict(src="s-cliffs-turq.jpg",   ratio=(4, 3), w=480, wm=400, focus=(0.55, 0.50), grade="place"),
    "d2":  dict(src="s-kecak-sunset.jpg",  ratio=(4, 3), w=480, wm=400, focus=(0.55, 0.50), grade="place"),
    "d3":  dict(src="u-ubud-haze.jpg",     ratio=(4, 3), w=480, wm=400, focus=(0.50, 0.50), grade="place"),
    "d4":  dict(src="x-tirta.jpg",         ratio=(4, 3), w=480, wm=400, focus=(0.50, 0.55), grade="place"),
    "d5":  dict(src="batur-1.jpg",         ratio=(4, 3), w=480, wm=400, focus=(0.45, 0.45), grade="place"),
    "d6":  dict(src="x-frangipani.jpg",    ratio=(4, 3), w=480, wm=400, focus=(0.55, 0.50), grade="place"),
    "d7":  dict(src="jatiluwih-1.jpg",     ratio=(4, 3), w=480, wm=400, focus=(0.50, 0.50), grade="place"),
    "d8":  dict(src="g-gili-water.jpg",    ratio=(4, 3), w=480, wm=400, focus=(0.55, 0.45), grade="place"),
    "d9":  dict(src="g-turtle.jpg",        ratio=(4, 3), w=480, wm=400, focus=(0.50, 0.45), grade="place"),
    "d10": dict(src="gilimeno-3.jpg",      ratio=(4, 3), w=480, wm=400, focus=(0.45, 0.50), grade="place"),
    "d11": dict(src="n-sanur-boats.jpg",   ratio=(4, 3), w=480, wm=400, focus=(0.60, 0.55), grade="place"),
}

PROFILES = {
    # Обложка и светлые кадры: чуть теплее и светлее — солнечный глянец
    "glow": dict(warm_r=1.03, warm_b=0.975, green=0.97, sat=1.08, contrast=1.09, sharpen=45, bright=1.05, clarity=18),
    # Честное ч/б без тонирования
    "bw": dict(warm_r=1.0, warm_b=1.0, green=1.0, sat=0.0, contrast=1.14, sharpen=45, clarity=18),
    # Съёмка команды: авторский грейд уже есть, только сводим к общему тону
    "team": dict(warm_r=1.012, warm_b=0.992, green=0.97, sat=1.04, contrast=1.08, sharpen=45, clarity=16),
    # Две половины пары сняты в разное время суток — уводим обе к общему тону
    "pair-warm": dict(warm_r=1.005, warm_b=1.005, green=0.88, sat=0.80, contrast=1.03, sharpen=40),
    "pair-cool": dict(warm_r=1.045, warm_b=0.975, green=0.92, sat=0.86, contrast=1.02, sharpen=40),
    # Селфи с яркой кожей: контраст есть, насыщенность и тепло — вниз
    "portrait": dict(warm_r=0.985, warm_b=1.01, green=1.0, sat=0.84, contrast=1.05, sharpen=40, clarity=10),
    # Гостиничные кадры обычно пересвечены и перекручены по HDR
    "hotel": dict(warm_r=1.01, warm_b=0.995, green=0.92, sat=0.98, contrast=1.05, sharpen=50, clarity=14),
    # Кадры мест из открытых источников: сводим к тёплому глянцу обложки
    "place": dict(warm_r=1.02, warm_b=0.985, green=0.97, sat=1.08, contrast=1.09, sharpen=50, clarity=20),
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
    if pr.get("bright"):
        im = ImageEnhance.Brightness(im).enhance(pr["bright"])
    if pr.get("clarity"):
        # Глянец: мягкий локальный контраст крупным радиусом, как «clarity» в редакторах
        im = im.filter(ImageFilter.UnsharpMask(radius=24, percent=pr["clarity"], threshold=2))
    return im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=pr["sharpen"], threshold=3))


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, spec in SHOTS.items():
        path = SRC / spec["src"]
        if not path.exists():
            print("НЕТ ИСХОДНИКА", spec["src"])
            continue

        src = Image.open(path).convert("RGB")
        im = grade(crop_to(src, spec["ratio"], spec["focus"]), spec["grade"])
        # Для телефона широкий кадр режется заново под вертикальную пропорцию
        mob = spec.get("mobile")
        im_m = grade(crop_to(src, mob["ratio"], mob["focus"]), spec["grade"]) if mob else im

        for suffix, target_w, im in (("", spec["w"], im), ("-m", spec["wm"], im_m)):
            target_w = min(target_w, im.width)
            resized = im.resize((target_w, round(im.height * target_w / im.width)), Image.LANCZOS)
            jpg, webp = OUT / f"{name}{suffix}.jpg", OUT / f"{name}{suffix}.webp"
            resized.save(jpg, "JPEG", quality=80, optimize=True, progressive=True)
            resized.save(webp, "WEBP", quality=78, method=6)
            print(f"{name}{suffix}: {resized.size[0]}×{resized.size[1]}  "
                  f"{jpg.stat().st_size // 1024}KB jpg / {webp.stat().st_size // 1024}KB webp")


if __name__ == "__main__":
    build()
