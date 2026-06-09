# Aisystant MCP — перенос в мировую инфраструктуру (GKE)

> Карта сервисов, конфигурация и план развёртывания для пересоздания Aisystant MCP в новой (мировой) инфраструктуре на Google Kubernetes Engine.
> Текущие (российские) экземпляры остаются работать отдельно — этот документ описывает, как поднять те же сервисы заново для новых пользователей.
> Все репозитории приватные (`aisystant/*`). Актуально на 2026-06-09.

> **Принцип шлюза.** Aisystant MCP = это **шлюз** (`gateway-mcp`, `mcp.aisystant.com`) — единственная точка, к которой подключаются внешние клиенты (claude.ai, Claude Code, VS Code). Задача шлюза одна: принять запрос и отмаршрутизировать его на нужный сервер. В его конфиге должны быть только адреса серверов, которые он объединяет (плюс парные ключи для них) — без баз данных. Прикладная логика живёт в отдельных сервисах за шлюзом, а не в самом шлюзе.

<details open>
<summary><b>1. Карта сервисов</b></summary>

За шлюзом стоят два класса сервисов: серверы знаний (backend-MCP) и вспомогательные сервисы (прикладная логика). Шлюз раздаёт запросы серверам знаний и проксирует часть вызовов во вспомогательные сервисы.

**A. Шлюз**

| Сервис | Репозиторий | Платформа | Статус |
|--------|-------------|-----------|--------|
| **gateway-mcp** | https://github.com/aisystant/gateway-mcp | Cloudflare Worker | В проде. Авто-деплой при push в `main`. `/health` отдаёт 503, пока сервисы ниже не подключены |

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
| **bridge-scope-service** | https://github.com/aisystant/bridge-scope-service | Проверяет, можно ли агенту писать в репозиторий пользователя | `POST /check-scope`, `GET /health` | Dockerfile ✅, README ✅ |
| **agent-status-service** | https://github.com/aisystant/agent-status-service | Доска статусов агентов (кто чем занят, какие файлы трогает) | `POST /api/v1/status`, `GET /api/v1/status` (фильтр `?repo=`), `GET /health` | Dockerfile ❌ (добавить), README ✅ |
| **github-integration-service** | https://github.com/aisystant/github-integration-service | Вебхуки GitHub App, вход через GitHub, создание репозиториев пользователей | `POST /github/webhook`; `/api/v1/github/*` (`connect`/`status`/`disconnect`/`repo`); `/github/*` (`install`/`setup`/`create-repo`/`repo-callback`); `GET /health` | Dockerfile ✅, README ✅ |
| **user-profile-service** | https://github.com/aisystant/user-profile-service | Профиль пользователя: контекст, тариф, ключи к моделям (BYOK), уведомления боту | `GET /user-context`, `GET /tier`, `POST /byok`, `POST /notify-bot`, `GET /github-connected`, `GET /onboarding-context` | Dockerfile ✅, README ✅ |
| **learning-context-service** | https://github.com/aisystant/learning-context-service | Согласие на обработку данных, когнитивный бриф, состояние онбординга | `GET /consent`, `POST /grant-consent`, `GET /cognitive-brief`, `GET /onboarding-state` | Dockerfile ✅, README ✅ |

> **Итог по конфигу шлюза:** после выноса логики шлюз держит только адреса — 3 сервера знаний (B) + 5 вспомогательных сервисов (C) = 8 адресов с парными ключами, без баз данных на пути маршрутизации (известные исключения — в разделе 4).

</details>

<details>
<summary><b>2. Конфигурация: секреты и переменные окружения</b></summary>

### 2.1 Шлюз — адреса и ключи вспомогательных сервисов

Шлюз остаётся на Cloudflare Workers и проксирует часть вызовов в GKE-сервисы. Для каждого сервиса — пара «адрес + общий ключ»:

```bash
# bridge-scope
wrangler secret put SCOPE_SERVICE_URL            # внутренний адрес сервиса в кластере
wrangler secret put SCOPE_SERVICE_SHARED_SECRET

# agent-status
wrangler secret put AGENT_STATUS_SERVICE_URL
wrangler secret put AGENT_STATUS_SHARED_SECRET

# github-integration
wrangler secret put GITHUB_INTEGRATION_SERVICE_URL
wrangler secret put GITHUB_INTEGRATION_SHARED_SECRET

# user-profile
wrangler secret put USER_PROFILE_SERVICE_URL
wrangler secret put USER_PROFILE_SHARED_SECRET

# learning-context
wrangler secret put LEARNING_CONTEXT_SERVICE_URL
wrangler secret put LEARNING_CONTEXT_SHARED_SECRET
```

