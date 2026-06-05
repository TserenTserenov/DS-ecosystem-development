---
created: 2026-06-05
type: visual-prompts
event: "Семинар IWE 2.0 · 7 июня 2026"
deck: seminar-2026-06-07-slides.md
wp: WP-351
note: >
  Промпты для генерации визуалов слайдов. Стиль — чистая схема, не комикс
  (требование структуры). Результаты класть в ./visuals/ под именами NN-slug.png,
  как они подключены в деске.
---

# Промпты для визуала — Семинар IWE 2.0

> **Где брать:** Ideogram / DALL·E 3 / Midjourney. Для схем с подписями лучше Ideogram или DALL·E (точнее держат текст). Чистые иллюстрации — Midjourney.
> **Куда класть:** `./visuals/NN-slug.png` (имена совпадают с комментариями в `seminar-2026-06-07-slides.md`).
> **Формат:** 16:9, под тёмные и светлые фоны — см. пометку у каждого.

## Общий стиль (добавлять к каждому промпту)

```
Style: clean minimalist vector schematic, professional, flat design.
Palette: deep navy #1a3a5c, bright blue #0066cc, white, light grey.
No comic style, no cartoon superhero. Generous white space. 16:9.
Thin confident lines, geometric, calm. No clutter, no busy backgrounds.
```

---

## Слайд 1 — Титул: человек в контуре экзоскелета (фон, тёмный)

**Назначение:** задать образ «железного человека» — человек + усиливающий контур, без комикса.

```
A single human figure standing confidently, seen from front, rendered as a clean
line drawing. Around the figure — a subtle geometric exoskeleton outline (thin glowing
blue lines, like an augmentation framework), NOT armor, NOT a comic superhero.
Dark navy background (#0d2438). The exoskeleton lines glow soft blue (#0066cc).
Minimalist, elegant, schematic. Leave the upper-left area emptier for the title text.
16:9, cinematic calm.
```
*Под тёмный титульный слайд. Текст накладывается слева.*

---

## Слайд 3 — Йода (мудрый наставник, мировоззрение)

**Назначение:** «дело в мышлении, не в инструментах».

```
A small, wise, ancient mentor figure (Yoda-like archetype: small green wise master
with large ears, calm closed eyes, meditative pose), painterly but restrained,
soft studio lighting, dark navy background. Conveys wisdom and philosophy.
Centered, lots of negative space around for text.
```
**Caveat:** Йода — персонаж с защитой авторских прав. Для публичного показа безопаснее взять **официальный лицензированный кадр** Star Wars или заменить на нейтрального «мудрого наставника». Промпт выше даёт архетип, не точного персонажа.

---

## Слайд 6 — Внимание: мир → надсистема → я (сначала вовне, потом вовнутрь)

**Назначение:** показать направление внимания снаружи внутрь.

```
A schematic diagram of three nested circles: large outer circle labelled "Мир",
middle circle "Надсистема", small inner circle "Я + костюм".
A bold blue arrow flows from OUTSIDE inward (from "Мир" toward "Я"), showing
attention direction. Clean flat vector, navy and blue palette, white background,
minimal labels in Russian. Lots of white space.
```
*Светлый фон.*

---

## Слайд 12 — Человек + костюм = железный человек

**Назначение:** формула образа.

```
A simple equation-style schematic, left to right:
[clean line drawing of a person]  +  [geometric blue exoskeleton outline]
=  [the person inside the glowing exoskeleton outline].
Flat vector, navy/blue on white, thin lines, generous spacing.
Plus sign and equals sign in blue. No text labels needed.
```
*Светлый фон.*

---

## Слайд 15 — Три объекта внимания (три круга)

**Назначение:** карта объектов.

```
Three clean circles in a row, equal size, connected by thin lines.
Circle 1: a small human icon, label "Человек".
Circle 2: an exoskeleton/environment icon, label "Костюм".
Circle 3: human-inside-exoskeleton icon, label "Железный человек".
Flat minimalist vector, navy/blue on white, balanced, lots of white space.
Russian labels.
```
*Светлый фон.*

---

## Слайд 19 — Таксист vs персональный водитель

**Назначение:** различие готового ИИ и своей среды.

```
A side-by-side comparison illustration, two panels:
LEFT panel — a generic taxi with a "?" passenger, label "Готовый ИИ — таксист:
общий, тебя не знает".
RIGHT panel — a personal driver in a car who clearly knows the passenger
(a small notebook/learning icon), label "Своя среда — водитель, которого ты дообучаешь".
Clean flat vector, navy/blue palette, white background, friendly but professional,
Russian labels. Clear visual contrast between the two.
```
*Светлый фон.*

---

## Слайд 20 — Из чего состоит костюм: ядро + слои

**Назначение:** устройство ИИ-среды.

```
A concentric-layers diagram. Center core circle labelled "LLM (ядро)".
Around it, a ring divided into labelled segments: "Память", "Персона", "База знаний",
"Роли / скиллы", "Скрипты", "MCP", "Агенты". Thin connecting lines from core to each segment.
Clean flat vector, navy core, blue ring segments, white background, Russian labels,
balanced and readable. Minimalist.
```
*Светлый фон. Семь сегментов вокруг ядра.*

---

## Слайд 23 — Лесенка старта

**Назначение:** путь онбординга.

```
An ascending staircase of 6 steps, left to right going up. Each step labelled in Russian:
"Подключи среду", "Войди", "Дай согласие", "Диагностика (5 мин)", "Получи руководство",
"Работай". A small figure climbing. Flat vector, blue steps on white, navy labels,
clean and motivating, generous white space.
```
*Светлый фон.*

---

## Слайд 28 — Лестница владения костюмом

**Назначение:** три ступени мастерства.

```
Three ascending steps, left to right going up, labelled in Russian:
"Управлять" (today), "Развивать" (over time), "Создавать" (mastery).
Each step slightly higher and a deeper blue. A small figure progressing upward.
Flat minimalist vector, navy/blue on white, clean, lots of white space.
```
*Светлый фон.*

---

## Слайд 27 — Костюм умнеет с каждым днём (опционально)

**Назначение:** дообучение среды растёт во времени.

```
A simple growth timeline: a small exoskeleton outline on day 1 that becomes richer
and brighter across several steps (day 1 → day 7 → day 30), with small "+" icons
(notes, work products) feeding into it at each step. Flat vector, blue gradient
of intensity, white background, minimal Russian labels ("каждый РП кормит среду").
```
*Светлый фон. Опционально — если на слайде 27 нужен визуал помимо текста.*

---

## Сводка: что под какой слайд

| Слайд | Файл | Фон |
|-------|------|-----|
| 1 Титул | `visuals/01-iron-human.png` | тёмный |
| 3 Мировоззрение | `visuals/03-yoda.png` | тёмный |
| 6 Вовне→вовнутрь | `visuals/06-attention-outward.png` | светлый |
| 12 Железный человек | `visuals/12-human-plus-suit.png` | светлый |
| 15 Три объекта | `visuals/15-three-objects.png` | светлый |
| 19 Таксист vs водитель | `visuals/19-taxi-vs-driver.png` | светлый |
| 20 Устройство среды | `visuals/20-core-layers.png` | светлый |
| 23 Лесенка старта | `visuals/23-start-staircase.png` | светлый |
| 28 Лестница владения | `visuals/28-mastery-ladder.png` | светлый |
| 27 Рост среды (опц.) | `visuals/27-costume-grows.png` | светлый |

> Остальные слайды — текстовые, визуал не требуется.
