---
id: DP.RUNBOOK.002
name: "Runbook: L2.5 outbox-replay"
type: domain-entity
status: active
summary: "Procedure для restore parity между journal и проекциями consumer'ов (rewards / publication / lead) при drift 0.5-1% — Playbook L2.5 из DP.ROADMAP.001 §10"
created: 2026-04-25
trust:
  F: 4
  G: domain
  R: 0.8
epistemic_stage: validated
related:
  - id: DP.ROADMAP.001
    type: realizes
  - id: DP.ROLE.034
    type: uses
---

# Runbook: L2.5 outbox-replay

## 1. Когда применять

**Триггер:** drift между journal и проекцией consumer'а 0.5-1% (между L2 revert и L3 Neon backup).

| delta_pct | Что делать |
|-----------|-----------|
| < 0.1% | Норма, действий не требуется |
| 0.1-1% | **L2.5 outbox-replay** (этот runbook) |
| 1-5% | L2.5 replay → если delta после ≥ 0.1% → L3 (Neon PITR) |
| > 5% | L3 (Neon PITR) сразу + post-mortem |

**Источник сигнала:**
- Дневной cron: `count-parity.sql` → Grafana → TG-алерт.
- Ручной запуск перед cut-over reader switch.
- Подозрение на bug в projection-worker (исследование).

## 2. Pre-flight checks

```bash
# 1. Какой consumer пострадал?
psql "$DATABASE_URL_REWARDS" -v consumer=rewards -v window_hours=24 -f count-parity.sql
psql "$DATABASE_URL_PUBLICATION" -v consumer=publication -v window_hours=24 -f count-parity.sql
psql "$DATABASE_URL_LEAD" -v consumer=lead -v window_hours=24 -f count-parity.sql

# 2. Зафиксировать current watermark consumer'а — на случай отката
psql "$DATABASE_URL_REWARDS" -c "SELECT MAX(event_id) FROM rewards.processed_events WHERE consumer_name='rewards';"

# 3. Проверить что projection-worker не работает в фоне
# (replay должен быть атомарным — никто не пишет параллельно)
psql "$DATABASE_URL_REWARDS" -c "SELECT pid, query, state FROM pg_stat_activity WHERE query LIKE '%processed_events%' AND state='active';"
# Ожидаем 0 rows — иначе остановить projection-worker через Railway / kill -9
```

## 3. Procedure

### Шаг 1. Dry-run

```bash
cd /opt/neon-migrations/scripts  # или DS-IT-systems/neon-migrations/scripts
python3 outbox_replay.py --consumer rewards --since 0 --dry-run
```

Ожидаемый вывод:
```
acquired advisory lock: outbox-replay-rewards
chunk #1: ... events
[DRY-RUN] done: replayed=N skipped_idempotent=M chunks=K duration_ms=...
```

`replayed` показывает сколько событий нужно реплеить. Если N=0 — drift вызван не пропуском, а другой причиной (bug в apply-логике, неправильный watermark, etc.) → НЕ запускать replay, эскалация в L3 + post-mortem.

### Шаг 2. Real replay

Если dry-run показал ожидаемое replayed=N (равно delta из count-parity.sql):

```bash
python3 outbox_replay.py --consumer rewards --since 0
```

Длительность: ~22ms на 1000 событий (sandbox). На 100k событий ≈ 4-5 минут на Neon (network latency × per-row INSERT). Для очень больших replay (>1M) — увеличить chunk-size:

```bash
python3 outbox_replay.py --consumer rewards --since 0 --chunk-size 50000
```

### Шаг 3. Verify

```bash
psql "$DATABASE_URL_REWARDS" -v consumer=rewards -v window_hours=24 -f count-parity.sql
```

Ожидаем `delta_pct < 0.1`. Если ≥ 0.1 — replay не сработал полностью; проверить:
- `pg_advisory_lock` отпущен? (`SELECT pg_advisory_unlock_all();` от того же session)
- `replay_log` показывает что replay завершился?
- Есть ли apply-функция bug? (для rewards — точно ли начисляет правильные points?)

