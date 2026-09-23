"""Карта маршрута: Бали, Ломбок и Гили в одной рисованной SVG.

Береговые линии — Natural Earth 10m (public domain), выгружены в
scripts/data/bali-land.json. Проекция равнопромежуточная с поправкой на
широту: на таком маленьком участке её хватает.

Две версии: широкая для экрана и кадрированная с крупными подписями
для телефона. Обе рисуются из одних и тех же координат.
"""

import json
import math
import pathlib

LAND = json.loads((pathlib.Path(__file__).resolve().parent / "data" / "bali-land.json").read_text())

# Точки маршрута: долгота, широта
P = {
    "dps":       (115.167, -8.748),
    "balangan":  (115.122, -8.793),
    "uluwatu":   (115.086, -8.829),
    "ubud":      (115.263, -8.507),
    "mengening": (115.317, -8.412),
    "batur":     (115.375, -8.242),
    "jatiluwih": (115.131, -8.370),
    "batukaru":  (115.087, -8.334),
    "padangbai": (115.509, -8.531),
    "meno":      (116.057, -8.350),
    "sanur":     (115.263, -8.690),
}

VIEWS = {
    # lon0, lon1, lat_top, lat_bottom, ширина viewBox, масштаб точек
    "wide":   (114.42, 116.30, -7.98, -8.98, 1200, 1.0),
    "narrow": (114.96, 116.14, -8.14, -8.90, 600, 1.5),
}

COS = math.cos(math.radians(8.5))


def _proj(view):
    lon0, lon1, top, bottom, width, _ = VIEWS[view]
    k = width / ((lon1 - lon0) * COS)
    height = round((top - bottom) * k)

    def pt(lon, lat):
        return round((lon - lon0) * COS * k, 1), round((top - lat) * k, 1)
    return pt, width, height


def _ring(pt, ring):
    pts = [pt(*p) for p in ring]
    return "M" + " L".join(f"{x},{y}" for x, y in pts) + "Z"


def _curve(pt, a, b, bend):
    """Плавная дуга от a к b; bend — смещение контрольной точки по нормали (в долях длины)."""
    (x1, y1), (x2, y2) = pt(*P[a]), pt(*P[b])
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    cx, cy = mx - dy * bend, my + dx * bend
    return f"M{x1},{y1} Q{round(cx, 1)},{round(cy, 1)} {x2},{y2}"


def _chain(pt, legs):
    """Несколько дуг подряд одной линией."""
    d = _curve(pt, *legs[0])
    for leg in legs[1:]:
        d += " Q" + _curve(pt, *leg).split(" Q")[1]
    return d


def svg(view="wide"):
    pt, w, h = _proj(view)
    wide = view == "wide"

    land = "".join(f'<path class="map__land" d="{_ring(pt, r)}"/>' for r in LAND.values())

    # Основной путь по главам: Баланган → Убуд → Паданг-Бай → море → Гили Мено,
    # обратный — лодкой в Паданг-Бай и по берегу в Санур
    main = _chain(pt, [("balangan", "ubud", -0.18), ("ubud", "padangbai", 0.12), ("padangbai", "meno", -0.22)])
    back = _chain(pt, [("meno", "padangbai", -0.12), ("padangbai", "sanur", 0.10)])
    trips = "".join(
        f'<path class="map__trip" d="{_curve(pt, a, b, bend)}"/>'
        for a, b, bend in (("ubud", "batur", -0.15), ("ubud", "mengening", 0.2),
                           ("ubud", "jatiluwih", 0.18), ("jatiluwih", "batukaru", 0.3),
                           ("balangan", "uluwatu", 0.3)))

    # Подписи: смещения в em, чтобы размер шрифта из CSS не ломал раскладку.
    # На узкой карте часть подписей переставлена, а мелкие убраны.
    r = VIEWS[view][5]

    def stay(key, roman, name, dx, dy, anchor="start"):
        x, y = pt(*P[key])
        return (f'<g class="map__stay"><circle cx="{x}" cy="{y}" r="{7 * r:.1f}"/>'
                f'<circle class="map__halo" cx="{x}" cy="{y}" r="{15 * r:.1f}"/>'
                f'<text x="{x}" y="{y}" dx="{dx}em" dy="{dy}em" text-anchor="{anchor}">'
                f'<tspan class="map__roman">{roman}</tspan> {name}</text></g>')

    def spot(key, name, dx=0, dy=0, anchor="start"):
        x, y = pt(*P[key])
        text = (f'<text x="{x}" y="{y}" dx="{dx}em" dy="{dy}em" text-anchor="{anchor}">{name}</text>'
                if name else "")
        return f'<g class="map__spot"><circle cx="{x}" cy="{y}" r="{4 * r:.1f}"/>{text}</g>'

    def sea(lon, lat, text, cls="map__sea"):
        x, y = pt(lon, lat)
        return f'<text class="{cls}" x="{x}" y="{y}" text-anchor="middle">{text}</text>'

    if wide:
        stays = [stay("balangan", "I", "Баланган", -0.7, 0.35, "end"), stay("ubud", "II", "Убуд", -0.6, -0.35, "end"),
                 stay("meno", "III", "Гили Мено", 0, -1, "middle"), stay("sanur", "IV", "Санур", 0.75, 0.5)]
        spots = [spot("uluwatu", "Улувату", -1, 2.1, "end"), spot("batur", "Батур", 1, -0.8),
                 spot("mengening", "Мелукат", 1, -0.4), spot("jatiluwih", "Джатилувих", -0.9, 1.6, "end"),
                 spot("batukaru", "Батукару", -0.9, -0.8, "end"), spot("padangbai", "Паданг-Бай", 0.9, 2.1),
                 spot("dps", "Аэропорт", 1, 0.5)]
        labels = [sea(115.62, -8.16, "Море Бали"), sea(115.55, -8.90, "Индийский океан"),
                  sea(114.72, -8.24, "Бали", "map__island"), sea(116.06, -8.66, "Ломбок", "map__island")]
    else:
        stays = [stay("balangan", "I", "Баланган", 0.7, 0.35), stay("ubud", "II", "Убуд", 0.75, 1.15),
                 stay("meno", "III", "Гили Мено", 0.4, -0.9, "end"), stay("sanur", "IV", "Санур", 0.75, 0.5)]
        spots = [spot("uluwatu", "Улувату", 0.9, 1.4), spot("batur", "Батур", 1, -0.6),
                 spot("mengening", "Мелукат", 1, 0), spot("jatiluwih", "Джатилувих", 0.9, -0.7),
                 spot("batukaru", ""), spot("padangbai", "Паданг-Бай", 0.9, 1.9), spot("dps", "")]
        labels = [sea(115.75, -8.21, "Море Бали"), sea(115.74, -8.86, "Индийский океан")]
    stays, spots, labels = "".join(stays), "".join(spots), "".join(labels)
    return f"""<svg class="map__svg map__svg--{view}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="map-title-{view}">
  <title id="map-title-{view}">Карта маршрута: Баланган, Убуд, Гили Мено, Санур и выезды к Улувату, Батуру, Мелукату и Джатилувиху</title>
  <defs><mask id="route-mask-{view}" maskUnits="userSpaceOnUse">
    <path class="map__draw" d="{main}" pathLength="1"/>
    <path class="map__draw map__draw--late" d="{back}" pathLength="1"/>
  </mask></defs>
  {land}
  {labels}
  <g class="map__trips">{trips}</g>
  <g mask="url(#route-mask-{view})">
    <path class="map__route" d="{main}"/>
    <path class="map__route map__route--back" d="{back}"/>
  </g>
  {spots}
  {stays}
</svg>"""
