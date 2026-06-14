---
id: ADR-IWE-020
title: Semantic agent-write nudge для Schema Registration Gate (AR.234)
status: accepted-design   # решение принято; реализация — отдельный спин-офф РП (S-33 на правку хуков)
date: 2026-06-14
deciders: [пилот (Цэрэн), claude-code (писатель), kimi (напарник)]
parent_wp: WP-419
source_session: DS-my-strategy/sessions/2026-06/2026-06-14-50-adr-schema-write-nudge/report.md
related:
  - AR.234 (Schema Registration Gate) — PACK-agent-rules/rules/AR.234-schema-registration-gate.md
  - AR.009 (Routing Gate) — спящее правило, развязка
  - DP.METHOD.054 §5 §9 (метод кодирования/классификации)
supersedes: []
schema_version: 1
---

# ADR-IWE-020: Semantic agent-write nudge для Schema Registration Gate (AR.234)

> **Статус:** принято как дизайн (`accepted-design`). Решение зафиксировано; врезка в хуки — отдельный спин-офф РП под явное разрешение пилота (S-33, правка `.claude/hooks/`). Этот ADR — контракт реализации, не сама реализация.

## Контекст

WP-419 («Описание метода кодирования») закрыл метод (DP.METHOD.054), правило-доставку (AR.234) и **structural**-замок принуждения (новый реестр → запись в каталоге) как E2 в CI DS-ecosystem. Остался отложенным **semantic**-слой AR.234: подсказка агенту о **дизайне осей** (владелец namespace? ось ортогональна? bounded_context?) в момент создания новой кодовой схемы. Этого CI не ловит — он проверяет наличие записи в каталоге, не корректность дизайна. Именно недизайн осей и отсутствие владельца породили коллизии COL-01…08.

### Разведка кода (факты на 2026-06-14)

- `rule-engine.sh::dispatch_event` грузит active-правила по `RULE_EVENT` и гоняет `check_<fn>` по priority. События возбуждают обёртки-хуки из `settings.json` (matcher только по имени инструмента, не по пути).
- **AR.009 (Routing Gate):** `status: active`, `check_routing_gate` реализована (`rule-engine.sh:589`), триггер `artifact_creation_attempt`. Но **ни одна обёртка в `settings.json` его не firing'ит** → правило спит. FP задекларирован 30-40%, срабатывает на КАЖДЫЙ новый файл.
- **AR.234:** `check_schema_registration_gate` в диспетчере **не вшита** (только PSEUDOCODE в .md). Релевантна редко (новая схема — штучное событие).
- AR.009 и AR.234 завязаны на один событийный слой → наивное оживление события будит оба.

## Решаемая проблема

Оживить semantic-nudge так, чтобы (а) он реально срабатывал в design-time, (б) **не разбудил шумный AR.009**, (в) честно назвал свой уровень принуждения, (г) сам не умер молча, как умер AR.009.

## Решение (консенсус peer-сессии 2026-06-14-50, ходы 0-5)

1. **Оживить semantic-слой AR.234 как write-time agent-write nudge.** Единственный gate в design-time для класса «новая схема ниже порога ArchGate» — там, где CI бесполезен (post-hoc), а ArchGate/.md-reminder не срабатывают.

2. **Честный уровень принуждения — не E2, не «E3-displayed»:**
   - для **файловой схемы** (`*registry*.yaml`/`*-catalog.yaml`, новое ID-префикс-семейство) → **E3-prompted-with-detection**: PreToolUse показывает шаблон + PostToolUse проверяет, заполнены ли обязательные поля (owner / bounded_context) в каноническом месте схемы; не заполнены → `warn` в `session-warn-log` → всплывает в Close summary, пилот дожимает;
   - для **inline-оси** в существующем артефакте (нет канонического слота) → **displayed + soft-ack** через `session-warn-log`.

3. **Развязка от AR.009 — узкое событие `schema_registration_attempt`**, которое слушает только AR.234. `artifact_creation_attempt` (триггер AR.009) **не реанимируем**. Реабилитация AR.009 (снизить FP <15% через расширение whitelist + 50 FP/FN примеров + subagent-классификатор) — **вне scope этого ADR**, отдельное предусловие.

4. **Membership-условие в одном месте — `schema-triggers.yaml`** (рядом с rule-engine):
   - читают **оба**: обёртка-хук (`should_fire` — грубый glob, возбуждать ли событие) и `check_schema_registration_gate` (`is_in_scope` — тонкий verdict);
   - `AR.234.triggers` в реестре сводится к **одному** `schema_registration_attempt`, синхронному с `fired_event` конфига (сейчас в AR.234 три имени-триггера — начало смазывания, чинится этим пунктом).

5. **Анти-молчаливая-смерть + гарантия обратимости таксономии — dogfood-self-test** (расширение существующего недельного self-test rule-engine): симулировать `schema_registration_attempt` на fixture и проверять (а) `schema-triggers.yaml` читается, (б) `fired_event` совпадает с `AR.234.triggers`, (в) событие реально firing'ит, (г) check возвращает `warn` с ожидаемым шаблоном.

