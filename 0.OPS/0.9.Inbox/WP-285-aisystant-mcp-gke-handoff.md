# WP-285 — Передача Aisystant MCP в GKE

> Документ handoff для Андрея Смирнова (архитектор / Track B).
> Актуально на 2026-06-09 (после верификации WP-402 Р8+Р9, peer-сессия 2026-06-09-07). Все репозитории приватные (`aisystant/*`).
>
> **Статус одной строкой:** вынос кода Р1-Р9 закрыт и в проде (gateway авто-деплоится при push в main). Сервисы НЕ развёрнуты → `mcp.aisystant.com/health` сейчас отдаёт **503** (`missing: USER_PROFILE_SERVICE_URL, LEARNING_CONTEXT_SERVICE_URL`). Главная работа Андрея — развернуть 5 сервисов в GKE и подключить их к gateway (раздел 3).

<details open>
<summary><b>1. Карта сервисов за Aisystant MCP</b></summary>

> **Важно про терминологию.** «Aisystant MCP» = это **шлюз** (`gateway-mcp`, `mcp.aisystant.com`) — единственная точка, к которой подключаются внешние клиенты (claude.ai, Claude Code, VS Code). За ним стоят два РАЗНЫХ класса сервисов: исходные backend-MCP (серверы знаний) и вынесенные из шлюза вспомогательные сервисы (WP-402). Пять новых сервисов — это НЕ замена трёх MCP, а вынесенная наружу прикладная логика самого шлюза.

**A. Шлюз (Aisystant MCP)**

| Сервис | Репозиторий | Платформа | Статус |
|--------|-------------|-----------|--------|
| **gateway-mcp** | https://github.com/aisystant/gateway-mcp | Cloudflare Worker | **Задеплоен** (авто-деплой при push в main); `/health` = 503 пока 5 сервисов группы C не подключены |

**B. Backend-MCP — серверы знаний за шлюзом (мигрируют в GKE вместе со шлюзом)**

Шлюз делает fan-out (раздачу запросов) к ним: поиск, цифровой двойник, личные знания. Логика WP-402 их не меняла, но в Track B они тоже переезжают в GKE. Это «3 URL» из теста Андрея.

| Сервис | Репозиторий | Платформа (цель) | Что делает | Dockerfile |
|--------|-------------|------------------|------------|------------|
| **knowledge-mcp** | https://github.com/aisystant/knowledge-mcp | GKE Standard europe-west4 | Поиск по базе знаний (Pack, гайды) | ❌ Нет (сейчас CF Worker) |
| **digital-twin-mcp** | https://github.com/aisystant/digital-twin-mcp | GKE Standard europe-west4 | Цифровой двойник пилота | ❌ Нет (сейчас CF Worker) |
| **personal-knowledge-mcp** | https://github.com/aisystant/personal-knowledge-mcp | GKE Standard europe-west4 | Личные знания пользователя | ❌ Нет (сейчас CF Worker) |

> **Контейнеризация (важно):** все три сейчас Cloudflare Workers — для GKE нужны Dockerfile + адаптация (runtime Workers ≠ Node-контейнер). Добавить так же, как для agent-status-service (раздел 3). После переезда `KNOWLEDGE_MCP_URL` / `DIGITAL_TWIN_MCP_URL` / `PERSONAL_KNOWLEDGE_MCP_URL` в шлюзе указывают на ClusterIP кластера, а не на CF.

**C. Вспомогательные сервисы — вынесенная из шлюза логика (WP-402, новые, в GKE)**

Это прикладная логика, которую шлюз раньше держал в себе; WP-402 вынес её в отдельные сервисы, чтобы шлюз стал чистым маршрутизатором.

