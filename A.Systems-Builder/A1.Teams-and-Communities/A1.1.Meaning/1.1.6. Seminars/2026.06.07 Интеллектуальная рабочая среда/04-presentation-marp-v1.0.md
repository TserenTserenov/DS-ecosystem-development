---
marp: true
theme: may31
paginate: true
size: 16:9
html: true
header: "7 июня 2026 · Интеллектуальная рабочая среда 2.0"
footer: "v1.0 · Aisystant · @aist_me_bot"
style: |
  /* 7 июня override: показываем eyebrow (Блок N · …) — даёт progress в 150-мин семинаре */
  section.with-eyebrow .eyebrow {
    display: block;
    color: #94a3b8;
    font-size: 0.7em;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 8px;
  }
---

<!-- _class: title -->
<!-- _paginate: false -->
<!-- _header: "" -->
<!-- _footer: "" -->

# Интеллектуальная&nbsp;рабочая&nbsp;среда&nbsp;2.0

## Практическая&nbsp;сборка

<div class="speaker">
Церен Церенов · сооснователь МИМ
</div>

<div class="meta">7 июня 2026 · платный онлайн-семинар · 150 мин</div>

---

<!-- _class: center -->

# Карта семинара

<div class="cards-3" style="margin-top:30px">

<div class="card accent">
<span class="num">0:00 → 1:00</span>
<h3>Часть 1 · Демо</h3>
<p>Живое демо IWE изнутри: 10 фич, которые видно за 30-60 сек</p>
</div>

<div class="card accent">
<span class="num">1:00 → 1:30</span>
<h3>Часть 2 · Архитектура</h3>
<p>Словарь IWE · 4 слоя знаний · агенты · IWE vs Платформа</p>
</div>

<div class="card accent">
<span class="num">1:30 → 2:30</span>
<h3>Часть 3 · Практика + ЛР</h3>
<p>Подключаете браузер к Aisystant MCP · 4 мастерства · мост к программе</p>
</div>

</div>

<p class="muted" style="text-align:center;margin-top:30px;font-size:1.05em"><strong>Уйдёте</strong> с подключённым браузером, диагнозом ступени и планом «куда дальше».</p>

---

<!-- _class: with-eyebrow -->

<div class="eyebrow">Блок 1 · Мост от 31 мая</div>

# Кто был · кто впервые

<div class="cards-2" style="margin-top:24px">

<div class="card muted">
<h3>Кто был 31 мая</h3>
<p>Вы уже сделали первый шаг — увидели связку человек-ИИ. Сегодня собираем среду, в которой связка живёт.</p>
</div>

<div class="card accent">
<h3>Кто впервые</h3>
<p>Карточка A5 у вас на руках. Пять тезисов 31 мая — это весь контекст, который нужен, чтобы войти в разговор без чувства «пропустил половину».</p>
</div>

</div>

<p style="text-align:center;margin-top:30px;font-size:1.15em;color:#f1f5f9"><strong style="color:#f97316">Сегодня не «как пользоваться ИИ».</strong></p>

<p class="muted" style="text-align:center;font-size:1em">Сегодня про то, как перестать быть заложником одной специальности. Как выращивать новую компетенцию <strong>системно</strong>.</p>

---

<!-- _class: with-eyebrow -->

<div class="eyebrow">Блок 2 · Диагностика</div>

# Три ограничения ИИ-ассистента

<div class="cards-3" style="margin-top:30px">

<div class="card">
<span class="num">№1</span>
<h3>Чужая память</h3>
<p>Понедельник: «помоги спланировать неделю». Среда: «давайте я на этот раз запишу» — а память всё равно останется в чёрном ящике вендора.</p>
</div>

<div class="card">
<span class="num">№2</span>
<h3>Галлюцинации</h3>
<p>В незнакомой области — уверенные ответы, часть из которых неверна. Без эксперта рядом вы не заметите ошибку.</p>
</div>

<div class="card">
<span class="num">№3</span>
<h3>Один на всё</h3>
<p>Сотни часов работы не превращаются в вашу базу знаний — только в чужие заметки, которые вы не контролируете.</p>
</div>

</div>

<p class="muted" style="text-align:center;margin-top:24px;font-size:1.05em">Для разовых задач — терпимо. Для выращивания экспертности — катастрофа.</p>

---

<!-- _class: with-eyebrow center -->

<div class="eyebrow">Блок 2 · Вывод</div>

<p class="big-label accent" style="font-size:1.6em;line-height:1.3">Ассистент решает задачи.<br>Но не выращивает экспертность.</p>

<p class="muted" style="font-size:1.1em;max-width:760px;margin-top:24px"><strong>Нужна другая архитектура.</strong> Среда, а не ассистент.</p>

