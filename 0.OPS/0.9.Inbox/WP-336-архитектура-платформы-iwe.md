# WP-336: Контекст платформы Aisystant IWE для архитектора
## Документ для Андрея

> **Связанные документы:**
> - [Обещание пользователю и сценарии использования](WP-336-обещание-и-сценарии.md)
> - [Инвентарь сервисов Track A → Track B](WP-285-services-inventory.md) — текущая инфраструктура (16 CF Workers + Python, 16 БД), план миграции на GKE

---

<details open>
<summary><b>1. Что строим и зачем</b></summary>

Aisystant IWE — среда профессионального роста: специалист работает быстрее и системнее, развивает системное мышление и применяет его к собственному рабочему окружению. Платформа ведёт человека по пяти ступеням Ученика (Случайный → Проактивный) — меняет интерфейс, содержание и набор сервисов по мере роста. Это **Букварь-модель (Из Алмазного века)**: адаптация к конкретному человеку, не к масштабу пользователей.

Безопасность данных гарантируется архитектурно через **Parliament Model**: N доменных агентов + 1 координатор + 1 верификатор (read-only). Ни один агент не имеет доступа за пределы своего домена.

</details>

---

<details>
<summary><b>2. Что уже построено</b></summary>

Текущий инвентарь — [WP-285-services-inventory.md](WP-285-services-inventory.md): 16 CF Workers, Python-сервисы, 16 Neon БД, матрица ответственности Андрей/Паша, план миграции Track A → Track B (GKE + Cloud SQL).

</details>

---

<details>
<summary><b>3. Data Layers: Трёхслойное разделение данных</b></summary>

Все остальные части платформы (events, Parliament Model, агентный уровень) строятся поверх этих трёх слоёв.

### Слой 1: Персона (Git, пользователь владеет) — ~10%

```
~/.iwe/persona/
├─ methods.md              # Какие методы применяю (мой выбор)
├─ captures/               # Явные знания, которые я зафиксировал
├─ preferences.json        # Настройки интерфейса, выбранные сервисы
└─ goals.md                # Какие цели преследую в этом периоде
```

**Читается:** из Git репо, один раз за сессию  
**Пишется:** пользователем вручную или через UI captures  
**Гарантия:** пользователь контролирует — export/backup/удалить

### Слой 2: Память (Neon, платформа владеет) — ~85%

**Observed Events (первичные):**
```sql
activity_log (
  user_id uuid,
  event_type text,  -- task_completed, lesson_started, day_close, iwe_session, etc.
  domain text,       -- 'learning', 'work', 'community', 'self-development'
  metadata jsonb,
  created_at timestamp
)
```

**Derived Indicators (вычисленные):**
```sql
learner_cp_profile (
  user_id uuid,
  stage int,       -- 1-5
  cp_rhy float,   -- consistency/rhythm
  cp_wld float,   -- world view (системное мышление)
  cp_skl float,   -- skills (мастерство методов)
  cp_iwe float,   -- tool mastery
  cp_int float,   -- integration (применение к себе)
  cp_agt float,   -- agency (инициатива)
  calculated_at timestamp
)

behavior_indicators (
  user_id uuid,
  bh_sys float,   -- systematicity
  bh_inv float,   -- investment
  bh_awr float,   -- awareness
  bh_per float,   -- persistence
  calculated_at timestamp
)
```

**Гарантия:** immutable audit trail (APPEND ONLY), удаление только по GDPR-запросу через Verifier

### Слой 3: Контекст (Runtime, LLM-сессия) — ~5%

```python
context = {
    "user_id": "...",
    "current_stage": 3,
    "bottleneck": "cp_iwe",
    "relevant_methods": [...],
    "recent_artifacts": [...],
    "task_description": "...",
    "available_services": ["calendar", "git", "notes", ...],
    "session_history": [...],
}
```

**Гарантия:** Ephemeral — не сохраняется, удаляется в конце сессии

### Согласованность между слоями

