# WP-336: Архитектура платформы Aisystant IWE
## Документ для архитектора Андрея

---

Платформа Aisystant строится вокруг одной идеи: специалист должен расти в системном мышлении не через абстрактные курсы, а через реальную работу — с ИИ-помощником рядом. Hermes помнит паттерны его ошибок, предлагает методы в нужный момент, автоматизирует рутину. Параллельно платформа ведёт человека по ступеням мастерства — от «случайного» применения методов до осознанного исполнения ролей и собственного вклада в развитие инструментов. Это не LMS с курсами, это среда профессионального роста.

Архитектурно платформа реализует **Bukvar-модель**: адаптация происходит к росту конкретного пользователя, а не к масштабу по числу пользователей. Для каждой ступени меняются три вещи — интерфейс (упрощается или расширяется), содержание (от рецептов к философии методов) и доступные сервисы (от базовых до пользовательских микроприложений). Безопасность данных гарантирована архитектурно через **Parliament Model**: ни один агент не имеет доступа ко всем данным сразу — только к своей зоне ответственности через явный контракт (Service Clause), с независимым верификатором.

---

<details open>
<summary><b>1. Parliament Model: Триада Учёт / Доступ / Аудит</b></summary>

### Проблема, которую решает
Один агент с полным доступом ко всем данным пользователя = **Президент-модель** = уязвимость при скомпрометировании агента или промпта.

### Решение: Parliament Model
Разделение ответственности на **три независимые роли**:

```
User Request
    ↓
Coordinator (stateless, N domain agents, не хранит сырые данные)
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
<summary><b>2. Hermes Agent: Память и самокоррекция</b></summary>

### Архитектура памяти
Hermes хранит **паттерны** работы пользователя, не переписку и не личные данные.

#### Две базы

**Neon (долгоживущая, синхронизация между сессиями):**
```sql
hermes_fault_patterns (
  user_id uuid,
  pattern_name text,
  trigger_condition text,
  correction_method text,
  success_rate float,
  last_applied_at timestamp
)

hermes_checklist_library (
  user_id uuid,
  domain text,
  checklist_name text,
  steps jsonb,
  is_custom boolean,
  created_by text  -- 'platform' или 'user'
)

hermes_method_adoption (
  user_id uuid,
  method_id text,
  stage_introduced int,
  times_suggested int,
  times_applied int,
  last_successful_at timestamp
)
```

**SQLite локальный (быстрая память в рабочей директории):**
```
iwe_memory.db
├─ fault_signatures (что сломалось в прошлых сессиях)
├─ manual_checklist_overrides (пользователь отредактировал чек-лист)
├─ method_shortcuts (сокращения методов, которые пользователь выбрал)
└─ session_context_cache (что делал в прошлой сессии, для быстрого восстановления)
```

#### Алгоритм Hermes.suggest()

1. Получить текущий task от пользователя
2. Найти в `fault_patterns` похожие сценарии (по trigger_condition)
3. Если найдено: показать чек-лист из `hermes_checklist_library` или пошаговую инструкцию
4. Если пользователь применил метод успешно: обновить `success_rate` и `last_applied_at`
5. Если пользователь нашёл лучший способ: он может обновить чек-лист → синхронизируется в Neon

#### Самопоправка (Self-Correction Loop)

```
User completes action
  ↓
Hermes: "Отлично, но есть лучше"
(показывает pattern из fault_patterns)
  ↓
User applies suggested method
  ↓
Hermes.success_rate += 1
  ↓
Next time similar condition: suggest that method first
```

</details>

---

<details>
<summary><b>3. Data Layers: Трёхслойное разделение данных</b></summary>

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
```

**Гарантия:** immutable audit trail (APPEND ONLY), удаление только по GDPR-запросу через Verifier

### Слой 3: Контекст (Runtime, LLM-сессия) — ~5%

```python
context = {
    "user_id": "...",
    "current_stage": 3,
    "bottleneck": "cp_iwe",
    "relevant_methods": [...],
    "fault_patterns": [...],
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
  ├─ query_to_hermes (query_text, domain)
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
<summary><b>5. Service Architecture: Domain-Isolated Services</b></summary>

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
<summary><b>6. Session Flow: Интеграция всех слоёв</b></summary>

```
1. Пользователь открывает IWE (VS Code / браузер / бот)

