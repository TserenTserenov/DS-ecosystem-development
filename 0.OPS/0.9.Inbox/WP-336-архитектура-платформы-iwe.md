---
type: architecture-context
status: active
source_wp: WP-336 (закрыт), контент актуален для WP-337 + WP-281
updated: 2026-06-09
---

# WP-336: Архитектура Платформы Aisystant и IWE — контекст для архитектора
## Документ для Андрея

> **Связанные документы:**
> - [Обещание пользователю и сценарии использования](WP-336-обещание-и-сценарии.md)
> - [Инвентарь сервисов Track A → Track B](WP-285-services-inventory.md) — текущая инфраструктура (16 CF Workers + Python, 16 БД), план миграции на GKE
> - [Различение: Платформа Aisystant ≠ IWE](../0.99.Archive/WP-73-iwe-platform-distinction.md) — граница двух систем, правило размещения артефактов, матрица доступа
> - [Доступ агентов к личной памяти пилота — архитектура Парламент](WP-337-память-агентов-proposal.md) — 5 элементов Парламента (Координатор, N доменных агентов, Замок, Верификатор, Окошко команд), порядок пилотного запуска; обсуждался на встрече 21 (май 2026), итог — см. WP-337

---

> **Системы в этом документе:**
>
> | Система | Что это | Где живёт | Кто разрабатывает |
> |---|---|---|---|
> | **Платформа Aisystant (Track B — Мир)** | Облачный бэкенд: Identity, сервисы, данные прогресса, Knowledge Index, Gateway, марафон | GKE Standard europe-west4 / Cloud SQL / Stripe | Андрей |
> | **Платформа МИМ (Track A — Россия)** | Облачный бэкенд: Identity, сервисы, данные прогресса, Knowledge Index, Gateway, марафон | VK Cloud K8s / Neon / YooKassa | Ильшат |
> | **IWE** | Система организации интеллектуальной работы | Применяется пользователем в его рабочей среде (Git-репо, VS Code, файловая система) | Тсерен (FMT-exocortex-template) |
>
> _Текущий MVP работает на Railway / Neon / CF Workers — переходное состояние до завершения миграции на Track B (GKE) и Track A (VK Cloud)._
>
> В этом документе описывается **Платформа** (§1–9). Рабочая среда пользователя = §3 Слой 1 (Данные пользователя, Git) + хост VS Code (Anthropic). IWE — система организации работы, применяемая в этой среде. Граница: MCP Gateway `mcp.aisystant.com`.

---

<details open>
<summary><b>1. Что строим и зачем</b></summary>

Продукт — среда профессионального роста: специалист работает быстрее и системнее, развивает системное мышление и применяет его к собственному рабочему окружению. **Платформа** ведёт человека по траектории Созидателя: от Ученика (Ступени 1–5: Случайный → Проактивный) через Интеллектуала и Профессионала к Исследователю и Просветителю — меняет интерфейс, содержание и набор сервисов по мере роста. Это **Букварь-модель (Из Алмазного века)**: адаптация к конкретному человеку, не к масштабу пользователей.

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

> **Владельцы слоёв:**
> | Слой | Владелец | Где живёт | Что inside |
> |------|----------|-----------|------------|
> | Слой 1 — Данные пользователя | Пользователь (IWE) | Git-репо пользователя | methods, captures, goals, preferences — явные фиксации пользователя |
> | Слой 2 — Данные платформы | Платформа Aisystant | Neon (облако) | events, вычисленные indicators (cp_*, bh_*), audit trail |
> | Слой 3 — Оперативный контекст | Ephemeral (runtime) | Промпт LLM | Собранный на лету срез из Слоёв 1–2 + Pack/DS |

### Слой 1: Данные пользователя (Git, данные рабочей среды, Платформа не владеет) — ~10%