| Сервис | Репозиторий | Платформа | Статус | Dockerfile |
|--------|-------------|-----------|--------|------------|
| **bridge-scope-service** | https://github.com/aisystant/bridge-scope-service | GKE Standard europe-west4 | Код готов, не задеплоен | ✅ Есть |
| **agent-status-service** | https://github.com/aisystant/agent-status-service | GKE Standard europe-west4 | Код готов, не задеплоен | ❌ **Нет** (добавить — см. раздел 3) |
| **github-integration-service** | https://github.com/aisystant/github-integration-service | GKE Standard europe-west4 | Код готов, не задеплоен | ✅ Есть |
| **user-profile-service** | https://github.com/aisystant/user-profile-service | GKE Standard europe-west4 | Код готов, не задеплоен | ✅ Есть |
| **learning-context-service** | https://github.com/aisystant/learning-context-service | GKE Standard europe-west4 | Код готов, не задеплоен | ✅ Есть |

> **Итог по конфигу шлюза (тест Андрея):** после WP-402 шлюз содержит только адреса — 3 backend-MCP (группа B) + 5 вынесенных сервисов (группа C) = 8 URL + парные секреты, без баз данных на роутинг-пути (кроме легитимных остатков — token hook + техдолг BYOK, см. 4.4).
>
> **Авто-деплой gateway:** репозиторий `gateway-mcp` содержит `.github/workflows/deploy.yml` на `push: [main]` → каждый push в main выкатывается на прод. Код Р1-Р9 уже в проде; сервисы группы C нужно поднять под него.

</details>

<details>
<summary><b>2. Всё необходимое для переноса (секреты и env)</b></summary>

### 2.1 Gateway — новые Wrangler-секреты

Gateway остаётся на Cloudflare Workers, но теперь проксирует часть вызовов в GKE-сервисы.

```bash
# Р1 (bridge-scope)
wrangler secret put SCOPE_SERVICE_URL          # http://bridge-scope-service (ClusterIP)
wrangler secret put SCOPE_SERVICE_SHARED_SECRET

# Р2 (agent-status)
wrangler secret put AGENT_STATUS_SERVICE_URL
wrangler secret put AGENT_STATUS_SHARED_SECRET

# Р6 (github-integration)
wrangler secret put GITHUB_INTEGRATION_SERVICE_URL
wrangler secret put GITHUB_INTEGRATION_SHARED_SECRET

# Р8 (user-profile)
wrangler secret put USER_PROFILE_SERVICE_URL
wrangler secret put USER_PROFILE_SHARED_SECRET

# Р9 (learning-context)
wrangler secret put LEARNING_CONTEXT_SERVICE_URL
wrangler secret put LEARNING_CONTEXT_SHARED_SECRET
```

> **Naming стыковки:** gateway шлёт `Authorization: Bearer <SERVICE>_SHARED_SECRET` + `X-User-Id` заголовок. Каждый сервис читает секрет из переменной `GATEWAY_SHARED_SECRET` (та же строка, другое имя env).
>
> **/health hard-required (после WP-402 verify, коммит `fed4f7f`):** `USER_PROFILE_*` и `LEARNING_CONTEXT_*` теперь обязательны в проверке здоровья gateway — без них `/health` отдаёт 503 (закрыт ложно-зелёный статус). `SCOPE_*`/`AGENT_STATUS_*`/`GITHUB_INTEGRATION_*` пока по схеме «обе или ни одной» (both-unset проходит как зелёный — потенциальный ложно-зелёный, кандидат на ужесточение, см. раздел 4.4).

### 2.2 Оставшиеся секреты gateway (не убирать)

| Секрет | Зачем | Когда уйдёт |
|--------|-------|-------------|
| `DATABASE_URL` | persona DB: personal_connect_source, GitHub webhook, scout page, syncUpstreamForks, **BYOK-management (list/grant/revoke_llm_key — техдолг Р11)** | После выноса остатков (вне WP-402) |
| `SUBSCRIPTION_DATABASE_URL` | Token hook `/hydra-hook/token` — читает подписку для claim injection | После установки Ory TTL 5 мин + подтверждения что hotfix-B больше не нужен |
| `INDICATORS_DATABASE_URL` | `provisionBridgeScopes` — fire-and-forfeit запись в `indicators.agent_scopes_mvp` | Когда bridge-scope-service получит provisioning endpoint |

### 2.3 Env-переменные для GKE-сервисов (Secret Manager / Cloud SQL)

