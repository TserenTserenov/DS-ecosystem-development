---
id: student-stage-accounting-concept
version: v1.1
status: approved
created: 2026-05-07
authors: [Тсерен, Claude]
related_pack: PD.FORM.080, PD.FORM.089, PD.FORM.093
related_wps: [WP-214 Ф10, WP-121, WP-151, WP-117]
---

# Концепция учёта и расчёта ступени Ученика в IWE

> **Назначение:** Этот документ описывает как платформа определяет, на какой ступени находится Ученик — через какие данные, по каким критериям, с каким запасом эволюционируемости. Он является source-of-truth для реализации расчётного движка.

---

## 1. Скоуп

**Охватывает:**
- Ступени 1–5 программы «Личное развитие» (ЛР): Случайный → Практикующий → Систематический → Дисциплинированный → Проактивный
- Учёт и наблюдение на ступени 5: человек остаётся в системе, может упасть со ступени
- Начисление баллов за все действия
- Классификация действий по доменам (learning / practice / work)

**НЕ охватывает:**
- Программу «Рабочее развитие» (РР) — отдельный трек, будущий РП
- M3 (профессиональные методы) — за рамкой ЛР
- Автономные ночные агенты (WP-132) — отдельный РП

---

## 2. Три домена активности

Каждое действие пользователя принадлежит одному из трёх доменов. Домен определяет: влияет ли действие на ступень Ученика.

| Домен | Определение | Влияет на ступень | Трек РР | Баллы |
|-------|------------|:-----------------:|:-------:|:-----:|
| `learning` | Освоение нового: уроки, практикумы, KE-сессии, стратсессии, клуб | ✅ | — | ✅ |
| `practice` | Применение изученного в IWE: Day/Week Close, Pack-обновление, IWE-сессия, WP в governance-репо | ✅ | — | ✅ |
| `work` | Рабочая активность: коммиты на продуктовых репо, закрытые WP в DS-IT/DS-MCP, WakaTime рабочие часы | — | ✅ (будущее) | ✅ |

**Инвариант:** ступень Ученика (`stage_raw`) считается ТОЛЬКО по `learning + practice` событиям. `work`-события собираются и дают баллы, но в stage-gate не входят.

### Классификация event_type по домену

| event_type | domain | Обоснование |
|---|---|---|
| `lesson_completed` | `learning` | Урок LMS |
| `qualification_granted` | `learning` | Подтверждение квалификации |
| `training_passed` | `learning` | Практикум LMS |
| `marathon_tasks` | `learning` | Марафон LMS |
| `strategy_session_completed` | `learning` | Производство системного артефакта (M4) |
| `knowledge_extracted` | `learning` | KE-сессия = производство знания |
| `club_post_created` | `learning` | Публикация в Клубе — обратная связь в обучении |
| `club_topic_created` | `learning` | Тема в Клубе |
| `day_plan_opened` | `practice` | Слот ОРЗ — открытие дня |
| `day_plan_closed` | `practice` | Слот ОРЗ — закрытие с рефлексией |
| `week_plan_closed` | `practice` | Ритм недели |
| `month_plan_closed` | `practice` | Долгосрочный ритм |
| `slot_logged` | `practice` | Слот саморазвития в боте |
| `pack_updated` | `practice` | Обновление Pack (M2) |
| `iwe_session` | `practice` | Время в Claude Code |
| `wp_created` | `practice` | Создание РП в IWE governance-репо |
| `wp_closed` (IWE-репо) | `practice` | Закрытие РП в DS-my-strategy (M4) |
| `git_commit` (IWE-репо) | `practice` | Коммит в Pack/governance-репо |
| `wp_closed` (продуктовые репо) | `work` | Рабочий РП |
| `git_commit` (продуктовые репо) | `work` | Коммит в DS-IT/DS-MCP |

**Разграничение git_commit по репо** (через `reference.repo_domain_map`):

| Репо | domain |
|------|--------|
| DS-my-strategy, PACK-personal, PACK-digital-platform, PACK-agent-rules, FMT-exocortex-template, DS-autonomous-agents | `practice` |
| DS-IT-systems, DS-MCP, DS-ecosystem-development | `work` |

---

## 3. RCS-слоты как измерения (от PD.FORM.089)

Семь слотов RCS. Для расчёта ступени используются **стержневые**: M1, M2, M4, W.

