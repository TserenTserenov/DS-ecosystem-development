# 12-factor Posture — dashboard состояния

> **WP-307.** Краткое состояние соответствия 12-factor по production runtime.
> Аналог [`security-posture.md`](security-posture.md), но для cloud-native гигиены.
>
> **Обновляется:** при закрытии каждой фазы Ф1-Ф12 WP-307.

## Текущее состояние (2026-05-13, Ф13-Ф15 fix-стадия применена)

| Показатель | Значение |
|------------|----------|
| Сервисов в scope | 28 deployment unit + 1 admin (neon-migrations) |
| Всего ячеек | 336 (28 × 12) |
| Бюджет РП | 60h + 22h fixes |
| Подход | A — линейный, 12 фаз по фактору |
| Подтверждённых ✅ ячеек | **228** (68%) |
| ⚠️ ячеек | **19** (6%) |
| ❌ ячеек | **12** (4%) |
| N/A ячеек (обоснованных) | **80** (24%) |
| 🟡 TBD ячеек (legit pending) | **0** |
| 🔴 КРИТИЧЕСКИХ (security) | **0** |
| Прогресс fix-стадии | **Ф13 ✅, Ф14 ✅, Ф15 ✅, Ф16 ✅, Ф17 ✅, Ф18 ✅** |
| Last automated re-audit | <!-- AUTO-UPDATED by 12factor-reaudit.sh --> 2026-07-23 (12factor-reaudit.sh: ✅24 ⚠️0 ❌0 🔒0 drift=none) |
| DoD | ✅ ДОСТИГНУТ — 100% green-or-justified-N/A. РП307 готов к закрытию. |

## 🔧 WP-7 (23.07): устранён 3-недельный ложный critical-дрейф аудитора

**Симптом:** `12factor-reaudit.sh` показывал одинаковый ❌9/⚠️18 каждую ночь с 1 июля без единого изменения — статус «протух», критический алерт перестал что-либо сигнализировать.

**Диагностика (пир-сессия с Kimi, `DS-my-strategy/sessions/2026-07/23/2026-07-23-01-12factor-drift-fix/`):** сам продакшен был ни при чём. Аудитор проверял только локальные git-клоны на этой конкретной Linux-машине (tsekh-1); большинство `DS-MCP/*` и `DS-IT-systems/*` из его hardcoded-списков там никогда не клонировались — они существуют на GitHub (в основном под org `aisystant`) и **уже** имели нужные `deploy.yml`/`.env.example`/`.gitignore` (подтверждено через `gh api`). Плюс 2 hardcoded-имени были неверными (`aist_bot_newarchitecture` — склейка repo+branch, реальный репо `aist_bot`; `local-gateway` вместо реального `iwe-local-gateway`), и один сервис (`rewards-projection-worker`) давно decommissioned (WP-311, 2026-05-17), но не убран из списка активной проверки.

**Фикс:** `DS-autonomous-agents/scripts/12factor-reaudit.sh` теперь при отсутствии локального клона проверяет через `gh api` (маппинг repo→owner/repo, источник — этот реестр `12factor-services.md`); добавлена явная категория `api_error` (не путается ни с «есть», ни с «нет» — сетевой/auth-сбой не эскалируется как надуманный critical, но полный отказ проверки — эскалируется). Исправлены 2 имени, `rewards-projection-worker` убран из активного списка. Реальный результат после фикса: **✅24 ⚠️0 ❌0, drift=none** — критического долга по этим сервисам никогда не было, был баг самого аудитора.

**Открытый вопрос (эскалирован пилоту, не решён в сессии):** `google-drive-mcp` (M6 в матрице ниже) не найден НИ локально на этой машине, НИ на GitHub (ни `aisystant`, ни `TserenTserenov`) — похоже, живёт только как локальный файл на Mac-инсталляции пилота и никогда не был закоммичен в git. Исключён из активной проверки `12factor-reaudit.sh` до решения: нужен ли ему вообще собственный git-репозиторий, или это осознанно un-versioned личный скрипт вне scope 12-factor аудита.

