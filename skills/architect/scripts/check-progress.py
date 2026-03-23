#!/usr/bin/env python3
"""Scan the spec/ directory and report webapp-architect pipeline progress (Steps 10-17).

Checks Steps 10-17 across all detected apps and suggests the next step to work on.
Verifies .blueprint-meta.json prerequisite before reporting.
"""

import argparse
import json
import os
from pathlib import Path

# Tier 3 per-app single files (Steps 10, 12-14)
APP_SPEC_FILES = {
    10: ("Information Architecture", "ia-spec.md"),
    12: ("State & Interaction", "state-interaction.md"),
    13: ("API Contracts", "api-contracts.md"),
    14: ("Authorization Policy", "authorization.md"),
}

# Tier 3 per-app directories (Step 11)
APP_DIRS = {
    11: ("Page Patterns", "pages", ".md"),
}

# Tier 4 labels (Steps 15-17)
TIER4_LABELS = {
    15: "Spec Validator",
    16: "Generation Briefs",
    17: "Seed Data",
}


def count_files(directory: Path, suffix: str) -> int:
    """Count files in a directory matching the given suffix."""
    if not directory.is_dir():
        return 0
    return sum(1 for f in directory.iterdir() if f.is_file() and f.name.endswith(suffix))


def check_prerequisites(spec_dir: Path) -> dict:
    """Check that .blueprint-meta.json exists and Steps 1-9 are complete."""
    meta_path = spec_dir / ".blueprint-meta.json"
    result = {"exists": False, "complete": False, "meta": None}

    if not meta_path.is_file():
        return result

    result["exists"] = True
    try:
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)
        result["meta"] = meta
        steps = meta.get("steps_completed", [])
        result["complete"] = all(s in steps for s in range(1, 10))
    except (json.JSONDecodeError, KeyError):
        pass

    return result


def check_domain_files(spec_dir: Path) -> dict:
    """Check essential domain files exist (fallback if no .blueprint-meta.json)."""
    return {
        "domain_model": (spec_dir / "suite" / "domain-model.md").is_file(),
        "has_apps": (spec_dir / "apps").is_dir() and any(
            (spec_dir / "apps" / d.name / "archetype.md").is_file()
            for d in (spec_dir / "apps").iterdir()
            if d.is_dir()
        ) if (spec_dir / "apps").is_dir() else False,
        "has_features": any(
            count_files(spec_dir / "apps" / d.name / "features", ".feature.md") > 0
            for d in (spec_dir / "apps").iterdir()
            if d.is_dir()
        ) if (spec_dir / "apps").is_dir() else False,
    }


def check_app(spec_dir: Path, app_name: str) -> dict:
    """Check Steps 10-17 completion for a single app."""
    app_dir = spec_dir / "apps" / app_name
    result = {"tier3": {}, "tier4": {}}

    # Tier 3 — single files (Steps 10, 12-14)
    for step, (_, fname) in APP_SPEC_FILES.items():
        result["tier3"][step] = {"exists": (app_dir / fname).is_file(), "count": None}

    # Tier 3 — directories (Step 11)
    for step, (_, dirname, suffix) in APP_DIRS.items():
        d = app_dir / dirname
        n = count_files(d, suffix)
        result["tier3"][step] = {"exists": n > 0, "count": n}

    # Tier 4 — validation reports (Step 15)
    val_dir = spec_dir / "validation" / "reports" / app_name
    result["tier4"][15] = (val_dir / "completeness-score.md").is_file()

    # Tier 4 — generation briefs (Step 16)
    gen_dir = app_dir / "generation-briefs"
    result["tier4"][16] = (gen_dir / "_build-order.md").is_file()

    # Tier 4 — seed data (Step 17)
    result["tier4"][17] = (app_dir / "seed-data.md").is_file()

    return result


def detect_apps(spec_dir: Path) -> list[str]:
    """Discover app directories under spec/apps/."""
    apps_dir = spec_dir / "apps"
    if not apps_dir.is_dir():
        return []
    return sorted(d.name for d in apps_dir.iterdir() if d.is_dir())


