# 12-factor Posture — dashboard состояния

> **WP-307.** Краткое состояние соответствия 12-factor по production runtime.
> Аналог [`security-posture.md`](security-posture.md), но для cloud-native гигиены.
>
> **Обновляется:** при закрытии каждой фазы Ф1-Ф12 WP-307.

## Текущее состояние (2026-05-12, Ф5 завершено)

| Показатель | Значение |
|------------|----------|
| Сервисов в scope | 31 deployment unit + 1 admin (neon-migrations) |
| Бюджет РП | 60h |
| Подход | A — линейный, 12 фаз по фактору |
| Подтверждённых ✅ ячеек | 77 (17 F1 + 12 F2 + 11 F3 + 19 F4 + 17 F5 + 1 AD1 F12) |
| ⚠️ ячеек | 30 (8 F1 + 8 F2 + 11 F3 + 1 F4 + 2 F5) |
| ❌ ячеек | 16 (1 F1 + 6 F2 + 4 F3 + 0 F4 + 5 F5) |
| 🔴 КРИТИЧЕСКИХ (security) | **0** |
| N/A ячеек (обоснованных) | 22 (20 + 2 F5: O1/AD1) |
| 🟡 TBD ячеек | ~191 |
| Прогресс аудита | 5/12 факторов (Ф1+Ф2+Ф3+Ф4+Ф5 ✅ done 2026-05-12) |

## Артефакты

- [12factor-services.md](12factor-services.md) — реестр production runtime сервисов
- [12factor-matrix.md](12factor-matrix.md) — детальная матрица сервис × фактор
- [WP-307 context](../../../../DS-my-strategy/inbox/WP-307-12factor-compliance.md) — рабочий контекст РП

## Открытые вопросы (Ф0)

См. секцию «Open questions» в [12factor-services.md](12factor-services.md). 8 вопросов к пилоту, разблокирующие окончательный реестр.

## Следующий шаг

**Срочно (вне очереди фаз):** M6 google-drive-mcp — ротация секретов + `bfg-repo-cleaner` для очистки `.env` из git history. Линейная очередь:

Ф6 — аудит Factor 6 (Stateless Processes): локальное состояние, in-memory кэш, file-on-disk. Критично для масштабирования R1→R2→R3.

---

*Source: `DS-my-strategy/inbox/WP-307-12factor-compliance.md`.*