| Слот | Роль в расчёте ступени | Когда включается в gate |
|------|------------------------|------------------------|
| **M1** | Собранность — основа всех ступеней | **1→2, 2→3, 3→4, 4→5** |
| **M2** | Культура работы — регулярные действия любой системной практики | **3→4, 4→5** (не блокирует 1→3) |
| **M4** | Системное мышление — артефакты и разборы | **3→4, 4→5** (не блокирует 1→3) |
| **W** | Мировоззрение — скомпилированные мемы | **2→3** (минимум), растёт к **4→5** |

**Связь W → M4:** M4 (системный разбор) вырастает из W (системный взгляд). M4.idx не может устойчиво обгонять W.idx более чем на 1.

M3, IT, A — вспомогательные, в `stage_raw` не входят. A — gate только для перехода 4→5.

---

## 3а. Мировоззрение (W) — измерение через мемы

**Источник:** PD.CAT.001 (64 мема × 5 областей, колонка «Блокирует переход»)

W.baseline_idx определяется тем, какие **блокирующие мемы скомпилированы** в поведение человека.

| W.idx | Что скомпилировано | Примеры мемов из PD.CAT.001 |
|-------|-------------------|------------------------------|
| **1** | Мемы 1→2 ещё активны | M-002 «теория бесполезна», M-008 «я нормальный», M-022 «я ленивый» |
| **2** | Мемы 1→2 скомпилированы, мемы 2→3 ещё активны | M-005 «прочитал = знаю», M-028 «инсайт = изменение», M-027 «мышление в голове» |
| **3** | Мемы 2→3 скомпилированы, мемы 3→4 ещё активны | M-003 «мой опыт говорит об обратном», M-009 «успех = проблемы исчезнут», M-030 «поздно меняться» |
| **4** | Мемы 3→4 скомпилированы, мемы 4→5 ещё активны | M-052 «проактивность = больше инициативы», M-015 «ИИ скажет что делать» |
| **5** | Все блокирующие мемы скомпилированы, передаёт мемы другим | — |

**Три механизма измерения W (по возрастанию точности):**

1. **Авто-косвенный** — платформа видит поведение через события. Регулярные Day Close → M-028 скомпилирован. WP-контексты с системным языком → M-027 скомпилирован. `pack_updated`, `knowledge_extracted` → M-005, M-006 скомпилированы. Применяется на всех ступенях как фоновый сигнал.

2. **Периодический опрос (бот)** — 1 раз в 2–4 недели. Вопрос из Диагноста (PD.FORM.089 §6.1): «Когда что-то идёт не так — как ты это объясняешь?» Ответ калибрует W.idx.

3. **Диалог Оценщика мировоззрения (R29)** — для gate 3→4 и 4→5. Специализированная роль агента (см. §3б). Обязательна для подтверждения W.idx ≥ 3+.

**Дополнительные сигналы W на ступенях 4–5:**
- **Неудовлетворённости** — человек на ст. 4–5 формулирует системные неудовлетворённости (проблемы надсистемного масштаба), не личные жалобы. Оценщик различает: «меня бесит X» (ст. 1–2) vs «в системе X не хватает механизма Y» (ст. 4–5).
- **Калибр личности** — масштаб охвата системных изменений, которые человек инициирует или удерживает. Ст. 4 = Я/Ближний круг, ст. 5 = организация/экосистема.

**W не блокирует ступени 1→2.** Включается как gate начиная с 2→3 (W.idx ≥ 2). Отслеживается по всем ступеням, но в расчёт stage_raw входит только начиная с 2→3.

---

## 3б. Оценщик мировоззрения (R29) — роль агента

> **Назначение:** Специализированная роль, которая оценивает W.baseline_idx через диалог. Дополняет Диагноста (R28) — тот определяет ступень в целом, Оценщик фокусируется только на мировоззрении.

### Обещание роли

Оценщик за ≤ 5 вопросов определяет W.idx (1–5) и выдаёт:
```
W.idx: N
Ключевые скомпилированные мемы: [список из PD.CAT.001]
Активные блокирующие мемы: [список]
Механизм вывода: [авто-косвенный / опрос / диалог]
Confidence: low | medium | high
```

### Алгоритм (три фазы)

**Фаза 1 — Авто-контекст (без вопросов):**
Оценщик запрашивает доступные данные:
- Паттерн поведения (day_plan_closed, wp_closed, knowledge_extracted за 30 дн)
- Язык артефактов (WP-контексты, Pack-обновления — есть ли системный язык)
- Результаты предыдущих опросов (если есть)

Предварительная оценка W.idx по косвенным. Если confidence ≥ medium — достаточно, далее не спрашивает.

