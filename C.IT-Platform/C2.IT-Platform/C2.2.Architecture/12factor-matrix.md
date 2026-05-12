# 12-factor: Матрица соответствия

> **WP-307** «Соответствие 12-factor — аудит и дорожная карта для production runtime»
> **Source-of-truth для статуса compliance.** Состояние на момент аудита.
> **Создан:** 2026-05-12 (Ф0).
> **Реестр сервисов:** [12factor-services.md](12factor-services.md).
>
> **Легенда статуса:**
> - ✅ — фактор соблюдён
> - ⚠️ — соблюдён частично (с оговорками или с известным дефектом, не блокирующим работу)
> - ❌ — нарушен (план исправления нужен)
> - 🟡 — TBD / аудит фактора по сервису ещё не делался
> - N/A — фактор неприменим к сервису (обоснование обязательно)
>
> **DoD РП-307:** все ячейки заполнены ✅ / N/A-with-justification. ⚠️ и ❌ закрыты до соответствия или мотивированно понижены до N/A.

## Матрица: сервис × фактор

| Сервис | F1 Codebase | F2 Deps | F3 Config | F4 Backing | F5 BRR | F6 Stateless | F7 Port | F8 Concurrency | F9 Disposability | F10 Dev/Prod | F11 Logs | F12 Admin |
|--------|:-----------:|:-------:|:---------:|:----------:|:------:|:------------:|:-------:|:--------------:|:----------------:|:------------:|:--------:|:---------:|
| B1 aist-bot prod | ⚠️ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| B2 aist-bot pilot | ⚠️ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| W1 activity-hub | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| W2 bridge-2-events-poller | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| W3 multi-domain-projection-worker | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| W4 rewards-projection-worker | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| W5 payment-registry | ⚠️ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| M1 gateway-mcp (Cloud Gateway) | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| M2 knowledge-mcp | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| M3 personal-knowledge-mcp | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| M4 digital-twin-mcp | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| M5 fsm-mcp | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| M6 google-drive-mcp | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| M7 guides-mcp | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| M8 event-gateway | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| M9 observability-webhook | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| M10 payment-receiver | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| M11 status-proxy | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| L1 local-gateway (DP.IWE.005) | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | N/A | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| O1 OAuth Hydra gateway | N/A | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| A1 auditor (overnight) | ⚠️ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| A2-A6 другие агенты | ⚠️ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| X1 CRM Directus | ⚠️ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| X2 hetzner-backstage | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| X3 ssm2025 | ⚠️ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| P1 profiler | ❌ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| T1 scheduler.sh (launchd) | ⚠️ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | N/A | 🟡 | 🟡 | N/A | 🟡 | 🟡 |
| AD1 neon-migrations | N/A | 🟡 | 🟡 | 🟡 | N/A | N/A | N/A | N/A | 🟡 | 🟡 | 🟡 | ✅* |

> *AD1 neon-migrations — это сам admin process; для него F12 ≈ ✅ по определению. Остальные «runtime»-факторы (codebase, BRR, stateless, port, concurrency, disposability) к admin-скрипту не применяются.

> L1 F7 (port) = N/A — Unix socket вместо HTTP-порта.
> T1 F7 (port) = N/A — нет порта, scheduled-trigger через launchd; F10 (dev/prod parity) = N/A — это сам tooling, dev=prod по сути.
> O1 F1 = N/A — управляемый SaaS (Ory Cloud / self-hosted), нет IWE-codebase. Остальные факторы O1 = 🟡 TBD (конфигурация Hydra не версионирована в IWE).
> T1 F1 = ⚠️ — scheduler.sh задепрекейчен (2026-03-10). Текущий runtime = per-role launchd plists в `~/Library/LaunchAgents/` — НЕ в VCS.
> P1 F1 = ❌ — DS-ai-systems монорепо (8+ независимых сервисов в одном репо: profiler, strategist, extractor, fixer, pulse, evaluator, hw-checker, synchronizer).

## Заметки по факторам — итоги аудита и ожидаемые блокеры

