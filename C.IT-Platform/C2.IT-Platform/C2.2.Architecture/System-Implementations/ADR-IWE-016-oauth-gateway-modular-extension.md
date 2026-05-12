---
id: ADR-IWE-016
title: "OAuth Gateway как модуль gateway-mcp (revision ADR-IWE-015)"
status: accepted
version: 1.0
date: 2026-05-12
deciders: [Tseren]
context: "WP-305 Ф1 revision после independent review субагента Opus (12 мая); supersedes ADR-IWE-015 в части carrier (где реализуется), сохраняет SC и Role"
supersedes: ADR-IWE-015
related:
  pack: [DP.SC.130, DP.ROLE.040, DP.ARCH.001, DP.SOTA.011]
  realized_by: [WP-305]
  blocks: [WP-304]
  uses: [ADR-IWE-008, ADR-IWE-012]
family: F8
kernel: C
system: C2
role: Architecture
---

# ADR-IWE-016: OAuth Gateway как модуль gateway-mcp

## 1. Контекст пересмотра

ADR-IWE-015 (12 мая) принял Вариант B (новый репо `DS-oauth-gateway`). Через независимый review субагента Opus в тот же день обнаружены **5 контраргументов**, заставляющих пересмотреть решение:

1. **gateway-mcp уже на 40% — OAuth.** Из 3016 LOC `src/index.ts` ~1200 LOC = handlers OAuth (`handleOAuthAuthorize`, `handleOAuthCallback`, `handleGitHubInstall`, `handleGitHubCreateRepo`, `handleGitHubRepoCallback`, `/github/webhook`, hydra-hook, JWKS verify, encryptCode/decryptCode, state-tokens). DDD-аргумент про «Knowledge BC vs OAuth Identity BC» — post-hoc rationalization структуры, которая уже composite gateway.

2. **Реальная разница BC иллюзорна.** Та же Ory JWKS, та же Neon, тот же CF runtime, тот же auth-сервер (Ory Hydra). «Отдельный BC» получает только новое имя schema. Конкретный сценарий, где coupling вредит, не назван ни в ADR-15, ни в SC.130.

3. **Бюджет 16h нереалистичен.** Ф1 = 2h. Остаток 14h должен покрыть: bootstrap CF Worker repo (DNS+route+secrets+wrangler+CI), Hono setup, port HMAC из Python в TS, dual identity-resolution, Neon migration, bot proxy, cross-system contract tests. Реалистично — **24-32h** + двойной maintenance Ф4-Ф5. Конфликт с P0 wave-2 (16-17 мая).

4. **Critical path WP-304 Ф3 не требует extraction.** Блокирует **один** endpoint `/auth/github_app/setup` с dual identity. Это можно добавить в gateway-mcp за **3-4h**. Остальные 5 OAuth (Linear/Twin/WakaTime/GCal/Ory) — Marathon-only, не блокеры web-канала.

5. **ADR-IWE-015 противоречит сам себе.** В «триггерах пересмотра» написано: «<100 setup/день в Q3 → выгоднее объединить». На 11 мая ровно так: 50 пилотов, ~10 setup/день. **Premature decomposition** по DP.SOTA.011 (Coupling Model: separation оправдано только при доказанной semantic divergence — её здесь нет).

## 2. Решение (revision)

**Принят Вариант A-lite — OAuth модуль в `gateway-mcp/src/oauth/`**, не отдельный CF Worker.

### 2.1. Архитектурные параметры

- **Carrier:** `DS-MCP/gateway-mcp/src/oauth/` (модульная подпапка, не отдельный Worker)
- **CF Worker:** тот же `gateway-mcp` Worker (один deploy, одни secrets, один monitoring channel)
- **Domain:** `oauth.aisystant.com` — **CF custom domain alias** на тот же Worker (zero infra overhead)
- **Storage:** Neon, schema `knowledge` — переиспользуем `github_installations`, расширяем `github_connections` для web-flow
- **Identity-resolution:** реиспользуем существующий Ory JWKS verify из gateway-mcp + добавляем bot's HMAC state-token verify

### 2.2. Endpoints (Ф2-Ф3 WP-305 — total ~3-4h)

| Endpoint | Метод | Назначение | Время |
|----------|-------|-----------|-------|
| `/auth/github_app/setup` | GET | Старт GitHub App install. Dual identity: `?telegram_user_id=X` (legacy HMAC state) ИЛИ Ory session cookie | ~1.5h |
| `/auth/github_app/callback` | GET | Обработка install → INSERT/UPDATE `github_connections` (web: `chat_id IS NULL`; legacy: с `chat_id`) | ~1h |
| `oauth.aisystant.com` CF custom domain | — | Alias на gateway-mcp Worker | ~15min |
| Tests | — | state-token sign/verify + dual identity + integration | ~1h |

