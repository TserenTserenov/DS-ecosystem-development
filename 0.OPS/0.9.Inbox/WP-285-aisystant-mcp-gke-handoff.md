# Aisystant MCP — перенос в мировую инфраструктуру (GKE)

> Карта сервисов, конфигурация и план развёртывания для пересоздания Aisystant MCP в новой (мировой) инфраструктуре на Google Kubernetes Engine (Track B).
> Текущие (российские) экземпляры остаются работать отдельно на Railway + Cloudflare Workers (Track A) — этот документ описывает, как поднять те же сервисы заново для новых пользователей мира.
> Все репозитории приватные (`aisystant/*`). Актуально на 2026-06-10.
>
> **Контекст:** кто разрабатывает MVP, кто принимает и разворачивает на GKE, кто разворачивает на российской инфраструктуре — см. [WP-73-org-split-principles.md §5 «Поток разработки и передачи между контурами»](WP-73-org-split-principles.md).
>
> **Разделение треков:**
> - **Track A (Россия):** шлюз `gateway-mcp` на Cloudflare Workers + 5 вспомогательных сервисов на Railway. Остаётся без изменений для текущих пользователей.
> - **Track B (Мир):** полный стек в GKE Standard (europe-west4) + Cloud SQL. Этот документ — плейбук для Track B.

> **Принцип шлюза.** Aisystant MCP = это **шлюз** (`gateway-mcp`, `mcp.aisystant.com`) — единственная точка, к которой подключаются внешние клиенты (claude.ai, Claude Code, VS Code). Задача шлюза одна: принять запрос и отмаршрутизировать его на нужный сервер. В его конфиге должны быть только адреса серверов, которые он объединяет (плюс парные ключи для них) — без баз данных. Прикладная логика живёт в отдельных сервисах за шлюзом, а не в самом шлюзе.

<details open>
<summary><b>1. Карта сервисов</b></summary>

За шлюзом стоят два класса сервисов: серверы знаний (backend-MCP) и вспомогательные сервисы (прикладная логика). Шлюз раздаёт запросы серверам знаний и проксирует часть вызовов во вспомогательные сервисы.

**A. Шлюз (Track B — мир)**

| Сервис | Репозиторий | Платформа | Статус |
|--------|-------------|-----------|--------|
| **gateway-mcp** | https://github.com/aisystant/gateway-mcp | **GKE** (Kubernetes Deployment) | Пересоздаётся в GKE. Конфиг — только URL-адреса 8 сервисов + парные ключи, без баз данных на пути маршрутизации |

> **Track A (Россия):** текущий шлюз остаётся на Cloudflare Workers (`mcp.aisystant.com`) и проксирует в Railway. Track B получает **отдельный** экземпляр шлюза в GKE (свой домен или поддомен). Два шлюза независимы — у каждого свои env-переменные и свои бэкенды.

**B. Серверы знаний (backend-MCP)**

Шлюз раздаёт им запросы: поиск, цифровой двойник, личные знания. Это и есть те «адреса серверов», к которым сводится конфиг шлюза.

| Сервис | Репозиторий | Что делает | Готовность к контейнеру |
|--------|-------------|------------|-------------------------|
| **knowledge-mcp** | https://github.com/aisystant/knowledge-mcp | Поиск по базе знаний | ❌ Dockerfile (сейчас Cloudflare Worker) |
| **digital-twin-mcp** | https://github.com/aisystant/digital-twin-mcp | Цифровой двойник пользователя | ❌ Dockerfile (сейчас Cloudflare Worker) |
| **personal-knowledge-mcp** | https://github.com/aisystant/personal-knowledge-mcp | Личные знания пользователя | ❌ Dockerfile (сейчас Cloudflare Worker) |

> Все три сейчас на Cloudflare Workers — для GKE нужны Dockerfile и адаптация (среда Workers ≠ Node-контейнер). После переезда адреса `KNOWLEDGE_MCP_URL` / `DIGITAL_TWIN_MCP_URL` / `PERSONAL_KNOWLEDGE_MCP_URL` в шлюзе указывают на внутренние адреса кластера (ClusterIP), а не на Cloudflare.

**C. Вспомогательные сервисы (прикладная логика за шлюзом)**

