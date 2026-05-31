#!/usr/bin/env python3
"""
Генератор автоматических отчётов по хранилищу знаний.

Использование:
    python3 .ops/build_report.py --report architecture-snapshot
    python3 .ops/build_report.py --report content-completeness
    python3 .ops/build_report.py --report technical-issues
    python3 .ops/build_report.py --report all

    # С AI-анализом (требует OPENROUTER_API_KEY)
    python3 .ops/build_report.py --report terminology --ai-analysis
    python3 .ops/build_report.py --report recommendations --ai-analysis

Типы отчётов:
    architecture-snapshot   - Архитектурный слепок хранилища
    content-completeness    - Содержательная полнота описания
    technical-issues        - Противоречия и несогласованности хранилища
    terminology             - Терминологическая согласованность (AI)
    recommendations         - Рекомендации по развитию (AI)
    links-map               - Карта связей между документами
    all                     - Все отчёты

Флаги:
    --ai-analysis           - Использовать Claude для AI-анализа
    --dry-run               - Не сохранять файлы, только вывести
    --output, -o            - Указать путь для сохранения
"""

import os
import re
import sys
import json
import yaml
import argparse
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Optional, Tuple, Any

# Загрузка переменных окружения из .env файла
try:
    from dotenv import load_dotenv
    load_dotenv()  # Загружает .env из корня проекта
except ImportError:
    pass  # python-dotenv не установлен, используем переменные окружения

# Опциональная поддержка AI-анализа
try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

# Константы
CONTENT_DIR = Path("content")
REPORTS_DIR = CONTENT_DIR / "0. Управление" / "0.4. Автоматические отчёты ИИ" / "0.4.2. Актуальные автоматические отчеты"

# Семейства документов F0-F9
FAMILIES = {
    "F0": {"name": "Управление", "level": "Метасистема", "role": "-", "section": "0"},
    "F1": {"name": "Видение и привлечение", "level": "Мир", "role": "Предприниматель", "section": "1.1"},
    "F2": {"name": "Контекст и интерфейсы", "level": "Мир", "role": "Инженер", "section": "1.2"},
    "F3": {"name": "Репутация и партнёрства", "level": "Мир", "role": "Менеджер", "section": "1.3"},
    "F4": {"name": "Ценность и бизнес-модели", "level": "Созидатель", "role": "Предприниматель", "section": "2.1"},
    "F5": {"name": "Модель и компетенции", "level": "Созидатель", "role": "Инженер", "section": "2.2"},
    "F6": {"name": "Путь и сопровождение", "level": "Созидатель", "role": "Менеджер", "section": "2.3"},
    "F7": {"name": "Экономика и инвестиции", "level": "Экосистема", "role": "Предприниматель", "section": "3.1"},
    "F8": {"name": "Платформа и подсистемы", "level": "Экосистема", "role": "Инженер", "section": "3.2"},
    "F9": {"name": "Команда и службы", "level": "Экосистема", "role": "Менеджер", "section": "3.3"},
}

# OpenRouter конфигурация для AI-анализа (WP-366 Ф4.E)
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
AI_MODEL = "moonshotai/kimi-k2"
AI_MAX_TOKENS = 4096


class AIAnalyzer:
    """Класс для AI-анализа документов через OpenRouter (WP-366 Ф4.E)."""

    def __init__(self):
        if not HAS_HTTPX:
            raise RuntimeError(
                "Для AI-анализа требуется библиотека httpx.\n"
                "Установите: pip install httpx"
            )

        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError(
                "Не установлена переменная окружения OPENROUTER_API_KEY.\n"
                "Получите ключ на https://openrouter.ai/"
            )

        self.api_key = api_key

    def analyze(self, prompt: str, context: str, max_tokens: int = AI_MAX_TOKENS) -> str:
        """Выполнение AI-анализа через OpenRouter."""
        payload = {
            "model": AI_MODEL,
            "max_tokens": max_tokens,
            "messages": [
                {
                    "role": "user",
                    "content": f"{prompt}\n\n---\n\nКонтекст:\n{context}"
                }
            ]
        }
        try:
            resp = httpx.post(
                OPENROUTER_API_URL,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://iwe.local",
                    "X-Title": "IWE-AI-Reports",
                },
                json=payload,
                timeout=120,
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            return f"*Ошибка AI-анализа: {e}*"

    def analyze_terminology(self, documents: List['Document']) -> str:
        """Анализ терминологической согласованности."""
        # Собираем определения терминов из документов
        terms_context = self._extract_terms_context(documents)

        prompt = """Проанализируй терминологическую согласованность документов хранилища знаний.

Задачи:
1. Найди термины, которые используются с разными определениями в разных документах
2. Найди термины, которые упоминаются без явного определения
3. Найди синонимы/вариации терминов (одно понятие - разные названия)
4. Оцени общую терминологическую согласованность

Формат ответа в Markdown:

## Тепловая карта терминологии

| Категория | Количество | Статус |
|-----------|------------|--------|
| Согласованные термины | N | 🟢 |
| Термины с вариациями | N | 🟡 |
| Термины с конфликтами определений | N | 🔴 |

## 1. Термины с конфликтами определений

### 1.1. [TERM-001] «Название термина»
**Определения:**
- Документ A: определение 1
- Документ B: определение 2

**Рекомендация:** ...

## 2. Термины с вариациями (синонимы)

| Основной термин | Вариации | Документы |
|-----------------|----------|-----------|
| ... | ... | ... |

## 3. Термины без определений

- Термин 1 (упоминается в: док1, док2)
- Термин 2 (упоминается в: док3)

## 4. Рекомендации по унификации

1. ...
2. ...
"""

        return self.analyze(prompt, terms_context)

    def analyze_recommendations(self, documents: List['Document'], by_family: Dict[str, List['Document']]) -> str:
        """Генерация рекомендаций по развитию хранилища."""
        # Собираем статистику
        stats_context = self._build_stats_context(documents, by_family)

        prompt = """Проанализируй состояние хранилища знаний и сформируй рекомендации по его развитию.

Задачи:
1. Оцени полноту покрытия тем по матрице 3×3 (Мир/Созидатель/Экосистема × Предприниматель/Инженер/Менеджер)
2. Найди критические пробелы в документации
3. Выяви документы, требующие обновления или расширения
4. Предложи приоритизированный план развития

Формат ответа в Markdown:

## Executive Summary

Краткий обзор состояния хранилища (2-3 предложения).

## 1. Критические пробелы 🔴

### 1.1. [GAP-001] Название пробела
**Описание:** ...
**Влияние:** ...
**Рекомендуемые документы для создания:**
- Документ 1
- Документ 2

## 2. Важные улучшения 🟡

### 2.1. [IMP-001] Название улучшения
**Описание:** ...
**Документы для обновления:**
- [[Документ]] — что добавить

## 3. План развития по приоритетам

### Приоритет 1 (критично)
1. ...
2. ...

### Приоритет 2 (важно)
1. ...
2. ...

### Приоритет 3 (желательно)
1. ...

## 4. Метрики для отслеживания

| Метрика | Текущее | Целевое |
|---------|---------|---------|
| ... | ... | ... |
"""

        return self.analyze(prompt, stats_context)

    def _extract_terms_context(self, documents: List['Document']) -> str:
        """Извлечение контекста терминов из документов."""
        context_parts = []

        # Ищем документы с определениями (глоссарии, концепции)
        priority_patterns = ["глоссарий", "термин", "определени", "концепц", "понятие"]

        # Сначала приоритетные документы
        priority_docs = []
        other_docs = []

        for doc in documents:
            name_lower = doc.name.lower()
            if any(p in name_lower for p in priority_patterns):
                priority_docs.append(doc)
            else:
                other_docs.append(doc)

        # Добавляем приоритетные полностью
        for doc in priority_docs[:10]:
            context_parts.append(f"### {doc.name}\n\n{doc.body[:3000]}")

        # Добавляем выдержки из остальных
        for doc in other_docs[:30]:
            # Ищем определения (паттерны типа "X — это Y" или "X: Y")
            definitions = re.findall(
                r'(?:^|\n)([А-ЯЁA-Z][а-яёa-zA-Z\s]+?)(?:\s*[—–-]\s*|\s*:\s*)([^\n]{20,200})',
                doc.body
            )
            if definitions:
                context_parts.append(f"### {doc.name}\n")
                for term, definition in definitions[:5]:
                    context_parts.append(f"- **{term.strip()}**: {definition.strip()}")

        return "\n\n".join(context_parts)[:15000]  # Ограничиваем контекст

    def _build_stats_context(self, documents: List['Document'], by_family: Dict[str, List['Document']]) -> str:
        """Построение контекста статистики для рекомендаций."""
        context = f"## Статистика хранилища\n\n"
        context += f"- Всего документов: {len(documents)}\n"

        for family, docs in sorted(by_family.items()):
            context += f"- {family}: {len(docs)} документов\n"

        context += "\n## Документы по семействам\n\n"

        for family, docs in sorted(by_family.items()):
            context += f"### {family}\n"
            for doc in docs[:10]:
                status = "✅" if not doc.is_empty else "⚠️ пустой"
                context += f"- {doc.name} ({status})\n"
            if len(docs) > 10:
                context += f"- ... и ещё {len(docs) - 10}\n"
            context += "\n"

        context += "\n## Пустые/незаполненные документы\n\n"
        empty_docs = [d for d in documents if d.is_empty]
        for doc in empty_docs[:20]:
            context += f"- {doc.name}\n"

        return context[:15000]


# Соответствие папок семействам
FOLDER_TO_FAMILY = {
    "0. Управление": "F0",
    "1. Мир (Надсистема)": None,  # Определяется по подпапке
    "1.1.": "F1",
    "1.2.": "F2",
    "1.3.": "F3",
    "2. Созидатель (Целевая система)": None,
    "2.1.": "F4",
    "2.2.": "F5",
    "2.3.": "F6",
    "3. Экосистема развития (Система создания)": None,
    "3.1.": "F7",
    "3.2.": "F8",
    "3.3.": "F9",
}


