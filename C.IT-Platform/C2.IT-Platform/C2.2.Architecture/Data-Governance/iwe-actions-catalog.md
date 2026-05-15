---
family: F5
kernel: C
system: C2
role: Architecture
status: active
created: 2026-05-05
valid_from: 2026-05-07
updated: 2026-05-07
related:
  source: "WP-214"
  depends_on: [DP.SC.020, DP.ARCH.004]
---

# Каталог действий IWE: события, хранение, баллы

> **Назначение.** Полный реестр действий пользователя в IWE-среде — с маппингом на event_type, источник сигнала, базу хранения и правила начисления баллов. Основа для Ф8 (правила баллов) и Ф9 (связь с personal-guide).
>
> **Принцип учёта:** каждое значимое действие → `domain_event` (Neon learning). Источник сигнала может быть разным (git-hook, Claude Code hook, cron, bot), но канал единый — `event-gateway` (DP.SC.020).

---

## 0. Сводный реестр событий

> **Онтологическая организация:** события упорядочены по тому, *что они сигнализируют* о человеке (характеристика ступени), а не по источнику-инструменту.
> §2 ниже содержит legacy-организацию по эмиттерам — оставлена для справки об архитектуре источников.
> Псевдонимы `day_open` / `day_close` = legacy-alias для `day_plan_opened` / `day_plan_closed`, поддерживаются в SELF_DEV_EVENT_TYPES.
> Хранение всех активных событий: `learning.domain_event` (Neon), канал — `event-gateway` (DP.SC.020).

| Название | `event_type` | Характеристика(и) | Где возникает | Статус | Источник |
|---|---|---|---|---|---|
| День открыт | `day_plan_opened` | Систематичность | Day Open завершён | ✅ | ОРЗ-хук (Stop) |
| День закрыт | `day_plan_closed` | Систематичность | Day Close завершён | ✅ | ОРЗ-хук (Stop) |
| Сессия Claude Code | `iwe_session` | Систематичность | Сессия ≥5 мин | ✅ | ОРЗ-хук (Stop) |
| Урок завершён | `lesson_completed` | Систематичность, Инвестированное время, Методичность | LMS, прохождение урока | ✅ | Bridge-2 |
| Экстракция знания | `knowledge_extracted` | Систематичность, Методичность, Системность мировоззрения | /ke завершён | ✅ | ОРЗ-хук (Stop) |
| Неделя закрыта | `week_plan_closed` | Систематичность, Системность мировоззрения | Week Close завершён | ✅ | ОРЗ-хук (Stop) |
| Месяц закрыт | `month_plan_closed` | Систематичность, Системность мировоззрения | Month Close завершён | ✅ | ОРЗ-хук (Stop) |
| Стратегическая сессия | `strategy_session_completed` | Систематичность, Системность мировоззрения, Агентность | /strategy-session | ✅ | ОРЗ-хук (Stop) |
| Время в редакторе | `coding_time` | Инвестированное время | WakaTime, IDE активность | ✅ | iwe.py adapter |
| Слот залогирован | `slot_logged` | Инвестированное время | /slot в боте | ✅ | aist-bot |
| Pack обновлён | `pack_updated` | Методичность, Системность мировоззрения | Коммит в PACK-* | ✅ | git hook (post-commit) |
| Квалификация получена | `qualification_granted` | Методичность | LMS, завершение программы | ⚠️ Gap-В | Bridge-2 (не реализовано) |
| РП зарегистрирован | `wp_created` | Агентность | Создание WP-NNN файла | ✅ | ОРЗ-хук (PostToolUse) |
| РП закрыт | `wp_closed` | Агентность | Закрытие РП | ✅ | ОРЗ-хук (Stop) |
| Пост в клубе | `club_post_created` | Методичность | Публикация поста | ❌ WP-296 | WP-296 ingestor |
| Тема в клубе | `club_topic_created` | Агентность | Создание темы в клубе | ❌ WP-296 | WP-296 ingestor |
| Коммит | `git_commit` | Служебное | Любой git commit | ✅ | git hook (post-commit) |
| Платёж принят | `payment_received` | Служебное | LMS, оплата | ✅ | Bridge-2 |
| Команда вызвана | `command_invoked` | Служебное | Любая команда в боте | ✅ | aist-bot |
| Файл отредактирован | `file_edited` | Служебное (практика) | Edit/Write в IWE | ❌ | Claude Code hook |
| Исследование | `iwe_research` | Служебное (практика) | WebSearch в IWE | ❌ | Claude Code hook |
| Git push | `git_push` | Служебное | git push | ❌ | git post-push hook |