6. **Surface — PreToolUse non-block stdout, шаблон 3-4 поля** (owner / ось ортогональна? / bounded_context / enforcement_mechanism), не эссе. Ack = заполненные §5-поля в каноне схемы, не отдельная церемония.

7. **Метрики (split, не «динамика COL-класса» — N≈13/квартал = шум):**
   - **лид-индикатор** (меряем сразу): доля `schema_registration_attempt`, где §5-поля заполнены до ближайшего commit (источник — PostToolUse-check);
   - **лаг-индикатор** (audit, не статистика): ежеквартальный ручной/субагентский разбор новых схем → `audit_finding_count` (схемы без owner/ортогональности);
   - **фальсификатор:** за первые **K=5 срабатываний на файловой схеме** доля заполнения §5 < 50% → откат к null-опции. Не ждём квартал. *(уточнение Kimi: K=5 считается по файловым схемам с машинной детекцией; inline-оси в тот же знаменатель без ручной пометки не смешиваются.)*

8. **Открытый вопрос (не deliverable):** governance `schema-triggers.yaml` + nudge-конфига (owner = DP.ROLE.012 Стратег по догфуду AR.234) — рекурсивно та же схема, что лечим. Без живого governance «обратимость таксономии» (п.4) перестаёт быть гарантией → держится тестом п.5.

## Главная дистинкция (на вынос в Pack)

**E3-prompted ≠ E3-displayed.** Prompt без требования ответа = только *displayed*: агент видит подсказку в non-block stdout, читает и спокойно продолжает Write, не ответив на §5. Gate реален только если **игнор детектируется** — в каноне артефакта (PostToolUse presence-check) или в Close summary (session-warn-log). Без детекции ответа «E3-prompted» — самообман, переименование дыры в фичу.

## Цена решения (названа явно)

Узкое событие = размен **single-source-of-trigger** (чистая generic-шина dispatch_event) на **изоляцию шума AR.009**. Это не «архитектурная чистота», а осознанный trade-off. Сделан в правильную сторону по асимметрии:
- размазанность trigger-таксономии **обратима** (собирается обратно одним `schema-triggers.yaml` + синхронным `triggers:`), **при условии** живого governance (п.8) и dogfood-теста (п.5);
- отравление редкого ценного nudge шумом AR.009 **необратимо** — привычку «игнорировать маркер» не разучить.

Размен ограниченной обратимой цены на устранение необратимого риска.

## Отвергнутые альтернативы

- **Generic-event `artifact_creation_attempt` + самофильтрация check-функций** (single-source-of-trigger). Отвергнуто: будит спящий AR.009 (FP 30-40% на каждый файл) → шум топит редкий ценный nudge. Развязка обязательна.
- **Null-опция (reminder в AR.234.md + CI structural + ArchGate semantic).** Отвергнуто: .md-reminder невидим в write-time; CI ловит только structural post-hoc; ArchGate не триггерится на «ещё один yaml-реестр» (sub-threshold). Дыра «тихое создание схемы ниже порога ArchGate» остаётся открытой — а это и есть источник COL-01…08.
- **Coarse-glob в обёртке + независимая логика в check** (без общего конфига). Отвергнуто: дублирует membership-условие (два места правки при добавлении нового типа схемы) → дрейф. Заменено общим `schema-triggers.yaml`.

## Реализация (контракт для спин-офф РП; не исполнено в этой сессии)

> Требует разрешения пилота на правку хуков (S-33). Конкретные точки врезки:

- `~/IWE/.claude/hooks/schema-registration-gate.sh` — новая PreToolUse[Write] обёртка: `should_fire` по `schema-triggers.yaml` → при совпадении `RULE_EVENT=schema_registration_attempt` → `source rule-engine.sh; dispatch_event`.
- `~/IWE/.claude/hooks/schema-triggers.yaml` — membership-конфиг (path_globs / id_prefix_family / classification_axis / fired_event).
- `rule-engine.sh::check_schema_registration_gate` — вшить (сейчас PSEUDOCODE); `is_in_scope` из того же конфига.
- **PostToolUse presence-check** *(уточнение Kimi — назвать конкретику, не hand-wavy):* расширить `DS-ecosystem-development/0.OPS/.../registry-catalog.py --validate` на required-non-empty (owner, bounded_context) для файловой схемы; для inline-оси — `warn`-маркер из `rule-engine.sh` в `session-warn-log`.
- `AR.234.triggers` → свести к `schema_registration_attempt`; `hook_status` обновить.
- dogfood-fixture в недельный self-test rule-engine (п.5).
- Регистрация обёртки в `.claude/settings.json` PreToolUse[Write].

## Метрика отслеживания

- Срабатываний: 0 (не реализовано). Первое — при врезке + первом новом реестре.
- Ревизия: после K=5 срабатываний на файловой схеме (фальсификатор п.7).