---

<!-- _class: with-eyebrow -->

<div class="eyebrow">Блок 3 · Экзокортекс vs Ассистент</div>

# Возьмите ту же услугу — довезти куда нужно

> **Такси:** садитесь, называете адрес, водитель везёт. Знает ли он, куда вы едете и зачем? Не знает и не должен. Поездка разовая.
>
> **Личный водитель:** знает расписание сына, какую школу, что у бабушки лестница без лифта, что в пятницу вы летите. Один и тот же навык — разные миры. Разница не в том, кто лучше водит, а в том, **кто знает вашу жизнь**.

<p class="muted" style="font-size:0.95em;margin-top:24px"><em>Свежий бенчмарк Artificial Analysis × IBM (ITBench-AA, май 2026): лучшие в мире модели справляются меньше чем с половиной задач рядового айтишника в крупной фирме. Не потому, что глупые. Потому что не понимают контекст.</em></p>

---

<!-- _class: with-eyebrow -->

<div class="eyebrow">Блок 3 · Таблица различий</div>

# Чат-ИИ ≠ Экзокортекс

|  | <span class="muted">ИИ-ассистент</span> | <span style="color:#f97316">ИИ-экзокортекс</span> |
|---|---|---|
| **Что делает** | Решает задачи | Выращивает компетенции |
| **Память** | Есть или нет — в любом случае чужая | Накапливает паттерны, принадлежит вам |
| **Контекст** | Вводите заново каждый раз | Знает вашу историю |
| **Инициатива** | Реагирует на запрос | Сам предлагает следующий шаг |
| **Через полгода** | Те же задачи быстрее | Новая область компетенции |

<p style="text-align:center;margin-top:24px;font-size:1.1em;color:#f1f5f9">Ассистент даёт <strong>знание</strong> (что сделать).<br>Экзокортекс выращивает <strong>мастерство</strong> (кем стать).</p>

---

<!-- _class: center -->

# Часть 1 · Живое демо

<p class="lead">10 фич, которые делает за вас среда.</p>

<p class="sub" style="margin-top:20px">35 минут · 4 акта · реальная работа на экране, не слайды.</p>

<p class="muted" style="margin-top:30px;font-size:0.95em">📦 Утро → 🔧 Работа → 📱 Везде → 🎯 Среда узнаёт меня</p>

---

<!-- _class: with-eyebrow -->

<div class="eyebrow">Акт 1 · Утро — план уже готов (5 мин)</div>

# Фича 1 · Day Open в 4:00

<div class="highlight-box" style="margin-top:20px">
<p style="font-size:1.05em"><strong>Что показываем (скриншот):</strong></p>
<ul style="font-size:1em">
<li>DayPlan, собранный агентом-Стратегом ночью</li>
<li>WeekPlan + REGISTRY рабочих продуктов недели</li>
<li>Compact dashboard: вчерашние коммиты, заметки, календарь</li>
</ul>
</div>

<p style="margin-top:24px;font-size:1.1em;color:#f1f5f9"><strong style="color:#f97316">Я проснулся — план уже на экране.</strong></p>

<p class="muted" style="font-size:0.95em">Среда работает, пока я сплю. 20-30 минут утреннего «с чего начать» — закрыты до того, как я сел.</p>

---

<!-- _class: with-eyebrow -->

<div class="eyebrow">Акт 1 · WP Gate</div>

# Фича 2 · ИИ сначала проверяет план

<div class="cards-2" style="margin-top:20px">

<div class="card muted">
<h3>Обычный ChatGPT</h3>
<p>«Сделай X» → начинает делать. Не проверяет, нужно ли это.</p>
</div>

<div class="card accent">
<h3>IWE Claude Code</h3>
<p>«Сделай X» → <strong>STOP.</strong> «Этой задачи нет в плане недели. Вот текущие РП: [таблица]. Записать?»</p>
</div>

</div>

<p style="text-align:center;margin-top:24px;font-size:1.05em;color:#f1f5f9">Среда <strong>удерживает фокус</strong>. Не вы должны помнить — среда помнит за вас.</p>

---

<!-- _class: with-eyebrow -->

<div class="eyebrow">Акт 2 · Работа · движок (10 мин)</div>

# Фича 3 · Capture-to-Pack — главный движок

<p style="font-size:1.05em"><strong>Live-задача:</strong> «добавь в бота приветствие на казахском».</p>

