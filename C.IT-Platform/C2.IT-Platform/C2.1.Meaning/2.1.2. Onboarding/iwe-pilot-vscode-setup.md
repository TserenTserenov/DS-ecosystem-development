---
family: F2
kernel: C
system: C2
role: Meaning
audience: pilots, warm-channel
valid_from: 2026-05-13
status: draft
wp: 309
phase: Ф5
note: Инструкция использования IWE через VS Code (Claude Code) с акцентом на персональное руководство — для пилотов программы ЛР.
related:
  - iwe-browser-setup.md (парный файл — браузер claude.ai/code)
  - iwe-pilot-starter.md (стартовая инструкция, общая)
  - personal-guide-channels.md (SoT каналов доставки)
  - SETUP-GUIDE.md (полная установка IWE, FMT-exocortex-template/docs/)
---

# Персональное руководство через VS Code (Claude Code)

> **Для кого:** пилот программы ЛР, который хочет полный контроль (git, hooks, локальные файлы, slash-skills) — не только чтение в браузере.
> **Парный документ:** [iwe-browser-setup.md](iwe-browser-setup.md) (если нужен только браузер).
> **Полная установка IWE:** см. `FMT-exocortex-template/docs/SETUP-GUIDE.md` (Этапы 0-7). Этот документ — только специфика personal-guide.

## Что даёт VS Code канал

- **Локальный `personal-guide/`** — все 6 файлов + `history/` на диске, можно открыть в любом редакторе
- **`git commit` + `git push`** — стандартный flow без MCP-проксирования
- **Slash-skills работают:** `/personal-guide-start`, `/personal-guide-render`, `/lesson`, `/lesson-close`, `/connect-guide`
- **Hooks:** PreToolUse / PostToolUse / pre-commit запускаются (если настроены в `.claude/hooks/`)
- **Pull-on-Touch:** при первом обращении к репо за сессию автоматически `git pull --rebase`

## Шаг 1. Установить Claude Code

Через npm (требует Node.js 20+):

```bash
npm install -g @anthropic-ai/claude-code
```

Полный сценарий установки (Homebrew + Node + Claude Code + Gateway OAuth) — `SETUP-GUIDE.md` Этап 0.4.

Проверка:

```bash
claude --version
# должно вывести версию, например: 1.x.x
```

## Шаг 2. Создать personal-guide (~3 мин)

В новой сессии Claude Code (`cd ~/`, потом `claude`):

```
/personal-guide-start
```

Скилл создаст репо на GitHub под вашим аккаунтом + наполнит 6 файлами через MCP. После завершения скилл выведет URL для клонирования.

Клонируйте локально:

```bash
git clone https://github.com/<ваш-login>/personal-guide.git ~/IWE/personal-guide
```

(Подставьте свой GitHub-login. `gh auth status` покажет, кто вы.)

## Шаг 3. Подключить GitHub App (опционально, для бота)

Если планируете писать рефлексию через бот (а не только через VS Code):

```
/connect-guide
```

Скилл откроет GitHub install page → выберите репо `personal-guide` → Install. После этого бот сможет слать `/reflect` команды.

**Ограничение текущей реализации:** `/connect-guide` требует `telegram_user_id`. Если вы не пользуетесь ботом (VS Code-only) — этот шаг можно пропустить, использовать `git commit` напрямую. Ory-direct flow без TG-зависимости — в WP-303.

## Шаг 4. Ежедневные операции

| Операция | Команда |
|----------|---------|
| Открыть план на сегодня | `cat ~/IWE/personal-guide/daily/<сегодня>.md` или в VS Code: открыть файл |
| Закоммитить рефлексию | Скопировать `history/reflection-template.md` → `history/<дата>-reflection.md`, заполнить, `git add` + `git commit` + `git push` |
| Пересобрать руководство | `/personal-guide-render` (читает RCS из Память.Derived, перезаписывает 6 файлов, прежние weekly/daily в `history/`) |
| Закрыть занятие | `/lesson-close` (push + webhook → ЦД обновляется) |

## Где живут скиллы

Skills в Claude Code могут жить в двух местах:

| Расположение | Доступ | Когда использовать |
|--------------|--------|--------------------|
| `~/.claude/skills/` (user-global) | Во всех сессиях на этой машине | Стандартный путь после `setup.sh` IWE |
| `<repo>/.claude/skills/` (repo-local) | Только когда `claude` запущен из этого репо | Если работаете в репо с особыми скиллами |

`/personal-guide-render` на первом запуске копирует 5 скиллов в `<repo>/.claude/skills/` вашего `personal-guide` — это нужно для браузера claude.ai/code (там user-global не пробрасывается). На VS Code они работают и так, но repo-local копия не мешает.

## Ограничения VS Code канала

- **Мобильный / планшет** — нет; используйте браузерный канал (`iwe-browser-setup.md`).
- **Без интернета** — `git`, локальные файлы, `Read`/`Edit` работают; `personal_search` / `knowledge_search` через MCP — нет.
- **Identity для `/connect-guide`** — пока требует Telegram (см. Шаг 3); WP-303 решит для VS Code-only пилотов.

## Сравнение с другими каналами

| Возможность | VS Code (этот) | Браузер (claude.ai) | Бот (@aist_me_bot) |
|-------------|---------------|---------------------|---------------------|
| Create repo | ✅ через `/personal-guide-start` | ✅ через `/personal-guide-start` (MCP) | ✅ кнопка после `/start` |
| Read guide | ✅ локальные файлы | ✅ `personal_search` MCP | ✅ TG-кнопки |
| Commit reflection | ✅ `git commit` + push | ✅ `personal_write` MCP | ⚠️ `/reflect` ещё не реализован (Ф4 WP-309) |
| Refresh on RCS | ✅ `/personal-guide-render` | ✅ `/personal-guide-render` (если скиллы разданы) | ⚠️ нет webhook-listener (Ф6 WP-309) |
| Hooks (preCommit) | ✅ | ❌ | — |
| Работа без интернета | ✅ | ❌ | ❌ |
| Мобильный | ❌ | ✅ | ✅ |

Полная матрица каналов → [personal-guide-channels.md](personal-guide-channels.md).

## Следующий шаг

Когда настроено и `personal-guide` склонирован — пройдите первое занятие:

```
/lesson
```

Скилл откроет ближайший `daily/<дата>.md` и проведёт по нему. Закрытие — `/lesson-close`.