Прикладная логика, вынесенная из шлюза в отдельные сервисы — чтобы шлюз остался чистым маршрутизатором. Все на TypeScript/Node, с README и базовыми тестами.

| Сервис | Репозиторий | Что делает | Эндпоинты | Готов |
|--------|-------------|------------|-----------|-------|
| **bridge-scope-service** | https://github.com/aisystant/bridge-scope-service | Проверяет, можно ли агенту писать в репозиторий пользователя; выдаёт стартовые права при подключении источника | `POST /check-scope`, `POST /api/v1/provision`, `GET /health` | Dockerfile ✅, README ✅ |
| **agent-status-service** | https://github.com/aisystant/agent-status-service | Доска статусов агентов (кто чем занят, какие файлы трогает) | `POST /api/v1/status`, `GET /api/v1/status` (фильтр `?repo=`), `GET /health` | Dockerfile ✅, README ✅ |
| **github-integration-service** | https://github.com/aisystant/github-integration-service | Вебхуки GitHub App, вход через GitHub, создание репозиториев пользователей | `POST /github/webhook`; `/api/v1/github/*` (`connect`/`status`/`disconnect`/`repo`); `/github/*` (`install`/`setup`/`create-repo`/`repo-callback`); `GET /health` | Dockerfile ✅, README ✅ |
| **user-profile-service** | https://github.com/aisystant/user-profile-service | Профиль пользователя: контекст, тариф, ключи к моделям (BYOK + управление ключами), уведомления боту | `GET /user-context`, `GET /tier`, `POST /byok`, `GET\|POST /llm-keys`, `POST /llm-keys/revoke`, `POST /notify-bot`, `GET /github-connected`, `GET /onboarding-context` | Dockerfile ✅, README ✅ |
| **learning-context-service** | https://github.com/aisystant/learning-context-service | Согласие на обработку данных, когнитивный бриф, состояние онбординга | `GET /consent`, `POST /grant-consent`, `GET /cognitive-brief`, `GET /onboarding-state` | Dockerfile ✅, README ✅ |

> **Итог по конфигу шлюза:** после выноса логики шлюз держит только адреса — 3 сервера знаний (B) + 5 вспомогательных сервисов (C) = 8 адресов с парными ключами, без баз данных на пути маршрутизации (известные исключения — в разделе 4).

</details>

<details>
<summary><b>2. Конфигурация: секреты и переменные окружения</b></summary>

### 2.1 Шлюз — адреса и ключи вспомогательных сервисов

Шлюз в Track B разворачивается в GKE и проксирует вызовы во внутренние сервисы кластера. Для каждого сервиса — пара «адрес + общий ключ»:

```bash
# GKE SecretManager / Helm values — шлюз Track B
SCOPE_SERVICE_URL=http://bridge-scope-service:3000
SCOPE_SERVICE_SHARED_SECRET=<generate>

AGENT_STATUS_SERVICE_URL=http://agent-status-service:3000
AGENT_STATUS_SHARED_SECRET=<generate>

GITHUB_INTEGRATION_SERVICE_URL=http://github-integration-service:3000
GITHUB_INTEGRATION_SHARED_SECRET=<generate>

USER_PROFILE_SERVICE_URL=http://user-profile-service:3000
USER_PROFILE_SHARED_SECRET=<generate>   # Нужен для backward-compat REST-путей; /mcp использует JWT

LEARNING_CONTEXT_SERVICE_URL=http://learning-context-service:3000
LEARNING_CONTEXT_SHARED_SECRET=<generate>   # Нужен для backward-compat REST-путей; /mcp использует JWT

# Новые секреты (добавлены WP-410):
GITHUB_WEBHOOK_SECRET=<generate>   # HMAC-валидация вебхуков GitHub в шлюзе (CF Web Crypto, constant-time)
```

> **Track A (Россия):** шлюз на Cloudflare Workers использует `wrangler secret put` с публичными URL-адресами Railway (`*.up.railway.app`). Тот же формат пар «URL + SHARED_SECRET», другие значения.

