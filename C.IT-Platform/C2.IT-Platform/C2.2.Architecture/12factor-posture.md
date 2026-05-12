# 12-factor Posture — dashboard состояния

> **WP-307.** Краткое состояние соответствия 12-factor по production runtime.
> Аналог [`security-posture.md`](security-posture.md), но для cloud-native гигиены.
>
> **Обновляется:** при закрытии каждой фазы Ф1-Ф12 WP-307.

## Текущее состояние (2026-05-12, Ф2 завершено)

| Показатель | Значение |
|------------|----------|
| Сервисов в scope | 31 deployment unit + 1 admin (neon-migrations) |
| Бюджет РП | 60h |
| Подход | A — линейный, 12 фаз по фактору |
| Подтверждённых ✅ ячеек | 30 (17 F1 + 12 F2 + 1 AD1 F12) |
| ⚠️ ячеек | 16 (8 F1 + 8 F2) |
| ❌ ячеек | 7 (1 F1 + 6 F2) |
| N/A ячеек (обоснованных) | 12 (O1/AD1 F1, X1 F2, O1 F2 + pre-existing) |
| 🟡 TBD ячеек | ~271 |
| Прогресс аудита | 2/12 факторов (Ф1+Ф2 ✅ done 2026-05-12) |
| Критических ❌ | 7 — DS-ai-systems монорепо (F1+F2), W5/M6/A1-A6/X2 (F2 нет manifest) |

## Артефакты

- [12factor-services.md](12factor-services.md) — реестр production runtime сервисов
- [12factor-matrix.md](12factor-matrix.md) — детальная матрица сервис × фактор
- [WP-307 context](../../../../DS-my-strategy/inbox/WP-307-12factor-compliance.md) — рабочий контекст РП

## Открытые вопросы (Ф0)

См. секцию «Open questions» в [12factor-services.md](12factor-services.md). 8 вопросов к пилоту, разблокирующие окончательный реестр.

## Следующий шаг

Ф3 — аудит Factor 3 (Config): секреты вне кода, env vars, hardcoded API keys/URLs/tokens. Самый критичный фактор (security tax).

---

*Source: `DS-my-strategy/inbox/WP-307-12factor-compliance.md`.*