```
~/.iwe/
├─ methods.md              # Какие методы применяю (мой выбор)
├─ captures/               # Явные знания, которые я зафиксировал
├─ preferences.json        # Настройки интерфейса, выбранные сервисы
└─ goals.md                # Какие цели преследую в этом периоде
```

**Читается:** из Git-репо, один раз за сессию  
**Пишется:** пользователем вручную, через UI captures, или через MCP write tool из AI-клиента  
**Гарантия:** пользователь контролирует — export/backup/удалить

> **Различение:** Показатели характеристик (cp_*, bh_*) — это не «Персона». Они вычисляются платформой из событий и хранятся в Слое 2 (Neon). Слой 1 — только явные фиксации пользователя.

> **Personal Knowledge MCP — индексация личных репо.** Данные участника лежат в его GitHub-репо (он контролирует), платформа хранит только эмбеддинги. Запись из AI-клиента через MCP write tool → GitHub App «Aisystant Knowledge» коммитит в репо → push → webhook → автоматическая переиндексация изменённых файлов. Никаких ручных шагов: запись и индексация — один атомарный шаг для пользователя. Реализовано в WP-187 (Gateway v2.0.0, апр 2026). Подробно → [WP-74 §SC-17 «IWE как сервис»](../0.99.Archive/WP-74-platform-concept-of-use.md).

### Слой 2: Данные платформы (Neon, платформа владеет) — ~85%

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

**Гарантия:** immutable audit trail (APPEND ONLY), удаление только по GDPR-запросу через Verifier.  
> **Аналогия:** Как штамп Почты России на налоговой декларации — фиксируется факт отправки, который нельзя подделать или стереть. Event sourcing = неподкупная запись: каждое событие timestamped, signed, append-only.

### Слой 3: Оперативный контекст (Runtime, LLM-сессия) — ~5%

**Откуда собирается:** Контекст — это не «пустая оперативная память LLM». Он ассемблируется перед каждым вызовом модели из трёх источников:
1. **Pack / DS** — база знаний платформы (роли, методы, этапы, онтология)
2. **Слой 2** — данные платформы: indicators, recent events, bottleneck
3. **Слой 1** — данные пользователя: goals, methods, recent artifacts из Git

```python
context = {
    "user_id": "...",
    "current_stage": 3,
    "bottleneck": "cp_iwe",
    "relevant_methods": [...],      # ← из Pack + Слоя 1
    "recent_artifacts": [...],      # ← из Слоя 1 (Git)
    "task_description": "...",
    "available_services": ["calendar", "git", "notes", ...],
    "session_history": [...],
    "pack_knowledge": [...],        # ← релевантные фрагменты онтологии/ролей
}
```

**Гарантия:** Ephemeral — не сохраняется между сессиями. При новой сессии собирается заново из актуальных Слоёв 1–2 и Pack.

### Согласованность между слоями

```
User action
    ↓
Event → activity_log (Слой 2)
    ↓
Projection worker → обновляет indicators (Слой 2)
    ↓
Данные пользователя обновляются по желанию (Слой 1)
    ↓
В следующей сессии контекст собирается из обновлённых Слоёв 1–2 + Pack (Слой 3)
```

**Важно:** Stage считается из indicators (Neon, Слой 2), не из явных фиксаций пользователя (Слой 1). Слой 1 подтверждает убеждения пользователя, но не является главным критерием ступени.

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

domain: 'support'
  ├─ ticket_created (ticket_id, category: 'bug'|'question'|'feature'|'points'|'guide', channel: 'telegram'|'web')
  ├─ ticket_assigned (ticket_id, assignee_id, auto: boolean)
  ├─ ticket_resolved (ticket_id, resolution_time_min, resolved_by: 'human'|'faq_bot')
  └─ ticket_escalated (ticket_id, reason, escalation_level: 1|2|3)
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
└─ Coordinator routes to correct agent
   ├─ Parliament Model ensures isolation
   └─ Verifier logs all access
