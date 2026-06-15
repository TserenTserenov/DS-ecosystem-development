---
type: handoff
status: active
created: 2026-06-10
updated: 2026-06-15
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

> **Состояние перехода (на 2026-06-14).** Чистый шлюз без общих паролей — это **целевое** состояние, к которому ведёт WP-410. P1 (нет ни одного `*_SHARED_SECRET`) **достижимо после конкретных шагов ниже, ещё не достигнуто.** Не читать как «уже чисто».
>
> **USER_PROFILE** — код шлюза очищен и задеплоен 14 июня (шаг A: шлюз больше НЕ читает `USER_PROFILE_SHARED_SECRET`, health-gate снят). Прогон каждого инструмента живым токеном после деплоя — зелёный. Осталось одно: пилот удаляет само значение пароля с Cloudflare (`wrangler secret delete`, шаг B) после проверки assertion-пути через `wrangler tail`. **Для Track B:** свежая выкатка по разделу 2.2 (без этого пароля) теперь корректна — 503-риска нет.
>
> **SCOPE (bridge-scope)** — ещё жив, закрывается через WP-410 в три шага (это же делает Track B по-настоящему чистым):
> 1. ✅ **СДЕЛАНО (SHA 70f2df4, 15 июня):** `provisionBridgeScopes` подключён безусловно в `connectSource` — каждый connect прописывает права; self-healing при утере прав.
> 2. перенести install-webhook provisioning (`/v1/admin/scope-provision`, сейчас `github-integration → agent-runner`) в дом с явной server-to-server авторизацией;
> 3. вывести `bridge-scope-service` и снять `SCOPE_SERVICE_SHARED_SECRET`+URL из шлюза.
>
> На **живом Track A** шаг enforce делается после выдержки теневой проверки (≥7 дней, ориентир ~20 июня) — чтобы не заблокировать запись текущим пользователям. На **свежем Track B** живого трафика нет, поэтому guard включается в enforce сразу, bridge-scope не разворачивается вовсе — но шаги 1-2 (provisioning) выполнить всё равно нужно, иначе подключение источника и установка GitHub App не пропишут права.
>
> **learning-context (на заметку при деплое):** в текущем Track A `get_cognitive_brief` падает с `ORY_URL not configured` — фиксы авторизации (ORY_URL optional + приём подписи шлюза) в `main`, но не задеплоены (у сервиса ручной `railway up`). На Track B разворачивается свежий код из `main` → бага не будет; на Track A нужен redeploy сервиса.

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
- ⏳ Авторизация без общих паролей — **P1 достижимо после конкретных шагов, не достигнуто на 2026-06-14.** Сервисы проверяют личность сами (раздел 2.1). USER_PROFILE-пароль снят на стороне кода шлюза (14 июня) — осталось удалить значение с Cloudflare (шаг B). SCOPE-пароль уходит после 3 шагов provisioning-консолидации + enforce guard'а (см. «Состояние перехода» в шапке). Свежий Track B: разворачивается без обоих паролей by design, но шаги provisioning (1-2) выполнить обязательно.
- ⚠️ **Легитимный остаток** — хук выдачи токена (`/hydra-hook/token`) читает базу подписок (`SUBSCRIPTION_DATABASE_URL`), чтобы вшить тариф в токен. Это эндпоинт выдачи, не путь маршрутизации. Зафиксировано в ADR DP.IWE.003 §10.

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

<details>
<summary><b>6. Сборка раздачи прав (provisioning) — обязательно для Track B</b></summary>

> Чтобы Track B был чистым by design (без `bridge-scope-service` и без `SCOPE_SERVICE_SHARED_SECRET`), проверку прав агента переносят внутрь `personal-knowledge-mcp`. Решение уже принято (Вариант 2, peer-сессия 2026-06-11-26): встроить guard в personal-knowledge, `bridge-scope-service` не разворачивать. Но раздачу прав (provisioning) нужно собрать в один дом — иначе подключение источника и установка GitHub App не пропишут права, и enforce будет молча всё запрещать.

**Три точки раздачи прав сегодня (разбросаны):**

