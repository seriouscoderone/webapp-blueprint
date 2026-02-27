#!/usr/bin/env python3
"""Generate a suite-scoped JSON blackbox test template from BDD feature files (Step 19).

Discovers all apps under spec/apps/ and reads their .feature.md files to produce
a single JSON template with one entry per scenario across every app, all initialized
to UNTESTED status. The output file is always overwritten — it always reflects the
current feature files with fresh defaults.

Usage:
    python3 scripts/generate-blackbox-template.py --suite acme [--spec-dir ./spec] [--output-dir ./blackbox/templates]
"""

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------------------------
# Regex patterns — follows validate-spec.py heuristic style
# ---------------------------------------------------------------------------

FEATURE_RE = re.compile(r'^#\s+Feature:\s+(.+)$', re.MULTILINE)
SCENARIO_RE = re.compile(r'^###\s+Scenario(?:\s+Outline)?:\s+(.+)$', re.MULTILINE)


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def parse_feature_file(path: Path) -> tuple[str | None, list[tuple[str, str]]]:
    """Parse a .feature.md file.

    Returns (feature_name, [(scenario_name, scenario_type), ...]).
    scenario_type is "scenario" or "scenario_outline".
    Returns (None, []) if no Feature heading is found.
    """
    text = path.read_text(encoding="utf-8", errors="replace")

    feature_match = FEATURE_RE.search(text)
    if not feature_match:
        return None, []

    feature_name = feature_match.group(1).strip()

    scenarios = []
    for m in SCENARIO_RE.finditer(text):
        scenario_name = m.group(1).strip()
        stype = "scenario_outline" if "Outline" in m.group(0) else "scenario"
        scenarios.append((scenario_name, stype))

    return feature_name, scenarios


def build_template(suite_name: str, spec_dir: Path) -> tuple[dict, int, int, int]:
    """Build the full JSON template dict from all feature files across all apps.

    Returns (template_dict, total_apps, total_features, total_scenarios).
    Raises FileNotFoundError if no apps or no feature files are found.
    """
    apps_dir = spec_dir / "apps"
    if not apps_dir.is_dir():
        raise FileNotFoundError(f"Apps directory not found: {apps_dir}")

    app_names = sorted(d.name for d in apps_dir.iterdir() if d.is_dir())
    if not app_names:
        raise FileNotFoundError(f"No app directories found in {apps_dir}")

    template: dict = {
        "_meta": {
            "suite": suite_name,
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "schema_version": "1.0",
        }
    }

    total_apps = 0
    total_features = 0
    total_scenarios = 0
    found_any_feature = False

    for app_name in app_names:
        features_dir = apps_dir / app_name / "features"
        if not features_dir.is_dir():
            continue

        feature_files = sorted(
            f for f in features_dir.iterdir()
            if f.is_file() and f.name.endswith(".feature.md")
        )
        if not feature_files:
            continue

        found_any_feature = True
        total_apps += 1

        # Derive a display path for _meta.spec_dir (relative to project root)
        try:
            spec_display = str(features_dir.relative_to(spec_dir.parent)) + "/"
        except ValueError:
            spec_display = str(features_dir) + "/"

        app_feature_count = 0
        app_scenario_count = 0
        app_entry: dict = {
            "_meta": {
                "spec_dir": spec_display,
                "feature_count": 0,  # updated below
            }
        }

        for fpath in feature_files:
            feature_name, scenarios = parse_feature_file(fpath)
            if feature_name is None:
                continue

            app_feature_count += 1
            app_entry[feature_name] = {
                "_meta": {
                    "file": fpath.name,
                    "scenario_count": len(scenarios),
                }
            }

            for scenario_name, stype in scenarios:
                app_entry[feature_name][scenario_name] = {
                    "_type": stype,
                    "status": "UNTESTED",
                    "message": "Untested",
                    "error_detail": None,
                    "steps_to_reproduce": [],
                    "last_run": None,
                    "build_id": None,
                }
                app_scenario_count += 1

        app_entry["_meta"]["feature_count"] = app_feature_count
        template[app_name] = app_entry

        total_features += app_feature_count
        total_scenarios += app_scenario_count

        print(f"  App '{app_name}': {app_feature_count} features, {app_scenario_count} scenarios")

    if not found_any_feature:
        raise FileNotFoundError(
            f"No .feature.md files found in any app under {apps_dir}"
        )

    return template, total_apps, total_features, total_scenarios


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a suite-scoped JSON blackbox test template from BDD feature files (Step 19)"
    )
    parser.add_argument("--suite", required=True, help="Suite name (e.g. 'acme', 'my-platform')")
    parser.add_argument("--spec-dir", default="./spec", help="Path to spec directory (default: ./spec)")
    parser.add_argument(
        "--output-dir",
        default="./blackbox/templates",
        help="Output directory for the template (default: ./blackbox/templates)",
    )
    args = parser.parse_args()

    spec_dir = Path(args.spec_dir).resolve()
    output_dir = Path(args.output_dir).resolve()

    if not spec_dir.is_dir():
        print(f"ERROR: Spec directory not found: {spec_dir}")
        return 1

    apps_dir = spec_dir / "apps"
    if not apps_dir.is_dir():
        print(f"ERROR: Apps directory not found: {apps_dir}")
        return 1

    print(f"Generating suite-scoped blackbox test template for suite '{args.suite}'...")

    try:
        template, total_apps, total_features, total_scenarios = build_template(args.suite, spec_dir)
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{args.suite}_test.template.json"
    output_path.write_text(json.dumps(template, indent=2) + "\n", encoding="utf-8")

    print(f"\nGenerated suite-scoped blackbox test template for suite '{args.suite}'")
    print(f"  Apps     : {total_apps}")
    print(f"  Features : {total_features}")
    print(f"  Scenarios: {total_scenarios}")
    print(f"  Output   : {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
