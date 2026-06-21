# Seed-файлы Исследовательского Развития (ИР)

**Формат seed-файла v0 (WP-149 Ф-rung-fidelity, 2026-06-21).**
Расширение схемы и продакшн-контент — в рамках WP-364 Ф12.

## Назначение

Seed-файлы (.md) в этой директории подхватываются `_program_seed_source_present`
как индикатор того, что у программы research-development есть собственный контент.
До WP-364 Ф12 в директории только тестовая фикстура.

## Формат seed-файла v0

```markdown
---
program: research-development
level: <int>           # degree_level (1-7, см. _MSH_TO_DEGREE_LEVEL)
stage_name: <str>      # имя уровня (Наблюдатель / Исследователь / ...)
domain: <str>          # domain slug или "generic"
seed_type: fixture     # fixture | content (fixture = только для тестов)
created: YYYY-MM-DD
---

## Нарративная фаза

<Короткое описание того, где находится человек на этом уровне.>

## Ключевой фокус развития

<Что сейчас важнее всего развивать.>

## Типичный bottleneck

<Что чаще всего мешает.>
```

## Файлы

| Файл | Уровень | Тип | Назначение |
|------|---------|-----|------------|
| `reformator-knowledge-worker.md` | 6 (Реформатор) | fixture | pytest smoke WP-149 |