- **F1 Codebase (Ф1 done 2026-05-12):** ✅ 17/28 строк, ⚠️ 8/28, ❌ 1/28. Критический дефект: **P1 / DS-ai-systems — монорепо** с 8+ независимыми сервисами в одном репо. ⚠️-группы: B1/B2 (1 уникальный коммит в pilot — consent feature), A1-A6 (DS-autonomous-agents монорепо, deployment model не задокументирован), T1 (launchd plists не в VCS), W5/X1/X3 (deployment config неизвестен). M6 — Python MCP, не CF Worker (важно для F7/F10).
- **F3 Config (security tax):** ожидается ❌ для большинства сервисов — секреты в `.env` файлах и/или дублирование переменных между Railway / wrangler / локальной средой. Нужен ревизионный grep на коммиты.
- **F6 Stateless:** ожидается ⚠️ для бота (FSM-state хранится в БД ✅, но кэш `data['raw_state']` в памяти — см. `lessons_aiogram_raw_state_cache.md`) и workers (cursor в локальной памяти — см. `feedback_silent_projection_fail.md`).
- **F10 Dev/Prod parity:** ожидается ❌ — нет Docker Compose окружения для большинства сервисов; локальная разработка с одной БД, прод с другой архитектурой.
- **F11 Logs:** ожидается ⚠️ — есть `feedback_silent_fail_log_to_stdout.md` (bash log() пишет в stderr — корректно для 12-factor), но для Python-сервисов нужно проверить структурированность.

## Журнал нарушений и исправлений

> Каждое нарушение (⚠️ / ❌) фиксируется здесь со ссылкой на дочерний фикс. Пустой раздел = аудит ещё не начат.

| Дата | Сервис | Фактор | Нарушение | План исправления | Статус |
|------|--------|--------|-----------|-------------------|--------|
| 2026-05-12 | P1 profiler | F1 | DS-ai-systems монорепо: 8+ независимых сервисов (profiler, strategist, extractor, fixer, pulse, evaluator, hw-checker, synchronizer) в одном репо | Разделить на отдельные репо ИЛИ оформить как unified Platform Layer с атомарным версионированием + отдельными CI/CD pipeline на каждый sub-сервис | 🔴 открыт |
| 2026-05-12 | B1, B2 | F1 | Ветки `new-architecture` (prod) и `pilot` имеют расхождение: 1 уникальный коммит в `pilot` — consent feature (WP-188). Одна ветка задеплоена в прод, другая — в пилот с дополнительным кодом | Смёрджить `pilot` → `new-architecture` после валидации consent-фичи ИЛИ вынести за feature flag + env var `ENABLE_CONSENT` | ⚠️ открыт |
| 2026-05-12 | A1-A6 | F1 | DS-autonomous-agents монорепо: 6 агентов в одном репо, каждый = только `agent-card.yaml` + `prompt.md`. Deployment model не задокументирован (prompts-only vs independent services) | Задокументировать модель деплоя. Если prompt-only → ✅ допустимо как unified config artifact. Если независимо деплоятся → разделить репо | ⚠️ открыт |
| 2026-05-12 | T1 | F1 | scheduler.sh задепрекейчен (2026-03-10). Новый runtime — per-role launchd plists (`~/Library/LaunchAgents/*.plist`) — НЕ находятся в VCS | Добавить plist-файлы в DS-ai-systems (или отдельный infra-репо) | ⚠️ открыт |
| 2026-05-12 | W5 | F1 | payment-registry — нет Dockerfile в корне; deployment model не идентифицирован (Railway? schema-only? manual?) | Уточнить deployment config; добавить Dockerfile или задокументировать как schema-only (тогда → AD2) | ⚠️ открыт |
| 2026-05-12 | X1 | F1 | CRM Directus — в IWE-репо найдена только схема в Neon. Активный Directus-сервер (deployment unit) не обнаружен в IWE-репозиториях | Подтвердить: активен? Где задеплоен? Добавить репо в реестр или исключить из scope | ⚠️ открыт |
| 2026-05-12 | X3 | F1 | ssm2025 — `deploy-nomad.sh` + GitHub Actions `deploy.yml` есть, но полный deployment config не проверен | Проверить Nomad job config; убедиться, что prod deployment из main branch | ⚠️ открыт |

---

*Source: `DS-my-strategy/inbox/WP-307-12factor-compliance.md` (WP-context).*
