#!/usr/bin/env python3
"""Сборка лендинга «Соль. Рис. Тишина.» из bali/content.json.

Весь текст, даты и фото — в bali/content.json. Этот файл только раскладывает
их по разметке. Запуск: python3 scripts/build_bali.py → bali/index.html
"""

import html
import json
import pathlib

import bali_map

ROOT = pathlib.Path(__file__).resolve().parent.parent
BALI = ROOT / "bali"


def e(value):
    return html.escape(str(value), quote=True)


def picture(img, sizes="100vw", cls="", eager=False, load=None):
    """<picture> с webp/jpg и мобильным вариантом (или отдельным кадром для телефона)."""
    base = img["src"]
    mobile = img.get("srcMobile") or base + "-m"
    loading = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
    if load == "eager-low":
        # Лента едет по горизонтали: ленивая загрузка не успевает, грузим сразу, но без приоритета
        loading = 'loading="eager" fetchpriority="low"'
    cls_attr = f' class="{cls}"' if cls else ""
    return (
        f'<picture{cls_attr}>'
        f'<source type="image/webp" media="(max-width: 700px)" srcset="{e(mobile)}.webp">'
        f'<source type="image/webp" srcset="{e(base)}.webp">'
        f'<source media="(max-width: 700px)" srcset="{e(mobile)}.jpg">'
        f'<img src="{e(base)}.jpg" alt="{e(img["alt"])}" width="{img["width"]}" '
        f'height="{img["height"]}" sizes="{e(sizes)}" {loading} decoding="async">'
        f'</picture>'
    )


def label(text, cls=""):
    return f'<p class="label{(" " + cls) if cls else ""}">{e(text)}</p>' if text else ""


# ------------------------------------------------------------------ head

def head(c):
    m, cfg = c["meta"], c["config"]
    robots = '<meta name="robots" content="noindex, nofollow">' if m.get("noindex") else ""
    og_url = m["siteUrl"].rstrip("/") + "/" + m["ogImage"] if m.get("ogImage") else ""
    og = (f'<meta property="og:image" content="{e(og_url)}">'
          '<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">'
          '<meta name="twitter:card" content="summary_large_image">') if og_url else ""
    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q["q"], "acceptedAnswer": {"@type": "Answer", "text": q["a"]}}
        for q in c["faq"]]}
    trip_ld = {"@context": "https://schema.org", "@type": "TouristTrip",
               "name": f'{cfg["projectName"]} {cfg["format"]}', "description": m["description"],
               "touristType": ["Телесные практики", "Йога", "Медитация"]}
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(m['title'])}</title>
<meta name="description" content="{e(m['description'])}">
<link rel="canonical" href="{e(m['siteUrl'])}">
{robots}
<meta property="og:type" content="website">
<meta property="og:locale" content="ru_RU">
<meta property="og:title" content="{e(m['ogTitle'])}">
<meta property="og:description" content="{e(m['ogDescription'])}">
<meta property="og:url" content="{e(m['siteUrl'])}">
{og}
<meta name="theme-color" content="#fbf8f2">
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' fill='%23283044'/%3E%3Cpath d='M4 20c4 0 4-3 8-3s4 3 8 3 4-3 8-3' stroke='%23C3A057' stroke-width='2' fill='none'/%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+Display:wght@400;500&family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="preload" as="image" href="images/cover.webp" media="(min-width: 701px)">
<link rel="preload" as="image" href="images/cover-m.webp" media="(max-width: 700px)">
<link rel="stylesheet" href="styles.css">
<script>document.documentElement.classList.add('js');</script>
<script type="application/ld+json">{json.dumps(trip_ld, ensure_ascii=False)}</script>
<script type="application/ld+json">{json.dumps(faq_ld, ensure_ascii=False)}</script>
</head>
<body>
<a class="skip" href="#main">К содержанию</a>
"""


def header(c):
    cfg = c["config"]
    links = [("Маршрут", "#route"), ("Практики", "#practices"), ("Ведущие", "#team"),
             ("Где живём", "#stay"), ("Программа", "#program"), ("Вопросы", "#faq")]
    items = "".join(f'<li><a href="{h}">{e(t)}</a></li>' for t, h in links)
    return f"""