### Шаг 4. Перезапустить projection-worker

После replay PASS — projection-worker возвращается в строй.

> **Update 2026-05-17 (WP-311 Ф-Close):** production projection-worker = `multi-domain-projection-worker` в проекте `attractive-optimism` (legacy `rewards-projection-worker` в `peaceful-vision` decommission'd).

```bash
railway --service multi-domain-projection-worker restart
# Verify он LISTEN'ит / cursor движется:
railway --service multi-domain-projection-worker logs --tail 20 | grep -E "LISTEN|cursor"
```

Проверить что новые события идут:
```bash
psql "$DATABASE_URL_JOURNAL" -c "INSERT INTO learning.domain_event(source, external_id, type, payload, ts) VALUES ('manual-test', 'replay-verify-$(date +%s)', 'lesson_completed', '{}', NOW());"

# Через 1-2 секунды:
psql "$DATABASE_URL_REWARDS" -c "SELECT * FROM rewards.processed_events ORDER BY processed_at DESC LIMIT 1;"
```

## 4. Rollback (если что-то пошло не так)

L2.5 replay через `ON CONFLICT DO NOTHING RETURNING` идемпотентен — повторный запуск безопасен (пропустит уже обработанные события). Для отката:

1. **Откат processed_events:** не нужен — replay только добавляет, не удаляет.
2. **Откат point_balances:** если apply начислил больше чем нужно (bug в apply-логике), идти в L3 (Neon PITR на момент до replay).
3. **Forensic из replay_log:**
   ```sql
   SELECT * FROM rewards.replay_log ORDER BY started_at DESC LIMIT 5;
   ```

## 5. Post-mortem (всегда после L2.5)

После L2.5 replay создать инцидент в `C2.3.Operations/Incidents/<YYYY-MM-DD>-l2.5-replay-<consumer>.md`:

```markdown
# Incident: L2.5 replay для <consumer> (YYYY-MM-DD)

## Что
- Drift detection: <delta_pct>%, <delta> events за <window>
- Replay: replayed=<N>, skipped_idempotent=<M>, duration=<ms>ms
- Verify post-replay: delta_pct=<X>%

## Почему
- Корневая причина drift'а
- Какой bug в projection-worker / cut-over / network

## Что изменили
- Fix в коде (commit hash)
- Adjustment в monitoring / threshold
- KE candidate
```

## 6. Escalation

| Условие | Действие |
|---------|----------|
| Lock не берётся (другой replay висит) | Проверить `pg_locks` + kill заглохшую сессию |
| `replayed=0` при non-zero delta | Stop, эскалация в L3 + post-mortem (drift НЕ из-за пропуска) |
| `delta_pct ≥ 0.1` после replay | Stop, эскалация в L3 (Neon PITR) |
| Replay >30 мин | Прервать, увеличить chunk-size, повторить |

## 7. Связанные документы

- [DP.ROADMAP.001 §10 Playbook L2.5](../../../../../PACK-digital-platform/pack/digital-platform/02-domain-entities/DP.ROADMAP.001-neon-migration.md)
- [Sandbox L2.5 валидация](../../../../../DS-IT-systems/neon-migrations/sandbox/L2.5-outbox-replay/README.md)
- [outbox_replay.py production](../../../../../DS-IT-systems/neon-migrations/scripts/outbox_replay.py)
- [count-parity.sql](../../../../../DS-IT-systems/neon-migrations/scripts/count-parity.sql)

## 8. История

| Дата | Версия | Что |
|------|--------|-----|
| 2026-04-25 | v0.1 | Создан после ArchGate v3 PASS + L2.5 sandbox PASS (DP.ROADMAP.001 §10). Готов к использованию в P2+ multi-consumer фазах. |
