#!/usr/bin/env python3
"""Сборка лендинга «Соль. Рис. Тишина.» из bali/content.json.

Вся правка контента — в bali/content.json. Верстка и стили не трогаются.
Запуск:  python3 scripts/build_bali.py
Результат: bali/index.html
"""

import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
BALI = ROOT / "bali"


def e(value):
    """Экранирование текста для HTML."""
    return html.escape(str(value), quote=True)


def kicker(text):
    """Моноширинная надпись над заголовком. Пустая строка — значит не нужна."""
    return f'<p class="mono kicker">{e(text)}</p>' if text else ""


def slug(value):
    value = re.sub(r"[^a-z0-9]+", "-", str(value).lower())
    return value.strip("-")


def picture(base, base_mobile, alt, width, height, cls="", loading="lazy", sizes=None):
    """<picture> с webp/jpg и мобильным вариантом."""
    attrs = f' class="{e(cls)}"' if cls else ""
    sizes_attr = f' sizes="{e(sizes)}"' if sizes else ""
    prio = ' fetchpriority="high"' if loading == "eager" else ""
    mobile = base_mobile or base
    return f"""<picture{attrs}>
      <source type="image/webp" media="(max-width: 640px)" srcset="{e(mobile)}.webp">
      <source type="image/webp" srcset="{e(base)}.webp">
      <source media="(max-width: 640px)" srcset="{e(mobile)}.jpg">
      <img src="{e(base)}.jpg" alt="{e(alt)}" width="{width}" height="{height}"{sizes_attr} loading="{loading}" decoding="async"{prio}>
    </picture>"""


def placeholder(shot, ratio="4 / 3", cls=""):
    """Слот под фотографию: описание кадра из ТЗ фотографу.

    Пока реального снимка нет, на странице стоит тональный прямоугольник
    с подписью — без стоковых картинок и без чужих фотографий.
    """
    classes = "shot" + (f" {cls}" if cls else "")
    return f"""<div class="{classes}" style="--shot-ratio: {ratio}" role="img" aria-label="Место для фотографии: {e(shot)}">
      <span class="shot__label">{e(shot)}</span>
    </div>"""


# --------------------------------------------------------------------------
# Секции
# --------------------------------------------------------------------------

def head(c):
    m, cfg = c["meta"], c["config"]
    robots = '\n<meta name="robots" content="noindex, nofollow">' if m.get("noindex") else ""
    og_image = ""
    if m.get("ogImage"):
        og_url = m["ogImage"]
        if not og_url.startswith("http"):
            og_url = m["siteUrl"].rstrip("/") + "/" + og_url.lstrip("/")
        og_image = f"""
<meta property="og:image" content="{e(og_url)}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">"""

    ld = {
        "@context": "https://schema.org",
        "@type": "TouristTrip",
        "name": cfg["projectName"] + " " + cfg["format"],
        "description": m["description"],
        "touristType": ["Телесные практики", "Йога", "Медитация", "Путешествия"],
        "itinerary": {
            "@type": "ItemList",
            "numberOfItems": 4,
            "itemListElement": [
                {"@type": "ListItem", "position": i + 1,
                 "item": {"@type": "Place", "name": s["name"], "address": s["region"]}}
                for i, s in enumerate(c["map"]["stops"])
            ],
        },
    }
    faq_ld = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q["q"],
             "acceptedAnswer": {"@type": "Answer", "text": q["a"]}}
            for q in c["faq"]
        ],
    }

    return f"""<!DOCTYPE html>
<html lang="{e(m['lang'])}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(m['title'])}</title>
<meta name="description" content="{e(m['description'])}">
<meta name="keywords" content="{e(m['keywords'])}">
<link rel="canonical" href="{e(m['siteUrl'])}">{robots}

<meta property="og:type" content="website">
<meta property="og:locale" content="ru_RU">
<meta property="og:title" content="{e(m['ogTitle'])}">
<meta property="og:description" content="{e(m['ogDescription'])}">
<meta property="og:url" content="{e(m['siteUrl'])}">{og_image}

<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' fill='%23EDE7DB'/%3E%3Cpath d='M0 20c4 0 4-3 8-3s4 3 8 3 4-3 8-3 4 3 8 3' stroke='%233E4A63' stroke-width='2' fill='none'/%3E%3C/svg%3E">

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Onest:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="styles.css">
<script>document.documentElement.classList.add('js');</script>

<script type="application/ld+json">
{json.dumps(ld, ensure_ascii=False, indent=2)}
</script>
<script type="application/ld+json">
{json.dumps(faq_ld, ensure_ascii=False, indent=2)}
</script>
</head>
<body>
<a class="skip-link" href="#main">К содержанию</a>
"""


