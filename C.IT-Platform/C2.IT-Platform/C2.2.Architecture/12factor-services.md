# 12-factor: Реестр production runtime сервисов

> **WP-307** «Соответствие 12-factor — аудит и дорожная карта для production runtime»
> **Source-of-truth для scope аудита.** Каждая строка — самостоятельный deployment unit (runtime-процесс), к которому применяются 12 факторов.
> **Создан:** 2026-05-12 (Ф0 инвентаризация).
> **Связано:** `PACK-digital-platform/.../07-map/DP.MAP.002-iwe-service-catalog.md` (каталог методов).
>
> **Различение:** «сервис» в MAP.002 = метод (что делается). «Сервис» здесь = deployment unit (что крутится). Один deployment unit может реализовывать несколько методов MAP.002.

## Принципы включения / исключения

**Включены (по решению пилота 2026-05-12):**
- Долгоживущие процессы, обслуживающие пользователей или интеграции (бот, MCP-серверы, projection-workers).
- Edge-функции (Cloudflare Workers).
- Сервисы, к которым «приходят» извне (HTTP / WebSocket / TCP).
- Локальный launchd-runtime (`scheduler.sh`) — да, включаем.
- Overnight автономные агенты на VPS (tsekh-1) — да, включаем.
- Серверный tooling (hetzner-backstage, ssm2025) — да, включаем.

**Исключены:**
- `DS-IT-systems/SystemsSchool_bot` — отдельный Telegram-бот aisystant-org с Kubernetes/werf деплоем. Исключён по решению пилота 2026-05-12: чужой org, нет полномочий на аудит и исправления.
- `DS-IT-systems/aisystant` — документационный репо, не runtime.
- `DS-IT-systems/DS-ai-systems/{strategist,extractor,fixer,pulse,evaluator,hw-checker,setup}` — GitHub Actions / on-demand скрипты, не постоянный runtime. T1 (scheduler.sh) покрывает их оркестрацию.
- Hooks / skills / governance scripts автора без отдельного runtime.
- Чистые библиотеки и Pack-репо без runtime.

## Категоризация (по runtime платформе)

### Tier R-1: Telegram bot (Railway)

| ID | Сервис | Репо | Branch / Project | Entry point | Реализует методы MAP.002 |
|----|--------|------|-------------------|-------------|--------------------------|
| **B1** | aist-bot (prod) | `DS-IT-systems/aist_bot_newarchitecture` | `new-architecture` / Railway `peaceful-vision`/`aist_bot_newarchitecture` | `bot.py` | S12, S13, S14, S15, S16, S26, S27, S28, S29, S31-S34, S37, S51, S60 |
| **B2** | aist-bot (pilot) | `DS-IT-systems/aist_bot_newarchitecture` | `pilot` / Railway `peaceful-vision`/`aist_bot_newarchitecture` (pilot env) | `bot.py` | то же, что B1 |

> B1 и B2 — один codebase, разные deployments (factor 1 совпадает). Аудит делается раз, статусы заносятся по обоим.

### Tier R-2: Projection workers + event infrastructure (Railway)

| ID | Сервис | Репо | Runtime | Entry point |
|----|--------|------|---------|-------------|
| **W1** | activity-hub (event store + collector) | `DS-IT-systems/activity-hub` | Railway (Dockerfile, github.com/aisystant/activity-hub) | `runner.py` |
| **W2** | bridge-2-events-poller | `DS-IT-systems/bridge-2-events-poller` | Railway (Dockerfile, github.com/TserenTserenov/bridge-2-events-poller) | TBD |
| **W3** | multi-domain-projection-worker | `DS-IT-systems/multi-domain-projection-worker` | Railway (Dockerfile, github.com/aisystant/multi-domain-projection-worker) | TBD |
| **W4** | rewards-projection-worker | `DS-IT-systems/rewards-projection-worker` | Railway (Dockerfile, github.com/aisystant/rewards-projection-worker) | TBD |
| **W5** | payment-registry | `DS-IT-systems/payment-registry` | **⚠️ TBD** — нет Dockerfile в корне, deployment model не идентифицирован (Ф1: F1=⚠️) | TBD |

### Tier R-3: MCP-серверы (Cloudflare Workers / Node.js / Python)

