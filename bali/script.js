'use strict';

/* =========================================================================
   Соль. Рис. Тишина. — клиентская логика.
   Все изменяемые значения приходят из bali/content.json через
   window.BALI_CONFIG (её проставляет scripts/build_bali.py).
   ========================================================================= */

var CFG = window.BALI_CONFIG || {};

function reducedMotion() {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

/* ---------------------------------------------------------------------
   Ссылки в мессенджеры с заготовленным текстом
   --------------------------------------------------------------------- */
function initContactLinks() {
  var text = encodeURIComponent(CFG.prefilledMessage || '');

  if (CFG.telegramUrl) {
    document.querySelectorAll('[data-cta="telegram"]').forEach(function (el) {
      el.setAttribute('href', CFG.telegramUrl + (text ? '?text=' + text : ''));
      el.setAttribute('rel', 'noopener');
    });
  }

  document.querySelectorAll('[data-cta="whatsapp"]').forEach(function (el) {
    if (!CFG.whatsappNumber) {
      // Контакта нет — убираем ссылку вместе с разделителем перед ней.
      var separator = el.previousSibling;
      if (separator && separator.nodeType === 3) separator.remove();
      el.remove();
      return;
    }
    el.setAttribute(
      'href',
      'https://wa.me/' + CFG.whatsappNumber + (text ? '?text=' + text : '')
    );
    el.setAttribute('rel', 'noopener');
  });
}

/* ---------------------------------------------------------------------
   Мобильное меню: полноэкранный слой, закрывается по Esc и по клику
   --------------------------------------------------------------------- */
function initNav() {
  var toggle = document.getElementById('nav-toggle');
  var panel = document.getElementById('nav-panel');
  if (!toggle || !panel) return;

  function setOpen(open) {
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Закрыть меню' : 'Открыть меню');
    panel.classList.toggle('is-open', open);
    document.body.style.overflow = open ? 'hidden' : '';
  }

  toggle.addEventListener('click', function () {
    setOpen(toggle.getAttribute('aria-expanded') !== 'true');
  });

  panel.addEventListener('click', function (event) {
    if (event.target.closest('a')) setOpen(false);
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
      setOpen(false);
      toggle.focus();
    }
  });

  // При переходе на широкий экран слой не должен оставаться открытым.
  window.matchMedia('(min-width: 901px)').addEventListener('change', function (event) {
    if (event.matches) setOpen(false);
  });
}

/* ---------------------------------------------------------------------
   Аккордеоны программы и вопросов.
   В разметке панели открыты — без JS страница остаётся читаемой.
   Здесь мы их сворачиваем и включаем управление.
   --------------------------------------------------------------------- */
function initAccordion(selector, keepOpenIndex) {
  var triggers = Array.prototype.slice.call(document.querySelectorAll(selector));

  triggers.forEach(function (trigger, index) {
    var panel = document.getElementById(trigger.getAttribute('aria-controls'));
    if (!panel) return;

    var open = index === keepOpenIndex;
    trigger.setAttribute('aria-expanded', String(open));
    panel.hidden = !open;

    trigger.addEventListener('click', function () {
      var expanded = trigger.getAttribute('aria-expanded') === 'true';
      trigger.setAttribute('aria-expanded', String(!expanded));
      panel.hidden = expanded;
    });
  });

  return triggers;
}

function initProgram() {
  // Все дни свёрнуты; сама программа спрятана под одну кнопку.
  // Без JS разметка остаётся раскрытой — программа читается целиком.
  initAccordion('[data-day-trigger]', -1);
  var button = document.querySelector('[data-program-toggle]');
  if (!button) return;
  var box = document.getElementById(button.getAttribute('aria-controls'));
  var text = button.querySelector('.prog__toggle-text');
  if (!box) return;

  function set(open) {
    button.setAttribute('aria-expanded', String(open));
    box.hidden = !open;
    if (text) text.textContent = open ? 'Свернуть программу' : 'Открыть программу · 11 дней';
  }
  set(false);
  button.addEventListener('click', function () {
    var open = button.getAttribute('aria-expanded') !== 'true';
    set(open);
    reach(open ? 'program_open' : 'program_close');
  });
}

/* ---------------------------------------------------------------------
   Шапка: тонкая линия появляется при прокрутке
   --------------------------------------------------------------------- */
