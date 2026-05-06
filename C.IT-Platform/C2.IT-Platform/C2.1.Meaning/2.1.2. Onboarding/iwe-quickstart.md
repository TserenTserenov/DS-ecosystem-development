---
family: F2
system: C2 (IT-Platform / IWE)
role: Meaning
audience: new-users
valid_from: 2026-05-06
status: draft
---

# Быстрый старт за 15 минут

> Черновик для холодного канала (лендинг WP-188). Охват Q2: VS Code + Telegram бот. Браузерная версия — Q4+.

## Что вам понадобится

- Компьютер с macOS, Linux или Windows (WSL)
- VS Code (бесплатно: code.visualstudio.com)
- Аккаунт на claude.ai или API-ключ Anthropic (для Claude Code)
- Telegram — для Aisystant бота

## Шаг 1. Установите Claude Code (~5 мин)

Claude Code — это ИИ-агент внутри VS Code, который работает с вашим IWE-окружением.

```bash
# В терминале VS Code:
npm install -g @anthropic-ai/claude-code
```

Проверка:
```bash
claude --version
```

## Шаг 2. Форкните и установите IWE (~5 мин)

1. Откройте [FMT-exocortex-template](https://github.com/TserenTserenov/FMT-exocortex-template) на GitHub
2. Нажмите **Fork** → выберите свой аккаунт
3. Склонируйте и запустите wizard установки:

```bash
mkdir -p ~/IWE && cd ~/IWE
gh repo fork TserenTserenov/FMT-exocortex-template --clone
cd FMT-exocortex-template
bash setup.sh
```

`setup.sh` — интерактивный wizard. Спросит GitHub-username, часовой пояс и согласие на Data Policy. На остальные вопросы — Enter (подставятся defaults). В конце предложит запустить финальную валидацию (`setup.sh --validate`) — нажмите `y`.

**Альтернативные режимы:**
- `bash setup.sh --core` — минимальная установка без сети (для офлайн / любого AI CLI, не только Claude Code)
- `bash setup.sh --dry-run` — показать что будет сделано, без изменений

## Шаг 3. Подключите Aisystant бота (~2 мин)

1. Откройте Telegram → найдите [@aist_me_bot](https://t.me/aist_me_bot)
2. Напишите `/start`
3. Следуйте инструкции онбординга

Бот — это ваш второй интерфейс к IWE: вопросы, прогресс, напоминания — всё работает и в мобильном.

## Шаг 4. Первая сессия с ОРЗ-ритуалом (~5 мин)

ОРЗ (Открытие → Работа → Закрытие) — основной ритуал IWE. Не пропускайте его: именно он обеспечивает сохранность контекста.

В VS Code, в папке вашего IWE, откройте терминал и запустите:

```bash
claude
```

Напишите агенту:

```
открывай
```

Агент:
- Прочитает вашу память и контексты
- Соберёт план дня
- Проверит, что важное ничего не потеряно

После работы — закройте сессию:

```
закрывай
```

Агент зафиксирует результаты, обновит планы.

## Что происходит под капотом

После клонирования вы получили:
- **`memory/`** — ваша персональная память (читается каждую сессию)
- **`CLAUDE.md`** — правила для ИИ-агента (не редактируйте вручную)
- **`.claude/skills/`** — скиллы: day-open, week-close, archgate, etc.
- **`DS-my-strategy/`** — ваш стратегический хаб (планы недели, ревью)

## Первые 7 дней

| День | Что делать |
|------|-----------|
| 1 | Установка + первый `/day-open` |
| 2–3 | Утренний `/day-open`, вечерний `/day-close` |
| 4–5 | Создайте первый Pack: ваша предметная область |
| 6–7 | Первый `/week-close` — агент соберёт итоги недели |

После 7 дней вы почувствуете разницу: ИИ знает ваш контекст, планы не теряются, каждое утро начинается не с нуля.

## Если что-то пошло не так

→ Telegram [@aist_me_bot](https://t.me/aist_me_bot) — поддержка
→ [GitHub Issues](https://github.com/TserenTserenov/FMT-exocortex-template/issues) — баги и предложения
→ [Клуб Aisystant](https://aisystant.com) — сообщество пользователей