> `lesson_completed` входит в Инвестированное время через `payload.duration_minutes`; в Систематичность — как факт дня саморазвития.
> `strategy_session_completed` входит в Агентность как собственная стратегическая инициатива.

---

## 1. Классификация действий

Все действия делятся на **6 категорий**. Категория определяет множитель баллов.

| Категория | Множитель | Смысл |
|-----------|-----------|-------|
| `time` | 1.0× | Время за работой (трекинг WakaTime, слоты) |
| `wp` | 2.0× | Создание/закрытие рабочих продуктов |
| `quality` | 3.0× | Рефлексия, верификация, экстракция знания |
| `platform` | 5.0× | Протоколы ОРЗ, стратегирование |
| `condition` | 0.0× | Условные (не начисляются без combo) |
| `none` | 0.0× | Служебные, не начисляются |

---

## 2. Полный каталог (по эмиттерам, legacy)

> **Онтологический реестр (что сигнализирует):** см. **§0** выше.
> Этот раздел организован по источнику сигнала (ОРЗ / WP / Git / Учёба / Клуб / Бот) — полезен для понимания архитектуры эмиттеров, но НЕ является онтологически правильной классификацией.

> **Колонка `activity_domain`** добавлена в `domain_event` (решение WP-214, 7 мая). Значения: `learning` / `practice` / `work`. Влияет на ступень Ученика (программа «Личное развитие»): только `learning + practice`. `work` — баллы, но не stage_raw.

### 2.1 Протоколы ОРЗ

| Действие | event_type | activity_domain | Источник сигнала | Категория | base_points |
|----------|-----------|-----------------|-----------------|-----------|-------------|
| Day Open завершён | `day_plan_opened` | `practice` | Claude Code hook Stop (/day-open) | `platform` | 15 |
| Day Close завершён | `day_plan_closed` | `practice` | Claude Code hook Stop (/day-close) | `platform` | 20 |
| Week Close завершён | `week_plan_closed` | `practice` | Claude Code hook Stop (/week-close) | `platform` | 30 |
| Month Close завершён | `month_plan_closed` | `practice` | Claude Code hook Stop (/month-close) | `platform` | 50 |
| Strategy Session завершена | `strategy_session_completed` | `learning` | Claude Code hook Stop (/strategy-session) | `platform` | 40 |
| KE (экстракция знания) | `knowledge_extracted` | `learning` | Claude Code hook Stop (/ke) | `quality` | 25 |

**Статус (✅ 5 май):** все эмитятся через iwe-orz-tracker.sh Stop-хук.

---

### 2.2 Рабочие продукты (WP)

| Действие | event_type | activity_domain | Источник сигнала | Категория | base_points |
|----------|-----------|-----------------|-----------------|-----------|-------------|
| WP зарегистрирован | `wp_created` | `practice` | iwe-wp-tracker.sh PostToolUse | `wp` | 30 |
| WP закрыт (IWE governance) | `wp_closed` | `practice` | iwe-orz-tracker.sh Stop | `wp` | 80 |
| WP закрыт (продуктовые репо) | `wp_closed` | `work` | iwe-orz-tracker.sh Stop | `wp` | 80 |
| WP заблокирован | `wp_blocked` | `practice` | manual / strategy-session | `none` | 0 |

> `wp_closed` классифицируется по `reference.repo_domain_map`: governance-репо → `practice`, DS-IT/DS-MCP → `work`.

**Статус (✅ 5 май):** wp_created + wp_closed работают (Worker 79e39dbb). Классификация по repo_domain_map — pending (Ф10.5).

---

### 2.3 Работа в редакторе (Claude Code)

| Действие | event_type | activity_domain | Источник сигнала | Категория | base_points |
|----------|-----------|-----------------|-----------------|-----------|-------------|
| Сессия Claude Code (≥5 мин) | `iwe_session` | `practice` | iwe-orz-tracker.sh Stop | `time` | 10 |
| Редактирование файла | `file_edited` | `practice` | PostToolUse hook (Edit/Write) | `time` | 3 |
| Исследование | `iwe_research` | `practice` | PostToolUse hook (WebSearch) | `time` | 2 |

**Статус:** `iwe_session` ✅ (Stop-хук). `file_edited` / `iwe_research` — ❌ backlog.

---

### 2.4 Git-действия

| Действие | event_type | activity_domain | Источник сигнала | Категория | base_points |
|----------|-----------|-----------------|-----------------|-----------|-------------|
| Commit (governance/Pack-репо) | `git_commit` | `practice` | global post-commit hook | `wp` | 20 |
| Commit (продуктовые репо) | `git_commit` | `work` | global post-commit hook | `wp` | 20 |
| Pack обновлён | `pack_updated` | `practice` | global post-commit hook (PACK-*) | `quality` | 30 |
| Git push | `git_push` | `practice`/`work` | post-push hook | `wp` | 10 |