function initHeader() {
  var header = document.getElementById('site-header');
  if (!header) return;
  var onScroll = function () {
    header.classList.toggle('is-scrolled', window.scrollY > 24);
  };
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
}

/* ---------------------------------------------------------------------
   Мобильная панель: прячется на первом экране и в зоне формы,
   чтобы не перекрывать поля ввода
   --------------------------------------------------------------------- */
function initMobileBar() {
  var bar = document.getElementById('mobile-bar');
  var hero = document.getElementById('top');
  var request = document.getElementById('request');
  if (!bar || !hero || !request) return;

  var state = { hero: true, request: false };

  function sync() {
    bar.classList.toggle('mobile-bar--hidden', state.hero || state.request);
  }

  function watch(element, key) {
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          state[key] = entry.isIntersecting;
          sync();
        });
      },
      { threshold: 0.12 }
    );
    observer.observe(element);
  }

  watch(hero, 'hero');
  watch(request, 'request');
  sync();
}

/* ---------------------------------------------------------------------
   Появление блоков при прокрутке
   --------------------------------------------------------------------- */
function initReveal() {
  var items = document.querySelectorAll('[data-reveal]');
  if (!items.length) return;

  if (reducedMotion() || !('IntersectionObserver' in window)) {
    items.forEach(function (el) {
      el.classList.add('is-visible');
    });
    return;
  }

  var observer = new IntersectionObserver(
    function (entries, obs) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          obs.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.12, rootMargin: '0px 0px -8% 0px' }
  );

  items.forEach(function (el) {
    observer.observe(el);
  });
}

/* ---------------------------------------------------------------------
   Аналитика: цели Яндекс.Метрики. Счётчик подключается отдельно,
   идентификатор задаётся в content.json → config.analytics.ymCounterId.
   --------------------------------------------------------------------- */
function reach(goal) {
  if (typeof window.ym === 'function' && CFG.ymCounterId) {
    window.ym(CFG.ymCounterId, 'reachGoal', goal);
  }
}

function initAnalytics() {
  document.querySelectorAll('[data-goal]').forEach(function (el) {
    el.addEventListener('click', function () {
      reach(el.getAttribute('data-goal'));
    });
  });

  document.querySelectorAll('[data-cta="telegram"]').forEach(function (el) {
    el.addEventListener('click', function () {
      reach('telegram_click');
    });
  });
  document.querySelectorAll('[data-cta="whatsapp"]').forEach(function (el) {
    el.addEventListener('click', function () {
      reach('whatsapp_click');
    });
  });

  document.querySelectorAll('[data-day-trigger]').forEach(function (el) {
    el.addEventListener('click', function () {
      reach('program_day_open');
    }, { once: true });
  });
  document.querySelectorAll('[data-faq-trigger]').forEach(function (el) {
    el.addEventListener('click', function () {
      reach('faq_open');
    }, { once: true });
  });

  var form = document.getElementById('request-form');
  if (form) {
    var started = false;
    form.addEventListener('input', function () {
      if (!started) {
        started = true;
        reach('form_start');
      }
    });
  }

  var marks = { 25: false, 50: false, 75: false, 100: false };
  window.addEventListener(
    'scroll',
    function () {
      var total = document.documentElement.scrollHeight - window.innerHeight;
      if (total <= 0) return;
      var pct = Math.round((window.scrollY / total) * 100);
      [25, 50, 75, 100].forEach(function (mark) {
        if (pct >= mark && !marks[mark]) {
          marks[mark] = true;
          reach('scroll_' + mark);
        }
      });
    },
    { passive: true }
  );
}

/* ---------------------------------------------------------------------
   Форма заявки.
   Основной канал — endpoint из content.json (config.formEndpoint).
   Пока он не задан, данные уходят резервным путём: заготовленным
   сообщением в Telegram, а на странице показывается состояние успеха
   с прямыми контактами.
   --------------------------------------------------------------------- */
var ERRORS = {
  name: 'Напишите, как к вам обращаться',
  contact: 'Нужен телефон или ник в Telegram — иначе мы не ответим',
  email: 'Проверьте адрес: похоже, в нём опечатка',
  consent: 'Без согласия мы не сможем обработать заявку',
};

