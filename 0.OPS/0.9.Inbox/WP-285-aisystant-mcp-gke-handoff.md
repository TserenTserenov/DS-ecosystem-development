# W286 — Передача Aisystant MCP в GKE

> Документ handoff для Андрея Смирнова (архитектор / Track B).
> Актуально на 2026-06-09. Все репозитории приватные (`aisystant/*`).

---

## 1. Список передаваемых MCP

| Сервис | Репозиторий | Платформа | Статус | Dockerfile |
|--------|-------------|-----------|--------|------------|
| **gateway-mcp** | https://github.com/aisystant/gateway-mcp | Cloudflare Worker (Wrangler) | Очищен, код готов | Нет (Worker) |
| **bridge-scope-service** | https://github.com/aisystant/bridge-scope-service | GKE Standard europe-west4 | Код готов, не задеплоен | ✅ Есть |
| **agent-status-service** | https://github.com/aisystant/agent-status-service | GKE Standard europe-west4 | Код готов, не задеплоен | ❌ **Нет** |
| **github-integration-service** | https://github.com/aisystant/github-integration-service | GKE Standard europe-west4 | Код готов, не задеплоен | ✅ Есть |
| **user-profile-service** | https://github.com/aisystant/user-profile-service | GKE Standard europe-west4 | Код готов, не задеплоен | ✅ Есть |
| **learning-context-service** | https://github.com/aisystant/learning-context-service | GKE Standard europe-west4 | Код готов, не задеплоен | ✅ Есть |

---

## 2. Всё необходимое для переноса

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

### 2.2 Оставшиеся секреты gateway (не убирать)

| Секрет | Зачем | Когда уйдёт |
|--------|-------|-------------|
| `DATABASE_URL` | persona DB: personal_connect_source, GitHub webhook, scout page, syncUpstreamForks | После выноса остатков (вне WP-402) |
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

---

## 3. Рекомендация Андрею — пошаговый план

### Критично (до первого деплоя)

1. **Добавить Dockerfile в `agent-status-service`** — единственный сервис без контейнера.
2. **Применить RLS-миграцию `262-scope-rls.sql`** на prod INDICATORS DB (`neon-migrations/mvp/262-scope-rls.sql`) — блокер для `bridge-scope-service`.
3. **Установить Ory access-token TTL = 5 мин** в Ory Network — после этого `SUBSCRIPTION_DATABASE_URL` можно убрать из gateway routing path (hotfix-B станет не нужен).

### Порядок деплоя (рекомендуемый)

1. **bridge-scope-service** → GKE + Secret Manager
   - Проверить `/health`
   - Проверить RLS работает (`SET LOCAL app.user_id`)
2. **agent-status-service** → GKE + Secret Manager
   - Проверить `/health`
3. **github-integration-service** → GKE + Secret Manager
   - Проверить `/health`
   - Проверить webhook delivery (GitHub App callback URL = gateway, gateway проксирует)
4. **user-profile-service** → GKE + Secret Manager
   - Проверить `/health`
   - Проверить `/tier?userId=<uuid>`
5. **learning-context-service** → GKE + Secret Manager
   - Проверить `/health`
   - Проверить `/consent?userId=<uuid>`
6. **gateway-mcp** — обновить Wrangler secrets (все `*_SERVICE_URL` + `*_SHARED_SECRET` пары)
   - Проверить `/health` возвращает `{"ok":true}`
   - Проверить tool handlers проксируются (smoke: `get_user_context`, `grant_consent`, `github_connect`)

### Private networking

Все новые сервисы деплоятся в **тот же GKE-кластер Track B** (europe-west4) → ClusterIP недоступны извне → вариант C auth (shared-secret + `X-User-Id`) безопасен без mTLS.

---

## 4. Что сделано — очистка gateway-mcp и новые сервисы

### 4.1 Что удалено из gateway-mcp

| Что | Где было | Куда ушло | Коммит |
|-----|----------|-----------|--------|
| `scope.ts` (670 строк) | `gateway-mcp/src/` | `bridge-scope-service` | `af680ee` |
| `agent-status.ts` | `gateway-mcp/src/` | `agent-status-service` (proxy) | `6ae2d09` |
| `backend-registry.ts` | `gateway-mcp/src/` | Удалён полностью | `d4203f4` |
| `github-setup.ts` (~1185 строк) | `gateway-mcp/src/` | `github-integration-service` | `07b5b14` + `a38fcb7` |
| `checkTier` + `checkConsent` + `getCognitiveBrief` + `grantConsentInGateway` + `resolveUserLlmKey` + `notifyBotUserRepoIndexing` + `decryptApiKey` | `gateway-mcp/src/index.ts` | Удалены; заменены на HTTP-прокси | `ff24dcd` |

### 4.2 Что создано — новые сервисы

| Сервис | Репозиторий | Что делает | Endpoints |
|--------|-------------|------------|-----------|
| **bridge-scope-service** | https://github.com/aisystant/bridge-scope-service | Scope enforcement + provisioning | `POST /check`, `POST /provision` |
| **agent-status-service** | https://github.com/aisystant/agent-status-service | Agent status board | `POST /update`, `GET /list`, `GET /by-repo` |
| **github-integration-service** | https://github.com/aisystant/github-integration-service | GitHub App webhooks + OAuth + repo creation | `POST /webhook`, `GET /github/*`, `POST /api/v1/repo/create` |
| **user-profile-service** | https://github.com/aisystant/user-profile-service | Identity, context, BYOK, bot notify, tier | `GET /user-context`, `GET /tier`, `POST /byok`, `POST /notify-bot`, `GET /github-connected`, `GET /onboarding-context` |
| **learning-context-service** | https://github.com/aisystant/learning-context-service | Consent, cognitive brief, onboarding state | `GET /consent`, `POST /grant-consent`, `GET /cognitive-brief`, `GET /onboarding-state` |

### 4.3 Gateway — что осталось

Gateway = чистый маршрутизатор + Ory JWT auth + fan-out к backends.

- **Проходит тест Андрея** (роутинг-путь без прикладных Neon-коннектов, кроме легитимных остатков).
- **Tool handlers** остаются в `tools/list` для внешних MCP-клиентов, но делегируют вызовы в сервисы.
- **Hydra token hook** (`/hydra-hook/token`) — признан легитимным остатком: endpoint выдачи claims, читает БД по роли, не на роутинг-пути.

### 4.4 Открытый техдолг (не блокирует деплой)

- GitHub issue #13: [Migrate GET endpoints from ?userId= query param to X-User-Id header](https://github.com/aisystant/gateway-mcp/issues/13) — API-гигиена, условие Kimi для отложения П3.

---

## 5. Быстрая проверка после деплоя (smoke)

```bash
# Gateway health
curl https://mcp.aisystant.com/health | jq .

# Service health (через kubectl port-forward или внутри кластера)
curl http://bridge-scope-service/health
curl http://agent-status-service/health
curl http://github-integration-service/health
curl http://user-profile-service/health
curl http://learning-context-service/health

# Gateway proxy smoke (с JWT-токеном)
curl -H "Authorization: Bearer <JWT>" https://mcp.aisystant.com/api/v1/user-context
```

---

*Составлено: Kimi (WP-402 Р8+Р9) + Claude Code (Р1-Р7).*