**Фаза 2 — Калибровочные вопросы (1–3 вопроса):**
Используются якорные вопросы из PD.FORM.089 §6.1. Примеры:
- «Когда последний раз что-то шло не так — как ты это объяснял?» → внешнее/внутреннее/системное
- «Что ты сделал, чтобы изменить условия, а не только своё поведение?» → уровень агентности
- «Назови неудовлетворённость, которую ты сейчас удерживаешь» → калибр охвата (ст. 4–5)

**Фаза 3 — Верификация активных мемов (0–2 вопроса):**
По слабому месту (активный блокирующий мем из PD.CAT.001). Drill-down: «Как ты относишься к тому, что...?»

### Сигналы по ступеням

| W.idx | Что говорит Оценщик в диалоге |
|-------|-------------------------------|
| **1** | Объясняет проблемы внешними причинами. «Мне не повезло», «они не понимают» |
| **2** | Видит себя как систему, но окружение — вне контроля. Управляет временем и методами |
| **3** | Осознанно меняет среду. «Я перестроил своё окружение, убрал X, добавил Y» |
| **4** | Описывает мир через роли и системы. Формулирует неудовлетворённости на уровне надсистемы. Калибр = Я/Ближний круг → Организация |
| **5** | Agency + передача культуры. «Создал условия, где другие начали меняться». Калибр = Экосистема |

### Ограничения роли

- Оценщик **не даёт рекомендации** (это Навигатор, R27)
- Оценщик **не определяет ступень в целом** (это Диагност, R28) — только W.idx
- Оценщик **не выносит оценочных суждений** о личности: только фиксирует, что скомпилировано, что нет
- Язык: русский, бытовой, без академических конструкций

### Тренировочный набор (примеры для файн-тюнинга)

Каждый пример = диалог (≤5 реплик) + эталонный вывод `W.idx + confidence + active_blocking_memes`.

Структура примера:
```yaml
scenario: "ступень 2→3 gate"
context:
  day_plan_closed_30d: 18
  knowledge_extracted_30d: 3
  wp_closed_30d: 1
dialog:
  - q: "Когда последний раз что-то шло не так — как ты это объяснял?"
    a: "Я просто не успел, слишком много задач навалилось"
  - q: "Что ты сделал, чтобы таких ситуаций стало меньше?"
    a: "Ничего, жду когда станет меньше задач"
output:
  W_idx: 2
  confidence: medium
  active_memes: ["M-028 инсайт=изменение", "M-029 жду условий"]
  compiled_memes: ["M-022 я ленивый — нет, работает стабильно"]
```

Тренировочный датасет создаётся в рамках WP-151 (характеристики и измерение). Минимум 20 сценариев × 5 ступеней = 100 примеров.

---



> **Источник:** PD.FORM.089 §5.1–5.3

### 4.1 Формула

```
# Ступени 1–2: только M1
stage_1_2 = M1.baseline_idx

# Ступень 3: M1 + W-gate
stage_2_3 = M1.baseline_idx >= 3 AND W.baseline_idx >= 2

# Ступени 3–4 и выше: все стержневые
stage_raw = min(M1.baseline_idx, M2.baseline_idx, M4.baseline_idx)

# W не входит в min, но ограничивает сверху начиная с ступени 3:
if stage_raw >= 3 and W.baseline_idx < stage_raw - 1:
    stage = W.baseline_idx + 1  # W не может сильно отставать
```

Bottleneck = слот с минимальным значением среди активных для данной ступени.

### 4.2 Baseline = скользящее среднее, окно зависит от ступени

Все пороги считаются по **baseline** (устойчивый уровень), а не по «сейчас». Всплеск в одну неделю не поднимает baseline.

| Переход | Период наблюдения для baseline | Логика |
|---------|-------------------------------|--------|
| 1 → 2 | **1–2 недели** | Достаточно первых устойчивых признаков активности |
| 2 → 3 | **4 недели** | Нужен устойчивый ритм (не один всплеск) |
| 3 → 4 | **8 недель** | Нужна долгосрочная стабилизация |
| 4 → 5 | **8+ недель** (тройной gate) | Характеристики выпускника формируются медленно |

### 4.3 Индексы слотов и их observable proxy

Каждый baseline_idx — описание устойчивого уровня (PD.FORM.089 §4). Платформа вычисляет idx по событиям из domain_event.

#### M1 (Собранность) — anchor: часы/неделю в среднем

