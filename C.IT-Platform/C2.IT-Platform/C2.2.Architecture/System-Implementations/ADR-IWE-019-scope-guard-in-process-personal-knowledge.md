# ADR-IWE-019 — Перенос scope-guard in-process в personal-knowledge-mcp (Ф-scope)

- **Статус:** Accepted (ArchGate пройден 2026-06-11, peer-сессии 2026-06-11-26 решение В2 + 2026-06-11-44 дизайн миграции, Claude+Kimi)
- **Контекст РП:** WP-410 Ф-scope
- **Связанные:** ADR-IWE-017 (чистый шлюз-маршрутизатор), ADR-IWE-018 (Ф-byok), DP.SC.165 (scope enforcement), принцип «Gateway с одной ответственностью ≠ Gateway с прикладной логикой»

## Контекст

Шлюз (`gateway-mcp`) перед маршрутизацией `personal_write`/`personal_propose_capture` делает scope-check HTTP-зовом к `bridge-scope-service` через `SCOPE_SERVICE_SHARED_SECRET` + доверяемый `X-User-Id` (`index.ts:1955-2002`), и после `personal_connect_source` provision'ит scope-строки тем же секретом (`index.ts:2024-2039`).

- **P1 (безопасность):** утёк `SCOPE_SERVICE_SHARED_SECRET` → можно provision-нуть/проверить scope под любым `X-User-Id`.
- **P2 (архитектура):** шлюз знает scope-логику (какие инструменты, какой источник/путь) → прикладная логика в маршрутизаторе.

Верифицировано кодом 2026-06-11: bridge-scope-service экспортит ровно `/check-scope` + `/api/v1/provision`, оба user-path, единственный клиент — шлюз. install-webhook provision (`/v1/admin/scope-provision`) висит на `agent-runner` (`github-integration-service/src/utils/service-calls.ts:66`), **не** на bridge-scope → не блокирует его декоммишн.

## Решение

**Вариант 2 — guard in-process в personal-knowledge-mcp, bridge-scope-service удалить.**

Personal-knowledge владеет `personal_write` и персональными данными → guard живёт с данными, которые защищает. Шлюз перестаёт знать scope и держать scope-секрет.

| Аспект | Как |
|--------|-----|
| Транспорт identity | user-JWT (шлюз уже проксирует `Authorization: Bearer`, `index.ts:1128`); personal-knowledge сам валидирует Ory JWT → `userId = sub` |
| Признак агента | узкий whitelist `_meta = {agent_id, request_id}` в fan-out шлюза (раньше `_meta` не доходил) |
| Драйвер БД | `neon(INDICATORS_DATABASE_URL)` (scope-таблицы) + `neon(DATABASE_URL)` (own `knowledge.user_sources` для peer-pilot lookup) |
| RLS-пояс | `SET LOCAL app.user_id` снят (на `agent_scopes_mvp` RLS не форсится — `relforcerowsecurity=f`); изоляцию держит явный `WHERE user_id`. Снятие behavior-preserving. |
| Имена | канонические DP.SC.165 (`iwe_bridge:personal_write`) сохранены; локальное `write`→`personal_write` маппится на месте вызова (иначе `expectedAgentId` не совпал бы с выданными строками → ложный deny) |
| peer-pilot fallback | `requireDeclaredAgentId: true` сохранён (в проде активен, `bridge-scope server.ts:98`) |

## Rollout (инвариант: ≥1 enforcer на каждом шаге)

S0 shadow (pk считает+логирует, не блокирует; шлюз enforce) → S1 enforce (оба enforce, double-guard) → S2 шлюз убирает scope-check (pk единственный) → S3 декоммишн bridge-scope + снос scope-секрета из шлюза. Флип S0→S1 после 0 расхождений / 24ч / ≥10k / coverage ≥95% / зелёная deny-фикстур-сюита.

**Верификация двухконтурная:** allow-путь — live shadow + офлайн-join по request_id; deny-путь — fixture-сюита (шлюз режет deny до маршрутизации, live-shadow его не видит).

## Отвергнутые альтернативы

- **В1** (свап auth на JWT, сервис оставить): лечит P1, не P2 (лишний сервис). Снят детерминантом 2026-06-11-26.
- **inline-сравнение вердиктов в шлюзе** (snapshot предложения Kimi): сама прикладная логика в шлюзе — анти-паттерн этого РП. Заменён офлайн + fixture.
- **install-webhook provision оставить до Ф7**: install-webhook висит на agent-runner, не на bridge-scope → ничего оставлять не нужно.

## ЭМОГССБ (профиль)

7 характеристик: ✅ при управляемом ⚠️ Наблюдаемости (audit при переезде) и ⚠️ Безопасности (миграция access-control, закрыта инвариантом rollout + fixture). Вето-фильтр чист по 4 критическим. Полный профиль + §Б Security Gate → `DS-my-strategy/sessions/2026-06/2026-06-11-44-wp410-fscope-guard-port/archgate.md`.

## Последствия

- **+** P1 закрыт (scope-секрет уходит из шлюза после S2); P2 закрыт (scope-логика уходит из шлюза); −1 сервис (bridge-scope).
- **−/риски:** до co-deploy (шлюз-_meta + pk-shadow) `agent_id` не доходит → теневой вердикт идёт peer-pilot-веткой (ожидаемо до S0-деплоя). Cut-over S1-S3 + декоммишн под пилота (Railway-авторизация).
- **Action items:** пилот ставит `INDICATORS_DATABASE_URL` + `SCOPE_GUARD_MODE` на personal-knowledge; B2.1 Secrets Inventory минус `SCOPE_SERVICE_SHARED_SECRET` после S2.

## Реализация

Ветки `wp-410-fscope-guard-port`: personal-knowledge-mcp (`src/scope.ts` порт + проводка shadow + fixture-тесты), gateway-mcp (whitelist `_meta`). НЕ в main (оба авто-деплоятся при push в main). S0-деплой gated на пилота (нужен `INDICATORS_DATABASE_URL` secret + co-deploy).
