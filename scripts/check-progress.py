#!/usr/bin/env python3
"""Scan the spec/ directory and report webapp blueprint pipeline progress.

Checks each of the 9 pipeline steps across all tiers and detected apps,
then suggests the next step to work on.
"""

import argparse
import os
from pathlib import Path

# Tier 1 suite-level files (Steps 1-5)
SUITE_FILES = {
    1: ("Domain Discovery", "domain-model.md"),
    2: ("Role & Permission Matrix", "role-permission-matrix.md"),
    3: ("UI Conventions", "ui-conventions.md"),
    4: ("Navigation Shell", "navigation-shell.md"),
    5: ("Suite API Conventions", "api-event-contracts.md"),
}

# Tier 2 per-app files (Steps 6-8)
APP_FILES = {
    6: ("App Archetype", "archetype.md"),
    7: ("Domain Refinement", "domain-refinement.md"),
    8: ("Role Refinement", "role-refinement.md"),
}

# Tier 3 per-app directories (Step 9)
APP_DIRS = {
    9: ("BDD Features", "features", ".feature.md"),
}


def count_files(directory: Path, suffix: str) -> int:
    """Count files in a directory matching the given suffix."""
    if not directory.is_dir():
        return 0
    return sum(1 for f in directory.iterdir() if f.is_file() and f.name.endswith(suffix))


def check_tier1(spec_dir: Path) -> dict[int, bool]:
    """Check Tier 1 suite-level completion."""
    suite = spec_dir / "suite"
    return {step: (suite / fname).is_file() for step, (_, fname) in SUITE_FILES.items()}


def check_app(spec_dir: Path, app_name: str) -> dict:
    """Check Tier 2-3 completion for a single app."""
    app_dir = spec_dir / "apps" / app_name
    result = {"tier2": {}, "tier3": {}}

    # Tier 2
    for step, (_, fname) in APP_FILES.items():
        result["tier2"][step] = (app_dir / fname).is_file()

    # Tier 3 — directories with multiple files (Step 9)
    for step, (_, dirname, suffix) in APP_DIRS.items():
        d = app_dir / dirname
        n = count_files(d, suffix)
        result["tier3"][step] = {"exists": n > 0, "count": n}

    return result


def detect_apps(spec_dir: Path) -> list[str]:
    """Discover app directories under spec/apps/."""
    apps_dir = spec_dir / "apps"
    if not apps_dir.is_dir():
        return []
    return sorted(d.name for d in apps_dir.iterdir() if d.is_dir())


def suggest_next(tier1: dict, apps: list[str], app_results: dict) -> str:
    """Determine the lowest-numbered incomplete step."""
    # Check Tier 1 first
    for step in sorted(SUITE_FILES):
        if not tier1[step]:
            return f"Step {step} — {SUITE_FILES[step][0]}"

    if not apps:
        return "No apps detected. Create spec/apps/<app_name>/ and run Step 6 — App Archetype"

    # Check each app in order
    for app in apps:
        r = app_results[app]
        for step in sorted(r["tier2"]):
            if not r["tier2"][step]:
                return f"Step {step} — {APP_FILES[step][0]} (app: {app})"
        for step in sorted(r["tier3"]):
            if not r["tier3"][step]["exists"]:
                label = APP_DIRS.get(step, (None,))[0]
                return f"Step {step} — {label} (app: {app})"

    return "All 9 steps complete! Run webapp-architect for technical specification."


def main():
    parser = argparse.ArgumentParser(description="Check webapp blueprint pipeline progress")
    parser.add_argument("--project-dir", default=None, help="Project root directory (sets --spec-dir default to <project-dir>/spec)")
    parser.add_argument("--spec-dir", default=None, help="Path to spec directory (default: ./spec or <project-dir>/spec)")
    args = parser.parse_args()

    if args.project_dir is not None:
        project_dir = Path(args.project_dir).resolve()
        spec_dir = Path(args.spec_dir).resolve() if args.spec_dir else project_dir / "spec"
    else:
        spec_dir = Path(args.spec_dir).resolve() if args.spec_dir else Path("./spec").resolve()
    if not spec_dir.is_dir():
        print(f"Spec directory not found: {spec_dir}")
        print("No pipeline progress to report. Start with Step 1 — Domain Discovery.")
        return

    tier1 = check_tier1(spec_dir)
    apps = detect_apps(spec_dir)
    app_results = {app: check_app(spec_dir, app) for app in apps}

    # --- Print report ---
    total_steps = 5  # Tier 1 suite steps
    completed_steps = sum(1 for v in tier1.values() if v)

    print("=== Webapp Blueprint Pipeline Progress ===\n")
    print("Tier 1 — Suite Level:")
    for step in sorted(SUITE_FILES):
        mark = "\u2713" if tier1[step] else " "
        label, fname = SUITE_FILES[step]
        print(f"  [{mark}] Step {step}: {label} (suite/{fname})")

    if apps:
        print(f"\nDetected Apps: {', '.join(apps)}")
    else:
        print("\nNo apps detected under spec/apps/")

    for app in apps:
        r = app_results[app]
        app_total = 4  # Steps 6-9
        app_completed = 0

        print(f"\nApp: {app}")

        print("  Tier 2:")
        for step in sorted(r["tier2"]):
            mark = "\u2713" if r["tier2"][step] else " "
            if r["tier2"][step]:
                app_completed += 1
            print(f"    [{mark}] Step {step}: {APP_FILES[step][0]}")

        print("  Tier 3:")
        for step in sorted(r["tier3"]):
            info = r["tier3"][step]
            label = APP_DIRS[step][0]
            mark = "\u2713" if info["exists"] else " "
            if info["exists"]:
                app_completed += 1
            print(f"    [{mark}] Step {step}: {label} ({info['count']} files)")

        total_steps += app_total
        completed_steps += app_completed

    print(f"\nProgress: {completed_steps}/{total_steps} steps complete")

    suggestion = suggest_next(tier1, apps, app_results)
    print(f"Suggested Next Step: {suggestion}")


if __name__ == "__main__":
    main()