function showFieldError(form, field, message) {
  var holder = form.querySelector('[data-error-for="' + field + '"]');
  var input = form.elements[field];
  if (holder) {
    holder.textContent = message || '';
    holder.hidden = !message;
  }
  if (input) {
    if (message) {
      input.setAttribute('aria-invalid', 'true');
    } else {
      input.removeAttribute('aria-invalid');
    }
  }
}

function validate(form) {
  var problems = [];

  ['name', 'contact', 'email', 'consent'].forEach(function (field) {
    showFieldError(form, field, '');
  });

  if (!form.elements.name.value.trim()) problems.push('name');
  if (!form.elements.contact.value.trim()) problems.push('contact');

  var email = form.elements.email.value.trim();
  if (email && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) problems.push('email');

  if (!form.elements.consent.checked) problems.push('consent');

  problems.forEach(function (field) {
    showFieldError(form, field, ERRORS[field]);
  });

  return problems;
}

function collect(form) {
  var data = new FormData(form);
  return {
    name: (data.get('name') || '').trim(),
    contact: (data.get('contact') || '').trim(),
    email: (data.get('email') || '').trim(),
    channel: data.get('channel') || '',
    people: data.get('people') || '1',
    rooming: data.get('rooming') || '',
    comment: (data.get('comment') || '').trim(),
    page: 'Соль. Рис. Тишина. — Бали, 12–22 февраля 2027',
    source: window.location.href,
  };
}

function asMessage(payload) {
  var lines = [
    'Заявка с сайта: Соль. Рис. Тишина. (Бали, 12–22 февраля 2027)',
    'Имя: ' + payload.name,
    'Связь: ' + payload.contact,
    'Канал: ' + payload.channel,
    'Человек: ' + payload.people,
    'Размещение: ' + payload.rooming,
  ];
  if (payload.email) lines.push('Email: ' + payload.email);
  if (payload.comment) lines.push('Комментарий: ' + payload.comment);
  return lines.join('\n');
}

function initForm() {
  var form = document.getElementById('request-form');
  var success = document.getElementById('form-success');
  var failure = document.getElementById('form-error');
  if (!form) return;

  form.addEventListener('submit', function (event) {
    event.preventDefault();

    // Ловушка для ботов: люди это поле не видят и не заполняют.
    if (form.elements.company && form.elements.company.value) return;

    var problems = validate(form);
    if (problems.length) {
      var first = form.elements[problems[0]];
      if (first && first.focus) first.focus();
      return;
    }

    var payload = collect(form);
    var button = form.querySelector('button[type="submit"]');
    var label = button ? button.textContent : '';

    function done() {
      form.hidden = true;
      if (failure) failure.hidden = true;
      if (success) {
        success.hidden = false;
        success.setAttribute('tabindex', '-1');
        success.focus();
      }
      reach('form_success');
    }

    function fallback() {
      // Резервная доставка: заготовленное сообщение в Telegram.
      if (CFG.telegramUrl) {
        window.open(
          CFG.telegramUrl + '?text=' + encodeURIComponent(asMessage(payload)),
          '_blank',
          'noopener'
        );
        done();
        return;
      }
      if (failure) {
        failure.hidden = false;
        failure.setAttribute('tabindex', '-1');
        failure.focus();
      }
      reach('form_error');
    }

    if (!CFG.formEndpoint) {
      fallback();
      return;
    }

    if (button) {
      button.disabled = true;
      button.textContent = 'Отправляем…';
    }

    fetch(CFG.formEndpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify(payload),
    })
      .then(function (response) {
        if (!response.ok) throw new Error('HTTP ' + response.status);
        done();
      })
      .catch(function () {
        fallback();
      })
      .finally(function () {
        if (button) {
          button.disabled = false;
          button.textContent = label;
        }
      });
  });

  // Ошибка убирается сразу, как только человек начал править поле.
  ['name', 'contact', 'email'].forEach(function (field) {
    var input = form.elements[field];
    if (input) {
      input.addEventListener('input', function () {
        showFieldError(form, field, '');
      });
    }
  });
  if (form.elements.consent) {
    form.elements.consent.addEventListener('change', function () {
      showFieldError(form, 'consent', '');
    });
  }
}

/* ---------------------------------------------------------------------
   Лента «Бали в кадрах»: сама медленно плывёт, но её можно листать —
   стрелками, свайпом, колесом/тачпадом, перетаскиванием мышью и
   клавишами. После ручного листания автодвижение ждёт несколько секунд.
   Кадры в разметке продублированы, поэтому лента бесконечная.
   --------------------------------------------------------------------- */
