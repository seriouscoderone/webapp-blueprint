#!/usr/bin/env python3
"""Generate a machine-readable JSON blackbox test template from BDD feature files (Step 19).

Reads all .feature.md files for a given app and produces a JSON template with
one entry per scenario, all initialized to UNTESTED status. The output file is
always overwritten — it always reflects the current feature files with fresh defaults.

Usage:
    python3 scripts/generate-blackbox-template.py --app my-app [--spec-dir ./spec] [--output-dir ./blackbox/templates]
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


def build_template(app_name: str, spec_dir: Path) -> tuple[dict, int, int]:
    """Build the full JSON template dict from all feature files.

    Returns (template_dict, feature_count, scenario_count).
    Raises FileNotFoundError if features directory or files are missing.
    """
    features_dir = spec_dir / "apps" / app_name / "features"

    if not features_dir.is_dir():
        raise FileNotFoundError(f"Features directory not found: {features_dir}")

    feature_files = sorted(
        f for f in features_dir.iterdir()
        if f.is_file() and f.name.endswith(".feature.md")
    )

    if not feature_files:
        raise FileNotFoundError(f"No .feature.md files found in {features_dir}")

    # Derive a display path for _meta.spec_dir (relative to project root)
    try:
        spec_display = str(features_dir.relative_to(spec_dir.parent)) + "/"
    except ValueError:
        spec_display = str(features_dir) + "/"

    template: dict = {
        "_meta": {
            "app": app_name,
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "spec_dir": spec_display,
            "schema_version": "1.0",
        }
    }

    total_scenarios = 0
    feature_count = 0

    for fpath in feature_files:
        feature_name, scenarios = parse_feature_file(fpath)
        if feature_name is None:
            continue

        feature_count += 1
        template[feature_name] = {
            "_meta": {
                "file": fpath.name,
                "scenario_count": len(scenarios),
            }
        }

        for scenario_name, stype in scenarios:
            template[feature_name][scenario_name] = {
                "_type": stype,
                "status": "UNTESTED",
                "message": "Untested",
                "error_detail": None,
                "steps_to_reproduce": [],
                "last_run": None,
                "build_id": None,
            }
            total_scenarios += 1

    return template, feature_count, total_scenarios


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a machine-readable JSON blackbox test template from BDD feature files (Step 19)"
    )
    parser.add_argument("--app", required=True, help="App name (must exist under spec/apps/)")
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

    app_dir = spec_dir / "apps" / args.app
    if not app_dir.is_dir():
        print(f"ERROR: App directory not found: {app_dir}")
        return 1

    try:
        template, feature_count, scenario_count = build_template(args.app, spec_dir)
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{args.app}_test.template.json"
    output_path.write_text(json.dumps(template, indent=2) + "\n", encoding="utf-8")

    print(f"Generated blackbox test template for '{args.app}'")
    print(f"  Features : {feature_count}")
    print(f"  Scenarios: {scenario_count}")
    print(f"  Output   : {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
