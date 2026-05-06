---
family: F2
kernel: C
system: C2
role: Meaning
audience: platform-team
valid_from: 2026-05-06
status: active
wp: 287
phase: Ф2
related:
  - WP-149 (render-pilot-guides.py)
  - WP-222 (Портной как R27)
  - WP-245 Ф28 (bootstrap personal-guide)
  - PACK-personal/personal-guide-seeds/
note: Контракт тёплого канала WP-287 ↔ WP-222/WP-149. Source-of-truth нарратива — WP-245 / PACK-personal. Этот файл добавляет только «в каком формате это живёт».
---

# Контракт тёплого канала: WP-287 ↔ Портной

> **Аудитория:** платформенная команда (разработчики Портного, владелец WP-287).
> **Не для:** конечных пользователей (им — `iwe-pilot-starter.md`, затем персональное руководство в репо).
> **Source-of-truth нарратива:** `PACK-personal/pack/personal-development/04-work-products/personal-guide-seeds/` — что рассказывать на каждой ступени; здесь — только «в каком формате/файле это живёт».

## 1. Что такое тёплый канал

Тёплый канал = персональное руководство по IWE, генерируемое Портным для пилота с активной подпиской.

```
Память.Derived (stage + domain + bottleneck)
  ↓
Портной (R27, render-pilot-guides.py)
  ↓
personal-guide/<github-login>/ (GitHub репо пилота)
```

Граница «до/после регистрации»:
- До активной подписки → холодный канал (`iwe-quickstart.md`, лендинг WP-188)
- После активации + `/personal-guide-start` → тёплый канал (этот контракт)

## 2. Входной контракт: что Портной берёт из Памяти

| Поле | Источник в Neon | Приоритет | Значение по умолчанию |
|------|-----------------|-----------|----------------------|
| `stage` | `indicators.calculated_profile.rcs_current.stage` | 1 (целевой, после WP-253 Ф9.6) | 2 (Практикующий) |
| `stage` | `indicators.3_4_qualification.stage` (FORM.093) | 2 (B-lite fallback Q2) | 2 |
| `bottleneck` | `rcs_current.bottleneck` | 1 | `"M1"` |
| `domain` (M3) | `config/pilot-guides.yaml → domain` | конфиг (Q2 ручной) | `"knowledge-worker"` |
| `W, M1, M2, M4` | `rcs_current.*` | 1 | все = 2 |
| `confidence` | `rcs_current.confidence` | 1 | 0.0 (неопределённо) |

**Q2 ограничение:** `domain` берётся из `pilot-guides.yaml` (ручной конфиг), не из `rcs_current`. Автоматическое определение домена — Q3+.

**Иерархия fallback (из `render-pilot-guides.py:get_rcs_profile`):**
1. `rcs_current` (полный RCS-профиль) — целевой после WP-253 Ф9.6 RCS computation
2. `indicators.3_4_qualification` (FORM.093: stage + path) — B-lite fallback (активен Q2)
3. Hard default: stage=2, bottleneck=M1, все рычаги=2

## 3. Матрица выбора шаблона

| Ступень | stage | Файл заготовки | Статус Q2 |
|---------|-------|----------------|-----------|
| Практикующий | 2 | `stage-2-practicing.md` | ✅ активен |
| Систематический | 3 | `stage-3-systematic.md` | ✅ активен |
| Дисциплинированный | 4 | `stage-4-disciplined.md` | ✅ активен |
| Случайный | 1 | → fallback: `stage-2-practicing.md` | fallback (нет заготовки) |
| Проактивный | 5 | → fallback: `stage-4-disciplined.md` | fallback (нет заготовки) |

**Ступени 1 и 5 — fallback:** Claude Code в первом диалоге достраивает под пилота (WP-245 Ф28 spec). Полный набор для ступени 5 — Q3+ (Портной v2).

| Домен | Файл вставки |
|-------|--------------|
| `knowledge-worker` | `domain-knowledge-worker.md` |
| всё остальное | `domain-generic.md` |