class Document:
    """Представление документа хранилища."""

    def __init__(self, path: Path):
        self.path = path
        self.relative_path = path.relative_to(CONTENT_DIR) if path.is_relative_to(CONTENT_DIR) else path
        self.name = path.stem
        self.content = ""
        self.frontmatter: Dict[str, Any] = {}
        self.body = ""
        self.wikilinks: List[str] = []
        self.headings: List[Tuple[int, str]] = []
        self.family: Optional[str] = None
        self.size = 0
        self._parse()

    def _parse(self):
        """Парсинг документа: frontmatter, контент, ссылки."""
        try:
            self.content = self.path.read_text(encoding="utf-8")
            self.size = len(self.content)
        except Exception as e:
            print(f"⚠️  Ошибка чтения {self.path}: {e}")
            return

        # Парсинг frontmatter
        if self.content.startswith("---"):
            parts = self.content.split("---", 2)
            if len(parts) >= 3:
                try:
                    self.frontmatter = yaml.safe_load(parts[1]) or {}
                except yaml.YAMLError:
                    self.frontmatter = {}
                self.body = parts[2].strip()
            else:
                self.body = self.content
        else:
            self.body = self.content

        # Извлечение wikilinks
        self.wikilinks = re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', self.body)

        # Извлечение заголовков
        self.headings = [(len(m.group(1)), m.group(2))
                         for m in re.finditer(r'^(#{1,6})\s+(.+)$', self.body, re.MULTILINE)]

        # Определение семейства
        self.family = self._detect_family()

    def _detect_family(self) -> Optional[str]:
        """Определение семейства документа по пути и frontmatter."""
        # Приоритет: frontmatter
        if "family" in self.frontmatter:
            return self.frontmatter["family"]

        # По пути
        path_str = str(self.relative_path)
        path_segments = path_str.split("/")

        for pattern, family in FOLDER_TO_FAMILY.items():
            if pattern in path_str:
                if family:
                    return family
                # Для корневых папок смотрим подпапку
                # ВАЖНО: Проверяем, что паттерн находится В НАЧАЛЕ сегмента пути,
                # а не просто как подстрока (иначе "1.1.3." ошибочно матчится на "1.3.")
                # Сортируем в обратном порядке для корректного приоритета (3.3. > 3.2. > 3.1.)
                sorted_patterns = sorted(FOLDER_TO_FAMILY.items(), key=lambda x: x[0], reverse=True)
                for sub_pattern, sub_family in sorted_patterns:
                    if sub_family:
                        # Проверяем, что какой-то сегмент пути НАЧИНАЕТСЯ с паттерна
                        for segment in path_segments:
                            if segment.startswith(sub_pattern):
                                return sub_family

        return None

    @property
    def is_empty(self) -> bool:
        """Документ считается пустым, если контент < 200 символов или содержит только TODO."""
        body_clean = re.sub(r'<!--.*?-->', '', self.body, flags=re.DOTALL)
        body_clean = re.sub(r'TODO|FIXME', '', body_clean, flags=re.IGNORECASE)
        return len(body_clean.strip()) < 200

    @property
    def is_full(self) -> bool:
        """
        Документ считается полным согласно обновленным ТЗ:
        - >500 слов реального содержания
        - Структурированное изложение (≥3 заголовков)
        - Есть примеры (числа/метрики) ИЛИ диаграммы/таблицы
        - Не является заглушкой (<10% TODO/TBD)
        - Есть связи с другими документами
        """
        # Критерий 1: Объем >500 слов
        word_count = len(self.body.split())
        if word_count < 500:
            return False

        # Критерий 2: Структура (≥3 заголовков)
        if len(self.headings) < 3:
            return False

        # Критерий 3: Есть примеры (числа) ИЛИ визуализация (таблицы/диаграммы)
        has_numbers = bool(re.search(r'\d+[.,]?\d*\s*(%|руб|USD|слов|документов|человек)', self.body))
        has_tables = bool(re.search(r'\|.*\|.*\|', self.body))  # Markdown таблицы
        has_diagrams = bool(re.search(r'```(mermaid|plantuml|graphviz)', self.body, re.IGNORECASE))
        has_examples = has_numbers or has_tables or has_diagrams
        if not has_examples:
            return False

        # Критерий 4: Не заглушка (<10% TODO/TBD)
        todo_count = len(re.findall(r'TODO|TBD|FIXME|\.\.\.', self.body, re.IGNORECASE))
        total_lines = len(self.body.split('\n'))
        if total_lines > 0 and (todo_count / total_lines) > 0.1:
            return False

        # Критерий 5: Есть связи (wikilinks)
        if len(self.wikilinks) == 0:
            return False

        return True

    @property
    def status(self) -> str:
        return self.frontmatter.get("status", "unknown")

    @property
    def doc_type(self) -> str:
        return self.frontmatter.get("type", "unknown")


class ReportGenerator:
    """Базовый класс для генерации отчётов."""

    def __init__(self, ai_analyzer: Optional[AIAnalyzer] = None):
        self.documents: List[Document] = []
        self.by_family: Dict[str, List[Document]] = defaultdict(list)
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.git_hash = self._get_git_hash()
        self.ai_analyzer = ai_analyzer

    def _get_git_hash(self) -> str:
        """Получение текущего git commit hash."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except:
            return "unknown"

    def _get_weekly_growth_metrics(self) -> List[Dict[str, Any]]:
        """Получение метрик роста репозитория за последние 4 недели.

        Возвращает список словарей с метриками для каждой недели:
        - week: номер недели (W-4, W-3, W-2, W-1) или "Сейчас"
        - date: дата последнего коммита недели
        - files: количество .md файлов
        - lines: количество строк
        - chars: количество символов

        Если история git короче 4 недель, использует первый коммит как начальную точку.
        """
        from datetime import timedelta

        metrics = []
        today = datetime.now()

        # Получаем дату первого коммита для определения доступной истории
        try:
            result = subprocess.run(
                ["git", "log", "--reverse", "--format=%ad", "--date=short", "-1"],
                capture_output=True, text=True, check=True
            )
            first_commit_date_str = result.stdout.strip()
            if first_commit_date_str:
                first_commit_date = datetime.strptime(first_commit_date_str, "%Y-%m-%d")
            else:
                return []
        except:
            return []

        # Определяем начальную дату для анализа (не раньше первого коммита)
        four_weeks_ago = today - timedelta(weeks=4)
        start_date = max(first_commit_date, four_weeks_ago)

        # Вычисляем количество недель для анализа
        days_available = (today - start_date).days
        weeks_available = min(4, max(1, days_available // 7 + 1))

        for week_offset in range(weeks_available, 0, -1):
            # Дата конца недели (N недель назад от сегодня)
            target_date = today - timedelta(weeks=week_offset)

            # Если целевая дата раньше первого коммита, используем первый коммит
            if target_date < first_commit_date:
                target_date = first_commit_date

            date_str = target_date.strftime("%Y-%m-%d")

            try:
                # Получаем последний коммит до этой даты
                result = subprocess.run(
                    ["git", "log", f"--until={date_str} 23:59:59", "--format=%H", "-1"],
                    capture_output=True, text=True, check=True
                )
                commit_hash = result.stdout.strip()

                if not commit_hash:
                    continue

                # Получаем список .md файлов в content/ на этот коммит
                # Используем -c core.quotepath=false для корректной работы с кириллицей
                result = subprocess.run(
                    f"git -c core.quotepath=false ls-tree -r --name-only {commit_hash} -- content/ | grep '\\.md$'",
                    shell=True, capture_output=True, text=True
                )
                md_files = [f for f in result.stdout.strip().split('\n') if f]

                total_files = len(md_files)
                total_lines = 0
                total_chars = 0

                # Подсчитываем строки и символы
                for file_path in md_files:
                    try:
                        result = subprocess.run(
                            ["git", "show", f"{commit_hash}:{file_path}"],
                            capture_output=True, text=True
                        )
                        if result.returncode == 0:
                            content = result.stdout
                            total_lines += len(content.split('\n'))
                            total_chars += len(content)
                    except:
                        pass

                metrics.append({
                    'week': f"W-{week_offset}",
                    'date': date_str,
                    'files': total_files,
                    'lines': total_lines,
                    'chars': total_chars
                })
            except Exception as e:
                continue

        # Добавляем текущее состояние (Сейчас)
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True, text=True, check=True
            )
            commit_hash = result.stdout.strip()

            # Используем -c core.quotepath=false для корректной работы с кириллицей
            result = subprocess.run(
                f"git -c core.quotepath=false ls-tree -r --name-only {commit_hash} -- content/ | grep '\\.md$'",
                shell=True, capture_output=True, text=True
            )
            md_files = [f for f in result.stdout.strip().split('\n') if f]

            total_files = len(md_files)
            total_lines = 0
            total_chars = 0

            for file_path in md_files:
                try:
                    result = subprocess.run(
                        ["git", "show", f"{commit_hash}:{file_path}"],
                        capture_output=True, text=True
                    )
                    if result.returncode == 0:
                        content = result.stdout
                        total_lines += len(content.split('\n'))
                        total_chars += len(content)
                except:
                    pass

            metrics.append({
                'week': "Сейчас",
                'date': today.strftime("%Y-%m-%d"),
                'files': total_files,
                'lines': total_lines,
                'chars': total_chars
            })
        except:
            pass

        return metrics

    def scan_documents(self):
        """Сканирование всех документов в хранилище."""
        print("📂 Сканирование документов...")

        for md_file in CONTENT_DIR.rglob("*.md"):
            # Пропускаем служебные файлы
            if any(skip in str(md_file) for skip in [".obsidian", "node_modules", ".git"]):
                continue

            doc = Document(md_file)
            self.documents.append(doc)

            if doc.family:
                self.by_family[doc.family].append(doc)

        print(f"   Найдено документов: {len(self.documents)}")
        for family, docs in sorted(self.by_family.items()):
            print(f"   {family}: {len(docs)}")

    def generate(self, report_type: str) -> str:
        """Генерация отчёта указанного типа."""
        generators = {
            "architecture-snapshot": self._generate_architecture_snapshot,
            "content-completeness": self._generate_content_completeness,
            "technical-issues": self._generate_technical_issues,
            "terminology": self._generate_terminology,
            "recommendations": self._generate_recommendations,
            "links-map": self._generate_links_map,
        }

        if report_type not in generators:
            raise ValueError(f"Неизвестный тип отчёта: {report_type}")

        return generators[report_type]()

    def _header(self, title: str, extra: str = "") -> str:
        """Заголовок отчёта."""
        return f"""# {title}

> Автоматически сформирован: {self.timestamp}
> Проанализировано документов: {len(self.documents)}
> Версия хранилища: {self.git_hash}
{extra}
---