### 2.3. Что НЕ делаем (отложено)

| Что | Почему отложено | Когда трогать |
|-----|-----------------|---------------|
| Миграция Linear / Twin / WakaTime / GCal / Ory из `oauth_server.py` | Не блокирует web-канал (Marathon-only) | Отдельный РП в Q3 при необходимости |
| Создание отдельного `DS-oauth-gateway` репо | Premature decomposition — нет semantic divergence | Триггер: >100 setup/день ИЛИ security blast radius incident |
| Schema `oauth_gateway` в Neon | Переиспользуем `knowledge.github_*` | Только если будет separate provider, конкурирующий с GitHub |
| Bot's `oauth_server.py` proxy | Не нужен — bot's `/connect_guide` просто получает новый URL | — |

## 3. Триггеры обратного пересмотра (когда trigger полный extract в B)

1. **>100 OAuth setup/день** на постоянной основе в течение 2+ недель
2. **Security incident:** компрометация gateway-mcp Worker (XSS, RCE через зависимость) — нужна изоляция secrets
3. **Migration trigger:** второй tenant OAuth (например, корпоративные клиенты с своим Ory) — требует tenant-isolated state storage
4. **LOC growth:** `gateway-mcp/src/index.ts` > 5000 LOC и явная необходимость refactor

При срабатывании — открыть новый РП «WP-NNN OAuth Gateway extraction», переиспользуя уже написанные `src/oauth/*` модули как готовый код.

## 4. Связи

- **DP.SC.130** — Service Clause остаётся неизменным (обещание не меняется)
- **DP.ROLE.040** — Role остаётся; carrier section updated: `gateway-mcp/src/oauth/` вместо отдельного Worker
- **ADR-IWE-008** — Identity by Ory ID (universal) — переиспользуем
- **ADR-IWE-012** — MCP independent JWT verification — переиспользуем JWKS pattern
- **ADR-IWE-015** — superseded by this ADR (carrier decision reversed)
- **DP.SOTA.011** Coupling Model — обоснование: keep coupling tight там, где semantic divergence не доказана

## 5. Следствия

**Положительные:**
- WP-304 Ф3 разблокирован за **3-4h** (vs 24-32h в B) — wave-2 (16-17 мая) реально успевает
- Zero infrastructure overhead: +0 CF Workers, +0 secrets stores, +0 monitoring channels
- Существующие Ory JWKS verify + GitHub App pattern переиспользуются без портирования
- Bot's `oauth_server.py` для остальных 5 OAuth остаётся неизменным — не двойной maintenance

**Отрицательные:**
- `gateway-mcp/src/index.ts` растёт на ~200-300 LOC (с 3016 до ~3300)
- Knowledge BC + OAuth Identity BC формально в одном deploy unit — DDD violation (осознанный технический долг, фиксируется как WP-NNN trigger)
- При security incident в gateway-mcp скомпрометирован shared secret namespace (mitigated reasoning: gateway-mcp уже держит GitHub App private key, и его compromise в любой схеме = catastrophic)

## 6. Митигации технического долга

1. **Modular boundaries:** все OAuth handlers строго в `src/oauth/` подпапке, не размазываются по `index.ts`
2. **Separate test suite:** `src/oauth/*.test.ts` запускается изолированно (vitest project filter)
3. **Cross-system invariant:** при добавлении endpoint писать integration test `bot's /connect_guide` ↔ `gateway-mcp /auth/github_app/setup` дают тот же row в `github_connections`
4. **Документация в `oauth/README.md`:** ссылка на DP.SC.130 + DP.ROLE.040 + триггеры extraction (раздел 3)

## 7. Lessons (для будущих ArchGate)

- **Сравнительный профиль без operational backing — слабый довод.** ADR-15 показал ⚠️ vs ✅ профиль, но не назвал ни одного сценария, где coupling реально вредит. SOTA-чеклист (Coupling Model) требует **доказанной** semantic divergence — не предполагаемой.
- **Bootstrap-tax недооценивается.** Создание нового CF Worker = ~3-4h overhead (repo, DNS, secrets, wrangler, CI, doc). При бюджете 16h это >25% бюджета на чистый infrastructure setup.
- **Independent review (cold sub-agent) ловит post-hoc rationalization.** Главный агент после 2h работы на принятом решении не видит, что новые факты противоречат старому профилю. Periodic independent review нужен на критических архитектурных решениях.
