# WP-336: Архитектура платформы Aisystant IWE
## Документ для архитектора Андрея

---

## 1. Parliament Model: Триада Учёт / Доступ / Аудит

### Проблема, которую решает
Один агент с полным доступом ко всем данным пользователя = **Президент-модель** = уязвимость при скомпрометировании агента или промпта.

### Решение: Parliament Model
Разделение ответственности на **три независимые роли**:

```
User Request
    ↓
Coordinator (stateless, N domain agents, doesn't store raw data)
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

---

## 2. Hermes Agent: Runtime Memory + Autocorrection

### Архитектура памяти
Hermes хранит **паттерны** работы пользователя, не переписку или личные данные.

#### Две базы (в другой директории)

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
5. Если пользователь нашёл лучший способ: пользователь может обновить чек-лист → синхронизировать в Neon

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

---

## 3. Data Layers: Трёхслойное разделение

### Слой 1: Персона (Git, пользователь владеет) — ~10%

**Местоположение:** `~/.iwe/persona/`

```
~/.iwe/persona/
├─ methods.md              # Какие методы применяю (мой выбор)
├─ captures/               # Явные знания, которые я зафиксировал
│  ├─ decision-2026-05-19.md
│  ├─ insight-project-x.md
│  └─ lesson-learned.md
├─ preferences.json        # Настройки интерфейса, выбранные сервисы
└─ goals.md               # Какие цели преследую в этом периоде
```

**Читается из:** Git репо (один раз за сессию)
**Пишется:** пользователем вручную или через UI captures
**Гарантия:** пользователь контролирует, может export/backup/удалить

### Слой 2: Память (Neon, платформа владеет) — ~85%

**Категории:**

#### Observed Events (первичные):
```sql
activity_log (
  user_id uuid,
  event_type text,  -- task_completed, lesson_started, day_close, iwe_session, etc.
  domain text,       -- 'learning', 'work', 'community', 'self-development'
  metadata jsonb,
  created_at timestamp
)
```

#### Derived Indicators (вычисленные):
```sql
learner_cp_profile (
  user_id uuid,
  stage int,  -- 1-5
  cp_rhy float,  -- consistency/rhythm
  cp_wld float,  -- world view (системное мышление)
  cp_skl float,  -- skills (мастерство методов)
  cp_iwe float,  -- tool mastery
  cp_int float,  -- integration (применение к себе)
  cp_agt float,  -- agency (инициатива)
  calculated_at timestamp
)

behavior_indicators (
  user_id uuid,
  bh_sys float,  -- systematicity
  bh_inv float,  -- investment (сколько времени на развитие)
  bh_awr float,  -- awareness (осознанность)
  bh_per float,  -- persistence
  calculated_at timestamp
)

learning_baseline (
  user_id uuid,
  stage int,
  expected_session_duration_min int,
  expected_weekly_slots float,
  target_method_diversity int,
  calculated_at timestamp
)
```

**Читается:** Indicators читаются для рекомендаций, Events не читаются по одному (слишком много), используются через агрегаты
**Пишется:** Platform agents (projections worker) из activity_log
**Гарантия:** immutable audit trail (APPEND ONLY), удаление только по GDPR-запросу через Verifier

### Слой 3: Контекст (Runtime, LLM-сессия) — ~5%

**Собирается per-LLM-call:**

```python
# Context для Hermes агента в одной сессии

context = {
    "user_id": "...",
    "current_stage": 3,  # из learner_cp_profile
    "bottleneck": "cp_iwe",  # слабое звено
    "relevant_methods": [...],  # методы для ступени 3
    "fault_patterns": [...],  # какие ошибки были раньше
    "recent_artifacts": [...],  # последние выходные документы из Git
    "task_description": "...",  # что просит пользователь
    "available_services": ["calendar", "git", "notes", ...],
    "session_history": [...],  # что уже делали в этой сессии
}
```

**Читается:** Ассемблируется для текущего промпта LLM
**Пишется:** Никогда не сохраняется, только в логи сессии
**Гарантия:** Ephemeral, удаляется в конце сессии (за исключением activity_log event-а)

### Согласованность между слоями

```
User action (e.g., completes a learning task)
    ↓
Event написан в activity_log (Слой 2)
    ↓
Projection worker обрабатывает event → обновляет indicators (Слой 2)
    ↓
