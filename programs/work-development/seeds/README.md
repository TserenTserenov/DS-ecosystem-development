# Seed-файлы Рабочего Развития (РР)

**Формат seed-файла v0 (WP-149 Ф-rung-fidelity, 2026-06-21).**
Расширение схемы и продакшн-контент — в рамках WP-364 Ф12.

## Назначение

Seed-файлы (.md) в этой директории подхватываются `_program_seed_source_present`
как индикатор того, что у программы work-development есть собственный контент.
До WP-364 Ф12 в директории только тестовая фикстура.

## Формат seed-файла v0

```markdown
---
program: work-development
level: <int>           # degree_level (5-11, официальная 11-ступенчатая шкала ШСМ, см. _MSH_TO_DEGREE_LEVEL)
stage_name: <str>      # имя уровня (Работник / Стратег / ...)
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
| `5-knowledge-worker.md` | 5 (Работник) | content | продакшн-контент |
| `6-knowledge-worker.md` | 6 (Стратег) | content | продакшн-контент |
| `7-knowledge-worker.md` | 7 (Специалист) | content | продакшн-контент |
| `8-knowledge-worker.md` | 8 (Практик) | content | продакшн-контент |
| `9-knowledge-worker.md` | 9 (Мастер) | content | продакшн-контент; тот же текст скопирован в `research-development/seeds/9-knowledge-worker.md` (28.07) — Мастер одновременно выход РР и вход ИР, по решению пилота |
| `10-knowledge-worker.md` | 10 (Реформатор) | content | продакшн-контент |
| `11-knowledge-worker.md` | 11 (Революционер) | content | продакшн-контент |
| `reformator-knowledge-worker.md` | 6 (устарело) | fixture, не читается кодом | мёртвый файл-остаток, кандидат на удаление (найдено 28.07, WP-149) |
