---
type: incident
date: 2026-08-31
status: open
severity: high
class: perceived-breach
runbook: DP.RUNBOOK.003
---

# Инцидент: утечка переменных окружения прод-бота в чат

**Что просочилось:** полный список переменных окружения сервиса `aist_me_bot` (Railway, проект peaceful-vision, environment production) — запрошен через `mcp__railway__list-variables` без фильтра по одному имени. Автоматический guard распознал и отредактировал 27 значений по известным паттернам (Anthropic/OpenAI ключи, GitHub-токены, строки подключения к БД, Telegram bot token), но **остальные значения (десятки переменных) остались в чате незамаскированными** — включая `RAILWAY_API_TOKEN`, `ORY_CLIENT_SECRET`, `DISCOURSE_API_KEY`, `DISCOURSE_WEBHOOK_SECRET`, `GITHUB_CLIENT_SECRET`, `GOOGLE_CALENDAR_CLIENT_SECRET`, `LANGFUSE_SECRET_KEY`, `LINEAR_CLIENT_SECRET`, `PROXY_SHARED_SECRET`, `EVENT_GATEWAY_HMAC_KEY`, `WAKATIME_CLIENT_SECRET`, `YOOKASSA_PROVIDER_TOKEN`, `INTERNAL_NOTIFY_SECRET`, `INTROSPECT_SECRET`, `GATEWAY_ONBOARDING_READ_SECRET`, `EXTERNAL_AUTH_KEY`, `TEMPLATE_WEBHOOK_SECRET`, `WORKSHOP_WEBHOOK_SECRET`, `CHECKLIST_MCP_SERVICE_TOKEN_NUDGE`, `CHECKLIST_MCP_SERVICE_TOKEN_ONBOARDER`, `CHATWOOT_INBOX_IDENTIFIER`, `AISYSTANT_TECH_PASSWORD`, `GITHUB_TOKEN_ENCRYPTION_KEY`, `GITHUB_WORKBOOK_WEBHOOK_SECRET`, `WAKASTIME_CLIENT_ID`/`WAKATIME_API_KEY` и другие — практически весь секретный периметр прод-бота одним запросом.

**Канал утечки:** чат агента (Claude Code сессия, инструмент Railway MCP).

**Time-to-detect:** немедленно — сработал автоматический guard на вывод инструмента, но он покрыл только 27 из ~40+ секретных значений в ответе.

**Time-to-rotate:** не начата — инцидент зафиксирован, ротация ждёт решения пилота (объём — весь прод-периметр, high-cascade секреты вроде `DATABASE_URL`-класса требуют координации, часть НЕ была затронута в этом конкретном дампе — сам `DATABASE_URL`/`ANTHROPIC_API_KEY`/`TELEGRAM_BOT_TOKEN` guard замаскировал).

**Затронутые точки:** 1 Railway-сервис (`aist_me_bot`, production) — точное число cascade-точек по каждому секрету не оценивалось в рамках этой записи, требует прогона §2.2 самого runbook по каждому незамаскированному имени.

**Что предотвратило бы повтор:** запрашивать переменные Railway поимённо (`--variable-names` / grep по одному имени), не полным листингом; вывод MCP-инструментов, возвращающих секретные значения, должен маскировать по умолчанию весь ответ, а не только паттерн-совпадения — текущий guard пропускает произвольные hex/base64-строки без опознаваемого префикса.