def header(c):
    cfg = c["config"]
    nav = [
        ("Маршрут", "#route"),
        ("Практики", "#practices"),
        ("Ведущие", "#team"),
        ("Программа", "#program"),
        ("Условия", "#terms"),
        ("Вопросы", "#faq"),
    ]
    links = "\n".join(
        f'      <li><a href="{href}">{e(label)}</a></li>' for label, href in nav
    )
    return f"""
<header class="header" id="site-header">
  <div class="header__inner">
    <a class="header__brand" href="#top">
      <span class="header__brand-name">{e(cfg['projectName'])}</span>
      <span class="header__brand-dates">{e(cfg['dates'])}</span>
    </a>

    <button class="header__burger" type="button" id="nav-toggle"
            aria-expanded="false" aria-controls="nav-panel" aria-label="Открыть меню">
      <span class="header__burger-line"></span>
      <span class="header__burger-line"></span>
    </button>

    <nav class="nav" id="nav-panel" aria-label="Основная навигация">
      <ul class="nav__list">
{links}
      </ul>
    </nav>

    <a class="btn btn--primary header__cta" href="#request" data-goal="cta_header">{e(cfg['ctaPrimary'])}</a>
  </div>
</header>
"""


def hero(c):
    cfg, h = c["config"], c["hero"]
    lines = "\n".join(
        f'        <span class="hero__line">{e(line)}</span>' for line in h["titleLines"]
    )
    route = "\n".join(
        f'        <li>{e(stop)}</li>' for stop in h["route"]
    )
    if h.get("image"):
        media = picture(h["image"]["src"], h["image"].get("srcMobile"), h["image"]["alt"],
                        h["image"]["width"], h["image"]["height"],
                        cls="hero__media", loading="eager", sizes="100vw")
    else:
        media = f"""<div class="hero__media hero__media--empty" aria-hidden="true">
      <svg class="hero__waves" viewBox="0 0 1200 320" preserveAspectRatio="none" focusable="false">
        <path d="M0 96c150 0 150-34 300-34s150 34 300 34 150-34 300-34 150 34 300 34"></path>
        <path d="M0 168c150 0 150-34 300-34s150 34 300 34 150-34 300-34 150 34 300 34"></path>
        <path d="M0 240c150 0 150-34 300-34s150 34 300 34 150-34 300-34 150 34 300 34"></path>
      </svg>
    </div>"""

    return f"""
<main id="main">
<section class="hero" id="top">
  <div class="hero__inner">
    <p class="mono hero__eyebrow">{e(h['eyebrow'])}</p>
    <h1 class="hero__title">
{lines}
    </h1>
    <p class="hero__subtitle">{e(h['subtitle'])}</p>
    <p class="hero__tagline">{e(h['tagline'])}</p>
    <ul class="mono hero__route">
{route}
    </ul>
    <div class="hero__actions">
      <a class="btn btn--primary" href="#request" data-goal="cta_hero">{e(cfg['ctaPrimary'])}</a>
      <a class="btn btn--ghost" href="#route" data-goal="cta_route">{e(cfg['ctaSecondary'])}</a>
    </div>
  </div>
  {media}
</section>

<div class="marquee" aria-hidden="true">
  <div class="marquee__track">
    <span>{e(cfg['refrain'])}</span><span>{e(cfg['refrain'])}</span><span>{e(cfg['refrain'])}</span><span>{e(cfg['refrain'])}</span>
  </div>
</div>
"""


def manifesto(c):
    m = c["manifesto"]
    paras = "\n".join(f'      <p>{e(p)}</p>' for p in m["text"])
    return f"""
<section class="section manifesto">
  <div class="wrap wrap--narrow">
    <p class="mono kicker">{e(m['kicker'])}</p>
    <div class="manifesto__lead" data-reveal>
{paras}
    </div>
    <p class="manifesto__note">{e(m['note'])}</p>
  </div>
</section>
"""