> domain определяется через `reference.repo_domain_map` по `repo` в payload.

**Статус (✅ 5 май):** git_commit + pack_updated — global git template работает.

---

### 2.5 Учёба (из LMS)

| Действие | event_type | activity_domain | Источник сигнала | Категория | base_points |
|----------|-----------|-----------------|-----------------|-----------|-------------|
| Урок завершён | `lesson_completed` | `learning` | Bridge-2 (poll 15 мин) | `time` | 40 |
| Квалификация получена | `qualification_granted` | `learning` | Bridge-2 | `quality` | 200 |
| Платёж принят | `payment_received` | `none` | Bridge-2 | `none` | 0 |

**Статус:** ✅ Работает через Bridge-2.

---

### 2.6 Клуб (Discourse)

| Действие | event_type | activity_domain | Источник сигнала | Категория | base_points |
|----------|-----------|-----------------|-----------------|-----------|-------------|
| Пост в клубе | `club_post_created` | `learning` | WP-296 ingestor | `quality` | 15 |
| Тема в клубе | `club_topic_created` | `learning` | WP-296 ingestor | `quality` | 20 |

**Статус (WP-296):** Ф1-Ф3 ✅ (schema, SC.128, ROLE.036). Ф4 ingestor — ждёт ORY-SSO.

---

### 2.7 Бот-команды (aist-bot)

| Действие | event_type | activity_domain | Источник сигнала | Категория | base_points |
|----------|-----------|-----------------|-----------------|-----------|-------------|
| Слот залогирован | `slot_logged` | `practice` | aist-bot inline | `time` | 10×duration_min |
| Команда вызвана | `command_invoked` | `practice` | aist-bot inline | `time` | 5 |
| Рефлексия через бота | `bot_reflection` | `practice` | aist-bot | `quality` | 15 |

**Статус:** ✅ `slot_logged` и `command_invoked` работают.

---

## 3. Матрица покрытия (актуально на 7 мая 2026)

```
РАБОТАЕТ (✅)                                 BACKLOG (❌)
──────────────────────────────────────────    ─────────────────────
lesson_completed      Bridge-2                file_edited
qualification_granted Bridge-2                iwe_research
payment_received      Bridge-2                git_push
slot_logged           bot inline              club_post_created (ждёт ORY-SSO)
command_invoked       bot inline              club_topic_created (ждёт ORY-SSO)
day_plan_opened       iwe-orz-tracker Stop
day_plan_closed       iwe-orz-tracker Stop
week_plan_closed      iwe-orz-tracker Stop
month_plan_closed     iwe-orz-tracker Stop
strategy_session_completed  iwe-orz-tracker
knowledge_extracted   iwe-orz-tracker Stop
iwe_session           iwe-orz-tracker Stop
git_commit            global post-commit hook
pack_updated          global post-commit hook
wp_created            iwe-wp-tracker PostToolUse
wp_closed             iwe-orz-tracker Stop

PENDING (⏳ activity_domain classification)
───────────────────────────────────────────
wp_closed / git_commit — domain по repo_domain_map (Ф10.5 WP-214)
```

---

## 4. Архитектура эмиттеров

Три типа источников сигнала:

### Тип A: Claude Code Hook (IWE-харнесс)
- **Когда:** PostToolUse, Stop, UserPromptSubmit
- **Как:** `.claude/hooks/` скрипт читает harness JSON → формирует event payload → POST event-gateway
- **Примеры:** day_plan_opened, wp_created, iwe_session, file_edited
- **Готовность:** каркас есть (capture-bus.sh), нужно добавить detector'ы для IWE-событий

### Тип B: Git Hook
- **Когда:** post-commit, post-push
- **Как:** `~/.git-templates/hooks/post-commit` → git log --format → POST event-gateway
- **Примеры:** git_commit, pack_updated
- **Готовность:** ✅ global post-commit hook работает (5 май)

### Тип C: External Source (Bridge-2, bot)
- **Когда:** cron / inline в боте
- **Как:** уже реализовано через event_emitter.py / inline bot handler
- **Примеры:** lesson_completed, slot_logged
- **Готовность:** ✅ работает

---

## 5. Статус реализации (7 мая 2026)