<ol style="font-size:1em;margin-top:16px">
<li>WP Gate проверяет план → ОК</li>
<li>Claude работает: меняет код, тестирует</li>
<li><strong>Момент истины:</strong> обнаруживается паттерн → пауза:<br><code>Capture: i18n fallback chain → Pack (method)</code></li>
<li><strong>Показ файла:</strong> открываем <code>DP.M.NNN-i18n-fallback.md</code>. Видны frontmatter, описание метода, связи.</li>
<li><strong>Замыкание:</strong> «через 3 месяца, когда буду делать французский — Pack отдаст этот метод. Это не моя память — это формальная база знаний.»</li>
</ol>

<p class="muted" style="font-size:0.9em;margin-top:16px">📌 <strong>Bonus:</strong> «Если бы я случайно вставил сюда API-ключ — среда не дала бы закоммитить. Защита от утечки секретов вшита в хук.» (10 сек)</p>

---

<!-- _class: with-eyebrow center -->

<div class="eyebrow">Акт 2 · Что только что произошло</div>

<p class="big-label accent" style="font-size:1.5em;line-height:1.3">Находку не забуду — она в формальной базе знаний.</p>

<p class="muted" style="font-size:1.05em;margin-top:24px;max-width:780px">Без среды: «о, классное решение!» → через 3 недели не вспомнишь.<br>С IWE: паттерн остаётся как сущность с ID, связями, frontmatter — переиспользуется при любом следующем похожем кейсе.</p>

---

<!-- _class: with-eyebrow -->

<div class="eyebrow">Акт 2 · Команда (5 мин)</div>

# Фича 4 · Два агента — Claude vs Kimi

<p style="font-size:1.05em;margin-bottom:16px"><strong>Pre-recorded клип, 2 мин.</strong> Реальный спор из недавней сессии.</p>

<div class="cards-3" style="margin-top:16px">

<div class="card muted">
<span class="num">30 сек · Setup</span>
<p>Сложная задача: спор о выборе подхода.</p>
</div>

<div class="card accent">
<span class="num">60 сек · Обмен</span>
<p>Claude предлагает X → Kimi возражает Y → консенсус Z</p>
</div>

<div class="card muted">
<span class="num">30 сек · Итог</span>
<p>report.md с зафиксированным решением + commit SHA</p>
</div>

</div>

<p style="text-align:center;margin-top:24px;font-size:1.1em;color:#f1f5f9"><strong>Команда специализированных агентов</strong> вместо одного-на-всё.</p>

<p class="muted" style="text-align:center;font-size:0.95em">Два агента дискутируют, я наблюдаю и выбираю. Это работает по-другому, чем один ChatGPT.</p>

---

<!-- _class: with-eyebrow -->

<div class="eyebrow">Акт 3 · Среда везде (6 мин)</div>

# Фичи 5-8 · IWE с телефона

<div class="cards-2" style="margin-top:20px">

<div class="card">
<h3>Фича 5 · Бот <code>.</code> → заметка</h3>
<p>Telegram @aist_me_bot: отправил «<code>. идея для семинара</code>» → 3 сек → новая строка в <code>fleeting-notes.md</code></p>
<p class="muted" style="font-size:0.9em">Доступ к среде с телефона. Без VS Code, без терминала.</p>
</div>

<div class="card">
<h3>Фича 6 · <code>/plan</code> → план дня</h3>
<p>Бот отвечает планом, собранным агентом-Стратегом. Тот же план, что в DayPlan.</p>
<p class="muted" style="font-size:0.9em">Среда отвечает в Telegram.</p>
</div>

<div class="card accent">
<h3>Фича 7 · <code>/points</code> → счёт</h3>
<p><em>«15 баллов, уровень 1, следующий уровень через 3 задачи»</em></p>
<p class="muted" style="font-size:0.9em">Среда поощряет настойчивость, а не дисциплину. Это про «втянусь ли я?»</p>
</div>

<div class="card">
<h3>Фича 8 · Marathon 14 дней</h3>
<p>День 1 / 14 — задание + рекомендация + цифры. Следующий шаг после семинара.</p>
<p class="muted" style="font-size:0.9em">@aist_pilot_bot — готовый план на каждый день.</p>
</div>

</div>

---

<!-- _class: with-eyebrow -->

<div class="eyebrow">Акт 4 · Среда узнаёт меня (12 мин)</div>

# Фича 9 · Diagnose-IWE — ступень за 5 мин

<p style="font-size:1.05em;margin-bottom:16px"><strong>Live в Claude Code. Ведущий проводит на себе, реальные ответы.</strong></p>

<div class="highlight-box">
<ol style="font-size:1em;margin-bottom:0">
<li>«Как часто вы планируете неделю?» — отвечаю: <strong>4</strong></li>
<li>«Что чаще всего блокирует рост — внешние обстоятельства или непонимание куда расти?» — отвечаю реально</li>
<li>... 3 вопроса ещё</li>
</ol>
</div>

