---
type: incident
status: open
created: 2026-09-01
trigger: perceived-breach
---

# Секреты /etc/iwe/env засвечены в выводе инструмента агента (tsekh-1)

**Что:** во время диагностики (пир-сессия с Кодексом, разбор отсутствующего Telegram-алерта на tsekh-1) агент выполнил `sudo cat /etc/iwe/env` вместо точечного запроса нужной строки — вывел содержимое файла целиком через SSH. Пост-обработка (secret output guard) заредактировала 25 значений в отображённом тексте, но сам файл был прочитан агентом полностью до редактирования.

**Когда:** 2026-09-01, ~06:20 UTC (в ходе пир-сессии `2026-09-01-08-night-cycle-ne-zakryvaet-semafor`).

**Канал:** вывод инструмента Bash (SSH-сессия к tsekh-1) внутри агентского чата Claude Code.

**Затронутые секреты (класс, без значений):** `ANTHROPIC_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`/`TELEGRAM_TEAM_CHAT_ID` (не секрет сам по себе, но рядом), 7× `NEON_*_URL` (indicators/learning/persona/subscription/directus/aist-bot/rewards + `PANEL_DATABASE_URL`/`AISYSTANT_PG_URL`/`DATABASE_URL_STAGE_EVALUATOR`), `GITHUB_APP_PRIVATE_KEY`, `GITHUB_TOKEN_ENCRYPTION_KEY`, `INTERNAL_NOTIFY_SECRET`, `PROXY_SHARED_SECRET`, `OPENROUTER_API_KEY`, `WP455_BITCOIN_RPC_URL` (embedded basic-auth credentials) — практически весь файл `/etc/iwe/env` на tsekh-1 (~25 значений).

**Time-to-detect:** мгновенно — secret output guard перехватил и заредактировал вывод в этом же ходу, дал явное указание считать оригиналы засвеченными.

**Что дальше:** полный cascade rotation по `DP.RUNBOOK.003` не запущен агентом самостоятельно — объём (production-бот, БД, платёжный/биткоин RPC ключ) требует решения пилота о приоритизации и окне (§2.4 таблица blast radius runbook'а). Пилот уведомлён в чате сразу после обнаружения.
