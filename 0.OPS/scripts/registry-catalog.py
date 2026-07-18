#!/usr/bin/env python3
# see DP.METHOD.054, peer-session 2026-06-13-31-wp419-f5-generator-design
#
# --validate: E1a-E1d hard structural checks (blocking, exit 1) + W1 recommended-field
#             warnings (owner; non-blocking, listed for manual follow-up — WP-7 D3).
#             In CI: .github/workflows/registry-catalog-validate.yml runs this on push/PR.
# --report:   freshness flags (90d, incl. never-verified entries) + status summary;
#             stdout for Week Close log. Wired via
#             extensions/week-close.after.registry-catalog-freshness.md (WP-7 D3).
# --markdown: human-readable catalog grouped by status; stdout for pilot view.

import sys
import yaml
from pathlib import Path
from datetime import date, datetime

CATALOG_PATH = Path(__file__).parent.parent / "WP-419-registry-catalog-draft.yaml"
FRESHNESS_DAYS = 90
OWNER_TBD = {"N/A", "TBD", "команда"}
REQUIRED_FIELDS_HARD = {"name", "status"}  # E1d: hard-blocks --validate
RECOMMENDED_FIELDS = {"owner"}  # W1: warns only — owner rollout is WP-476 Ф3, see WP-7 D3