<header class="header" id="site-header">
  <div class="header__in">
    <a class="header__brand" href="#top">{e(cfg['projectName'])}</a>
    <nav class="nav" id="nav-panel" aria-label="Разделы страницы">
      <ul class="nav__list">{items}</ul>
    </nav>
    <a class="btn btn--primary btn--sm header__cta" href="#request" data-goal="cta_header">{e(cfg['ctaPrimary'])}</a>
    <button class="burger" type="button" id="nav-toggle" aria-expanded="false" aria-controls="nav-panel" aria-label="Открыть меню">
      <span></span><span></span>
    </button>
  </div>
</header>
<main id="main">
"""


# ------------------------------------------------------------------ sections

def stamp(cfg):
    """Круглая печать на обложке: текст по кругу медленно вращается."""
    ring = f"Бали · Гили Мено · {cfg['dates']} · "
    return f"""<div class="stamp" aria-hidden="true">
          <svg viewBox="0 0 200 200"><defs><path id="stamp-ring" d="M100,100 m-74,0 a74,74 0 1,1 148,0 a74,74 0 1,1 -148,0"/></defs>
            <text><textPath href="#stamp-ring" textLength="462">{e(ring)}</textPath></text></svg>
          <span class="stamp__c">11<small>дней</small></span>
        </div>"""


def hero(c):
    """Обложка выпуска: шапка журнала, заголовок-логотип, анонсы и главный кадр."""
    h, cfg = c["hero"], c["config"]
    title = "".join(f"<span>{e(x)}</span>" for x in h["titleLines"])
    facts = "".join(
        f'<div class="cover__fact"><dt>{e(f["label"])}</dt><dd>{e(f["value"])}</dd></div>'
        for f in h["facts"])
    lines = "".join(
        f'<li><a href="{e(l["href"])}"><span class="cover__kicker">{e(l["kicker"])}</span>'
        f'<span class="cover__line">{e(l["text"])}</span></a></li>' for l in h["coverLines"])
    img = h["image"]
    return f"""
<section class="cover" id="top">
  <div class="wrap">
    <div class="cover__strip"><span>{e(h['issue'])}</span><span>{e(h['place'])}</span></div>
    <h1 class="cover__title">{title}</h1>
    <div class="cover__grid">
      <div class="cover__text">
        <p class="cover__tagline">{e(h['tagline'])}</p>
        <p class="cover__sub">{e(h['subtitle'])}</p>
        <dl class="cover__facts">{facts}</dl>
        <div class="cover__actions">
          <a class="btn btn--primary" href="#request" data-goal="cta_hero">{e(cfg['ctaPrimary'])}</a>
          <a class="btn btn--line" href="#route" data-goal="cta_route">{e(cfg['ctaSecondary'])}</a>
        </div>
        <ul class="cover__lines">{lines}</ul>
      </div>
      <figure class="cover__photo">
        {picture(img, sizes="(max-width: 860px) 100vw, 50vw", eager=True)}
        {stamp(cfg)}
      </figure>
    </div>
  </div>
</section>

<div class="refrain" aria-hidden="true"><div class="refrain__track">
{"".join(f"<span>{e(cfg['refrain'])}</span>" for _ in range(6))}
</div></div>
"""


def spread(c):
    """Разворот: фото во всю ширину и одна строка поверх, как в журнале."""
    sp = c["spread"]
    return f"""
<figure class="spread">
  {picture(sp['image'], sizes="100vw")}
  <div class="spread__over"><p class="spread__line wrap">{e(sp['line'])}</p></div>
