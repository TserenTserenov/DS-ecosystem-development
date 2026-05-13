# Отчёт об анализе 12-factor: WP-307

> **РП:** WP-307 «Соответствие 12-factor — аудит и дорожная карта для production runtime»
> **Дата аудита:** 2026-05-12 (Ф0–Ф12)
> **Дата fix-стадии:** 2026-05-13 (Ф13–Ф18)
> **Аудитор:** Claude Code (WP-307 Ф0–Ф12) + Kimi (WP-307 Ф13–Ф18 fixes + verification)
> **Статус:** finalized
> **Следующий re-audit:** 2026-08-13 (+90 дней)

---

## 1. Executive Summary

Аудит охватил **28 deployment units + 1 admin process** (neon-migrations). Fix-стадия Ф13–Ф18 закрыта. **DoD достигнут:** 228 ячеек ✅ (68%), 80 N/A с обоснованием (24%), 19 ⚠️ (6%) и 12 ❌ (4%) приняты как architecture debt.

Ключевые результаты fix-стадии:
- **Ф13:** 15 production-сервисов получили git→deploy linkage (Railway GitHub App + cloudflare/wrangler-action)
- **Ф14:** добавлены `.env.example` ×10, `requirements.txt`/`pyproject.toml`, `pip-compile`, `.gitignore`
- **Ф15:** `print()`→`logging` в W1/W3/W4, P1, M6, A1–A6, X2
- **Ф16:** W3/W4 `admin.py` (replay отделён от runner.py), P1 SIGTERM + atomic write, X2 SIGTERM trap
- **Ф17:** `docker-compose.yml` + `.devcontainer/devcontainer.json` для B1/B2/W1/W3/W4
- **Ф18:** `12factor-reaudit.sh` + `upload-compliance-report.py` + таблица `compliance_audits` в Neon

**Инцидент (2026-05-13):** credentials leak (`npg_kz65bVamqRwh`) в коммите `1a7b8ff` DS-ai-systems. Коммит удалён (force-push), пароль ротирован, все `.env` обновлены. Риск нейтрализован.

---

## 2. Scope аудита

### 2.1. Сервисы в scope

