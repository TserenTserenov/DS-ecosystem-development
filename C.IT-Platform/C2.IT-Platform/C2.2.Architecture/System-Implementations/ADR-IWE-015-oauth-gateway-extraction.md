---
id: ADR-IWE-015
title: "Вынос OAuth flows в standalone DS-oauth-gateway (CF Worker)"
status: superseded
superseded_by: ADR-IWE-016
version: 1.0
date: 2026-05-12
superseded_on: 2026-05-12
deciders: [Tseren]
context: "WP-305 Ф1 ArchGate PASS 12 мая (Вариант B vs A vs C). Через ~2h independent review (Opus subagent) обнаружил premature decomposition — пересмотрено в ADR-IWE-016 (A-lite)"
related:
  pack: [DP.SC.130, DP.ROLE.040, DP.ARCH.001]
  realized_by: [WP-305]
  blocks: [WP-304]
  uses: [ADR-IWE-008, ADR-IWE-012]
family: F8
kernel: C
system: C2
role: Architecture
---

> ⚠️ **SUPERSEDED 2026-05-12** by [ADR-IWE-016](ADR-IWE-016-oauth-gateway-modular-extension.md). Решение оставлено в архиве как опорная точка профиля ЭМОГССБ A/B/C и lessons («ArchGate без operational backing — слабый довод» — см. ADR-IWE-016 §7).

# ADR-IWE-015: Вынос OAuth flows в standalone DS-oauth-gateway

## 1. Контекст

После WP-301 (SC.020 PRODUCTION) контур доставки уроков замкнут, но **идентификация пилота жёстко завязана на Telegram-бота** через `aist_bot_newarchitecture/oauth_server.py` (Python aiohttp, 1962 LOC, Railway-local Postgres). Конкретные точки связи:

- `save_app_installation` требует `dt_tokens.chat_id` (создаётся только при онбординге в боте)
- `sync_one_user_to_dt` ищет user через `development.engagement` (заполняется bot-событиями)
- Setup endpoint подписывает state-token c `chat_id` (Web-канал не знает Telegram ID)

**Следствие:** канал C (web-кнопка на лендинге `system-school.ru/iwe`, WP-304 Ф3) технически не работает.

**Архитектурный долг:** `oauth_server.py` физически живёт в репо бота, но обслуживает **6 OAuth-потоков** (Linear, Twin, GitHub OAuth, Google Cal, WakaTime, Ory). Это платформенный сервис, не бот-специфичный.

**Параллельно:** `DS-MCP/gateway-mcp` (CF Worker, TypeScript, 3016 LOC) уже обслуживает Ory + GitHub App + webhook — но это другой Bounded Context (Knowledge access control), смешивать OAuth Identity в него = DDD violation.

## 2. Рассмотренные варианты

**ArchGate WP-305 Ф1 (12 мая 2026)** прошёл с сравнением 3 вариантов; критические характеристики (Безопасность, Эволюционируемость, Современность) выбраны пилотом.

| | A: расширить gateway-mcp | **B: новый репо DS-oauth-gateway** | C: oauth_server.py + ory-session |
|---|---|---|---|
| Эволюционируемость | ⚠️ knowledge coupling растёт | ✅ clear separation BC | ❌ legacy fix |
| Масштабируемость | ✅ | ✅ | ❌ bound к bot |
| Обучаемость | ✅ паттерн знаком | ⚠️ +1 сервис | ⚠️ stack-specific |
| Генеративность | ✅ | ✅ extension point | ⚠️ |
| Скорость | ✅ edge | ✅ edge | ⚠️ Railway single-region |
| Современность | ⚠️ DDD violation (2 BC в Worker) | ✅ DDD aligned | ❌ legacy stack |
| Безопасность | ⚠️ shared attack surface | ✅ isolated runtime | ❌ B7.3.1 violations |
| **Итог** | 3⚠️ / 4✅ / 0❌ | **1⚠️ / 6✅ / 0❌** | 3⚠️ / 0✅ / 3❌ |

**Вето-фильтр:** A и B проходят. **C НЕ проходит** (≥2 ❌ + 3 критические ❌ → правила 1 и 2 сработали).

## 3. Решение

**Принят вариант B — создание нового репозитория `DS-oauth-gateway`** как standalone CF Worker.

### 3.1. Архитектурные параметры