def chapters(c):
    cards = []
    for i, ch in enumerate(c["chapters"], start=1):
        img = ch.get("image")
        media = (picture(img["src"], img.get("srcMobile"), img["alt"],
                         img["width"], img["height"],
                         sizes="(max-width: 560px) 100vw, (max-width: 1000px) 50vw, 25vw")
                 if img else placeholder(ch["shot"], ratio="3 / 4"))
        cards.append(f"""      <article class="chapter" data-reveal>
        <div class="chapter__media">
{media}
        </div>
        <div class="chapter__body">
          <p class="mono chapter__index">{i:02d} / {e(ch['nights'])}</p>
          <h3 class="chapter__name">{e(ch['name'])}</h3>
          <p class="mono chapter__place">{e(ch['place'])}</p>
          <p>{e(ch['text'])}</p>
        </div>
      </article>""")
    return f"""
<section class="section section--route" id="route">
  <div class="wrap">
    <p class="mono kicker">Маршрут</p>
    <h2 class="section__title">Четыре главы</h2>
    <div class="chapters">
{chr(10).join(cards)}
    </div>
  </div>
</section>
"""


def practices(c):
    p = c["practices"]
    groups = []
    for g in p["groups"]:
        items = "\n".join(f'          <li>{e(x)}</li>' for x in g["items"])
        img = g.get("image")
        media = ""
        if img:
            media = f"""        <div class="practice__media">
{picture(img["src"], img.get("srcMobile"), img["alt"], img["width"], img["height"],
         sizes="(max-width: 760px) 100vw, 45vw")}
        </div>
"""
        groups.append(f"""      <article class="practice" data-reveal>
{media}        <p class="mono practice__time">{e(g['time'])}</p>
        <h3 class="practice__title">{e(g['title'])}</h3>
        <p>{e(g['text'])}</p>
        <ul class="tags">
{items}
        </ul>
      </article>""")
    w = p.get("wide")
    wide = ""
    if w:
        wide = f"""<div class="practice-wide" data-reveal>
{picture(w["src"], w.get("srcMobile"), w["alt"], w["width"], w["height"],
         cls="practice-wide__media", sizes="100vw")}
    </div>"""

    changes = "\n".join(
        f"""        <li>
          <span class="mono change__place">{e(x['place'])}</span>
          <span class="change__text">{e(x['text'])}</span>
        </li>""" for x in p["howItChanges"]
    )
    return f"""
<section class="section section--practices" id="practices">
  <div class="wrap">
    {kicker(p['kicker'])}
    <h2 class="section__title">Практика следует за маршрутом</h2>
    <p class="section__lead">{e(p['lead'])}</p>
    <div class="practices">
{chr(10).join(groups)}
    </div>
    {wide}
    <div class="changes">
      <h3 class="changes__title">Как практика меняется по пути</h3>
      <ul class="changes__list">
{changes}
      </ul>
    </div>
  </div>
</section>
"""


def team(c):
    cards = []
    for person in c["leaders"]:
        if person.get("image"):
            media = picture(person["image"], person.get("imageMobile"), person["alt"],
                            person["width"], person["height"],
                            sizes="(max-width: 760px) 100vw, 40vw")
        else:
            media = placeholder(person["shot"], ratio="4 / 5")
        cards.append(f"""      <article class="person" data-reveal>
        <div class="person__media">
{media}
        </div>
        <div class="person__body">
          <p class="mono person__role">{e(person['role'])}</p>
          <h3 class="person__name">{e(person['name'])}</h3>
          <p>{e(person['text'])}</p>
        </div>
      </article>""")

    lab = c["lab"]
    lab_img = lab.get("image")
    lab_media = (picture(lab_img["src"], lab_img.get("srcMobile"), lab_img["alt"],
                         lab_img["width"], lab_img["height"],
                         sizes="(max-width: 760px) 100vw, 45vw")
                 if lab_img else placeholder(lab["shot"], ratio="3 / 2"))
    org = c["organizer"]
    org_media = picture(org["image"], org.get("imageMobile"), org["alt"],
                        org["width"], org["height"],
                        sizes="(max-width: 760px) 100vw, 40vw")

    return f"""
<section class="section section--team" id="team">
  <div class="wrap">
    <h2 class="section__title">Кто ведёт</h2>
    <div class="people">
{chr(10).join(cards)}
    </div>

    <article class="lab" data-reveal>
      <div class="lab__body">
        <p class="mono person__role">{e(lab['subtitle'])}</p>
        <h3 class="person__name">{e(lab['title'])}</h3>
        <p>{e(lab['text'])}</p>
      </div>
      <div class="lab__media">
{lab_media}
      </div>
    </article>

    <article class="person person--organizer" data-reveal>
      <div class="person__media">
{org_media}
      </div>
      <div class="person__body">
        <p class="mono person__role">{e(org['role'])}</p>
        <h3 class="person__name">{e(org['name'])}</h3>
        <p>{e(org['text'])}</p>
      </div>
    </article>
  </div>
</section>
"""


