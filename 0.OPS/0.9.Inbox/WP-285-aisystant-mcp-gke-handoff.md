# WP-285 — Передача Aisystant MCP (Россия → Мир)

> Документ handoff для Андрея Смирнова (архитектор / Track B — мировая инфраструктура).
> Актуально на 2026-06-09 (после верификации WP-402 Р8+Р9 + переформулировки Russia/World, peer-сессия 2026-06-09-10). Все репозитории приватные (`aisystant/*`).
>
> **Принцип передачи (уточнение пилота 2026-06-09).** Андрей **не переносит и не удаляет** текущие сервисы — он **пересоздаёт их заново** в мировой инфраструктуре (GKE) для новых платящих пользователей мира. Текущая (российская) инфра **остаётся** и обязана работать для ВСЕХ текущих пользователей. Наша задача по РП402 — отдать **чистую, документированную и работающую** российскую версию, с которой Андрей копирует всё для мира **без нашего участия**.
>
> **Статус одной строкой:** вынос кода Р1-Р9 закрыт и в проде (gateway авто-деплоится при push в main). 5 сервисов не развёрнуты → `mcp.aisystant.com/health` отдаёт **503** → у текущих (российских) пользователей переключённые инструменты (бриф, тариф, journey) деградируют. **Это наш долг — фаза Р10-RU (раздел 3А), а не работа Андрея.** Работа Андрея — пересоздание на GKE (Р10-World, раздел 3Б) с уже чистой российской версии.

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

**C. Вспомогательные сервисы — вынесенная из шлюза логика (WP-402, новые)**

Это прикладная логика, которую шлюз раньше держал в себе; WP-402 вынес её в отдельные сервисы, чтобы шлюз стал чистым маршрутизатором. **Платформа:** для России — Railway-контейнеры (подтверждено пилотом 2026-06-09, «пока»); для мира — Андрей пересоздаёт их на GKE Standard (europe-west4) сам.

| Сервис | Репозиторий | О чём сервис | Статус | Dockerfile |
|--------|-------------|--------------|--------|------------|
| **bridge-scope-service** | https://github.com/aisystant/bridge-scope-service | Scope enforcement for bridge write-tools (agent write permissions) | Code ready, not deployed | ✅ Dockerfile, ✅ README EN, ✅ tests (30) |
| **agent-status-service** | https://github.com/aisystant/agent-status-service | Agent status board (conflict prevention for multi-agent workspaces) | Code ready, not deployed | ❌ Dockerfile (add — see §3), ✅ README EN, ✅ tests (8) |
| **github-integration-service** | https://github.com/aisystant/github-integration-service | GitHub App webhooks, OAuth and user repository creation | Code ready, not deployed | ✅ Dockerfile, ✅ README EN, ✅ tests (5) |
| **user-profile-service** | https://github.com/aisystant/user-profile-service | User identity, tier, BYOK key resolution, bot notifications | Code ready, not deployed | ✅ Dockerfile, ✅ README EN, ✅ tests (2) |
| **learning-context-service** | https://github.com/aisystant/learning-context-service | Consent management, cognitive brief, onboarding state | Code ready, not deployed | ✅ Dockerfile, ✅ README EN, ✅ tests (3) |

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
<summary><b>3. План доделок (Р10–Р14) + рекомендация Андрею по GKE</b></summary>

### План остатка РП402 (peer-сессия 2026-06-09-10, Claude + Kimi)

> Рамка: «Россия (наша работа) → Мир (работа Андрея)». Граница — фаза Р10 расщеплена на Р10-RU (мы восстанавливаем текущих пользователей) и Р10-World (Андрей пересоздаёт на GKE).

| Фаза | Владелец | Суть | Блокер / критерий |
|------|----------|------|-------------------|
| **Р10-RU** | **Мы** | Восстановить работу текущих российских пользователей: развернуть 5 сервисов и подключить их к текущему gateway (Cloudflare Worker) | **Платформа: Railway** (подтверждено пилотом 2026-06-09, «пока»). На контроле: пересечение с уходом Railway к Ильшату (Track A) + auth только на общем ключе без приватной сети → для `bridge-scope` отдельный секрет. Критерий: `/health` → `{"ok":true}` + smoke брифа и journey возвращает корректные значения для известного пользователя (не только «не 5xx» — у journey тихая деградация) |
| **Р10-World** | **Андрей** | Пересоздание всех сервисов на GKE Standard (europe-west4) + Cloud SQL, копированием с чистой документированной российской версии | Без нашего участия. Пошаговый плейбук — раздел 3Б ниже |
| **Р11** | Мы | BYOK-management (`list/grant/revoke_llm_key`) — вынести из gateway в `user-profile-service` (`/llm-keys`) **или** признать осознанным остатком в ADR | Через `/archgate`. Это единственное живое нарушение теста Андрея на роутинг-пути |
| **Р12** | Мы | Тесты 5 сервисов + переписать `health-check.test.ts` на вызов реального обработчика (сейчас дублирует логику) | — |
| **Р13** | Мы (**блокер передачи**) | README (EN) на каждый из 5 сервисов по единому шаблону + вычистить ссылки на номера РП из кода и тестов | Прямое требование Андрея: «репозиторий самодостаточный, на английском, без отсылок к твоей стратегии» |
| **Р14** | Мы (опционально, low) | Перевести русские комментарии в исходниках 4 сервисов на английский | Post-handoff или по запросу Андрея. Комментарии ≠ публичная витрина |