| idx | Anchor ч/нед | Proxy из domain_event (за период baseline) |
|-----|-------------|---------------------------------------------|
| **1** | ~2 | day_plan_closed + slot_logged < 2 дней/нед в среднем |
| **2** | ~5 | ≥ 2 дней/нед с (day_plan_closed ИЛИ slot_logged), период 1–2 нед |
| **3** | ~6 | ≥ 4 дней/нед с day_plan_closed, период 4 нед; восстановление после срыва ≤ 1 нед |
| **4** | ~8 | ≥ 5 сессий/нед в среднем за 8 нед; срывы < 3 дней |
| **5** | ~10+ | ≥ 5 сессий/нед стабильно 8+ нед, адаптация к контексту |

> **Пример (слова пользователя):** «5 сессий саморазвития в неделю в среднем за 8 недель» → M1.baseline_idx = 4.

#### M2 (Культура работы) — anchor: количество систематических действий

> M2 измеряет наличие и регулярность действий по культуре работы — планирование, рефлексия, развитие практики. Не важен конкретный инструмент (IWE, Notion, бумажный дневник). Сейчас первичный источник — IWE-события. Для пользователей без IWE — периодический опрос в боте.

| idx | Характеристика | Proxy: IWE-события (за период baseline) | Fallback: опрос |
|-----|---------------|----------------------------------------|-----------------|
| **1** | Нет регулярной практики | Нет day_plan_closed, нет pack_updated, нет knowledge_extracted | «Веду ли я регулярно какую-то практику?» → нет |
| **2** | Эпизодические действия | day_plan_closed < 2/нед ИЛИ ≤ 1 week_plan_closed за 4 нед | Редко, нерегулярно |
| **3** | Регулярная практика | day_plan_closed ≥ 4/нед + week_plan_closed каждую нед + pack_updated/knowledge_extracted ≥ 4 за 30 дн | Ежедневно или через день, стабильно |
| **4** | Зрелая практика | Всё из idx 3 + month_plan_closed + pack_updated ≥ 8 за 30 дн | Полный цикл: день, неделя, месяц |
| **5** | Передача и расширение практики | Всё из idx 4 + strategy_session_completed регулярно + артефакты для других | Создаёт практику для окружающих |

#### M4 (Системное мышление) — anchor: применяемые различения

| idx | Различений | Proxy из domain_event (за период baseline) |
|-----|------------|---------------------------------------------|
| **1** | 0 | Нет wp_closed, нет strategy_session_completed, нет knowledge_extracted |
| **2** | 1–2 | knowledge_extracted ≥ 1 за период ИЛИ wp_closed ≥ 1 (любой) |
| **3** | 5–7 | knowledge_extracted ≥ 4 за 30 дн ИЛИ wp_closed ≥ 2 за 60 дн |
| **4** | 10+ | (wp_closed + strategy_session_completed) ≥ 5 за 60 дн, knowledge_extracted ≥ 8 за 30 дн |
| **5** | Интегрировано | Всё из idx 4 + артефакты передачи знания другим (club_post_created с системным языком) |

#### W (Мировоззрение) — диагностируется Диагностом (MIM.R.009), не авто

| idx | Фаза | Признак |
|-----|------|---------|
| **1** | Нет осознания | Внешние объяснения проблем |
| **2** | «Я — система» | Видит ресурсы, методы |
| **3** | «Окружение влияет» | Осознанно настраивает среду |
| **4** | «Мир — система, я деятель» | Описывает через роли и границы |
| **5** | Agency + передача | Инициирует изменения, обучает других |

W.baseline_idx определяется через диалог (≤ 5 вопросов Диагноста) + аудит артефактов, а не автоматически по событиям.

---

## 5. Критерии ступеней (конкретные пороги v1)

> Числа — калибровка v1 по PD.FORM.089. Пересмотр после 30 дн пилота на реальных данных.
> **Принцип:** M1 — gate для ВСЕХ переходов. M2 и M4 включаются только с 3→4. W включается с 2→3.

### Ступень 1 → 2: Случайный → Практикующий

**Период baseline: 1–2 недели. Gate: только M1.**

| Слот | Что нужно | Proxy из domain_event |
|------|-----------|-----------------------|
| **M1** | baseline_idx ≥ 2 (~5 ч/нед) | day_plan_closed ИЛИ slot_logged ≥ 2 дней/нед в среднем за 1–2 нед |

Дополнительный сигнал (не gate): lesson_completed ≥ 1 за 2 нед.

### Ступень 2 → 3: Практикующий → Систематический

**Период baseline: 4 недели. Gate: M1 + W.**

