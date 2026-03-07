#!/usr/bin/env python3
"""Poll for a new build to test.

Watches blackbox/builds/ for a subdirectory that has a manifest.json but
no final_test_results/ directory — indicating a build is ready for testing.

Usage:
    python3 scripts/wait-for-build.py [--blackbox-dir ./blackbox] [--timeout 3600] [--interval 15]

Exit codes:
    0  A ready build was found — prints the build_token to stdout
    1  Timeout expired before a build appeared
"""

import argparse
import sys
import time
from pathlib import Path


def find_ready_build(builds_dir: Path) -> str | None:
    """Return the build_token of the most recently created ready build, or None."""
    if not builds_dir.is_dir():
        return None

    candidates = []
    for d in builds_dir.iterdir():
        if not d.is_dir():
            continue
        if (d / "manifest.json").exists() and not (d / "final_test_results").exists():
            candidates.append(d)

    if not candidates:
        return None

    # Pick the most recently modified
    return max(candidates, key=lambda d: d.stat().st_mtime).name


def main() -> int:
    parser = argparse.ArgumentParser(description="Poll for a new build to test")
    parser.add_argument(
        "--blackbox-dir",
        default="./blackbox",
        help="Path to blackbox directory (default: ./blackbox)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=3600,
        help="Seconds before giving up (default: 3600)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=15,
        help="Seconds between polls (default: 15)",
    )
    args = parser.parse_args()

    builds_dir = Path(args.blackbox_dir).resolve() / "builds"

    print(f"Polling for new build in: {builds_dir}")
    print(f"Timeout: {args.timeout}s | Interval: {args.interval}s")

    start = time.monotonic()
    while True:
        token = find_ready_build(builds_dir)
        if token:
            print(token)  # machine-readable: build_token on its own line
            return 0

        elapsed = time.monotonic() - start
        if elapsed >= args.timeout:
            print(f"ERROR: Timeout after {args.timeout}s — no ready build found in {builds_dir}", file=sys.stderr)
            return 1

        minutes, seconds = divmod(int(elapsed), 60)
        print(f"Waiting for new build... {minutes}m {seconds}s elapsed", file=sys.stderr)
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