<p style="margin-top:20px;font-size:1.1em;color:#f1f5f9"><strong>Результат на экране:</strong></p>

<p style="font-family:monospace;font-size:0.95em;color:#94a3b8;text-align:center">Ступень: 3 (Систематический) → S3<br>Bottleneck: cp.iwe (idx=2)<br>Рекомендованный поток: S3</p>

<p class="muted" style="text-align:center;font-size:0.95em;margin-top:20px"><strong>5 минут — больше, чем анкета на 30 полей.</strong></p>

---

<!-- _class: with-eyebrow -->

<div class="eyebrow">Акт 4 · Bonus inserts</div>

# Personal-guide · 1 файл на экран

<div class="cards-2" style="margin-top:24px">

<div class="card accent">
<h3>Personal-guide (30 сек)</h3>
<p>Открыть <code>methods.md</code> на весь экран. Видны: заголовки, ступени, домены, ссылки на Pack.</p>
<p class="muted" style="font-size:0.9em">Руководство собирается из Pack под мою ступень и bottleneck. Каждому пилоту — своё.</p>
</div>

<div class="card muted">
<h3>Цифровой двойник</h3>
<p>Pack-проекция меня самого: ступень, активность, история, RCS-слоты.</p>
<p class="muted" style="font-size:0.9em">Обновляется по факту работы. Не анкета — живой профиль.</p>
</div>

</div>

---

<!-- _class: with-eyebrow center -->

<div class="eyebrow">Акт 4 · Масштаб</div>

# Фича 10 · IWE — это работает у других

<pre style="font-size:1.1em;line-height:1.6;background:#1e293b;padding:20px;border-radius:8px;color:#e2e8f0">
~25 репозиториев        — вся система в Git
200+ сущностей знаний   — формализованы, с ID и связями
10+ агентов             — каждый в своей зоне
Local + Cloud Gateway   — два слоя доставки знаний
50 волонтёров           — первая когорта уже работает
~10 автозапусков/день   — планирование, захват, синхронизация
</pre>

<p class="muted" style="font-size:1em;margin-top:20px;max-width:780px">Выросло из 3 файлов за 4 месяца. В феврале — 0 пользователей. Сейчас — 50 человек используют эту среду.</p>

---

<!-- _class: center -->

# Часть 2 · Архитектура

<p class="lead">Как это устроено изнутри.</p>

<p class="sub" style="margin-top:20px">Сначала — словарь (4 термина). Потом — слои, агенты, конвейер.</p>

---

<!-- _class: with-eyebrow -->

<div class="eyebrow">Блок 5 · Словарь IWE · Карточка 1 из 4</div>

# Система ≠ Роль ≠ Агент

<div class="cards-3" style="margin-top:24px">

<div class="card">
<span class="num">Система</span>
<h3>Целое с эмерджентным свойством</h3>
<p>Машина = транспорт (колёса + двигатель + кузов работают вместе).</p>
<p class="muted" style="font-size:0.9em">Те же запчасти в гараже — металлолом.</p>
</div>

<div class="card">
<span class="num">Роль</span>
<h3>Функциональное место</h3>
<p>«Водитель» — роль в системе перевозки. Шеф-повар — роль в кухне.</p>
<p class="muted" style="font-size:0.9em">Роль = что делается, не кем.</p>
</div>

<div class="card accent">
<span class="num">Агент</span>
<h3>Система-исполнитель</h3>
<p>LLM + промпт + инструменты + память + контекст.</p>
<p class="muted" style="font-size:0.9em">Один Claude в разных сессиях — Стратег / Кодер / Аудитор.</p>
</div>

</div>

<p style="text-align:center;margin-top:24px;font-size:1.05em;color:#f1f5f9"><strong>Один агент = много ролей. Одна роль = разные агенты.</strong></p>

---

<!-- _class: with-eyebrow -->

<div class="eyebrow">Блок 5 · Словарь IWE · Карточка 2 из 4</div>

# Скрипт ≠ Скилл

<div class="cards-2" style="margin-top:24px">

<div class="card muted">
<span class="num">Скрипт</span>
<h3>Фиксированный код без LLM</h3>
<p><strong>Аналогия:</strong> автоматический полив на таймере.</p>
<p>Каждый день в 7:00, независимо от погоды и температуры.</p>
</div>

<div class="card accent">
<span class="num">Скилл</span>
<h3>Протокол работы для LLM</h3>
<p><strong>Аналогия:</strong> садовник, которому сказали «полей, когда нужно».</p>
<p>Он смотрит на почву и решает сам.</p>
</div>

</div>

<p style="text-align:center;margin-top:24px;font-size:1.05em;color:#f1f5f9">Скрипт <strong>детерминирован</strong>. Скилл — <strong>пространство решений</strong>.</p>

