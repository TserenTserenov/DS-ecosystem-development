---
family: F2
kernel: C
system: C2
role: Meaning
audience: potential-users, cold-warm-channel
valid_from: 2026-05-06
status: active
wp: 287
phase: Ф4
note: Инструкция использования IWE через браузер (claude.ai) без VS Code. Q2 — частичная поддержка без новой инфраструктуры.
---

# Как использовать IWE в браузере (claude.ai)

> **Для кого:** если у вас нет VS Code или вы хотите работать с IWE «в дороге», с мобильного или просто в браузере.
> **Важно:** браузерная версия — это подмножество возможностей. Коммиты, хуки и скилл-команды работают только в VS Code. Но многое работает и здесь.

## Что работает в браузере

| Компонент | Как настроить | Ограничение |
|-----------|--------------|-------------|
| **Правила поведения (CLAUDE.md выжимка)** | Project → Custom instructions | Вручную, ~200-300 строк ключевых правил: WP Gate, ОРЗ, различения, форматирование |
| **Справочные файлы** | Project → Add knowledge (drag-n-drop) | `distinctions.md`, `roles.md`, `protocol-open.md`, `formatting.md` — загрузить в проект |
| **Доступ к Pack и Персоне** | Settings → Connectors → `https://mcp.aisystant.com/mcp` + OAuth | `knowledge_*`, `personal_*`, `search`, `personal_write` |
| **Протоколы как диалог** | Через text-инструкции в Project | Day Open чеклист, ArchGate-вопросник, Ритуал согласования — агент выполняет в диалоге без хуков |
| **Запись в personal-guide** | `personal_write` через MCP | Captures, черновики, WP-контексты — пишет в подключённый `personal-guide` репо |
| **Поиск по источникам** | `personal_search`, `knowledge_search` | Все подключённые `personal` и `knowledge` источники |

## Что НЕ работает в браузере

- `Read`/`Edit`/`Write` локальных файлов — нет файловой системы
- `git` (commit, push, pull) — нет терминала
- Hooks (PreToolUse/PostToolUse), scheduler, launchd
- Slash-skills (`.claude/skills/`) — работают только в Claude Code CLI/VS Code
- Работа с `DS-my-strategy`, governance-репо напрямую
- Полноценный Day Open/Close с коммитами

## Настройка за 15 минут

### Шаг 1. Создайте Project в claude.ai (~2 мин)

