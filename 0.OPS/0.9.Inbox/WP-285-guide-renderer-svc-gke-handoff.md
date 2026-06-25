---
type: handoff
status: draft
created: 2026-06-25
updated: 2026-06-25
owner: Андрей
next_review: 2026-07-09
related: [WP-285, WP-149, WP-415]
---

# guide-renderer-svc — план GKE-деплоя

**Источник:** Оперативка ИТ 23 июня 2026 (WP-285 Ф7 Часть Б).

Новый Python-сервис для генерации персональных руководств пользователям без IWE/Git («тайный гид»). Пользователи с IWE генерируют локально (на своей машине); пользователи без IWE/Git получают руководство с платформы через этот сервис.

---

## Что делает сервис

По расписанию (пн = полный прогон, вт–вс = дневной):

1. Загружает список пилотов из БД.
2. Для каждого пилота с `has_iwe_git=False` собирает контекст (профиль, активность, рефлексии, активные задачи).
3. Генерирует персональное руководство через Claude API.
4. Записывает результат в приватный GitHub-репозиторий пилота в `aisystant/*-guide` или `mim-school/*-guide`.
5. Отправляет Telegram-уведомление (дедуп: не чаще раза в день).

---

## Функции для переноса

Исходный модуль: `DS-autonomous-agents/scripts/render-pilot-guides.py` и смежные файлы.

| Функция | Модуль | Назначение |
|---------|--------|-----------|
| `load_pilots_from_db()` | `render-pilot-guides.py` | Загрузка пилотов из learning/indicators БД |
| `get_rcs_profile()` | `render-pilot-guides.py` | RCS-профиль: ступень, слабый слот |
| `_rcs_from_digital_twin()` | `render-pilot-guides.py` | Вспомогательная для get_rcs_profile |
| `get_cp_profile()` | `render-pilot-guides.py` | CP-профиль из digital twin |
| `get_recent_events()` | `render-pilot-guides.py` | Activity-события пилота |
| `get_iwe_activity_metrics()` | `render-pilot-guides.py` | WakaTime, слоты, коммиты |
| `get_strategy_inputs()` | `render-pilot-guides.py` | Активные РП из GitHub пилота |
| `_rank_wp_by_budget()` | `render-pilot-guides.py` | Вспомогательная для get_strategy_inputs |
| `get_pilot_reflections()` | `render-pilot-guides.py` | Рефлексии из GitHub-репо пилота |
| `_build_system_prompt_v2()` | `render-pilot-guides.py` | Сборка промпта с данными пилота |
| `generate_guide_v2()` | `render-pilot-guides.py` | Вызов Claude API (генерация) |
| `write_file()` | `render-pilot-guides.py` | Запись результата в GitHub-репо |
| `generate_guide_json()` | `render-pilot-guides.py` | JSON-версия руководства |
| `archive_old_weekly()` | `render-pilot-guides.py` | Архивирование старых еженедельных файлов |
| `archive_old_daily()` | `render-pilot-guides.py` | Архивирование старых дневных файлов |
| `send_tg()` | `render-pilot-guides.py` | Telegram-уведомление |
| `_guide_notified_today()` | `render-pilot-guides.py` | Дедуп уведомлений (не чаще 1/день) |
| `derive_rung()` | `program_dispatcher.py` | Ступень + МШС → рунг |
| `build_poly_context_by_rung()` | `program_dispatcher.py` | Поли-контекст по рунгу |
| `get_program_seed_context()` | `program_dispatcher.py` | Контекст программы (ЛР/РР/ИР) |
| `derive_volume_spec()` | `program_dispatcher.py` | Объём руководства (строки по рунгу) |
| `get_weights()` | `program_weights.py` | Веса программ по рунгу |
| `get_leading_program()` | `program_weights.py` | Ведущая программа по рунгу |
| `select_assignment()` | `assignment_selector.py` | Выбор задания из каталога |
| `build_snapshot()` | `prefetch-knowledge-snapshot.py` | Предзагрузка знаний (knowledge-mcp offline) |

---

## Переменные окружения

```env
ANTHROPIC_API_KEY=...
LEARNING_DB_URL=...           # Neon learning БД
INDICATORS_DB_URL=...         # Neon indicators БД
TELEGRAM_BOT_TOKEN=...        # Бот для уведомлений
GITHUB_APP_ID=...             # GitHub App для записи в приватные репо
GITHUB_APP_PRIVATE_KEY=...    # Приватный ключ GitHub App
```

---

## GitHub App — права

Нужен GitHub App с правом записи в:
- `aisystant/*-guide` — приватные репо мирового контура
- `mim-school/*-guide` — приватные репо российского контура

Создаётся в рамках WP-415 (GitHub App для синхронизации орг). Если WP-415 ещё не готов — создать отдельный App с минимальными правами (`contents: write` на целевые репо).

---

## GKE — Kubernetes CronJob

```yaml
schedule: "0 6 * * *"       # ежедневно 06:00 UTC
```

Два режима (определяется флагом при запуске или env):
- **Полный** (понедельник): все пилоты, еженедельное + дневное руководство
- **Дневной** (вт–вс): только дневное руководство

Фильтр: обрабатывать только пилотов с `has_iwe_git=False`. Пилоты с IWE генерируют самостоятельно.

---

## Зависимости

| Зависимость | Статус | Что нужно |
|-------------|--------|-----------|
| GKE-кластер (WP-285 Ф2) | prerequisite | Кластер для деплоя |
| GitHub App (WP-415) | pending | Права на запись в приватные guide-репо |
| WP-149 Ф-platform-guide | pending | Детали формата «тайного гида» |

---

## Следующий шаг

1. Андрей подтверждает план или уточняет.
2. Церен выносит функции в отдельный модуль / Dockerfile в `DS-autonomous-agents`.
3. Деплой в GKE после готовности GitHub App.