---

<!-- _class: with-eyebrow -->

<div class="eyebrow">Блок 5 · Словарь IWE · Карточка 3 из 4</div>

# MCP — разъём для знаний

<p style="font-size:1.15em;margin-bottom:16px"><strong>MCP (Model Context Protocol)</strong> — стандартный разъём между AI-агентом и источником знаний.</p>

<p style="text-align:center;font-size:1.4em;color:#f97316;margin:24px 0">⟶ Как <strong>USB-C</strong>: один разъём — любые источники ⟵</p>

<div class="highlight-box">
<p><strong>Зачем:</strong> один Claude может работать с разными источниками — знания Aisystant, ваш GitHub, личный календарь. До MCP это надо было склеивать вручную.</p>
<p style="margin-bottom:0"><strong>Aisystant MCP Gateway</strong> — ваше подключение к знаниям платформы. В Блоке 7 каждый подключит браузер именно через MCP.</p>
</div>

<p class="muted" style="text-align:center;font-size:0.95em;margin-top:16px">MCP — стандарт, который освободил знания от конкретной модели.</p>

---

<!-- _class: with-eyebrow -->

<div class="eyebrow">Блок 5 · Словарь IWE · Карточка 4 из 4</div>

# Экзокортекс + Harness — почему IWE ≠ Cursor

<div class="cards-2" style="margin-top:20px">

<div class="card muted">
<span class="num">Экзокортекс</span>
<h3>Продолжение головы</h3>
<p>Внешняя память + знания + автоматизация, которые становятся продолжением вашего мышления.</p>
<p class="muted" style="font-size:0.9em">Не «инструмент рядом», а «продолжение головы».</p>
</div>

<div class="card muted">
<span class="num">Harness</span>
<h3>Оснастка вокруг LLM</h3>
<p>Какие хуки, какие инструменты, какие правила, какая память. Не модель — способ её запрягать.</p>
<p class="muted" style="font-size:0.9em">Тот же Claude, разная оснастка = разный результат.</p>
</div>

</div>

<p style="text-align:center;margin-top:24px;font-size:1.15em;color:#f1f5f9"><strong>Cursor:</strong> harness для <span class="muted">кода</span>. &nbsp;&nbsp;<strong style="color:#f97316">IWE:</strong> harness для <span style="color:#f97316">развития мышления</span>.</p>

<p class="muted" style="text-align:center;font-size:0.95em;margin-top:12px">IWE = экзокортекс (память) + harness (оснастка) + методология (зачем).</p>

---

<!-- _class: with-eyebrow -->

<div class="eyebrow">Блок 5 · Архитектура · 4 слоя знаний</div>

# Что внутри среды

<pre style="font-size:1em;line-height:1.7;background:#1e293b;padding:20px;border-radius:8px;color:#e2e8f0;margin-top:16px">
┌───────────────────────────────────────────┐
│  <strong>Первые принципы (FPF)</strong>                  │
│  Как думать: система, роль, метод         │
├───────────────────────────────────────────┤
│  <strong>Вторые принципы (SPF)</strong>                  │
│  Как структурировать: Pack, DDD           │
├───────────────────────────────────────────┤
│  <strong>Pack — знания предметной области</strong>       │
│  Source-of-truth: сущности с ID,          │
│  связями, frontmatter                     │
├───────────────────────────────────────────┤
│  <strong>Downstream — производные системы</strong>       │
│  Бот, агенты, курсы — порождаются         │
│  из Pack                                  │
└───────────────────────────────────────────┘
</pre>

<p style="text-align:center;margin-top:16px;font-size:1.05em;color:#f1f5f9"><strong>Правило:</strong> Pack — единственный source-of-truth. Downstream меняется вслед за Pack.</p>

---

<!-- _class: with-eyebrow -->

<div class="eyebrow">Блок 5 · Архитектура · 4 ключевых агента</div>

# Команда среды

| Агент | Что делает | Когда |
|-------|-----------|-------|
| **Стратег** | Планирует неделю и день, ревьюит заметки | Автоматически пн 4:00, каждый день |
| **Экстрактор** | Превращает информацию в формализованные знания | Закрытие сессии |
| **Синхронизатор** | Собирает, маршрутизирует, уведомляет | Каждые 2 мин (файлы) |
| **Stage Evaluator** | Определяет ступень мастерства | По активности |

<p class="muted" style="text-align:center;font-size:1em;margin-top:20px">+ десятки других ролей (Аудитор, Верификатор, Постановщик, Декомпозитор, Контролёр развития...). Каждый — в своей зоне.</p>

---

<!-- _class: with-eyebrow -->

<div class="eyebrow">Блок 5 · Архитектура · Конвейер знаний</div>