def route_map(c):
    m = c["map"]
    stops = []
    for s in m["stops"]:
        places = "\n".join(f'            <li>{e(x)}</li>' for x in s["places"])
        stops.append(f"""      <article class="stop" data-reveal>
        <div class="stop__head">
          <h3 class="stop__name">{e(s['name'])}</h3>
          <p class="mono stop__meta">{e(s['nights'])} · {e(s['dates'])}</p>
          <p class="stop__region">{e(s['region'])}</p>
        </div>
        <ul class="stop__places">
{places}
        </ul>
      </article>""")

    # Лента маршрута: точки и перегоны между ними на одной линии.
    def strip_stop(name, note, muted=False):
        cls = "strip__stop strip__stop--muted" if muted else "strip__stop"
        return f"""        <li class="{cls}">
          <span class="strip__name">{e(name)}</span>
          <span class="mono strip__nights">{e(note)}</span>
        </li>"""

    def strip_leg(mode):
        return f"""        <li class="strip__leg">
          <span class="mono">{e(mode.lower())}</span>
        </li>"""

    strip = [strip_stop(m["start"]["name"], m["start"]["note"], muted=True)]
    for i, stop in enumerate(m["stops"]):
        leg = m["legs"][i] if i < len(m["legs"]) else None
        if leg:
            strip.append(strip_leg(leg["mode"]))
        strip.append(strip_stop(stop["name"], stop["nights"]))

    return f"""
<section class="section section--map" id="map">
  <div class="wrap">
    <p class="mono kicker">{e(m['kicker'])}</p>
    <h2 class="section__title">{e(m['title'])}</h2>
    <p class="section__lead">{e(m['lead'])}</p>

    <ol class="strip" aria-label="Лента маршрута с переездами">
{chr(10).join(strip)}
    </ol>

    <div class="stops">
{chr(10).join(stops)}
    </div>

    <p class="note">{e(m['note'])}</p>
  </div>
</section>
"""


def interlude(c):
    """Полноширинный кадр между разделами. Без него страница слишком ровная."""
    data = c.get("interlude")
    if not data:
        return ""
    img = data["image"]
    media = picture(img["src"], img.get("srcMobile"), img["alt"],
                    img["width"], img["height"], cls="interlude__media", sizes="100vw")
    caption = (f'<p class="mono interlude__caption">{e(data["caption"])}</p>'
               if data.get("caption") else "")
    return f"""
<section class="interlude">
{media}
  {caption}
</section>
"""