```

> **Важно:** Рабочая среда пользователя — **не платформенный сервис** и отсутствует в Parliament Model. VS Code + Claude Code + скиллы работают автономно на стороне пользователя и подключаются к Платформе только через MCP Gateway как внешний клиент. Parliament Model изолирует домены **внутри Платформы** — рабочая среда находится за её границей. IWE — система, которую пользователь применяет в этой среде.

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

Агенты — прикладной слой поверх Data Layers, Event Sourcing, Parliament Model и сервисов. **Все перечисленные ниже агенты — платформенные** (работают на Платформе, управляются Aisystant). Клиентская сторона = Claude Code + его скиллы (CLAUDE.md, memory/, .claude/) — они работают на стороне пользователя в VS Code и в Parliament Model не входят.

Каждый платформенный агент:
- Имеет **Service Clause** с явным обещанием, входами, выходами и режимом отказа
- Работает только через Coordinator — не имеет прямого доступа к чужому домену
- Proверяется Verifier при каждом запросе данных

### Роли агентов (DP.ROLE.NNN)

> **Различение:** Ниже перечислены **роли**, а не отдельные специализированные агенты. Универсальный агент при наличии соответствующего Service Clause может выполнять любую из этих ролей. Реальные имена агентов в системе — произвольные (например, `agent-7a3f`), роль определяется назначенным Service Clause.

```
Диагност          — определяет ступень Ученика и bottleneck через диалог
Портной           — строит персональное руководство под ступень + домен пользователя
Агент памяти      — хранит паттерны работы, предлагает методы и чек-листы
Артефактор        — помогает создавать, организовывать и восстанавливать контекст артефактов
Агент сообществ   — рекомендует релевантные посты и практики из сообщества
Агент поддержки   — принимает /support-запросы, автоматически отвечает по FAQ, маршрутизирует тикеты
                    (реализация: Chatwoot + Telegram inbox; домен = 'support'; read-scope = tier/stage для контекста)
Верификатор       — read-only, проверяет соответствие доступа Service Clause'ам
Координатор       — маршрутизирует запросы между агентами, stateless
```

### Горизонт расширения

На ступенях 3-5 пользователь может регистрировать собственные агенты:
- Регистрация с явным Scope (какие события и домены доступны)
- Verifier проверяет scope перед каждым запросом
- Пользователь может отключить агент в любой момент

**Полный каталог агентов (DP.ROLE.NNN) и их Service Clause'ы** — отдельная инициатива (аналог WP-337 для агентной платформы).

### Доступ агентов к личной памяти: Parliament-модель

Описанные выше агенты работают с личными данными пилота через **Parliament-архитектуру** (согласована встреча 18 мая). Принцип: отказ доступа на уровне платформы (токены / ACL), не на уровне промпта.

**5 элементов (подробно: [WP-337-память-агентов-proposal.md](WP-337-память-агентов-proposal.md)):**

| Элемент | Роль | Аналогия |
|---------|------|---------|
| Координатор | Знает имена доменных агентов, не данные → маршрутизирует | Телефонный коммутатор |
| N доменных агентов | HealthAgent / FinanceAgent / LearningAgent — каждый видит только свой домен | Специалисты в разных кабинетах с несовместимыми картами доступа |
| Платформенный замок | OAuth scope per domain agent — работает независимо от промптов | Карточка доступа в здании: нет карточки → дверь не открывается |
| Верификатор | Read-only аудит журнала запросов, не данных → сигнализирует аномалии | Камера видеонаблюдения |
| Окошко команд | Безопасные / Изменения (предпросмотр) / Необратимые (таймер 15 сек) — через доменного агента | — |

**Связь с Local Gateway (DP.IWE.005):** Координатор и Local Gateway — разные компоненты на разных сторонах границы. Local Gateway = IWE-сторона (координирует агентов VS Code через file-lock). Координатор = Платформа (маршрутизирует запросы к доменной памяти). Оба действуют по принципу «знаю имена, не знаю содержимое».

> Статус: предложение к согласованию на встрече 21. Источник: пункты 3–6 оперативки ИТ 24 мая.
>
> **Граница IWE (уточнено 26 мая, peer-сессия WP-337/И vs WP-336):** IWE реализует **Local Coordination Hub** — автономный слой координации агентов в рамках одного пилота (VS Code, peer-discovery, file-lock), не входящий в Parliament Model. Local Coordination Hub синхронизируется с Платформенным Координатором через **Platform Adapter** (DP.IWE.011) при наличии сети. При отсутствии сети IWE работает автономно с локальными Pack. См. `sessions/2026-05/2026-05-26-16-wp337-parliament-boundary/report.md`.

</details>

---

<details>
<summary><b>8. Session Flow: Всё вместе</b></summary>

```
1. Пользователь открывает интерфейс:
   - **Рабочая среда пользователя** → VS Code + Claude Code (локальная среда)
   - **Платформа** → браузер / Telegram-бот (облачные интерфейсы)

