---
type: spec
status: active
created: 2026-01-18
updated: 2026-04-10
family: F0
scope: repository
---

# Спецификация Frontmatter

> **Single source of truth** для словаря `status` и связанных полей во всём репозитории.
> Другие документы (02-document-families.md, 08-anti-patterns.md) ссылаются сюда, а не определяют свои словари.

## Формат

YAML-блок в начале документа, ограниченный `---`:

```yaml
---
field: value
list:
  - item1
  - item2
---
```

## Обязательные поля

### type

Тип документа.

```yaml
type: doc | spec | process | report | template
```

| Значение | Описание |
|----------|----------|
| `doc` | Описательный документ |
| `spec` | Спецификация, требования |
| `process` | Описание процесса |
| `report` | Отчёт, результат |
| `template` | Шаблон |

### status

Статус зрелости документа. **Статус — это атрибут документа, не его адрес.** Место документа в репозитории определяется матрицей 3×3 (ядро/система/роль) и не меняется при смене статуса. См. раздел «Размещение vs статус» ниже и антипаттерн АП-23.

```yaml
status: stub | draft | review | active | archived | superseded
```

| Значение | Описание | Типичные поля |
|----------|----------|----------------|
| `stub` | Заглушка, только заголовок | — |
| `draft` | Черновик, в работе. Могут быть нерешённые вопросы, блокеры. | `blockers:` |
| `review` | Готов к ревью/обсуждению. Блокеров нет, ждём решения. | — |
| `active` | Принят, используется. Для архитектурных решений — породил ADR. | `adr_ref:` (если ADR) |
| `archived` | Устарел, не используется, но сохранён для истории. | — |
| `superseded` | Заменён новым документом. | `superseded_by:` |

**Переходы:**

```
stub → draft → review → active → archived
                 ↓         ↓
              archived   superseded
```

- `draft → review`: автор снял блокеры
- `review → active`: принято решением команды / на обсуждении / ритуалом Close
- `active → superseded`: появился новый документ, покрывающий ту же область (обязательно заполнить `superseded_by:`)
- `active → archived`: документ устарел, замены нет (исторический)

### blockers

Список нерешённых вопросов/зависимостей, мешающих промоции документа (актуально для `status: draft`).

```yaml
blockers:
  - "РФ + инвесторы — противоречие (обсуждение 13 апр с Андреем)"
  - "Ждём решения Ory JWT (WP-187)"
```

### adr_ref

Ссылка на ADR, который зафиксировал решения этого документа (актуально для `status: active` архитектурных документов).

```yaml
adr_ref: "B3.1.Meaning/ADR-012-regional-split.md"
```

### superseded_by

Путь к документу-замене (обязательно при `status: superseded`).

```yaml
superseded_by: "../new-location/new-document.md"
```

### created

Дата создания в формате ISO 8601.

```yaml
created: 2026-01-14
```

### updated

Дата последнего обновления.

```yaml
updated: 2026-01-14
```

## Рекомендуемые поля

### family

Код семейства документа.

```yaml
family: FA4    # Ядро A, семейство 4
family: FB9    # Ядро B, семейство 9
family: F0     # Управление хранилищем
```

### kernel

Буква ядра.

```yaml
kernel: A | B | C | ...
```

### system

Система в рамках ядра.

```yaml
system: Suprasystem | System-of-Interest | Constructor
```

### role

Роль (угол зрения).

```yaml
role: Meaning | Architecture | Operations
```

### scope

Область применимости.

```yaml
scope: local-edge | project | ecosystem | universal
```

### layer

Слой знаний.

```yaml
layer: methodology | architecture | operations | data
```

### related

Связанные документы.

```yaml
related:
  - ../path/to/doc1.md
  - ../path/to/doc2.md
```

### fpf_patterns

Связанные паттерны FPF.

```yaml
fpf_patterns:
  - A.1       # Holonic Foundation
  - A.1.1     # Bounded Context
  - B.3       # Trust Calculus
```

### target_audience

Целевая аудитория.

```yaml
target_audience:
  - developers
  - managers
  - ai-agents
```

### tags

Свободные теги для поиска.

```yaml
tags:
  - architecture
  - api
  - security
```

## Полный пример

```yaml
---
type: spec
status: active
created: 2026-01-14
updated: 2026-01-14
family: FA5
kernel: A
system: System-of-Interest
role: Architecture
scope: project
layer: architecture
related:
  - ../A2.1.Meaning/requirements.md
  - ../A2.3.Operations/deployment.md
fpf_patterns:
  - A.1
  - A.7
target_audience:
  - developers
  - architects
tags:
  - api
  - design
---
```

## Размещение vs статус

**Правило:** размещение документа в репозитории определяется **матрицей 3×3** (ядро × система × роль), а статус зрелости — **полем `status` в frontmatter**. Это ортогональные измерения.

**Что из этого следует:**

- ❌ **Нельзя** заводить папки `drafts/`, `proposals/`, `accepted/` — это создаёт второй словарь размещения, конфликтующий с S2R.
- ❌ **Нельзя** перемещать документ при смене статуса (`git mv` при промоции `draft → active`).
- ✅ **Можно и нужно** сразу класть документ в правильное место по S2R, даже если он `stub` или `draft`.
- ✅ **Можно и нужно** менять только `status` и связанные поля (`blockers`, `adr_ref`, `superseded_by`) при промоции.

**Почему:**
1. Адрес документа должен быть стабильным — ссылки не должны ломаться при промоции.
2. История git чище: `status: draft → active` видно в одной правке, а не в коммите переименования.
3. Документ ищется по теме, а не по статусу. Тема = адрес S2R, статус = метаданные.
4. Статусы машиночитаемы: можно сделать отчёт «все `draft` с блокерами» без обхода папок.

**См. также:** антипаттерн [АП-23](../0.1.Knowledge-Logic/08-anti-patterns.md#ап-23-папки-по-статусу-зрелости) в 08-anti-patterns.md.

## Валидация

Frontmatter должен:
1. Начинаться с `---`
2. Заканчиваться `---`
3. Быть валидным YAML
4. Содержать все обязательные поля
5. `status` — только значения из словаря выше
6. При `status: superseded` обязательно поле `superseded_by`

## См. также

- [02-standards.md](02-standards.md) — стандарты оформления
- [04-document-creation.md](04-document-creation.md) — процесс создания
- [../0.1.Knowledge-Logic/02-document-families.md](../0.1.Knowledge-Logic/02-document-families.md) — семейства F1-F9 и целевые читатели
- [../0.1.Knowledge-Logic/08-anti-patterns.md](../0.1.Knowledge-Logic/08-anti-patterns.md) — антипаттерны (в т.ч. АП-23 «папки по статусу»)
