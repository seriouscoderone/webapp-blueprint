#!/usr/bin/env python3
"""Convert .feature.md files to standard Gherkin .feature files.

Reads BDD feature specs written in the webapp-blueprint markdown format
and transforms them into valid Gherkin that can be consumed by Cucumber,
Behave, or any other BDD framework.

Usage:
    python3 scripts/feature-md-to-gherkin.py --app APP --project-dir DIR [--output-dir DIR] [--validate-only]
"""

import argparse
import re
import sys
from pathlib import Path


# Step keywords that get 4-space indent in Gherkin output
STEP_KEYWORDS = ("Given", "When", "Then", "And", "But")

# Patterns that indicate problems in .feature.md files
FORBIDDEN_PATTERNS = [
    (re.compile(r"\[.*?\]\(.*?\)"), "markdown link in step"),
    (re.compile(r"`[^`]+`"), "inline code backtick in step"),
    (re.compile(r"^\s*[-*]\s"), "bullet list inside scenario"),
    (re.compile(r"^#{4,}"), "nested heading below ### inside scenario"),
    (re.compile(r":\s*-{3,}\s*:"), "markdown alignment colons in table"),
]


def strip_bold(text: str) -> str:
    """Remove **bold** markers from text."""
    return re.sub(r"\*\*(.+?)\*\*", r"\1", text)


def strip_markdown_links(text: str) -> str:
    """Convert [text](url) to just text."""
    return re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)


def strip_backticks(text: str) -> str:
    """Remove inline code backticks."""
    return re.sub(r"`([^`]+)`", r"\1", text)


def is_step_line(line: str) -> bool:
    """Check if a line starts with a BDD step keyword."""
    stripped = line.strip()
    stripped = strip_bold(stripped)
    for kw in STEP_KEYWORDS:
        if stripped.startswith(kw + " ") or stripped == kw:
            return True
    return False


def is_table_row(line: str) -> bool:
    """Check if a line is a Gherkin examples table row."""
    stripped = line.strip()
    return stripped.startswith("|") and stripped.endswith("|")


def is_examples_line(line: str) -> bool:
    """Check if a line is an Examples: header."""
    stripped = line.strip()
    return stripped.lower().startswith("examples:")