def suggest_next(apps: list[str], app_results: dict) -> str:
    """Determine the lowest-numbered incomplete step across all apps."""
    if not apps:
        return "No apps detected. Ensure spec/apps/<app_name>/ exists with archetype.md."

    for app in apps:
        r = app_results[app]
        for step in sorted(r["tier3"]):
            if not r["tier3"][step]["exists"]:
                label = APP_DIRS.get(step, (None,))[0] or APP_SPEC_FILES.get(step, (None,))[0]
                return f"Step {step} — {label} (app: {app})"
        for step in sorted(r["tier4"]):
            if not r["tier4"][step]:
                label = TIER4_LABELS.get(step, f"Step {step}")
                return f"Step {step} — {label} (app: {app})"

    return "All steps (10-17) complete!"


def main():
    parser = argparse.ArgumentParser(description="Check webapp-architect pipeline progress (Steps 10-17)")
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
        print("No pipeline progress to report. Run webapp-blueprint first to complete Steps 1-9.")
        return

    # --- Check prerequisites ---
    prereq = check_prerequisites(spec_dir)
    domain_files = check_domain_files(spec_dir)

    print("=== Webapp Architect Pipeline Progress (Steps 10-17) ===\n")

    print("Prerequisites (Steps 1-9):")
    if prereq["exists"]:
        if prereq["complete"]:
            print("  [\u2713] .blueprint-meta.json — all 9 steps completed")
        else:
            completed = prereq["meta"].get("steps_completed", []) if prereq["meta"] else []
            print(f"  [!] .blueprint-meta.json exists but only steps {completed} completed")
            print("      Run webapp-blueprint to complete remaining domain discovery steps.")
    else:
        print("  [!] .blueprint-meta.json not found")
        # Fall back to checking files directly
        if domain_files["domain_model"] and domain_files["has_apps"] and domain_files["has_features"]:
            print("      Domain files detected — Steps 1-9 may be complete but metadata is missing.")
            print("      Consider running webapp-blueprint to generate .blueprint-meta.json.")
        else:
            print("      Run webapp-blueprint first to complete domain discovery (Steps 1-9).")
            if not domain_files["domain_model"]:
                print("      Missing: suite/domain-model.md")
            if not domain_files["has_apps"]:
                print("      Missing: at least one app with archetype.md")
            if not domain_files["has_features"]:
                print("      Missing: at least one app with .feature.md files")

    # --- Check architect metadata ---
    architect_meta_path = spec_dir / ".architect-meta.json"
    if architect_meta_path.is_file():
        try:
            with open(architect_meta_path, encoding="utf-8") as f:
                arch_meta = json.load(f)
            tech = arch_meta.get("tech_stack", {})
            if tech:
                print(f"\n  Tech Stack: {tech.get('framework', '?')} / {tech.get('styling', '?')} / {tech.get('api', '?')}")
        except (json.JSONDecodeError, KeyError):
            pass
    else:
        print("\n  Tech stack not yet declared (.architect-meta.json missing)")

    # --- Detect and check apps ---
    apps = detect_apps(spec_dir)
    app_results = {app: check_app(spec_dir, app) for app in apps}

    if apps:
        print(f"\nDetected Apps: {', '.join(apps)}")
    else:
        print("\nNo apps detected under spec/apps/")

    for app in apps:
        r = app_results[app]
        print(f"\nApp: {app}")

        print("  Tier 3 (Steps 10-14):")
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

        print("  Tier 4 (Steps 15-17):")
        for step in sorted(r["tier4"]):
            label = TIER4_LABELS.get(step, f"Step {step}")
            mark = "\u2713" if r["tier4"][step] else " "
            print(f"    [{mark}] Step {step}: {label}")

    suggestion = suggest_next(apps, app_results)
    print(f"\nSuggested Next Step: {suggestion}")


if __name__ == "__main__":
    main()
