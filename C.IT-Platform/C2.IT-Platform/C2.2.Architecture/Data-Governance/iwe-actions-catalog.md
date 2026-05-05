---
family: F5
kernel: C
system: C2
role: Architecture
status: draft
created: 2026-05-05
valid_from: 2026-05-05
related:
  source: "WP-214"
  depends_on: [DP.SC.020, DP.ARCH.004]
---

# Каталог действий IWE: события, хранение, баллы

> **Назначение.** Полный реестр действий пользователя в IWE-среде — с маппингом на event_type, источник сигнала, базу хранения и правила начисления баллов. Основа для Ф8 (правила баллов) и Ф9 (связь с personal-guide).
>
> **Принцип учёта:** каждое значимое действие → `domain_event` (Neon learning). Источник сигнала может быть разным (git-hook, Claude Code hook, cron, bot), но канал единый — `event-gateway` (DP.SC.020).

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

## 2. Полный каталог

### 2.1 Протоколы ОРЗ

| Действие | event_type | Источник сигнала | Payload ключевые поля | Категория | base_points |
|----------|-----------|------------------|-----------------------|-----------|-------------|
| Day Open завершён | `day_plan_opened` | Claude Code hook Stop (скилл /day-open) | plan_date, is_strategy_day, planned_slots | `platform` | 15 |
| Day Close завершён | `day_plan_closed` | Claude Code hook Stop (скилл /day-close) | plan_date, executed_slots, self_rating_outcome | `platform` | 20 |
| Week Close завершён | `week_plan_closed` | Claude Code hook Stop (скилл /week-close) | week_start, total_slots, wps_closed | `platform` | 30 |
| Month Close завершён | `month_plan_closed` | Claude Code hook Stop (скилл /month-close) | month, total_weeks, quality_rating | `platform` | 50 |
| Strategy Session завершена | `strategy_session_completed` | Claude Code hook Stop (скилл /strategy-session) | week_start, wps_created, wps_closed | `platform` | 40 |
| KE (экстракция знания) | `knowledge_extracted` | Claude Code hook Stop (скилл /ke) | target (pack/memory/claude), domain, extract_type | `quality` | 25 |

**Текущий статус:** `day_plan_opened`/`day_plan_closed` — эмитится из скилла (работает). Остальные — **не реализованы**, нужен emitter в каждом скилле (PostToolUse/Stop hook с фильтром по скиллу).

---

### 2.2 Рабочие продукты (WP)

| Действие | event_type | Источник сигнала | Payload ключевые поля | Категория | base_points |
|----------|-----------|------------------|-----------------------|-----------|-------------|
| WP зарегистрирован | `wp_created` | wp-gate-check.sh (PreToolUse Edit) | wp_id, wp_title, budget_hours, verification_class | `wp` | 30 |
| WP закрыт | `wp_closed` | Close-скилл или wp-gate (Edit WP-REGISTRY) | wp_id, actual_hours, result_quality | `wp` | 80 |
| WP заблокирован/заморожен | `wp_blocked` | manual или strategy-session | wp_id, reason | `none` | 0 |

**Текущий статус (✅ done, 5 май):**
- `wp_created` — `.claude/hooks/iwe-wp-tracker.sh` PostToolUse на Write/Edit inbox/WP-NNN-*.md → эмитит с external_id `wp-{NNN}` (идемпотентно между сессиями)
- `wp_closed` — `iwe-orz-tracker.sh` Stop-хук, per-WP external_id `wp-{NNN}`, расширенный regex (done/closed/✅/закрыт/завершён/complete)
- Оба зарегистрированы в event-gateway LEGACY_BOT_EVENT_TYPES + zadeplоены (Worker 79e39dbb)

---

### 2.3 Работа в редакторе (Claude Code)

| Действие | event_type | Источник сигнала | Payload ключевые поля | Категория | base_points |
|----------|-----------|------------------|-----------------------|-----------|-------------|
| Сессия Claude Code (≥15 мин) | `iwe_session` | PostToolUse/Stop hook (с WakaTime duration) | project, duration_min, tools_used | `time` | 10 |
| Редактирование файла | `file_edited` | PostToolUse hook (Edit/Write) | repo, file_path, tool_name | `time` | 3 |
| Исследование (WebSearch/Read) | `iwe_research` | PostToolUse hook (WebSearch/WebFetch) | query, project | `time` | 2 |