> **Стыковка авторизации:** шлюз шлёт сервису `Authorization: Bearer <SERVICE>_SHARED_SECRET` + заголовок `X-User-Id` (идентификатор пользователя, уже проверенный шлюзом). Сервис читает тот же ключ из своей переменной `GATEWAY_SHARED_SECRET`.
>
> **Mode A (JWT-прямая авторизация, WP-410 Ф4б, ADR-IWE-017):** `user-profile-service` и `learning-context-service` теперь имеют эндпоинт `POST /mcp`, который принимает Ory JWT напрямую (без shared-secret). Шлюз вызывает `buildJourneyState` и `getOnboardingContext` через этот эндпоинт, передавая JWT пользователя как `Authorization: Bearer`. Shared-secret пары остаются для backward-compat REST-путей (inline-обработчики шлюза + BYOK/LLM-ключи) до завершения полной миграции (Ф6 WP-410).
>
> **Проверка здоровья:** адреса `USER_PROFILE_*` и `LEARNING_CONTEXT_*` обязательны — без них `/health` шлюза отдаёт 503. Остальные три пары пока проверяются мягче.

### 2.2 Оставшиеся базы в шлюзе — только Track A (Россия)

| Переменная | Зачем нужна | Статус для Track B |
|------------|-------------|-------------------|
| `DATABASE_URL` | База персон: подключение источников, вебхук GitHub, страница Scout, синхронизация форков | **Убрана полностью** — всё делегировано `github-integration-service` и `user-profile-service` |
| `SUBSCRIPTION_DATABASE_URL` | Хук выдачи токенов читает подписку, чтобы вшить признак в токен | **Убрана с пути маршрутизации** — остаётся только в хуке `/hydra-hook/token` (эндпоинт выдачи, не роутер). См. раздел 4 |
| `INDICATORS_DATABASE_URL` | Запись стартовых прав агента при онбординге | **Убрана** — делегировано `bridge-scope-service` + `agent-status-service` |

> **Принцип шлюза:** конфиг = только URL-адреса сервисов + ключи. Базы данных на пути маршрутизации отсутствуют. Хук `/hydra-hook/token` — исключение, зафиксированное в ADR DP.IWE.003 §10 как легитимный остаток.

### 2.3 Переменные окружения для GKE-сервисов (Secret Manager / Cloud SQL)

<details>
<summary><b>bridge-scope-service</b></summary>

- `DATABASE_URL` — база indicators (обязательно)
- `GATEWAY_SHARED_SECRET` — авторизация от шлюза (обязательно)
- `PORT` — по умолчанию 3000

</details>

<details>
<summary><b>agent-status-service</b></summary>

- `DATABASE_URL` — база indicators (обязательно)
- `GATEWAY_SHARED_SECRET` — авторизация от шлюза (обязательно)
- `PORT` — по умолчанию 3000
- `GHOST_TTL_HOURS` — опционально

</details>

<details>
<summary><b>github-integration-service</b></summary>

- `DATABASE_URL` — база персон (обязательно)
- `ORY_CLIENT_SECRET` — интроспекция токенов Ory (обязательно)
- `GATEWAY_PUBLIC_ORIGIN` — публичный адрес шлюза (обязательно)
- `GATEWAY_SHARED_SECRET` — авторизация от шлюза
- GitHub App: `GITHUB_APP_ID`, `GITHUB_APP_PRIVATE_KEY`, `GITHUB_WEBHOOK_SECRET`
- GitHub OAuth: `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`
- Переиндексация: `KNOWLEDGE_REINDEX_SECRET`, `PERSONAL_REINDEX_SECRET`
- Уведомления боту: `BOT_NOTIFY_URL`, `BOT_NOTIFY_SECRET`
- Рабочая тетрадь бота: `BOT_WORKBOOK_WEBHOOK_URL`, `BOT_WORKBOOK_WEBHOOK_SECRET`
- Прочее: `AGENT_RUNNER_URL`, `PROXY_SHARED_SECRET`, `PERSONAL_KNOWLEDGE_MCP_URL`, `KNOWLEDGE_MCP_URL`, `LEARNING_DATABASE_URL`, `KNOWLEDGE_DB_SCHEMA`

</details>

<details>
<summary><b>user-profile-service</b></summary>