Persona может быть обновлена (Слой 1) если пользователь захочет зафиксировать инсайт
    ↓
В следующей сессии контекст собирается из обновлённых indicators (Слой 3)
```

**Важно:** Persona не является источником истины для stage/indicators.  
Stage считается **из indicators** (Neon), не из persona.  
Persona подтверждает/переопределяет отдельные убеждения пользователя, но не главный критерий.

---

## 4. Event Sourcing: От действия к знанию

### Event Catalog (in application code)

```
domain: 'learning'
  ├─ lesson_started (lesson_id, stage_expected)
  ├─ lesson_completed (lesson_id, score, time_spent_min)
  ├─ lesson_skipped (lesson_id, reason)
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

### Projection Rules (как events → indicators)

**Example: cp_iwe (инструментальное мастерство)**

```
Rule: "Мастерство IWE = применение методов в реальных сессиях"

Events that increase cp_iwe:
  - iwe_session_end (artifact_count > 0) → +0.1
  - artifact_committed (tool_used == 'vscode') → +0.15
  - method_practiced (method_id in ['git', 'refactoring', ...]) → +0.2

Events that stagnate cp_iwe:
  - slot_logged BUT iwe_session_count == 0 that week → no increase
  - day_close WITH reflection="没有用到IWE" → no increase

Calculation (weekly):
  cp_iwe_new = min(5, cp_iwe_old + sum(events_weight))
```

### Drift Detection

**Detector 1: Event staleness**
```
If no events in 7 days but user is marked 'active':
  → send alert to Verifier
  → might need manual review
```

**Detector 2: Indicator regression**
```
If cp.* decreases by >0.5 in one week:
  → check if events are legitimate (or data corruption)
  → update bottleneck in context for next session
```

---

## 5. Service Architecture: Domain-Isolated Services

### Service Clause Pattern (DP.SC.NNN)

Каждый сервис (календарь, заметки, гит, чат) имеет контракт:

```
DP.SC.135: Day Close Ritual

Promise: "Помочь пользователю закрыть день, зафиксировав достигнутое"

Input:
  - reflection_text: что сделал, что узнал
  - artifacts: список файлов, которые создал
  - day_quality_self_assessment: 1-5

Output:
  - day_closed: boolean
  - events_generated: [event1, event2, ...]
  - suggestions_for_tomorrow: [suggestion1, ...]

SLA:
  - response_time: <1s
  - availability: 99.9%

Failure mode:
  - If reflection is empty: prompt user, retry
  - If artifacts can't be read: log to error_queue, alert human
```

### Domain Isolation

```
┌─ Service: Schedule
│  ├─ Can read: calendar events, user preferences
│  ├─ Can't read: learning metrics, private notes
│  └─ Coordinator: "schedule" domain agent
│
├─ Service: Learning
│  ├─ Can read: lesson metadata, user stage
│  ├─ Can't read: work calendar, email
│  └─ Coordinator: "learning" domain agent
│
├─ Service: IWE (IDE)
│  ├─ Can read: user's own Git repo, Persona
│  ├─ Can't read: other users' data
│  └─ Coordinator: "workspace" domain agent
│
└─ Coordinator routes to correct agent
   ├─ Parliament Model ensures isolation
   └─ Verifier logs all access
```

### Service Composition (Ф2+)

**Plug-and-play model:**
- Пользователь может подключить свой сервис (microapp)
- Microapp регистрируется в Coordinator с Scope (какие события может читать)
- Verifier проверяет scope перед каждым доступом
- Пользователь может отключить, если не нравится

**Example: Third-party "Daily Goal Tracker"**
```
Service registration:
  name: "goal-tracker"
  scope: ["day_close", "iwe_session_end"]
  owner: "user" (vs "platform")
  manifest: "https://github.com/user/goal-tracker/manifest.json"

Access:
  ✓ goal-tracker CAN read day_close events
  ✗ goal-tracker CAN'T read learning_completed events (not in scope)
  
User can:
  - Disable service (stop sending events)
  - Change scope (with re-approval)
  - Delete service data (GDPR request)
```

---

## 6. Интеграция с Persona/Memory/Context

### Session Flow (на примере рабочей сессии)