"""

    # ==================== АРХИТЕКТУРНЫЙ СЛЕПОК ====================

    def _generate_architecture_snapshot(self) -> str:
        """Генерация отчёта 'Архитектурный слепок хранилища'."""
        report = self._header(
            "Архитектурный слепок хранилища",
            "\n**Структура документа**: Иерархическая — соответствует логике описания экосистемы от целей к реализации.\n"
        )

        # Тепловая карта разделов
        report += self._architecture_heatmap()

        # Разделы
        report += self._architecture_section_1_mission()
        report += self._architecture_section_2_personas()
        report += self._architecture_section_3_goals()
        report += self._architecture_section_4_creator()
        report += self._architecture_section_5_functioning()
        report += self._architecture_section_6_platform()
        report += self._architecture_section_7_data()
        report += self._architecture_section_8_epistemic()
        report += self._architecture_section_9_economy()
        report += self._architecture_section_10_quality()
        report += self._architecture_section_11_metrics()
        report += self._architecture_section_12_stats()
        report += self._architecture_section_13_links()

        return report

    def _check_main_question_coverage(self, family_id: str, docs: list, main_question: str) -> bool:
        """
        Проверяет, раскрыт ли главный вопрос семейства в документах.

        Критерий: хотя бы один полный документ содержит детальный ответ на главный вопрос
        (>3 абзацев с примерами и структурой)
        """
        if not main_question or not docs:
            return False

        # Извлекаем ключевые слова из вопроса
        question_keywords = set(re.findall(r'\w+', main_question.lower()))
        question_keywords -= {'как', 'что', 'зачем', 'для', 'кого', 'это', 'устроен', 'устроена', 'устроено'}

        for doc in docs:
            if not doc.is_full:
                continue

            # Подсчитываем абзацы
            paragraphs = [p.strip() for p in doc.body.split('\n\n') if len(p.strip()) > 100]
            if len(paragraphs) < 3:
                continue

            # Проверяем наличие ключевых слов вопроса в содержании
            body_lower = doc.body.lower()
            matches = sum(1 for keyword in question_keywords if keyword in body_lower)

            # Если хотя бы 50% ключевых слов найдены и есть структура
            if matches >= len(question_keywords) * 0.5 and len(doc.headings) >= 3:
                return True

        return False

    def _architecture_heatmap(self) -> str:
        """Тепловая карта по семействам F0-F9 согласно ТЗ Архитектурный слепок 0.4.1."""

        # Типичные документы для проверки по каждому семейству (из ТЗ)
        typical_docs = {
            "F0": ["модель семейств", "стандарт", "глоссарий", "классификац"],
            "F1": ["манифест", "проблем", "целев", "jtbd", "аудитор"],
            "F2": ["концепция использования", "сценари", "контекст", "диаграмм"],
            "F3": ["коммуникац", "партнёр", "регулятор", "compliance"],
            "F4": ["ценностн", "трансформац", "бизнес-модел", "оффер"],
            "F5": ["созидател", "компетенц", "мастерств", "модель"],
            "F6": ["онбординг", "маршрут", "деканат", "метрик"],
            "F7": ["экономик", "токеномик", "инвестиц"],
            "F8": ["платформ", "архитектур", "систем", "ассистент"],
            "F9": ["рол", "ритм", "служб", "команд", "эксплуатац"],
        }

        # Главные вопросы семейств (из Модели семейств документов 0.1)
        main_questions = {
            "F0": "Как устроены правила и онтология?",
            "F1": "Зачем миру эта экосистема?",
            "F2": "Как созидатель встраивается в мир?",
            "F3": "Как работаем с внешним миром?",
            "F4": "Какую ценность получает созидатель?",
            "F5": "Как устроен созидатель?",
            "F6": "Как происходит развитие созидателя?",
            "F7": "Как устроена экономика экосистемы?",
            "F8": "Как устроена платформа?",
            "F9": "Как работает команда?",
        }

        heatmap = "## Тепловая карта по семействам документов\n\n"
        heatmap += "| Семейство | Название | Статус | Документов | Комментарий |\n"
        heatmap += "|-----------|----------|--------|------------|-------------|\n"

        status_counts = {"🟢": 0, "🟡": 0, "🔴": 0}

        for family_id in ["F0", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9"]:
            family = FAMILIES[family_id]
            docs = self.by_family.get(family_id, [])
            count = len(docs)

            # Анализ СОДЕРЖАНИЯ документов согласно обновленному ТЗ 0.4.1
            # Критерии полноты: >500 слов + структура + примеры + диаграммы + связи
            typical_patterns = typical_docs.get(family_id, [])
            full_docs_count = 0  # Документы, удовлетворяющие is_full
            typical_full_docs = 0  # Типичные документы, которые полные

            for doc in docs:
                # Проверяем полноту документа (используем is_full property)
                if doc.is_full:
                    full_docs_count += 1

                    # Проверяем, является ли документ типичным для семейства
                    doc_name_lower = doc.name.lower()
                    for pattern in typical_patterns:
                        if pattern in doc_name_lower:
                            typical_full_docs += 1
                            break  # Один документ может соответствовать только одному паттерну

            # Оценка статуса согласно ОБНОВЛЕННОМУ ТЗ (п. 2.1)
            # Главный критерий: процент ПОЛНЫХ типичных документов
            # 🟢 Полный: ≥80% типичных документов полные (>500 слов + структура + примеры + диаграммы + связи)
            # 🟡 Частичный: 50-79% типичных документов полные
            # 🔴 Минимальный (ПО УМОЛЧАНИЮ): <50% типичных документов полные

            typical_count = len(typical_patterns)
            full_ratio = full_docs_count / count if count > 0 else 0
            typical_full_ratio = typical_full_docs / typical_count if typical_count > 0 else 0

            # Проверяем главный вопрос семейства (анализ содержания)
            main_question_covered = self._check_main_question_coverage(family_id, docs, main_questions.get(family_id, ""))

            # Проверяем процент документов со связями
            docs_with_links = sum(1 for doc in docs if len(doc.wikilinks) > 0)
            links_ratio = docs_with_links / count if count > 0 else 0

            # Критерии статуса:
            # 🟢 Полный: ≥80% документов полные
            # 🟡 Частичный: 50-79% документов полные
            # 🔴 Минимальный: <50% документов полные

            if full_ratio >= 0.8:
                status = "🟢"
                comment = f"{int(full_ratio*100)}% документов полные"
                # Добавляем информацию о связях и главном вопросе, если они выполнены
                if main_question_covered and links_ratio >= 0.7:
                    comment += ", главный вопрос раскрыт"
            elif full_ratio >= 0.5:
                status = "🟡"
                comment = f"{int(full_ratio*100)}% документов полные"
            else:
                status = "🔴"
                if count == 0:
                    comment = "Документы отсутствуют"
                elif full_docs_count == 0:
                    comment = "Нет полных документов (только заглушки/TODO)"
                else:
                    comment = f"Только {int(full_ratio*100)}% документов полные (требуется ≥50%)"

            status_counts[status] += 1
            heatmap += f"| {family_id} | {family['name']} | {status} | {count} | {comment} |\n"

        heatmap += f"\n**Общий статус:** 🟢 {status_counts['🟢']} | 🟡 {status_counts['🟡']} | 🔴 {status_counts['🔴']}\n"

        return heatmap + "\n---\n\n"

    def _architecture_section_1_mission(self) -> str:
        """Раздел 1: Зачем, для кого, что мы делаем."""
        section = "## 1. Зачем, для кого, что мы делаем\n\n"

        # Ищем манифест
        manifesto = self._find_doc_by_pattern("Манифест")
        if manifesto:
            section += "### 1.1. Миссия экосистемы\n\n"
            section += self._extract_summary(manifesto, max_sentences=3)
            section += "\n\n"

        section += "### 1.2. Три инварианта (конституционный слой)\n\n"
        section += "- **Эволюционность** — любой процесс способен к непрерывному улучшению через циклы обратной связи\n"
        section += "- **Сквозная целостность** — от личных целей до глобальных систем единая трассировка\n"
        section += "- **Дидактическая прозрачность** — каждый артефакт показывает свою причинно-следственную дорожку\n\n"

        section += "### 1.3. Принципы реализации\n\n"
        section += "- C4+ADR для архитектурного описания\n"
        section += "- Минимально достаточная документация\n"
        section += "- Разделение Method / MethodDescription / Work\n\n"

        sources = [d.name for d in self.by_family.get("F1", [])[:3]]
        section += f"**Источники:** {', '.join(f'[[{s}]]' for s in sources)}\n\n"

        return section + "---\n\n"

    def _architecture_section_2_personas(self) -> str:
        """Раздел 2: Персоны и роли."""
        section = "## 2. Персоны и роли\n\n"

        section += "### 2.1. Целевые аудитории\n\n"
        ta_doc = self._find_doc_by_pattern("Целевые аудитории")
        if ta_doc:
            section += self._extract_summary(ta_doc, max_sentences=3)
        else:
            section += "*Документ не найден*\n"
        section += "\n\n"

        section += "### 2.2. Роли в экосистеме\n\n"
        section += "- Ученик/Стажёр\n"
        section += "- Создатель/Методист\n"
        section += "- Куратор/Ментор\n"
        section += "- Разработчик ИИ-агентов\n"
        section += "- Организатор/Оунер проекта\n"
        section += "- Эпистемический совет\n\n"

        return section + "---\n\n"

    def _architecture_section_3_goals(self) -> str:
        """Раздел 3: Проблемы, гипотезы и цели."""
        section = "## 3. Проблемы, гипотезы и цели\n\n"

        section += "### 3.1. Ключевые проблемы\n\n"
        problems_doc = self._find_doc_by_pattern("Проблемы")
        if problems_doc:
            section += self._extract_summary(problems_doc, max_sentences=5)
        else:
            section += "- Свобода без «грамматики» личной траектории\n"
            section += "- «Интеллект как узкое место»\n"
            section += "- Обучение «рядом», а не внутри производства\n"
        section += "\n\n"

        section += "### 3.2. Гипотезы решения\n\n"
        hypotheses_doc = self._find_doc_by_pattern("Гипотезы")
        if hypotheses_doc:
            section += self._extract_summary(hypotheses_doc, max_sentences=5)
        section += "\n\n"

        section += "### 3.3. Цели по горизонтам\n\n"
        section += "- **2026** — доказательства и сборка ядра\n"
        section += "- **2027–2030** — масштабирование и стандарты\n"
        section += "- **После 2030** — культурная норма\n\n"

        return section + "---\n\n"

    def _architecture_section_4_creator(self) -> str:
        """Раздел 4: Целевая система - Созидатель."""
        section = "## 4. Целевая система: Созидатель\n\n"

        section += "### 4.1. Что такое Созидатель\n\n"
        creator_doc = self._find_doc_by_pattern("Концепция созидателя")
        if creator_doc:
            section += self._extract_summary(creator_doc, max_sentences=3)
        section += "\n\n"

        section += "### 4.2. Модель компетенций и уровни мастерства\n\n"
        competencies_doc = self._find_doc_by_pattern("Карта компетенций|Компетенции")
        if competencies_doc:
            section += self._extract_summary(competencies_doc, max_sentences=3)
        section += "\n\n"

        section += "### 4.3. Ценностное предложение\n\n"
        value_doc = self._find_doc_by_pattern("Ценностное предложение")
        if value_doc:
            section += self._extract_summary(value_doc, max_sentences=3)
        section += "\n\n"

        section += "### 4.4. Ролевая траектория\n\n"
        section += "Ученик → Интеллектуал → Профессионал → Исследователь → Просветитель\n\n"

        return section + "---\n\n"

    def _architecture_section_5_functioning(self) -> str:
        """Раздел 5: Функционирование экосистемы."""
        section = "## 5. Функционирование экосистемы\n\n"

        section += "### 5.1. Главные процессы (сквозные циклы)\n\n"
        section += "- **C1.** Онбординг и инициализация двойника\n"
        section += "- **C2.** Обучение → Артефакт → Перенос\n"
        section += "- **C3.** Производство руководств\n"
        section += "- **C4.** Конструирование и эксплуатация ИИ-агентов\n"
        section += "- **C5.** Продвижение (просвещение, маркетинг, продажи)\n"
        section += "- **C6.** Товарообмен и расчёты (фиат + токен)\n"
        section += "- **C7.** Экономика вклада (токен)\n"
        section += "- **C8.** Исследование научного фронтира\n"
        section += "- **C9.** Наблюдаемость/качество\n"
        section += "- **C10.** Подтверждение эпистемического статуса\n\n"

        section += "### 5.2. Концепция использования для ролей\n\n"
        conops_doc = self._find_doc_by_pattern("Концепция функционирования")
        if conops_doc:
            section += self._extract_summary(conops_doc, max_sentences=5)
        section += "\n\n"

        return section + "---\n\n"

    def _architecture_section_6_platform(self) -> str:
        """Раздел 6: Структура ИИ-платформы."""
        section = "## 6. Структура ИИ-платформы\n\n"

        section += "### 6.1. Карта подсистем\n\n"

        # Ищем документы подсистем
        subsystems = [d for d in self.by_family.get("F8", [])
                      if any(kw in d.name.lower() for kw in ["подсистем", "система", "платформа"])]

        if subsystems:
            section += "| № | Подсистема | Описание |\n"
            section += "|---|------------|----------|\n"
            for i, doc in enumerate(subsystems[:10], 1):
                desc = self._extract_first_sentence(doc)
                section += f"| {i} | [[{doc.name}]] | {desc[:80]}... |\n"
        section += "\n"

        section += "### 6.2. Мультиагентная ОС: компоненты\n\n"
        section += "- **Reasoning Core** — планирование и выбор инструментов\n"
        section += "- **Memory Store** — хранилище знаний и контекста\n"
        section += "- **Tool/Action Interface** — декларативные действия (Apps SDK)\n"
        section += "- **Goal Manager** — цели, ограничения, бюджеты\n"
        section += "- **Dialogue Layer** — коммуникация с пользователем\n\n"

        section += "### 6.3. Стадии жизненного цикла агента\n\n"
        section += "1. **Инициализация** — цель, метрики, контекст\n"
        section += "2. **Планирование** — выбор инструментов, план вызовов\n"
        section += "3. **Выполнение** — вызовы инструментов, протоколирование\n"
        section += "4. **Оценка** — пересчёт ценности, самокритика\n\n"

        return section + "---\n\n"

    def _architecture_section_7_data(self) -> str:
        """Раздел 7: Данные и сущности."""
        section = "## 7. Данные и сущности\n\n"

        section += "### 7.1. Сквозные модели данных\n\n"
        section += "- **Digital Twin** — цели, навыки, предпочтения, расписание\n"
        section += "- **Epistemic Graph** — эпистемы и их статусы/связи/доказательства\n"
        section += "- **Activity Ledger** — все события (обучение, проекты, публикации)\n"
        section += "- **Token Ledger** — начисления/списания, заморозки, тарифы\n\n"

        section += "### 7.2. Основные сущности\n\n"
        section += "`User`, `DigitalTwin`, `Program`, `Guide/Step/Task`, `Artifact`, "
        section += "`ActionEvent`, `Qualification`, `Episteme`, `Work`, `MethodDescription`, `Evidence`\n\n"

        section += "### 7.3. Политика библиотеки\n\n"
        section += "- **curated/** — строго через PR/ревью\n"
        section += "- **derived/** — только автоматом (агенты/ETL)\n\n"

        return section + "---\n\n"

    def _architecture_section_8_epistemic(self) -> str:
        """Раздел 8: Эпистемический статус."""
        section = "## 8. Эпистемический статус и доказательства\n\n"

        section += "### 8.1. ESG (Epistemic Status Graph)\n\n"
        section += "**Draft** → **PeerChecked** → **Accepted** → **Superseded**\n\n"

        section += "### 8.2. Сигналы для статуса\n\n"
        section += "- Подтверждённые артефакты и их перенос\n"
        section += "- Рецензии наставников\n"
        section += "- Использование другими\n"
        section += "- Стабильность недельных инкрементов\n"
        section += "- Evidence-bindings к утверждениям\n\n"

        section += "### 8.3. Процедура присвоения и обновления\n\n"
        section += "1. Сбор сигналов из событийной шины\n"
        section += "2. Нормировка по сложности задачи\n"
        section += "3. Предварительный рейтинг\n"
        section += "4. Человеческое подтверждение (по порогу риска)\n"
        section += "5. Публикация статуса и логика «старения»\n\n"

        return section + "---\n\n"

    def _architecture_section_9_economy(self) -> str:
        """Раздел 9: Экономика вклада."""
        section = "## 9. Экономика вклада: Proof-of-Impact и токеномика\n\n"

        section += "### 9.1. Идея и пайплайн начисления\n\n"
        section += "События → Work → Episteme → Evidence → Начисление → Заморозка\n\n"

        section += "### 9.2. Как зарабатывать и тратить токены\n\n"
        section += "**Заработок:**\n"
        section += "- За подтверждённые уроки/сертификации\n"
        section += "- За ревью чужих артефактов\n"
        section += "- За публикации с доказанным охватом\n"
        section += "- За вклад в проекты с измеримым эффектом\n\n"
        section += "**Расход:**\n"
        section += "- Доступ к премиум-курсам\n"
        section += "- Вычислительные квоты агентов\n"
        section += "- Маркетплейс ИИ-ассистентов\n"
        section += "- Сессии с наставниками\n\n"

        section += "### 9.3. Внутренняя биржа и управление treasury\n\n"
        tokenomics_doc = self._find_doc_by_pattern("Токеномика")
        if tokenomics_doc:
            section += self._extract_summary(tokenomics_doc, max_sentences=3)
        section += "\n\n"

        return section + "---\n\n"

    def _architecture_section_10_quality(self) -> str:
        """Раздел 10: Культура и стандарты качества."""
        section = "## 10. Культура и стандарты качества\n\n"

        section += "### 10.1. Принципы качества\n\n"
        section += "- **Делать-показывать-мерить-улучшать** — недельные инкременты и peer-review\n"
        section += "- **Воспроизводимость** — логи, версии, источники, критерии приёмки\n"
        section += "- **Curated vs Derived** — ручная зона отделена от авто-зоны\n"
        section += "- **Минимальные привилегии** — Policy-as-code в Apps SDK\n\n"

        section += "### 10.2. Архитектурные границы и принятие решений\n\n"
        section += "- **C4 Model** — контекст → контейнеры → компоненты\n"
        section += "- **ADR** — контекст → решение → trade-offs → ссылки\n\n"

        return section + "---\n\n"

    def _architecture_section_11_metrics(self) -> str:
        """Раздел 11: Метрики."""
        section = "## 11. Метрики\n\n"

        section += "### 11.1. Ключевые метрики\n\n"
        section += "- **Time-to-Master (TTM)** — время до достижения уровня мастера\n"
        section += "- **Cost-to-Master (CTM)** — суммарные затраты (фиат + токены)\n"
        section += "- **Время онбординга** — <30 минут до первого значимого действия\n"
        section += "- **Качество и перенос** — доля задач с переносом (7–14 дней)\n"
        section += "- **Экономика** — MRR/NRR, оборот токена\n"
        section += "- **Репутация** — динамика эпистемического статуса\n\n"

        return section + "---\n\n"

    def _architecture_section_12_stats(self) -> str:
        """Раздел 12: Статистика хранилища."""
        section = "## 12. Статистика хранилища\n\n"

        section += "| Метрика | Значение |\n"
        section += "|---------|----------|\n"
        section += f"| Всего документов | {len(self.documents)} |\n"

        by_family_str = ", ".join(f"{f}: {len(docs)}" for f, docs in sorted(self.by_family.items()))
        section += f"| По семействам | {by_family_str} |\n"

        active = sum(1 for d in self.documents if d.status == "active")
        draft = sum(1 for d in self.documents if d.status == "draft")
        section += f"| Активных | {active} |\n"
        section += f"| Черновиков | {draft} |\n\n"

        # Раздел 12.1: Динамика роста за 4 недели
        section += self._architecture_section_12_1_growth()

        return section + "---\n\n"

    def _architecture_section_12_1_growth(self) -> str:
        """Раздел 12.1: Динамика роста за 4 недели."""
        section = "### 12.1. Динамика роста за 4 недели\n\n"

        metrics = self._get_weekly_growth_metrics()

        if len(metrics) < 2:
            section += "*Недостаточно данных для расчёта динамики (требуется минимум 2 недели истории)*\n\n"
            return section

        # Таблица динамики по неделям
        section += "| Неделя | Документов | Строк | Символов | Прирост документов | Прирост строк |\n"
        section += "|--------|------------|-------|----------|-------------------|---------------|\n"

        prev_files = None
        prev_lines = None
        for m in metrics:
            files_growth = ""
            lines_growth = ""
            if prev_files is not None:
                files_diff = m['files'] - prev_files
                files_pct = (files_diff / prev_files * 100) if prev_files > 0 else 0
                files_growth = f"+{files_diff} ({files_pct:+.0f}%)" if files_diff >= 0 else f"{files_diff} ({files_pct:.0f}%)"
            if prev_lines is not None:
                lines_diff = m['lines'] - prev_lines
                lines_pct = (lines_diff / prev_lines * 100) if prev_lines > 0 else 0
                lines_growth = f"+{lines_diff:,} ({lines_pct:+.0f}%)" if lines_diff >= 0 else f"{lines_diff:,} ({lines_pct:.0f}%)"

            section += f"| {m['week']} | {m['files']} | {m['lines']:,} | {m['chars']:,} | {files_growth or '—'} | {lines_growth or '—'} |\n"

            prev_files = m['files']
            prev_lines = m['lines']

        section += "\n"

        # Сводка динамики
        first = metrics[0]
        last = metrics[-1]

        files_growth = last['files'] - first['files']
        lines_growth = last['lines'] - first['lines']
        chars_growth = last['chars'] - first['chars']

        files_pct = (files_growth / first['files'] * 100) if first['files'] > 0 else 0
        lines_pct = (lines_growth / first['lines'] * 100) if first['lines'] > 0 else 0
        chars_pct = (chars_growth / first['chars'] * 100) if first['chars'] > 0 else 0

        weeks_count = len(metrics)
        files_per_week = files_growth / weeks_count if weeks_count > 0 else 0
        lines_per_week = lines_growth / weeks_count if weeks_count > 0 else 0

        section += "**Сводка динамики:**\n\n"
        section += f"| Метрика | Начало ({first['week']}) | Конец ({last['week']}) | Прирост | В неделю |\n"
        section += "|---------|--------|-------|---------|----------|\n"
        section += f"| Документов (.md) | {first['files']} | {last['files']} | {files_growth:+} ({files_pct:+.0f}%) | {files_per_week:+.1f}/нед |\n"
        section += f"| Строк | {first['lines']:,} | {last['lines']:,} | {lines_growth:+,} ({lines_pct:+.0f}%) | {lines_per_week:+,.0f}/нед |\n"
        section += f"| Символов | {first['chars']:,} | {last['chars']:,} | {chars_growth:+,} ({chars_pct:+.0f}%) | — |\n\n"

        # ASCII-график роста документов
        section += "**ASCII-график роста документов:**\n\n"
        section += "```\n"

        max_files = max(m['files'] for m in metrics)
        bar_width = 40

        for m in metrics:
            bar_len = int((m['files'] / max_files) * bar_width) if max_files > 0 else 0
            bar = '█' * bar_len
            section += f"{m['week']}: {bar} {m['files']}\n"

        section += "```\n\n"

        # Определяем тренд
        if files_growth > 0:
            trend = "↑ Рост"
        elif files_growth < 0:
            trend = "↓ Снижение"
        else:
            trend = "→ Стабильно"

        section += f"**Тренд:** {trend}\n\n"

        return section

    def _architecture_section_13_links(self) -> str:
        """Раздел 13: Связанные документы."""
        return """## 13. Связанные документы