```
User action
    ↓
Event → activity_log (Слой 2)
    ↓
Projection worker → обновляет indicators (Слой 2)
    ↓
Persona обновляется по желанию пользователя (Слой 1)
    ↓
В следующей сессии контекст собирается из обновлённых indicators (Слой 3)
```

**Важно:** Stage считается из indicators (Neon), не из Persona. Persona подтверждает убеждения пользователя, но не является главным критерием ступени.

</details>

---

<details>
<summary><b>4. Event Sourcing: От действия к знанию</b></summary>

События — единственный способ записи в Слой 2 (Память). Всё, что пользователь делает, превращается в событие → проекция обновляет indicators.

### Event Catalog

```
domain: 'learning'
  ├─ lesson_started (lesson_id, stage_expected)
  ├─ lesson_completed (lesson_id, score, time_spent_min)
  ├─ assignment_submitted (assignment_id, solution_uri, self_assessment)
  └─ quiz_passed (quiz_id, score, attempts)

domain: 'self-development'
  ├─ day_open (timestamp)
  ├─ slot_logged (duration_min, domain, self_assessed_quality)
  ├─ method_practiced (method_id, success_indicator)
  ├─ capture_created (topic, artifact_uri)
  └─ day_close (reflection)

domain: 'work'
  ├─ iwe_session_start (tool_used: 'vscode' | 'browser' | 'bot')
  ├─ artifact_committed (file_path, tool_used)
  └─ iwe_session_end (duration_min, artifact_count)

domain: 'community'
  ├─ post_read (post_id)
  ├─ post_shared (post_id, where)
  ├─ discussion_participated (discussion_id)
  └─ co_creator_action (action_type)
```

### Projection Rules (events → indicators)

**Пример: cp_iwe (инструментальное мастерство)**

```
Rule: "Мастерство IWE = применение методов в реальных сессиях"

+ iwe_session_end (artifact_count > 0)           → +0.1
+ artifact_committed (tool_used == 'vscode')      → +0.15
+ method_practiced (method_id in ['git', ...])    → +0.2

Stagnation:
  slot_logged BUT iwe_session_count == 0 that week → no increase

Calculation (weekly):
  cp_iwe_new = min(5, cp_iwe_old + sum(events_weight))
```

### Drift Detection

```
Detector 1: Event staleness
  If no events in 7 days but user is 'active' → alert to Verifier

Detector 2: Indicator regression
  If cp.* decreases >0.5 in one week → check legitimacy, update bottleneck
```

</details>

---

<details>
<summary><b>5. Parliament Model: Триада Учёт / Доступ / Аудит</b></summary>

Определяет, кто и как читает данные из Слоя 2. Строится поверх Data Layers.

### Проблема, которую решает
Один агент с полным доступом ко всем данным пользователя = **Президент-модель** = уязвимость при скомпрометировании агента или промпта.

### Решение: Parliament Model
Разделение ответственности на **три независимые роли**:

```
User Request
    ↓
Coordinator (stateless, маршрутизирует, не хранит сырые данные)
    ├→ Domain Agent #1 (Schedule): read access only to calendar
    ├→ Domain Agent #2 (Metrics): read access only to performance indicators
    ├→ Domain Agent #3 (Community): read access only to shared posts
    └→ ...
    ↓
Verifier (isolated, read-only, cross-checks access)
    ↓
Audit Log (immutable, for compliance)
```

### Гарантия на уровне платформы
- Coordinator имеет **список разрешений** (что может просить), не полный доступ
- Каждый Domain Agent имеет **узкую зону ответственности**
- Verifier проверяет: был ли запрос в рамках Service Clause агента?
- Если нарушение → отказ на уровне API, не в промпте

### Реализация в Neon
```
Tables:
├─ access_permissions (coordinator_id, domain_id, operations)
├─ domain_agent_capabilities (agent_id, domain, allowed_tables, read_only)
├─ access_audit (timestamp, agent_id, request, result, verifier_check)
└─ service_clauses (agent_id, promise, input_signature, output_signature)
```

**Trigger:** каждый SELECT через Coordinator проверяется Verifier перед возвратом данных.

</details>

---

