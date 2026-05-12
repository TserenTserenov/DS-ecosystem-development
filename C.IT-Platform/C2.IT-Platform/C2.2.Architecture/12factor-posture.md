# 12-factor Posture — dashboard состояния

> **WP-307.** Краткое состояние соответствия 12-factor по production runtime.
> Аналог [`security-posture.md`](security-posture.md), но для cloud-native гигиены.
>
> **Обновляется:** при закрытии каждой фазы Ф1-Ф12 WP-307.

## Текущее состояние (2026-05-12, Ф7 завершено)

| Показатель | Значение |
|------------|----------|
| Сервисов в scope | 31 deployment unit + 1 admin (neon-migrations) |
| Бюджет РП | 60h |
| Подход | A — линейный, 12 фаз по фактору |
| Подтверждённых ✅ ячеек | 109 (17 F1 + 12 F2 + 11 F3 + 19 F4 + 17 F5 + 19 F6 + 13 F7 + 1 AD1 F12) |
| ⚠️ ячеек | 34 (без изменений в Ф7) |
| ❌ ячеек | 16 (без изменений в Ф7) |
| 🔴 КРИТИЧЕСКИХ (security) | **0** |
| N/A ячеек (обоснованных) | 38 (25 + 13 F7: W1-W4/M6/L1/O1/A1-A6/X2/P1/T1/AD1) |
| 🟡 TBD ячеек | ~139 |
| Прогресс аудита | 7/12 факторов (Ф1-Ф7 ✅ done 2026-05-12) |

## Артефакты

- [12factor-services.md](12factor-services.md) — реестр production runtime сервисов
- [12factor-matrix.md](12factor-matrix.md) — детальная матрица сервис × фактор
- [WP-307 context](../../../../DS-my-strategy/inbox/WP-307-12factor-compliance.md) — рабочий контекст РП

## Открытые вопросы (Ф0)

См. секцию «Open questions» в [12factor-services.md](12factor-services.md). 8 вопросов к пилоту, разблокирующие окончательный реестр.

## Следующий шаг

**Срочно (вне очереди фаз):** M6 google-drive-mcp — ротация секретов + `bfg-repo-cleaner` для очистки `.env` из git history. Линейная очередь:

Ф8 — аудит Factor 8 (Concurrency): web/worker разделение, можно ли запустить N replicas без race conditions.

---

*Source: `DS-my-strategy/inbox/WP-307-12factor-compliance.md`.*