### DONE (✅)
1. **iwe-orz-tracker.sh Stop-хук** — week_plan_closed, month_plan_closed, strategy_session_completed, knowledge_extracted, iwe_session, wp_closed
2. **iwe-wp-tracker.sh PostToolUse** — wp_created (inbox/WP-NNN-*.md)
3. **global post-commit hook** — git_commit, pack_updated (`~/.git-templates/hooks/post-commit`)
4. **Bridge-2** — lesson_completed, qualification_granted, payment_received
5. **Bot inline** — slot_logged, command_invoked

### PENDING (⏳ WP-214 Ф10)
6. **reference.repo_domain_map** — таблица классификации репозиториев (Ф10.5): нужна чтобы domain_event.activity_domain заполнялась корректно для git_commit / wp_closed
7. **Backfill activity_domain** — для исторических событий (при миграции колонки)

### BACKLOG (❌)
8. **club_post_created / club_topic_created** — WP-296 Ф4 (ждёт ORY-SSO Discourse)
9. **file_edited / iwe_research** (~2h): детекторы в capture-bus
10. **git_push** (~30 мин): post-push hook в git-templates

---

## 6. Схема event payload (стандартный для всех IWE-событий)

```json
{
  "source": "iwe-hooks",
  "external_id": "{event_type}-{session_id}-{timestamp_ms}",
  "event_type": "...",
  "occurred_at": "2026-05-05T10:00:00Z",
  "payload": {
    "project": "DS-my-strategy",
    "cwd": "/Users/tserentserenov/IWE/DS-my-strategy",
    "...": "специфичные поля события"
  }
}
```

**Идемпотентность:** `(source, external_id)` — уникальный ключ в `domain_event`.
**Авторизация:** service token для `iwe-hooks` source (не OAuth, не per-user JWT — это машинный источник).

---

## 7. Attribution: маппинг событий → характеристики ступени

> **Назначение.** Конфигурация весов для MVP авто-расчёта ступени по 5-характеристичной модели (FORM.089 §12, WP-310).
> **Потребитель:** `stage_evaluator.py` в activity-hub. Веса — числа очков за одно событие. Нормализация — в вычислителе.

### 7.1 Систематичность (`self_dev_days_per_week`)

**Смысл:** регулярность саморазвития, а не любой IWE-активности. Учитываются только дни с целенаправленным обучением или рефлексией.

**Принцип:** окно расчёта зависит от текущей ступени пользователя (`i.accounting_period`):

| Ступень | Окно SQL |
|---|---|
| Случайный (1) | `INTERVAL '7 days'` |
| Практикующий (2) | `INTERVAL '28 days'` |
| Систематический (3) | `INTERVAL '56 days'` |
| Дисциплинированный (4) | `INTERVAL '84 days'` |
| Проактивный (5) | `INTERVAL '168 days'` |

```sql
-- Шаблон: подставить окно под текущую ступень пользователя
SELECT COUNT(DISTINCT DATE(occurred_at))::float / {accounting_weeks} AS self_dev_days_per_week
FROM domain_event
WHERE account_id = %s::uuid
  AND event_type = ANY(ARRAY[
    'lesson_completed', 'knowledge_extracted', 'pack_updated', 'qualification_granted',
    'day_plan_opened', 'day_open',         -- day_open = legacy alias (iwe.py)
    'day_plan_closed', 'day_close',        -- day_close = legacy alias (ORZ hook)
    'week_plan_closed', 'month_plan_closed',
    'strategy_session_completed', 'iwe_session'
  ])
  AND occurred_at >= NOW() - INTERVAL '{accounting_weeks * 7} days'
```

**НЕ входят:** `git_commit`, `coding_time`, `wp_created`, `wp_closed`, `wp_completed`, `command_invoked`, `slot_logged`, `club_post_created`.

> **Gap-Д:** текущий rcs-collector (`recalculate_derived.py`) использует `activity_domain IN ('practice', 'learning')` — шире SELF_DEV_EVENT_TYPES. Аттестатор требует отдельного запроса. Фикс — Ф4+ WP-310.
>
> **Gap-Б (minor):** legacy aliases `day_close`/`day_open` в ORZ hook и iwe.py. Поддерживать оба до миграции.

### 7.2 Инвестированное время (`avg_hours_per_week`)

Суммируются часы из источников за окно текущей ступени (аналогично §7.1), делятся на `accounting_weeks`.

| Источник | event_type | Поле payload | Формула |
|----------|-----------|-------------|---------|
| WakaTime | `coding_time` | `payload.total_seconds` | `/ 3600` |
| Бот-слоты | `slot_logged` | `payload.hours` | прямо |
| Обучение LMS | `lesson_completed` | `payload.duration_minutes` | `/ 60` |
| Day Close bonus | `day_close` | `payload.wakatime_h` | прямо (если WakaTime не подключён) |