2. Сборка Context (Слой 3):
   - Данные пользователя из Git (~50KB) ← Слой 1
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

4a. Ошибка или инцидент обнаружен (автоматически)
   - n8n-workflow (health probe / alerter) детектирует outage
   - n8n создаёт тикет в Chatwoot (Telegram-канал поддержки)
   - ticket_created event → activity_log domain='support'
   - Агент поддержки добавляет контекст ступени пользователя к тикету

5. Пользователь завершает задачу, коммитит артефакт
   - Artifact → Git (Слой 1 — Данные пользователя)
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
Context (Слой 3, ephemeral prompt: Слой 1 + Слой 2 + Pack/DS)
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
| IDE для работы в курсе | Cloud IDE / Embed Claude Code в браузер ⚠️ ArchGate (Claude Code — хост Anthropic, не Aisystant) / Custom через Agent SDK | — |
| LMS-формат | UX-обёртка над текстом / Рабочая тетрадь (применяется через IWE пользователя) / Гибрид | — |
| Мобильное расширение | Бот как основной интерфейс / **PWA с адаптивным дизайном** / Native iOS+Android | ✅ PWA (оперативка 19 мая) |
| Граница витрина/внутренняя часть | Monorepo / Два фронтенда + SSR-сайт / Hybrid | — |
| Post-MVP roadmap phasing | Что в Q3-Q4, что в Q1-2027+, критерии готовности | — |

### Двухфазная архитектура платформы

```
Сейчас (MVP):       LMS + базовые сервисы + ступени S1-S5 + агенты через бот/VS Code
                    Helpdesk: Chatwoot self-hosted на Railway + Neon (chatwoot DB) + Telegram inbox
Q3-Q4 2026:         Marketplace микроприложений + Multi-surface (PWA) + внешние интеграции
                    Helpdesk: Linear/GitHub Issues интеграция + автотикеты из алертов (WP-314)
Q1 2027+ (Prod):    Parliament Model на полную мощность + GKE + Cloud SQL + SLA
                    Helpdesk Track B: Chatwoot на GKE (решение: shared с Track A или отдельный инстанс → ArchGate)
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
7. **Helpdesk Track B placement:** Chatwoot shared один инстанс для Track A + Track B (проще, но смешивает данные разных юрисдикций) или отдельный инстанс на GKE (изоляция EU-данных, GDPR-чистота, но +операционная сложность)? Ответ влияет на схему Neon БД и Parliament Model scope для Агента поддержки.
8. **Helpdesk в Parliament Model:** Агент поддержки читает tier/stage пользователя для контекста тикета — минимальный read-scope через Coordinator. Нужен ли отдельный Verifier-check или достаточно существующего?
9. **Support events в activity_log:** `ticket_created` — писать ли в activity_log (learning DB) или отдельная таблица (support DB)? Цель: аналитика по типам обращений + выявление ступеней с наибольшим числом вопросов.

</details>