def program(c):
    p = c["program"]
    out = []
    for chapter in p["chapters"]:
        days = []
        for day in chapter["days"]:
            blocks = "\n".join(
                f"""            <div class="day__block">
              <p class="mono day__block-time">{e(b['time'])}</p>
              <p class="day__block-text">{e(b['text'])}</p>
            </div>""" for b in day["blocks"]
            )
            did = f"day-{day['n']}"
            stay = ""
            if day["stay"] != "—":
                stay = f'<p class="mono day__stay">Ночь: {e(day["stay"])}</p>'
            days.append(f"""        <article class="day">
          <h4 class="day__heading">
            <button class="day__trigger" type="button" id="{did}-trigger"
                    aria-expanded="true" aria-controls="{did}-panel" data-day-trigger>
              <span class="mono day__n">День {day['n']}</span>
              <span class="day__title">{e(day['title'])}</span>
              <span class="mono day__date">{e(day['date'])}</span>
              <span class="day__icon" aria-hidden="true"></span>
            </button>
          </h4>
          <div class="day__panel" id="{did}-panel" role="region"
               aria-labelledby="{did}-trigger">
            <p class="day__summary">{e(day['summary'])}</p>
{blocks}
            {stay}
          </div>
        </article>""")

        out.append(f"""      <section class="program__chapter">
        <div class="program__chapter-head">
          <h3 class="program__chapter-name">{e(chapter['name'])}</h3>
          <p class="mono program__chapter-place">{e(chapter['place'])}</p>
        </div>
        <div class="days">
{chr(10).join(days)}
        </div>
      </section>""")

    return f"""
<section class="section section--program" id="program">
  <div class="wrap">
    <p class="mono kicker">{e(p['kicker'])}</p>
    <h2 class="section__title">{e(p['title'])}</h2>
    <p class="section__lead">{e(p['lead'])}</p>
    <div class="program__controls">
      <button class="btn btn--text" type="button" id="expand-all" data-expand-all>Раскрыть все дни</button>
    </div>
    <div class="program">
{chr(10).join(out)}
    </div>
    <p class="note">{e(p['note'])}</p>
  </div>
</section>
"""


def gallery(c):
    """Сетка кадров маршрута. Подпись у каждого кадра называет реальное место."""
    g = c.get("gallery")
    if not g or not g.get("items"):
        return ""
    items = []
    for item in g["items"]:
        media = picture(item["src"], item["src"] + "-m", item["alt"], 1000, 750,
                        sizes="(max-width: 560px) 100vw, (max-width: 1000px) 50vw, 25vw")
        items.append(f"""      <figure class="shot-card">
{media}
        <figcaption class="shot-card__cap">
          <span class="shot-card__place">{e(item['caption'])}</span>
          <span class="mono shot-card__day">{e(item['day'])}</span>
        </figcaption>
      </figure>""")
    return f"""
<section class="section section--gallery" id="gallery">
  <div class="wrap">
    {kicker(g.get('kicker'))}
    <h2 class="section__title">{e(g['title'])}</h2>
    <div class="shot-grid" data-reveal>
{chr(10).join(items)}
    </div>
    <p class="note">{e(g['note'])}</p>
  </div>
</section>
"""


def arrival(c):
    """Практика перелёта: чем раньше человек это поймёт, тем раньше купит билет."""
    a = c.get("arrival")
    if not a:
        return ""
    rows = "\n".join(
        f"""        <div class="arrival__row">
          <p class="mono arrival__time">{e(r['time'])}</p>
          <div class="arrival__body">
            <h3 class="arrival__title">{e(r['title'])}</h3>
            <p>{e(r['text'])}</p>
          </div>
        </div>""" for r in a["rows"]
    )
    return f"""
<section class="section section--arrival" id="arrival">
  <div class="wrap wrap--narrow">
    {kicker(a.get('kicker'))}
    <h2 class="section__title">{e(a['title'])}</h2>
    <p class="section__lead">{e(a['lead'])}</p>
    <div class="arrival">
{rows}
    </div>
    <p class="note">{e(a['note'])}</p>
  </div>
</section>
"""


def testimonials(c):
    """Появляется, только когда есть настоящие отзывы с именем и разрешением."""
    t = c.get("testimonials")
    if not t or not t.get("items"):
        return ""
    cards = []
    for item in t["items"]:
        where = f'<span class="mono quote__where">{e(item["where"])}</span>' if item.get("where") else ""
        cards.append(f"""      <figure class="quote" data-reveal>
        <blockquote class="quote__text">{e(item['text'])}</blockquote>
        <figcaption class="quote__who">
          <span class="quote__name">{e(item['name'])}</span>
          {where}
        </figcaption>
      </figure>""")
    return f"""
<section class="section section--quotes" id="testimonials">
  <div class="wrap">
    {kicker(t.get('kicker'))}
    <h2 class="section__title">{e(t['title'])}</h2>
    <div class="quotes">
{chr(10).join(cards)}
    </div>
  </div>
</section>
"""


