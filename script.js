'use strict';

/* ======================================================================
   Единая точка правды для изменяемых значений страницы.
   Меняешь цифру здесь — обновляется везде (хиро, блок цены, мобильная панель).
   ====================================================================== */
const CONFIG = {
  dates: '5–20 апреля 2027',
  datesFull: '5–20 апреля 2027 года',
  days: 16,
  trekkingDays: 12,
  maxAltitude: '5143',
  groupMax: 15,
  priceEarly: 2200,
  priceRegular: 2500,
  earlySpotsTotal: 5,
  spotsLeft: 3,
  deposit: 1000,
  tipsAmount: 100,
  foodMin: 20,
  foodMax: 30,
  telegramHandle: 'vsemaya',
  telegramUrl: 'https://t.me/vsemaya',
  whatsappNumber: '79111660935',
  prefilledMessage:
    'Здравствуйте! Смотрю путешествие к Канченджанге 5–20 апреля. Хочу понять, подойдёт ли мне маршрут.',
};

CONFIG.telegramCtaUrl =
  CONFIG.telegramUrl + '?text=' + encodeURIComponent(CONFIG.prefilledMessage);
CONFIG.whatsappCtaUrl =
  'https://wa.me/' +
  CONFIG.whatsappNumber +
  '?text=' +
  encodeURIComponent(CONFIG.prefilledMessage);

/* ======================================================================
   Высотный профиль маршрута — фирменный элемент страницы.
   Один узел = одна ночёвка. peak/passAlt описывают радиальные точки
   (Пангпема, перевал Селе Ла), где группа поднимается выше, чем ночует.
   ====================================================================== */
const ROUTE_PROFILE = [
  { day: 1, date: '5 апр', place: 'Катманду → Бхадрапур → Илам', alt: 1680, hours: 'перелёт + 3–4 ч', zone: 'tea' },
  { day: 2, date: '6 апр', place: 'Илам → Секатум', alt: 1585, hours: '7–8 ч', zone: 'tea' },
  { day: 3, date: '7 апр', place: 'Секатум → Амджилоса', alt: 2500, hours: '5–6 ч', zone: 'rhodo' },
  { day: 4, date: '8 апр', place: 'Амджилоса → Гьябла', alt: 2730, hours: '4–5 ч', zone: 'rhodo' },
  { day: 5, date: '9 апр', place: 'Гьябла → Гунса', alt: 3500, hours: '5–6 ч', zone: 'conifer' },
  { day: 6, date: '10 апр', place: 'Гунса — днёвка (радиально 3900 м)', alt: 3500, hours: 'день акклиматизации', zone: 'conifer', accl: true, peakAlt: 3900, peakLabel: 'Смотровая точка' },
  { day: 7, date: '11 апр', place: 'Гунса → Камбачен', alt: 4050, hours: '4–5 ч', zone: 'moraine', marker: 'Здесь открывается Жанну' },
  { day: 8, date: '12 апр', place: 'Камбачен → Лонак', alt: 4780, hours: '4–6 ч', zone: 'moraine' },
  { day: 9, date: '13 апр', place: 'Лонак → Пангпема → Лонак', alt: 4780, hours: '8–9 ч', zone: 'moraine', peakAlt: 5143, peakLabel: 'Пангпема — северный базовый лагерь', isMax: true },
  { day: 10, date: '14 апр', place: 'Лонак → Камбачен → Гунса', alt: 3500, hours: '6–8 ч', zone: 'conifer' },
  { day: 11, date: '15 апр', place: 'Гунса → высокий лагерь Селе Ла', alt: 4200, hours: '3–5 ч', zone: 'rhodo' },
  { day: 12, date: '16 апр', place: 'Селе Ла → Церам', alt: 3870, hours: '7–8 ч', zone: 'pass', peakAlt: 4600, peakLabel: 'Перевал Селе Ла' },
  { day: 13, date: '17 апр', place: 'Церам → Тортонг', alt: 2995, hours: '4–5 ч', zone: 'forest' },
  { day: 14, date: '18 апр', place: 'Тортонг → Ясанг', alt: 1780, hours: '5–6 ч', zone: 'forest' },
  { day: 15, date: '19 апр', place: 'Ясанг → Тапледжунг', alt: 1820, hours: '2–3 ч пешком + 4–6 ч джип', zone: 'lowland' },
  { day: 16, date: '20 апр', place: 'Тапледжунг → Бхадрапур → Катманду', alt: 91, hours: 'джип + перелёт', zone: 'lowland' },
];