# Одна правка в Pack → всё downstream обновилось

<pre style="font-size:0.95em;line-height:1.6;background:#1e293b;padding:20px;border-radius:8px;color:#e2e8f0">
Вы работаете → Обнаружили паттерн → <span style="color:#f97316">«Capture: X → Y»</span>
       ↓
ЭКСТРАКТОР классифицирует → <span style="color:#f97316">PACK (сущность с ID)</span>
       ↓
СИНХРОНИЗАТОР проецирует
       ├──→ <span style="color:#94a3b8">Бот</span> (отвечает пользователям)
       ├──→ <span style="color:#94a3b8">MCP</span> (семантический поиск)
       └──→ <span style="color:#94a3b8">Курс</span> (материалы обновились)
</pre>

<p style="text-align:center;margin-top:20px;font-size:1.1em;color:#f1f5f9">Месяц работы = <strong>47 паттернов</strong>. 12 тем, в которых среда «знает» ваш контекст. Скорость погружения в 4-ю неделю — <strong>в 3 раза выше</strong> первой.</p>

---

<!-- _class: with-eyebrow -->

<div class="eyebrow">Блок 6 · IWE vs Платформа Aisystant</div>

# Apple ≠ iPhone

<div class="cards-2" style="margin-top:20px">

<div class="card">
<h3>iPhone (= IWE)</h3>
<ul style="font-size:0.95em">
<li><strong>Где:</strong> у вас в кармане</li>
<li><strong>Кто управляет:</strong> вы</li>
<li><strong>Что делает:</strong> личное устройство</li>
<li><strong>Без интернета:</strong> работает</li>
<li><strong>Данные:</strong> на устройстве</li>
</ul>
</div>

<div class="card accent">
<h3>Apple (= Платформа Aisystant)</h3>
<ul style="font-size:0.95em">
<li><strong>Где:</strong> в Купертино + дата-центры</li>
<li><strong>Кто управляет:</strong> Apple / Aisystant</li>
<li><strong>Что делает:</strong> экосистема (App Store, iCloud)</li>
<li><strong>Без подключения:</strong> нет доступа к сервисам</li>
<li><strong>Данные:</strong> в iCloud / цифровой двойник</li>
</ul>
</div>

</div>

<p style="text-align:center;margin-top:20px;font-size:1.1em;color:#f1f5f9"><strong>IWE — автономная персональная среда</strong>, развёрнутая у вас, подключается к Платформе через MCP Gateway.</p>

---

<!-- _class: with-eyebrow center -->

<div class="eyebrow">Блок 6 · Stage Evaluator</div>

# Как понять, что растёте — объективно

<p class="big-label accent" style="font-size:1.4em;line-height:1.3">Не «мне кажется».<br>Постоянная калибровка по фактам вашей работы.</p>

<p class="muted" style="font-size:1em;margin-top:24px;max-width:780px"><strong>Stage Evaluator</strong> живёт на Платформе. Видит агрегированные данные. Ваша IWE присылает активность — Платформа возвращает оценку: ступень + bottleneck + рекомендуемый следующий шаг.</p>

<p class="muted" style="font-size:0.95em;margin-top:16px">Не тест — умные весы для интеллектуальной формы.</p>

---

<!-- _class: center -->

# Часть 3 · Практика и финал

<p class="lead">Каждый подключает браузер к Aisystant MCP.</p>

<p class="sub" style="margin-top:20px">Уйдёте не с обещанием «попробую потом» — с работающим подключением и первым продуктом в базе.</p>

---

<!-- _class: with-eyebrow -->

<div class="eyebrow">Блок 7 · Практика (45-48 мин)</div>

# Подключаем браузер к Aisystant MCP

<p style="font-size:1em;margin-bottom:12px"><strong>Что значит «подключить браузер к MCP»:</strong></p>

<p style="font-size:0.95em;color:#cbd5e1">Представьте: в вашем браузере есть расширение, которое знает всю методологию Aisystant. Вы пишете вопрос в Claude или ChatGPT — Claude может обратиться к Aisystant MCP как к источнику знаний. <strong>Не к памяти модели — к проверенному источнику.</strong></p>

| Шаг | Что делаем | Время |
|-----|-----------|-------|
| 1 | Открываем claude.ai или Claude Desktop | 1 мин |
| 2 | Settings → MCP Servers | 1 мин |
| 3 | Добавляем Aisystant MCP endpoint | 2 мин |
| 4 | Проверяем: задаём вопрос из своей области | 2 мин |

<p class="muted" style="font-size:0.9em;margin-top:12px">Помощник в чате параллельно ведёт тех, у кого что-то пошло не так.</p>

---

<!-- _class: with-eyebrow -->

