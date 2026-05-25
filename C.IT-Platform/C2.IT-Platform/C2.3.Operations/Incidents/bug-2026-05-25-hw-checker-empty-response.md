# Bug: ДЗ-чекер возвращает пустой ответ

**Дата:** 2026-05-25  
**Система:** AISYS.008 ДЗ-чекер (n8n workflow)  
**Статус:** 🔴 Активный баг — требует ручного действия в n8n cloud

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
| Anthropic Haiku API? | Не проверено (требует n8n логов) |
| Репо-файл `n8n-workflow-v3.json` правильный? | ✅ `responseMode: responseNode`, `respondWith: json` |
| Deployed workflow = репо? | ❌ **НЕ СОВПАДАЕТ** — 200мс vs ожидаемых 3-10 сек |

**Вывод:** n8n workflow был изменён в UI без сохранения в JSON-файл репо. Deployed workflow расходится с `n8n-workflow-v3.json`.

## Исправление (требует доступа к n8n cloud)

1. Открыть `https://tseren.app.n8n.cloud` → Workflows
2. Найти workflow с path `check`
3. Проверить `Respond to Webhook` node → поле `Respond With`  
   Должно быть: `"json"`, `Response Body` = `={{ $json.body ?? $json }}`  
   Если другое — исправить или переимпортировать
4. **Рекомендуется:** сделать Export workflow из n8n UI и сравнить с `hw-checker/n8n-workflow-v3.json`
5. **Если расхождение большое:** удалить текущий workflow, импортировать `n8n-workflow-v3.json` из репо, активировать

## Дополнительный баг (исправлен в репо, нужен реимпорт)

В `Build Prompt` node был баг: `r.heading` → guides-mcp не возвращает поле `heading`, возвращает `section`/`guide`/`filename`. Все результаты поиска показывались как `[score=0.85] undefined:\n<content>`.

**Исправлено в коммите (сегодня):** `r.heading` → `r.section || r.guide || r.filename`

После реимпорта workflow из репо этот баг тоже будет исправлен.

## Что НЕ является причиной

- guides-mcp: работает корректно
- OpenAI API: работает (embeddings возвращаются)
- Anthropic API: не проверялось, но даже при отказе `Parse + Format` должен вернуть fallback-ответ с `comment: "Нет ответа от модели"` — не пустой body
