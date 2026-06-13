---
date: 2026-06-08
severity: medium
status: open
component: peaceful-vision/hermes-agent
---

# Bug: hermes-agent crash на Railway (8 июня), ~5 дней до восстановления

## Что произошло

Деплой `1a49af1b-f482-4638-b4c5-be61431c2314` сервиса `hermes-agent` (project `peaceful-vision`,
production) крэшнул. Railway прислал письмо «Deploy Crashed» (доставка customer.io пришла
пилоту в Telegram с задержкой — 13 июня ~14:00 МСК).

На момент разбора (13 июня) сервис восстановлен: новый деплой `f4a51b6a-9aed-46d1-8e8a-d9ff232b4112`
создан 13 июня 07:55 UTC, статус **SUCCESS**, подтверждённо живой:
- `GET /health 200 26ms` (07:57:03 UTC)
- `POST /v1/chat/completions 200 8294ms` (08:03:17 UTC) — обработан боевой запрос.

Упавший деплой `1a49af1b` сейчас в статусе **REMOVED** (перекрыт новым).

## Хронология деплоев (Railway API)

```
f4a51b6a  SUCCESS   2026-06-13 07:55:56 UTC   ← текущий, живой
1a49af1b  REMOVED   2026-06-08 14:32:11 UTC   ← крэш из письма
fb051633  REMOVED   2026-06-06 13:00:17 UTC
4e8cecfe  REMOVED   2026-06-06 09:39:21 UTC
dedbaca0  REMOVED   2026-06-04 15:38:38 UTC   ┐
7b14d856  REMOVED   2026-06-04 15:37:57 UTC   │ серия из 4 за ~3 минуты
d8d9e169  REMOVED   2026-06-04 15:36:47 UTC   │ (churn / повторные перезапуски)
121c22aa  REMOVED   2026-06-04 15:35:35 UTC   ┘
```

## Первопричина

**НЕ установлена.** Нужны deploy-логи `1a49af1b` (exit-code, stack trace, OOM-killer,
ошибки подключения к зависимостям). Логи снятого деплоя могут быть недоступны через UI —
проверить retention.

Сигналы для гипотез:
- Серия из 4 REMOVED 4 июня за 3 минуты = быстрые рестарты (crash-loop или ручной churn).
- ~5 дней между крэшем (8 июня) и редеплоем (13 июня) — означает, что автоматического
  восстановления не было; сервис подняли новым деплоем вручную/по push.

## Что НЕ делать

- Кнопку «Restart Deployment» из письма Railway **не нажимать** — она указывает на снятый
  деплой `1a49af1b`, текущий сервис уже здоров.

## Next steps (root-cause, вне scope триаж-сессии)

1. Снять deploy-логи `1a49af1b` (Railway: build + deploy, `level=error`).
2. Определить класс отказа: OOM / unhandled exception / dependency (БД, внешний API) / health-probe fail.
3. Проверить, настроен ли внешний heartbeat/alert на простой hermes-agent — 5 дней даунтайма
   прошли незамеченными (ср. INCIDENT-2026-06-03: «внутренний алерт ≠ внешний heartbeat»).
4. Если crash-loop повторяется — решить вопрос об устойчивости (restart policy, ресурсы).

## Связь

- Источник разбора: peer-session `DS-my-strategy/sessions/2026-06/2026-06-13-25-triage-three-notifications/report.md`
- Различение: «Внутренний алерт (failure) ≠ Внешний heartbeat (dead-man's switch)» (INCIDENT-2026-06-03)
- hermes-agent = Hermes runtime (DP.IWE.001 §5.2)
