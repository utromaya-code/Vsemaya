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
  tea: '#8ba876',
  rhodo: '#c65a6c',
  conifer: '#6f8a70',
  moraine: '#9aa5b0',
  pass: '#8fa3c4',
  forest: '#7a9a7c',
  lowland: '#d97706',
};

function prefersReducedMotion() {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

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
   Высотный профиль: Chart.js график с тултипами и природными зонами
   --------------------------------------------------------------------- */
function renderAltitudeChart() {
  const container = document.getElementById('altitude-profile');
  if (!container || typeof Chart === 'undefined') return;

  const canvas = document.createElement('canvas');
  canvas.setAttribute('role', 'img');
  canvas.setAttribute(
    'aria-label',
    'Высотный профиль маршрута от Бхадрапура (91 м) до северного базового лагеря Канченджанги, Пангпема (5143 м), и обратно'
  );
  canvas.height = 320;
  container.innerHTML = '';
  container.appendChild(canvas);

  const n = ROUTE_PROFILE.length;
  const labels = ROUTE_PROFILE.map((p) => 'Д' + p.day);
  const altData = ROUTE_PROFILE.map((p) => p.alt);
  const peakData = ROUTE_PROFILE.map((p) => p.peakAlt || null);
  const pointColors = ROUTE_PROFILE.map((p) => (p.accl ? '#c65a6c' : '#cbd3dc'));
  const pointRadii = ROUTE_PROFILE.map((p) => (p.accl ? 6 : 4));
  const peakRadii = ROUTE_PROFILE.map((p) => (p.peakAlt ? (p.isMax ? 7 : 5) : 0));
  const peakColors = ROUTE_PROFILE.map((p) => (p.isMax ? '#c65a6c' : '#d97706'));

  const zoneBandsPlugin = {
    id: 'zoneBands',
    beforeDraw(chart) {
      const { ctx, chartArea, scales } = chart;
      if (!chartArea) return;
      const xScale = scales.x;
      ctx.save();
      let zoneStart = 0;
      for (let i = 1; i <= n; i++) {
        const changed = i === n || ROUTE_PROFILE[i].zone !== ROUTE_PROFILE[zoneStart].zone;
        if (changed) {
          const x0 = zoneStart === 0 ? chartArea.left : (xScale.getPixelForValue(zoneStart - 1) + xScale.getPixelForValue(zoneStart)) / 2;
          const x1 = i === n ? chartArea.right : (xScale.getPixelForValue(i - 1) + xScale.getPixelForValue(i)) / 2;
          ctx.fillStyle = ZONE_COLORS[ROUTE_PROFILE[zoneStart].zone];
          ctx.globalAlpha = 0.14;
          ctx.fillRect(x0, chartArea.top, x1 - x0, chartArea.bottom - chartArea.top);
          zoneStart = i;
        }
      }
      ctx.restore();
    },
  };

  // eslint-disable-next-line no-undef
  new Chart(canvas.getContext('2d'), {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'Высота ночёвки',
          data: altData,
          borderColor: '#d97706',
          backgroundColor: 'rgba(217, 119, 6, 0.12)',
          fill: true,
          tension: 0.3,
          pointBackgroundColor: pointColors,
          pointBorderColor: '#fff',
          pointBorderWidth: 1,
          pointRadius: pointRadii,
          pointHoverRadius: 7,
          borderWidth: 2.5,
        },
        {
          label: 'Высшая точка дня',
          data: peakData,
          borderColor: 'transparent',
          showLine: false,
          pointRadius: peakRadii,
          pointHoverRadius: peakRadii.map((r) => r + 2),
          pointBackgroundColor: peakColors,
          pointBorderColor: '#fff',
          pointBorderWidth: 1,
        },
      ],
    },
    plugins: [zoneBandsPlugin],
    options: {
      responsive: true,
      animation: prefersReducedMotion() ? false : { duration: 1100, easing: 'easeOutCubic' },
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#0f172a',
          titleFont: { family: 'Inter', weight: '600' },
          bodyFont: { family: 'Inter' },
          padding: 12,
          cornerRadius: 8,
          filter: (item) => item.raw !== null && item.raw !== undefined,
          callbacks: {
            title(items) {
              const i = items[0].dataIndex;
              const p = ROUTE_PROFILE[i];
              return `День ${p.day} · ${p.date}: ${p.place}`;
            },
            label(item) {
              const i = item.dataIndex;
              const p = ROUTE_PROFILE[i];
              if (item.datasetIndex === 1 && p.peakAlt) {
                return `${p.peakLabel}: ${p.peakAlt} м`;
              }
              return `${p.alt} м · ${p.hours}`;
            },
          },
        },
      },
      scales: {
        y: {
          suggestedMin: 0,
          suggestedMax: 5400,
          ticks: { callback: (v) => v + ' м', color: '#93a0b0', font: { family: 'Inter', size: 11 } },
          grid: { color: 'rgba(255,255,255,0.08)' },
        },
        x: {
          ticks: { color: '#93a0b0', font: { family: 'Inter', size: 11 } },
          grid: { display: false },
        },
      },
    },
  });

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
   Аккордеоны (FAQ, общий тумблер полной программы)
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
   Аккордеон «Маршрут по дням»: каждая карточка раскрывается независимо
   --------------------------------------------------------------------- */