function initStrip() {
  var vp = document.querySelector('[data-strip]');
  if (!vp) return;
  var track = vp.querySelector('.strip__track');
  var prev = document.querySelector('[data-strip-prev]');
  var next = document.querySelector('[data-strip-next]');
  var still = reducedMotion();
  var pos = 0;
  var hold = 0;        // до какого времени автодвижение на паузе
  var hover = false;
  var visible = true;
  var SPEED = 0.45;    // px за кадр, около 27 px/с

  function half() { return still ? Infinity : track.scrollWidth / 2; }
  function pause(ms) { hold = Date.now() + ms; }
  function wrap() {
    var h = half();
    if (vp.scrollLeft >= h) vp.scrollLeft -= h;
    else if (vp.scrollLeft <= 0 && h !== Infinity) vp.scrollLeft += h;
    pos = vp.scrollLeft;
  }

  function step() {
    var item = track.firstElementChild;
    return item ? item.getBoundingClientRect().width + 16 : 320;
  }
  function go(dir) {
    pause(6000);
    var dist = step() * (window.innerWidth < 700 ? 1 : 2);
    if (!still) {
      // Перед шагом переносимся на такую же точку второй копии ленты,
      // чтобы у края было куда листать
      var h = half();
      if (dir < 0 && vp.scrollLeft < dist) vp.scrollLeft += h;
      if (dir > 0 && vp.scrollLeft + dist > h * 2 - vp.clientWidth) vp.scrollLeft -= h;
    }
    vp.scrollBy({ left: dir * dist, behavior: still ? 'auto' : 'smooth' });
  }
  if (prev) prev.addEventListener('click', function () { go(-1); reach('strip_prev'); });
  if (next) next.addEventListener('click', function () { go(1); reach('strip_next'); });

  // Любое ручное касание — пауза автодвижения
  ['wheel', 'touchstart', 'keydown'].forEach(function (type) {
    vp.addEventListener(type, function () { pause(5000); }, { passive: true });
  });
  vp.addEventListener('pointerenter', function (e) { if (e.pointerType === 'mouse') hover = true; });
  vp.addEventListener('pointerleave', function (e) { if (e.pointerType === 'mouse') { hover = false; pause(800); } });
  // Ручная прокрутка у самого края: незаметно переносимся на ту же
  // точку другой копии ленты, чтобы листать можно было бесконечно
  vp.addEventListener('scroll', function () {
    if (still || Date.now() > hold) return;
    var h = half();
    if (vp.scrollLeft > h * 2 - vp.clientWidth - 4) vp.scrollLeft -= h;
    else if (vp.scrollLeft < 4) vp.scrollLeft += h;
  }, { passive: true });

  // Перетаскивание мышью (на телефоне работает родной свайп)
  var drag = null;
  vp.addEventListener('pointerdown', function (e) {
    if (e.pointerType !== 'mouse') return;
    drag = { x: e.clientX, left: vp.scrollLeft };
    vp.style.cursor = 'grabbing';
    pause(5000);
  });
  window.addEventListener('pointermove', function (e) {
    if (!drag) return;
    vp.scrollLeft = drag.left - (e.clientX - drag.x);
    pause(5000);
  });
  window.addEventListener('pointerup', function () {
    if (!drag) return;
    drag = null;
    vp.style.cursor = '';
    wrap();
  });
  track.addEventListener('dragstart', function (e) { e.preventDefault(); });

  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (entries) { visible = entries[0].isIntersecting; }).observe(vp);
  }

  if (still) return;
  function frame() {
    if (visible && !hover && !drag && Date.now() > hold) {
      if (Math.abs(vp.scrollLeft - pos) > 2) pos = vp.scrollLeft; // человек листал — продолжаем с его места
      pos += SPEED;
      var h = half();
      if (pos >= h) pos -= h;
      vp.scrollLeft = pos;
    }
    window.requestAnimationFrame(frame);
  }
  window.requestAnimationFrame(frame);
}

document.addEventListener('DOMContentLoaded', function () {
  initContactLinks();
  initNav();
  initProgram();
  initAccordion('[data-faq-trigger]', -1);
  initHeader();
  initMobileBar();
  initReveal();
  initStrip();
  initForm();
  initAnalytics();
});