| Слот | Что нужно | Proxy из domain_event |
|------|-----------|-----------------------|
| **M1** | baseline_idx ≥ 3 (~6 ч/нед, 4+ дня/нед) | day_plan_closed ≥ 4 дней/нед в среднем за 4 нед (≥ 16 за 28 дн) |
| **W** | baseline_idx ≥ 2 («Я — система») | Диагност (≤ 5 вопросов) ИЛИ авто-косвенный (регулярный Day Close + артефакты) |

Дополнительный сигнал (не gate): training_passed ≥ 3 за 30 дн.

### Ступень 3 → 4: Систематический → Дисциплинированный

**Период baseline: 8 недель. Gate: M1 + M2 + M4 + W.**

| Слот | Что нужно | Proxy из domain_event |
|------|-----------|-----------------------|
| **M1** | baseline_idx ≥ 4 (~8 ч/нед, ≥ 5 сессий/нед) | day_plan_closed ≥ 5/нед в среднем за 8 нед (≥ 40 за 56 дн); восстановление после срыва ≤ 3 дня |
| **M2** | baseline_idx ≥ 3 (регулярная практика) | day_plan_closed ≥ 4/нед + week_plan_closed каждую нед + pack_updated + knowledge_extracted ≥ 4 за 30 дн |
| **M4** | baseline_idx ≥ 3 (5–7 различений) | knowledge_extracted ≥ 4 за 30 дн ИЛИ wp_closed ≥ 2 за 30 дн |
| **W** | baseline_idx ≥ 3 («Окружение влияет на меня») | Диагност (обязателен для 3→4) |

Дополнительный сигнал (не gate): training_passed ≥ 8 за 60 дн + marathon_tasks ≥ 5.

### Gate 4 → 5: Дисциплинированный → Проактивный (тройной)

**Источник:** PD.FORM.080 §7.1 + PD.FORM.089 §5.2 + PD.FORM.093 §7.2

Три условия одновременно:

**Gate 1 — rcs_gate (рычаги, автоматический):**
```
stage_raw ≥ 4 (min(M1,M2,M4).baseline_idx ≥ 4)
AND W.baseline_idx ≥ 4
AND A.baseline_idx ≥ 4
```

**Gate 2 — graduate_gate (характеристики выпускника, автоматический):**
```
ясность.baseline ≥ 4 AND агентность.baseline ≥ 4
AND собранность.baseline ≥ 4 AND регулярность.baseline ≥ 4
AND способность_производить.baseline ≥ 4
```
(PD.FORM.093 §5.4 — 5 gate-характеристик; 3 supporting ≥ 3)

**Gate 3 — real_change (мировоззренческий разворот, ручной):**
Диагност (MIM.R.009) через ≤ 3 вопроса подтверждает ≥ 1 инициированное изменение на уровне охвата 1–2 (Я / Ближний круг). Confidence ≥ medium. Хранится в `stage_transitions.evidence`.

---

## 5а. Архитектура данных (4 слоя)

```
Слой 1: Источники
  LMS (activity-hub БД) — lesson_completed, training_passed, qualification_granted
  Бот (aist_bot) — slot_logged, command_invoked
  Claude Code Hooks — day_plan_opened/closed, week_plan_closed, iwe_session,
                      knowledge_extracted, wp_created/closed, pack_updated
  Git (global post-commit) — git_commit
  Клуб Discourse — club_post_created, club_topic_created (через WP-296)
  WakaTime — work-кодинг (через heartbeat)

Слой 2: События (append-only)
  domain_event (platform БД, public schema)
  + reference.event_schemas (контракт payload)
  + reference.repo_domain_map (git_commit domain классификатор)

Слой 3: Показатели (расчётный)
  indicators.current (per-indicator cursor: account_id × indicator)
  indicators.weekly_snapshot (materialized MA-8)
  reference.indicator_definitions (формулы + rubric + grace_period)

Слой 4: Ступень (gate)
  PACK-agent-rules/rules/SR.001–SR.004 (stage_gate правила)
  reference.stage_criteria (загружены из SR.NNN.md)
  reference.criteria_formula_binding (version coupling: criteria_v × formula_v)
  indicators.stage_current (текущая ступень per account)
  indicators.stage_transitions (история переходов с direction + evidence)
```

### Ключевые таблицы