</figure>
"""


def numbers(c):
    cells = "".join(f'<div class="num"><p class="num__n">{e(x["n"])}</p><p class="num__t">{e(x["t"])}</p></div>'
                    for x in c["numbers"])
    return f"""
<section class="numbers" aria-label="Коротко о поездке">
  <div class="wrap"><div class="numbers__row" data-reveal>{cells}</div></div>
</section>
"""


def intro(c):
    m = c["manifesto"]
    return f"""
<section class="intro">
  <div class="wrap intro__grid">
    <div class="intro__media" data-reveal>
      {picture(m['image'], sizes="(max-width: 860px) 80vw, 34vw", cls="intro__main")}
      {picture(m['image2'], sizes="(max-width: 860px) 40vw, 16vw", cls="intro__small")}
    </div>
    <div class="intro__text" data-reveal>
      <p class="intro__lead">{e(m['text'])}</p>
    </div>
  </div>
</section>
"""


def gallery(c):
    """Лента «Бали в кадрах»: бесконечная прокрутка, копия ленты скрыта от скринридеров."""
    g = c["gallery"]
    def shape(it):
        if it["height"] > it["width"]:
            return "tall"
        return "sq" if it["height"] == it["width"] else "wide"

    def items(hidden):
        hide = ' aria-hidden="true"' if hidden else ""
        return "".join(
            f'<figure class="strip__item strip__item--{shape(it)}"{hide}>'
            f'{picture(dict(it, alt="" if hidden else it["alt"]), sizes="(max-width: 700px) 60vw, 30vw", load="eager-low")}'
            f'</figure>' for it in g["items"])
    return f"""
<section class="strip section--night" aria-labelledby="strip-title">
  <div class="wrap strip__head">
    {label("Атмосфера")}
    <h2 class="h2" id="strip-title">{e(g['title'])}</h2>
  </div>
  <div class="strip__frame">
    <div class="strip__viewport" tabindex="0" data-strip aria-label="Лента фотографий: листайте стрелками, свайпом или клавишами">
      <div class="strip__track">{items(False)}{items(True)}</div>
    </div>
    <button class="strip__btn strip__btn--prev" type="button" data-strip-prev aria-label="Предыдущие фото">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M15 5l-7 7 7 7"/></svg></button>
    <button class="strip__btn strip__btn--next" type="button" data-strip-next aria-label="Следующие фото">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5l7 7-7 7"/></svg></button>
  </div>
</section>
"""


def photo_break(b, cls=""):
    return f"""
<figure class="pbreak{(" " + cls) if cls else ""}">
  {picture(b['image'], sizes="100vw")}
  <figcaption class="pbreak__over wrap">
    <span class="pbreak__line">{e(b['line'])}</span>
  </figcaption>
</figure>
"""


ROMAN = {1: "I", 2: "II", 3: "III", 4: "IV"}


def chapters(c):
    cols = "".join(f"""
      <article class="chapter" data-reveal>
        <div class="chapter__media">{picture(ch['image'], sizes="(max-width: 700px) 80vw, (max-width: 960px) 45vw, 24vw")}
          <span class="chapter__roman">{ROMAN[i]}</span></div>
        <p class="chapter__num">{e(ch['nights'])} · {e(ch['place'])}</p>
        <h3 class="chapter__name">{e(ch['name'])}</h3>
        <p class="chapter__text">{e(ch['text'])}</p>
      </article>""" for i, ch in enumerate(c["chapters"], 1))
    return f"""
<section class="section section--cream" id="route">
  <div class="wrap">
    {label("Маршрут")}
    <h2 class="h2">Четыре главы, одиннадцать дней</h2>
    <div class="map" data-reveal>
      {bali_map.svg("wide")}
      {bali_map.svg("narrow")}
      <p class="map__legend"><span class="map__key map__key--route"></span>Путь группы
        <span class="map__key map__key--trip"></span>Выезды</p>
    </div>
    <div class="chapters">{cols}
    </div>
  </div>
