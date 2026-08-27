---
type: proposal
status: draft
created: 2026-08-27
updated: 2026-08-27
owner: Церен
next_review: 2026-08-29
related: [06-killswitch-runbook.md, 01-scenario.md]
---

# Минимальный след воронки — «Практический семинар по IWE», 30.08.2026

> Источник: пир-сессия Claude+kimi+codex `sessions/2026-08/27/2026-08-27-13-wp514-seminar-3008-prep/`, консенсус по WP-514 Ф4. Карточка WP-514 явно исключает из объёма до 30.08 «универсальный агрегатор следа» и новый тип события — эта спецификация нового кода не требует: только конфигурация/сверка существующего (`reference.reward_rules`, `applied_events`) плюс два ручных TSV-чекпоинта.

## Идентификаторы корреляции

- `participant_id` — один псевдоним участника, единый во всех источниках (платёж, чат, диагностика, баллы, след).
- `session_id` — выдаётся в начале прохода участника, переносится в webhook metadata (WP-446), reward payload и обе ручные записи ниже.

## Таблица sanity-check по 7 этапам воронки

| Этап | Источник | Условие `pass` |
|---|---|---|
| `payment` | запись платёжного контура WP-446 | успешная тестовая оплата связана с `participant_id`/`session_id` |
| `receipt` | журнал webhook WP-446 | доставка чека имеет тот же correlation key и успешный конечный статус |
| `chat` | ID/URL claude.ai-диалога | диалог зафиксирован в `evidence_ref`, сопоставлен с той же парой идентификаторов |
| `diagnosis` | `applied_events`, `event_type='cp_assessment_recorded'` | найдена применённая запись диагностики |
| `points` | та же запись `applied_events` + `reference.reward_rules` | правило `cp_assessment_recorded` включено, начисление применено без ошибки |
| `trace` | `applied_events`, `event_type='space_created'` | событие применено, `evidence_ref` указывает на созданное пространство/репозитории |
| `generalization` | `decision_change_3008.tsv` (см. ниже) | записано изменение решения + ссылка на след |

Статус каждой строки — `pass` / `fail` / `not_observed`. Отсутствие evidence — `fail` или `not_observed`, не подразумеваемый успех.

## Sanity-check конфигурации (перед эфиром)

```sql
SELECT event_type, enabled
FROM reference.reward_rules
WHERE event_type IN ('space_created', 'cp_assessment_recorded');
```

## Выгрузка `applied_events` за окно семинара

Привести реальные колонки к обязательным алиасам:

```text
source_record_id, occurred_at, participant_id, session_id,
event_type, application_status, reward_rule_id, reward_delta, evidence_ref
```

**Открыто:** физическое имя таблицы/колонок платёжного контура WP-446 в доступной агенту проекции не определено — владелец WP-446 вписывает фактическое имя relation и сопоставляет поля с теми же алиасами до репетиции 28-29.08.

## Итоговый артефакт `funnel_3008.tsv`

Одна строка на этап на участника:

```text
participant_id
session_id
stage
status                 # pass | fail | not_observed
occurred_at
source_table
source_record_id
event_type
evidence_ref
note
```

## Ручной чекпоинт `decision_change_3008.tsv`

Одна строка на участника после прохода:

```text
participant_id
session_id
before_statement
decision_change
next_action
trace_ref
recorded_at
recorded_by
```
