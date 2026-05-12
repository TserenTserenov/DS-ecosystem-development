# 12-factor Posture — dashboard состояния

> **WP-307.** Краткое состояние соответствия 12-factor по production runtime.
> Аналог [`security-posture.md`](security-posture.md), но для cloud-native гигиены.
>
> **Обновляется:** при закрытии каждой фазы Ф1-Ф12 WP-307.

## Текущее состояние (2026-05-12, Ф0 завершено)

| Показатель | Значение |
|------------|----------|
| Сервисов в scope | 31 deployment unit + 1 admin (neon-migrations) |
| Бюджет РП | 60h (поднят с 30h после инвентаризации) |
| Подход | A — линейный, 12 фаз по фактору |
| Подтверждённых ✅ ячеек | 0 / 372 |
| ⚠️ ячеек | 0 |
| ❌ ячеек | 0 |
| 🟡 TBD ячеек | ~365 (с учётом N/A) |
| Прогресс аудита | 0% (Ф0 — инвентаризация) |

## Артефакты

- [12factor-services.md](12factor-services.md) — реестр production runtime сервисов
- [12factor-matrix.md](12factor-matrix.md) — детальная матрица сервис × фактор
- [WP-307 context](../../../../DS-my-strategy/inbox/WP-307-12factor-compliance.md) — рабочий контекст РП

## Открытые вопросы (Ф0)

См. секцию «Open questions» в [12factor-services.md](12factor-services.md). 8 вопросов к пилоту, разблокирующие окончательный реестр.

## Следующий шаг

Ф1 — аудит Factor 1 (Codebase) по подтверждённым сервисам (B1, B2, M1, M2, L1) после прояснения scope.

---

*Source: `DS-my-strategy/inbox/WP-307-12factor-compliance.md`.*