def convert_feature_md(lines: list[str], feature_tag: str) -> list[str]:
    """Convert .feature.md lines to Gherkin .feature lines.

    Returns list of output lines (without trailing newlines).
    """
    output = []
    in_scenario = False
    in_user_story = False
    in_background = False
    in_examples = False
    skip_next_blockquote = False

    # Add feature tag
    output.append(f"@{feature_tag}")

    for line in lines:
        stripped = line.rstrip("\n").rstrip()

        # Rule 10: Strip horizontal rules
        if re.match(r"^-{3,}\s*$", stripped) or re.match(r"^\*{3,}\s*$", stripped):
            continue

        # Rule 1: # Feature: X -> Feature: X
        m = re.match(r"^#\s+Feature:\s*(.+)$", stripped)
        if m:
            output.append(f"Feature: {m.group(1)}")
            in_scenario = False
            in_user_story = False
            in_background = False
            in_examples = False
            continue

        # Rule 2: ## User Story -> free-text description
        if re.match(r"^##\s+User\s+Stor", stripped, re.IGNORECASE):
            in_user_story = True
            in_scenario = False
            in_background = False
            in_examples = False
            continue

        # Capture user story lines (As a / I want / So that)
        if in_user_story:
            if re.match(r"^##", stripped):
                # Next section heading — stop user story
                in_user_story = False
                # Fall through to process this heading below
            elif stripped == "":
                output.append("")
                continue
            else:
                # Indent user story lines with 2 spaces
                clean = strip_bold(stripped)
                clean = strip_markdown_links(clean)
                clean = strip_backticks(clean)
                output.append(f"  {clean}")
                continue

        # Rule 3: ## Background -> Background:
        if re.match(r"^##\s+Background", stripped, re.IGNORECASE):
            output.append("")
            output.append("  Background:")
            in_background = True
            in_scenario = False
            in_user_story = False
            in_examples = False
            skip_next_blockquote = True
            continue

        # Rule 4: ## Scenarios heading -> drop
        if re.match(r"^##\s+Scenarios?\s*$", stripped, re.IGNORECASE):
            in_background = False
            in_examples = False
            continue

        # Rule 5: ### Scenario: X -> Scenario: X
        m = re.match(r"^###\s+Scenario:\s*(.+)$", stripped)
        if m:
            output.append("")
            output.append(f"  Scenario: {m.group(1)}")
            in_scenario = True
            in_background = False
            in_user_story = False
            in_examples = False
            skip_next_blockquote = True
            continue

        # Rule 6: ### Scenario Outline: X -> Scenario Outline: X
        m = re.match(r"^###\s+Scenario\s+Outline:\s*(.+)$", stripped)
        if m:
            output.append("")
            output.append(f"  Scenario Outline: {m.group(1)}")
            in_scenario = True
            in_background = False
            in_user_story = False
            in_examples = False
            skip_next_blockquote = True
            continue

        # Drop blockquote description lines after Scenario/Background headers
        if skip_next_blockquote:
            if stripped.startswith(">"):
                skip_next_blockquote = False
                continue
            elif stripped == "":
                continue
            else:
                skip_next_blockquote = False
                # Fall through to process this line

        # Rule 7: Step keywords
        if in_scenario or in_background:
            clean = strip_bold(stripped)
            clean = strip_markdown_links(clean)
            clean = strip_backticks(clean)
            clean = clean.strip()

            # Check for step keywords
            for kw in STEP_KEYWORDS:
                if clean.startswith(kw + " ") or clean == kw:
                    in_examples = False
                    output.append(f"    {clean}")
                    break
            else:
                # Rule 8: Examples:
                if is_examples_line(clean):
                    in_examples = True
                    output.append(f"    Examples:")
                    continue

                # Rule 9: Table rows in examples
                if in_examples and is_table_row(stripped):
                    # Clean alignment colons from table separators
                    clean_row = re.sub(r":?-{3,}:?", "---", stripped.strip())
                    # Skip separator rows
                    if re.match(r"^\|[\s\-|]+\|$", clean_row):
                        continue
                    output.append(f"      {stripped.strip()}")
                    continue

                # Table rows outside examples (in background or scenario)
                if is_table_row(stripped):
                    clean_row = re.sub(r":?-{3,}:?", "---", stripped.strip())
                    if re.match(r"^\|[\s\-|]+\|$", clean_row):
                        continue
                    output.append(f"      {stripped.strip()}")
                    continue

                # Blank lines
                if clean == "":
                    continue

        # Drop other ## headings that aren't recognized
        if re.match(r"^#{1,3}\s", stripped):
            continue

        # Drop empty lines outside of known contexts
        if stripped == "":
            continue

    # Ensure file ends with newline
    return output