#### bridge-scope-service
- `DATABASE_URL` — Neon **indicators** DB (обязательно)
- `GATEWAY_SHARED_SECRET` — для middleware auth (обязательно)
- `PORT` — default 3000

#### agent-status-service
- `DATABASE_URL` — Neon **indicators** DB (обязательно)
- `GATEWAY_SHARED_SECRET` — для middleware auth (обязательно)
- `PORT` — default 3000
- `GHOST_TTL_HOURS` — optional

#### github-integration-service
- `DATABASE_URL` — Neon **persona** DB (обязательно)
- `ORY_CLIENT_SECRET` — для Ory token introspection (обязательно)
- `GATEWAY_PUBLIC_ORIGIN` — публичный origin gateway (обязательно)
- `GATEWAY_SHARED_SECRET` — для middleware auth
- GitHub App: `GITHUB_APP_ID`, `GITHUB_APP_PRIVATE_KEY`, `GITHUB_WEBHOOK_SECRET`
- GitHub OAuth: `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`
- Reindex secrets: `KNOWLEDGE_REINDEX_SECRET`, `PERSONAL_REINDEX_SECRET`
- Bot notify: `BOT_NOTIFY_URL`, `BOT_NOTIFY_SECRET`
- Bot workbook: `BOT_WORKBOOK_WEBHOOK_URL`, `BOT_WORKBOOK_WEBHOOK_SECRET`
- Прочее: `AGENT_RUNNER_URL`, `PROXY_SHARED_SECRET`, `PERSONAL_KNOWLEDGE_MCP_URL`, `KNOWLEDGE_MCP_URL`, `LEARNING_DATABASE_URL`, `KNOWLEDGE_DB_SCHEMA`

#### user-profile-service
- `DATABASE_URL` — Neon **persona** DB (обязательно)
- `GATEWAY_SHARED_SECRET` — для middleware auth (обязательно)
- `BYOK_KEK` — для расшифровки пользовательских LLM-ключей
- `BOT_NOTIFY_URL` + `BOT_NOTIFY_SECRET` — для `/notify-bot`
- `KNOWLEDGE_DB_SCHEMA` — default: knowledge

#### learning-context-service
- `GATEWAY_SHARED_SECRET` — для middleware auth (обязательно)
- `LEARNING_DATABASE_URL` — Neon **learning** DB (или `DATABASE_URL`, сервис сам деривирует `/persona` → `/learning`)
- `PORT` — default 3000
- **БД-зависимости (применить миграции на LEARNING):** `learning.consent_grant` (`neon-migrations/mvp/229`, `261`), `cognitive.brief` (схема `cognitive` в той же learning-БД, `neon-migrations/mvp/230`). Без них `/grant-consent` и `/cognitive-brief` падают.

</details>

<details>
<summary><b>3. Рекомендация Андрею — пошаговый план</b></summary>

### Критично (до первого деплоя)

1. **Добавить Dockerfile (4 сервиса без контейнера):** `agent-status-service` + три backend-MCP (`knowledge-mcp`, `digital-twin-mcp`, `personal-knowledge-mcp`) — все сейчас без Dockerfile. У трёх backend-MCP сверх контейнера нужна адаптация с runtime Cloudflare Workers на Node-контейнер.
2. **Применить миграции БД:**
   - `262-scope-rls.sql` на prod **INDICATORS** (`neon-migrations/mvp/262-scope-rls.sql`) — блокер для `bridge-scope-service`.
   - `consent_grant` (`229`, `261`) + `cognitive.brief` (`230`) на prod **LEARNING** — блокер для `learning-context-service`.
3. **Установить Ory access-token TTL = 5 мин** в Ory Network — после этого `SUBSCRIPTION_DATABASE_URL` можно убрать из gateway routing path (hotfix-B станет не нужен).

### Порядок деплоя (рекомендуемый)

**Сначала — 3 backend-MCP (серверы знаний, группа B):**

1. **knowledge-mcp** → контейнеризация + GKE → проверить поиск
2. **digital-twin-mcp** → контейнеризация + GKE → проверить чтение двойника
3. **personal-knowledge-mcp** → контейнеризация + GKE → проверить личные знания