def load_catalog():
    with open(CATALOG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def check_e1_hard(entry: dict) -> list[str]:
    """Return list of E1-hard violations (blocking) for one catalog entry."""
    violations = []
    name = entry.get("name", "<unnamed>")

    # E1d: hard-required fields present
    for field in REQUIRED_FIELDS_HARD:
        if not entry.get(field):
            violations.append(f"E1d [{name}]: missing required field '{field}'")

    # E1a: active registry must have code_scheme
    if entry.get("status") == "active" and not entry.get("code_scheme"):
        violations.append(f"E1a [{name}]: status=active but code_scheme is absent")

    # E1b: derived registry must have derived_from
    if entry.get("sot_or_derived") == "derived" and not entry.get("derived_from"):
        violations.append(f"E1b [{name}]: sot_or_derived=derived but derived_from is absent")

    # E1c: git verification requires sot_path (dead/missing entries are not verified)
    if (entry.get("verification_method") == "git"
            and not entry.get("sot_path")
            and entry.get("status") not in ("dead", "missing")):
        violations.append(f"E1c [{name}]: verification_method=git but sot_path is absent")

    return violations


def check_w1_recommended(entry: dict) -> list[str]:
    """Return list of W1 warnings (non-blocking): missing or placeholder recommended fields."""
    warnings = []
    name = entry.get("name", "<unnamed>")

    for field in RECOMMENDED_FIELDS:
        value = entry.get(field)
        if not value or str(value) in OWNER_TBD:
            warnings.append(f"W1 [{name}]: missing recommended field '{field}'")

    return warnings


def validate(data: dict) -> int:
    registries = data.get("registries", [])
    all_violations = []
    all_warnings = []
    for entry in registries:
        all_violations.extend(check_e1_hard(entry))
        all_warnings.extend(check_w1_recommended(entry))

    if all_warnings:
        print(f"registry-catalog --validate: {len(all_warnings)} non-blocking W1 warnings:", file=sys.stderr)
        for w in all_warnings:
            print(f"  {w}", file=sys.stderr)

    if all_violations:
        print("registry-catalog E1-hard violations:", file=sys.stderr)
        for v in all_violations:
            print(f"  {v}", file=sys.stderr)
        return 1

    print(f"registry-catalog --validate: OK ({len(registries)} entries, 0 E1 violations, {len(all_warnings)} W1 warnings)")
    return 0


def report(data: dict) -> int:
    registries = data.get("registries", [])
    today = date.today()
    stale = []
    never_verified = []
    counts = {"active": 0, "drifting": 0, "dead": 0, "missing": 0, "other": 0}

    for entry in registries:
        status = entry.get("status", "other")
        counts[status if status in counts else "other"] += 1

        lv = entry.get("last_verified")
        if lv and str(lv) != "null":
            try:
                lv_date = datetime.strptime(str(lv), "%Y-%m-%d").date()
                age = (today - lv_date).days
                if age > FRESHNESS_DAYS:
                    stale.append((entry.get("name", "<unnamed>"), age, entry.get("risk_priority", "?")))
            except ValueError:
                print(f"  ⚠️ bad last_verified date in '{entry.get('name', '?')}': {lv!r}", file=sys.stderr)
        else:
            # Missing/null last_verified is the worst case (never checked), not the
            # best one — silently skipping it here produced a false-green report (WP-7 D3).
            never_verified.append((entry.get("name", "<unnamed>"), entry.get("risk_priority", "?")))

    print(f"\n## Registry Catalog — Week Close report ({today})")
    print(f"Entries: {len(registries)} total | "
          f"active={counts['active']} drifting={counts['drifting']} "
          f"dead={counts['dead']} missing={counts['missing']}")

    total_flags = len(stale) + len(never_verified)
    if total_flags:
        print(f"\nFreshness flags (>{FRESHNESS_DAYS}d stale or never verified): {total_flags}")
        if never_verified:
            never_verified.sort(key=lambda x: x[1])
            print(f"  Никогда не проверялись ({len(never_verified)}):")
            for name, priority in never_verified[:10]:
                print(f"    {name} (риск={priority})")
            if len(never_verified) > 10:
                print(f"    ... и ещё {len(never_verified)-10}")
        if stale:
            stale.sort(key=lambda x: -x[1])
            print(f"  Просрочены ({len(stale)}):")
            for name, age, priority in stale[:10]:
                print(f"    {name}: {age}d (риск={priority})")
            if len(stale) > 10:
                print(f"    ... и ещё {len(stale)-10}")
    else:
        print("Freshness: все записи проверены менее 90 дней назад")

    return 0


STATUS_LABEL = {
    "active": "Живые",
    "drifting": "Отставшие",
    "dead": "Мёртвые",
    "missing": "Пробелы (реестра нет)",
}


def markdown(data: dict) -> int:
    registries = data.get("registries", [])
    by_status = {st: [] for st in STATUS_LABEL}
    for entry in registries:
        by_status.setdefault(entry.get("status", "other"), []).append(entry)

    print("# Каталог реестров IWE\n")
    print(f"> Читаемый вид. Генерируется: `registry-catalog.py --markdown`. "
          f"Источник — каталог-черновик (WP-419 Ф5). Всего записей: {len(registries)}.\n")
    print("> **Единица каталога — реестр, а не код.** Схема кодов (колонка «Схема кодов») — "
          "конституирующий признак реестра: реестра без схемы кодов не бывает. Но код — следствие "
          "существования реестра, а не наоборот; каталогизируются реестры, коды — их обязательный "
          "атрибут. Место хранения данных (дом) реестром не является — у дома своей схемы кодов нет "
          "(см. «Реестр домов хранения», WP-427).\n")

    for st, label in STATUS_LABEL.items():
        items = by_status.get(st, [])
        if not items:
            continue
        print(f"## {label} ({len(items)})\n")
        print("| Риск | Реестр | Схема кодов | Владелец | Тир |")
        print("|------|--------|-------------|----------|-----|")
        for e in sorted(items, key=lambda x: x.get("risk_priority", "z")):
            print(f"| {e.get('risk_priority', '-')} | {e.get('name', '?')} | "
                  f"{e.get('code_scheme', '-')} | {e.get('owner', '-')} | "
                  f"{e.get('tier', '-')} |")
        print()
    return 0


def main():
    modes = ("--validate", "--report", "--markdown")
    if len(sys.argv) < 2 or sys.argv[1] not in modes:
        print("Usage: registry-catalog.py --validate | --report | --markdown", file=sys.stderr)
        sys.exit(2)

    data = load_catalog()
    if sys.argv[1] == "--validate":
        sys.exit(validate(data))
    elif sys.argv[1] == "--report":
        sys.exit(report(data))
    else:
        sys.exit(markdown(data))


if __name__ == "__main__":
    main()
