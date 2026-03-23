#!/usr/bin/env python3
"""
Parse Playwright JSON reporter output and update .prover-meta.json.

Usage:
    python3 parse-playwright-results.py \
        --results-file test-results/results.json \
        --meta-file .prover-meta.json \
        --cycle 1 \
        --app admin-portal \
        --project-dir .

Exit codes:
    0 — All scenarios passed
    1 — Some scenarios failed or are exhausted
    2 — File/parse error
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

EXHAUSTION_THRESHOLD = 3

STATUS_MAP = {
    "passed": "PASSED",
    "failed": "FAILED",
    "timedOut": "ERROR",
    "skipped": "NOT_RUN",
    "interrupted": "ERROR",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Parse Playwright JSON results and update prover metadata"
    )
    parser.add_argument(
        "--results-file",
        required=True,
        help="Path to Playwright JSON reporter output (e.g., test-results/results.json)",
    )
    parser.add_argument(
        "--meta-file",
        required=True,
        help="Path to .prover-meta.json (created if missing)",
    )
    parser.add_argument(
        "--cycle",
        type=int,
        required=True,
        help="Current cycle number (1-based)",
    )
    parser.add_argument(
        "--app",
        required=True,
        help="Application name (e.g., admin-portal)",
    )
    parser.add_argument(
        "--project-dir",
        default=".",
        help="Project root directory (default: current directory)",
    )
    return parser.parse_args()


def load_json(path: str) -> dict[str, Any] | None:
    """Load a JSON file, return None if missing or invalid."""
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse {path}: {e}", file=sys.stderr)
        return None


def save_json(path: str, data: dict[str, Any]) -> None:
    """Write JSON to file with pretty formatting."""
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def extract_scenarios(results: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Walk the Playwright JSON reporter structure and extract per-scenario results.

    Returns a list of dicts:
        {
            "feature": "Feature Name",
            "scenario": "Scenario Title",
            "status": "PASSED" | "FAILED" | "ERROR" | "NOT_RUN",
            "duration": 1234,
            "error": "error message" | None,
            "trace": "path/to/trace.zip" | None,
        }
    """
    scenarios = []

    def walk_suites(suites: list[dict], feature_name: str = "") -> None:
        for suite in suites:
            title = suite.get("title", "")

            # Detect feature-level suite (title starts with "Feature:")
            current_feature = feature_name
            if title.startswith("Feature:") or (
                not feature_name and title and not title.endswith(".feature")
            ):
                # Clean up feature title
                current_feature = title.replace("Feature:", "").strip() or title

            # Process specs (scenarios)
            for spec in suite.get("specs", []):
                scenario_title = spec.get("title", "Unknown")

                # A spec may have multiple tests (e.g., across projects/browsers)
                # We take the worst status across all tests
                worst_status = "PASSED"
                total_duration = 0
                error_msg = None
                trace_path = None

                for test in spec.get("tests", []):
                    for result in test.get("results", []):
                        raw_status = result.get("status", "failed")
                        mapped = STATUS_MAP.get(raw_status, "ERROR")
                        total_duration += result.get("duration", 0)

                        # Track worst status: ERROR > FAILED > NOT_RUN > PASSED
                        priority = {"PASSED": 0, "NOT_RUN": 1, "FAILED": 2, "ERROR": 3}
                        if priority.get(mapped, 3) > priority.get(worst_status, 0):
                            worst_status = mapped

                        # Capture error from first failure
                        if mapped in ("FAILED", "ERROR") and error_msg is None:
                            err = result.get("error", {})
                            if isinstance(err, dict):
                                error_msg = err.get("message", str(err))
                            elif isinstance(err, str):
                                error_msg = err

                        # Capture trace path
                        for att in result.get("attachments", []):
                            if att.get("name") == "trace" and att.get("path"):
                                trace_path = att["path"]

                scenarios.append(
                    {
                        "feature": current_feature or "Unknown Feature",
                        "scenario": scenario_title,
                        "status": worst_status,
                        "duration": total_duration,
                        "error": error_msg,
                        "trace": trace_path,
                    }
                )

            # Recurse into nested suites
            if suite.get("suites"):
                walk_suites(suite["suites"], current_feature)

    # The top-level structure has suites at the root or under projects
    # Handle both structures
    top_suites = results.get("suites", [])
    if top_suites:
        walk_suites(top_suites)

    # Also check projects (Playwright v1.40+ structure)
    for project in results.get("config", {}).get("projects", []):
        if "suites" in project:
            walk_suites(project["suites"])

    # Handle the common structure where suites are nested under a root suite
    if not scenarios:
        # Try walking from the root differently
        for key in ("suites", "specs"):
            if key in results:
                walk_suites(results[key] if isinstance(results[key], list) else [results])
                if scenarios:
                    break

    return scenarios


