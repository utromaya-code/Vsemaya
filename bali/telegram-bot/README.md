# Заявки с сайта → Telegram

Форма на лендинге отправляет заявку POST-запросом на `config.formEndpoint`
из `bali/content.json`. Этот адрес — маленький воркер (`worker.js`), который
пересылает заявку ботом вам в личку. Токен бота живёт в секретах воркера,
на сайте его нет.

Пока `formEndpoint` пустой, форма работает запасным путём: открывает ваш
Telegram (`config.telegramUrl`) с уже заполненным текстом заявки — человеку
остаётся нажать «Отправить».

## Настройка (10 минут, бесплатно)

1. **Бот.** В Telegram откройте @BotFather → `/newbot` → придумайте имя.
   Сохраните токен вида `123456:ABC…`.
2. **Ваш chat id.** Напишите своему боту `/start`. Откройте в браузере
   `https://api.telegram.org/bot<ТОКЕН>/getUpdates` и найдите
   `"chat":{"id": 123456789` — это число и есть chat id.
3. **Воркер.** dash.cloudflare.com → Workers & Pages → Create → Worker →
   вставьте содержимое `worker.js` → Deploy.
4. **Переменные.** В воркере: Settings → Variables and Secrets:
   - `BOT_TOKEN` — тип Secret, токен из шага 1;
   - `CHAT_ID` — chat id из шага 2;
   - `ALLOWED_ORIGIN` — адрес сайта, например `https://bali.vsemaya.ru`.
5. **Сайт.** Адрес воркера (`https://….workers.dev`) впишите в
   `config.formEndpoint` в `bali/content.json` и пересоберите страницу:
   `python3 scripts/build_bali.py`.

Проверка: отправьте тестовую заявку — сообщение придёт от бота за секунду.
Если воркер недоступен, форма сама откроет Telegram с текстом заявки.