</section>
"""


def practices(c):
    p = c["practices"]
    groups = "".join(f"""
      <article class="practice" data-reveal>
        <div class="practice__media">{picture(g['image'], sizes="(max-width: 760px) 100vw, 45vw")}</div>
        {label(g['time'], 'label--accent')}
        <h3 class="h3">{e(g['title'])}</h3>
        <p class="muted">{e(g['text'])}</p>
        <p class="practice__items">{" · ".join(e(x) for x in g['items'])}</p>
      </article>""" for g in p["groups"])
    return f"""
<section class="section" id="practices">
  <div class="wrap">
    {label("Практики")}
    <h2 class="h2">{e(p['title'])}</h2>
    <div class="practices">{groups}
    </div>
  </div>
</section>
"""


def people(c):
    leaders = "".join(f"""
      <article class="leader" data-reveal>
        <div class="leader__media">{picture({"src": p['image'], "srcMobile": p['imageMobile'], "alt": p['alt'], "width": p['width'], "height": p['height']}, sizes="(max-width: 760px) 100vw, 45vw")}</div>
        {label(p['role'], 'label--accent')}
        <h3 class="leader__name">{e(p['name'])}</h3>
        <p class="muted">{e(p['text'])}</p>
      </article>""" for p in c["leaders"])
    lab, org = c["lab"], c["organizer"]
    lab_imgs = "".join(f'<div class="lab__shot">{picture(i, sizes="(max-width: 760px) 50vw, 26vw")}</div>'
                       for i in lab["images"])
    org_img = {"src": org["image"], "srcMobile": org["imageMobile"], "alt": org["alt"],
               "width": org["width"], "height": org["height"]}
    return f"""
<section class="section section--sand" id="team">
  <div class="wrap">
    {label("Ведущие")}
    <h2 class="h2">Кто ведёт</h2>
    <div class="leaders">{leaders}
    </div>
  </div>
</section>

<section class="section section--night lab">
  <div class="wrap lab__grid">
    <div class="lab__text" data-reveal>
      {label(lab['subtitle'])}
      <h2 class="h2">{e(lab['title'])}</h2>
      <p class="muted">{e(lab['text'])}</p>
    </div>
    <div class="lab__shots" data-reveal>{lab_imgs}</div>
  </div>
</section>

<section class="section org-section">
  <div class="wrap org" data-reveal>
    <div class="org__media">{picture(org_img, sizes="(max-width: 760px) 70vw, 30vw")}</div>
    <div class="org__text">
      {label(org['role'], 'label--accent')}
      <h2 class="org__name">{e(org['name'])}</h2>
      <p class="org__years"><span>{e(org['years'])}</span>{e(org['yearsText'])}</p>
      <p class="org__places">{" · ".join(e(x) for x in org['places'])}</p>
      <p class="org__lead">{e(org['text'])}</p>
      <a class="btn btn--line" href="{e(c['config']['telegramUrl'])}" data-cta="telegram">Написать Андрею</a>
    </div>
  </div>
</section>
"""


def stay(c):
    s = c["stay"]
    rows, plain = [], []
    for n, pl in enumerate(s["places"]):
        if pl.get("images"):
            shots = "".join(
                f'<div class="stay__shot{" stay__shot--wide" if im.get("wide") else ""}">'
                f'{picture(im, sizes="(max-width: 860px) 100vw, 60vw" if im.get("wide") else "(max-width: 860px) 50vw, 30vw")}</div>'
                for im in pl["images"])
            rows.append(f"""
      <article class="stay__place{' stay__place--flip' if n % 2 else ''}" data-reveal>
        <div class="stay__text">
          {label(pl['nights'], 'label--accent')}
          <h3 class="stay__name">{e(pl['place'])}</h3>
          <p class="muted">{e(pl['text'])}</p>
        </div>
        <div class="stay__shots">{shots}</div>
      </article>""")
        else:
            plain.append(f"""
        <article class="stay__plain" data-reveal>
          {label(pl['nights'], 'label--accent')}
          <h3 class="stay__name stay__name--sm">{e(pl['place'])}</h3>
          <p class="muted">{e(pl['text'])}</p>
        </article>""")
    return f"""