<div class="eyebrow">Блок 7 · Упражнение (12 мин)</div>

# Запрос из вашей области

<div class="highlight-box">
<p style="font-size:1.1em;margin-bottom:8px"><strong>Напишите вопрос про вашу область — то, с чем вы работаете.</strong></p>
<p style="margin-bottom:0">Не технический, а содержательный.<br>
<em>«Что такое рабочий продукт?»</em> или<br>
<em>«Как системное мышление применяется к маркетингу?»</em></p>
</div>

<p class="muted" style="margin-top:20px;font-size:1em">Пауза 8-10 минут. Ведущий проходит по чату, помогает с техническими проблемами, комментирует интересные ответы.</p>

<p style="text-align:center;margin-top:20px;font-size:1.15em;color:#f1f5f9"><strong>Вы только что спросили не ChatGPT — вы спросили платформу Aisystant.</strong></p>

<p class="muted" style="text-align:center;font-size:0.95em">Ответ пришёл из проверенных знаний, не из общего обучения модели.</p>

---

<!-- _class: with-eyebrow -->

<div class="eyebrow">Блок 7 · Путь роста</div>

# Где вы сейчас и куда дальше

| Уровень | Что есть | Что можете |
|---------|---------|-----------|
| **0** — Голый ChatGPT | Только ИИ | Решать задачи без своего контекста |
| **1** — Браузер + Aisystant MCP <span style="color:#f97316">← ВЫ ЗДЕСЬ</span> | Контекст методологии | Спрашивать из проверенного источника |
| **2** — Минимальная IWE | 3 файла: CLAUDE.md + MEMORY.md + goals | Накапливать локально |
| **3** — IWE + команда агентов | Стратег + Экстрактор + другие | Среда работает за вас |
| **4** — Полная IWE | ~25 репо, автоматизация | Осваивать новые области системно |

<p style="text-align:center;margin-top:20px;font-size:1.1em;color:#f1f5f9">Уровень 1 — простой старт. <strong>Не нужны репозитории, не нужны агенты.</strong></p>

<p class="muted" style="text-align:center;font-size:0.95em">Просто подключение — и ваш ИИ теперь знает методологию. Это уже не голый ChatGPT.</p>

---

<!-- _class: with-eyebrow -->

<div class="eyebrow">Блок 8 · Преамбула</div>

# А что с моей профессией?

<p style="font-size:1.1em;max-width:800px;margin-top:30px"><strong>Первое мастерство — ваше текущее:</strong> юрист, инженер, HR, продавец.</p>

<p style="font-size:1.05em;max-width:800px;color:#cbd5e1">С ИИ оно меняется. Рутина забирается: типовые договоры, типовая аналитика, типовые отчёты.</p>

<p style="font-size:1.05em;max-width:800px;color:#cbd5e1">Прикладное мастерство <strong>не исчезает</strong> — оно сжимается до того, что нельзя автоматизировать.</p>

<p style="font-size:1.2em;color:#f1f5f9;margin-top:30px"><strong style="color:#f97316">IWE развивает остальные 4 мастерства</strong> — которые ИИ НЕ забирает, потому что они не про конкретную задачу, а про связку «человек — среда — мир».</p>

---

<!-- _class: with-eyebrow -->

<div class="eyebrow">Блок 8 · 4 мастерства в IWE</div>

# Что растёт с ИИ, а не вопреки

| Мастерство IWE | Что делает носитель | Аналогия |
|---|---|---|
| **1. Мыслительное** | Переводит проблему в задачу. Видит границы системы, выбирает метод. ИИ это НЕ делает за вас. | Архитектор, не строитель |
| **2. Владение IWE** | Пользоваться готовой средой: Day Open, capture, спросить через MCP. | Водитель машины |
| **3. Развитие IWE** | Наращивать среду под свои задачи: писать скиллы, скрипты, расширения. | Проектировать мастерскую под себя |
| **4. Развитие себя** | Осознанно проходить ступени мастерства. Это ЗАЧЕМ IWE существует. | Ставить цели и двигаться |

<p style="text-align:center;margin-top:20px;font-size:1.05em;color:#f1f5f9">Прикладное сжимается с ИИ. Остальные 4 — <strong>растут с ИИ, не вопреки</strong>.</p>

---

<!-- _class: with-eyebrow center -->

<div class="eyebrow">Блок 8 · Главный тезис</div>

<p class="big-label accent" style="font-size:1.7em;line-height:1.25">IWE без программы развития —<br>как мощный ноутбук без цели.</p>

<p style="font-size:1.1em;margin-top:20px;color:#f1f5f9">Всё работает, но вы не растёте.</p>

---

<!-- _class: with-eyebrow -->