```sql
-- Классификатор репозиториев для git_commit
reference.repo_domain_map (
  repo_name TEXT PRIMARY KEY,
  activity_domain TEXT NOT NULL  -- 'practice' | 'work'
)

-- Текущий показатель (per-indicator cursor)
indicators.current (
  account_id UUID,
  indicator TEXT,           -- 'M1', 'M2', 'M4', 'W', ...
  value_now NUMERIC,
  value_baseline NUMERIC,
  formula_version TEXT,
  last_event_id BIGINT,
  updated_at TIMESTAMPTZ,
  PRIMARY KEY (account_id, indicator)
)

-- Materialized weekly baseline (масштабируемость MA-8)
indicators.weekly_snapshot (
  account_id UUID,
  indicator TEXT,
  iso_week TEXT,            -- '2026-W19'
  value NUMERIC,
  formula_version TEXT,
  PRIMARY KEY (account_id, indicator, iso_week)
)

-- Текущая ступень
indicators.stage_current (
  account_id UUID PRIMARY KEY,
  stage INTEGER,            -- 1..5
  criteria_version TEXT,    -- 'v1'
  computed_at TIMESTAMPTZ
)

-- История переходов ступени
indicators.stage_transitions (
  id BIGSERIAL PRIMARY KEY,
  account_id UUID,
  from_stage INTEGER,
  to_stage INTEGER,
  direction TEXT,           -- 'up' | 'down'
  triggered_by JSONB,       -- {indicator: value, ...} что сработало
  evidence JSONB,           -- для gate 4→5: real_change подтверждение
  criteria_version TEXT,
  occurred_at TIMESTAMPTZ
)

-- Version binding (Б1 блокер эволюционируемости)
reference.criteria_formula_binding (
  criteria_version TEXT,
  indicator TEXT,
  formula_version TEXT,
  PRIMARY KEY (criteria_version, indicator)
)
```

---

## 5б. Расчётный pipeline (end-to-end, по таблицам)

> **Цель раздела:** показать как из событий в `domain_event` получается ступень в `indicators.stage_current`. Каждый показатель — конкретный SQL-запрос.

### Шаг 1: Фильтрация событий по домену

```sql
-- Только learning + practice входят в stage_raw
SELECT *
FROM platform.domain_event e
WHERE e.account_id = $1
  AND e.activity_domain IN ('learning', 'practice')
  AND e.occurred_at >= NOW() - ($period || ' days')::INTERVAL
```
Где `$period` зависит от ступени-кандидата (см. §4.2): 14 (1→2), 28 (2→3), 56 (3→4+).

### Шаг 2: Расчёт baseline_idx по слотам

#### M1.baseline_idx — собранность (часы/дни в неделю)

```sql
-- Считаем активные дни в неделю за период baseline
WITH active_days AS (
  SELECT DATE(occurred_at) AS d, COUNT(*) AS events
  FROM platform.domain_event
  WHERE account_id = $1
    AND event_type IN ('day_plan_closed', 'slot_logged')
    AND activity_domain IN ('learning', 'practice')
    AND occurred_at >= NOW() - ($period || ' days')::INTERVAL
  GROUP BY DATE(occurred_at)
)
SELECT
  COUNT(*)::FLOAT / ($period::FLOAT / 7.0) AS days_per_week_avg
FROM active_days;
```
Маппинг в idx: `<2 → 1`, `2–3 → 2`, `4 → 3`, `≥5 → 4`, `≥5 stable 8w → 5`.

#### M2.baseline_idx — регулярность культуры работы

```sql
-- Систематические действия по культуре работы: день/неделя/месяц + практика
-- Fallback для пользователей без IWE: indicators.current WHERE indicator='M2' AND last_evaluator='bot_survey'
WITH metrics AS (
  SELECT
    SUM(CASE WHEN event_type='day_plan_closed' THEN 1 END) AS days,
    SUM(CASE WHEN event_type='week_plan_closed' THEN 1 END) AS weeks,
    SUM(CASE WHEN event_type='month_plan_closed' THEN 1 END) AS months,
    SUM(CASE WHEN event_type IN ('pack_updated','knowledge_extracted') THEN 1 END) AS pack
  FROM platform.domain_event
  WHERE account_id = $1
    AND occurred_at >= NOW() - ($period || ' days')::INTERVAL
)
SELECT
  CASE
    WHEN days < 2 AND pack = 0 THEN 1
    WHEN days < 8 AND pack < 4 THEN 2
    WHEN days >= 16 AND weeks >= 3 AND pack >= 4 THEN 3
    WHEN days >= 40 AND months >= 1 AND pack >= 8 THEN 4
    WHEN days >= 40 AND months >= 2 AND pack >= 16 THEN 5
  END AS m2_idx
FROM metrics;
```
Период `$period` соответствует ступени-кандидату. Числа калибруются из §5.

#### M4.baseline_idx — системность (различения + артефакты)

