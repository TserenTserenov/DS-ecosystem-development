# 12-factor Posture — dashboard состояния

> **WP-307.** Краткое состояние соответствия 12-factor по production runtime.
> Аналог [`security-posture.md`](security-posture.md), но для cloud-native гигиены.
>
> **Обновляется:** при закрытии каждой фазы Ф1-Ф12 WP-307.

## Текущее состояние (2026-05-12, Ф9 завершено)

| Показатель | Значение |
|------------|----------|
| Сервисов в scope | 31 deployment unit + 1 admin (neon-migrations) |
| Бюджет РП | 60h |
| Подход | A — линейный, 12 фаз по фактору |
| Подтверждённых ✅ ячеек | 142 (Ф9 +20: B1/B2/W1-W4/M1-M11/L1/X3/AD1) |
| ⚠️ ячеек | 43 (Ф9 +5: A1/A2-A6/X2/P1/T1) |
| ❌ ячеек | 21 |
| 🔴 КРИТИЧЕСКИХ (security) | **0** |
| N/A ячеек (обоснованных) | 42 (Ф9 +1: O1 F9=N/A managed SaaS) |
| 🟡 TBD ячеек | ~89 (Ф9 -26: 20→✅, 5→⚠️, 1→N/A; остались W5/X1) |
| Прогресс аудита | 9/12 факторов (Ф1-Ф9 ✅; Ф5b открыта — fix-фаза, не audit) |

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

**Ф10 (~3h):** Dev/Prod parity — Docker Compose, версии PG/Python/Node, локальная среда vs production. Затем Ф11 (Logs), Ф12 (Admin Processes).

**Ф5b (fix-фаза, ~3h, в очереди):** GitHub auto-deploy для 5 Railway worker'ов — connect в Railway dashboard. Это ИСПРАВЛЕНИЕ, не audit; выполняется после закрытия оставшихся аудит-фаз или параллельно.

(M6 google-drive-mcp F3 — снято с критики, ложная тревога, см. matrix journal.)

---

*Source: `DS-my-strategy/inbox/WP-307-12factor-compliance.md`.*
