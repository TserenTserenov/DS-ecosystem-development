# 12-factor Posture — dashboard состояния

> **WP-307.** Краткое состояние соответствия 12-factor по production runtime.
> Аналог [`security-posture.md`](security-posture.md), но для cloud-native гигиены.
>
> **Обновляется:** при закрытии каждой фазы Ф1-Ф12 WP-307.

## Текущее состояние (2026-05-12, audit-фаза закрыта + VR.R.001 fold-back)

| Показатель | Значение |
|------------|----------|
| Сервисов в scope | 28 deployment unit + 1 admin (neon-migrations) |
| Всего ячеек | 336 (28 × 12) |
| Бюджет РП | 60h |
| Подход | A — линейный, 12 фаз по фактору |
| Подтверждённых ✅ ячеек | **155** (46%) |
| ⚠️ ячеек | **71** (21%) |
| ❌ ячеек | **33** (10%) |
| N/A ячеек (обоснованных) | **74** (22%) |
| 🟡 TBD ячеек (legit pending) | **3** (1% — W3 F1/F5, X2 F4) |
| 🔴 КРИТИЧЕСКИХ (security) | **0** |
| Прогресс аудита | **12/12 факторов закрыто.** VR.R.001 fold-back применён (CF Workers F1/F5 → ⚠️/❌) |
| DoD | НЕ достигнут — 31% ячеек violations. Закрытие WP-307 как **audit-completed**; fixes выделены в отдельные РП |

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

## Открытые вопросы (Ф0)

См. секцию «Open questions» в [12factor-services.md](12factor-services.md). 8 вопросов к пилоту, разблокирующие окончательный реестр.

## Следующий шаг

**Audit-фаза закрыта 2026-05-12.** Остаётся:

**Ф-Close (~0.5h):** VR.R.001 верификация матрицы (Sonnet sub-agent с эталоном 12factor.net) + ArchGate review (ЭМОГССБ) + Capture-to-Pack (что добавить в PACK-digital-platform).

**Ф5b (fix-фаза, ~3h, в очереди вне audit-scope):** GitHub auto-deploy для 5 Railway worker'ов — connect в Railway dashboard. Закрывает F1/F5 gap для B1/B2/W1/W2/W4.

**Дальше — fix-фазы по приоритету (не входят в WP-307, выделяются в новые РП):**
1. F11 W1/W3 print()→logging (~2h, простой быстрый win)
2. F10 docker-compose для Railway-сервисов (~4h, повышает onboarding speed)
3. F12 W3/W4 admin CLI выделение (~3h, нужно при scaling > R1)
4. F5 A1-A6 containerization (~6h, большая работа, ждёт R2 когорту)

(M6 google-drive-mcp F3 — снято с критики, ложная тревога, см. matrix journal.)

---

*Source: `DS-my-strategy/inbox/WP-307-12factor-compliance.md`.*
