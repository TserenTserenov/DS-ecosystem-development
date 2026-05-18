# Bug: docs pre-commit блокирует коммит — сломанные ontology_anchor ссылки

**Дата:** 2026-05-18
**Репо:** aisystant/docs
**Файлы:** docs/ru/personal-design/1-2-self-development-methods/s2-time-investment/2.01-2.04.md

## Симптом

Pre-commit хук `[1/4] Checking broken cross-repo links` падает с exit 1.
Файлы 2.01-2.04.md содержат `ontology_anchor` ссылки на PACK-personal/ontology.md
(добавлены через sync-guide-to-ontology.py сегодня), но якоря не найдены в онтологии.

## Примеры сломанных ссылок

```
ontology_anchor: ../../../PACK-personal/ontology.md#инвестирование-времени
ontology_anchor: ../../../PACK-personal/ontology.md#трата-времени
ontology_anchor: ../../../PACK-personal/ontology.md#5-классов-работ
```

## Вероятная причина

PACK-personal/ontology.md расширен сегодня (v3-v5, ~60 новых понятий).
Якоря добавлены через sync-guide-to-ontology.py, но часть хешей markdown не совпадает
с реальными заголовками (русские символы, цифры в начале).

## Статус

Изменения в 2.01-2.04.md НЕ закоммичены (хук заблокировал, S-33 не обходить).
Файлы остаются modified в docs (unstaged).

## Следующий шаг

Проверить реальные якоря: `grep "^## " ~/IWE/PACK-personal/ontology.md | head -30`
Или запустить `sync-guide-to-ontology.py --validate` для автоисправления.