- [[Концепция автоматических отчётов ИИ 0.4.1]]
- [[Содержательная полнота описания 0.4]]
- [[Модель семейств документов 0.1]]
"""

    # ==================== СОДЕРЖАТЕЛЬНАЯ ПОЛНОТА ====================

    def _generate_content_completeness(self) -> str:
        """Генерация отчёта 'Содержательная полнота описания'."""
        report = self._header("Содержательная полнота описания")

        # Тепловая карта 3x3
        report += self._completeness_heatmap()

        # Executive Summary
        report += self._completeness_summary()

        # Анализ по ячейкам
        report += self._completeness_by_cells()

        # Применение SoTA-методов
        report += self._completeness_sota()

        # Интересы стейкхолдеров
        report += self._completeness_stakeholders()

        # Приоритизированные пробелы
        report += self._completeness_gaps()

        # Связанные документы
        report += self._completeness_links()

        return report

    def _completeness_heatmap(self) -> str:
        """
        Тепловая карта 3x3 для содержательной полноты.
        Согласно обновленному ТЗ 0.4.1, проверяем:
        1. Процент ПОЛНЫХ документов (>500 слов + структура + примеры + диаграммы)
        2. Применение SoTA-методов
        3. Наличие текстовых связей
        4. Актуальность (обновлены за 6 месяцев)
        """
        heatmap = "## Тепловая карта содержательной полноты\n\n"

        # SoTA-методы для каждой роли (из ТЗ)
        sota_methods = {
            "Предприниматель": ["jtbd", "business model", "value proposition", "бизнес-модел", "ценностн"],
            "Инженер": ["c4", "adr", "architecture", "архитектур", "диаграмм"],
            "Менеджер": ["conops", "okr", "метрик", "процесс", "эксплуатац"],
        }

        def cell_status(family_id):
            """Оценка статуса ячейки на основе процента полных документов."""
            docs = self.by_family.get(family_id, [])
            if not docs:
                return "🔴", 0

            # Подсчет ПОЛНЫХ документов
            full_docs = [d for d in docs if d.is_full]
            full_ratio = len(full_docs) / len(docs)

            # Критерии статуса:
            # 🟢 Полный: ≥80% документов полные
            # 🟡 Частичный: 50-79% документов полные
            # 🔴 Минимальный: <50% документов полные
            if full_ratio >= 0.8:
                return "🟢", int(full_ratio * 100)
            elif full_ratio >= 0.5:
                return "🟡", int(full_ratio * 100)
            else:
                return "🔴", int(full_ratio * 100)

        # Построение таблицы
        heatmap += "|                    | Предприниматель | Инженер | Менеджер |\n"
        heatmap += "|                    | (Смыслы)        | (Архитектура) | (Операции) |\n"
        heatmap += "|--------------------|-----------------|---------|----------|\n"

        f1_status, f1_pct = cell_status('F1')
        f2_status, f2_pct = cell_status('F2')
        f3_status, f3_pct = cell_status('F3')
        heatmap += f"| **Мир (Надсистема)** | {f1_status} F1 ({f1_pct}%) | {f2_status} F2 ({f2_pct}%) | {f3_status} F3 ({f3_pct}%) |\n"

        f4_status, f4_pct = cell_status('F4')
        f5_status, f5_pct = cell_status('F5')
        f6_status, f6_pct = cell_status('F6')
        heatmap += f"| **Созидатель (Целевая)** | {f4_status} F4 ({f4_pct}%) | {f5_status} F5 ({f5_pct}%) | {f6_status} F6 ({f6_pct}%) |\n"

        f7_status, f7_pct = cell_status('F7')
        f8_status, f8_pct = cell_status('F8')
        f9_status, f9_pct = cell_status('F9')
        heatmap += f"| **Экосистема (Создания)** | {f7_status} F7 ({f7_pct}%) | {f8_status} F8 ({f8_pct}%) | {f9_status} F9 ({f9_pct}%) |\n"

        return heatmap + "\n---\n\n"

    def _completeness_summary(self) -> str:
        """Executive Summary для содержательной полноты."""
        # Общий % полных документов
        full_docs = sum(1 for d in self.documents if d.is_full)
        total_docs = len(self.documents)
        completeness = int(full_docs / total_docs * 100) if total_docs > 0 else 0

        # % полных документов по каждому семейству (F1-F9)
        family_ratios = {}
        for f in ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9"]:
            docs = self.by_family.get(f, [])
            if docs:
                full_count = sum(1 for d in docs if d.is_full)
                family_ratios[f] = full_count / len(docs)
            else:
                family_ratios[f] = 0

        best = max(family_ratios, key=family_ratios.get)
        worst = min(family_ratios, key=family_ratios.get)

        # Критические пробелы: семейства с <50% полных документов
        gaps = [f for f, ratio in family_ratios.items() if ratio < 0.5]

        summary = "## 1. Executive Summary\n\n"
        summary += f"- **Общая содержательная полнота:** {completeness}% ({full_docs}/{total_docs} документов полные)\n"
        summary += f"- **Наиболее полное семейство:** {best} ({FAMILIES[best]['name']}) — {int(family_ratios[best]*100)}%\n"
        summary += f"- **Наименее полное семейство:** {worst} ({FAMILIES[worst]['name']}) — {int(family_ratios[worst]*100)}%\n"
        summary += f"- **Критические пробелы (<50%):** {', '.join(gaps) if gaps else 'нет'}\n\n"

        return summary + "---\n\n"

    def _completeness_by_cells(self) -> str:
        """Анализ по ячейкам матрицы 3x3."""
        cells = ""

        for family_id in ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9"]:
            family = FAMILIES[family_id]
            docs = self.by_family.get(family_id, [])

            cells += f"### 2.{family_id[1]}. {family['level']} × {family['role']} ({family_id}: {family['name']})\n\n"

            expected = {"F1": 8, "F2": 6, "F3": 6, "F4": 6, "F5": 8, "F6": 6, "F7": 6, "F8": 15, "F9": 10}
            ratio = len(docs) / expected.get(family_id, 5)
            status = "🟢" if ratio >= 0.8 else ("🟡" if ratio >= 0.4 else "🔴")

            cells += f"**Статус:** {status} ({len(docs)} документов)\n\n"

            if docs:
                cells += "**Документы:**\n"
                for doc in docs[:5]:
                    cells += f"- [[{doc.name}]]\n"
                if len(docs) > 5:
                    cells += f"- ... и ещё {len(docs) - 5}\n"
            else:
                cells += "*Документы отсутствуют*\n"

            cells += "\n"

        return "## 2. Анализ по ячейкам матрицы 3×3\n\n" + cells + "---\n\n"

    def _completeness_sota(self) -> str:
        """Проверка применения SoTA-методов."""
        sota = "## 3. Применение SoTA-методов\n\n"

        # Проверяем наличие артефактов методов
        methods = {
            "JTBD": self._find_doc_by_pattern("JTBD|Jobs.to.be.done"),
            "Value Proposition": self._find_doc_by_pattern("Ценностное предложение|Value Proposition"),
            "C4 Model": self._find_doc_by_pattern("C4|Контекст.*контейнер|архитектур"),
            "ADR": self._find_doc_by_pattern("ADR|Architecture Decision"),
            "ConOps": self._find_doc_by_pattern("ConOps|Концепция.*использования|Concept.*Operations"),
            "OKR": self._find_doc_by_pattern("OKR|Objectives.*Key.*Results|Цели.*задачи"),
        }

        sota += "| Метод | Статус | Документ |\n"
        sota += "|-------|--------|----------|\n"

        for method, doc in methods.items():
            if doc:
                sota += f"| {method} | ✅ Применён | [[{doc.name}]] |\n"
            else:
                sota += f"| {method} | ❌ Не найден | — |\n"

        return sota + "\n---\n\n"

    def _completeness_stakeholders(self) -> str:
        """Ответы на интересы заинтересованных лиц."""
        stakeholders = "## 4. Ответы на интересы заинтересованных лиц\n\n"

        questions = [
            ("Ученик", "Что я получу?", "F4", "Ценностное предложение"),
            ("Ученик", "Как начать?", "F6", "Онбординг"),
            ("Наставник", "Как работать с учениками?", "F6", "Деканат|наставник"),
            ("Инвестор", "Какова бизнес-модель?", "F7", "Экономическ|бизнес.модел"),
            ("Разработчик", "Как устроена платформа?", "F8", "Архитектур|платформ"),
            ("Партнёр", "Как интегрироваться?", "F2", "Интеграц|партнёр"),
        ]

        stakeholders += "| Стейкхолдер | Вопрос | Статус | Где ответ |\n"
        stakeholders += "|-------------|--------|--------|----------|\n"

        for stakeholder, question, family, pattern in questions:
            doc = self._find_doc_by_pattern(pattern)
            if doc:
                stakeholders += f"| {stakeholder} | {question} | ✅ | [[{doc.name}]] |\n"
            else:
                stakeholders += f"| {stakeholder} | {question} | ❌ | *Не найден* |\n"

        return stakeholders + "\n---\n\n"

    def _completeness_gaps(self) -> str:
        """Приоритизированные пробелы."""
        gaps = "## 5. Приоритизированные пробелы\n\n"

        expected = {"F1": 8, "F2": 6, "F3": 6, "F4": 6, "F5": 8, "F6": 6, "F7": 6, "F8": 15, "F9": 10}

        critical = []
        important = []

        for f, exp in expected.items():
            count = len(self.by_family.get(f, []))
            ratio = count / exp
            if ratio < 0.4:
                critical.append((f, FAMILIES[f]['name'], int(ratio * 100)))
            elif ratio < 0.8:
                important.append((f, FAMILIES[f]['name'], int(ratio * 100)))

        gaps += "### 5.1. Критические 🔴\n\n"
        if critical:
            for f, name, pct in critical:
                gaps += f"- **{f} ({name})** — {pct}% заполненности\n"
        else:
            gaps += "*Критических пробелов нет*\n"
        gaps += "\n"

        gaps += "### 5.2. Важные 🟡\n\n"
        if important:
            for f, name, pct in important:
                gaps += f"- **{f} ({name})** — {pct}% заполненности\n"
        else:
            gaps += "*Важных пробелов нет*\n"

        return gaps + "\n---\n\n"

    def _completeness_links(self) -> str:
        return """## 6. Связанные документы