| ID | Сервис | Репо | Runtime | Entry point |
|----|--------|------|---------|-------------|
| **M1** | gateway-mcp (Aisystant MCP / Cloud Gateway DP.IWE.003) | `DS-MCP/gateway-mcp` | Cloudflare Workers (`name = "gateway-mcp-v2"`, custom domain mcp.aisystant.com) | `src/` (TypeScript) |
| **M2** | knowledge-mcp | `DS-MCP/knowledge-mcp` | Cloudflare Workers | TypeScript |
| **M3** | personal-knowledge-mcp | `DS-MCP/personal-knowledge-mcp` | Cloudflare Workers (wrangler.toml: `name = "personal-knowledge-mcp"`) | TypeScript |
| **M4** | digital-twin-mcp | `DS-MCP/digital-twin-mcp` | Cloudflare Workers (wrangler.toml: `name = "digital-twin-mcp"`) | TypeScript |
| **M5** | fsm-mcp | `DS-MCP/fsm-mcp` | Cloudflare Workers (wrangler.toml: `name = "fsm-mcp"`) | TypeScript |
| **M6** | google-drive-mcp | `DS-MCP/google-drive-mcp` | **Python MCP server** (НЕ CF Worker — нет wrangler.toml, есть `mcp_server.py`) | `mcp_server.py` |
| **M7** | guides-mcp | `DS-MCP/guides-mcp` | Cloudflare Workers (wrangler.toml: `name = "guides-mcp"`) | TypeScript |
| **M8** | event-gateway | `DS-MCP/event-gateway` | Cloudflare Workers (wrangler.toml: `name = "event-gateway"`) | TypeScript |
| **M9** | observability-webhook | `DS-MCP/observability-webhook` | Cloudflare Workers (wrangler.toml: `name = "observability-webhook"`) | TypeScript |
| **M10** | payment-receiver | `DS-MCP/payment-receiver` | Cloudflare Workers (wrangler.toml: `name = "payment-receiver"`) | TypeScript |
| **M11** | status-proxy | `DS-MCP/status-proxy` | Cloudflare Workers (wrangler.toml: `name = "status-proxy"`) | TypeScript |

> **M6 уточнение (Ф1):** google-drive-mcp — Python MCP server, не CF Worker. Важно для F7 (порт vs stdio), F10 (dev/prod parity), F11 (логи).

### Tier R-4: Local Gateway (DP.IWE.005)

| ID | Сервис | Репо | Runtime | Entry point | Примечание |
|----|--------|------|---------|-------------|-----------|
| **L1** | iwe-local-gateway | `DS-MCP/local-gateway` | Локально (Unix socket, single-user) | TypeScript dist/ | Не «cloud», но runtime production-grade. Factor 6 (stateless) и Factor 11 (logs) применимы; Factor 7 (port binding) частично N/A (Unix socket) |

### Tier R-5: OAuth / Edge

| ID | Сервис | Репо | Runtime | Entry point |
|----|--------|------|---------|-------------|
| **O1** | OAuth Hydra gateway | **Managed SaaS** — Ory Cloud / self-hosted на `auth.system-school.ru/hydra/` | Managed — нет IWE-codebase | N/A |

> **O1 уточнение (Ф1):** Hydra — управляемый OAuth2-провайдер (Ory SaaS или self-hosted Hetzner). Нет IWE-owned codebase → F1 = N/A. Конфигурация (client registrations, realm) не версионирована в IWE-репо — потенциальный F3-gap.

### Tier R-6: Autonomous agents (VPS tsekh-1) — под вопросом

| ID | Сервис | Репо | Runtime | Entry point |
|----|--------|------|---------|-------------|
| **A1** | auditor (nightly) | `DS-autonomous-agents/agents/auditor` | tsekh-1 systemd-timer | TBD |
| **A2** | idea-scout | `DS-autonomous-agents/agents/idea-scout` | tsekh-1 | TBD |
| **A3** | orchestrator | `DS-autonomous-agents/agents/orchestrator` | tsekh-1 | TBD |
| **A4** | tailor | `DS-autonomous-agents/agents/tailor` | tsekh-1 | TBD |
| **A5** | tester | `DS-autonomous-agents/agents/tester` | tsekh-1 | TBD |
| **A6** | verifier | `DS-autonomous-agents/agents/verifier` | tsekh-1 | TBD |

> Включены по решению пилота 2026-05-12.

