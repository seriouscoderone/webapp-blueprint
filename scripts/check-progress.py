#!/usr/bin/env python3
"""Scan the spec/ directory and report webapp blueprint pipeline progress.

Checks each of the 19 pipeline steps across all tiers and detected apps,
then suggests the next step to work on.
"""

import argparse
import os
from pathlib import Path

# Tier 1 suite-level files (Steps 1-5)
SUITE_FILES = {
    1: ("Domain Discovery", "domain-model.md"),
    2: ("Role & Permission Matrix", "role-permission-matrix.md"),
    3: ("Design System", "design-system.md"),
    4: ("Navigation Shell", "navigation-shell.md"),
    5: ("API & Event Contracts", "api-event-contracts.md"),
}

# Tier 2 per-app files (Steps 6-8)
APP_FILES = {
    6: ("App Archetype", "archetype.md"),
    7: ("Domain Refinement", "domain-refinement.md"),
    8: ("Role Refinement", "role-refinement.md"),
}

# Tier 3 per-app specs (Steps 9-15)
APP_DIRS = {
    9: ("BDD Features", "features", ".feature.md"),
    11: ("Page Specifications", "pages", ".md"),
    12: ("Component Specifications", "components", ".md"),
}
APP_SPEC_FILES = {
    10: ("Information Architecture", "ia-spec.md"),
    13: ("State & Interaction", "state-interaction.md"),
    14: ("API Contracts", "api-contracts.md"),
    15: ("Authorization Spec", "authorization.md"),
}

# Tier 4 validation outputs (Steps 16-19)
VALIDATION_REPORTS = ["gap-report.md", "contradiction-report.md", "completeness-score.md"]

TIER4_LABELS = {
    16: "Validation & Gap Analysis",
    17: "Generation Briefs",
    18: "Seed Data Specification",
    19: "Blackbox Test Template",
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
    """Check Tier 2-4 completion for a single app."""
    app_dir = spec_dir / "apps" / app_name
    result = {"tier2": {}, "tier3": {}, "tier4": {}}

    # Tier 2
    for step, (_, fname) in APP_FILES.items():
        result["tier2"][step] = (app_dir / fname).is_file()

    # Tier 3 — single files
    for step, (_, fname) in APP_SPEC_FILES.items():
        result["tier3"][step] = {"exists": (app_dir / fname).is_file(), "count": None}

    # Tier 3 — directories with multiple files
    for step, (_, dirname, suffix) in APP_DIRS.items():
        d = app_dir / dirname
        n = count_files(d, suffix)
        result["tier3"][step] = {"exists": n > 0, "count": n}

    # Tier 4 — validation reports
    val_dir = spec_dir / "validation" / "reports" / app_name
    reports_exist = all((val_dir / r).is_file() for r in VALIDATION_REPORTS)
    result["tier4"][16] = reports_exist

    # Tier 4 — generation briefs
    gen_dir = app_dir / "generation-briefs"
    result["tier4"][17] = gen_dir.is_dir() and any(gen_dir.iterdir()) if gen_dir.is_dir() else False

    # Tier 4 — seed data (Step 18)
    result["tier4"][18] = (app_dir / "seed-data.md").is_file()

    # Tier 4 — blackbox test template (Step 19) — suite-scoped file
    blackbox_dir = spec_dir.parent / "blackbox" / "templates"
    suite_template_exists = blackbox_dir.is_dir() and any(
        f.is_file() and f.name.endswith("_test.template.json")
        for f in blackbox_dir.iterdir()
    )
    result["tier4"][19] = suite_template_exists

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
                label = APP_DIRS.get(step, (None,))[0] or APP_SPEC_FILES.get(step, (None,))[0]
                return f"Step {step} — {label} (app: {app})"
        for step in sorted(r["tier4"]):
            if not r["tier4"][step]:
                label = TIER4_LABELS.get(step, f"Step {step}")
                return f"Step {step} — {label} (app: {app})"

    return "All steps complete!"


def main():
    parser = argparse.ArgumentParser(description="Check webapp blueprint pipeline progress")
    parser.add_argument("--spec-dir", default="./spec", help="Path to spec directory (default: ./spec)")
    args = parser.parse_args()

    spec_dir = Path(args.spec_dir).resolve()
    if not spec_dir.is_dir():
        print(f"Spec directory not found: {spec_dir}")
        print("No pipeline progress to report. Start with Step 1 — Domain Discovery.")
        return

    tier1 = check_tier1(spec_dir)
    apps = detect_apps(spec_dir)
    app_results = {app: check_app(spec_dir, app) for app in apps}

    # --- Print report ---
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
        print(f"\nApp: {app}")

        print("  Tier 2:")
        for step in sorted(r["tier2"]):
            mark = "\u2713" if r["tier2"][step] else " "
            print(f"    [{mark}] Step {step}: {APP_FILES[step][0]}")

        print("  Tier 3:")
        for step in sorted(r["tier3"]):
            info = r["tier3"][step]
            if info["count"] is not None:
                label = APP_DIRS[step][0]
                mark = "\u2713" if info["exists"] else " "
                print(f"    [{mark}] Step {step}: {label} ({info['count']} files)")
            else:
                label = APP_SPEC_FILES[step][0]
                mark = "\u2713" if info["exists"] else " "
                print(f"    [{mark}] Step {step}: {label}")

        print("  Tier 4:")
        for step in sorted(r["tier4"]):
            label = TIER4_LABELS.get(step, f"Step {step}")
            mark = "\u2713" if r["tier4"][step] else " "
            print(f"    [{mark}] Step {step}: {label}")

    suggestion = suggest_next(tier1, apps, app_results)
    print(f"\nSuggested Next Step: {suggestion}")


if __name__ == "__main__":
    main()