```
1. User opens IWE (VS Code / browser / bot)
   
2. Assemble Context:
   - Load Persona from Git (~50KB)
   - Load learner_cp_profile from Neon (~1KB)
   - Load active_services list (~100B)
   - Load recent fault_patterns from SQLite (~10KB)
   → Total context: ~60KB
   
3. Hermes initialized:
   - Memory loaded from iwe_memory.db (local)
   - Synced with Neon baseline (for consistency check)
   
4. User asks Hermes for help with a task
   - Hermes checks fault_patterns (do I know this problem?)
   - Suggests checklist from hermes_checklist_library
   - If yes: show checklist, propose method
   - If no: use generic method for stage
   
5. User completes task, commits artifact
   - Artifact stored in Git (Persona layer)
   - Event created: artifact_committed (Memory layer)
   - Coordinator logs: which services accessed? (Audit)
   
6. Day close ritual
   - Generate day_close event
   - Update cp_* indicators based on all day's events
   - Suggest what to practice tomorrow
   
7. Session ends
   - Sync SQLite changes back to Neon
   - Clear context (ephemeral)
   - Log session_end event
```

### Data Flow in Dependencies

```
Events (activity_log)
  ↓ projection_worker (batch every 5 min)
Indicators (learner_cp_profile, behavior_indicators)
  ↓ context_assembler (before each LLM call)
Context (ephemeral in prompt)
  ↓ Hermes decision-making
  ↓ Service calls
Events generated (artifact_committed, etc.)
  ↓ (back to activity_log)
```

---

## 7. Deployment & Scaling Considerations

### Faza 1 (MVP): Single-region, single Neon DB
```
┌─ LMS + IWE (web/bot/VS Code)
│
├─ Neon (single region: EU)
│  ├─ learning DB (activity_log, indicators, lessons)
│  ├─ personas DB (Git refs if needed, won't store full content)
│  └─ audit DB (access_log for Parliament Model)
│
└─ SQLite (local in each user's workspace)
   └─ iwe_memory.db (fault patterns, checklists, cache)
```

### Faza 2: Multi-region (if needed), per-domain scaling
```
Can split:
- learning domain to separate Postgres instance (read-heavy)
- audit domain to time-series DB (ClickHouse) for analytics
- community domain to separate DB (post-index optimized)

Parliament Model makes this easy: each domain agent talks to its own DB.
```

### Costs estimate

**Per-user-month:**
- Neon activity_log: ~50KB/month (at 20 events/day)
- Indicators recalculation: <0.1s CPU per day
- SQLite local: ~1MB per user (evergreen, not growing much)
- Hermes pattern storage: ~100KB per 100 error patterns

**Example: 1,000 users**
- Neon: ~50GB stored, ~2-3 vCPU needed
- Storage cost: $50-100/month
- Compute cost: $200-300/month

---

## 8. Security & Compliance (Parliament Model guarantee)

### GDPR Rights

**Right to access:**
- User sees their own Persona (Git export)
- User sees their events in activity_log (Neon export)
- User doesn't see raw calculations (cp_* are audited, not raw traces)

**Right to delete:**
- Delete all activity_log events (after audit log entry: "deleted at YYYY-MM-DD")
- Delete all Persona Git data
- Recalculate all indicators (may change stage)

**Right to object (to processing):**
- User can opt-out of Hermes memory (disable fault pattern tracking)
- User can opt-out of specific domain agent (e.g., no schedule analysis)
- Verifier checks these preferences before each access

### Audit Trail

```sql
access_audit table:
  ┌─ timestamp (when)
  ├─ agent_id (who)
  ├─ request (what)
  ├─ scope_applied (was access in scope?)
  ├─ verifier_approved (yes/no)
  └─ result (data returned / denied)

Monthly report: "Agent X accessed User Y data Z times, all within scope"
```

---

## 9. Open Questions for ArchGate

1. **Event versioning:** если формат event изменится (e.g., добавим поле), как backward-compatible? (versioning в SQL, migration script)
2. **Projection worker latency:** сейчас batch every 5 min, ок ли для stage-change detection? (можно trigger-based if needed)
3. **Hermes storage in Neon vs local:** если пользователь работает с двух машин, синхронизация? (push iwe_memory.db to Neon в конце сессии)
4. **Service scopes:** кто может менять scope? (изначально только пилот, позже расширить до пользователя)
5. **Coordinator state:** координатор stateless, но нужно кэшировать разрешения (Redis? или переделать запрос в одном вызове?)
