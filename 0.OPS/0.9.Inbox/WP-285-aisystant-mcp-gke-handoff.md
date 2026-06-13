---
type: handoff
status: active
created: 2026-06-10
updated: 2026-06-13
owner: Андрей
next_review: 2026-06-27
related: [WP-415-russia-world-split-concept.md]
---

# Aisystant MCP — развёртывание в мировой инфраструктуре (GKE)

> Плейбук пересоздания Aisystant MCP на Google Kubernetes Engine для мировых пользователей (Track B). Текущие российские экземпляры (Track A) работают отдельно на Cloudflare Workers + Railway и не затрагиваются.
> Все репозитории приватные (`aisystant/*`).
> Кто разрабатывает, принимает, разворачивает — см. [WP-415 §6](WP-415-russia-world-split-concept.md).

**Что разворачиваем (Track B):** отдельный экземпляр шлюза в GKE + 8 сервисов за ним + Cloud SQL. Свой домен (например, `mcp-world.aisystant.com`), свои переменные окружения, свои бэкенды. От Track A независим.

**Принцип шлюза.** Aisystant MCP = это **шлюз** (`gateway-mcp`) — единственная точка подключения внешних клиентов (claude.ai, Claude Code, VS Code). Задача одна: принять запрос и отмаршрутизировать на нужный сервис. В конфиге шлюза — только адреса сервисов + собственный ключ подписи. Без баз данных на пути маршрутизации, без общих паролей к сервисам. Прикладная логика живёт в сервисах за шлюзом.

<details open>
<summary><b>1. Карта сервисов</b></summary>

За шлюзом — два класса сервисов: серверы знаний и вспомогательные сервисы.

**Шлюз**

| Сервис | Репозиторий | Что в конфиге |
|--------|-------------|---------------|
| **gateway-mcp** | aisystant/gateway-mcp | Только адреса 8 сервисов + ключ подписи. Без баз на пути маршрутизации |

**Серверы знаний** (шлюз раздаёт им запросы)

| Сервис | Что делает | Контейнер |
|--------|------------|-----------|
| **knowledge-mcp** | Поиск по базе знаний | ❌ нужен Dockerfile (сейчас Cloudflare Worker) |
| **digital-twin-mcp** | Цифровой двойник пользователя | ❌ нужен Dockerfile |
| **personal-knowledge-mcp** | Личные знания пользователя | ❌ нужен Dockerfile |

**Вспомогательные сервисы** (прикладная логика за шлюзом, все на TypeScript/Node, с Dockerfile и README)

| Сервис | Что делает |
|--------|------------|
| **user-profile-service** | Профиль: контекст, тариф, ключи к моделям (BYOK), уведомления боту |
| **learning-context-service** | Согласие на обработку данных, когнитивный бриф, состояние онбординга |
| **github-integration-service** | Вебхуки GitHub App, вход через GitHub, создание репозиториев |
| **agent-status-service** | Доска статусов агентов |
| **bridge-scope-service** | Проверка прав агента на запись в репозиторий пользователя |

> После переезда адреса серверов знаний в шлюзе указывают на внутренние адреса кластера (ClusterIP), не на Cloudflare.

</details>

<details>
<summary><b>2. Конфигурация и авторизация</b></summary>

### 2.1 Авторизация: сервисы проверяют личность сами, общих паролей нет

Шлюз не хранит общих паролей к сервисам. Личность доходит до сервиса одним из двух способов, оба проверяются самим сервисом:

1. **Личный токен пользователя (Ory JWT).** Шлюз пробрасывает токен как `Authorization: Bearer`; сервис проверяет его по JWKS Ory (`ORY_URL`). Так работают серверы знаний, `user-profile`, `learning-context`, `agent-status`.
2. **Подпись шлюза (короткоживущая RS256-подпись).** Для путей без пользовательского JWT (непрозрачные OAuth-токены коннектора) и для `github-integration` шлюз выписывает подпись своим приватным ключом; сервис проверяет её по публичному ключу шлюза (`GATEWAY_JWKS_URL`). Подпись живёт 60 секунд, привязана к адресату (`audience`) и назначению (`purpose`).