const ZONE_LABELS = {
  tea: 'Чайные холмы',
  rhodo: 'Рододендроновый лес',
  conifer: 'Хвойный лес',
  moraine: 'Морены и лёд',
  pass: 'Высокий перевал',
  forest: 'Древний лес южной долины',
  lowland: 'Равнина и террасы',
};

const ZONE_COLORS = {
  tea: '#5a6e4f',
  rhodo: '#8a4a4a',
  conifer: '#39493f',
  moraine: '#7c8894',
  pass: '#5b6a86',
  forest: '#465c46',
  lowland: '#7a6a45',
};

/* ---------------------------------------------------------------------
   Применение констант ко всем data-cfg / data-cta элементам страницы
   --------------------------------------------------------------------- */
function applyConfig() {
  document.querySelectorAll('[data-cfg]').forEach((el) => {
    const key = el.getAttribute('data-cfg');
    if (key in CONFIG) {
      el.textContent = CONFIG[key];
    }
  });

  document.querySelectorAll('[data-cta="telegram"]').forEach((el) => {
    el.setAttribute('href', CONFIG.telegramCtaUrl);
  });
  document.querySelectorAll('[data-cta="whatsapp"]').forEach((el) => {
    el.setAttribute('href', CONFIG.whatsappCtaUrl);
  });
}

/* ---------------------------------------------------------------------
   Линия высотного профиля «прорисовывается» при появлении в зоне видимости
   --------------------------------------------------------------------- */
function animateLineDraw(line, container) {
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (prefersReduced || !('IntersectionObserver' in window)) return;

  const length = line.getTotalLength();
  line.style.strokeDasharray = String(length);
  line.style.strokeDashoffset = String(length);

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          line.style.transition = 'stroke-dashoffset 2.4s cubic-bezier(0.22, 1, 0.36, 1)';
          line.style.strokeDashoffset = '0';
          observer.disconnect();
        }
      });
    },
    { threshold: 0.3 }
  );
  observer.observe(container);
}

/* ---------------------------------------------------------------------
   Высотный профиль: рендерим SVG из ROUTE_PROFILE
   --------------------------------------------------------------------- */
