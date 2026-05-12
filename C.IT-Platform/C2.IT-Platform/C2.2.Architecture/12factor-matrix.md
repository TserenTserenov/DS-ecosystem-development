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
| B1 aist-bot prod | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| B2 aist-bot pilot | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| W1 activity-hub | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| W2 bridge-2-events-poller | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| W3 multi-domain-projection-worker | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| W4 rewards-projection-worker | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| W5 payment-registry | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| M1 gateway-mcp (Cloud Gateway) | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| M2 knowledge-mcp | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| M3 personal-knowledge-mcp | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| M4 digital-twin-mcp | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| M5 fsm-mcp | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| M6 google-drive-mcp | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| M7 guides-mcp | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| M8 event-gateway | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| M9 observability-webhook | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| M10 payment-receiver | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| M11 status-proxy | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| L1 local-gateway (DP.IWE.005) | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | N/A | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| O1 OAuth Hydra gateway | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| A1 auditor (overnight) | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| A2-A6 другие агенты | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| X1 CRM Directus | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| X2 hetzner-backstage | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| X3 ssm2025 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| P1 profiler | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| T1 scheduler.sh (launchd) | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | N/A | 🟡 | 🟡 | N/A | 🟡 | 🟡 |
| AD1 neon-migrations | N/A | 🟡 | 🟡 | 🟡 | N/A | N/A | N/A | N/A | 🟡 | 🟡 | 🟡 | ✅* |

> *AD1 neon-migrations — это сам admin process; для него F12 ≈ ✅ по определению. Остальные «runtime»-факторы (codebase, BRR, stateless, port, concurrency, disposability) к admin-скрипту не применяются.

> L1 F7 (port) = N/A — Unix socket вместо HTTP-порта.
> T1 F7 (port) = N/A — нет порта, scheduled-trigger через launchd; F10 (dev/prod parity) = N/A — это сам tooling, dev=prod по сути.

## Заметки по факторам — заранее ожидаемые блокеры

- **F3 Config (security tax):** ожидается ❌ для большинства сервисов — секреты в `.env` файлах и/или дублирование переменных между Railway / wrangler / локальной средой. Нужен ревизионный grep на коммиты.
- **F6 Stateless:** ожидается ⚠️ для бота (FSM-state хранится в БД ✅, но кэш `data['raw_state']` в памяти — см. `lessons_aiogram_raw_state_cache.md`) и workers (cursor в локальной памяти — см. `feedback_silent_projection_fail.md`).
- **F10 Dev/Prod parity:** ожидается ❌ — нет Docker Compose окружения для большинства сервисов; локальная разработка с одной БД, прод с другой архитектурой.
- **F11 Logs:** ожидается ⚠️ — есть `feedback_silent_fail_log_to_stdout.md` (bash log() пишет в stderr — корректно для 12-factor), но для Python-сервисов нужно проверить структурированность.

## Журнал нарушений и исправлений

> Каждое нарушение (⚠️ / ❌) фиксируется здесь со ссылкой на дочерний фикс. Пустой раздел = аудит ещё не начат.

| Дата | Сервис | Фактор | Нарушение | План исправления | Статус |
|------|--------|--------|-----------|-------------------|--------|
| — | — | — | — | — | — |

---

*Source: `DS-my-strategy/inbox/WP-307-12factor-compliance.md` (WP-context).*
