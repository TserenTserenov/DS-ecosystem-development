# 12-factor Posture — dashboard состояния

> **WP-307.** Краткое состояние соответствия 12-factor по production runtime.
> Аналог [`security-posture.md`](security-posture.md), но для cloud-native гигиены.
>
> **Обновляется:** при закрытии каждой фазы Ф1-Ф12 WP-307.

## Текущее состояние (2026-05-12, Ф1 завершено)

| Показатель | Значение |
|------------|----------|
| Сервисов в scope | 31 deployment unit + 1 admin (neon-migrations) |
| Бюджет РП | 60h |
| Подход | A — линейный, 12 фаз по фактору |
| Подтверждённых ✅ ячеек | 18 (17 по F1 + 1 AD1 F12) |
| ⚠️ ячеек | 8 (F1: B1, B2, W5, A1, A2-A6, X1, X3, T1) |
| ❌ ячеек | 1 (F1: P1 — DS-ai-systems монорепо) |
| N/A ячеек (обоснованных) | 10 (F1: O1, AD1; L1 F7; T1 F7/F10; AD1 F1/F5/F6/F7/F8) |
| 🟡 TBD ячеек | ~299 |
| Прогресс аудита | 1/12 факторов (Ф1 F1-Codebase ✅ done 2026-05-12) |
| Критических ❌ | 1 — P1/DS-ai-systems монорепо (блокер масштабирования) |

## Артефакты

- [12factor-services.md](12factor-services.md) — реестр production runtime сервисов
- [12factor-matrix.md](12factor-matrix.md) — детальная матрица сервис × фактор
- [WP-307 context](../../../../DS-my-strategy/inbox/WP-307-12factor-compliance.md) — рабочий контекст РП

## Открытые вопросы (Ф0)

См. секцию «Open questions» в [12factor-services.md](12factor-services.md). 8 вопросов к пилоту, разблокирующие окончательный реестр.

## Следующий шаг

Ф2 — аудит Factor 2 (Dependencies): явные зависимости, pinned versions, lock-файлы, implicit system tool dependencies.

---

*Source: `DS-my-strategy/inbox/WP-307-12factor-compliance.md`.*