**Текущий статус:** WakaTime hook (`wakatime-heartbeat.sh`) **существует, но НЕ подключён** в settings.json. Нужно добавить в UserPromptSubmit/PostToolUse/Stop. Для агрегации session duration — cron или Stop-hook с накоплением.

---

### 2.4 Git-действия

| Действие | event_type | Источник сигнала | Payload ключевые поля | Категория | base_points |
|----------|-----------|------------------|-----------------------|-----------|-------------|
| Git commit | `git_commit` | git post-commit hook (в каждом репо) | repo, commit_hash, files_changed, message | `wp` | 20 |
| Git push | `git_push` | git post-push hook | repo, branch, commits_count | `wp` | 10 |
| Pack обновлён (commit в Pack-репо) | `pack_updated` | git post-commit hook (PACK-* репо) | pack_name, files_changed, commit_hash | `quality` | 30 |

**Текущий статус:** git hooks — только sample файлы, **не настроены**. Нужно установить post-commit hook в каждый репо ~/IWE (или глобальный git template).

---

### 2.5 Учёба (из LMS)

| Действие | event_type | Источник сигнала | Payload ключевые поля | Категория | base_points |
|----------|-----------|------------------|-----------------------|-----------|-------------|
| Урок завершён | `lesson_completed` | Bridge-2 (poll 15 мин) | lesson_id, course_id, score | `time` | 40 |
| Квалификация получена | `qualification_granted` | Bridge-2 | qualification_id, level | `quality` | 200 |
| Платёж принят | `payment_received` | Bridge-2 | amount, product_id | `none` | 0 |

**Текущий статус:** ✅ Работает через Bridge-2.

---

### 2.6 Бот-команды (aist-bot)

| Действие | event_type | Источник сигнала | Payload ключевые поля | Категория | base_points |
|----------|-----------|------------------|-----------------------|-----------|-------------|
| Слот залогирован | `slot_logged` | aist-bot inline | slot_type, duration_min, quality_rating | `time` | 10×duration_min |
| Команда вызвана | `command_invoked` | aist-bot inline | command_name, mode | `time` | 5 |
| Рефлексия через бота | `bot_reflection` | aist-bot (текущий сеанс) | reflection_type, content_length | `quality` | 15 |

**Текущий статус:** ✅ `slot_logged` и `command_invoked` работают.

---

## 3. Матрица покрытия: действие → статус реализации

```
РАБОТАЕТ (✅)                ЕСТЬ HOOK (⚠️)              НЕТ (❌)
──────────────────────────  ──────────────────────       ──────────────────
lesson_completed             wakatime-heartbeat.sh        file_edited
qualification_granted        (в settings.json ✅,         iwe_research
payment_received             но iwe_session Stop          git_push
slot_logged                  детектирует ≥5 мин)
command_invoked
day_plan_opened
day_plan_closed
week_plan_closed             ← iwe-orz-tracker Stop
month_plan_closed            ← iwe-orz-tracker Stop
strategy_session_completed   ← iwe-orz-tracker Stop
knowledge_extracted          ← iwe-orz-tracker Stop
iwe_session                  ← iwe-orz-tracker Stop
git_commit                   ← global post-commit hook
pack_updated                 ← global post-commit hook
wp_created                   ← iwe-wp-tracker PostToolUse
wp_closed                    ← iwe-orz-tracker Stop
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
- **Готовность:** нет, нужно создать

### Тип C: External Source (Bridge-2, bot)
- **Когда:** cron / inline в боте
- **Как:** уже реализовано через event_emitter.py / inline bot handler
- **Примеры:** lesson_completed, slot_logged
- **Готовность:** ✅ работает

---

## 5. Приоритизация реализации

### DONE (✅ 5 май 2026)
1. **WakaTime hook** — подключён в settings.json Stop
2. **week_plan_closed / month_plan_closed / strategy_session_completed / knowledge_extracted / iwe_session** — iwe-orz-tracker.sh Stop-хук
3. **wp_created** — iwe-wp-tracker.sh PostToolUse (inbox/WP-NNN-*.md)
4. **wp_closed** — iwe-orz-tracker.sh Stop-хук, per-WP external_id
5. **git_commit / pack_updated** — global git template `~/.git-templates/hooks/post-commit`

### LOW: детализация (backlog)
6. **file_edited / iwe_research** (2h): детекторы в capture-bus (каркас есть)
7. **git_push** (30 мин): post-push hook в git-templates

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
