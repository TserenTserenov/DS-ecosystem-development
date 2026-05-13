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

## Reflection contract (Ф3)

**Формат:** `history/<YYYY-MM-DD>-reflection.md`, 5 вопросов на 5 минут.

Шаблон-источник: `~/IWE/.claude/skills/personal-guide-render/templates/reflection-template.md`. Копируется в репо пилота при first-run через `/personal-guide-render` Шаг 6.8 (`history/reflection-template.md`).

**5 вопросов:**

1. Что сделал сегодня (три факта)
2. Что не сделал (одна-две вещи)
3. Что узнал
4. Зачем это (связь с программой развития)
5. Что завтра (одна вещь)

**Куда писать (по каналу):**

| Канал | Способ записи |
|-------|--------------|
| Бот | через команду `/reflect <дата> <содержимое>` (Ф4 — ещё не реализована) |
| Браузер | `personal_write(source: "personal-guide", path: "history/<дата>-reflection.md", content: ...)` |
| VS Code | редактирование локального файла + `git commit` + `git push` |

**Как Портной (WP-149) читает обратно:**

В Шаге 1 следующего render (`/personal-guide-render`) — после `dt_read_digital_twin` дополнительно вызывается `personal_search(source: "personal-guide", path: "history/", pattern: "*-reflection.md")` за последние 7 дней. Извлекаются:

- Ответ на (3) «Что узнал» → сигнал для PD.FORM.087 фазового перехода (Шаг 2 проверки ступени).
- Ответ на (5) «Что завтра» → input для пересборки `daily/<завтра>.md` (Шаг 6.6).

**Контракт не закрывает:** в Ф3 не описан handler бота `/reflect` (это Ф4 — браузерный smoke + ботовая реализация). До Ф4 пилоты wave-1 пишут рефлексию через VS Code или браузер.

## Lifecycle репо

Четыре цикла жизни репо `personal-guide`, каждый со своим контрактом.

### 1. Reindex после push

После push в `personal-guide` MCP `personal_search` должен подхватить изменения, чтобы при следующем запросе `personal_search(source: "personal-guide", path: "...")` агент вернул свежее содержимое.

**Контракт:**
- Триггер: push в `main` репо `personal-guide` (или write через `personal_write` MCP).
- Механизм: GitHub App «Aisystant Personal Guide» (установлен в `/connect-guide`) → webhook `oauth_server.py:/webhook/github/workbook` → `sync_one_user_to_dt` → reindex в `personal_*` каталоге.
- Время отклика: ≤30 сек от push до видимости в `personal_search`.
- Failure mode: если App не установлен или webhook не дошёл — `personal_search` может вернуть устаревший контент. Решение — пилот вручную может попросить «переиндексируй мой personal-guide».

**Что проверить пилоту:** `personal_reindex_status(source: "personal-guide")` или просто запрос «когда последний раз обновился индекс моего personal-guide».

### 2. History/ архивация при пересборке

При вызове `/personal-guide-render` — Шаг 5 перемещает прежние `weekly/<YYYY-Www>.md` и `daily/<YYYY-MM-DD>.md` за прошлые периоды в `history/<period>.md`. Текущая неделя/день — НЕ архивируются (перезаписываются Шагом 6).

**Что не архивируется автоматически:**
- `reflection-template.md` — остаётся в `history/` как шаблон (живёт там постоянно).
- `<дата>-reflection.md` — пилот пишет напрямую в `history/`, никогда не перезаписывается рендером.

**Failure mode:** двойной запуск render в один день — Шаг 5 пропустит архивацию (текущая дата не считается прошлым периодом). Это норма.

### 3. Skill distribution refresh

5 скиллов (`lesson`, `lesson-close`, `connect-guide`, `personal-guide-render`, `personal-guide-start`) живут в `<repo>/.claude/skills/` пилотского репо. Контракт обновления:

