---
created: 2026-06-05
updated: 2026-06-06
type: visual-prompts
event: "Семинар IWE 2.0 · 7 июня 2026"
deck: seminar-2026-06-07-slides.md
wp: WP-351
note: >
  Промпты для генерации визуалов слайдов. Стиль — чистая схема, не комикс.
  Результаты класть в ./visuals/. Номера слайдов — по текущему деску (4 часа).
---

# Промпты для визуала — Семинар IWE 2.0

> **Где брать:** Ideogram / DALL·E 3 (схемы с подписями) · Midjourney (чистые иллюстрации).
> **Куда класть:** `./visuals/` (имена ниже совпадают с комментариями в `seminar-2026-06-07-slides.md`).
> **Формат:** 16:9.

## Общий стиль (добавлять к каждому промпту)

```
Style: clean minimalist vector schematic, professional, flat design.
Palette: deep navy #1a3a5c, bright blue #0066cc, white, light grey.
No comic style, no cartoon superhero. Generous white space. 16:9.
Thin confident lines, geometric, calm. No clutter.
```

---

## Титул (тёмный) — человек в контуре экзоскелета

`visuals/01-iron-human.png`
```
A single human figure standing confidently, clean line drawing. Around it — a subtle
geometric exoskeleton outline (thin glowing blue lines, augmentation framework),
NOT armor, NOT a comic superhero. Dark navy background (#0d2438), lines glow soft blue.
Minimalist, elegant. Upper-left area emptier for title text. 16:9.
```

## Боли — три «было»-карточки (слайд «Узнаёте себя?»)

`visuals/03-pains.png`
```
Three flat cards in a row, each showing a frustrated knowledge worker mini-scene,
muted grey-blue tone (problem state):
Card 1 — many scattered chat windows, one fading away, label "всё теряется".
Card 2 — a robot behind a locked vendor safe holding a notepad it won't hand over, label "память чужая".
Card 3 — a pile of documents that doesn't grow into anything, label "опыт не копится".
Clean flat vector, navy/grey palette, white background, Russian labels, calm not chaotic.
```

## Траектория — новичок → пользователь → создатель (ранний слайд И финал)

`visuals/06-trajectory.png`
```
An ascending 3-step staircase, left to right going up, each step a deeper blue.
Step 1 "Новичок" (small figure with a phone/chat). Step 2 "Пользователь костюма"
(figure with a glowing environment around). Step 3 "Создатель костюма" (figure
building/shaping the environment). Flat vector, navy/blue on white, motivating,
generous white space, Russian labels.
```

## Мировоззрение — Йода (наставник)

`visuals/08-yoda.png`
```
A small, wise, ancient mentor figure (Yoda-like archetype: small green wise master,
large ears, calm closed eyes, meditative pose), restrained painterly style, soft
lighting, dark navy background, lots of negative space for text.
```
**Caveat:** Йода защищён авторским правом. Для публичного показа — лицензированный кадр Star Wars или нейтральный «мудрый наставник». Промпт даёт архетип, не точного персонажа.

## Сначала вовне, потом вовнутрь

`visuals/10-attention-outward.png`
```
Three nested circles: large outer "Мир", middle "Надсистема", small inner "Я + костюм".
A bold blue arrow flows from OUTSIDE inward, showing attention direction. Flat vector,
navy/blue on white, minimal Russian labels, lots of white space.
```

## Не панацея — много сред, мастерство твоё (опц., слайд «Мой IWE — не панацея»)

`visuals/12-not-panacea.png`
```
Several different AI-environment "boxes" of varying brands/colours arranged loosely
(interchangeable tools), and one constant human figure in the centre carrying a small
glowing badge labelled "мышление + мастерство". Arrows show the human moving between
the boxes while keeping the badge. Flat vector, navy/blue on white, Russian labels.
Message: environments are swappable, the human's mastery is constant.
```

## Железный человек

`visuals/19-human-plus-suit.png`
```
Equation-style schematic, left to right:
[person line drawing] + [blue exoskeleton outline] = [person inside the glowing outline].
Flat vector, navy/blue on white, thin lines, plus and equals signs in blue. No labels.
```

## Три объекта внимания

`visuals/22-three-objects.png`
```
Three equal circles in a row, connected by thin lines. Circle 1 human icon "Человек",
circle 2 environment icon "Костюм", circle 3 human-inside-exoskeleton "Железный человек".
Flat minimalist vector, navy/blue on white, balanced, Russian labels.
```

## Таксист vs персональный водитель

`visuals/26-taxi-vs-driver.png`
```
Two-panel comparison. LEFT — a generic taxi with a "?" passenger, label
"Готовый ИИ: общий, тебя не знает". RIGHT — a personal driver who knows the passenger
(small learning/notebook icon), label "Своя среда: дообучаешь под себя".
Flat vector, navy/blue, white background, clear contrast, Russian labels.
```

## Из чего состоит костюм — ядро + слои

`visuals/27-core-layers.png`
```
Concentric-layers diagram. Center core "LLM (ядро)". Around it a ring of labelled
segments: "Память", "Персона", "База знаний", "Роли / скиллы", "Скрипты", "MCP", "Агенты".
Thin lines from core to each. Flat vector, navy core, blue ring, white background,
readable Russian labels.
```

## Лесенка старта

`visuals/30-start-staircase.png`
```
Ascending staircase of 6 steps going up, Russian labels: "Подключи среду", "Войди",
"Дай согласие", "Диагностика (5 мин)", "Получи руководство", "Работай". Small figure
climbing. Flat vector, blue steps on white, navy labels, generous white space.
```

## Лестница владения костюмом

`visuals/35-mastery-ladder.png`
```
Three ascending steps, Russian labels "Управлять", "Развивать", "Создавать", each
higher and deeper blue, small figure progressing upward. Flat minimalist vector,
navy/blue on white, lots of white space.
```

---

## Сводка: файл → слайд

| Файл | Слайд | Фон |
|------|-------|-----|
| `01-iron-human.png` | Титул | тёмный |
| `03-pains.png` | «Узнаёте себя?» (боли) | светлый |
| `06-trajectory.png` | «Куда растём» + финал | светлый |
| `08-yoda.png` | «Сначала мировоззрение» | тёмный |
| `10-attention-outward.png` | «Создатель меняет мир» | светлый |
| `12-not-panacea.png` | «Мой IWE — не панацея» (опц.) | светлый |
| `19-human-plus-suit.png` | «Железный человек» | светлый |
| `22-three-objects.png` | «Три объекта внимания» | светлый |
| `26-taxi-vs-driver.png` | «Таксист или водитель?» | светлый |
| `27-core-layers.png` | «Из чего состоит костюм» | светлый |
| `30-start-staircase.png` | «Как стартовать» | светлый |
| `35-mastery-ladder.png` | «Лестница владения» | светлый |

> Остальные слайды — текстовые, визуал не требуется.