- **Стэк:** TypeScript, Cloudflare Workers, Hono framework
- **Domain:** `oauth.aisystant.com` (новый CF route)
- **Storage:** Neon — отдельный schema `oauth_gateway` (state_tokens, tokens encrypted-at-rest Fernet)
- **OAuth Authorization Server:** Ory Hydra (как `gateway-mcp`)
- **Identity-resolution приоритет:** Ory session > telegram_user_id > github_username
- **Reuse:** Ory JWKS verify, GitHub App install pattern — переиспользуем код из `gateway-mcp` и `personal-knowledge-mcp`

### 3.2. Endpoints (Ф2-Ф4 WP-305)

| Endpoint | Метод | Назначение |
|----------|-------|-----------|
| `/auth/github_app/setup` | GET | Старт GitHub App install. Принимает `?telegram_user_id=X` (legacy) ИЛИ ory_session cookie |
| `/auth/github_app/callback` | GET | Обработка install → запись `github_connections` |
| `/auth/{provider}/callback` | GET | Linear, Twin, Google Cal, WakaTime, Ory (Ф5, постепенная миграция) |
| `/.well-known/oauth-protected-resource` | GET | OAuth metadata |

### 3.3. Миграция (последовательность)

| Этап | Что делаем | Что не ломаем |
|------|-----------|----------------|
| **Ф2 (Ф_a)** | Каркас сервиса + endpoint `/auth/github_app/setup` с dual identity | bot's existing flow остаётся параллельно |
| **Ф3** | Endpoint `/auth/github_app/callback` + identity-mapping в `github_connections` | оба пути (Ory и telegram) работают |
| **Ф4** | Bot's `oauth_server.py:github_app_setup_handler` редиректит на oauth-gateway (proxy) | существующие пилоты не замечают |
| **Ф5 (постепенно)** | Linear, Twin, Google Cal, WakaTime, Ory — миграция по одному провайдеру | каждый по отдельному mini-РП |
| **Ф6** | Документация URL для лендинга `system-school.ru/iwe` → разблокировать WP-304 Ф3 | — |

### 3.4. Митигация ⚠️ Обучаемость

Единственное предупреждение профиля B — «+1 сервис в инвентаре». Митигации:
1. README в `DS-oauth-gateway/README.md` со ссылкой на DP.SC.130 и DP.ROLE.040 как точку входа
2. Diagram в `C2.2.Architecture/System-Implementations/oauth-gateway-architecture.md` (после Ф2)
3. Обновление `REPOSITORY-REGISTRY.md` в `0.OPS/`

## 4. Триггеры пересмотра

- **Снижение нагрузки до <100 OAuth setup/день в течение Q3 2026** → может быть выгоднее объединить с `gateway-mcp` (refactor, не разделение)
- **Регуляторное требование локализации OAuth tokens в РФ** → возможен switch на Track B инфру (см. WP-285)
- **Compromise одного из CF accounts** → отдельный CF account для oauth-gateway (currently shared с другими Workers)

## 5. Следствия

**Положительные:**
- Web-канал C разблокирован (WP-304 Ф3) — wave-2 пилот (16-17 мая) может использовать
- Bot становится тонким клиентом (Marathon-only) — приближается к WP-262
- Чистая DDD-граница: Knowledge BC (gateway-mcp) ≠ OAuth Identity BC (oauth-gateway) ≠ Marathon BC (bot)
- B2.5 token encryption-at-rest будет реализован сразу в новом сервисе (правильное место для нового долга)

**Отрицательные:**
- +1 CF Worker в инвентаре (deploy, secrets, monitoring)
- Бюджет 16h WP-305 — впритык (Ф2-Ф4 ~9h, Ф5 ~4h, Ф6 ~1h, общая обвязка ~2h)
- Bot's `oauth_server.py` остаётся как proxy в течение migration window (Ф4-Ф5) — двойной maintenance

## 6. Связи

- **DP.SC.130** — Service Clause «OAuth Gateway»
- **DP.ROLE.040** — Role «OAuth Orchestrator»
- **ADR-IWE-008** — Identity by Ory ID (universal) — мы переиспользуем
- **ADR-IWE-012** — MCP independent JWT verification — мы переиспользуем JWKS pattern
- **WP-305** — реализующий рабочий продукт
- **WP-304** — заблокирован Ф3, разблокируется после Ф6 WP-305