> Шлюз публикует публичный ключ на `/<gateway>/.well-known/jwks.json`. Утёкший публичный ключ подделать подпись не позволяет — это не общий пароль.

### 2.2 Переменные окружения — шлюз (Track B)

```bash
# Адреса 8 сервисов (внутренние адреса кластера)
KNOWLEDGE_MCP_URL / DIGITAL_TWIN_MCP_URL / PERSONAL_KNOWLEDGE_MCP_URL
USER_PROFILE_SERVICE_URL / LEARNING_CONTEXT_SERVICE_URL
GITHUB_INTEGRATION_SERVICE_URL / AGENT_STATUS_SERVICE_URL / SCOPE_SERVICE_URL

# Ключ подписи шлюза (для подписи вызовов в сервисы)
GATEWAY_SIGNING_PRIVATE_JWK   # приватный RS256-ключ
GATEWAY_SIGNING_KID           # идентификатор ключа (публикуется в JWKS)

GATEWAY_PUBLIC_ORIGIN         # публичный адрес шлюза
GITHUB_WEBHOOK_SECRET         # HMAC-валидация вебхуков GitHub
SUBSCRIPTION_DATABASE_URL     # ТОЛЬКО для хука выдачи токена (см. раздел 4), не на пути маршрутизации
# + параметры OAuth-сервера (Ory client) для входа клиентов
```

### 2.3 Переменные окружения — сервисы

Каждый сервис проверяет личность сам (`ORY_URL` и/или `GATEWAY_JWKS_URL`) и держит свою базу.

<details>
<summary><b>user-profile-service</b></summary>

- `DATABASE_URL` — база персон
- `ORY_URL` — проверка личного токена пользователя
- `GATEWAY_JWKS_URL` — проверка подписи шлюза (путь непрозрачных токенов)
- `BYOK_KEK` — расшифровка пользовательских ключей к моделям
- `BOT_NOTIFY_URL` + `BOT_NOTIFY_SECRET` — уведомления боту
- `KNOWLEDGE_DB_SCHEMA` — по умолчанию `knowledge`

</details>

<details>
<summary><b>learning-context-service</b></summary>

- `LEARNING_DATABASE_URL` — база learning (или `DATABASE_URL`)
- `ORY_URL` — проверка личного токена пользователя
- `GATEWAY_JWKS_URL` — проверка подписи шлюза
- `PORT` — по умолчанию 3000
- Миграции на базу learning: `learning.consent_grant` (`neon-migrations/mvp/229`, `261`), `cognitive.brief` (`230`). Без них `/grant-consent` и `/cognitive-brief` падают.

</details>

<details>
<summary><b>github-integration-service</b></summary>

- `DATABASE_URL` — база персон
- `ORY_CLIENT_SECRET` — интроспекция токенов Ory
- `GATEWAY_PUBLIC_ORIGIN` — публичный адрес шлюза
- `GATEWAY_JWKS_URL` — проверка подписи шлюза (шлюз авторизуется в этот сервис только подписью)
- GitHub App: `GITHUB_APP_ID`, `GITHUB_APP_PRIVATE_KEY`, `GITHUB_WEBHOOK_SECRET`
- GitHub OAuth: `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`
- Переиндексация: `KNOWLEDGE_REINDEX_SECRET`, `PERSONAL_REINDEX_SECRET`
- Уведомления боту: `BOT_NOTIFY_URL`, `BOT_NOTIFY_SECRET`, `BOT_WORKBOOK_WEBHOOK_URL`, `BOT_WORKBOOK_WEBHOOK_SECRET`
- Прочее: `AGENT_RUNNER_URL`, `PERSONAL_KNOWLEDGE_MCP_URL`, `KNOWLEDGE_MCP_URL`, `LEARNING_DATABASE_URL`, `KNOWLEDGE_DB_SCHEMA`