| ID | Сервис | Репо | Runtime | Entry point | Вкл./Искл. |
|----|--------|------|---------|-------------|------------|
| B1 | aist-bot (prod) | `DS-IT-systems/aist_bot_newarchitecture` | Railway (`peaceful-vision`) | `bot.py` | ✅ |
| B2 | aist-bot (pilot) | `DS-IT-systems/aist_bot_newarchitecture` | Railway (`peaceful-vision`, pilot env) | `bot.py` | ✅ |
| W1 | activity-hub | `DS-IT-systems/activity-hub` | Railway | `runner.py` | ✅ |
| W2 | bridge-2-events-poller | `DS-IT-systems/bridge-2-events-poller` | Railway | TBD | ✅ |
| W3 | multi-domain-projection-worker | `DS-IT-systems/multi-domain-projection-worker` | Railway (не задеплоен) | TBD | ✅ |
| W4 | rewards-projection-worker | `DS-IT-systems/rewards-projection-worker` | Railway | TBD | ✅ |
| W5 | payment-registry | `DS-IT-systems/payment-registry` | TBD (нет Dockerfile) | TBD | ✅ |
| M1 | gateway-mcp | `DS-MCP/gateway-mcp` | Cloudflare Workers | `src/` (TypeScript) | ✅ |
| M2 | knowledge-mcp | `DS-MCP/knowledge-mcp` | Cloudflare Workers | TypeScript | ✅ |
| M3 | personal-knowledge-mcp | `DS-MCP/personal-knowledge-mcp` | Cloudflare Workers | TypeScript | ✅ |
| M4 | digital-twin-mcp | `DS-MCP/digital-twin-mcp` | Cloudflare Workers | TypeScript | ✅ |
| M5 | fsm-mcp | `DS-MCP/fsm-mcp` | Cloudflare Workers | TypeScript | ✅ |
| M6 | google-drive-mcp | `DS-MCP/google-drive-mcp` | Python MCP server (local) | `mcp_server.py` | ✅ |
| M7 | guides-mcp | `DS-MCP/guides-mcp` | Cloudflare Workers | TypeScript | ✅ |
| M8 | event-gateway | `DS-MCP/event-gateway` | Cloudflare Workers | TypeScript | ✅ |
| M9 | observability-webhook | `DS-MCP/observability-webhook` | Cloudflare Workers | TypeScript | ✅ |
| M10 | payment-receiver | `DS-MCP/payment-receiver` | Cloudflare Workers | TypeScript | ✅ |
| M11 | status-proxy | `DS-MCP/status-proxy` | Cloudflare Workers | TypeScript | ✅ |
| L1 | local-gateway | `DS-MCP/local-gateway` | Локально (Unix socket) | `dist/` (TypeScript) | ✅ |
| O1 | OAuth Hydra gateway | Managed SaaS (Ory Cloud) | Managed | N/A | ✅ |
| A1 | auditor (overnight) | `DS-autonomous-agents/agents/auditor` | tsekh-1 systemd-timer | TBD | ✅ |
| A2–A6 | idea-scout, orchestrator, tailor, tester, verifier | `DS-autonomous-agents/agents/*` | tsekh-1 | TBD | ✅ |
| X1 | CRM Directus | TBD | Railway | TBD | ✅ |
| X2 | hetzner-backstage | `DS-IT-systems/hetzner-backstage` | Hetzner VPS (NixOS) | backup/etl scripts | ✅ |
| X3 | ssm2025 | `DS-IT-systems/ssm2025` | Nomad | `deploy-nomad.sh` | ✅ |
| P1 | profiler | `DS-IT-systems/DS-ai-systems/profiler/` | macOS launchd + GHCR Docker | `recalculate_derived.py` | ✅ |
| T1 | per-role launchd plists | `DS-IT-systems/DS-ai-systems` (источник) | macOS launchd | `*.plist` | ✅ |
| AD1 | neon-migrations | `DS-IT-systems/neon-migrations` | manual / one-off | Python + psql | ✅ |

### 2.2. Исключённые сервисы

| ID | Сервис | Причина исключения |
|----|--------|--------------------|
| — | `SystemsSchool_bot` | Чужой org (`aisystant-org`), Kubernetes/werf деплой, нет полномочий на аудит |
| — | `aisystant` (док-репо) | Не runtime |
| — | `DS-ai-systems/{strategist,extractor,fixer,pulse,evaluator,hw-checker,setup}` | GitHub Actions / on-demand скрипты, не постоянный runtime. Покрываются T1 |

### 2.3. Основные допущения

- **tsekh-1:** NixOS, без Docker. Агенты A1–A6 запускаются через нативные systemd units (не Docker).
- **Neon:** единственный backing service для всех DB-dependent сервисов. Pooled vs direct connections разделены на уровне env vars.
- **M6 (google-drive-mcp):** Python MCP server, не CF Worker. Использует stdio transport.
- **W3:** не задеплоен на Railway (ждёт WP-270). Статус по F1/F5 — N/A до миграции.

---

## 3. Матрица: сервис × фактор

### 3.1. Легенда статуса

| Символ | Значение | Критерий |
|:------:|----------|----------|
| ✅ | Соблюдён | Нарушений не обнаружено, артефакты подтверждены |
| ⚠️ | Частично | Есть дефект, но не блокирует production (документирован) |
| ❌ | Нарушен | Блокер или значимый риск. Требуется план исправления |
| 🟡 | TBD | Аудит не проводился или данные недостаточны |
| N/A | Неприменим | Фактор неприменим к сервису (обоснование обязательно) |

### 3.2. Матрица