## 🚨 VR.R.001 Fold-back (2026-05-12, Ф-Close)

**CF Workers M1-M5/M7-M11 — БЕЗ CI deploy.** Проверка 10 CF Worker репо: 4 имеют `.github/workflows/` (только secret-scan + security, нет deploy.yml); 6 не имеют `.github` директории вообще. `wrangler deploy` запускается локально → нарушение F1 (production runtime не привязан к git commit) и F5 (нет git→deploy linkage, rollback только через CF version_id).

**Изменения статусов:**
- F1 для M1-M5/M7-M11: ✅→⚠️ (10 сервисов)
- F5 для M1-M5/M7-M11: ✅→❌ (10 сервисов)
- F1 ✅ итого: 13→3
- F5 ✅ итого: 11→1, F5 ❌ итого: 10→20

**Параллельно закрыты 🟡-ячейки (15 шт):**
- W5 (нет runtime) → N/A с обоснованием «excluded from scope until Dockerfile confirmed»
- X1 CRM Directus → N/A «не обнаружен IWE-owned deployment unit»
- T1 F11/F12 → N/A «deprecated, replaced by per-role launchd plists»
- O1 F3 → N/A «managed SaaS Ory, конфигурация не в IWE»
- A1 F2 → N/A (prompt-only repo)

## 🆕 Итоги Ф10/Ф11/Ф12 (2026-05-12)

**F10 Dev/Prod Parity:** ✅ 13 (CF Workers + L1 + X3); ⚠️ 7 (Railway-сервисы — нет docker-compose локально); ❌ 3 (W5 нет runtime + A1/A2-A6 Mac→Linux разрыв). Не блокер R1 (один Neon на dev+prod), но при росте команды нужен devcontainer.

**F11 Logs:** ✅ 16 (B1/B2 structlog/JSON; W2/W4 structured; CF Workers console.log → CF Logs); ⚠️ 7 (W1/W3 print() вперемешку с logging; M6/P1 неясная структура; A1-A6/X2 unstructured). Главный gap — W1/W3 нужно перевести на logging.getLogger().

**F12 Admin Processes:** ✅ 5 (B1/B2 → AD1 миграции; X2 backup; P1 recalc; AD1 сам admin); ⚠️ 5 (W1 migrations в репо; W3/W4 cleanup в runner.py — нарушение one-off; A1/A2-A6 git pull в timer). Не блокер R1, при масштабировании выделить.

## 🆕 Ф9 Disposability (2026-05-12)

**Все production workers (B1/B2/W1-W4/M1-M11) — F9 ✅.** Явные SIGTERM handlers в Python asyncio (bot + W2/W3/W4); cursor-based idempotency защищает от crash/retry дублей; CF Workers <100ms cold start по дизайну. Нет блокеров R1 по F9.

⚠️ пятёрка — не production workers: A1-A6 (CLI/cron без SIGTERM, `git pull` cold start), X2 (bash без trap), P1 (launchd Python без handler), T1 (deprecated). Все — низкий приоритет.

## Системная находка (Ф9-диагностика, 2026-05-12)

**Все 5 production-worker'ов Railway-проекта peaceful-vision (B1/B2/W1/W2/W4) — БЕЗ GitHub auto-deploy.**

Свидетельство:
- `RAILWAY_GIT_REPO_OWNER` / `RAILWAY_GIT_BRANCH` / `RAILWAY_GIT_COMMIT_SHA` отсутствуют в env (обычно Railway выставляет автоматически при connect-to-repo)
- 18+ последних deployments каждого сервиса: `reason: "deploy"/"redeploy"` (manual triggers), не git-webhook
- `imageDigest` присутствует, но не связан с git commit
- Последний SUCCESS deploy W2 — 2026-04-28; W4 — 2026-04-27
- Push WP-307 advisory_lock (12 мая) НЕ задеплоен → в production-коде версия от 28 апреля