| Событие | Поведение |
|---------|-----------|
| First-run `/personal-guide-start` | Раздать все 5 скиллов (Шаг 6.7 render) |
| Повторный render через ≥30 дней | Перезаписать все 5 скиллов из `~/IWE/.claude/skills/` (проверка через checksum) |
| Hotfix скилла (BUG в SKILL.md) | Пилот вызывает `/personal-guide-render` явно — Шаг 6.7 перезапишет |
| Smen schema_version скиллов | Поднять banner в Шаге 7 «скиллы обновились, перечитайте инструкции» |

**Failure mode:** если ~/IWE/.claude/skills/ недоступен (платформа другая) — Шаг 6.7 пропустит с warning, скиллы остаются старой версии.

### 4. GDPR right-to-delete

При отписке пилота от подписки «Бесконечное развитие» или явном запросе на удаление личных данных:

**Runbook:**

1. Uninstall GitHub App «Aisystant Personal Guide» с репо пилота (пилот делает сам в GitHub Settings).
2. Удалить репо `personal-guide` (через `gh repo delete <login>/personal-guide --yes` пилотом, или вручную через UI).
3. Purge MCP indexes: `personal_purge_source(source: "personal-guide")` — удаляет все embeddings и metadata из Persona-стора.
4. (Опционально) Удалить webhook-маппинг из Neon `github_connections` таблицы — это часть общего GDPR-flow при отписке.

**Контракт времени:** ≤72 часа от запроса до полного удаления (требование GDPR).

**Что НЕ удаляется автоматически:**
- Локальный клон `~/IWE/personal-guide/` на машине пилота — пилот удаляет сам.
- События в `learning.user_events` Neon — это Память.Derived, не Персона. Удаляются отдельным GDPR-flow (см. `DATA-POLICY.md` в FMT-exocortex-template).

**Failure mode:** если step 3 (`personal_purge_source`) не сработал — индексы могут давать residual поиск ещё ~24h до полного eviction. Это в SLA.

## Smoke wave-1 (Ф7 — для пилотов)

Чеклист e2e-проверки для каждого из 5 wave-1 пилотов × 3 интерфейса = 15 прогонов.

**Для каждого пилота:**

| Интерфейс | Шаги | Ожидаемый результат |
|-----------|------|---------------------|
| **Бот** | `/start` → кнопка «Создать personal-guide» | Репо создан за ≤4 сек, push-уведомление в TG, ссылка на репо |
| **Браузер** | claude.ai/code → новый проект IWE → MCP подключен → `/personal-guide-start` | Репо создан, 6 файлов записаны, 5 скиллов в `<repo>/.claude/skills/` |
| **VS Code** | `~/` → `claude` → `/personal-guide-start` → `git clone` | Репо склонирован локально, файлы видны, можно открыть в VS Code |

**Затем (для каждого интерфейса):**
- Скопировать `history/reflection-template.md` → `history/<сегодня>-reflection.md`
- Заполнить 5 вопросов
- Закоммитить (бот: команда `/reflect` — pending Ф4 ботового handler; браузер: `personal_write`; VS Code: `git commit + push`)

**Багрепорты:** если что-то сломалось — записать в `DS-my-strategy/inbox/bugs/bug-2026-05-XX-pgчерез-<канал>.md` со скриншотом / логом.

**Критерий выхода Ф7:** 5 пилотов × 3 интерфейса = 15 успешных прогонов ИЛИ ≤1 баг-репорт на интерфейс (3 итого) с известным workaround.

## Связи

- **Контракт write-side** (как Портной создаёт контент): [iwe-tailor-contract.md](iwe-tailor-contract.md), WP-149.
- **Consent перед create_repository:** WP-188 Ф17.
- **SC.020 — обещание доставки бота:** Pack `DP.SC.020`.
- **Публичные docs IWE:** [iwe-quickstart.md](iwe-quickstart.md), [iwe-browser-setup.md](iwe-browser-setup.md), `FMT-exocortex-template/docs/`.
- **Identity Ory-direct для VS Code-only:** WP-303 (Q2-Q3).

---

*Создан 2026-05-13 (WP-309 Ф2). Обновляется при изменении канала или операции.*