def validate_feature_md(filepath: Path) -> list[str]:
    """Validate a .feature.md file for Gherkin compatibility issues.

    Returns a list of warning strings. Empty list means clean.
    """
    warnings = []
    lines = filepath.read_text().splitlines()
    in_scenario = False
    has_feature = False
    has_scenario = False
    has_step = False

    for i, line in enumerate(lines, 1):
        stripped = line.strip()

        # Check for Feature:
        if re.match(r"^#\s+Feature:", stripped):
            has_feature = True
            continue

        # Track scenario context
        if re.match(r"^###\s+Scenario", stripped):
            has_scenario = True
            in_scenario = True
            continue

        if re.match(r"^##\s+Background", stripped, re.IGNORECASE):
            in_scenario = True
            continue

        if re.match(r"^##\s", stripped) and not re.match(r"^##\s+Background", stripped, re.IGNORECASE):
            in_scenario = False
            continue

        # Check for bold step keywords
        for kw in STEP_KEYWORDS:
            if re.match(rf"^\s*\*\*{kw}\*\*", stripped):
                warnings.append(f"{filepath.name}:{i}: bold step keyword '**{kw}**' — use bare '{kw}' instead")
                break

        # Check step lines
        clean = strip_bold(stripped)
        if in_scenario and any(clean.startswith(kw + " ") for kw in STEP_KEYWORDS):
            has_step = True
            # Check forbidden patterns in step lines
            for pattern, desc in FORBIDDEN_PATTERNS:
                if pattern.search(stripped):
                    warnings.append(f"{filepath.name}:{i}: {desc}")

        # Check for forbidden constructs inside scenarios
        if in_scenario:
            if re.match(r"^#{4,}", stripped):
                warnings.append(f"{filepath.name}:{i}: nested heading below ### inside scenario")
            if re.match(r"^\s*[-*]\s+\S", stripped) and not is_table_row(stripped):
                # Could be a bullet list — only warn if it's not a step
                if not any(strip_bold(stripped.strip()).startswith(kw) for kw in STEP_KEYWORDS):
                    warnings.append(f"{filepath.name}:{i}: bullet list inside scenario")

    # Structure checks
    if not has_feature:
        warnings.append(f"{filepath.name}: missing '# Feature:' heading")
    if not has_scenario:
        warnings.append(f"{filepath.name}: no scenarios found")
    if not has_step:
        warnings.append(f"{filepath.name}: no Given/When/Then steps found")

    return warnings


def main():
    parser = argparse.ArgumentParser(
        description="Convert .feature.md files to standard Gherkin .feature files"
    )
    parser.add_argument("--app", required=True, help="App name (directory under spec/apps/)")
    parser.add_argument(
        "--project-dir", required=True,
        help="Project root directory (parent of spec/)"
    )
    parser.add_argument(
        "--spec-dir", default=None,
        help="Path to spec directory (default: <project-dir>/spec)"
    )
    parser.add_argument(
        "--output-dir", default=None,
        help="Output directory for .feature files (default: <project-dir>/tests/features/<app>)"
    )
    parser.add_argument(
        "--validate-only", action="store_true",
        help="Parse and validate without writing output files"
    )
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    spec_dir = Path(args.spec_dir).resolve() if args.spec_dir else project_dir / "spec"
    features_dir = spec_dir / "apps" / args.app / "features"

    if not features_dir.is_dir():
        print(f"Features directory not found: {features_dir}")
        sys.exit(1)

    feature_files = sorted(features_dir.glob("*.feature.md"))
    if not feature_files:
        print(f"No .feature.md files found in {features_dir}")
        sys.exit(1)

    print(f"Found {len(feature_files)} feature file(s) for app '{args.app}'")

    if args.validate_only:
        all_warnings = []
        for fpath in feature_files:
            warnings = validate_feature_md(fpath)
            all_warnings.extend(warnings)

        if all_warnings:
            print(f"\n{len(all_warnings)} warning(s):")
            for w in all_warnings:
                print(f"  WARNING: {w}")
            sys.exit(1)
        else:
            print("All files pass Gherkin compatibility checks.")
            sys.exit(0)

    # Convert mode
    output_base = Path(args.output_dir).resolve() if args.output_dir else project_dir / "tests" / "features" / args.app
    output_base.mkdir(parents=True, exist_ok=True)

    converted = 0
    for fpath in feature_files:
        # Feature tag from filename: user-registration.feature.md -> user-registration
        stem = fpath.name
        if stem.endswith(".feature.md"):
            tag = stem[: -len(".feature.md")]
        else:
            tag = fpath.stem

        lines = fpath.read_text().splitlines()
        gherkin_lines = convert_feature_md(lines, tag)

        out_path = output_base / f"{tag}.feature"
        out_path.write_text("\n".join(gherkin_lines) + "\n")
        converted += 1
        print(f"  {fpath.name} -> {out_path.name}")

    print(f"\nConverted {converted} file(s) to {output_base}")


if __name__ == "__main__":
    main()