- [[Концепция автоматических отчётов ИИ 0.4.1]]
- [[Модель семейств документов 0.1]]
- [[Структура хранилища 0.1]]
"""

    # ==================== ТЕХНИЧЕСКИЕ ПРОБЛЕМЫ ====================

    def _generate_technical_issues(self) -> str:
        """Генерация отчёта 'Противоречия и несогласованности хранилища'."""
        report = self._header("Противоречия и несогласованности хранилища")

        # Собираем проблемы
        dup_folders = self._find_duplicate_folders()
        dup_docs = self._find_duplicate_documents()
        broken_links = self._find_broken_links()
        missing_metadata = self._find_missing_metadata()

        # Тепловая карта
        report += self._technical_heatmap(dup_folders, dup_docs, broken_links, missing_metadata)

        # Executive Summary
        total = len(dup_folders) + len(dup_docs) + len(broken_links) + len(missing_metadata)
        critical = len(dup_folders) + len([d for d in dup_docs if d[2] == "exact"])

        report += "## 1. Executive Summary\n\n"
        report += f"- **Всего технических проблем:** {total}\n"
        report += f"- **Критических:** {critical}\n"
        report += f"- **Требуют внимания:** {total - critical}\n\n"
        report += "---\n\n"

        # Дублирование папок
        report += self._technical_dup_folders(dup_folders)

        # Дублирование документов
        report += self._technical_dup_docs(dup_docs)

        # Битые ссылки
        report += self._technical_broken_links(broken_links)

        # Отсутствующие метаданные
        report += self._technical_missing_metadata(missing_metadata)

        # Связанные документы
        report += """## 7. Связанные документы

