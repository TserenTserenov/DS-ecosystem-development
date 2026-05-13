---
family: F2
kernel: C
system: C2
role: Meaning
audience: pilots, cold-warm-channel
valid_from: 2026-05-13
status: draft
wp: 309
phase: Ф2
note: SoT-документ доставки персонального руководства через 3 интерфейса (бот / браузер / VS Code). Матрица операций × каналов + инварианты + lifecycle.
related:
  - DP.SC.020 (доставка занятий)
  - WP-149 (Портной — write-side)
  - WP-188 (consent gate Ф17)
  - WP-287 (публичные docs IWE)
---

# Каналы доставки персонального руководства

> **Для кого:** пилоты программы личного развития; команда IWE.
> **Что это:** SoT-документ о том, как одно и то же репо `personal-guide` живёт в 3 интерфейсах (бот / браузер / VS Code) и какие гарантии каждый канал даёт.
> **Парные документы:** [iwe-browser-setup.md](iwe-browser-setup.md) (как настроить браузер), [iwe-pilot-starter.md](iwe-pilot-starter.md) (первые шаги).

## Зачем три канала

Пилот заходит в pipeline персонального руководства из разной обстановки:

- С мобильного — нет VS Code, есть бот.
- С чужого ноутбука — нет VS Code, есть браузер.
- Со своего рабочего места — есть всё.

Один и тот же репо `personal-guide` должен работать одинаково везде, иначе пилот теряет нить программы при смене обстановки.

## Четыре операции с репо

| Операция | Что делает | Кто инициирует |
|----------|-----------|----------------|
| **Create** | Создать репо на GitHub пилота + первое наполнение 6 файлами | Пилот один раз через `/personal-guide-start` |
| **Read** | Прочитать руководство (profile / worldview / methods / weekly / daily / README) | Пилот многократно |
| **Commit reflection** | Записать дневную рефлексию по шаблону `history/YYYY-MM-DD-reflection.txt` | Пилот ежедневно |
| **Refresh on RCS change** | Пересобрать руководство при обновлении RCS-профиля (Память.Derived) | Портной (автоматически) или пилот командой |

## Матрица каналов × операций

> Статус: ✅ работает / ⚠️ частично / ❌ не работает / ⬜ не проверено

| Операция | Бот (@aist_me_bot) | Браузер (claude.ai/code) | VS Code (Claude Code) |
|----------|--------------------|-----------------------|----------------------|
| Create | ✅ SC.020 PROD, 4 сек | ⬜ smoke в WP-309 Ф4 | ✅ через `/personal-guide-start` |
| Read | ✅ кнопки бота | ⬜ smoke в WP-309 Ф4 | ✅ файлы в `~/IWE/personal-guide/` |
| Commit reflection | ❌ нет `/reflect` или эквивалента | ⚠️ через `personal_write` MCP, не задокументировано | ✅ `git commit` + push |
| Refresh on RCS change | ❌ нет webhook-listener | ⚠️ через MCP, не задокументировано | ✅ ручной `/personal-guide-render` |

**Wave-1 (13 мая)** использует только колонку «Бот create». Wave-2 (16-17 мая) требует все 12 ячеек ✅.

## Инварианты (одинаково для всех каналов)

1. **Имя репо — константа** `personal-guide` (не `personal-guide-<login>`). Один личный аккаунт пилота = один репо. Источник: `/personal-guide-start` SKILL.md.
2. **Структура** — 6 верхнеуровневых файлов: `README.md`, `profile.md`, `worldview.md`, `methods.md`, `weekly/<YYYY-Www>.md`, `daily/<YYYY-MM-DD>.md`.
3. **History/** — архив старых weekly/daily при пересборке + ежедневные reflection-файлы.
4. **Consent gate** — `create_repository` блокируется без opt-in (WP-188 Ф17). Применяется во всех каналах.
5. **Identity** — пилот определяется по `ory_user_id` (одинаково для бота и MCP). Telegram ID = алиас.
6. **Source-of-truth контента** — Pack `PACK-personal-development` + Память.Derived (RCS). Каналы — только интерфейс доставки.

## Специфично для каждого канала

### Бот (@aist_me_bot)

- **Команда создания:** inline-кнопка в `/start` flow (handler в `aist_bot_newarchitecture`).
- **Чтение:** TG-кнопки выдают актуальный `daily/` или `weekly/`.
- **Коммит рефлексии:** ⚠️ команда `/reflect` ещё не реализована — это пробел Ф3.
- **Refresh:** ❌ webhook-listener на push в `personal-guide` отсутствует — пробел Ф6.

### Браузер (claude.ai/code)

- **Команда создания:** `/personal-guide-start` через Aisystant MCP connector. Скиллы раздаются в `<repo>/.claude/skills/` на первом render (Шаг 6.7 `/personal-guide-render`).
- **Чтение:** `personal_search(source: "personal-guide", path: "...")` через MCP.
- **Коммит рефлексии:** `personal_write(source: "personal-guide", path: "history/...")` через MCP (без `git`). Документация — раздел в [iwe-browser-setup.md](iwe-browser-setup.md), пробел Ф4.
- **Refresh:** `/personal-guide-render` через Skill в браузере — работает, если скиллы раздались.
- **Ограничения:** нет `git` (commit/push/pull), нет hooks, нет launchd.

### VS Code (Claude Code)

- **Команда создания:** `/personal-guide-start` локально (Claude Code CLI). Требует склонированного `~/IWE/personal-guide/`.
- **Чтение:** `Read` локальных файлов.
- **Коммит рефлексии:** `git commit` + `git push` — стандартный flow.
- **Refresh:** `/personal-guide-render` + локальная пересборка + push.
- **Identity-зависимость:** `/connect-guide` требует `telegram_user_id` (пробел для VS Code-only-пилотов — закрывается WP-303 Ory-direct).

## Lifecycle (детализация — Ф6)

Каждый из 4 циклов требует явного контракта:

1. **Reindex** — после push GitHub App → webhook → MCP `personal_search` reindex. Как пилот видит «индекс свежий»?
2. **History/ архивация** — `/personal-guide-render` Шаг 5 перемещает прежние weekly/daily в `history/`. Reflection-файлы туда же.
3. **Skill distribution refresh** — 5 скиллов в `<repo>/.claude/skills/` обновляются при каждом render? При смене версии? Вручную?
4. **GDPR right-to-delete** — отписка пилота → uninstall GitHub App + delete repo + purge `personal_*` indexes.

Полный runbook lifecycle — см. WP-309 Ф6 (откроется по приоритету после wave-1 smoke).

## Связи

- **Контракт write-side** (как Портной создаёт контент): [iwe-tailor-contract.md](iwe-tailor-contract.md), WP-149.
- **Consent перед create_repository:** WP-188 Ф17.
- **SC.020 — обещание доставки бота:** Pack `DP.SC.020`.
- **Публичные docs IWE:** [iwe-quickstart.md](iwe-quickstart.md), [iwe-browser-setup.md](iwe-browser-setup.md), `FMT-exocortex-template/docs/`.
- **Identity Ory-direct для VS Code-only:** WP-303 (Q2-Q3).

---

*Создан 2026-05-13 (WP-309 Ф2). Обновляется при изменении канала или операции.*