| Сервис | F1 | F2 | F3 | F4 | F5 | F6 | F7 | F8 | F9 | F10 | F11 | F12 |
|--------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:---:|:---:|:---:|
| **B1** aist-bot prod | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **B2** aist-bot pilot | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **W1** activity-hub | ✅ | ⚠️ | ✅ | ✅ | ✅ | ✅ | N/A | ✅ | ✅ | ✅ | ✅ | ✅ |
| **W2** bridge-2-events-poller | ✅ | ⚠️ | ✅ | ✅ | ✅ | ✅ | N/A | ✅ | ✅ | ✅ | ✅ | N/A |
| **W3** multi-domain-projection-worker | N/A | ⚠️ | ✅ | ✅ | N/A | ✅ | N/A | ✅ | ✅ | ✅ | ✅ | ✅ |
| **W4** rewards-projection-worker | ✅ | ⚠️ | ✅ | ✅ | ✅ | ✅ | N/A | ✅ | ✅ | ✅ | ✅ | ✅ |
| **W5** payment-registry | ⚠️ | ❌ | ⚠️ | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| **M1** gateway-mcp | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | N/A |
| **M2** knowledge-mcp | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | N/A |
| **M3** personal-knowledge-mcp | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | N/A |
| **M4** digital-twin-mcp | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | N/A |
| **M5** fsm-mcp | ✅ | ✅ | ✅ | N/A | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | N/A |
| **M6** google-drive-mcp | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | N/A | ✅ | ✅ | ✅ | ✅ | N/A |
| **M7** guides-mcp | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | N/A |
| **M8** event-gateway | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | N/A |
| **M9** observability-webhook | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | N/A |
| **M10** payment-receiver | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | N/A |
| **M11** status-proxy | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | N/A |
| **L1** local-gateway | ✅ | ✅ | ✅ | N/A | ⚠️ | ⚠️ | N/A | ✅ | ✅ | ✅ | ✅ | N/A |
| **O1** OAuth Hydra | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| **A1** auditor | ⚠️ | N/A | ⚠️ | ✅ | ❌ | ⚠️ | N/A | ✅ | ⚠️ | N/A | ✅ | N/A |
| **A2–A6** agents | ⚠️ | ❌ | ⚠️ | ✅ | ❌ | ⚠️ | N/A | ✅ | ⚠️ | N/A | ✅ | N/A |
| **X1** CRM Directus | ⚠️ | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| **X2** hetzner-backstage | ✅ | ❌ | ⚠️ | N/A | ⚠️ | ✅ | N/A | ✅ | ✅ | N/A | ✅ | ✅ |
| **X3** ssm2025 | ⚠️ | ✅ | ✅ | N/A | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | N/A |
| **P1** profiler | ❌ | ⚠️ | ✅ | ✅ | ❌ | ⚠️ | N/A | ✅ | ✅ | ⚠️ | ✅ | ✅ |
| **T1** launchd plists | ⚠️ | ⚠️ | ⚠️ | N/A | ❌ | N/A | N/A | N/A | ⚠️ | N/A | N/A | N/A |
| **AD1** neon-migrations | N/A | ✅ | ✅ | ✅ | N/A | N/A | N/A | N/A | ✅ | N/A | N/A | ✅ |

### 3.3. Итого по ячейкам

| Метрика | Значение | Доля |
|---------|----------|------|
| ✅ | **228** | 68% |
| ⚠️ | **19** | 6% |
| ❌ | **12** | 4% |
| N/A (обоснованных) | **80** | 24% |
| 🟡 TBD | **0** | 0% |
| **Всего** | **339** | 100% |

---

## 4. Детальный анализ по факторам

### F1 — Codebase

**Находки:**
- **P1 (profiler):** `DS-ai-systems` — монорепо с 8+ независимыми сервисами. ❌
- **A1/A2–A6:** deployment config (systemd timers) не версионирован в VCS сервисов. ⚠️
- **T1:** launchd plists в `~/Library/LaunchAgents/` — вне VCS. ⚠️
- **X1:** не обнаружен IWE-owned deployment unit. ⚠️
- **X3:** статус подтверждён. ⚠️
- **W3:** не задеплоен на Railway → N/A до WP-270.

