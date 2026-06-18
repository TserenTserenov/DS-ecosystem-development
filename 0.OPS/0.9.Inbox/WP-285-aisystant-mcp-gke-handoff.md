# Aisystant MCP — развёртывание в мировой инфраструктуре (GKE)

**Что разворачиваем (Track B):** отдельный экземпляр шлюза в GKE + сервисы за ним + Cloud SQL (europe-west4). Домен уточняется при согласовании именования (Р-22-2: `aisystant.com` → мировая платформа). От Track A независим.

**Track A остаётся как есть** (Neon + Railway + VK Cloud Ory + YooKassa) — Р-инв-1. Ильшат принимает Track A (Р-15-1). Track B стартует **пустым** — данные не мигрируются (Р-инв-2).

**Принцип шлюза.** Aisystant MCP = **шлюз** ([`gateway-mcp`](https://github.com/aisystant/gateway-mcp)) — единственная точка подключения внешних клиентов (claude.ai, Claude Code, VS Code). В конфиге шлюза — только адреса сервисов + ключ подписи. Без баз на пути маршрутизации, без общих паролей. Прикладная логика живёт в сервисах за шлюзом.

<details open>
<summary><b>§1. Карта сервисов MCP</b></summary>

За шлюзом — два класса сервисов: серверы знаний (сейчас CF Workers, нужен Dockerfile для GKE) и вспомогательные Node.js сервисы (Dockerfile уже есть у всех).

**Шлюз**

| Сервис | Репозиторий | Track A URL | Что в конфиге |
|--------|-------------|-------------|---------------|
| **gateway-mcp** | [aisystant/gateway-mcp](https://github.com/aisystant/gateway-mcp) | https://mcp.aisystant.com | Только адреса 8 сервисов + ключ подписи. Без баз на пути маршрутизации |

**Серверы знаний** (CF Workers → нужен Dockerfile для GKE)

| Сервис | Репозиторий | Track A URL | Что делает |
|--------|-------------|-------------|------------|
| **knowledge-mcp** | [aisystant/knowledge-mcp](https://github.com/aisystant/knowledge-mcp) | https://knowledge-mcp.aisystant.workers.dev | Поиск по базе знаний (Pack, guides, граф концептов) |
| **digital-twin-mcp** | [aisystant/digital-twin-mcp](https://github.com/aisystant/digital-twin-mcp) | https://digital-twin-mcp.aisystant.workers.dev | Цифровой двойник пользователя, показатели прогресса |
| **personal-knowledge-mcp** | [aisystant/personal-knowledge-mcp](https://github.com/aisystant/personal-knowledge-mcp) | https://personal-knowledge-mcp.aisystant.workers.dev | Личная база знаний пользователя |

**Вспомогательные сервисы** (Node.js, Dockerfile есть)

| Сервис | Репозиторий | Track A URL | Что делает |
|--------|-------------|-------------|------------|
| **user-profile-service** | [aisystant/user-profile-service](https://github.com/aisystant/user-profile-service) | https://user-profile-service-production.up.railway.app | Профиль: контекст, тариф, BYOK-ключи, уведомления боту |
| **learning-context-service** | [aisystant/learning-context-service](https://github.com/aisystant/learning-context-service) | https://learning-context-service-production.up.railway.app | Согласие на данные, когнитивный бриф, состояние онбординга |
| **github-integration-service** | [aisystant/github-integration-service](https://github.com/aisystant/github-integration-service) | https://github-integration-service-production.up.railway.app | Вебхуки GitHub App, вход через GitHub, создание репозиториев |
| **agent-status-service** | [aisystant/agent-status-service](https://github.com/aisystant/agent-status-service) | TBD (не задеплоен) | Доска статусов агентов |
| ~~bridge-scope-service~~ | — | — | **Не разворачивать** — guard перенесён в `personal-knowledge-mcp` (`scope.ts`, WP-410 ✅ 17 июня) |

**Итого:** 8 сервисов за шлюзом (3 знания + 4 вспомогательных). bridge-scope устарел.

</details>

<details>
<summary><b>§2. Авторизация и IdP (Ory Kratos + Hydra)</b></summary>

**Решение (Р-22-5):** Ory остаётся для Track B. Zitadel отклонён — нет RFC 7591 (DCR) и RFC 8707 (Resource Indicators), что ломает интеграцию с claude.ai/ChatGPT. Conjunctive screening: Ory 0×, Zitadel 1× ([WP-285-ory-vs-zitadel-emogssb.md](WP-285-ory-vs-zitadel-emogssb.md)).

**Что разворачивать (Р-22-5а):** Только Kratos + Hydra на GKE EU — отдельный инстанс от Track A VK Cloud, своя БД. Keto и Oathkeeper не нужны — права через таблицы в БД.

**Методы входа для Track B (Р-22-8):**
- Email + Magic Link (обязательно)
- Sign in with Google — OIDC federation поверх IdP (Р-22-6; IdP обязателен, Google не заменяет)
- Sign in with Apple (обязательно при iOS-приложении — App Store policy)
- Sign in with GitHub (опционально, developer-аудитория)
- Passkey/WebAuthn (на будущее)

**Для справки — Track A (Р-22-9):** Email + Magic Link, Yandex ID, Telegram Login Widget, VK ID (опционально). Ory поддерживает все через OIDC-providers.

**Как шлюз передаёт личность** (без общих паролей к сервисам):

1. **Личный токен пользователя (Ory JWT).** Шлюз форвардит `Authorization: Bearer`; сервис проверяет по JWKS Ory (`ORY_URL`). Так работают: knowledge-mcp, digital-twin-mcp, personal-knowledge-mcp, user-profile, learning-context, agent-status.
2. **Подпись шлюза (RS256, 60 сек).** Для путей без пользовательского JWT (непрозрачные OAuth-токены коннектора) и для github-integration. Сервис проверяет по `GATEWAY_JWKS_URL`. Подпись привязана к audience и purpose.

</details>

<details>
<summary><b>§3. Переменные окружения</b></summary>

### Шлюз (gateway-mcp, Track B)

```bash
# Адреса 8 сервисов (внутренние адреса GKE-кластера)
KNOWLEDGE_MCP_URL / DIGITAL_TWIN_MCP_URL / PERSONAL_KNOWLEDGE_MCP_URL
USER_PROFILE_SERVICE_URL / LEARNING_CONTEXT_SERVICE_URL
GITHUB_INTEGRATION_SERVICE_URL / AGENT_STATUS_SERVICE_URL / SCOPE_SERVICE_URL

# Ключ подписи шлюза (RS256)
GATEWAY_SIGNING_PRIVATE_JWK   # приватный RS256-ключ
GATEWAY_SIGNING_KID           # идентификатор ключа (публикуется в JWKS)

GATEWAY_PUBLIC_ORIGIN         # публичный адрес шлюза (Track B домен)
GITHUB_WEBHOOK_SECRET         # HMAC-валидация вебхуков GitHub
SUBSCRIPTION_DATABASE_URL     # только для хука выдачи токена (/hydra-hook/token),
                              # не на пути маршрутизации (легитимный остаток ADR DP.IWE.003 §10)
# + параметры OAuth-сервера Ory для входа клиентов
```

### user-profile-service

- `DATABASE_URL` — база персон (Cloud SQL)
- `ORY_URL` — Ory EU GKE endpoint
- `GATEWAY_JWKS_URL` — публичный JWKS шлюза
- `BYOK_KEK` — расшифровка пользовательских ключей к моделям
- `BOT_NOTIFY_URL` + `BOT_NOTIFY_SECRET` — уведомления боту Track B
- `KNOWLEDGE_DB_SCHEMA` — по умолчанию `knowledge`

### learning-context-service

- `LEARNING_DATABASE_URL` — база learning
- `ORY_URL` + `GATEWAY_JWKS_URL`
- `PORT` — по умолчанию 3000
- Миграции: `learning.consent_grant` (229, 261), `cognitive.brief` (230) — **без них `/grant-consent` и `/cognitive-brief` падают**

### github-integration-service

- `DATABASE_URL` — база персон
- `GATEWAY_JWKS_URL` — шлюз авторизуется только подписью (нет `ORY_CLIENT_SECRET`)
- `GATEWAY_PUBLIC_ORIGIN`
- GitHub App: `GITHUB_APP_ID`, `GITHUB_APP_PRIVATE_KEY`, `GITHUB_WEBHOOK_SECRET`
- GitHub OAuth: `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`
- `KNOWLEDGE_REINDEX_SECRET`, `PERSONAL_REINDEX_SECRET`
- `BOT_NOTIFY_URL`, `BOT_NOTIFY_SECRET`, `BOT_WORKBOOK_WEBHOOK_URL`, `BOT_WORKBOOK_WEBHOOK_SECRET`
- `AGENT_RUNNER_URL`, `PERSONAL_KNOWLEDGE_MCP_URL`, `KNOWLEDGE_MCP_URL`, `LEARNING_DATABASE_URL`, `KNOWLEDGE_DB_SCHEMA`

### agent-status-service

- `DATABASE_URL` — база indicators
- `ORY_URL`
- `PORT` — по умолчанию 3000
- `GHOST_TTL_HOURS` — опционально

### Серверы знаний (knowledge / digital-twin / personal-knowledge)

- `DATABASE_URL` — своя база (knowledge / indicators / persona соответственно)
- `ORY_URL` — проверка JWT пользователя
- `GATEWAY_JWKS_URL` — проверка подписи шлюза
- **personal-knowledge-mcp дополнительно:**
  - `SCOPE_GUARD_MODE=enforce` (для Track B сразу enforce — живого трафика нет, shadow-период не нужен)
  - `INDICATORS_DATABASE_URL` — для scope-проверок

</details>

<details>
<summary><b>§4. Базы данных (15 Cloud SQL)</b></summary>

Track B использует Cloud SQL (PostgreSQL, europe-west4). Схемы берутся из Neon (`pg_dump --schema-only`). Данные **не мигрируются** — Track B стартует пустым (Р-инв-2, Р-инв-3).

| # | База | Что хранит | Примечания для Track B |
|---|------|-----------|------------------------|
| 1 | **persona** | Аккаунты, настройки, заметки, эмбеддинги | Создать пустой |
| 2 | **payment** | Платежи, возвраты | Создать + добавить Stripe-поля (Track B = Stripe only, Р-инв-7) |
| 3 | **subscription** | Подписки, автопродления | Создать пустой |
| 4 | **indicators** | Показатели, baseline, снапшоты | Создать пустой |
| 5 | **learning** | Курсы, прогресс, задания | Создать + загрузить EN-контент |
| 6 | **reference** | Тарифы, программы, справочники | Создать + загрузить мировые тарифы |
| 7 | **rewards** | Баллы, достижения, квалификации | Создать + новая эмиссия для Track B |
| 8 | **health** | audit.log (RLS) — security/compliance | Prerequisite для compliance Track B |
| 9 | **community** | Наставничество, встречи, группы | Создать пустой |
| 10 | **journal** | События платформы (event sourcing) | Создать пустой |
| 11 | **knowledge** | Граф концептов, индексы, эмбеддинги | Создать + переиндексировать EN-контент |
| 12 | **lead** | Лиды, UTM-визиты, воронка | Создать пустой |
| 13 | **payment_registry** | Encrypted credentials (Fernet column-level) | **Fernet pgcrypto setup до первого insert** (DP.ARCH.004 §1 v2.3, Р-инв-9) |
| 14 | **publication** | Статьи, посты, каналы | Создать пустой |
| 15 | **secrets** | Encrypted OAuth tokens (ADR-004) | **Fernet keys в K8s Secret до первого OAuth-flow** (Р-инв-10) |

Метабаза исключена из Track B — откладывается до накопления аналитических данных.

**Миграции (Р-22-4):** app-startup self-migrate через Alembic + `pg_advisory_lock` (multi-replica safe). Werf-хук не используется — это уровень приложения, не инфраструктуры. Тяжёлые миграции (reindex миллионов строк) — отдельный admin-процесс в maintenance window.

</details>

<details>
<summary><b>§5. Порядок развёртывания</b></summary>

**Предварительные требования**

1. Добавить Dockerfile трём серверам знаний: knowledge-mcp, digital-twin-mcp, personal-knowledge-mcp (среда CF Workers ≠ Node-контейнер).
2. Применить миграции БД: `262-scope-rls.sql` на indicators; `consent_grant` (229, 261) + `cognitive.brief` (230) на learning.
3. Создать 15 баз Cloud SQL, схемы из Neon.

**Порядок деплоя** (зависимости: Ory и БД первыми, шлюз последним)

1. **Ory EU** — Kratos + Hydra на GKE EU, своя БД; без него авторизация не работает.
2. **Серверы знаний** → контейнеризация + GKE → проверить поиск / двойник / личные знания.
3. **Вспомогательные сервисы** → GKE + K8s Secret → проверить `/health` у каждого.
4. **Шлюз последним** → прописать внутренние адреса кластера + ключ подписи → `/health` должен вернуть `{"ok":true}` (503 = сервисы ещё не подключены).

**Приватная сеть.** Все 8 сервисов — в одном GKE-кластере (europe-west4). Серверы знаний без публичных адресов вне периметра.

**CI/CD (Р-14-4):** GitHub Actions → Artifact Registry → Werf → GKE. PR merge = auto-deploy. Werf-манифест пишет разработчик, DevOps добавляет инфра-специфику (Р-14-5).

</details>

<details>
<summary><b>§6. Раздача прав при подключении источника</b></summary>

**Две точки provisioning:**

| Точка | Что делает | Где сейчас | Целевое место |
|-------|-----------|-----------|---------------|
| user-path | `personal_connect_source` прописывает права на репозиторий пользователя | вызов шлюза → `bridge-scope /api/v1/provision` | in-process в `personal-knowledge-mcp` (владелец инструмента), личность из user-JWT (`sub`) |
| install-webhook | установка GitHub App прописывает права | `github-integration → agent-runner /v1/admin/scope-provision` | в `github-integration-service` с подписью шлюза (server-to-server, пользователя нет) |

**Статус Track A / Track B:**

- **Track A (Cloudflare/Railway):** enforce ✅ выполнено 17 июня. Shadow-окно прошло без `indicators_db_unavailable` (старт 15 июня 08:41 UTC, 48ч+). `SCOPE_GUARD_MODE=enforce` выставлен на `personal-knowledge-mcp`. Следующий шаг: вывести bridge-scope с Railway (проект peaceful-vision).
- **Track B (свежий GKE):** живого трафика нет → `SCOPE_GUARD_MODE=enforce` с первого деплоя. `bridge-scope-service` не разворачивается вовсе. Provisioning (user-path + install-webhook) **обязателен до приёма первого пользователя** — иначе подключение источника и установка GitHub App не пропишут права.

**Открытые шаги (owner — РП-410):**

2. Перенести install-webhook provisioning в s2s-дом: путь `/v1/admin/scope-provision` из `github-integration → agent-runner` в `github-integration-service` с подписью шлюза (`GATEWAY_JWKS_URL`), не на общий пароль — Provisioning на пароле = дыра P1.
3. Вывести bridge-scope после шагов 1-2: шлюз убирает гейт `BRIDGE_WRITE_TOOLS` + вызовы `callScopeService`/`callScopeProvision` → снять `SCOPE_SERVICE_SHARED_SECRET` и URL → `bridge-scope-service` не разворачивать.

</details>

<details>
<summary><b>§7. Чистота шлюза (тест)</b></summary>

**Принцип:** посмотри конфиг шлюза. Только адреса сервисов + ключ подписи → правильный шлюз. Появились базы или прикладная логика → шлюз взял лишнее. (Gateway с одной ответственностью ≠ Gateway с прикладной логикой — ИТ-встреча 07.06.2026, Андрей Смирнов.)

✅ Путь маршрутизации чист: 3 адреса серверов знаний + 4 адреса вспомогательных сервисов + ключ подписи. Баз данных на пути нет.
✅ Управление ключами к моделям (BYOK) — в `user-profile-service`, шлюз только проксирует.
✅ **Легитимный остаток** — хук выдачи токена (`/hydra-hook/token`) читает базу подписок (`SUBSCRIPTION_DATABASE_URL`), чтобы вшить тариф в токен. Это эндпоинт выдачи, не путь маршрутизации. Зафиксировано в ADR DP.IWE.003 §10.

</details>

<details>
<summary><b>§8. Проверка после деплоя</b></summary>

```bash
# Шлюз (503 → {"ok":true} после подключения всех сервисов)
curl https://mcp-world.aisystant.com/health | jq .

# Сервисы (внутри кластера)
curl http://knowledge-mcp/health
curl http://digital-twin-mcp/health
curl http://personal-knowledge-mcp/health
curl http://user-profile-service/health
curl http://learning-context-service/health
curl http://github-integration-service/health
curl http://agent-status-service/health
# bridge-scope-service: НЕ разворачивается на Track B
```

**Поинструментная проверка с токеном (обязательно)** — `/health`=200 не доказывает, что инструмент работает. Прогнать живой вызов по каждому семейству:
- поиск (knowledge-mcp)
- двойник и показатели (digital-twin-mcp)
- личные знания (personal-knowledge-mcp)
- тариф и BYOK (user-profile-service)
- бриф и согласие (learning-context-service)
- статус агента (agent-status-service)
- вход через GitHub (github-integration-service)

Бриф возвращает данные известного пользователя; состояние пути — корректную ступень.

**Better Stack мониторы (Р-инв-11):** обязателен keyword-check для каждого endpoint. HTTP 200 + 0 bytes = false-green без keyword-check (HD #51).

</details>

<details>
<summary><b>§9. Доказательная база</b></summary>

**USER_PROFILE-чистка (P1, мёртвый код):**
```
refactor(WP-410): drop dead USER_PROFILE secret path from gateway
 src/index.ts | 23 +++++++++--------------
 1 file changed, 9 insertions(+), 14 deletions(-)
```

**Дефект learning-context (`ORY_URL not configured`) — не из РП-410:**
- **Для Track B риска нет** — разворачивается свежий `main`, где фиксы уже есть. Track A требует одного `railway up`.

**Scope enforce (WP-410, ✅ 17 июня):**
- Shadow-окно стартовало 15 июня 08:41 UTC, прошло 48ч+ без `indicators_db_unavailable`.
- SQL-проверка: `indicators_db_unavailable = 0`, `scope_not_found = 7` (легитимно — пользователи без provisioning).
- `SCOPE_GUARD_MODE=enforce` выставлен через `npx wrangler secret put` 17 июня на `personal-knowledge-mcp`.
- `SCOPE_REASON_CLASS` — exhaustive `Record<ScopeDenyReason, "deny" | "infra">` с compile-time enforcement. `indicators_db_unavailable` → `"infra"` → fail-open с алертом (не SPOF). Явные deny → fail-closed. Исходник: [`personal-knowledge-mcp/src/scope.ts`](https://github.com/aisystant/personal-knowledge-mcp/blob/main/src/scope.ts).

</details>
