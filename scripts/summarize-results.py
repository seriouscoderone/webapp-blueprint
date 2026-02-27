#!/usr/bin/env python3
"""Summarize webapp-blueprint-test results.

Reads final_test_results/results.json for a given build token and prints
PASSED/FAILED/UNTESTED counts per app, a suite total, and lists FAILED scenarios.

Usage:
    python3 scripts/summarize-results.py --build-token TOKEN [--blackbox-dir ./blackbox]
    python3 scripts/summarize-results.py --results-file path/to/results.json

Exit codes:
    0  All scenarios PASSED (no FAILEDs, no UNTESTEDs)
    1  One or more FAILED or UNTESTED scenarios
    2  Results file not found or unreadable
"""

import argparse
import json
import sys
from pathlib import Path


def is_meta(key: str) -> bool:
    return key == "_meta"


def summarize_app(app_data: dict, app_name: str) -> tuple[int, int, int, list[str]]:
    """Return (passed, failed, untested, [failed_titles]) for one app."""
    passed = failed = untested = 0
    failed_titles: list[str] = []

    for feature_name, feature_data in app_data.items():
        if is_meta(feature_name):
            continue
        if not isinstance(feature_data, dict):
            continue

        for scenario_name, scenario_data in feature_data.items():
            if is_meta(scenario_name):
                continue
            if not isinstance(scenario_data, dict):
                continue

            status = scenario_data.get("status", "UNTESTED")
            if status == "PASSED":
                passed += 1
            elif status == "FAILED":
                failed += 1
                failed_titles.append(f"  [{app_name}] {feature_name} / {scenario_name}")
            else:
                untested += 1

    return passed, failed, untested, failed_titles


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize webapp-blueprint-test results")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--build-token", help="Build token (reads from blackbox/builds/{token}/final_test_results/results.json)")
    group.add_argument("--results-file", help="Direct path to results.json")
    parser.add_argument(
        "--blackbox-dir",
        default="./blackbox",
        help="Path to blackbox directory (default: ./blackbox)",
    )
    args = parser.parse_args()

    if args.results_file:
        results_path = Path(args.results_file).resolve()
    else:
        blackbox_dir = Path(args.blackbox_dir).resolve()
        results_path = blackbox_dir / "builds" / args.build_token / "final_test_results" / "results.json"

    if not results_path.is_file():
        print(f"ERROR: Results file not found: {results_path}")
        return 2

    try:
        data = json.loads(results_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        print(f"ERROR: Cannot read results file: {e}")
        return 2

    meta = data.get("_meta", {})
    suite = meta.get("suite", "unknown")
    build_token = meta.get("build_token", args.build_token or "unknown")
    tested_at = meta.get("tested_at", "unknown")

    print(f"=== Test Results: {suite} / {build_token} ===")
    print(f"Tested at: {tested_at}\n")

    total_passed = total_failed = total_untested = 0
    all_failed_titles: list[str] = []

    for app_name, app_data in data.items():
        if is_meta(app_name):
            continue
        if not isinstance(app_data, dict):
            continue

        passed, failed, untested, failed_titles = summarize_app(app_data, app_name)
        total_passed += passed
        total_failed += failed
        total_untested += untested
        all_failed_titles.extend(failed_titles)

        status_icon = "+" if failed == 0 and untested == 0 else "x"
        print(f"  [{status_icon}] {app_name}: {passed} passed, {failed} failed, {untested} untested")

    print(f"\nSuite Total: {total_passed} passed, {total_failed} failed, {total_untested} untested")

    if all_failed_titles:
        print("\nFailed Scenarios:")
        for title in all_failed_titles:
            print(title)

    if total_failed > 0 or total_untested > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