function renderAltitudeProfile() {
  const container = document.getElementById('altitude-profile');
  if (!container) return;

  const width = 1000;
  const height = 380;
  const padTop = 56;
  const padBottom = 46;
  const padSide = 28;
  const maxAlt = 5143;
  const minAlt = 0;

  const n = ROUTE_PROFILE.length;
  const stepX = (width - padSide * 2) / (n - 1);
  const yFor = (alt) =>
    padTop + (1 - (alt - minAlt) / (maxAlt - minAlt)) * (height - padTop - padBottom);
  const xFor = (i) => padSide + i * stepX;

  const points = ROUTE_PROFILE.map((d, i) => ({ ...d, x: xFor(i), y: yFor(d.alt) }));

  const NS = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(NS, 'svg');
  svg.setAttribute('viewBox', `0 0 ${width} ${height}`);
  svg.setAttribute('class', 'profile-svg');
  svg.setAttribute('role', 'img');
  svg.setAttribute(
    'aria-label',
    'Высотный профиль маршрута от Бхадрапура (91 м) до северного базового лагеря Канченджанги, Пангпема (5143 м), и обратно'
  );

  // фон: зоны природных поясов
  const zonesGroup = document.createElementNS(NS, 'g');
  zonesGroup.setAttribute('class', 'profile-zones');
  let zoneStart = 0;
  for (let i = 1; i <= n; i++) {
    const zoneChanged = i === n || points[i].zone !== points[zoneStart].zone;
    if (zoneChanged) {
      const rect = document.createElementNS(NS, 'rect');
      const x1 = i === n ? points[n - 1].x + stepX / 2 : (points[i - 1].x + points[i].x) / 2;
      const x0 = zoneStart === 0 ? 0 : (points[zoneStart - 1].x + points[zoneStart].x) / 2;
      rect.setAttribute('x', x0);
      rect.setAttribute('y', padTop - 30);
      rect.setAttribute('width', Math.max(0, x1 - x0));
      rect.setAttribute('height', height - padTop - padBottom + 30);
      rect.setAttribute('fill', ZONE_COLORS[points[zoneStart].zone]);
      rect.setAttribute('opacity', '0.12');
      zonesGroup.appendChild(rect);
      zoneStart = i;
    }
  }
  svg.appendChild(zonesGroup);

  // линия высоты (ночёвки)
  const pathD = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');
  const areaD = `${pathD} L ${points[n - 1].x} ${height - padBottom} L ${points[0].x} ${height - padBottom} Z`;

  const area = document.createElementNS(NS, 'path');
  area.setAttribute('d', areaD);
  area.setAttribute('class', 'profile-area');
  svg.appendChild(area);

  const line = document.createElementNS(NS, 'path');
  line.setAttribute('d', pathD);
  line.setAttribute('class', 'profile-line');
  svg.appendChild(line);

  // радиальные пики (Пангпема, перевал, смотровая в Гунсе)
  points.forEach((p) => {
    if (p.peakAlt) {
      const py = yFor(p.peakAlt);
      const tick = document.createElementNS(NS, 'line');
      tick.setAttribute('x1', p.x);
      tick.setAttribute('y1', p.y);
      tick.setAttribute('x2', p.x);
      tick.setAttribute('y2', py);
      tick.setAttribute('class', 'profile-peak-tick');
      svg.appendChild(tick);

      const peakDot = document.createElementNS(NS, 'circle');
      peakDot.setAttribute('cx', p.x);
      peakDot.setAttribute('cy', py);
      peakDot.setAttribute('r', p.isMax ? 7 : 5);
      peakDot.setAttribute('class', p.isMax ? 'profile-peak-dot profile-peak-dot--max' : 'profile-peak-dot');
      svg.appendChild(peakDot);

      const label = document.createElementNS(NS, 'text');
      label.setAttribute('x', p.x);
      label.setAttribute('y', py - (p.isMax ? 16 : 12));
      label.setAttribute('class', p.isMax ? 'profile-label profile-label--max' : 'profile-label');
      label.setAttribute('text-anchor', p.x > width - 120 ? 'end' : p.x < 120 ? 'start' : 'middle');
      label.textContent = `${p.peakLabel} · ${p.peakAlt} м`;
      svg.appendChild(label);
    }
  });

  // точки ночёвок
  points.forEach((p) => {
    const dot = document.createElementNS(NS, 'circle');
    dot.setAttribute('cx', p.x);
    dot.setAttribute('cy', p.y);
    dot.setAttribute('r', p.accl ? 6 : 4.5);
    dot.setAttribute('class', p.accl ? 'profile-dot profile-dot--accl' : 'profile-dot');
    svg.appendChild(dot);

    if (p.marker) {
      const markerText = document.createElementNS(NS, 'text');
      markerText.setAttribute('x', p.x);
      markerText.setAttribute('y', p.y - 18);
      markerText.setAttribute('class', 'profile-marker');
      markerText.setAttribute('text-anchor', p.x > width - 140 ? 'end' : 'middle');
      markerText.textContent = p.marker;
      svg.appendChild(markerText);
    }

    // день + высота под графиком
    const dayLabel = document.createElementNS(NS, 'text');
    dayLabel.setAttribute('x', p.x);
    dayLabel.setAttribute('y', height - padBottom + 20);
    dayLabel.setAttribute('class', 'profile-day');
    dayLabel.setAttribute('text-anchor', 'middle');
    dayLabel.textContent = `Д${p.day}`;
    svg.appendChild(dayLabel);

    const altLabel = document.createElementNS(NS, 'text');
    altLabel.setAttribute('x', p.x);
    altLabel.setAttribute('y', height - padBottom + 36);
    altLabel.setAttribute('class', 'profile-alt');
    altLabel.setAttribute('text-anchor', 'middle');
    altLabel.textContent = `${p.alt}`;
    svg.appendChild(altLabel);
  });

  container.innerHTML = '';
  container.appendChild(svg);
  animateLineDraw(line, container);

  // легенда природных зон
  const legend = document.createElement('div');
  legend.className = 'profile-legend';
  const seen = new Set();
  ROUTE_PROFILE.forEach((p) => {
    if (seen.has(p.zone)) return;
    seen.add(p.zone);
    const item = document.createElement('span');
    item.className = 'profile-legend__item';
    item.innerHTML = `<i style="background:${ZONE_COLORS[p.zone]}"></i>${ZONE_LABELS[p.zone]}`;
    legend.appendChild(item);
  });
  container.appendChild(legend);

  // текстовая цепочка точек (доступность + для скринридеров/SEO)
  const chain = document.createElement('p');
  chain.className = 'profile-chain sr-friendly';
  chain.textContent =
    'Бхадрапур → Илам → Секатум → Гунса → Камбачен → Лонак → Пангпема → Селе Ла → Церам → Тортонг';
  container.appendChild(chain);
}