> **Что в этой рамке означает «передать по правильным принципам»:** Андрей получает (1) работающую российскую инфру — текущие пользователи не сломаны (Р10-RU); (2) самодостаточные репозитории с README на английском без внутренних ссылок (Р13); (3) чистый роутер по своему тесту (Р11 закрыт или задокументирован); (4) этот документ как карту развёртывания. С этого он копирует мир сам.

---

### 3А. Р10-RU — восстановить текущих пользователей (владелец: мы)

> **Зачем:** gateway после Р1-Р9 уже в проде и зовёт 5 сервисов, которых нет → бриф/тариф/journey деградируют у живых российских пользователей прямо сейчас. Это наша регрессия, не работа Андрея.

1. **Хостинг 5 сервисов: Railway** (подтверждено пилотом 2026-06-09, «пока»). 4/5 сервисов уже с Dockerfile, текущий gateway (Cloudflare Worker) зовёт их по публичным URL. На контроле: на Railway аутентификация остаётся только на общем ключе (без приватной сети, как в GKE) → для `bridge-scope` (запись + персональные данные) держать **отдельный** секрет; и Railway по текущему плану уходит Ильшату (Track A) — согласовать пересечение при исполнении.
2. **Применить миграции** (те же, что для мира): `262-scope-rls.sql` на INDICATORS; `consent_grant` (229, 261) + `cognitive.brief` (230) на LEARNING.
3. **Развернуть 5 сервисов** на выбранной российской платформе + прописать пары URL/ключ в gateway (`wrangler secret put`, раздел 2.1).
4. **Smoke (обязательно содержательный):** `/health` → `{"ok":true}`; `get_cognitive_brief` возвращает бриф известного пользователя; `get_journey_state` — корректный stage (а не «consent=false для всех»). Мониторинг по 5xx тихую деградацию journey не ловит.

---

### 3Б. Р10-World — пересоздание на GKE (владелец: Андрей)

> Ниже — рекомендованный пошаговый плейбук для пересоздания на мировой инфраструктуре. Андрей проходит его сам (с Пашей), копируя с чистой российской версии.

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
| **bridge-scope-service** | https://github.com/aisystant/bridge-scope-service | Scope enforcement (provisioning остался в gateway → техдолг `INDICATORS_DATABASE_URL`) | `POST /check-scope`, `GET /health` |
| **agent-status-service** | https://github.com/aisystant/agent-status-service | Agent status board | `POST /api/v1/status` (update), `GET /api/v1/status` (list, фильтр `?repo=`), `GET /health` |
| **github-integration-service** | https://github.com/aisystant/github-integration-service | GitHub App webhooks + OAuth + repo creation | `POST /github/webhook`; `/api/v1/github/*` (`connect`/`status`/`disconnect`/`repo`); `/github/*` (`install`/`setup`/`create-repo`/`repo-callback`); `GET /health` |
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
- **Тесты новых сервисов** (Р12): базовые тесты написаны для 4 сервисов (bridge-scope: 30, agent-status: 8, github-integration: 5, user-profile: 2, learning-context: 3). `health-check.test.ts` в gateway-mcp всё ещё дублирует логику вместо вызова реального обработчика — требует рефакторинга server.ts (export app).
- **Гигиена публичных репо** (Р13, **блокер передачи — ЗАКРЫТ**): README (EN) добавлены для всех 5 сервисов; ссылки на номера РП (`WP-402`/`WP-381`/`WP-373`/`WP-391`) вычищены из кода и тестов. Русские комментарии в исходниках 4 из 5 — остаются как опционный post-handoff пункт (Р14).
- GitHub issue #13: [Migrate GET endpoints from ?userId= query param to X-User-Id header](https://github.com/aisystant/gateway-mcp/issues/13) — API-гигиена.

> **Проверка на чувствительные данные (2026-06-09):** этот документ просканирован регулярками на значения ключей/токенов/строк подключения — **значений нет**, только имена переменных и команды их установки без значений. Безопасен для приватного репозитория `aisystant/*`. Не выкладывать в публичный доступ как есть: содержит полный инвентарь имён секретов и внутреннюю карту архитектуры.

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