```sql
SELECT COALESCE(SUM(hours), 0) / 4.0 AS avg_per_week FROM (
  SELECT (payload->>'total_seconds')::float / 3600 AS hours
    FROM domain_event WHERE event_type = 'coding_time'
      AND occurred_at > NOW() - INTERVAL '28 days'
  UNION ALL
  SELECT (payload->>'hours')::float
    FROM domain_event WHERE event_type = 'slot_logged'
      AND occurred_at > NOW() - INTERVAL '28 days'
  UNION ALL
  SELECT (payload->>'duration_minutes')::float / 60
    FROM domain_event WHERE event_type = 'lesson_completed'
      AND occurred_at > NOW() - INTERVAL '28 days'
) t
```

Нормализация в индекс 0–5: < 1 ч/нед → 0 / 1–2 → 1 / 2–5 → 2 / 5–8 → 3 / 8–12 → 4 / > 12 → 5.

> **Аудит Ф1:** WakaTime хранится как event_type=`coding_time` с `payload.total_seconds` (iwe.py adapter). Не `slot_logged` и не `payload.hours`. Скорректировано.

### 7.3 Методичность мышления (`methodical_events_per_month`)

Прямой счёт событий за 30 дней. Нормализация: 0 → 0 / 1–3 → 1 / 4–10 → 2 / 11–25 → 3 / 26–50 → 4 / > 50 → 5.

| event_type | Вес (очков за событие) |
|-----------|------------------------|
| `lesson_completed` | 2 |
| `knowledge_extracted` | 1.5 |
| `pack_updated` | 1 |
| `qualification_granted` | 3 |

### 7.4 Системность мировоззрения (`worldview_score`)

Взвешенная сумма за 30 дней → нормализация в индекс 0–5.
Нормализация: 0 → 0 / 1–4 → 1 / 5–12 → 2 / 13–28 → 3 / 29–50 → 4 / > 50 → 5.

| event_type | Вес | Условие |
|-----------|-----|---------|
| `week_plan_closed` | 4 | `payload.quality >= 3` (⚠️ Gap-А: поле отсутствует в текущем ORZ hook — всегда fallback 1) |
| `week_plan_closed` | 1 | fallback если `payload.quality` не заполнен (текущее состояние) |
| `month_plan_closed` | 8 | — |
| `strategy_session_completed` | 6 | — |
| `knowledge_extracted` | 1 | — |
| `pack_updated` | 1 | — |

### 7.5 Агентность (`agency_score`)

Взвешенная сумма за 30 дней → нормализация в индекс 0–5.
Нормализация: 0 → 0 / 1–3 → 1 / 4–8 → 2 / 9–17 → 3 / 18–30 → 4 / > 30 → 5.

| event_type | Вес | Примечание |
|-----------|-----|-----------|
| `wp_created` | 3 | MVP: все wp_created = самоинициированные (нет поля `initiator`, WP-214 Ф10.5) |
| `wp_closed` | 2 | завершение инициативы |
| `wp_completed` | 2 | — |
| `strategy_session_completed` | 5 | собственная стратегическая повестка |

### 7.6 Пример расчёта (Тсерен, 12 мая 2026)

Текущая ступень: 2 (Практикующий) → окно расчёта = 4 нед (28 дней).

| Характеристика | Данные | Расчёт | Индекс |
|---|---|---|:---:|
| Систематичность | ~20 self-dev дней за 28 дн | 20/4 = 5 дн/нед | **3** (≥5 — Систематический порог ✅) |
| Инвестированное время | WakaTime ~2.5 ч/нед | 2.5 ч/нед < 4 | **1** (ниже Практикующего порога) |
| Накоп. часы | ~60 ч всего | 60 ≥ 20 ✅, ≥ 48 ✅ | gate до ст.3 пройден |
| Методичность | 55 events/30d (ke+pack+iwe) | 26/мес | **4** |
| Системность | 1 Week Close, q=3 | worldview_points = 4 | **1** |
| Агентность | не реализован | — | **0** |

```
compute_stage_mvp(s=3, t=1, m=4, w=1, a=0, total_hours=60)
→ t=1 → ступень 2 (t < 2, нельзя подняться до 3)
→ hours gate: 60 ≥ 20 (ст.2) ✅
→ итог: ступень 2
```

Bottleneck: **Инвестированное время** (нужно ≥ 4 ч/нед × 4 нед, сейчас ~2.5). Второй bottleneck: Агентность = 0 (заблокирует ст.3 даже при исправлении времени).