def rhythm(c):
    r = c["rhythm"]
    rows = "\n".join(
        f"""        <div class="rhythm__row">
          <p class="mono rhythm__time">{e(x['time'])}</p>
          <p class="rhythm__text">{e(x['text'])}</p>
        </div>""" for x in r["rows"]
    )
    img = r.get("image")
    if img:
        media = picture(img["src"], img.get("srcMobile"), img["alt"],
                        img["width"], img["height"],
                        sizes="(max-width: 860px) 100vw, 34vw")
        return f"""
<section class="section section--rhythm">
  <div class="wrap">
    {kicker(r['kicker'])}
    <h2 class="section__title">{e(r['title'])}</h2>
    <div class="rhythm-layout">
      <div>
        <div class="rhythm" data-reveal>
{rows}
        </div>
        <p class="note">{e(r['note'])}</p>
      </div>
      <div class="rhythm__media" data-reveal>
{media}
      </div>
    </div>
  </div>
</section>
"""

    return f"""
<section class="section section--rhythm">
  <div class="wrap wrap--narrow">
    {kicker(r['kicker'])}
    <h2 class="section__title">{e(r['title'])}</h2>
    <div class="rhythm" data-reveal>
{rows}
    </div>
    <p class="note">{e(r['note'])}</p>
  </div>
</section>
"""


def stay(c):
    s = c["stay"]
    cards = []
    for card in s["cards"]:
        reqs = "\n".join(f'          <li>{e(x)}</li>' for x in card["requirements"])
        cards.append(f"""      <article class="stay-card" data-reveal>
        <h3 class="stay-card__place">{e(card['place'])}</h3>
        <p class="mono stay-card__nights">{e(card['nights'])}</p>
        <ul class="stay-card__reqs">
{reqs}
        </ul>
      </article>""")
    return f"""
<section class="section section--stay" id="stay">
  <div class="wrap">
    <p class="mono kicker">{e(s['kicker'])}</p>
    <h2 class="section__title">{e(s['title'])}</h2>
    <p class="section__lead">{e(s['lead'])}</p>
    <div class="stay-cards">
{chr(10).join(cards)}
    </div>
    <p class="note">{e(s['note'])}</p>
  </div>
</section>
"""


def terms(c):
    a = c["audience"]
    items = "\n".join(f'        <li>{e(x)}</li>' for x in a["items"])
    return f"""
<section class="section section--terms" id="terms">
  <div class="wrap">
    <p class="mono kicker">{e(a['kicker'])}</p>
    <h2 class="section__title">{e(a['title'])}</h2>
    <div class="terms">
      <ul class="terms__list" data-reveal>
{items}
      </ul>
      <div class="terms__notes">
        <article class="terms__note" data-reveal>
          <h3>{e(a['load']['title'])}</h3>
          <p>{e(a['load']['text'])}</p>
        </article>
        <article class="terms__note" data-reveal>
          <h3>{e(a['consent']['title'])}</h3>
          <p>{e(a['consent']['text'])}</p>
        </article>
      </div>
    </div>
  </div>
</section>
"""


def price(c):
    p = c["price"]
    inc = "\n".join(f'          <li>{e(x)}</li>' for x in p["included"])
    exc = "\n".join(f'          <li>{e(x)}</li>' for x in p["excluded"])
    will = "\n".join(f'        <li>{e(x)}</li>' for x in p["willInclude"])
    amount = p.get("amount")
    if amount:
        headline = f"""      <p class="price__amount">{e(amount)}</p>
      <p class="price__terms">{e(p.get('terms', ''))}</p>"""
    else:
        headline = f'      <p class="price__status">{e(p["status"])}</p>'

    return f"""
<section class="section section--price" id="price">
  <div class="wrap">
    <p class="mono kicker">{e(p['kicker'])}</p>
    <h2 class="section__title">{e(p['title'])}</h2>

    <div class="price" data-reveal>
{headline}
      <ul class="price__will">
{will}
      </ul>
    </div>

    <div class="package">
      <div class="package__col">
        <h3 class="mono package__title">Входит в стоимость</h3>
        <ul class="package__list package__list--in">
{inc}
        </ul>
      </div>
      <div class="package__col">
        <h3 class="mono package__title">Не входит</h3>
        <ul class="package__list package__list--out">
{exc}
        </ul>
      </div>
    </div>
  </div>
</section>
"""