/* ---------------------------------------------------------------------
   Аккордеоны (FAQ, полная программа по дням)
   --------------------------------------------------------------------- */
function initAccordions() {
  document.querySelectorAll('[data-accordion-trigger]').forEach((trigger) => {
    trigger.addEventListener('click', () => {
      const panelId = trigger.getAttribute('aria-controls');
      const panel = document.getElementById(panelId);
      const expanded = trigger.getAttribute('aria-expanded') === 'true';
      trigger.setAttribute('aria-expanded', String(!expanded));
      if (panel) {
        panel.hidden = expanded;
      }
    });
  });
}

/* ---------------------------------------------------------------------
   Мобильная фиксированная панель: скрывается в зоне финального CTA
   --------------------------------------------------------------------- */
function initMobileBar() {
  const bar = document.getElementById('mobile-bar');
  const finalCta = document.getElementById('final-cta');
  if (!bar || !finalCta) return;

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        bar.classList.toggle('mobile-bar--hidden', entry.isIntersecting);
      });
    },
    { threshold: 0.15 }
  );
  observer.observe(finalCta);
}

/* ---------------------------------------------------------------------
   Плавное появление блоков при скролле (уважает prefers-reduced-motion)
   --------------------------------------------------------------------- */
function initReveal() {
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const items = document.querySelectorAll('[data-reveal]');
  if (prefersReduced || !('IntersectionObserver' in window)) {
    items.forEach((el) => el.classList.add('is-visible'));
    return;
  }
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
  );
  items.forEach((el) => observer.observe(el));
}

/* ---------------------------------------------------------------------
   Аналитика: цели Яндекс.Метрики (счётчик подключается отдельно в head)
   --------------------------------------------------------------------- */
function initAnalyticsGoals() {
  const reach = (goal) => {
    if (typeof window.ym === 'function' && window.YM_COUNTER_ID) {
      window.ym(window.YM_COUNTER_ID, 'reachGoal', goal);
    }
  };

  document.querySelectorAll('[data-cta="telegram"]').forEach((el) => {
    el.addEventListener('click', () => reach('click_telegram'));
  });
  document.querySelectorAll('[data-cta="whatsapp"]').forEach((el) => {
    el.addEventListener('click', () => reach('click_whatsapp'));
  });

  const priceBlock = document.getElementById('price');
  if (priceBlock) {
    const priceObserver = new IntersectionObserver(
      (entries, obs) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            reach('scroll_to_price');
            obs.disconnect();
          }
        });
      },
      { threshold: 0.3 }
    );
    priceObserver.observe(priceBlock);
  }

  document.querySelectorAll('[data-accordion-trigger="full-program"]').forEach((el) => {
    el.addEventListener('click', () => reach('open_full_program'), { once: true });
  });
  document.querySelectorAll('[data-accordion-trigger="faq"]').forEach((el) => {
    el.addEventListener('click', () => reach('open_faq'), { once: true });
  });

  const depthMarks = { 25: false, 50: false, 75: false, 100: false };
  window.addEventListener(
    'scroll',
    () => {
      const scrolled = window.scrollY + window.innerHeight;
      const total = document.documentElement.scrollHeight;
      const pct = Math.round((scrolled / total) * 100);
      [25, 50, 75, 100].forEach((mark) => {
        if (pct >= mark && !depthMarks[mark]) {
          depthMarks[mark] = true;
          reach('scroll_depth_' + mark);
        }
      });
    },
    { passive: true }
  );
}

document.addEventListener('DOMContentLoaded', () => {
  applyConfig();
  renderAltitudeProfile();
  initAccordions();
  initMobileBar();
  initReveal();
  initAnalyticsGoals();
});