1. Откройте [claude.ai](https://claude.ai) → **Projects** → **New project**
2. Назовите: `IWE — [ваше имя]`

### Шаг 2. Добавьте Custom instructions (~5 мин)

В Project → **Custom instructions** вставьте ключевые правила из вашего `CLAUDE.md`:
- WP Gate (§2 блокирующие правила)
- Правила форматирования (§6 / `.claude/rules/formatting.md`)
- Различения (`distinctions.md` — самые важные пары, первые 30 строк)

Размер: **не более 300 строк** — браузерная контекстная инструкция имеет лимит.

### Шаг 3. Загрузите справочные файлы (~3 мин)

Project → **Add knowledge** → перетащите файлы:
- `.claude/rules/distinctions.md`
- `memory/roles.md`
- `memory/protocol-open.md` (или выжимку)
- `memory/formatting.md`

### Шаг 4. Подключите Aisystant MCP (~5 мин)

1. claude.ai → **Settings** → **Integrations** → **Add Integration**
2. URL: `https://mcp.aisystant.com/mcp`
3. Нажмите **Connect** → авторизуйтесь через Aisystant OAuth

После подключения в проекте будут доступны инструменты:
- `knowledge_search` — поиск по Pack
- `personal_search` — поиск по вашим репо
- `personal_write` — запись в `personal-guide`

**Требование:** активная подписка Aisystant для `personal_*` и `search` (бесплатно — только `knowledge_*`).

## Архитектура браузерного проекта

```
claude.ai Project:
  ├── Custom instructions  ←  CLAUDE.md выжимка (~200-300 строк)
  ├── Project knowledge    ←  distinctions.md, roles.md, protocols
  └── Integrations         ←  Aisystant MCP (mcp.aisystant.com/mcp)
                                  → knowledge_* (Pack — бесплатно)
                                  → personal_* (Персона: форки, captures)
                                  → search (поиск по всем источникам)
```

## Сценарии, которые работают в браузере

| Сценарий | Как работает | Полнота |
|---------|-------------|---------|
| Вопросы по домену | `knowledge_search` по Pack | ✅ полностью |
| Captures и черновики | `personal_write` в personal-guide | ✅ полностью |
| ArchGate обсуждение (ЭМОГССБ) | диалог по чеклисту, фиксация через `personal_write` | 🔶 частично |
| Стратегия «в дороге» | обсуждение без коммитов | 🔶 частично (без артефактов) |
| Форкнутые репо как источники | если подключены через `personal_connect_source` | ✅ полностью |

## Ограничение форков

Все подключённые репо (свои + форки) попадают в единую выдачу `personal_search`. Разделить — только по `source:`-фильтру в запросе. Разделение на два MCP-профиля = feature request в IWE (Q3+).

## Персональное руководство через браузер

Если вы пилот программы ЛР — `personal-guide` доступен в браузере целиком (создание / чтение / запись рефлексии / пересборка), без `git` и VS Code.

### Создание (один раз, ~5 мин)

В чате claude.ai вызови `/personal-guide-start`. Скилл:

1. Создаст репо `personal-guide` под вашим GitHub-аккаунтом (через `create_repository` MCP).
2. Делегирует наполнение в `/personal-guide-render`: 6 файлов (`README.md`, `profile.md`, `worldview.md`, `methods.md`, `weekly/<неделя>.md`, `daily/<сегодня>.md`) + `history/reflection-template.md`.
3. Положит 5 скиллов в `<repo>/.claude/skills/` (lesson, lesson-close, connect-guide, personal-guide-render, personal-guide-start) — после этого они будут доступны в любой следующей сессии claude.ai с тем же проектом.

**Требование:** активная подписка Aisystant + GitHub подключён в `Settings → Integrations → Aisystant MCP`.

### Чтение руководства

Прямо в чате: «покажи мой `profile.md`», «прочитай `daily/<дата>.md`». Агент через `personal_search(source: "personal-guide", path: "...")` подтянет файл.

### Запись рефлексии (~5 мин)

Браузер не имеет `git`, но `personal_write` MCP пишет напрямую в GitHub через Gateway — отдельный push не нужен.

1. Открой `history/reflection-template.md` (5 вопросов на 5 минут).
2. Ответь.
3. Скажи агенту: «закоммить рефлексию за сегодня». Он вызовет `personal_write(source: "personal-guide", path: "history/<YYYY-MM-DD>-reflection.md", content: "...")`.
4. После записи reindex MCP `personal_search` обновляется автоматически.

### Пересборка (при изменении RCS)

Когда обновился RCS-профиль в Память.Derived (например, прошла W-рефлексия или повысился slot baseline) — вызови `/personal-guide-render`. Скилл прочитает RCS, выберет новые ступенные/доменные заготовки, перезапишет 6 файлов. Прежние weekly/daily автоматически уйдут в `history/` (Шаг 5 скилла).

### Ограничения

- Нет `git pull/push/commit` — все коммиты через `personal_write` (это норма для браузерного канала).
- Нет hooks (PreToolUse / PostToolUse), нет launchd, нет cron.
- Скиллы `/lesson`, `/lesson-close` и т.д. работают только если они уже разданы в `<repo>/.claude/skills/` (происходит на первом `/personal-guide-render`).
- Раздача `personal_connect_source` (форки чужих репо) — отдельная инструкция (см. `iwe-quickstart.md` → раздел «Подключение источников»).

Полная матрица каналов × операций → [personal-guide-channels.md](personal-guide-channels.md).

## Сравнение с VS Code

| Возможность | VS Code + Claude Code | Браузер (claude.ai) |
|-------------|----------------------|---------------------|
| ОРЗ-ритуал с коммитами | ✅ | ❌ |
| Slash-skills (`/day-open`) | ✅ | ❌ |
| Hooks (preCommit, WP Gate) | ✅ | ❌ |
| Captures и черновики | ✅ | ✅ |
| Поиск по Pack | ✅ | ✅ |
| personal-guide запись | ✅ | ✅ |
| Работа без интернета | ✅ (локальные файлы) | ❌ |
| Мобильный / планшет | ❌ | ✅ |

## Следующий шаг

Хотите попробовать полноценный IWE с коммитами и ритуалами? → [Быстрый старт за 15 минут (VS Code)](iwe-quickstart.md)