<details>
<summary><b>6. Service Architecture: Domain-Isolated Services</b></summary>

Сервисы — это потребители событий и данных. Каждый работает через Parliament Model: только в своём scope.

### Service Clause Pattern (DP.SC.NNN)

```
DP.SC.135: Day Close Ritual

Promise: "Помочь пользователю закрыть день, зафиксировав достигнутое"

Input:
  - reflection_text
  - artifacts
  - day_quality_self_assessment: 1-5

Output:
  - day_closed: boolean
  - events_generated: [...]
  - suggestions_for_tomorrow: [...]

SLA: response_time <1s, availability 99.9%

Failure mode:
  - reflection empty → prompt user, retry
  - artifacts unreadable → log to error_queue, alert human
```

### Domain Isolation

```
┌─ Service: Schedule
│  ├─ Can read: calendar events, user preferences
│  └─ Can't read: learning metrics, private notes
│
├─ Service: Learning
│  ├─ Can read: lesson metadata, user stage
│  └─ Can't read: work calendar, email
│
├─ Service: IWE (IDE)
│  ├─ Can read: user's own Git repo, Persona
│  └─ Can't read: other users' data
│
└─ Coordinator routes to correct agent
   ├─ Parliament Model ensures isolation
   └─ Verifier logs all access
```

### Service Composition (Ф2+)

- Пользователь подключает свой сервис (microapp)
- Microapp регистрируется в Coordinator с явным Scope
- Verifier проверяет scope перед каждым доступом
- Пользователь может отключить в любой момент

**Пример:**
```
Service: "goal-tracker"
scope: ["day_close", "iwe_session_end"]
owner: "user"

✓ CAN read: day_close events
✗ CAN'T read: learning_completed (not in scope)
```

</details>

---

<details>
<summary><b>7. Агентный уровень</b></summary>

Агенты — прикладной слой поверх Data Layers, Event Sourcing, Parliament Model и сервисов. Каждый агент:
- Имеет **Service Clause** с явным обещанием, входами, выходами и режимом отказа
- Работает только через Coordinator — не имеет прямого доступа к чужому домену
- Proверяется Verifier при каждом запросе данных

### Типы агентов

```
Диагностический     — определяет ступень Ученика и bottleneck через диалог
Портной             — строит персональное руководство под ступень + домен пользователя
Агент памяти        — хранит паттерны работы, предлагает методы и чек-листы
Артефактор          — помогает создавать, организовывать и восстанавливать контекст артефактов
Агент сообщества    — рекомендует релевантные посты и практики из сообщества
Верификатор         — read-only, проверяет соответствие доступа Service Clause'ам
Координатор         — маршрутизирует запросы между агентами, stateless
```

### Горизонт расширения

На ступенях 3-5 пользователь может регистрировать собственные агенты:
- Регистрация с явным Scope (какие события и домены доступны)
- Verifier проверяет scope перед каждым запросом
- Пользователь может отключить агент в любой момент

**Полный каталог агентов (DP.ROLE.NNN) и их Service Clause'ы** — отдельная инициатива (аналог WP-337 для агентной платформы).

</details>

---

<details>
<summary><b>8. Session Flow: Всё вместе</b></summary>

```
1. Пользователь открывает IWE (VS Code / браузер / бот)

2. Сборка Context (Слой 3):
   - Persona из Git (~50KB)            ← Слой 1
   - learner_cp_profile из Neon (~1KB) ← Слой 2 Derived
   - active_services list (~100B)
   - паттерны работы из Слоя 2 (~10KB)
   → Итого context: ~60KB

3. Агенты инициализируются:
   - Каждый агент получает только свой scope через Coordinator
   - Verifier проверяет разрешения

4. Пользователь запрашивает помощь
   - Coordinator маршрутизирует к нужному агенту
   - Агент памяти предлагает метод или чек-лист
   - Если паттерна нет → generic method для текущей ступени

5. Пользователь завершает задачу, коммитит артефакт
   - Artifact → Git (Слой 1 Персона)
   - Event artifact_committed → Neon (Слой 2 Observed)
   - Coordinator логирует доступ (Parliament Model Audit)

6. Day Close
   - Генерируется day_close event → Слой 2
   - Projection worker обновляет cp_* indicators
   - Предлагается что практиковать завтра

7. Конец сессии
   - Context очищается (ephemeral)
   - session_end event записывается
```