- `DATABASE_URL` — база персон (обязательно)
- `GATEWAY_SHARED_SECRET` — авторизация от шлюза для backward-compat REST-путей (обязательно)
- `ORY_URL` — адрес Ory для JWKS-верификации в `/mcp` эндпоинте (обязательно для Mode A, WP-410 Ф4б)
- `BYOK_KEK` — ключ для расшифровки пользовательских ключей к моделям
- `BOT_NOTIFY_URL` + `BOT_NOTIFY_SECRET` — для уведомлений боту
- `KNOWLEDGE_DB_SCHEMA` — по умолчанию `knowledge`

</details>

<details>
<summary><b>learning-context-service</b></summary>

- `GATEWAY_SHARED_SECRET` — авторизация от шлюза для backward-compat REST-путей (обязательно)
- `ORY_URL` — адрес Ory для JWKS-верификации в `/mcp` эндпоинте (обязательно для Mode A, WP-410 Ф4б)
- `LEARNING_DATABASE_URL` — база learning (или `DATABASE_URL`, сервис сам выводит адрес)
- `PORT` — по умолчанию 3000
- **Зависимости БД (применить миграции на learning):** `learning.consent_grant` (`neon-migrations/mvp/229`, `261`), `cognitive.brief` (схема `cognitive` в той же базе learning, `neon-migrations/mvp/230`). Без них `/grant-consent` и `/cognitive-brief` падают.

</details>

</details>

<details>
<summary><b>3. План развёртывания на GKE</b></summary>

### До первого деплоя

1. **Добавить Dockerfile (3 сервиса без контейнера):** три сервера знаний (`knowledge-mcp`, `digital-twin-mcp`, `personal-knowledge-mcp`). Для GKE нужны Dockerfile и адаптация (среда Cloudflare Workers ≠ Node-контейнер). Все 5 вспомогательных сервисов Dockerfile уже имеют.
2. **Применить миграции БД:**
   - `262-scope-rls.sql` на базу indicators (`neon-migrations/mvp/262-scope-rls.sql`) — нужен для `bridge-scope-service`.
   - `consent_grant` (`229`, `261`) + `cognitive.brief` (`230`) на базу learning — нужны для `learning-context-service`.
3. **Короткое время жизни токена Ory = 5 мин** — после этого подписку можно убрать с пути маршрутизации шлюза.

### Порядок деплоя

**Сначала — 3 сервера знаний:**

1. **knowledge-mcp** → контейнеризация + GKE → проверить поиск
2. **digital-twin-mcp** → контейнеризация + GKE → проверить чтение двойника
3. **personal-knowledge-mcp** → контейнеризация + GKE → проверить личные знания

**Затем — 5 вспомогательных сервисов** (каждый → GKE + Secret Manager, проверить `/health`):

4. **bridge-scope-service** — дополнительно проверить, что работает изоляция строк по пользователю (`SET LOCAL app.user_id`)
5. **agent-status-service**
6. **github-integration-service** — дополнительно проверить доставку вебхука (адрес обратного вызова GitHub App = шлюз, он проксирует)
7. **user-profile-service** — проверить `/tier?userId=<uuid>`
8. **learning-context-service** — проверить `/consent?userId=<uuid>` и `/cognitive-brief?userId=<uuid>`

**Последним — шлюз:**

9. **gateway-mcp** — прописать адреса: серверов знаний (на внутренние адреса кластера) + все пары «адрес + ключ» вспомогательных сервисов. Проверить `/health` → `{"ok":true}` (503 = сигнал «сервисы не подключены») и что вызовы проксируются (бриф, тариф, согласие, состояние пути, вход через GitHub, поиск).

> **Порядок важен:** поднять все 8 сервисов + миграции **первыми**, адреса в шлюз — **последним шагом**. Env-переменные применяются через GKE SecretManager / ConfigMap; до их установки `/health` остаётся 503.

### Приватная сеть

Все 8 сервисов деплоятся в **один GKE-кластер** (europe-west4) → внутренние адреса недоступны извне → авторизация общим ключом + заголовком `X-User-Id` безопасна без mTLS. Для серверов знаний это заодно убирает их публичные адреса за периметр кластера.

</details>

<details>
<summary><b>4. Известные ограничения и соответствие тесту Андрея</b></summary>

**Принцип проверки шлюза:** «Посмотри какие конфиги у gateway. Если там три URL тех MCP-серверов, которые он объединяет — всё здорово. Если там начинаются базы данных — значит gateway берёт на себя дополнительную логику».