function initDayAccordion() {
  document.querySelectorAll('.day-card__trigger').forEach((trigger) => {
    const panel = document.getElementById(trigger.getAttribute('aria-controls'));
    if (!panel) return;
    trigger.addEventListener('click', () => {
      const expanded = trigger.getAttribute('aria-expanded') === 'true';
      trigger.setAttribute('aria-expanded', String(!expanded));
      panel.style.maxHeight = expanded ? '0px' : panel.scrollHeight + 'px';
    });
  });
}

/* ---------------------------------------------------------------------
   Мобильная фиксированная панель: скрывается в зоне финального CTA
   --------------------------------------------------------------------- */
function initMobileBar() {
  const bar = document.getElementById('mobile-bar');
  const hero = document.getElementById('hero');
  const finalCta = document.getElementById('final-cta');
  if (!bar || !hero || !finalCta) return;

  const state = { hero: true, finalCta: false };
  const sync = () => {
    bar.classList.toggle('mobile-bar--hidden', state.hero || state.finalCta);
  };

  const heroObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        state.hero = entry.isIntersecting;
        sync();
      });
    },
    { threshold: 0.15 }
  );
  heroObserver.observe(hero);

  const finalCtaObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        state.finalCta = entry.isIntersecting;
        sync();
      });
    },
    { threshold: 0.15 }
  );
  finalCtaObserver.observe(finalCta);
}

/* ---------------------------------------------------------------------
   Glass-навбар: фон плотнее при скролле
   --------------------------------------------------------------------- */
function initHeader() {
  const header = document.getElementById('site-header');
  if (!header) return;
  const onScroll = () => {
    header.classList.toggle('is-scrolled', window.scrollY > 40);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
}

/* ---------------------------------------------------------------------
   Лёгкий параллакс на крупных фото гор (уважает prefers-reduced-motion)
   --------------------------------------------------------------------- */
function initParallax() {
  if (prefersReducedMotion()) return;
  const items = Array.from(document.querySelectorAll('[data-parallax]'));
  if (!items.length) return;

  let ticking = false;
  const update = () => {
    const viewportH = window.innerHeight;
    items.forEach((el) => {
      const rect = el.getBoundingClientRect();
      if (rect.bottom < 0 || rect.top > viewportH) return;
      const speed = parseFloat(el.getAttribute('data-parallax-speed')) || 0.15;
      const offset = (rect.top - viewportH / 2) * speed * -0.3;
      el.style.transform = `translateY(${offset}px) scale(1.1)`;
    });
    ticking = false;
  };
  window.addEventListener(
    'scroll',
    () => {
      if (!ticking) {
        window.requestAnimationFrame(update);
        ticking = true;
      }
    },
    { passive: true }
  );
  update();
}

/* ---------------------------------------------------------------------
   Swiper: «Пять сокровищ этого пути»
   --------------------------------------------------------------------- */
function initTreasuresSwiper() {
  const el = document.querySelector('.treasures-swiper');
  if (!el || typeof Swiper === 'undefined') return;
  // eslint-disable-next-line no-undef
  new Swiper('.treasures-swiper', {
    slidesPerView: 1.15,
    spaceBetween: 16,
    pagination: { el: '.swiper-pagination', clickable: true },
    navigation: { nextEl: '.swiper-button-next', prevEl: '.swiper-button-prev' },
    a11y: { enabled: true },
    keyboard: { enabled: true },
    breakpoints: {
      640: { slidesPerView: 2.2 },
      1000: { slidesPerView: 3.2 },
    },
  });
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
    el.addEventListener('click', () => {
      reach('telegram_click');
      const zone = el.getAttribute('data-cta-zone');
      if (zone) reach(zone);
    });
  });
  document.querySelectorAll('[data-cta="whatsapp"]').forEach((el) => {
    el.addEventListener('click', () => reach('whatsapp_click'));
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
    el.addEventListener('click', () => reach('itinerary_open'), { once: true });
  });
  document.querySelectorAll('.day-card__trigger').forEach((el) => {
    el.addEventListener('click', () => reach('itinerary_day_open'), { once: true });
  });
  document.querySelectorAll('[data-accordion-trigger="faq"]').forEach((el) => {
    el.addEventListener('click', () => reach('faq_open'), { once: true });
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
  renderAltitudeChart();
  initAccordions();
  initDayAccordion();
  initMobileBar();
  initHeader();
  initParallax();
  initTreasuresSwiper();
  initAnalyticsGoals();

  if (typeof AOS !== 'undefined') {
    AOS.init({
      duration: 800,
      once: true,
      disable: prefersReducedMotion() ? true : false,
    });
  }
});