def group_scenario_outlines(
    scenarios: list[dict[str, Any]],
) -> dict[str, dict[str, dict[str, Any]]]:
    """
    Group scenarios by feature and base title.

    For Scenario Outlines, multiple results may share the same base title
    (with different example row suffixes). We group them and take the worst status.

    Returns:
        {
            "Feature Name": {
                "Scenario Title": {
                    "status": "PASSED"|"FAILED"|...,
                    "duration": 1234,
                    "error": "..." | None,
                    "trace": "..." | None,
                }
            }
        }
    """
    grouped: dict[str, dict[str, dict[str, Any]]] = {}
    priority = {"PASSED": 0, "NOT_RUN": 1, "FAILED": 2, "ERROR": 3}

    for s in scenarios:
        feature = s["feature"]
        # Strip example row indicators from scenario outline titles
        # Common patterns: "Title (Example #1)", "Title -- row 0"
        title = s["scenario"]
        base_title = title
        for sep in [" (Example #", " -- ", " [", " Example "]:
            if sep in base_title:
                base_title = base_title[: base_title.index(sep)]

        if feature not in grouped:
            grouped[feature] = {}

        if base_title not in grouped[feature]:
            grouped[feature][base_title] = {
                "status": s["status"],
                "duration": s["duration"],
                "error": s["error"],
                "trace": s["trace"],
            }
        else:
            existing = grouped[feature][base_title]
            # Take worst status
            if priority.get(s["status"], 3) > priority.get(existing["status"], 0):
                existing["status"] = s["status"]
                if s["error"]:
                    existing["error"] = s["error"]
                if s["trace"]:
                    existing["trace"] = s["trace"]
            existing["duration"] += s["duration"]

    return grouped


def create_empty_meta(app: str, cycle: int) -> dict[str, Any]:
    """Create an empty .prover-meta.json structure."""
    return {
        "version": "1.0",
        "skill": "webapp-prover",
        "app": app,
        "status": "in_progress",
        "current_cycle": cycle,
        "max_cycles": 10,
        "base_url": os.environ.get("BASE_URL", "http://localhost:3000"),
        "summary": {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "exhausted": 0,
            "not_run": 0,
        },
        "features": {},
    }


def update_meta(
    meta: dict[str, Any],
    grouped: dict[str, dict[str, dict[str, Any]]],
    cycle: int,
) -> dict[str, Any]:
    """
    Update .prover-meta.json with results from the current cycle.
    """
    meta["current_cycle"] = cycle

    features = meta.get("features", {})

    for feature_name, scenarios in grouped.items():
        if feature_name not in features:
            features[feature_name] = {"source": "", "scenarios": {}}

        for scenario_name, result in scenarios.items():
            scenario_data = features[feature_name]["scenarios"].get(
                scenario_name,
                {
                    "status": "NOT_RUN",
                    "history": [],
                    "consecutive_failures": 0,
                    "exhausted": False,
                },
            )

            # Skip exhausted scenarios
            if scenario_data.get("exhausted", False):
                continue

            # Build history entry
            history_entry: dict[str, Any] = {
                "cycle": cycle,
                "status": result["status"],
            }
            if result["error"]:
                # Truncate long error messages
                error_text = result["error"]
                if len(error_text) > 500:
                    error_text = error_text[:500] + "..."
                history_entry["error"] = error_text
            if result["trace"]:
                history_entry["trace"] = result["trace"]

            scenario_data["history"].append(history_entry)
            scenario_data["status"] = result["status"]

            # Update consecutive failures
            if result["status"] in ("FAILED", "ERROR"):
                scenario_data["consecutive_failures"] = (
                    scenario_data.get("consecutive_failures", 0) + 1
                )
                if scenario_data["consecutive_failures"] >= EXHAUSTION_THRESHOLD:
                    scenario_data["exhausted"] = True
                    scenario_data["status"] = "EXHAUSTED"
            else:
                scenario_data["consecutive_failures"] = 0

            features[feature_name]["scenarios"][scenario_name] = scenario_data

    meta["features"] = features

    # Recompute summary
    total = 0
    passed = 0
    failed = 0
    exhausted = 0
    not_run = 0

    for feat in features.values():
        for sc in feat.get("scenarios", {}).values():
            total += 1
            status = sc.get("status", "NOT_RUN")
            if status == "PASSED":
                passed += 1
            elif status == "EXHAUSTED":
                exhausted += 1
            elif status in ("FAILED", "ERROR"):
                failed += 1
            else:
                not_run += 1

    meta["summary"] = {
        "total": total,
        "passed": passed,
        "failed": failed,
        "exhausted": exhausted,
        "not_run": not_run,
    }

    # Determine overall status
    if total == 0:
        meta["status"] = "in_progress"
    elif passed == total:
        meta["status"] = "passed"
    elif failed == 0 and exhausted > 0:
        meta["status"] = "partial"
    elif cycle >= meta.get("max_cycles", 10):
        meta["status"] = "failed"
    else:
        meta["status"] = "in_progress"

    return meta


