#!/usr/bin/env python3
# see DP.METHOD.054, WP-419 Ф7 (peer-session 2026-06-14-21)
#
# Реестр сервисов платформы (облачный шлюз). Сестра registry-catalog.py / numbering-registry.py.
# --validate: E1-hard structural checks; exit 1 on violations.
# --markdown: человекочитаемый вид; stdout для пилота/Week Close.
#
# Граница: сервис = инстанс, исполняющий обещание; обещание = DP.SC.* (контракт); артефакт = копируется.

import sys
import yaml
from pathlib import Path

REGISTRY_PATH = Path(__file__).parent.parent / "0.9.Inbox" / "platform-services-registry.yaml"

SVC_REQUIRED = {"service", "serves", "consumers", "contract", "dom", "tenancy"}
VALID_DOM = {"world", "russia", "by-jurisdiction", "canon"}
VALID_TENANCY = {"multi-tenant", "per-user", "per-team", "single"}
REG_REQUIRED = {"name", "owner", "bounded_context", "enforcement_mechanism"}


def load_registry():
    with open(REGISTRY_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate(data: dict) -> list[str]:
    """Return list of E1-hard violations. Empty = well-formed."""
    errors = []

    reg = data.get("schema_registration") or {}
    for field in REG_REQUIRED:
        if not reg.get(field):
            errors.append(f"schema_registration: missing '{field}' (метод §5)")

    services = data.get("services") or []
    if not services:
        errors.append("services: пуст — реестр без записей не несёт смысла")

    seen = set()
    for svc in services:
        name = svc.get("service", "<no-name>")
        missing = SVC_REQUIRED - set(k for k, v in svc.items() if v not in (None, ""))
        if missing:
            errors.append(f"service [{name}]: missing {missing}")
        if svc.get("dom") not in VALID_DOM:
            errors.append(f"service [{name}]: invalid dom '{svc.get('dom')}', expected {VALID_DOM}")
        if svc.get("tenancy") not in VALID_TENANCY:
            errors.append(f"service [{name}]: invalid tenancy '{svc.get('tenancy')}', expected {VALID_TENANCY}")
        if name in seen:
            errors.append(f"service [{name}]: дубль")
        seen.add(name)

    return errors


def to_markdown(data: dict) -> str:
    reg = data.get("schema_registration", {})
    lines = ["# Реестр сервисов платформы IWE", ""]
    lines.append(f"> Метод: {data.get('method_ref','?')} · владелец: {reg.get('owner','?')} · "
                 f"принуждение: {reg.get('enforcement_mechanism','?')} · схема v{data.get('schema_version','?')}")
    lines.append("")
    lines.append("| Сервис | Что отдаёт | Потребители | Контракт | Дом | Тенантность |")
    lines.append("|--------|-----------|-------------|----------|-----|-------------|")
    for svc in data.get("services", []):
        lines.append(f"| `{svc.get('service','')}` | {svc.get('serves','')} | {svc.get('consumers','')} | "
                     f"{svc.get('contract','')} | {svc.get('dom','')} | {svc.get('tenancy','')} |")
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("--validate", "--markdown"):
        print("usage: platform-services-registry.py --validate | --markdown", file=sys.stderr)
        return 2

    data = load_registry()

    if sys.argv[1] == "--validate":
        errors = validate(data)
        if errors:
            for e in errors:
                print(f"  ✗ {e}", file=sys.stderr)
            print(f"platform-services-registry --validate: FAIL ({len(errors)} violations)", file=sys.stderr)
            return 1
        n = len(data.get("services", []))
        gaps = len((data.get("contract_gaps") or {}).get("services_without_contract", []))
        print(f"platform-services-registry --validate: OK ({n} services, {gaps} без формального контракта)")
        return 0

    print(to_markdown(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