### Tier R-7: Дополнительная инфраструктура

| ID | Сервис | Репо | Runtime | Назначение |
|----|--------|------|---------|-----------|
| **X1** | CRM Directus | TBD | Railway | S64 CRM Panel |
| **X2** | hetzner-backstage | `DS-IT-systems/hetzner-backstage` | Hetzner VPS (Docker + systemd) | Backup / etl / ops backstage |
| **X3** | ssm2025 | `DS-IT-systems/ssm2025` | Nomad (deploy-nomad.sh) | TBD — назначение уточнить в Ф1 |

### Tier R-8: Profiler

| ID | Сервис | Репо | Runtime | Entry point |
|----|--------|------|---------|-------------|
| **P1** | DT Profile Calculator (S52) | `DS-IT-systems/DS-ai-systems/profiler/` (часть монорепо `github.com/TserenTserenov/DS-ai-systems`) | macOS launchd (cron 04:30 МСК по `system.yaml`) + per-role systemd plist | `system.yaml` |

> **P1 / F1 = ❌:** DS-ai-systems — монорепо с 8+ независимыми сервисами. P1 (profiler) делит репо с strategist, extractor, fixer, pulse, evaluator, hw-checker, synchronizer.

### Tier R-9: Local scheduler (launchd)

| ID | Сервис | Где | Runtime | Назначение |
|----|--------|-----|---------|-----------|
| **T1** | per-role launchd плисты | `~/Library/LaunchAgents/*.plist` (**НЕ в VCS**) | macOS launchd (ноутбук пилота) | Запуск агентов DS-ai-systems по расписанию |

> **T1 уточнение (Ф1):** `scheduler.sh` задепрекейчен 2026-03-10. Текущий scheduler = per-role launchd plist файлы (`com.strategist.morning`, `com.exocortex.pomodoro-alert`, etc.) в `~/Library/LaunchAgents/` — **вне VCS**. Это F1-нарушение (deployment config не версионирован). Исходный path (`synchronizer/scripts/scheduler.sh`) оставлен как историческая справка.

### Admin / one-shot processes (Factor 12)

| ID | Артефакт | Репо | Назначение |
|----|----------|------|-----------|
| **AD1** | neon-migrations | `DS-IT-systems/neon-migrations` | DB-миграции (admin process) |

## Уточнения по runtime (итог Ф1, 2026-05-12)

**Закрыты в Ф1:**
- W1-W4: Railway (Dockerfile подтверждён, github.com/aisystant или TserenTserenov)
- M3-M11: CF Workers (wrangler.toml с именами подтверждён). Исключение: **M6 — Python MCP server**, не CF Worker
- O1: Managed SaaS (Ory), нет IWE-codebase — F1 = N/A
- P1: macOS launchd/systemd, часть DS-ai-systems монорепо
- X3: Nomad (deploy-nomad.sh + GitHub Actions deploy.yml)

**Остаётся TBD (уточнить в Ф2-Ф3):**
- W5: deployment model не идентифицирован (нет Dockerfile в корне)
- X1 CRM Directus: не найдено IWE-репо с Directus-сервером; только схема в Neon

## Итог Ф0

**Production runtime сервисы (финальный scope):** 2 + 5 + 11 + 1 + 1 + 6 + 3 + 1 + 1 = **31 deployment unit**.

Разбивка по tier'ам:
- R-1 Бот: 2 (B1, B2)
- R-2 Workers: 5 (W1-W5)
- R-3 MCP: 11 (M1-M11)
- R-4 Local Gateway: 1 (L1)
- R-5 OAuth: 1 (O1)
- R-6 Autonomous agents: 6 (A1-A6)
- R-7 Прочее: 3 (X1, X2, X3)
- R-8 Profiler: 1 (P1)
- R-9 Local scheduler: 1 (T1)

Плюс admin: 1 (AD1 neon-migrations) — но это сам Factor 12 example, не runtime в обычном смысле.

**Подтверждённые (без TBD по runtime):** B1, B2, M1, M2, L1, T1 — **6 сервисов**.

**Бюджет (пересчёт):** ~60h (вместо первоначальных 30h). Подход A сохранён по решению пилота 2026-05-12 — 12 фаз × ~5h на фактор по 31 сервису.

---

*Source: `DS-my-strategy/inbox/WP-307-12factor-compliance.md` (WP-context).*