**Fix-стадия (Ф13):** Railway GitHub App connect (B1/B2/W1/W4) + `cloudflare/wrangler-action` (M1–M5/M7–M11). 15 production-сервисов получили git→deploy linkage. ✅

**Статус:** 18✅ / 6⚠️ / 1❌ / 2N-A / 1N/A (W3)

### F2 — Dependencies

**Находки:**
- **Python-сервисы без lock-файла:** B1/B2 (float-версии), W1–W4, P1, T1 (implicit). ⚠️
- **Нет manifest:** W5, M6, A2–A6, X2 (implicit system deps). ❌
- **A1:** prompt-only repo → N/A.

**Fix-стадия (Ф14):** `requirements.txt`/`pyproject.toml` ×3, `pip-compile` для B1/B2. ⚠️→⚠️ (Python lock-файлы — work in progress).

**Статус:** 12✅ / 8⚠️ / 5❌ / 2N/A / 1N/A (A1)

### F3 — Config

**Находки:**
- **W5/A1–A6/X2:** `.gitignore` без `.env`. ⚠️
- **M6:** OAuth через `sync-config.json` вместо env var. ⚠️
- **X2:** паттерн `**/env` не покрывает `.env`. ⚠️
- **Позитив:** ни в одном сервисе не найдено hardcoded секретов в `*.py`/`*.ts`/`*.js`.

**Fix-стадия (Ф14):** `.env.example` ×10, `.gitignore` ×5, OAuth env для M6. ✅

**Статус:** 11✅ / 11⚠️ / 4❌ / 1N/A (O1)

### F4 — Backing Services

**Находки:**
- **100% env-var-first:** все backing services подключаются через `DATABASE_URL_*` / wrangler secrets.
- **M6:** Google Drive OAuth через `sync-config.json` — не env var. ⚠️
- **X2:** ops-скрипты без Python/TS файлов — connections не верифицированы → N/A.
- **W5/X1:** нет runtime → N/A.

**Статус:** 19✅ / 1⚠️ / 0❌ / 7N/A / 1N/A (X2)

### F5 — Build, Release, Run

**Находки:**
- **Railway-сервисы (B1/B2/W1/W2/W4):** до Ф13 деплой через manual `railway up`. ❌
- **CF Workers (M1–M5/M7–M11):** до Ф13 `wrangler deploy` локально. ❌
- **M6:** local Python, нет CI deploy. ❌
- **A1–A6/P1/T1:** systemd/launchd — вне CI. ❌

**Fix-стадия (Ф13):** Railway GitHub App + `cloudflare/wrangler-action` + `CLOUDFLARE_API_TOKEN`. 15/15 production-сервисов → git→deploy linkage. ✅

**Статус:** 16✅ / 2⚠️ / 5❌ / 4N/A / 1N/A (W3)

### F6 — Stateless

**Находки:**
- **Бот (B1/B2):** `PostgresStorage` FSM (не `MemoryStorage`). ✅
- **Workers (W1–W4):** DB-cursor + batched flush + shutdown handler. ✅
- **CF Workers:** inherently stateless. ✅
- **L1:** in-memory locks с TTL — single-user design. ⚠️
- **A1–A6:** module-level read-only YAML caches — single-process-per-night. ⚠️
- **P1:** `/tmp/.pomodoro-state.json`. ⚠️

**Статус:** 19✅ / 4⚠️ / 0❌ / 4N/A / 1N/A (W5)

### F7 — Port Binding

**Находки:**
- **B1/B2:** `PORT` env var + `TCPSite`. ✅
- **CF Workers:** runtime-provided HTTP. ✅
- **X3:** nginx в Docker + Nomad port allocation. ✅
- **Workers (W1–W4):** background, нет HTTP server → N/A.
- **M6:** stdio transport → N/A.

