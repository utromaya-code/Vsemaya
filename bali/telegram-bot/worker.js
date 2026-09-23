/**
 * Приёмник заявок лендинга «Соль. Рис. Тишина.» → Telegram.
 *
 * Cloudflare Worker: сайт отправляет заявку сюда (config.formEndpoint
 * в content.json), воркер пересылает её ботом в личку организатору.
 * Токен бота хранится в секретах воркера и на сайт не попадает.
 *
 * Переменные окружения (Settings → Variables):
 *   BOT_TOKEN       — секрет, токен от @BotFather
 *   CHAT_ID         — ваш chat id (узнать: написать боту /start, затем
 *                     открыть https://api.telegram.org/bot<TOKEN>/getUpdates)
 *   ALLOWED_ORIGIN  — адрес сайта, например https://bali.vsemaya.ru
 *                     (через запятую, если адресов несколько)
 */

const LIMIT = 1500; // максимальная длина одного поля

function cors(origin, allowed) {
  const ok = allowed.split(',').map((s) => s.trim()).includes(origin);
  return {
    'Access-Control-Allow-Origin': ok ? origin : allowed.split(',')[0].trim(),
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    Vary: 'Origin',
  };
}

function clean(value) {
  return String(value ?? '').replace(/[<>]/g, '').trim().slice(0, LIMIT);
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || '';
    const headers = cors(origin, env.ALLOWED_ORIGIN || '*');

    if (request.method === 'OPTIONS') return new Response(null, { status: 204, headers });
    if (request.method !== 'POST') return new Response('Method not allowed', { status: 405, headers });

    let data;
    try {
      data = await request.json();
    } catch {
      return Response.json({ ok: false, error: 'bad json' }, { status: 400, headers });
    }

    // Ловушка для ботов и минимальная проверка
    if (data.company) return Response.json({ ok: true }, { headers });
    const name = clean(data.name);
    const contact = clean(data.contact);
    if (!name || !contact) return Response.json({ ok: false, error: 'required' }, { status: 422, headers });

    const lines = [
      '🌴 Заявка: Соль. Рис. Тишина. — Бали, 12–22 февраля 2027',
      '',
      `Имя: ${name}`,
      `Связь: ${contact}`,
      `Канал: ${clean(data.channel)}`,
      `Человек: ${clean(data.people)}`,
      `Размещение: ${clean(data.rooming)}`,
    ];
    if (data.email) lines.push(`Email: ${clean(data.email)}`);
    if (data.comment) lines.push('', `Комментарий: ${clean(data.comment)}`);
    if (data.source) lines.push('', `Страница: ${clean(data.source)}`);

    const tg = await fetch(`https://api.telegram.org/bot${env.BOT_TOKEN}/sendMessage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: env.CHAT_ID, text: lines.join('\n'), disable_web_page_preview: true }),
    });

    if (!tg.ok) return Response.json({ ok: false, error: 'telegram' }, { status: 502, headers });
    return Response.json({ ok: true }, { headers });
  },
};
