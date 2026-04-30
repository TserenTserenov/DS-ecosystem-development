---
date: 2026-04-30
severity: high
status: open
component: tsekh-1/strategist
---

# Bug: strategist morning 401 auth failure — DayPlan не создан автоматически

## Что произошло

С 03:00 до 06:00 МСК 30 апр strategist.sh падает с `401 Invalid authentication credentials`.
DayPlan 2026-04-30 не создан на сервере — пользователь открыл день вручную в VS Code.

## Логи

```
[2026-04-30 04:00:07] Morning: running day plan
Failed to authenticate. API Error: 401 {"message":"Invalid authentication credentials"}
[2026-04-30 04:00:11] FAILED scenario: day-plan (rc=1)
```

Повторяется во всех dispatch'ах: 03:00, 04:00, 06:00.

## Первопричина

`ANTHROPIC_API_KEY` в `/etc/iwe/env` на tsekh-1 — невалидный или отсутствует.
Сервер поднят 29 апр (WP-138 Ф3), ключ, возможно, не был прописан корректно.

## Вторичная проблема

`OnFailure = "iwe-failure-alert@%n.service"` не сработал — scheduler.service выходит с exit=0
даже при внутренних WARN/FAIL задач. Нет alert о провале критичных задач (morning, note-review).

## Фикс

1. `ssh root@95.216.75.148 "echo 'ANTHROPIC_API_KEY=sk-ant-...' >> /etc/iwe/env"`
2. Проверить все переменные в `/etc/iwe/env` (TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
3. В scheduler.sh: если `strategist-morning` или `strategist-note-review` упали → exit 1 (не 0)
   чтобы `OnFailure` сработал

## Связь

- WP-138 Ф5 (командная инфра tsekh-1) — настройка секретов не была верифицирована
- DP.SC.019 (autonomous cloud runtime) — service clause нарушен (DayPlan не создан)
