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
| B1 aist-bot prod | ⚠️ | ⚠️ | ⚠️ | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| B2 aist-bot pilot | ⚠️ | ⚠️ | ⚠️ | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| W1 activity-hub | ✅ | ⚠️ | ✅ | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| W2 bridge-2-events-poller | ✅ | ⚠️ | ⚠️ | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| W3 multi-domain-projection-worker | ✅ | ⚠️ | ⚠️ | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| W4 rewards-projection-worker | ✅ | ⚠️ | ⚠️ | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| W5 payment-registry | ⚠️ | ❌ | ❌ | N/A | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| M1 gateway-mcp (Cloud Gateway) | ✅ | ✅ | ✅ | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| M2 knowledge-mcp | ✅ | ✅ | ✅ | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| M3 personal-knowledge-mcp | ✅ | ✅ | ✅ | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| M4 digital-twin-mcp | ✅ | ✅ | ✅ | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| M5 fsm-mcp | ✅ | ✅ | ✅ | N/A | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| M6 google-drive-mcp | ✅ | ❌ | ⚠️ | ⚠️ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| M7 guides-mcp | ✅ | ✅ | ✅ | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| M8 event-gateway | ✅ | ✅ | ✅ | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| M9 observability-webhook | ✅ | ✅ | ✅ | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| M10 payment-receiver | ✅ | ✅ | ✅ | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| M11 status-proxy | ✅ | ✅ | ✅ | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| L1 local-gateway (DP.IWE.005) | ✅ | ✅ | ⚠️ | N/A | 🟡 | 🟡 | N/A | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| O1 OAuth Hydra gateway | N/A | N/A | 🟡 | N/A | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| A1 auditor (overnight) | ⚠️ | ❌ | ❌ | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| A2-A6 другие агенты | ⚠️ | ❌ | ❌ | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| X1 CRM Directus | ⚠️ | N/A | N/A | N/A | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| X2 hetzner-backstage | ✅ | ❌ | ❌ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| X3 ssm2025 | ⚠️ | ✅ | ⚠️ | N/A | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| P1 profiler | ❌ | ❌ | ⚠️ | ✅ | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 | 🟡 |
| T1 scheduler.sh (launchd) | ⚠️ | ⚠️ | ⚠️ | N/A | 🟡 | 🟡 | N/A | 🟡 | 🟡 | N/A | 🟡 | 🟡 |
| AD1 neon-migrations | N/A | ⚠️ | ⚠️ | ✅ | N/A | N/A | N/A | N/A | 🟡 | 🟡 | 🟡 | ✅* |

> *AD1 neon-migrations — это сам admin process; для него F12 ≈ ✅ по определению. Остальные «runtime»-факторы (codebase, BRR, stateless, port, concurrency, disposability) к admin-скрипту не применяются.

> L1 F7 (port) = N/A — Unix socket вместо HTTP-порта.
> T1 F7 (port) = N/A — нет порта, scheduled-trigger через launchd; F10 (dev/prod parity) = N/A — это сам tooling, dev=prod по сути.
> O1 F1 = N/A — управляемый SaaS (Ory Cloud / self-hosted), нет IWE-codebase. Остальные факторы O1 = 🟡 TBD (конфигурация Hydra не версионирована в IWE).
> T1 F1 = ⚠️ — scheduler.sh задепрекейчен (2026-03-10). Текущий runtime = per-role launchd plists в `~/Library/LaunchAgents/` — НЕ в VCS.
> P1 F1 = ❌ — DS-ai-systems монорепо (8+ независимых сервисов в одном репо: profiler, strategist, extractor, fixer, pulse, evaluator, hw-checker, synchronizer).
> X1 F3 = N/A — нет IWE-репо, аудит невозможен.
> M6 F3 = ❌ КРИТИЧНО — .env в git history. Требует ротации секретов и очистки истории.
> **Позитив F3:** ни в одном сервисе НЕ найдено hardcoded секретов (Telegram tokens, API keys, sk-/pk-) в `*.py`/`*.ts`/`*.js` файлах HEAD-кода. Это значит, что культура «всё через env var» в целом соблюдается — проблемы только в `.gitignore` гигиене и истории.