**Затем — 5 вынесенных сервисов (группа C):**

4. **bridge-scope-service** → GKE + Secret Manager
   - Проверить `/health`
   - Проверить RLS работает (`SET LOCAL app.user_id`)
5. **agent-status-service** → GKE + Secret Manager
   - Проверить `/health`
6. **github-integration-service** → GKE + Secret Manager
   - Проверить `/health`
   - Проверить webhook delivery (GitHub App callback URL = gateway, gateway проксирует)
7. **user-profile-service** → GKE + Secret Manager
   - Проверить `/health`
   - Проверить `/tier?userId=<uuid>`
8. **learning-context-service** → GKE + Secret Manager
   - Проверить `/health`
   - Проверить `/consent?userId=<uuid>` и `/cognitive-brief?userId=<uuid>`

**Последним — gateway:**

9. **gateway-mcp** — обновить Wrangler secrets: все backend-URL (`KNOWLEDGE_MCP_URL`/`DIGITAL_TWIN_MCP_URL`/`PERSONAL_KNOWLEDGE_MCP_URL` → ClusterIP) + все `*_SERVICE_URL` + `*_SHARED_SECRET` пары
   - Проверить `/health` возвращает `{"ok":true}` (сейчас 503 — это и есть сигнал «сервисы не подключены»)
   - Проверить tool handlers проксируются (smoke: `get_user_context`, `grant_consent`, `get_cognitive_brief`, `get_journey_state`, `github_connect`, поиск через backend-MCP)

> **Важно по порядку:** поднять все 8 сервисов (3 backend-MCP + 5 вынесенных) + миграции ПЕРВЫМИ, env-vars в gateway — последним шагом. Gateway авто-деплоится при push, но секреты `wrangler secret put` применяются к уже задеплоенному Worker сразу. До установки секретов `/health` остаётся 503.

### Private networking

Все 8 сервисов деплоятся в **тот же GKE-кластер Track B** (europe-west4) → ClusterIP недоступны извне → вариант C auth (shared-secret + `X-User-Id`) безопасен без mTLS. Для backend-MCP это также убирает их публичные CF-URL за периметр кластера.

</details>

<details>
<summary><b>4. Что сделано — очистка gateway-mcp, новые сервисы, верификация</b></summary>

### 4.1 Что удалено из gateway-mcp

| Что | Где было | Куда ушло | Коммит |
|-----|----------|-----------|--------|
| `scope.ts` (670 строк) | `gateway-mcp/src/` | `bridge-scope-service` | `af680ee` |
| `agent-status.ts` | `gateway-mcp/src/` | `agent-status-service` (proxy) | `6ae2d09` |
| `backend-registry.ts` | `gateway-mcp/src/` | Удалён полностью | `d4203f4` |
| `github-setup.ts` (~1185 строк) | `gateway-mcp/src/` | `github-integration-service` | `07b5b14` + `a38fcb7` |
| `checkTier` + `checkConsent` + `getCognitiveBrief` + `grantConsentInGateway` + `resolveUserLlmKey` + `notifyBotUserRepoIndexing` + `decryptApiKey` | `gateway-mcp/src/index.ts` | Удалены; заменены на HTTP-прокси | `ff24dcd`, `903891a` |

### 4.2 Что создано — новые сервисы

| Сервис | Репозиторий | Что делает | Endpoints |
|--------|-------------|------------|-----------|
| **bridge-scope-service** | https://github.com/aisystant/bridge-scope-service | Scope enforcement + provisioning | `POST /check`, `POST /provision` |
| **agent-status-service** | https://github.com/aisystant/agent-status-service | Agent status board | `POST /update`, `GET /list`, `GET /by-repo` |
| **github-integration-service** | https://github.com/aisystant/github-integration-service | GitHub App webhooks + OAuth + repo creation | `POST /webhook`, `GET /github/*`, `POST /api/v1/repo/create` |
| **user-profile-service** | https://github.com/aisystant/user-profile-service | Identity, context, BYOK, bot notify, tier | `GET /user-context`, `GET /tier`, `POST /byok`, `POST /notify-bot`, `GET /github-connected`, `GET /onboarding-context` |
| **learning-context-service** | https://github.com/aisystant/learning-context-service | Consent, cognitive brief, onboarding state | `GET /consent`, `POST /grant-consent`, `GET /cognitive-brief`, `GET /onboarding-state` |