<div class="eyebrow">Блок 8 · Без vs С программой развития</div>

# Что меняет программа ЛР

| Без программы | С программой ЛР |
|---|---|
| Прирост мастерства — случайный | 5 ступеней — известный путь |
| Bottleneck не закрывается, переключаетесь на лёгкое | Bottleneck диагностируется (Diagnose из Б4) |
| Через полгода — та же ступень, просто «быстрее» | Среда подстраивается под текущую ступень |
| Personal-guide не обновляется | Personal-guide + цифровой двойник обновляются |

<p class="muted" style="text-align:center;margin-top:20px;font-size:1em">5 ступеней мастерства = известный путь. Среда подстраивается под текущую — Personal-guide пересобирается, цифровой двойник обновляется.</p>

---

<!-- _class: with-eyebrow center -->

<div class="eyebrow">Блок 8 · 3 уровня одного целого</div>

<pre style="font-size:1.05em;line-height:1.8;background:#1e293b;padding:24px;border-radius:8px;color:#e2e8f0;text-align:left;display:inline-block;margin-top:20px">
<strong>Бесплатник 31 мая:</strong>    «связка человек-ИИ»  ──── <span style="color:#f97316">ЧТО</span>
                            ↓
<strong>Платник 7 июня:</strong>       «как собрать среду»  ──── <span style="color:#f97316">КАК</span>
                            ↓
<strong>Программа ЛР:</strong>         «куда расти»         ──── <span style="color:#f97316">ЗАЧЕМ</span>
</pre>

<p class="big-label accent" style="font-size:1.5em;margin-top:30px"><strong>IWE — носитель.<br>ЛР — направление.</strong></p>

---

<!-- _class: with-eyebrow -->

<div class="eyebrow">Блок 8 · Резюме</div>

# Куда вы пришли за 150 минут

| | <span class="muted">ИИ-Ассистент</span> | <span style="color:#f97316">ИВЕ/Экзокортекс</span> |
|---|---|---|
| Управление | Вы управляете ИИ | ИИ — часть вашего мышления |
| Память | Чужая (или её нет) | Ваша, копится и растёт |
| Качество | Галлюцинирует | Работает с проверенным знанием |
| Архитектура | Один на всё | Команда специалистов |
| Класс | Инструмент | Среда |

<p style="text-align:center;margin-top:20px;font-size:1.1em;color:#f1f5f9"><strong>Контур тот же — что был на бесплатнике 31 мая.</strong></p>

<p class="muted" style="text-align:center;font-size:0.95em">Но вместо «я должен помнить» — среда помнит за вас.</p>

---

<!-- _class: with-eyebrow center -->

<div class="eyebrow">Блок 8 · Мост к ЛР</div>

<p class="big-label accent" style="font-size:1.5em;line-height:1.3">Среда настроена.<br>Теперь вопрос — <strong>куда двигаться.</strong></p>

<p class="muted" style="font-size:1.1em;margin-top:24px;max-width:780px">Без ответа IWE будет <strong>мощным ноутбуком без цели</strong>, не больше.</p>

---

<!-- _class: with-eyebrow -->

<div class="eyebrow">Блок 8 · Два пути дальше</div>

# Регистрация — 14 июня старт

<div class="cards-2" style="margin-top:30px">

<div class="card accent">
<span class="num">Путь 1 · С поддержкой</span>
<h3>Программа Личного Развития</h3>
<p>Экзокортекс усилит любую программу. 5 ступеней, известный путь, обратная связь, среда сопроизводителей.</p>
<p class="muted" style="font-size:0.9em">Старт 14 июня · регистрация открыта</p>
</div>

<div class="card muted">
<span class="num">Путь 2 · Самостоятельно</span>
<h3>IWE с нуля</h3>
<p>Шаблон на GitHub + @aist_me_bot для ежедневной поддержки. Подходит для тех, кто хочет собирать сам.</p>
<p class="muted" style="font-size:0.9em">github.com/aisystant/FMT-exocortex-template</p>
</div>

</div>

<p style="text-align:center;margin-top:24px;font-size:1.1em;color:#f1f5f9">Вы только что прошли путь с уровня 0 до уровня 1. Куда дальше — выбирайте.</p>

---

<!-- _class: title -->
<!-- _paginate: false -->
<!-- _header: "" -->
<!-- _footer: "" -->

# Q&A

<div class="speaker" style="font-size:1.5em;margin-top:40px">
Спасибо!
</div>

<div class="meta" style="margin-top:40px">Регистрация на ЛР · @aist_me_bot · github.com/aisystant</div>

<div class="meta" style="margin-top:8px;font-size:0.85em;color:#94a3b8">Запись и материалы — придут на email участникам</div>