- [[Концепция автоматических отчётов ИИ 0.4.1]]
- [[Терминологическая согласованность 0.4]]
- [[Структура хранилища 0.1]]
"""

        return report

    def _technical_heatmap(self, dup_folders, dup_docs, broken_links, missing_metadata) -> str:
        heatmap = "## Тепловая карта технических проблем\n\n"
        heatmap += "| Тип проблемы | Количество | Статус |\n"
        heatmap += "|--------------|------------|--------|\n"

        def status(count, threshold_red=1, threshold_yellow=5):
            if count >= threshold_red:
                return "🔴"
            elif count >= threshold_yellow:
                return "🟡"
            return "🟢"

        heatmap += f"| Дублирование названий папок | {len(dup_folders)} | {status(len(dup_folders))} |\n"
        heatmap += f"| Дублирование названий документов | {len(dup_docs)} | {status(len(dup_docs), 3, 10)} |\n"
        heatmap += f"| Битые wikilinks | {len(broken_links)} | {status(len(broken_links), 5, 15)} |\n"
        heatmap += f"| Несогласованность метаданных | {len(missing_metadata)} | {status(len(missing_metadata), 10, 30)} |\n"

        total = len(dup_folders) + len(dup_docs) + len(broken_links) + len(missing_metadata)
        heatmap += f"| **Итого проблем** | **{total}** | — |\n"

        return heatmap + "\n---\n\n"

    def _find_duplicate_folders(self) -> List[Tuple[str, List[str], str]]:
        """Поиск папок с одинаковыми названиями или номерами.

        Возвращает список кортежей: (ключ_дубля, [пути], тип_дубля)
        Типы: 'number' (одинаковый номер раздела), 'name' (одинаковое название)
        """
        # Сканируем ВСЕ папки рекурсивно, а не только родителей документов
        all_folders = set()
        for folder in CONTENT_DIR.rglob("*"):
            if folder.is_dir():
                # Пропускаем служебные папки
                if any(skip in str(folder) for skip in [".obsidian", "node_modules", ".git"]):
                    continue
                if folder != CONTENT_DIR:
                    all_folders.add(folder)

        # Словари для поиска дублей
        folder_numbers = defaultdict(list)  # номер раздела -> пути
        folder_names = defaultdict(list)    # название (без номера) -> пути

        for folder in all_folders:
            rel_path = str(folder.relative_to(CONTENT_DIR))
            folder_name = folder.name

            # Извлекаем номер раздела (например, "0.4.1." из "0.4.1. Название")
            number_match = re.match(r'^(\d+(?:\.\d+)*\.?)\s*', folder_name)
            if number_match:
                section_number = number_match.group(1).rstrip('.')  # "0.4.1"
                folder_numbers[section_number].append(rel_path)

            # Извлекаем название без номера
            name = re.sub(r'^\d+(?:\.\d+)*\.?\s*', '', folder_name).lower().strip()
            if name:
                folder_names[name].append(rel_path)

        duplicates = []

        # Дублирование номеров разделов (критично!)
        for number, paths in folder_numbers.items():
            unique_paths = list(set(paths))
            if len(unique_paths) > 1:
                duplicates.append((f"Номер {number}", unique_paths, "number"))

        # Дублирование названий
        for name, paths in folder_names.items():
            unique_paths = list(set(paths))
            if len(unique_paths) > 1:
                duplicates.append((name, unique_paths, "name"))

        return duplicates

    def _find_duplicate_documents(self) -> List[Tuple[str, List[str], str]]:
        """Поиск документов с одинаковыми названиями."""
        doc_names = defaultdict(list)

        for doc in self.documents:
            # Убираем номер раздела из названия
            name = re.sub(r'\s*\d+\.\d+\.?$', '', doc.name).lower().strip()
            doc_names[name].append(str(doc.relative_path))

        duplicates = []
        for name, paths in doc_names.items():
            if len(paths) > 1:
                # Определяем тип дубля
                dup_type = "exact" if len(set(paths)) == len(paths) else "similar"
                duplicates.append((name, paths, dup_type))

        return duplicates

    def _find_broken_links(self) -> List[Tuple[str, str, str]]:
        """Поиск битых wikilinks."""
        # Собираем все имена документов
        doc_names = {doc.name.lower(): doc.name for doc in self.documents}

        broken = []
        for doc in self.documents:
            for link in doc.wikilinks:
                link_lower = link.lower()
                # Проверяем существование
                if link_lower not in doc_names:
                    # Ищем похожие
                    similar = self._find_similar_name(link, doc_names.values())
                    broken.append((str(doc.relative_path), link, similar or "не найден"))

        return broken[:50]  # Ограничиваем вывод

    def _find_missing_metadata(self) -> List[Tuple[str, List[str]]]:
        """Поиск документов без обязательных метаданных."""
        required_fields = ["type", "status"]

        missing = []
        for doc in self.documents:
            absent = [f for f in required_fields if f not in doc.frontmatter]
            if absent:
                missing.append((str(doc.relative_path), absent))

        return missing[:30]  # Ограничиваем вывод

    def _technical_dup_folders(self, duplicates) -> str:
        section = "## 2. Дублирование папок\n\n"

        if not duplicates:
            return section + "*Дублирования не обнаружено* 🟢\n\n---\n\n"

        # Разделяем по типу: сначала дубли номеров (критичнее), потом названий
        number_dups = [(n, p, t) for n, p, t in duplicates if t == "number"]
        name_dups = [(n, p, t) for n, p, t in duplicates if t == "name"]

        idx = 1

        if number_dups:
            section += "### Дублирование номеров разделов 🔴\n\n"
            for name, paths, _ in number_dups[:10]:
                section += f"#### 2.{idx}. [DUP-F{idx:03d}] {name}\n\n"
                section += "**Найдены папки с одинаковым номером:**\n"
                for path in paths[:5]:
                    section += f"- `{path}`\n"
                section += "\n**Проблема:** Дублирование номера раздела нарушает иерархию хранилища.\n"
                section += "**Рекомендация:** Переименовать одну из папок с новым номером.\n\n"
                idx += 1

        if name_dups:
            section += "### Дублирование названий папок 🟡\n\n"
            for name, paths, _ in name_dups[:10]:
                section += f"#### 2.{idx}. [DUP-F{idx:03d}] Дублирование «{name}»\n\n"
                section += "**Найдены папки:**\n"
                for path in paths[:5]:
                    section += f"- `{path}`\n"
                section += "\n**Рекомендация:** Объединить или переименовать.\n\n"
                idx += 1

        return section + "---\n\n"

    def _technical_dup_docs(self, duplicates) -> str:
        section = "## 3. Дублирование названий документов\n\n"

        if not duplicates:
            return section + "*Дублирования не обнаружено* 🟢\n\n---\n\n"

        section += "| № | Название | Количество | Пути |\n"
        section += "|---|----------|------------|------|\n"

        for i, (name, paths, dup_type) in enumerate(duplicates[:15], 1):
            paths_str = "; ".join(paths[:3])
            if len(paths) > 3:
                paths_str += f" и ещё {len(paths) - 3}"
            section += f"| {i} | {name[:40]} | {len(paths)} | {paths_str[:60]}... |\n"

        return section + "\n---\n\n"

    def _technical_broken_links(self, broken) -> str:
        section = "## 4. Битые wikilinks\n\n"

        if not broken:
            return section + "*Битых ссылок не обнаружено* 🟢\n\n---\n\n"

        section += "| № | Документ | Ссылка | Рекомендация |\n"
        section += "|---|----------|--------|-------------|\n"

        for i, (doc_path, link, suggestion) in enumerate(broken[:20], 1):
            doc_short = doc_path.split("/")[-1][:30]
            section += f"| {i} | {doc_short} | `[[{link[:30]}]]` | {suggestion[:30]} |\n"

        if len(broken) > 20:
            section += f"\n*... и ещё {len(broken) - 20} битых ссылок*\n"

        return section + "\n---\n\n"

    def _technical_missing_metadata(self, missing) -> str:
        section = "## 5. Документы без обязательных метаданных\n\n"

        if not missing:
            return section + "*Все документы имеют обязательные метаданные* 🟢\n\n---\n\n"

        section += "| № | Документ | Отсутствуют поля |\n"
        section += "|---|----------|------------------|\n"

        for i, (doc_path, fields) in enumerate(missing[:20], 1):
            doc_short = doc_path.split("/")[-1][:40]
            section += f"| {i} | {doc_short} | {', '.join(fields)} |\n"

        if len(missing) > 20:
            section += f"\n*... и ещё {len(missing) - 20} документов*\n"

        return section + "\n---\n\n"

    # ==================== ВСПОМОГАТЕЛЬНЫЕ ОТЧЁТЫ ====================

    def _generate_terminology(self) -> str:
        """Генерация отчёта по терминологической согласованности."""
        report = self._header("Терминологическая согласованность")

        if not self.ai_analyzer:
            report += "*Этот отчёт требует AI-анализа для сравнения определений терминов.*\n\n"
            report += "Запустите с флагом `--ai-analysis` для полного анализа:\n"
            report += "```bash\n"
            report += "python3 .ops/build_report.py --report terminology --ai-analysis\n"
            report += "```\n\n"
            report += "**Требования:**\n"
            report += "- Установите: `pip install httpx`\n"
            report += "- Задайте переменную окружения `OPENROUTER_API_KEY`\n"
            return report

        print("   🤖 Выполняется AI-анализ терминологии...")
        ai_analysis = self.ai_analyzer.analyze_terminology(self.documents)
        report += ai_analysis

        return report

    def _generate_recommendations(self) -> str:
        """
        Генерация отчёта с рекомендациями по развитию.
        Работает БЕЗ AI-анализа, агрегируя данные из всех отчетов согласно ТЗ 0.4.1.
        """
        report = self._header("Рекомендации по развитию")

        # Агрегированный анализ (без AI)
        report += self._recommendations_heatmap()
        report += self._recommendations_metrics()
        report += self._recommendations_critical_issues()
        report += self._recommendations_priorities()

        # Если есть AI-анализатор, добавляем AI-рекомендации
        if self.ai_analyzer:
            print("   🤖 Выполняется AI-анализ для дополнительных рекомендаций...")
            ai_analysis = self.ai_analyzer.analyze_recommendations(self.documents, self.by_family)
            report += "\n---\n\n## Дополнительные рекомендации AI\n\n"
            report += ai_analysis

        return report

    def _recommendations_heatmap(self) -> str:
        """Тепловая карта здоровья хранилища согласно ТЗ."""
        # Расчет показателей
        full_docs = [d for d in self.documents if d.is_full]
        full_docs_count = len(full_docs)
        full_ratio = full_docs_count / len(self.documents) if self.documents else 0

        docs_with_links = sum(1 for d in self.documents if len(d.wikilinks) > 0)
        links_ratio = docs_with_links / len(self.documents) if self.documents else 0

        # Подсчет критических проблем (семейства с 🔴 статусом)
        critical_families = 0
        for family_id in ["F0", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9"]:
            docs = self.by_family.get(family_id, [])
            if not docs:
                critical_families += 1
                continue
            full_count = sum(1 for d in docs if d.is_full)
            full_fam_ratio = full_count / len(docs)
            if full_fam_ratio < 0.5:
                critical_families += 1

        # Взвешенная оценка здоровья (согласно ТЗ)
        # Вес показателей: полнота документов 40%, связность 30%, отсутствие проблем 30%
        health_score = (
            (full_ratio * 40) +  # 40% вес
            (links_ratio * 30) +  # 30% вес
            ((1 - critical_families / 10) * 30)  # 30% вес
        )

        # Определение статуса согласно ТЗ п. 2
        if (full_docs_count >= 90 and
            health_score >= 90 and
            links_ratio >= 0.8 and
            critical_families < 10):
            overall_status = "🟢"
            status_desc = "Здоровое"
        elif (full_docs_count >= 60 and
              health_score >= 75 and
              links_ratio >= 0.4 and
              critical_families <= 30):
            overall_status = "🟡"
            status_desc = "Требует внимания"
        else:
            overall_status = "🔴"
            status_desc = "Критическое"

        heatmap = "## Тепловая карта здоровья хранилища\n\n"
        heatmap += f"**Общий статус:** {overall_status} {status_desc}\n\n"

        heatmap += "| Измерение | Оценка | Вес | Вклад | Статус |\n"
        heatmap += "|-----------|--------|-----|-------|--------|\n"
        heatmap += f"| Полнота документов | {full_docs_count}/{len(self.documents)} ({int(full_ratio*100)}%) | 40% | {full_ratio*40:.1f} | {'🟢' if full_ratio >= 0.8 else '🟡' if full_ratio >= 0.5 else '🔴'} |\n"
        heatmap += f"| Связность | {docs_with_links}/{len(self.documents)} ({int(links_ratio*100)}%) | 30% | {links_ratio*30:.1f} | {'🟢' if links_ratio >= 0.7 else '🟡' if links_ratio >= 0.4 else '🔴'} |\n"
        heatmap += f"| Отсутствие проблем | {10-critical_families}/10 семейств | 30% | {(1-critical_families/10)*30:.1f} | {'🟢' if critical_families < 3 else '🟡' if critical_families <= 5 else '🔴'} |\n"
        heatmap += f"| **Итого** | — | 100% | **{health_score:.1f}** | {overall_status} |\n\n"

        heatmap += f"**Интерпретация:** {'✅ Хранилище в хорошем состоянии' if overall_status == '🟢' else '⚠️ Требуется внимание и улучшения' if overall_status == '🟡' else '🚨 Критическое состояние, требуется срочное вмешательство'}\n\n"

        return heatmap + "---\n\n"

    def _recommendations_metrics(self) -> str:
        """Детальные показатели по отчетам."""
        metrics = "## 1. Детальные показатели\n\n"

        # Архитектурная полнота
        metrics += "### 1.1. Архитектурная полнота (по семействам F0-F9)\n\n"
        metrics += "| Семейство | Документов | Полных | % | Статус |\n"
        metrics += "|-----------|------------|--------|---|--------|\n"

        for family_id in ["F0", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9"]:
            family = FAMILIES[family_id]
            docs = self.by_family.get(family_id, [])
            count = len(docs)
            full_count = sum(1 for d in docs if d.is_full)
            full_pct = int(full_count / count * 100) if count > 0 else 0
            status = "🟢" if full_pct >= 80 else "🟡" if full_pct >= 50 else "🔴"
            metrics += f"| {family_id} | {count} | {full_count} | {full_pct}% | {status} |\n"

        metrics += "\n### 1.2. Связность документов\n\n"
        docs_with_links = sum(1 for d in self.documents if len(d.wikilinks) > 0)
        isolated = len(self.documents) - docs_with_links
        metrics += f"- **Документов со связями:** {docs_with_links} ({int(docs_with_links/len(self.documents)*100)}%)\n"
        metrics += f"- **Изолированных документов:** {isolated} ({int(isolated/len(self.documents)*100)}%)\n"
        metrics += f"- **Среднее связей на документ:** {sum(len(d.wikilinks) for d in self.documents) / len(self.documents):.1f}\n\n"

        return metrics + "---\n\n"

    def _recommendations_critical_issues(self) -> str:
        """Критические проблемы."""
        issues = "## 2. Критические проблемы 🔴\n\n"

        critical_found = False

        # Семейства с критическим статусом
        critical_families = []
        for family_id in ["F0", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9"]:
            docs = self.by_family.get(family_id, [])
            if not docs:
                critical_families.append((family_id, FAMILIES[family_id]['name'], 0, "Документы отсутствуют"))
                continue
            full_count = sum(1 for d in docs if d.is_full)
            full_ratio = full_count / len(docs)
            if full_ratio < 0.5:
                critical_families.append((family_id, FAMILIES[family_id]['name'], int(full_ratio*100), f"Только {int(full_ratio*100)}% документов полные"))

        if critical_families:
            critical_found = True
            issues += "### 2.1. Семейства с критическим уровнем полноты (<50%)\n\n"
            issues += "| Семейство | Название | % полных | Проблема |\n"
            issues += "|-----------|----------|----------|----------|\n"
            for fid, fname, pct, problem in critical_families[:5]:
                issues += f"| {fid} | {fname} | {pct}% | {problem} |\n"
            issues += "\n"

        # Изолированные документы
        isolated = [d for d in self.documents if len(d.wikilinks) == 0]
        if len(isolated) > 50:
            critical_found = True
            issues += f"### 2.2. Массовая изоляция документов\n\n"
            issues += f"**{len(isolated)} документов ({int(len(isolated)/len(self.documents)*100)}%) не имеют связей с другими документами.**\n\n"
            issues += "Это затрудняет навигацию и понимание структуры хранилища.\n\n"

        if not critical_found:
            issues += "*Критических проблем не обнаружено.*\n\n"

        return issues + "---\n\n"

    def _recommendations_priorities(self) -> str:
        """Приоритизированные рекомендации."""
        rec = "## 3. Рекомендации по приоритетам\n\n"

        rec += "### 3.1. Срочные (эта неделя)\n\n"

        urgent = []

        # Проверка семейств с 0% полноты
        for family_id in ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9"]:
            docs = self.by_family.get(family_id, [])
            if not docs:
                continue
            full_count = sum(1 for d in docs if d.is_full)
            if full_count == 0:
                urgent.append(f"**{family_id} ({FAMILIES[family_id]['name']}):** Наполнить семейство полными документами (сейчас 0/{len(docs)} полных)")

        if urgent:
            for item in urgent[:3]:
                rec += f"1. {item}\n"
        else:
            rec += "1. Продолжить развитие документации согласно плану\n"

        rec += "\n### 3.2. Важные (этот месяц)\n\n"

        important = []

        # Семейства с 1-49% полноты
        for family_id in ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9"]:
            docs = self.by_family.get(family_id, [])
            if not docs:
                continue
            full_count = sum(1 for d in docs if d.is_full)
            full_ratio = full_count / len(docs)
            if 0 < full_ratio < 0.5:
                important.append(f"**{family_id}:** Довести полноту до 50%+ (сейчас {int(full_ratio*100)}%)")

        # Связность
        isolated_pct = sum(1 for d in self.documents if len(d.wikilinks) == 0) / len(self.documents)
        if isolated_pct > 0.5:
            important.append(f"**Связность:** Добавить wikilinks в изолированные документы (сейчас {int(isolated_pct*100)}% без связей)")

        if important:
            for i, item in enumerate(important[:3], 1):
                rec += f"{i}. {item}\n"
        else:
            rec += "1. Улучшить качество существующих документов\n"

        rec += "\n### 3.3. Желательные (бэклог)\n\n"
        rec += "1. Добавить диаграммы и визуализации в документы\n"
        rec += "2. Обновить устаревшие документы (>6 месяцев)\n"
        rec += "3. Добавить примеры и метрики в документы\n\n"

        return rec + "---\n\n"

    def _generate_links_map(self) -> str:
        """
        Генерация карты связей между документами.
        Согласно обновленному ТЗ 0.4.1:
        - Детальная таблица для ВСЕХ документов
        - Проверка качества связанных документов (полные или заглушки)
        - Статус связности на основе содержания
        """
        report = self._header("Карта связей между документами")

        # Подсчет входящих ссылок
        incoming = defaultdict(int)
        for doc in self.documents:
            for link in doc.wikilinks:
                incoming[link.lower()] += 1

        # Индекс документов по имени для быстрого поиска
        doc_by_name = {d.name.lower(): d for d in self.documents}

        # Анализ каждого документа
        doc_stats = []
        for doc in self.documents:
            # Исходящие связи
            outgoing = len(doc.wikilinks)

            # Входящие связи
            incoming_count = incoming.get(doc.name.lower(), 0)

            # Всего связей
            total_links = incoming_count + outgoing

            # Текстовые связи (wikilinks в теле документа, не в frontmatter)
            text_links = len(doc.wikilinks)  # Все wikilinks уже из текста

            # Процент полных связанных документов
            linked_full_count = 0
            linked_total = 0
            for link in doc.wikilinks:
                linked_doc = doc_by_name.get(link.lower())
                if linked_doc:
                    linked_total += 1
                    if linked_doc.is_full:
                        linked_full_count += 1

            full_linked_ratio = (linked_full_count / linked_total * 100) if linked_total > 0 else 0

            # Определение статуса согласно ЖЕСТКИМ критериям ТЗ
            # 🟢 Хорошо связан: ≥5 связей + ≥70% текстовых + ≥70% связанных полные
            # 🟡 Слабо связан: 3-4 связи + ≥40% текстовых + ≥50% связанных полные
            # 🔴 Изолирован (ПО УМОЛЧАНИЮ): ≤2 связей ИЛИ связи нерелевантны/неполные

            if (total_links >= 5 and
                text_links >= total_links * 0.7 and
                full_linked_ratio >= 70):
                status = "🟢"
            elif (total_links >= 3 and
                  text_links >= total_links * 0.4 and
                  full_linked_ratio >= 50):
                status = "🟡"
            else:
                status = "🔴"

            doc_stats.append({
                'name': doc.name,
                'total': total_links,
                'text': text_links,
                'incoming': incoming_count,
                'outgoing': outgoing,
                'full_linked_pct': int(full_linked_ratio),
                'status': status
            })

        # Сортировка по количеству связей (убывание)
        doc_stats.sort(key=lambda x: x['total'], reverse=True)

        # Подсчет статусов
        status_counts = {"🟢": 0, "🟡": 0, "🔴": 0}
        for stat in doc_stats:
            status_counts[stat['status']] += 1

        # Тепловая карта связности (согласно ТЗ п. 2)
        report += "## Тепловая карта связей\n\n"
        report += "**Сводка по статусам:**\n"
        report += f"- 🟢 Хорошо связаны: {status_counts['🟢']} документов ({int(status_counts['🟢']/len(doc_stats)*100)}%)\n"
        report += f"- 🟡 Слабо связаны: {status_counts['🟡']} документов ({int(status_counts['🟡']/len(doc_stats)*100)}%)\n"
        report += f"- 🔴 Изолированы: {status_counts['🔴']} документов ({int(status_counts['🔴']/len(doc_stats)*100)}%)\n\n"

        report += "**Детализация по документам (первые 20, полный список см. ниже):**\n\n"
        report += "| Документ | Всего связей | Текстовых | Входящих | Исходящих | % полных связанных | Статус |\n"
        report += "|----------|--------------|-----------|----------|-----------|-------------------|--------|\n"

        # Первые 20 для preview
        for stat in doc_stats[:20]:
            name_short = stat['name'][:60]
            report += f"| {name_short} | {stat['total']} | {stat['text']} ({int(stat['text']/stat['total']*100) if stat['total'] > 0 else 0}%) | {stat['incoming']} | {stat['outgoing']} | {stat['full_linked_pct']}% | {stat['status']} |\n"

        report += f"\n*Полная таблица со всеми {len(doc_stats)} документами представлена в разделе 3.*\n\n"
        report += "---\n\n"

        # Секция 1: Executive Summary
        total_links = sum(stat['total'] for stat in doc_stats)
        avg_links = total_links / len(doc_stats) if doc_stats else 0

        report += "## 1. Executive Summary\n\n"
        report += f"- **Всего документов:** {len(doc_stats)}\n"
        report += f"- **Всего связей:** {total_links}\n"
        report += f"- **Изолированных документов:** {status_counts['🔴']} ({int(status_counts['🔴']/len(doc_stats)*100)}%)\n"
        report += f"- **Среднее связей на документ:** {avg_links:.1f}\n\n"
        report += "---\n\n"

        # Секция 2: Топ-10 хабов
        report += "## 2. Топ-10 документов по входящим связям (хабы)\n\n"
        report += "| № | Документ | Входящих | Исходящих | Всего |\n"
        report += "|---|----------|----------|-----------|-------|\n"

        top_incoming = sorted(doc_stats, key=lambda x: x['incoming'], reverse=True)[:10]
        for i, stat in enumerate(top_incoming, 1):
            report += f"| {i} | [[{stat['name']}]] | {stat['incoming']} | {stat['outgoing']} | {stat['total']} |\n"

        report += "\n---\n\n"

        # Секция 3: Полная таблица всех документов
        report += f"## 3. Полная таблица всех документов ({len(doc_stats)})\n\n"
        report += "| Документ | Всего связей | Текстовых | Входящих | Исходящих | % полных связанных | Статус |\n"
        report += "|----------|--------------|-----------|----------|-----------|-------------------|--------|\n"

        for stat in doc_stats:
            name_short = stat['name'][:60]
            text_pct = int(stat['text']/stat['total']*100) if stat['total'] > 0 else 0
            report += f"| {name_short} | {stat['total']} | {stat['text']} ({text_pct}%) | {stat['incoming']} | {stat['outgoing']} | {stat['full_linked_pct']}% | {stat['status']} |\n"

        report += "\n---\n\n"

        # Секция 4: Изолированные документы
        isolated = [stat for stat in doc_stats if stat['status'] == '🔴']
        report += f"## 4. Изолированные документы 🔴 ({len(isolated)})\n\n"

        if isolated:
            report += "| № | Документ | Всего связей | Причина изоляции |\n"
            report += "|---|----------|--------------|------------------|\n"

            for i, stat in enumerate(isolated[:20], 1):
                reason = "Нет связей" if stat['total'] == 0 else f"Только {stat['total']} связ."
                if stat['full_linked_pct'] < 50:
                    reason += f", связанные неполные ({stat['full_linked_pct']}%)"
                report += f"| {i} | {stat['name'][:50]} | {stat['total']} | {reason} |\n"

            if len(isolated) > 20:
                report += f"\n*... и ещё {len(isolated) - 20} изолированных документов*\n"
        else:
            report += "*Изолированных документов нет*\n"

        report += "\n---\n\n"

        return report

    # ==================== УТИЛИТЫ ====================

    def _find_doc_by_pattern(self, pattern: str) -> Optional[Document]:
        """Поиск документа по паттерну в названии."""
        regex = re.compile(pattern, re.IGNORECASE)
        for doc in self.documents:
            if regex.search(doc.name):
                return doc
        return None

    def _extract_summary(self, doc: Document, max_sentences: int = 3) -> str:
        """Извлечение краткого резюме из документа."""
        # Убираем заголовки и служебные элементы
        text = re.sub(r'^#.*$', '', doc.body, flags=re.MULTILINE)
        text = re.sub(r'\|.*\|', '', text)  # Убираем таблицы
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)  # Убираем код
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # Убираем ссылки
        text = re.sub(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', r'\1', text)  # Убираем wikilinks

        # Находим предложения
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

        return " ".join(sentences[:max_sentences])

    def _extract_first_sentence(self, doc: Document) -> str:
        """Извлечение первого предложения из документа."""
        summary = self._extract_summary(doc, max_sentences=1)
        return summary[:100] if summary else ""

    def _find_similar_name(self, name: str, candidates: List[str], threshold: float = 0.8) -> Optional[str]:
        """Поиск похожего названия (простой алгоритм)."""
        name_lower = name.lower()
        for candidate in candidates:
            candidate_lower = candidate.lower()
            # Простая проверка на вхождение
            if name_lower in candidate_lower or candidate_lower in name_lower:
                return candidate
        return None


def save_report(content: str, filename: str):
    """Сохранение отчёта в файл."""
    output_path = REPORTS_DIR / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    print(f"✅ Отчёт сохранён: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Генератор автоматических отчётов")
    parser.add_argument(
        "--report", "-r",
        required=True,
        choices=["architecture-snapshot", "content-completeness", "technical-issues",
                 "terminology", "recommendations", "links-map", "all"],
        help="Тип отчёта для генерации"
    )
    parser.add_argument(
        "--output", "-o",
        help="Путь для сохранения отчёта (по умолчанию: в папку отчётов)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Только показать отчёт, не сохранять"
    )
    parser.add_argument(
        "--ai-analysis",
        action="store_true",
        help="Использовать AI (Claude) для анализа терминологии и рекомендаций"
    )

    args = parser.parse_args()

    # Проверяем, что запущено из корня проекта
    if not CONTENT_DIR.exists():
        print(f"❌ Папка {CONTENT_DIR} не найдена. Запустите скрипт из корня проекта.")
        sys.exit(1)

    # Инициализируем AI-анализатор при необходимости
    ai_analyzer = None
    if args.ai_analysis:
        try:
            ai_analyzer = AIAnalyzer()
            print("✅ AI-анализ активирован")
        except RuntimeError as e:
            print(f"⚠️  {e}")
            print("   Продолжаем без AI-анализа...")

    generator = ReportGenerator(ai_analyzer=ai_analyzer)
    generator.scan_documents()

    report_files = {
        "architecture-snapshot": "Архитектурный слепок хранилища 0.4.md",
        "content-completeness": "Содержательная полнота описания 0.4.md",
        "technical-issues": "Противоречия и несогласованности 0.4.md",
        "terminology": "Терминологическая согласованность 0.4.md",
        "recommendations": "Рекомендации по развитию 0.4.md",
        "links-map": "Карта связей между документами 0.4.md",
    }

    if args.report == "all":
        reports_to_generate = list(report_files.keys())
    else:
        reports_to_generate = [args.report]

    for report_type in reports_to_generate:
        print(f"\n📝 Генерация отчёта: {report_type}")

        try:
            content = generator.generate(report_type)

            if args.dry_run:
                print("\n" + "=" * 60)
                print(content[:2000])
                print("..." if len(content) > 2000 else "")
                print("=" * 60)
            else:
                filename = args.output if args.output and args.report != "all" else report_files[report_type]
                save_report(content, filename)

        except Exception as e:
            print(f"❌ Ошибка при генерации {report_type}: {e}")
            import traceback
            traceback.print_exc()

    print("\n✅ Готово!")


if __name__ == "__main__":
    main()