2. Сборка Context:
   - Persona из Git (~50KB)
   - learner_cp_profile из Neon (~1KB)
   - active_services list (~100B)
   - recent fault_patterns из SQLite (~10KB)
   → Итого context: ~60KB

3. Hermes инициализируется:
   - Memory из iwe_memory.db (local)
   - Sync с Neon baseline (consistency check)

4. Пользователь запрашивает помощь
   - Hermes ищет в fault_patterns
   - Предлагает checklist из hermes_checklist_library
   - Если нет → generic method для ступени

5. Пользователь завершает задачу, коммитит артефакт
   - Artifact → Git (Persona layer)
   - Event artifact_committed → Neon (Memory layer)
   - Coordinator логирует доступ (Audit)

6. Day Close
   - Генерируется day_close event
   - Обновляются cp_* indicators
   - Предлагается что практиковать завтра

7. Конец сессии
   - SQLite → Neon sync
   - Context очищается (ephemeral)
   - session_end event записывается
```

**Data Flow:**
```
activity_log
  ↓ projection_worker (каждые 5 мин)
indicators (cp_*, bh_*)
  ↓ context_assembler (перед каждым LLM-вызовом)
Context (ephemeral prompt)
  ↓ Hermes + Services
New events → activity_log (цикл)
```

</details>

---

<details>
<summary><b>7. Deployment & Scaling</b></summary>

### Фаза 1 MVP — Single-region, single Neon DB
```
LMS + IWE (web / bot / VS Code)
    ↓
Neon (EU region):
  ├─ learning DB  (activity_log, indicators, lessons)
  ├─ personas DB  (Git refs)
  └─ audit DB     (access_log, Parliament Model)
    ↓
SQLite (local per user workspace):
  └─ iwe_memory.db
```

### Фаза 2 — Per-domain scaling
```
- learning domain → отдельный Postgres (read-heavy)
- audit domain → ClickHouse (time-series analytics)
- community domain → отдельная БД (post-index)

Parliament Model делает это легко:
каждый domain agent говорит только со своей БД.
```

### Cost estimate

| Ресурс | Объём / 1000 пользователей | Стоимость/мес |
|--------|---------------------------|---------------|
| Neon activity_log | ~50GB stored | $50-100 |
| Compute | ~2-3 vCPU | $200-300 |
| SQLite local | ~1MB/user | — |
| Hermes patterns | ~100KB/100 паттернов | — |

</details>

---

<details>
<summary><b>8. Security & Compliance (Parliament Model guarantee)</b></summary>

### GDPR Rights

**Right to access:**
- Пользователь видит свою Persona (Git export)
- Пользователь видит свои events в activity_log (Neon export)
- cp_* — аудитируемые агрегаты, не сырые трейсы

**Right to delete:**
- Удалить все activity_log events (с записью в audit log)
- Удалить все Persona Git данные
- Пересчитать все indicators (ступень может измениться)

**Right to object:**
- Opt-out из Hermes memory (отключить fault pattern tracking)
- Opt-out из конкретного domain agent
- Verifier проверяет эти preferences перед каждым доступом

### Audit Trail

```sql
access_audit:
  ├─ timestamp        (when)
  ├─ agent_id         (who)
  ├─ request          (what)
  ├─ scope_applied    (was access in scope?)
  ├─ verifier_approved (yes/no)
  └─ result           (data returned / denied)
```

Monthly report: «Agent X accessed User Y data Z times, all within scope»

</details>

---

<details>
<summary><b>9. Open Questions for ArchGate</b></summary>

1. **Event versioning:** если формат event изменится (добавим поле) — как backward-compatible? (versioning в SQL, migration script)
2. **Projection worker latency:** batch every 5 min — ок ли для stage-change detection? (можно trigger-based if needed)
3. **Hermes storage при работе с двух машин:** синхронизация iwe_memory.db? (push to Neon в конце сессии)
4. **Service scopes:** кто может менять scope? (изначально только пилот, затем расширить до пользователя)
5. **Coordinator state:** статeless координатор — нужно ли кэшировать разрешения? (Redis / один вызов)

</details>