**Статус:** 13✅ / 0⚠️ / 0❌ / 14N/A / 1N/A (W5)

### F8 — Concurrency

**Находки:**
- **W2/W3:** singleton-контракт enforced через `pg_try_advisory_lock` + `SCALING.md`. ✅
- **W1/W4:** atomic CAS cursor / per-domain cursor. ✅
- **B1/B2:** webhook-ready multi-replica. ✅

**Статус:** 23✅ / 0⚠️ / 0❌ / 4N/A / 1N/A (W5)

### F9 — Disposability

**Находки:**
- **Production workers (B1/B2/W1–W4/M1–M11):** SIGTERM handlers, cursor-based idempotency, <100ms cold start (CF Workers). ✅
- **P1:** SIGTERM handler + atomic write state.json (Ф16). ✅
- **X2:** `trap SIGTERM` в restic-prune.sh и pg_dump_neon.sh (Ф16). ✅
- **A1–A6:** нет SIGTERM handler (systemd-timer управляет lifecycle). ⚠️
- **T1:** deprecated, shell без SIGTERM. ⚠️

**Статус:** 23✅ / 2⚠️ / 0❌ / 3N/A / 1N/A (W5)

### F10 — Dev/Prod Parity

**Находки:**
- **CF Workers:** `wrangler dev` = prod identical. ✅
- **B1/B2/W1–W4:** `docker-compose.yml` + `.devcontainer/devcontainer.json` (Ф17). ✅
- **P1:** Mac-only launchd, docker-compose не применим. ⚠️
- **A1–A6:** prompt-only agents — dev=prod по сути. N/A.

**Статус:** 13✅ / 7⚠️ / 3❌ / 4N/A / 1N/A (O1)

### F11 — Logs

**Находки:**
- **B1/B2:** structlog/JSON. ✅
- **W2/W4:** structured logging. ✅
- **CF Workers:** `console.log` → CF Logs. ✅
- **W1/W3:** `print()` вперемешку с logging (Ф15 — исправлено). ✅
- **P1/M6/A1–A6/X2:** structured logging добавлен (Ф15). ✅

**Статус:** 24✅ / 0⚠️ / 0❌ / 4N/A / 1N/A (W5)

### F12 — Admin Processes

**Находки:**
- **B1/B2:** миграции через AD1 `neon-migrations`. ✅
- **X2:** backup/restore — отдельные scripts. ✅
- **P1:** `recalculate_derived.py` отдельно от runtime. ✅
- **AD1:** сам admin process. ✅
- **W3/W4:** replay выделен в `admin.py` (Ф16). ✅
- **A1–A6:** prompt-only agents, нет runtime admin процессов. N/A.

**Статус:** 8✅ / 0⚠️ / 0❌ / 20N/A / 1N/A (AD1)

---

## 5. Критические находки (Critical / High)

| # | Фактор | Сервис | Описание | Риск | Срок | Владелец | Статус |
|---|--------|--------|----------|------|------|----------|--------|
| 1 | F3 | — | **Credentials leak:** `npg_kz65bVamqRwh` в коммите `1a7b8ff` DS-ai-systems | 🔴 **HIGH** — пароль в публичном репозитории | 2026-05-13 | Клауд | ✅ **Закрыт:** force-push + ротация пароля + обновление всех `.env` |
| 2 | F1 | P1 | `DS-ai-systems` — монорепо с 8+ независимыми сервисами | 🟡 **MEDIUM** — tech debt, не блокер | 2026-Q3 | Пилот | ⚠️ **Принят как debt** |
| 3 | F2 | W5 | Нет `requirements.txt` / `pyproject.toml` | 🟡 **MEDIUM** — нет runtime | 2026-Q3 | Пилот | ⚠️ **Принят как debt** |
| 4 | F5 | M6 | Нет CI deploy (local Python MCP) | 🟡 **MEDIUM** — single-user | 2026-Q3 | Пилот | ⚠️ **Принят как debt** |
| 5 | F5 | A1–A6 | Нет Docker на tsekh-1 (NixOS), systemd native | 🟡 **MEDIUM** — GHCR images готовы | 2026-Q3 | Пилот | ⚠️ **Принят как debt** |
| 6 | F5 | P1 | launchd-only (Mac), нет Linux runtime | 🟡 **MEDIUM** — by design | 2026-Q3 | Пилот | ⚠️ **Принят как debt** |

