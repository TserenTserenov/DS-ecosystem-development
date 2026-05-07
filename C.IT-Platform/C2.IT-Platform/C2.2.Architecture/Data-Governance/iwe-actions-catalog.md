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