def faq(c):
    items = []
    for i, item in enumerate(c["faq"], start=1):
        fid = f"faq-{i}"
        items.append(f"""      <article class="faq-item">
        <h3 class="faq-item__heading">
          <button class="faq-item__trigger" type="button" id="{fid}-trigger"
                  aria-expanded="true" aria-controls="{fid}-panel" data-faq-trigger>
            <span>{e(item['q'])}</span>
            <span class="day__icon" aria-hidden="true"></span>
          </button>
        </h3>
        <div class="faq-item__panel" id="{fid}-panel" role="region"
             aria-labelledby="{fid}-trigger">
          <p>{e(item['a'])}</p>
        </div>
      </article>""")
    return f"""
<section class="section section--faq" id="faq">
  <div class="wrap wrap--narrow">
    <h2 class="section__title">Что обычно спрашивают</h2>
    <div class="faq">
{chr(10).join(items)}
    </div>
  </div>
</section>
"""


def request(c):
    f = c["form"]
    fl = f["fields"]
    cfg = c["config"]

    channels = "\n".join(
        f"""            <label class="radio">
              <input type="radio" name="channel" value="{e(x)}"{' checked' if i == 0 else ''}>
              <span>{e(x)}</span>
            </label>""" for i, x in enumerate(fl["channelOptions"])
    )
    roomings = "\n".join(
        f'              <option value="{e(x)}">{e(x)}</option>' for x in fl["roomingOptions"]
    )

    reply = ""
    if cfg.get("replyWindow"):
        reply = f' {e(cfg["replyWindow"])}'

    contacts = [f'<a href="{e(cfg["telegramUrl"])}" data-cta="telegram">Telegram</a>']
    if cfg.get("whatsappNumber"):
        contacts.append('<a href="#" data-cta="whatsapp">WhatsApp</a>')
    if cfg.get("email"):
        contacts.append(f'<a href="mailto:{e(cfg["email"])}">{e(cfg["email"])}</a>')
    contacts_html = " · ".join(contacts)

    privacy = "Согласен на обработку персональных данных"
    if cfg.get("privacyUrl"):
        privacy = (f'Согласен на <a href="{e(cfg["privacyUrl"])}" target="_blank" '
                   f'rel="noopener">обработку персональных данных</a>')

    return f"""
<section class="section section--request" id="request">
  <div class="wrap wrap--narrow">
    {kicker(f['kicker'])}
    <h2 class="section__title">{e(f['title'])}</h2>
    <p class="section__lead">{e(f['lead'])}</p>

    <form class="form" id="request-form" novalidate>
      <div class="form__row">
        <label class="field">
          <span class="field__label">{e(fl['name'])}</span>
          <input class="field__input" type="text" name="name" autocomplete="name" required>
          <span class="field__error" data-error-for="name" hidden></span>
        </label>

        <label class="field">
          <span class="field__label">{e(fl['contact'])}</span>
          <input class="field__input" type="text" name="contact" autocomplete="tel" required>
          <span class="field__error" data-error-for="contact" hidden></span>
        </label>
      </div>

      <div class="form__row">
        <label class="field">
          <span class="field__label">{e(fl['email'])}</span>
          <input class="field__input" type="email" name="email" autocomplete="email"
                 aria-describedby="email-hint">
          <span class="field__hint" id="email-hint">{e(fl['emailHint'])}</span>
          <span class="field__error" data-error-for="email" hidden></span>
        </label>

        <label class="field">
          <span class="field__label">{e(fl['people'])}</span>
          <input class="field__input" type="number" name="people" min="1" max="10" value="1" inputmode="numeric">
        </label>
      </div>

      <fieldset class="field field--group">
        <legend class="field__label">{e(fl['channel'])}</legend>
        <div class="radios">
{channels}
        </div>
      </fieldset>

      <label class="field">
        <span class="field__label">{e(fl['rooming'])}</span>
        <select class="field__input" name="rooming">
{roomings}
        </select>
      </label>

      <label class="field">
        <span class="field__label">{e(fl['comment'])}</span>
        <textarea class="field__input" name="comment" rows="4"
                  aria-describedby="comment-hint"></textarea>
        <span class="field__hint" id="comment-hint">{e(fl['commentHint'])}</span>
      </label>

      <div class="field field--hp" aria-hidden="true">
        <label>Не заполняйте это поле
          <input type="text" name="company" tabindex="-1" autocomplete="off">
        </label>
      </div>

      <label class="checkbox">
        <input type="checkbox" name="consent" required>
        <span>{privacy}</span>
      </label>
      <span class="field__error" data-error-for="consent" hidden></span>

      <button class="btn btn--primary btn--wide" type="submit" data-goal="form_submit">
        {e(fl['submit'])}
      </button>
    </form>

    <div class="form-result" id="form-success" role="status" hidden>
      <h3>{e(f['success']['title'])}</h3>
      <p>{e(f['success']['text'])}{reply}</p>
      <p class="mono form-result__contacts">{contacts_html}</p>
    </div>

    <div class="form-result form-result--error" id="form-error" role="alert" hidden>
      <h3>{e(f['error']['title'])}</h3>
      <p>{e(f['error']['text'])}</p>
      <p class="mono form-result__contacts">{contacts_html}</p>
    </div>
  </div>
</section>
</main>
"""