<section class="section" id="stay">
  <div class="wrap">
    {label("Размещение")}
    <h2 class="h2">{e(s['title'])}</h2>
    <p class="lead">{e(s['lead'])}</p>
    <div class="stay">{"".join(rows)}
    </div>
    <div class="stay__plainrow">{"".join(plain)}
    </div>
  </div>
</section>
"""


def program(c):
    p = c["program"]
    chapters_html = []
    for ch in p["chapters"]:
        days = []
        for d in ch["days"]:
            did = f"day-{d['n']}"
            blocks = "".join(
                f'<div class="day__block"><p class="day__time">{e(b["time"])}</p><p>{e(b["text"])}</p></div>'
                for b in d["blocks"])
            days.append(f"""
          <article class="day">
            <h4 class="day__h">
              <button class="day__btn" type="button" id="{did}-trigger" aria-expanded="true"
                      aria-controls="{did}-panel" data-day-trigger>
                <span class="day__thumb">{picture(dict(d['image'], alt=""), sizes="120px")}<span class="day__n">{d['n']}</span></span>
                <span class="day__title">{e(d['title'])}<span class="day__sum">{e(d['summary'])}</span></span>
                <span class="day__date">{e(d['date'])}</span>
                <span class="plus" aria-hidden="true"></span>
              </button>
            </h4>
            <div class="day__panel" id="{did}-panel" role="region" aria-labelledby="{did}-trigger">
              {blocks}
            </div>
          </article>""")
        chapters_html.append(f"""
        <section class="prog__chapter">
          <h3 class="prog__chapter-name">{e(ch['name'])} <span>{e(ch['place'])}</span></h3>
          {"".join(days)}
        </section>""")
    return f"""
<section class="section section--sand prog-section" id="program">
  <div class="wrap">
    <div class="prog__head">
      <div>
        {label("Программа")}
        <h2 class="h2">По дням</h2>
      </div>
      <button class="prog__toggle" type="button" aria-expanded="true" aria-controls="program-days" data-program-toggle>
        <span class="prog__toggle-text">Открыть программу · 11 дней</span>
        <span class="prog__toggle-plus plus" aria-hidden="true"></span>
      </button>
    </div>
    <div class="prog__days" id="program-days" role="region" aria-label="Программа по дням">{"".join(chapters_html)}
      <p class="note">{e(p['note'])}</p>
    </div>
  </div>
</section>
"""


def terms(c):
    arr = c["arrival"]
    rows = "".join(f"""
        <div class="road__row" data-reveal><p class="road__time">{e(r['time'])}</p>
          <h3 class="road__title">{e(r['title'])}</h3><p class="muted">{e(r['text'])}</p></div>"""
                   for r in arr["rows"])
    return f"""
<section class="section" id="terms">
  <div class="wrap">
    {label("Как добраться")}
    <h2 class="h2">{e(arr['title'])}</h2>
    <div class="road">{rows}
    </div>
  </div>
</section>
"""


def price(c):
    p, cfg = c["price"], c["config"]
    inc = "".join(f"<li>{e(x)}</li>" for x in p["included"])
    exc = "".join(f"<li>{e(x)}</li>" for x in p["excluded"])
    return f"""
<section class="section section--cream" id="price">
  <div class="wrap">
    {label("Стоимость")}
    <h2 class="h2">{e(p['title'])}</h2>
    <p class="lead">{e(p['lead'])}</p>
    <div class="pack">
      <div><h3 class="pack__h">Входит</h3><ul class="pack__list pack__list--in">{inc}</ul></div>
      <div><h3 class="pack__h">Не входит</h3><ul class="pack__list pack__list--out">{exc}</ul></div>
    </div>
    <a class="btn btn--primary" href="#request" data-goal="cta_price">{e(cfg['ctaPrimary'])}</a>
  </div>