**Сборка:** `templates["stage"] + templates["domain"]` → системный промпт Портного.

Все файлы заготовок: `PACK-personal/pack/personal-development/04-work-products/personal-guide-seeds/`

## 4. Выходная структура: что пишется в personal-guide репо

| Файл | Режим рендера | Содержимое |
|------|---------------|------------|
| `profile.md` | weekly (полный) | RCS-снимок, bottleneck, целевой ритм, история ступеней |
| `methods.md` | weekly (полный) | 2–3 метода по bottleneck из CAT.003 (WP-149 planner.py) |
| `worldview.md` | weekly (полный) | Нарративная фаза дуги (PD.FORM.087) под текущую ступень |
| `weekly/YYYY-WNN.md` | weekly (новый файл) | Фокус недели, задачи, метрика успеха; включает секцию «Что было» (Ф28.7, domain_event за 7 дней) |
| `daily/YYYY-MM-DD.md` | daily (новый файл) | Дневная тактика; monthly-theme если есть |
| `config/monthly-theme.md` | пользователем (Strategy Session) | Тема месяца → Портной читает при рендере |

**Путь записи (через `personal_write`):** `<github-owner>/personal-guide`
**Имя репо = константа `personal-guide`** для всех пилотов (HD #48, WP-245 Ф28.5).

## 5. Расписание рендера Q2

| Тип рендера | Расписание | Что обновляется |
|-------------|-----------|-----------------|
| **Weekly** | Понедельник 05:00 MSK (systemd) | Все 6 файлов (`profile.md`, `methods.md`, `worldview.md`, `README.md`, первый `weekly/`, первый `daily/`) |
| **Daily** | Вторник–Воскресенье 06:00 MSK (systemd) | Только `daily/YYYY-MM-DD.md` |
| **Manual** | `/personal-guide-start` (пилот в VS Code) | Bootstrap: создание репо + полный первый рендер |

**Инфраструктура:** systemd-timer на tsekh-1 (NixOS), конфиг → `DS-autonomous-agents/config/pilot-guides.yaml`, скрипт → `DS-autonomous-agents/scripts/render-pilot-guides.py`.

**Добавить нового пилота (Q2 ручной процесс):**
1. Пилот выполняет `/personal-guide-start` в своём Claude Code → `<login>/personal-guide` создан
2. Добавить запись в `pilot-guides.yaml` с `github_owner`, `account_id`, `domain`, `enabled: true`
3. Deploy конфига на tsekh-1: `nixos-rebuild switch`
4. Автоматический рендер начнётся со следующего запуска таймера

## 6. Что НЕ входит в тёплый канал (Q2 ограничения)

| Возможность | Статус | Зависимость |
|------------|--------|------------|
| Event-driven рендер (триггер по событию ЦД) | Q3+ | WP-253 Ф9.6 + RCS computation |
| Автоматическое определение домена M3 | Q3+ | RCS full profile |
| Ступени 1 и 5 с полными заготовками | Q3+ | PACK-personal extension |
| DB-based discovery пилотов | Q3+ (v2) | WP-149 v2 |
| Браузерная версия (claude.ai) тёплого канала | Q2 частично | `iwe-browser-setup.md` (Ф4) |

## 7. Ссылки на source-of-truth

| Артефакт | Где |
|---------|-----|
| Нарратив по ступеням | `PACK-personal/pack/personal-development/04-work-products/personal-guide-seeds/` |
| Скрипт рендера | `DS-autonomous-agents/scripts/render-pilot-guides.py` |
| Конфиг пилотов | `DS-autonomous-agents/config/pilot-guides.yaml` |
| Скилл bootstrap | `.claude/skills/personal-guide-start/SKILL.md` |
| Роль Портного (R27) | `PACK-agent-rules/rules/` + `memory/roles.md` |
| Расписание systemd | `iwe-server-config:modules/systemd-timers.nix` |
| Памяти.Derived схема | `DP.ARCH.003` (PACK-digital-platform) |