```sql
WITH artifacts AS (
  SELECT
    SUM(CASE WHEN event_type='knowledge_extracted' THEN 1 END) AS ke,
    SUM(CASE WHEN event_type='wp_closed' AND activity_domain='practice' THEN 1 END) AS wp,
    SUM(CASE WHEN event_type='strategy_session_completed' THEN 1 END) AS ss
  FROM platform.domain_event
  WHERE account_id = $1
    AND occurred_at >= NOW() - ($period || ' days')::INTERVAL
)
SELECT
  CASE
    WHEN (ke + wp + ss) = 0 THEN 1
    WHEN (ke + wp + ss) <= 2 THEN 2
    WHEN ke >= 4 OR wp >= 2 THEN 3
    WHEN (wp + ss) >= 5 AND ke >= 8 THEN 4
    WHEN (wp + ss) >= 8 AND ke >= 12 THEN 5
  END AS m4_idx
FROM artifacts;
```

#### W.baseline_idx — мировоззрение

Не вычисляется SQL-запросом. Источник:
- `indicators.current` со столбцом `last_evaluator` (`R29` для ручной оценки) и `evidence` (JSONB)
- Для авто-косвенного: SQL-запрос на наличие системного языка в WP-контекстах (LIKE `%система%`, `%роль%`, `%инвариант%`) — даёт фоновую оценку, но не gate

```sql
SELECT value_baseline AS w_idx, evidence
FROM indicators.current
WHERE account_id = $1 AND indicator = 'W';
```

### Шаг 3: Применение формулы ступени

```python
# pseudo-code (соответствует §4.1)
def calc_stage(account_id, period_days):
    m1 = calc_m1_idx(account_id, period_days)
    w  = read_w_idx(account_id)

    # 1→2: только M1
    if m1 < 2:
        return 1

    # 2→3: M1 + W
    if m1 < 3 or w < 2:
        return 2

    # 3→4+: M1 + M2 + M4 + W
    m2 = calc_m2_idx(account_id, period_days)
    m4 = calc_m4_idx(account_id, period_days)
    stage_raw = min(m1, m2, m4)

    # W ограничивает сверху начиная с stage 3
    if stage_raw >= 3 and w < stage_raw - 1:
        return w + 1

    # Gate 4→5 — тройной (см. §5)
    if stage_raw >= 4:
        a = read_a_idx(account_id)
        if not (w >= 4 and a >= 4):
            return 4
        if not graduate_gate_passed(account_id):
            return 4
        if not real_change_evidence_exists(account_id):
            return 4
        return 5

    return stage_raw
```

### Шаг 4: Запись результата

```sql
-- Идемпотентная запись текущей ступени
INSERT INTO indicators.stage_current (account_id, stage, criteria_version, computed_at)
VALUES ($1, $2, 'v1', NOW())
ON CONFLICT (account_id) DO UPDATE
SET stage = EXCLUDED.stage,
    criteria_version = EXCLUDED.criteria_version,
    computed_at = EXCLUDED.computed_at
WHERE indicators.stage_current.stage IS DISTINCT FROM EXCLUDED.stage;

-- Лог перехода (если ступень изменилась)
INSERT INTO indicators.stage_transitions
  (account_id, from_stage, to_stage, direction, triggered_by, evidence, criteria_version, occurred_at)
VALUES ($1, $old_stage, $new_stage,
        CASE WHEN $new_stage > $old_stage THEN 'up' ELSE 'down' END,
        jsonb_build_object('m1', $m1_idx, 'm2', $m2_idx, 'm4', $m4_idx, 'w', $w_idx),
        $evidence_jsonb, 'v1', NOW());
```

### Шаг 5: Верификация по таблицам

| Что проверяется | SQL-запрос | Ожидание |
|---|---|---|
| Все события классифицированы | `SELECT COUNT(*) FROM domain_event WHERE activity_domain IS NULL` | 0 |
| Cursor продвинулся | `SELECT last_event_id FROM indicators.current WHERE account_id=$1` | Растёт со временем |
| Ступень соответствует индексам | `SELECT stage, triggered_by FROM stage_transitions WHERE account_id=$1 ORDER BY occurred_at DESC LIMIT 1` | min из triggered_by ≥ stage (с учётом W-cap) |
| version binding активен | `SELECT formula_version FROM criteria_formula_binding WHERE criteria_version='v1'` | Все стержневые indicator'ы перечислены |

---

## 6. Принципы эволюционируемости

**P1. Данные отдельно от критериев.** `domain_event` — append-only факты. Критерии в `reference.stage_criteria` (загружаются из SR.NNN.md). Пересмотр критериев не требует пересчёта истории событий.