</section>
"""


def faq(c):
    items = "".join(f"""
      <article class="qa">
        <h3 class="qa__h">
          <button class="qa__btn" type="button" id="faq-{i}-trigger" aria-expanded="true"
                  aria-controls="faq-{i}-panel" data-faq-trigger>
            <span>{e(q['q'])}</span><span class="plus" aria-hidden="true"></span>
          </button>
        </h3>
        <div class="qa__panel" id="faq-{i}-panel" role="region" aria-labelledby="faq-{i}-trigger">
          <p>{e(q['a'])}</p>
        </div>
      </article>""" for i, q in enumerate(c["faq"], 1))
    return f"""
<section class="section section--sand" id="faq">
  <div class="wrap faq">
    <div class="faq__side">{label("Вопросы")}<h2 class="h2">Что обычно спрашивают</h2></div>
    <div class="faq__list">{items}
    </div>
  </div>
</section>
"""


def request(c):
    f, cfg = c["form"], c["config"]
    fl = f["fields"]
    channels = "".join(
        f'<label class="radio"><input type="radio" name="channel" value="{e(x)}"{" checked" if i == 0 else ""}><span>{e(x)}</span></label>'
        for i, x in enumerate(fl["channelOptions"]))
    roomings = "".join(f'<option value="{e(x)}">{e(x)}</option>' for x in fl["roomingOptions"])
    contacts = f'<a href="{e(cfg["telegramUrl"])}" data-cta="telegram">Telegram</a>'
    if cfg.get("whatsappNumber"):
        contacts += ' · <a href="#" data-cta="whatsapp">WhatsApp</a>'
    privacy = "Согласен на обработку персональных данных"
    if cfg.get("privacyUrl"):
        privacy = f'Согласен на <a href="{e(cfg["privacyUrl"])}">обработку персональных данных</a>'
    return f"""
<section class="section section--night" id="request">
  <div class="wrap req">
    <div class="req__side">
      {label("Заявка")}
      <h2 class="h2">{e(f['title'])}</h2>
      <p class="lead lead--night">{e(f['lead'])}</p>
      <p class="req__contacts">Или напишите напрямую: {contacts}</p>
    </div>
    <div class="card">
      <form class="form" id="request-form" novalidate>
        <div class="form__row">
          <label class="field"><span class="field__label">{e(fl['name'])}</span>
            <input class="field__input" type="text" id="f-name" name="name" autocomplete="name" required>
            <span class="field__error" data-error-for="name" hidden></span></label>
          <label class="field"><span class="field__label">{e(fl['contact'])}</span>
            <input class="field__input" type="text" id="f-contact" name="contact" autocomplete="tel" required>
            <span class="field__error" data-error-for="contact" hidden></span></label>
        </div>
        <div class="form__row">
          <label class="field"><span class="field__label">{e(fl['email'])}</span>
            <input class="field__input" type="email" id="f-email" name="email" autocomplete="email" aria-describedby="email-hint">
            <span class="field__hint" id="email-hint">{e(fl['emailHint'])}</span>
            <span class="field__error" data-error-for="email" hidden></span></label>
          <label class="field"><span class="field__label">{e(fl['people'])}</span>
            <input class="field__input" type="number" id="f-people" name="people" min="1" max="10" value="1" inputmode="numeric"></label>
        </div>
        <fieldset class="field field--group"><legend class="field__label">{e(fl['channel'])}</legend>
          <div class="radios">{channels}</div></fieldset>
        <label class="field"><span class="field__label">{e(fl['rooming'])}</span>
          <select class="field__input" id="f-rooming" name="rooming">{roomings}</select></label>
        <label class="field"><span class="field__label">{e(fl['comment'])}</span>
          <textarea class="field__input" id="f-comment" name="comment" rows="3" aria-describedby="comment-hint"></textarea>
          <span class="field__hint" id="comment-hint">{e(fl['commentHint'])}</span></label>
        <div class="hp" aria-hidden="true"><label>Не заполняйте<input type="text" name="company" tabindex="-1" autocomplete="off"></label></div>
        <label class="check"><input type="checkbox" id="f-consent" name="consent" required><span>{privacy}</span></label>
        <span class="field__error" data-error-for="consent" hidden></span>
        <button class="btn btn--primary btn--wide" type="submit" data-goal="form_submit">{e(fl['submit'])}</button>
      </form>
      <div class="result" id="form-success" role="status" hidden>
        <h3 class="h3">{e(f['success']['title'])}</h3><p>{e(f['success']['text'])}</p>
      </div>
      <div class="result result--error" id="form-error" role="alert" hidden>
        <h3 class="h3">{e(f['error']['title'])}</h3><p>{e(f['error']['text'])}</p><p>{contacts}</p>
      </div>
    </div>
  </div>