**Data Flow:**
```
activity_log (Слой 2 Observed)
  ↓ projection_worker (каждые 5 мин)
indicators cp_*, bh_* (Слой 2 Derived)
  ↓ context_assembler (перед каждым LLM-вызовом)
Context (Слой 3, ephemeral prompt)
  ↓ Агенты + Services (через Parliament Model)
New events → activity_log (цикл)
```

</details>

---

<details>
<summary><b>9. Что планируем</b></summary>

### Roadmap (Ф1-Ф7 WP-336)

| Фаза | Содержание | Статус |
|------|-----------|--------|
| Ф1 Discovery & Mapping (~4h) | Место документа в Pack, карта существующих проекций (DP.CONCEPT.001, DP.ARCH.001, DP.IWE.001-006), зависимости на WP-188/228/302/309 | Ожидает ответа по DP.CONCEPT.002 |
| Ф2 Карта аудитория × поверхности (~4h) | Витрина vs внутренняя часть, поверхности (web, mobile PWA, VS Code, бот), сценарии user flow | Ожидает Ф1 |
| Ф3 ArchGate × 5 развилок (~10-12h) | IDE-формат, LMS-формат, мобиль, граница витрина/внутренняя часть, Post-MVP phasing | Ожидает Ф1 |
| Ф4 Gate-1 (0.5h) | Go/no-go решение пилота по результатам Ф3 | — |
| Ф5 Pitch narrative (~10h) | VC-версия + Co-creators версия на единой архитектурной основе | Ожидает Ф4 |
| Ф6 Independent review (~4h) | Subagent cold-context ЭМОГССБ-анализ | — |
| Ф7 Финализация (~4h) | Top-3 контраргумента из review → pitch готов к рассылке | — |

### 5 архитектурных развилок (Ф3)

Каждая проходит ЭМОГССБ-скрининг (Эффективность / Мобильность / Операбельность / Гибкость / Стабильность / Стоимость / Безопасность):

| Развилка | Варианты | Решено |
|----------|---------|--------|
| IDE для работы в курсе | Cloud IDE / Embed Claude Code в браузер / Custom через Agent SDK | — |
| LMS-формат | UX-обёртка над текстом / Рабочая тетрадь → применение в IWE / Гибрид | — |
| Мобильное расширение | Бот как основной интерфейс / **PWA с адаптивным дизайном** / Native iOS+Android | ✅ PWA (оперативка 19 мая) |
| Граница витрина/внутренняя часть | Monorepo / Два фронтенда + SSR-сайт / Hybrid | — |
| Post-MVP roadmap phasing | Что в Q3-Q4, что в Q1-2027+, критерии готовности | — |

### Двухфазная архитектура платформы

```
Сейчас (MVP):       LMS + базовые сервисы + ступени S1-S5 + агенты через бот/VS Code
Q3-Q4 2026:         Marketplace микроприложений + Multi-surface (PWA) + внешние интеграции
Q1 2027+ (Prod):    Parliament Model на полную мощность + GKE + Cloud SQL + SLA
```

</details>

---

<details>
<summary><b>10. Открытые вопросы для ArchGate</b></summary>

1. **Event versioning:** если формат event изменится — как backward-compatible?
2. **Projection worker latency:** batch every 5 min — ок ли для stage-change detection?
3. **Агентная память при работе с двух машин:** синхронизация паттернов между устройствами?
4. **Service scopes:** кто может менять scope агента — только пилот или и пользователь?
5. **Coordinator state:** stateless координатор — нужно ли кэшировать разрешения?
6. **WP-285 gap:** `subscription.contract_event` пустая 6 недель при 541 active subscriptions — нужна диагностика projection-worker (WP-228 Ф32) до миграции в Track B

</details>