| Точка | Что делает | Где сейчас | Куда должна |
|-------|-----------|-----------|-------------|
| user-path | `personal_connect_source` прописывает права на репозиторий пользователя | вызов из шлюза → `bridge-scope /api/v1/provision` | in-process в `personal-knowledge-mcp` (владелец инструмента), личность из user-JWT (`sub`) |
| install-webhook | установка GitHub App прописывает права | `github-integration → agent-runner /v1/admin/scope-provision` | в `github-integration-service` с server-to-server подписью (пользователя нет) |
| функция-порт | `provisionBridgeScopes` уже перенесена в personal-knowledge | ✅ DONE (SHA 70f2df4, 15 июня) — подключена безусловно в `connectSource`, self-healing | — |

**Шаги (actionable, owner — РП-410):**

1. ✅ **СДЕЛАНО (SHA 70f2df4, 15 июня).** `provisionBridgeScopes` подключена безусловно в `connectSource` personal-knowledge-mcp: каждый `connect_source` (новый, повторный, self-healing) вызывает `provisionBridgeScopes`. При недоступности indicators-БД — connect не падает, возвращает `scope_provisioning: "failed"` с явным сообщением. `INDICATORS_DATABASE_URL` уже на сервисе (установлен 13 июня, shadow активен).
2. **Перенести install-webhook provisioning в s2s-дом.** Путь `/v1/admin/scope-provision` (установка GitHub App, пользователя нет) перенести из связки `github-integration → agent-runner` в `github-integration-service` с подписью шлюза (`GATEWAY_JWKS_URL`), не на общий пароль. **Provisioning на пароле = та же дыра P1** (можно прописать права любому `userId`).
3. **Вывести bridge-scope.** После шагов 1-2 и (для Track A) выдержки теневой проверки → шлюз убирает гейт `BRIDGE_WRITE_TOOLS` + вызовы `callScopeService`/`callScopeProvision` → снять `SCOPE_SERVICE_SHARED_SECRET`+URL → `bridge-scope-service` не разворачивать.

**Track A vs Track B:**
- **Track A (живой Cloudflare/Railway):** шаг 3 (enforce + снятие секрета) делается ТОЛЬКО после выдержки теневой проверки ≥7 дней (старт 13 июня → ориентир ~20 июня), чтобы не заблокировать запись текущим пользователям. Шаги 1-2 можно готовить заранее.
- **Track B (свежий GKE):** живого трафика нет → guard включается в enforce сразу, `bridge-scope` не разворачивается вовсе. Но шаги 1-2 (provisioning) выполнить **обязательно** до приёма трафика, иначе первое подключение источника / установка App не пропишут права.

</details>

<details>
<summary><b>7. Доказательная база (proof для приёмки)</b></summary>

> Чтобы заявления «USER_PROFILE-код очищен» и «дефект learning-context не из РП-410» не пришлось перепроверять вручную.

**USER_PROFILE-чистка инертна (1 файл, мёртвый код):**
```
$ git show dca2986 --stat   # repo: aisystant/gateway-mcp
refactor(WP-410): drop dead USER_PROFILE secret path from gateway
 src/index.ts | 23 +++++++++--------------
 1 file changed, 9 insertions(+), 14 deletions(-)
```
Коммит в `main` как `1980f88` (cherry-pick: тот же набор изменений и та же статистика `+9/-14`; номера строк в hunk сдвинуты, т.к. лёг на более свежую базу). Убирает только чтение `USER_PROFILE_SHARED_SECRET` (мёртвая ветка `mode:"secret"` — ни один из 4 вызовов её не передаёт), поле в `Env`, ложное health-требование. Прикладной логики не трогает. typecheck чисто, 162 теста, cold-review 0 critical/high, после деплоя per-tool smoke живым токеном зелёный.

**Дефект learning-context (`ORY_URL not configured`) — не из РП-410:**
- `git show dca2986` не содержит learning-context (трогает только USER_PROFILE-код шлюза).
- Корень: фиксы авторизации `54366b3`/`a2a0062`/`2e3d334` в `main` сервиса, но не задеплоены (у `learning-context-service` ручной `railway up`, авто-деплоя нет). «Push ≠ deploy».
- **Для Track B риска нет** — разворачивается свежий `main` сервиса, где фиксы уже есть. Track A требует одного `railway up`.

</details>