> **Стыковка авторизации:** шлюз шлёт сервису `Authorization: Bearer <SERVICE>_SHARED_SECRET` + заголовок `X-User-Id` (идентификатор пользователя, уже проверенный шлюзом). Сервис читает тот же ключ из своей переменной `GATEWAY_SHARED_SECRET`.
>
> **Проверка здоровья:** адреса `USER_PROFILE_*` и `LEARNING_CONTEXT_*` обязательны — без них `/health` шлюза отдаёт 503. Остальные три пары пока проверяются мягче.

### 2.2 Оставшиеся базы в шлюзе (по разделу 4)

| Переменная | Зачем нужна | Когда уйдёт |
|------------|-------------|-------------|
| `DATABASE_URL` | База персон: подключение источников, вебхук GitHub, страница Scout, синхронизация форков, управление ключами BYOK | После выноса управления BYOK (раздел 4) |
| `SUBSCRIPTION_DATABASE_URL` | Хук выдачи токенов читает подписку, чтобы вшить признак в токен | После установки короткого времени жизни токена в Ory (5 мин) |
| `INDICATORS_DATABASE_URL` | Запись стартовых прав агента при онбординге | После того как bridge-scope-service получит эндпоинт выдачи прав |

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
- `GATEWAY_SHARED_SECRET` — авторизация от шлюза (обязательно)
- `BYOK_KEK` — ключ для расшифровки пользовательских ключей к моделям
- `BOT_NOTIFY_URL` + `BOT_NOTIFY_SECRET` — для уведомлений боту
- `KNOWLEDGE_DB_SCHEMA` — по умолчанию `knowledge`

</details>

<details>
<summary><b>learning-context-service</b></summary>

- `GATEWAY_SHARED_SECRET` — авторизация от шлюза (обязательно)
- `LEARNING_DATABASE_URL` — база learning (или `DATABASE_URL`, сервис сам выводит адрес)
- `PORT` — по умолчанию 3000
- **Зависимости БД (применить миграции на learning):** `learning.consent_grant` (`neon-migrations/mvp/229`, `261`), `cognitive.brief` (схема `cognitive` в той же базе learning, `neon-migrations/mvp/230`). Без них `/grant-consent` и `/cognitive-brief` падают.

</details>

</details>

<details>
<summary><b>3. План развёртывания на GKE</b></summary>

### До первого деплоя

1. **Добавить Dockerfile (4 сервиса без контейнера):** `agent-status-service` + три сервера знаний (`knowledge-mcp`, `digital-twin-mcp`, `personal-knowledge-mcp`). У трёх серверов знаний сверх контейнера нужна адаптация со среды Cloudflare Workers на Node-контейнер.
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

> **Порядок важен:** поднять все 8 сервисов + миграции **первыми**, адреса в шлюз — **последним шагом**. Секреты `wrangler secret put` применяются к уже задеплоенному шлюзу сразу; до их установки `/health` остаётся 503.

### Приватная сеть

Все 8 сервисов деплоятся в **один GKE-кластер** (europe-west4) → внутренние адреса недоступны извне → авторизация общим ключом + заголовком `X-User-Id` безопасна без mTLS. Для серверов знаний это заодно убирает их публичные адреса за периметр кластера.

</details>

<details>
<summary><b>4. Известные ограничения</b></summary>

Шлюз = маршрутизатор + авторизация (Ory JWT) + раздача запросов серверам знаний. Путь маршрутизации почти чист от баз, кроме двух мест:

- **Хук выдачи токенов** (`/hydra-hook/token`) — читает базу подписок, чтобы вшить признак подписки в токен. Это эндпоинт выдачи токена, не путь маршрутизации — оставлен осознанно.
- **Управление ключами BYOK** (`list`/`grant`/`revoke` ключей к моделям) — пока ходит в базу напрямую из шлюза. Это последний кусок прикладной логики на пути маршрутизации; план — вынести его в `user-profile-service` или оставить как осознанное исключение.

</details>

<details>
<summary><b>5. Проверка после деплоя (smoke)</b></summary>

```bash
# Здоровье шлюза (503 → {"ok":true} после подключения сервисов)
curl https://mcp.aisystant.com/health | jq .

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

# Проксирование через шлюз (с токеном)
curl -H "Authorization: Bearer <JWT>" https://mcp.aisystant.com/api/v1/user-context
```

**Содержательная проверка (не только «не 5xx»):** бриф возвращает данные известного пользователя (а не «service not configured»); состояние пути развития возвращает корректную ступень (а не «согласие не дано для всех»).

</details>

---

> **Безопасность документа:** проверен на значения ключей/токенов/строк подключения — значений нет, только имена переменных. Безопасен для приватного репозитория. Не выкладывать в публичный доступ как есть: содержит инвентарь имён секретов и карту архитектуры.
