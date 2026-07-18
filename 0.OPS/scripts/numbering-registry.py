#!/usr/bin/env python3
# see DP.METHOD.054, WP-419 Ф6 Г-полный (peer-session 2026-06-14-21)
#
# Реестр нумераций IWE (ID-префикс-семейства). Сестра registry-catalog.py.
# --validate: E1-hard structural checks; exit 1 on violations (путь чтения падает на битом реестре).
# --markdown: человекочитаемый вид (namespace'ы + коллизии); stdout для пилота/Week Close.
#
# Граница: registry-catalog = реестры/списки; numbering-registry = ID-префикс-семейства.

import sys
import yaml
from pathlib import Path

REGISTRY_PATH = Path(__file__).parent.parent / "numbering-registry.yaml"

NS_REQUIRED = {"pattern", "meaning", "sot_pointer", "managed_by"}
COLLISION_REQUIRED = {"id", "type", "status", "verdict"}
VALID_COLLISION_TYPES = {"collision", "collision_family"}
VALID_COLLISION_STATUS = {"open", "resolved"}
REG_REQUIRED = {"name", "owner", "bounded_context", "enforcement_mechanism"}


def load_registry():
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate(data: dict) -> list[str]:
    """Return list of E1-hard violations. Empty list = registry is well-formed."""
    errors = []

    # §5 self-registration present and complete (dogfood DP.METHOD.054)
    reg = data.get("schema_registration") or {}
    for field in REG_REQUIRED:
        if not reg.get(field):
            errors.append(f"schema_registration: missing '{field}' (метод §5 обязателен)")

    namespaces = data.get("namespaces") or []
    if not namespaces:
        errors.append("namespaces: пуст — реестр без записей не несёт смысла")

    seen_patterns = set()
    for ns in namespaces:
        pat = ns.get("pattern", "<no-pattern>")
        missing = NS_REQUIRED - set(k for k, v in ns.items() if v not in (None, ""))
        if missing:
            errors.append(f"namespace [{pat}]: missing {missing}")
        if pat in seen_patterns:
            errors.append(f"namespace [{pat}]: дубль pattern (один префикс = одна строка)")
        seen_patterns.add(pat)

    for col in data.get("collisions") or []:
        cid = col.get("id", "<no-id>")
        missing = COLLISION_REQUIRED - set(k for k, v in col.items() if v not in (None, ""))
        if missing:
            errors.append(f"collision [{cid}]: missing {missing}")
        if col.get("type") not in VALID_COLLISION_TYPES:
            errors.append(f"collision [{cid}]: invalid type '{col.get('type')}', expected {VALID_COLLISION_TYPES}")
        if col.get("status") not in VALID_COLLISION_STATUS:
            errors.append(f"collision [{cid}]: invalid status '{col.get('status')}', expected {VALID_COLLISION_STATUS}")

    return errors


def to_markdown(data: dict) -> str:
    lines = ["# Реестр нумераций IWE (ID-префикс-семейства)", ""]
    reg = data.get("schema_registration", {})
    lines.append(f"> Метод: {data.get('method_ref', '?')} · владелец: {reg.get('owner', '?')} · "
                 f"принуждение: {reg.get('enforcement_mechanism', '?')} · "
                 f"схема v{data.get('schema_version', '?')}")
    lines.append("")
    lines.append("## Пространства имён")
    lines.append("")
    lines.append("| Префикс | Смысл | Источник истины | Кем ведётся | Живых | Риск | Коллизия |")
    lines.append("|---------|-------|-----------------|-------------|-------|------|----------|")
    for ns in data.get("namespaces", []):
        lc = ns.get("live_count")
        lc = "—" if lc is None else lc
        lines.append(f"| `{ns.get('pattern','')}` | {ns.get('meaning','')} | "
                     f"{ns.get('sot_pointer','')} | {ns.get('managed_by','')} | {lc} | "
                     f"{ns.get('risk','')} | {ns.get('collision','')} |")
    lines.append("")
    lines.append("## Коллизии")
    lines.append("")
    lines.append("| ID | Токены | Тип | Статус | Вердикт |")
    lines.append("|----|--------|-----|--------|---------|")
    for col in data.get("collisions", []):
        lines.append(f"| {col.get('id','')} | {col.get('tokens','')} | {col.get('type','')} | "
                     f"**{col.get('status','')}** | {col.get('verdict','')} |")
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("--validate", "--markdown"):
        print("usage: numbering-registry.py --validate | --markdown", file=sys.stderr)
        return 2

    data = load_registry()

    if sys.argv[1] == "--validate":
        errors = validate(data)
        if errors:
            for e in errors:
                print(f"  ✗ {e}", file=sys.stderr)
            print(f"numbering-registry --validate: FAIL ({len(errors)} violations)", file=sys.stderr)
            return 1
        n_ns = len(data.get("namespaces", []))
        n_col = len(data.get("collisions", []))
        n_open = sum(1 for c in data.get("collisions", []) if c.get("status") == "open")
        print(f"numbering-registry --validate: OK ({n_ns} namespaces, {n_col} collisions, {n_open} open)")
        return 0

    print(to_markdown(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