**Соответствие:**
- ✅ **Путь маршрутизации чист.** Конфиг Track B = 3 URL серверов знаний + 5 URL вспомогательных сервисов + парные ключи. Базы данных на пути маршрутизации отсутствуют. `DATABASE_URL` полностью удалена из шлюза, включая объявление типа `Env` (рефакторинг 2026-06-10, Track A gateway-mcp).
- ✅ **BYOK-управление** (`list/grant/revoke_llm_key`) вынесено в `user-profile-service` (эндпоинты `/llm-keys`). Шлюз только проксирует.
- ⚠️ **Хук выдачи токенов** (`/hydra-hook/token`) — единственное место, где шлюз читает базу (`SUBSCRIPTION_DATABASE_URL`). Это **эндпоинт выдачи токена**, не путь маршрутизации. Зафиксировано в ADR DP.IWE.003 §10 как легитимный остаток: вынос хука усложнит архитектуру без выигрыша, потому что он не на пути обработки пользовательских запросов.
- ✅ **Try1 (opaque-токены)** тоже не читает базу подписок. Вместо этого спрашивает тир у `user-profile-service` (`/tier`) и считает подписку оттуда: T2 = подписка есть, T1 = нет.
- ✅ **Try2 (Kratos-сессии)** удалён полностью — подтверждено, что никакой клиент не использует Kratos session token при обращении к шлюзу.

**Прогресс WP-410 (обновлено 2026-06-10):**
- ✅ **Гидра-хук инжектирует `ext.tier` для ВСЕХ тиров T0-T4** (commit `52863d3`). Ранее только T3/T4 — остальные вызывали DB-fallback в `validateOryToken` Try 0. Теперь tier из claim; DB-fallback убран из Try 0 полностью.
- ✅ **`buildJourneyState` и `getOnboardingContext` переведены на Mode A** (commit `9eb2b45`, WP-410 Ф4б). Шлюз вызывает `POST /mcp` у `user-profile-service` и `learning-context-service` через `callMcpTool` с JWT пользователя — shared-secret на этом пути больше не нужен.
- ✅ **GITHUB_WEBHOOK_SECRET добавлен** (commit `52863d3`). HMAC-валидация вебхуков GitHub в шлюзе через CF Workers Web Crypto API (constant-time `crypto.subtle.verify`).
- ⚠️ **Оставшиеся inline-обработчики** (`get_user_context`, `grant_consent`, BYOK/LLM-ключи, Hermes-контекст, Try 1) по-прежнему используют shared-secret REST API для backward-compat. Полный переход на Mode A — Ф6 WP-410 (отложена, требует миграции каждого inline-обработчика).

**Что это значит для Track B:** при пересоздании шлюза в GKE переменная `SUBSCRIPTION_DATABASE_URL` всё ещё нужна (для хука), но она не нарушает тест Андрея — хук ≠ роутер. Новые переменные `ORY_URL` нужны в `user-profile-service` и `learning-context-service` для Mode A `/mcp` эндпоинтов.

</details>

<details>
<summary><b>5. Проверка после деплоя (smoke)</b></summary>

```bash
# Здоровье шлюза Track B (503 → {"ok":true} после подключения сервисов)
curl https://mcp-world.aisystant.com/health | jq .

# Здоровье серверов знаний (внутри кластера)
curl http://knowledge-mcp/health
curl http://digital-twin-mcp/health
curl http://personal-knowledge-mcp/health

# Здоровье вспомогательных сервисов (внутри кластера или через port-forward)
curl http://bridge-scope-service/health
curl http://agent-status-service/health
curl http://github-integration-service/health
curl http://user-profile-service/health
curl http://learning-context-service/health

# Проксирование через шлюз Track B (с токеном)
curl -H "Authorization: Bearer <JWT>" https://mcp-world.aisystant.com/api/v1/user-context
```

> **Track A (Россия):** smoke-адрес шлюза — `https://mcp.aisystant.com/health` (Cloudflare Workers → Railway). Независимый от Track B.

**Содержательная проверка (не только «не 5xx»):** бриф возвращает данные известного пользователя (а не «service not configured»); состояние пути развития возвращает корректную ступень (а не «согласие не дано для всех»).

</details>