### 4.3 Верификация WP-402 Р8+Р9 (peer-сессия 2026-06-09-07)

165 тестов gateway зелёные, production-код компилируется чисто. При проверке найдены и **починены 2 блокера + 1 дефект:**

| Дефект | Починка |
|--------|---------|
| `get_cognitive_brief` читал таблицу `learning.cognitive_brief`, которой нет в миграциях → 500 на проде. Каноническая — `cognitive.brief`. | learning-context-service `bc0fee6`: чтение `cognitive.brief` + прежний контракт полей + GUC в `begin()` |
| Потерян consent-guard: `cognitive_profile` (PII) отдавался без `text_analysis` consent | тот же коммит — guard восстановлен (B7.3) |
| Фикс `grant-consent` был незакоммичен; закоммиченная версия использовала старую схему consent_grant → упала бы в проде | закоммичен в `bc0fee6` (каноническая схема) |
| `/health` не проверял два новых сервиса → ложно-зелёный | gateway `fed4f7f`: пары добавлены в health-check |

### 4.4 Gateway — что осталось

Gateway = маршрутизатор + Ory JWT auth + fan-out к backends.

- **Роутинг-путь почти чист** — кроме легитимных остатков (token hook) **и одного техдолга:**
  - **Hydra token hook** (`/hydra-hook/token`) — легитимный остаток: endpoint выдачи claims, читает БД по роли, не на роутинг-пути.
  - **⚠️ BYOK-management** (`list_llm_keys`/`grant_llm_key`/`revoke_llm_key`, `index.ts:2109+`) — всё ещё ходит в `DATABASE_URL` напрямую. Это **прикладная БД-логика на роутинг-пути, нарушает тест Андрея**. Не успели в Р8. Решение (Р11 в WP-402): вынести в `user-profile-service` (`/llm-keys`) или признать остатком — **через ArchGate**.
- **Tool handlers** остаются в `tools/list` для внешних MCP-клиентов, но делегируют вызовы в сервисы.

### 4.5 Открытый техдолг (не блокирует деплой)

- **BYOK-management вынос** (Р11, требует ArchGate) — см. 4.4.
- **Тесты новых сервисов** (Р12): у 5 сервисов нет тестов; `health-check.test.ts` дублирует логику вместо вызова реального обработчика.
- GitHub issue #13: [Migrate GET endpoints from ?userId= query param to X-User-Id header](https://github.com/aisystant/gateway-mcp/issues/13) — API-гигиена.

</details>

<details>
<summary><b>5. Быстрая проверка после деплоя (smoke)</b></summary>

```bash
# Gateway health (сейчас 503; после подключения сервисов → {"ok":true})
curl https://mcp.aisystant.com/health | jq .

# Backend-MCP health (группа B — серверы знаний, после переезда в GKE)
curl http://knowledge-mcp/health
curl http://digital-twin-mcp/health
curl http://personal-knowledge-mcp/health

# Вынесенные сервисы health (группа C, через kubectl port-forward или внутри кластера)
curl http://bridge-scope-service/health
curl http://agent-status-service/health
curl http://github-integration-service/health
curl http://user-profile-service/health
curl http://learning-context-service/health

# Gateway proxy smoke (с JWT-токеном)
curl -H "Authorization: Bearer <JWT>" https://mcp.aisystant.com/api/v1/user-context
```

**Критерий приёмки переключённых инструментов:** `get_cognitive_brief` возвращает бриф известного пользователя (а не «service not configured»); `get_journey_state` возвращает корректный stage (а не «consent=false для всех»).

</details>

---

*Составлено: Kimi (WP-402 Р8+Р9) + Claude Code (Р1-Р7, верификация 2026-06-09-07).*
