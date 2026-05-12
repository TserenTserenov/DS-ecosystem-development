# 12-factor Posture — dashboard состояния

> **WP-307.** Краткое состояние соответствия 12-factor по production runtime.
> Аналог [`security-posture.md`](security-posture.md), но для cloud-native гигиены.
>
> **Обновляется:** при закрытии каждой фазы Ф1-Ф12 WP-307.

## Текущее состояние (2026-05-12, Ф8 завершено)

| Показатель | Значение |
|------------|----------|
| Сервисов в scope | 31 deployment unit + 1 admin (neon-migrations) |
| Бюджет РП | 60h |
| Подход | A — линейный, 12 фаз по фактору |
| Подтверждённых ✅ ячеек | 132 (17 F1 + 12 F2 + 11 F3 + 19 F4 + 17 F5 + 19 F6 + 13 F7 + 23 F8 + 1 AD1 F12) |
| ⚠️ ячеек | 34 (F8 mitigation done: W2/W3 advisory_lock + SCALING.md) |
| ❌ ячеек | 16 (без изменений в Ф8) |
| 🔴 КРИТИЧЕСКИХ (security) | **0** |
| N/A ячеек (обоснованных) | 41 (38 + 3 F8: O1/T1/AD1) |
| 🟡 TBD ячеек | ~113 |
| Прогресс аудита | 8/12 факторов (Ф1-Ф8 ✅ done 2026-05-12) |

## Артефакты

- [12factor-services.md](12factor-services.md) — реестр production runtime сервисов
- [12factor-matrix.md](12factor-matrix.md) — детальная матрица сервис × фактор
- [WP-307 context](../../../../DS-my-strategy/inbox/WP-307-12factor-compliance.md) — рабочий контекст РП

## Открытые вопросы (Ф0)

См. секцию «Open questions» в [12factor-services.md](12factor-services.md). 8 вопросов к пилоту, разблокирующие окончательный реестр.

## Следующий шаг

**Срочно (вне очереди фаз):** M6 google-drive-mcp — ротация секретов + `bfg-repo-cleaner` для очистки `.env` из git history. Линейная очередь:

Ф9 — аудит Factor 9 (Disposability): cold-start < 30s, SIGTERM graceful shutdown, idempotency повторов.

---

*Source: `DS-my-strategy/inbox/WP-307-12factor-compliance.md`.*