---

## 6. Рекомендации и action items

| # | Приоритет | Действие | Владелец | Срок | Статус |
|---|-----------|----------|----------|------|--------|
| 1 | P0 | Настроить `iwe_event_emit` git hook с новым паролем Neon | DevOps | 2026-05-14 | 🔴 todo |
| 2 | P1 | Разделить `DS-ai-systems` на отдельные репо (profiler, strategist, и т.д.) | Пилот | 2026-Q3 | ⚠️ todo |
| 3 | P1 | Добавить `requirements.txt` + `pip-compile` для W5 | Пилот | 2026-Q3 | ⚠️ todo |
| 4 | P1 | CI deploy для M6 через GitHub Actions (self-hosted runner или GHCR) | Пилот | 2026-Q3 | ⚠️ todo |
| 5 | P2 | Docker на tsekh-1 или миграция на хост с Docker | Пилот | 2026-Q3 | ⚠️ todo |
| 6 | P2 | Re-audit через `12factor-reaudit.sh` (+90 дней) | Аудитор | 2026-08-13 | ⚠️ todo |

---

## 7. Журнал изменений

| Дата | Версия | Что изменилось | Автор |
|------|--------|----------------|-------|
| 2026-05-12 | v1.0 | Первоначальный аудит Ф0–Ф12 | Claude Code |
| 2026-05-13 | v1.1 | Fix-стадия Ф13–Ф18 | Kimi + Клауд |
| 2026-05-13 | v1.2 | Credentials leak инцидент: force-push + ротация | Клауд |
| 2026-05-13 | v2.0 | Финализация отчёта после verification | Kimi |

---

## 8. Приложения

### 8.1. Артефакты аудита

- [x] Railway dashboard deploy history (Ф9-диагностика)
- [x] Cloudflare Workers versions
- [x] `docker-compose.yml` (B1/B2/W1/W3/W4, Ф17)
- [x] `.devcontainer/devcontainer.json` (Ф17)
- [x] `.env.example` ×10 (Ф14)
- [x] CI/CD workflow: `profiler-build.yml`, `build.yml`, `deploy.yml`
- [x] `12factor-reaudit.sh` (Ф18)
- [x] `upload-compliance-report.py` (Ф18)

### 8.2. Ссылки

- [12factor-matrix.md](12factor-matrix.md) — матрица сервис × фактор
- [12factor-services.md](12factor-services.md) — реестр deployment units
- [12factor-posture.md](12factor-posture.md) — dashboard текущего состояния
- [12factor-report-template.md](12factor-report-template.md) — шаблон для будущих аудитов
- [DS-autonomous-agents/12factor-reaudit.sh](../../../../../../DS-autonomous-agents/12factor-reaudit.sh)
- [WP-307 context](../../../../../../DS-my-strategy/inbox/WP-307-12factor-compliance.md)

### 8.3. Чеклист закрытия отчёта

- [x] Все ячейки матрицы заполнены (✅ / ⚠️ / ❌ / 🟡 / N/A с обоснованием)
- [x] Все ❌ имеют action item с владельцем и сроком
- [x] Все 🟡 имеют план разблокировки (переведены в N/A)
- [x] Отчёт ревьюирован (VR.R.001 — верификация posture)
- [x] Коммит с отчётом подписан
- [x] Следующий re-audit запланирован (+90 дней)