def footer(c):
    cfg, f = c["config"], c["footer"]
    legal = f'<p class="footer__legal">{e(cfg["legalName"])}</p>' if cfg.get("legalName") else ""
    privacy = ""
    if cfg.get("privacyUrl"):
        privacy = f'<a href="{e(cfg["privacyUrl"])}">Политика конфиденциальности</a>'

    links = [f'<a href="{e(cfg["telegramUrl"])}" data-cta="telegram">Telegram</a>']
    if cfg.get("whatsappNumber"):
        links.append('<a href="#" data-cta="whatsapp">WhatsApp</a>')
    if cfg.get("email"):
        links.append(f'<a href="mailto:{e(cfg["email"])}">{e(cfg["email"])}</a>')
    if privacy:
        links.append(privacy)

    credits = ""
    if f.get("credits"):
        cr = f["credits"]
        items = ", ".join(
            f'{e(x["who"])} — {e(x["what"])} (<a href="{e(x["url"])}" '
            f'rel="license noopener" target="_blank">{e(x["license"])}</a>)'
            for x in cr["items"]
        )
        credits = (f'<p class="footer__credits">{e(cr["intro"])} {items}. '
                   f'{e(cr.get("note", ""))}</p>')

    return f"""
<footer class="footer">
  <div class="wrap">
    <div class="footer__top">
      <p class="footer__name">{e(cfg['projectName'])}</p>
      <p class="mono footer__note">{e(f['note'])}</p>
    </div>
    <nav class="mono footer__links" aria-label="Контакты">
      {' · '.join(links)}
    </nav>
    <p class="footer__disclaimer">{e(f['disclaimer'])}</p>
    {credits}
    {legal}
  </div>
</footer>

<div class="mobile-bar" id="mobile-bar">
  <div class="mobile-bar__info">
    <span class="mono mobile-bar__dates">{e(cfg['dates'])}</span>
    <span class="mono mobile-bar__route">{e(cfg['duration'])}</span>
  </div>
  <a class="btn btn--primary" href="#request" data-goal="cta_mobile">{e(cfg['ctaPrimary'])}</a>
</div>

<script>
window.BALI_CONFIG = {json.dumps({
    "telegramUrl": c["config"]["telegramUrl"],
    "whatsappNumber": c["config"]["whatsappNumber"],
    "prefilledMessage": c["config"]["prefilledMessage"],
    "formEndpoint": c["config"]["formEndpoint"],
    "ymCounterId": c["config"]["analytics"]["ymCounterId"],
}, ensure_ascii=False)};
</script>
<script src="script.js" defer></script>
</body>
</html>
"""


def build():
    c = json.loads((BALI / "content.json").read_text(encoding="utf-8"))
    parts = [
        head(c), header(c), hero(c), manifesto(c), chapters(c), practices(c),
        team(c), route_map(c), interlude(c), program(c), rhythm(c), gallery(c),
        stay(c), arrival(c), terms(c), price(c), testimonials(c), faq(c),
        request(c), footer(c),
    ]
    out = "".join(parts)
    (BALI / "index.html").write_text(out, encoding="utf-8")
    print(f"bali/index.html — {len(out):,} bytes")


if __name__ == "__main__":
    build()