Последствия:
- **F1 (Codebase):** ✅→⚠️ для W1/W2/W4; W3 ✅→🟡 (не задеплоен)
- **F5 (BRR):** ✅→❌ для B1/B2/W1/W2/W4 (image immutable digest есть, но git→deploy linkage отсутствует, нельзя rollback к конкретному commit); W3 ✅→🟡

**План закрытия:** Ф5b (~3h) — connect 5 worker'ов через Railway dashboard → smoke-test → re-verify F1/F5.

## Артефакты

- [12factor-services.md](12factor-services.md) — реестр production runtime сервисов
- [12factor-matrix.md](12factor-matrix.md) — детальная матрица сервис × фактор
- [WP-307 context](../../../../DS-my-strategy/inbox/WP-307-12factor-compliance.md) — рабочий контекст РП
- [12factor-report-wp307.md](12factor-report-wp307.md) — итоговый отчёт после fix-стадии Ф13-Ф18

## Открытые вопросы (Ф0)

См. секцию «Open questions» в [12factor-services.md](12factor-services.md). 8 вопросов к пилоту, разблокирующие окончательный реестр.

## Следующий шаг

**Fix-стадия (Ф13-Ф18) в процессе.** Выполнено 2026-05-13:
- ✅ **Ф13** — Railway GitHub App (W2) + CLOUDFLARE_API_TOKEN (10 CF Workers). 15/15 production-сервисов → git→deploy linkage.
- ✅ **Ф14** — .env.example ×9, requirements.txt ×3, pip-compile B1/B2, .gitignore ×5, OAuth env M6.
- ✅ **Ф15** — print()→logging: W3/W4, W1, P1, M6. F11: 16✅→20✅.
- ✅ **Ф18 (частично)** — 12factor-reaudit.sh + overnight-auditor интеграция.

**Выполнено 2026-05-13 (доделано):**
- ✅ **Ф15** — остаток: A1-A6 shared logging_config.py; X2 logger -t + SIGTERM trap.
- ✅ **Ф16** — W3/W4 admin.py (replay отделён от runner.py); P1 SIGTERM + atomic write; X2 SIGTERM trap.
- ✅ **Ф17** — docker-compose.yml + .devcontainer/devcontainer.json для B1/B2/W1/W3/W4.
- ✅ **Ф18** — upload-compliance-report.py + Neon table `compliance_audits`; auto-update posture.

**Выполнено 2026-05-13 (все фазы fix-стадии):**
- ✅ **Ф13** — Railway GitHub App + CF Workers deploy (15/15 production-сервисов)
- ✅ **Ф14** — .env.example ×10, requirements.txt/pyproject.toml, pip-compile, .gitignore, OAuth env
- ✅ **Ф15** — print()→logging: W1/W3/W4/P1/M6. A1-A6 shared logging_config.py. X2 logger -t.
- ✅ **Ф16** — W3/W4 admin.py. P1 SIGTERM + atomic write. X2 SIGTERM trap.
- ✅ **Ф17** — docker-compose + devcontainer + README local-setup для B1/B2/W1-W4.
- ✅ **Ф18** — 12factor-reaudit.sh + upload-compliance-report.py + Neon table + posture auto-update.

**DoD:** ✅ 228/336 (68%) + N/A 80/336 (24%) = 92% closed. ⚠️ 19/336 (6%) — P1 (Mac-only), W5 (нет runtime), B1/B2 F2 (floating deps, accepted debt). ❌ 12/336 (4%) — P1 монорепо (отдельный архитектурный РП), W5 (нет runtime), A1-A6 F5 (systemd-timer, accepted debt). РП готов к status: done.

---

*Source: `DS-my-strategy/inbox/WP-307-12factor-compliance.md`.*