## Заметки по факторам — итоги аудита и ожидаемые блокеры

- **F1 Codebase (Ф1 done 2026-05-12):** ✅ 17/28 строк, ⚠️ 8/28, ❌ 1/28. Критический дефект: **P1 / DS-ai-systems — монорепо** с 8+ независимыми сервисами в одном репо. ⚠️-группы: B1/B2 (1 уникальный коммит в pilot — consent feature), A1-A6 (DS-autonomous-agents монорепо, deployment model не задокументирован), T1 (launchd plists не в VCS), W5/X1/X3 (deployment config неизвестен). M6 — Python MCP, не CF Worker (важно для F7/F10).
- **F2 Dependencies (Ф2 done 2026-05-12):** ✅ 12/28 (M1-M5, M7-M11, L1, X3 — package.json + lock), ⚠️ 8/28 (все Python без lock-файла; B1/B2 + float-версии; T1 implicit), ❌ 6/28 (W5, M6, A1-A6, X2, P1 — нет manifest). X2 — implicit system deps (restic, ssh). Node.js CF Workers ✅: caret + package-lock = npm-стандарт.
- **F3 Config (Ф3 done 2026-05-12):** ✅ 11/28 (CF Workers M1-M5, M7-M11, W1 — env vars/wrangler secrets), ⚠️ 11/28 (M6 + 10 без `.env.example`), ❌ 4/28. ~~🔴 КРИТИЧНО M6~~ — **проверено: ложная тревога** (`.env` никогда не был в истории; репо локальный без remote; `.gitignore` расширен в d1db091). **🟠 HIGH:** W5/A1-A6 (`.gitignore` без `.env`), X2 (паттерн `**/env` не покрывает `.env`). Hardcoded secrets в HEAD-коде НЕ найдены — это позитивно.
- **F4 Backing Services (Ф4 done 2026-05-12):** ✅ 19/28 (B1/B2, W1-W4, M1-M4/M7-M11, A1-A6, P1, AD1 — все через env vars/wrangler secrets), N/A 7 (W5 пустой репо, M5 stateless, L1 без backing services, O1 managed SaaS, X1 нет IWE-репо, X3 статичный сайт, T1 scheduler), ⚠️ 1 (M6 Google Drive OAuth через `sync-config.json` вместо env var), ❌ 0, 🟡 1 (X2 ops-скрипты без Python/TS файлов — backing service connections не верифицированы). **Позитив F4:** 100% env-var-first для backing services (DATABASE_URL_* паттерн, wrangler secrets); fail-fast при старте (Pydantic Field required / _require_env()); pooled vs unpooled Neon правильно разделены на уровне отдельных env vars.
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
| 2026-05-12 | W5 | F2 | payment-registry — нет manifest (requirements.txt / package.json) вообще. Только shell-скрипты | Создать manifest; уточнить runtime (shell-only или Python/Node?) | ❌ открыт |
| 2026-05-12 | M6 | F2 | google-drive-mcp — Python MCP server без requirements.txt и pyproject.toml | Создать requirements.txt с зафиксированными версиями | ❌ открыт |
| 2026-05-12 | A1-A6 | F2 | DS-autonomous-agents — нет ни requirements.txt, ни package.json в корне или в каждом агенте | Если агенты prompt-only → N/A обоснованно; если есть Python/Node зависимости → создать manifest | ❌ открыт |
| 2026-05-12 | X2 | F2 | hetzner-backstage — только shell-скрипты (setup-ssh-keys.sh, restic-prune.sh и др.), нет manifest. Implicit system deps: restic, ssh, systemd | Создать `infrastructure.md` с перечнем system tools ИЛИ Dockerfile с apt-get резервных deps | ❌ открыт |
| 2026-05-12 | P1 | F2 | DS-ai-systems монорепо — нет единого manifest. Только `publisher/scripts/requirements.txt` (floating: httpx>=0.27, pyyaml>=6.0). Profiler, strategist, extractor и др. — без manifest | Добавить `requirements.txt` для каждого sub-сервиса с pinned-версиями; добавить lock-файл | ❌ открыт |
| 2026-05-12 | B1, B2 | F2 | requirements.txt: `aiogram>=3.20.0`, `langfuse>=4.0.0` — floating-версии (>=). Нет lock-файла | Заменить >= на ==; добавить `requirements.lock` через `pip-compile` | ⚠️ открыт |
| 2026-05-12 | W1-W4 | F2 | requirements.txt / pyproject.toml есть, версии зафиксированы (==), но lock-файл отсутствует у всех 4 | Добавить `poetry.lock` или `.txt` от `pip-compile` | ⚠️ открыт |
| 2026-05-12 | AD1 | F2 | neon-migrations — Python ETL-скрипты (`etl-*.py`) без requirements.txt. SQL-файлы — N/A | Создать requirements.txt для Python-скриптов (pandas, psycopg2 и др.) | ⚠️ открыт |
| 2026-05-12 | M6 | F3 | ~~**🔴 CRITICAL: `.env` в git history**~~ — **ЗАКРЫТО (ложная тревога).** Верификация в соседней сессии: git log --all -- '*.env' пусто, репо чисто локальный без remote, 2 коммита. `.gitignore` был только `__pycache__/`; расширен до `.env*`, `*.token`, `credentials*.json`, `token*.json` в коммите d1db091. `sync-config.json` содержит только path-маппинг, никаких секретов. Остаток ⚠️: нет `.env.example` для OAuth-переменных | `.env.example` с placeholder OAuth vars | ⚠️ открыт |
| 2026-05-12 | W5 | F3 | payment-registry — `.gitignore` не содержит `.env` (только `_backups`, `.claude`). Любой `git add .env` пройдёт без предупреждения | Добавить `*.env` и `.env*` в `.gitignore`; создать `.env.example` | ❌ открыт |
| 2026-05-12 | A1-A6 | F3 | DS-autonomous-agents — `.gitignore` без `.env`-правила. Config pattern не очевиден | (1) Добавить `.env*` в `.gitignore`; (2) аудит на hardcoded config в агентах; (3) создать `.env.example` | ❌ открыт |
| 2026-05-12 | X2 | F3 | hetzner-backstage — `.gitignore` содержит `**/env` (без точки) — НЕ покрывает `.env` файлы | Заменить `**/env` на `**/.env*` | ❌ открыт |
| 2026-05-12 | B1, B2, W2-W4, L1, X3, AD1, P1 | F3 | `.gitignore` корректен, но отсутствует `.env.example` — onboarding-friction, разработчик не знает какие переменные нужны | Создать `.env.example` в каждом сервисе с placeholder-значениями | ⚠️ открыт |
| 2026-05-12 | M6 | F4 | google-drive-mcp — Google Drive OAuth 2.0 credentials хранятся в `sync-config.json` (файл на диске), а не в env var. Замена инстанса = ручное редактирование файла | Перейти на env-based OAuth (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN) + убрать sync-config.json из репо | ⚠️ открыт |
| 2026-05-12 | X2 | F4 | hetzner-backstage — репо содержит только shell-скрипты (нет Python/TS файлов). Backing service connections в bash-скриптах не поддаются автоматической верификации через grep | Ручной аудит: проверить restore/backup-скрипты на env var usage (RESTIC_REPOSITORY, RESTIC_PASSWORD, BACKUP_TARGET) | 🟡 открыт |

*Source: `DS-my-strategy/inbox/WP-307-12factor-compliance.md` (WP-context).*