**P2. Один event_type — один owner.** `reference.event_schemas` фиксирует кто может писать каждый тип. Нарушение = ошибка синхронизации.

**P3. Version binding обязателен.** При смене формулы показателя — новая `formula_version`. Привязка `criteria_version → formula_version` через `criteria_formula_binding`. Без этой таблицы пересмотр критериев ломает историческую интерпретацию.

**P4. Grace period для новых источников.** Новый event_type добавляется в `indicator_definitions.grace_period_days` (по умолчанию 14 дней). За этот период он не влияет на понижение ступени, только на повышение. Защита от ложной регрессии при добавлении нового сигнала.

**P5. Прокси ≠ критерий.** `day_plan_closed` — прокси M1. Прокси может меняться (лучший источник данных), критерий (`M1 ≥ X`) — нет. Код оперирует показателями, не event_type напрямую.

**P6. Двойной gate против ложной регрессии (gate 4→5).** Количественный (rcs + graduate_gate) необходим, но недостаточен. Gate 3 (real_change) предотвращает сценарий «знает, но не делает».

**P7. Эволюция через SR.NNN.md, не через хардкод.** Все пороги — в Pack (PACK-agent-rules/rules/SR.NNN.md). Программист не трогает числа в коде при калибровке. `generate-rules-registry.py` перегенерирует `.claude/rules-registry.yaml` → `reference.stage_criteria` синхронизируется.

---

## 7. Что НЕ меняет ступень Ученика

- Рабочие коммиты (`git_commit` в DS-IT/DS-MCP) — domain=`work`, не входят в stage_raw
- WakaTime рабочие часы — domain=`work`
- `wp_created` — только сигнал намерения, не доказательство
- Квалификация МИМ (Реформатор, Практик) — это отдельная шкала (LMS, не ступень Ученика)
- Баллы — накапливаются независимо от ступени

---

## 8. Открытые вопросы для утверждения

| # | Вопрос | Вариант A | Вариант B | Статус |
|---|--------|-----------|-----------|--------|
| Q1 | Пороги и периоды (§5) — корректно откалиброваны по PD.FORM.089? | Утвердить v1, пересмотр после 30 дн пилота на реальных данных | Скорректировать числа сейчас | ✅ A — утвердить v1 |
| Q2 | `wp_closed` в DS-my-strategy = `practice` или зависит от WP-типа? | Все WP в governance = `practice` (репо = классификатор) | WP-тип продуктовый = `work` даже в governance | ✅ A — репо = классификатор |
| Q3 | M4 proxy для 3→4: `wp_closed + strategy_session` ≥5 — или KE тоже входит в M4 proxy? | wp+стратсессия только (артефакты M4) | + knowledge_extracted (тоже системная работа) | ✅ B — +knowledge_extracted |
| Q4 | `activity_domain` в event payload: поле в JSON или колонка? | Поле в payload JSONB (нет миграции) | Колонка в domain_event (явная типизация, миграция нужна) | ✅ B — колонка |
| Q5 | W.baseline_idx для ст. 2→3: idx ≥ 2 («Я-система») достаточно или ≥ 3? | idx ≥ 2 (достаточно для Систематического) | idx ≥ 3 (окружение тоже должно осознаваться) | ✅ A — idx ≥ 2 |

---

## 9. Связи

- **Источник ступеней:** PD.FORM.080 (нормативная матрица), PD.FORM.089 (RCS-слоты)
- **Gate Д→П:** PD.FORM.089 §5.2, PD.FORM.093 §5.4 и §7.2
- **Мемы (W-измерение):** PD.CAT.001 (64 мема × 5 областей, колонка «Блокирует переход»)
- **Роли агентов:** R27 Навигатор, R28 Диагност, R29 Оценщик мировоззрения (§3б этого документа)
- **Правила агента:** PACK-agent-rules/rules/SR.001–SR.004 (создаются в WP-214 Ф10.1)
- **Реализация:** `DS-IT-systems/activity-hub/activity_hub/profiler/dt_calc.py::calc_student_stage()`
- **Сбор событий:** `.claude/hooks/iwe-orz-tracker.sh`, `.claude/hooks/iwe-wp-tracker.sh`, `~/.git-templates/hooks/post-commit`
- **Баллы:** WP-121 Ф2 (points_subscriber.py использует те же domain_event)
- **Personal-guide:** WP-149 Ф9 (render использует indicators.current)
- **Тренировочный датасет R29:** WP-151 (создание 100 сценариев для файн-тюнинга)
