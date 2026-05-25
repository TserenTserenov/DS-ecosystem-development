# Bug: ДЗ-чекер возвращает пустой ответ

**Дата:** 2026-05-25  
**Система:** AISYS.008 ДЗ-чекер (n8n workflow)  
**Статус:** 🔴 Активный баг — требует апгрейда n8n cloud плана

---

## Симптом

`POST https://tseren.app.n8n.cloud/webhook/check` возвращает:
```
HTTP 200
Content-Length: 0
(пустое тело)
```

Время ответа ~200-300мс — в 10-30 раз быстрее нормального выполнения (guides-mcp + Haiku = 3-10 сек).

## Диагностика

| Проверка | Результат |
|---------|-----------|
| guides-mcp жив? | ✅ `semantic_search` отвечает корректно |
| OpenAI API в guides-mcp? | ✅ embeddings возвращаются |
| n8n workflow код правильный? | ✅ Исправлен и задеплоен 2026-05-25 |
| n8n исполнение запускается? | ❌ **НЕТ — лимит плана исчерпан** |

**Вывод:** n8n cloud план достиг лимита исполнений. Каждый запрос отклоняется на уровне Webhook node ещё до запуска workflow.

Из логов n8n executions (execution #6858):
```
"Execution limit reached. Consider upgrading your plan"
```

## Исправление (требует действия в n8n cloud)

**Вариант A — апгрейд плана:**
1. Открыть `https://app.n8n.cloud/account/change-plan`
2. Выбрать план с бо́льшим лимитом исполнений

**Вариант B — ждать сброса лимита:**
Лимит сбрасывается 1-го числа следующего месяца (1 июня 2026).

## Дополнительные исправления (уже задеплоены, вступят в силу после разблокировки)

Пока разбирались с симптомом, в workflow были обнаружены и устранены два бага:

### Баг 1: r.heading → r.section || r.guide || r.filename
В `Build Prompt` node использовалось поле `r.heading`, которое guides-mcp не возвращает.
guides-mcp возвращает `section`/`guide`/`filename`. Все заголовки чанков отображались как `undefined`.

**Исправлено:** коммит `2e5545c` в репо + задеплоено в n8n cloud 2026-05-25.

### Баг 2: IF ok? FALSE ветка → Respond to Webhook (race condition с v1 execution order)
С `settings.executionOrder: "v1"` и IF FALSE ветка, подключённая к тому же `Respond to Webhook` что и основной pipeline:
n8n v1 выполнял FALSE ветку (0 элементов) немедленно, что тригерило `Respond to Webhook` с пустым body до того, как основной pipeline завершался.

**Исправлено:** добавлен отдельный `respond-error-001` "Respond Error" node для IF FALSE ветки.
Задеплоено в n8n cloud 2026-05-25 (версия `814e3065-78a7-4192-8005-6c9f3e103131`).

## Что НЕ является причиной

- guides-mcp: работает корректно
- OpenAI API: работает (embeddings возвращаются)
- Anthropic API (Haiku): нет причин подозревать (до лимита workflow работал)
- Код workflow: исправлен и задеплоен