</section>
</main>
"""


def footer(c):
    cfg, f = c["config"], c["footer"]
    links = f'<a href="{e(cfg["telegramUrl"])}" data-cta="telegram">Telegram</a>'
    if cfg.get("whatsappNumber"):
        links += ' <a href="#" data-cta="whatsapp">WhatsApp</a>'
    if cfg.get("privacyUrl"):
        links += f' <a href="{e(cfg["privacyUrl"])}">Политика конфиденциальности</a>'
    credits = "".join(
        f'<li>{e(x["title"])} — {e(x["author"])}, <a href="{e(x["licenseUrl"])}" rel="license noopener" target="_blank">{e(x["license"])}</a>, '
        f'<a href="{e(x["source"])}" rel="noopener" target="_blank">источник</a></li>' for x in c["photoCredits"])
    boot = json.dumps({"telegramUrl": cfg["telegramUrl"], "whatsappNumber": cfg["whatsappNumber"],
                       "prefilledMessage": cfg["prefilledMessage"], "formEndpoint": cfg["formEndpoint"],
                       "ymCounterId": cfg["analytics"]["ymCounterId"]}, ensure_ascii=False)
    return f"""
<footer class="footer">
  <div class="wrap">
    <p class="footer__name">{e(cfg['projectName'])}</p>
    <p class="footer__note">{e(f['note'])}</p>
    <nav class="footer__links" aria-label="Контакты">{links}</nav>
    <p class="footer__small">{e(f['disclaimer'])}</p>
    <details class="credits">
      <summary>{e(f['credits'])}</summary>
      <ul>{credits}</ul>
      <p>Кадры обрезаны и тонированы под общий стиль страницы.</p>
    </details>
  </div>
</footer>

<div class="mobile-bar" id="mobile-bar">
  <span class="mobile-bar__info">{e(cfg['dates'])}</span>
  <a class="btn btn--primary btn--sm" href="#request" data-goal="cta_mobile">{e(cfg['ctaPrimary'])}</a>
</div>

<script>window.BALI_CONFIG = {boot};</script>
<script src="script.js" defer></script>
</body>
</html>
"""


def build():
    c = json.loads((BALI / "content.json").read_text(encoding="utf-8"))
    parts = [head(c), header(c), hero(c), spread(c), numbers(c), intro(c), gallery(c), chapters(c),
             practices(c), photo_break(c["breaks"]["batur"]), people(c), stay(c),
             photo_break(c["breaks"]["gili"], "pbreak--dusk"), program(c), terms(c), price(c), faq(c),
             request(c), footer(c)]
    out = "".join(parts)
    (BALI / "index.html").write_text(out, encoding="utf-8")
    print(f"bali/index.html — {len(out):,} bytes")


if __name__ == "__main__":
    build()