def main() -> int:
    args = parse_args()

    project_dir = Path(args.project_dir).resolve()
    results_path = (
        Path(args.results_file)
        if os.path.isabs(args.results_file)
        else project_dir / args.results_file
    )
    meta_path = (
        Path(args.meta_file)
        if os.path.isabs(args.meta_file)
        else project_dir / args.meta_file
    )

    # Load Playwright results
    results = load_json(str(results_path))
    if results is None:
        print(f"ERROR: Cannot read results file: {results_path}", file=sys.stderr)
        return 2

    # Extract and group scenarios
    scenarios = extract_scenarios(results)
    if not scenarios:
        print(
            "WARNING: No scenarios found in results file. "
            "Check that tests ran and the JSON reporter is configured.",
            file=sys.stderr,
        )
        # Still update meta to record the empty cycle
        grouped: dict[str, dict[str, dict[str, Any]]] = {}
    else:
        grouped = group_scenario_outlines(scenarios)

    # Load or create meta
    meta = load_json(str(meta_path))
    if meta is None:
        meta = create_empty_meta(args.app, args.cycle)

    # Update meta with results
    meta = update_meta(meta, grouped, args.cycle)

    # Save meta
    save_json(str(meta_path), meta)

    # Print summary
    summary = meta["summary"]
    print(f"\n{'='*50}")
    print(f"  Prover Cycle {args.cycle} — {args.app}")
    print(f"{'='*50}")
    print(f"  Total:     {summary['total']}")
    print(f"  Passed:    {summary['passed']}")
    print(f"  Failed:    {summary['failed']}")
    print(f"  Exhausted: {summary['exhausted']}")
    print(f"  Not Run:   {summary['not_run']}")
    print(f"  Status:    {meta['status']}")
    print(f"{'='*50}\n")

    # Print failures for quick reference
    if summary["failed"] > 0:
        print("FAILURES:")
        for feat_name, feat in meta["features"].items():
            for sc_name, sc in feat.get("scenarios", {}).items():
                if sc["status"] in ("FAILED", "ERROR"):
                    latest = sc["history"][-1] if sc["history"] else {}
                    error = latest.get("error", "Unknown error")
                    # Truncate for display
                    if len(error) > 120:
                        error = error[:120] + "..."
                    print(f"  [{sc['status']}] {feat_name} > {sc_name}")
                    print(f"         {error}")
        print()

    # Print exhausted scenarios
    if summary["exhausted"] > 0:
        print("EXHAUSTED (3 consecutive failures — skipped):")
        for feat_name, feat in meta["features"].items():
            for sc_name, sc in feat.get("scenarios", {}).items():
                if sc.get("exhausted"):
                    print(f"  {feat_name} > {sc_name}")
        print()

    # Exit code
    if summary["passed"] == summary["total"] and summary["total"] > 0:
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
