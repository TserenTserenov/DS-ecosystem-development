#!/usr/bin/env python3
# see DP.METHOD.054, peer-session 2026-06-13-31-wp419-f5-generator-design
#
# --validate: E1a-E1d structural checks; exit 1 on violations.
#             In Week Close call as: registry-catalog.py --validate || echo "⚠️ E1"
#             In CI (after DP.METHOD.054 activation): exit 1 blocks pipeline.
# --report:   freshness flags (90d) + status summary; stdout for Week Close log.

import sys
import yaml
from pathlib import Path
from datetime import date, datetime

CATALOG_PATH = Path(__file__).parent.parent / "0.9.Inbox" / "WP-419-registry-catalog-draft.yaml"
FRESHNESS_DAYS = 90
OWNER_TBD = {"N/A", "TBD", "команда"}
REQUIRED_FIELDS = {"name", "status", "owner"}


def load_catalog():
    with open(CATALOG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def check_e1_hard(entry: dict) -> list[str]:
    """Return list of E1-hard violations for one catalog entry."""
    violations = []
    name = entry.get("name", "<unnamed>")

    # E1d: required fields present
    for field in REQUIRED_FIELDS:
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


def validate(data: dict) -> int:
    registries = data.get("registries", [])
    all_violations = []
    for entry in registries:
        all_violations.extend(check_e1_hard(entry))

    if all_violations:
        print("registry-catalog E1-hard violations:", file=sys.stderr)
        for v in all_violations:
            print(f"  {v}", file=sys.stderr)
        return 1

    print(f"registry-catalog --validate: OK ({len(registries)} entries, 0 E1 violations)")
    return 0


def report(data: dict) -> int:
    registries = data.get("registries", [])
    today = date.today()
    stale = []
    counts = {"active": 0, "drifting": 0, "dead": 0, "missing": 0, "other": 0}

    for entry in registries:
        status = entry.get("status", "other")
        counts[status if status in counts else "other"] += 1

        lv = entry.get("last_verified")
        if lv and lv != "null":
            try:
                lv_date = datetime.strptime(str(lv), "%Y-%m-%d").date()
                age = (today - lv_date).days
                if age > FRESHNESS_DAYS:
                    stale.append((entry.get("name", "<unnamed>"), age, entry.get("risk_priority", "?")))
            except ValueError:
                print(f"  ⚠️ bad last_verified date in '{entry.get('name', '?')}': {lv!r}", file=sys.stderr)

    print(f"\n## Registry Catalog — Week Close report ({today})")
    print(f"Entries: {len(registries)} total | "
          f"active={counts['active']} drifting={counts['drifting']} "
          f"dead={counts['dead']} missing={counts['missing']}")

    if stale:
        stale.sort(key=lambda x: -x[1])
        print(f"\nFreshness flags (>{FRESHNESS_DAYS}d not verified): {len(stale)}")
        for name, age, priority in stale[:10]:
            print(f"  {name}: {age}d (риск={priority})")
        if len(stale) > 10:
            print(f"  ... и ещё {len(stale)-10}")
    else:
        print("Freshness: все записи проверены менее 90 дней назад")

    return 0


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("--validate", "--report"):
        print("Usage: registry-catalog.py --validate | --report", file=sys.stderr)
        sys.exit(2)

    data = load_catalog()
    if sys.argv[1] == "--validate":
        sys.exit(validate(data))
    else:
        sys.exit(report(data))


if __name__ == "__main__":
    main()
