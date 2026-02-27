#!/usr/bin/env python3
"""Poll for webapp-blueprint-test results.

Waits for the test agent to create the final_test_results/ directory inside
the given build's folder, indicating all scenarios have been executed.

Usage:
    python3 scripts/wait-for-results.py --build-token TOKEN [--timeout 600] [--interval 30]

Exit codes:
    0  Final results directory found — test run is complete
    1  Timeout expired before results appeared — treat as test infrastructure failure
"""

import argparse
import sys
import time
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Poll for webapp-blueprint-test results"
    )
    parser.add_argument("--build-token", required=True, help="Build token (subdirectory under blackbox/builds/)")
    parser.add_argument("--timeout", type=int, default=600, help="Seconds before giving up (default: 600)")
    parser.add_argument("--interval", type=int, default=30, help="Seconds between status prints (default: 30)")
    parser.add_argument(
        "--blackbox-dir",
        default="./blackbox",
        help="Path to blackbox directory (default: ./blackbox)",
    )
    args = parser.parse_args()

    blackbox_dir = Path(args.blackbox_dir).resolve()
    results_dir = blackbox_dir / "builds" / args.build_token / "final_test_results"

    print(f"Waiting for test results: {results_dir}")
    print(f"Timeout: {args.timeout}s | Check interval: {args.interval}s")

    start = time.monotonic()
    while True:
        if results_dir.is_dir():
            elapsed = time.monotonic() - start
            print(f"Test results found after {elapsed:.0f}s — {results_dir}")
            return 0

        elapsed = time.monotonic() - start
        if elapsed >= args.timeout:
            print(
                f"ERROR: Timeout after {args.timeout}s — "
                f"final_test_results/ not found at {results_dir}"
            )
            print("Check the webapp-blueprint-test session for errors.")
            return 1

        minutes, seconds = divmod(int(elapsed), 60)
        print(f"Waiting for test results... {minutes}m {seconds}s elapsed")
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