</details>

<details>
<summary><b>agent-status-service</b></summary>

- `DATABASE_URL` — база indicators
- `ORY_URL` — проверка личного токена пользователя
- `PORT` — по умолчанию 3000
- `GHOST_TTL_HOURS` — опционально

</details>

<details>
<summary><b>bridge-scope-service</b></summary>

- `DATABASE_URL` — база indicators
- `PORT` — по умолчанию 3000
- Авторизация: сейчас единственный сервис на общем ключе от шлюза; проверку прав переносят внутрь `personal-knowledge-mcp`. Для Track B уточнить у владельца РП-410, разворачивать ли как отдельный сервис.

</details>

</details>

<details>
<summary><b>3. Порядок развёртывания</b></summary>

**До первого деплоя**

1. Добавить Dockerfile трём серверам знаний (среда Cloudflare Workers ≠ Node-контейнер). У 5 вспомогательных сервисов Dockerfile уже есть.
2. Применить миграции БД: `262-scope-rls.sql` на базу indicators; `consent_grant` (`229`, `261`) + `cognitive.brief` (`230`) на базу learning.
3. Время жизни токена Ory = 5 минут.

**Порядок деплоя** (все 8 сервисов + миграции — первыми, адреса в шлюз — последними)

1. Серверы знаний → контейнеризация + GKE → проверить поиск / двойник / личные знания.
2. Вспомогательные сервисы → GKE + Secret Manager → проверить `/health` у каждого.
3. **Шлюз последним** → прописать адреса сервисов (внутренние адреса кластера) + ключ подписи → `/health` должен вернуть `{"ok":true}` (503 = сервисы ещё не подключены), вызовы проксируются.

**Приватная сеть.** Все 8 сервисов — в одном GKE-кластере (europe-west4), внутренние адреса недоступны извне, у серверов знаний пропадают публичные адреса за периметр кластера.

</details>

<details>
<summary><b>4. Чистота шлюза (тест Андрея)</b></summary>

**Принцип:** посмотри конфиг шлюза. Только адреса сервисов + ключ подписи → правильный шлюз. Появились базы или прикладная логика → шлюз взял лишнее.

- ✅ Путь маршрутизации чист: 3 адреса серверов знаний + 5 адресов вспомогательных сервисов + ключ подписи. Баз данных на пути нет.
- ✅ Управление ключами к моделям (BYOK) — в `user-profile-service`, шлюз только проксирует.
- ✅ Авторизация без общих паролей: сервисы проверяют личность сами (раздел 2.1).
- ⚠️ **Единственное исключение** — хук выдачи токена (`/hydra-hook/token`) читает базу подписок (`SUBSCRIPTION_DATABASE_URL`), чтобы вшить тариф в токен. Это эндпоинт выдачи, не путь маршрутизации. Зафиксировано в ADR DP.IWE.003 §10 как легитимный остаток.

</details>

<details>
<summary><b>5. Проверка после деплоя</b></summary>

```bash
# Шлюз (503 → {"ok":true} после подключения сервисов)
curl https://mcp-world.aisystant.com/health | jq .

# Сервисы (внутри кластера)
curl http://knowledge-mcp/health      ; curl http://digital-twin-mcp/health
curl http://personal-knowledge-mcp/health
curl http://user-profile-service/health   ; curl http://learning-context-service/health
curl http://github-integration-service/health
curl http://agent-status-service/health   ; curl http://bridge-scope-service/health
```

**Поинструментная проверка с токеном (обязательно — `/health`=200 не доказывает, что инструмент работает):** прогнать живой вызов по каждому семейству (поиск, двойник, личные знания, тариф, бриф, статус агента, вход через GitHub). Бриф возвращает данные известного пользователя, состояние пути — корректную ступень.

</details>
