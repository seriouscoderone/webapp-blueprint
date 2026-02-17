#!/usr/bin/env python3
"""Cross-reference validator for webapp blueprint specs (Step 16).

Reads all spec files for a given app and checks for gaps, contradictions,
and completeness. Writes validation reports to spec/validation/reports/{app}/.
"""

import argparse
import os
import re
from pathlib import Path


# ---------------------------------------------------------------------------
# Extraction helpers — heuristic regex patterns for markdown specs
# ---------------------------------------------------------------------------

def read_file(path: Path) -> str:
    """Read a file and return its contents, or empty string if missing."""
    if path.is_file():
        return path.read_text(encoding="utf-8", errors="replace")
    return ""


def extract_heading_items(text: str, pattern: str) -> list[str]:
    """Extract items from markdown headings matching a pattern.

    Looks for lines like '## Entity: OrderItem' or '## Role: Admin' and
    returns the captured group.
    """
    return re.findall(pattern, text, re.MULTILINE | re.IGNORECASE)


def extract_entities(text: str) -> list[str]:
    """Extract entity names from domain model markdown."""
    # Match headings: ## Entity: Name, ### Name, or table rows | Name |
    entities = extract_heading_items(text, r"^#{1,4}\s+(?:Entity:\s*)?(\w[\w\s-]*\w)")
    # Also look for bold items in lists: - **EntityName**
    entities += re.findall(r"^\s*[-*]\s+\*\*(\w[\w\s-]*\w)\*\*", text, re.MULTILINE)
    return list(dict.fromkeys(e.strip() for e in entities))  # dedupe, preserve order


def extract_roles(text: str) -> list[str]:
    """Extract role names from role/permission matrix markdown."""
    roles = extract_heading_items(text, r"^#{1,4}\s+(?:Role:\s*)?(\w[\w\s-]*\w)")
    roles += re.findall(r"^\s*[-*]\s+\*\*(\w[\w\s-]*\w)\*\*", text, re.MULTILINE)
    # Table header roles: | | Admin | Editor | Viewer |
    header_match = re.search(r"^\|[^|]*\|(.+)\|", text, re.MULTILINE)
    if header_match:
        cells = [c.strip() for c in header_match.group(1).split("|") if c.strip()]
        roles += cells
    return list(dict.fromkeys(r.strip() for r in roles))


def extract_routes(text: str) -> list[str]:
    """Extract route/URL paths from IA spec or page specs."""
    # Match /path/to/page or /path/:param patterns
    return list(dict.fromkeys(re.findall(r"(?:^|\s)(/[\w/:.-]+)", text)))


def extract_component_refs(text: str) -> list[str]:
    """Extract component references from page spec markdown.

    Looks for patterns like <ComponentName>, `ComponentName`, or
    ## Component: Name headings.
    """
    refs = re.findall(r"<(\w+(?:Card|Button|Table|List|Form|Modal|Panel|Widget|Nav|Header|Footer|Sidebar|Menu|Dialog|Drawer|Badge|Alert|Banner|Chart|Grid|Layout|Container|Section|View|Page|Tab|Tabs|Input|Select|Dropdown|Picker|Search|Filter|Sort|Pagination|Avatar|Icon|Image|Logo|Link|Tooltip|Popover|Snackbar|Toast|Spinner|Loader|Skeleton|Placeholder|Divider|Separator|Breadcrumb|Stepper|Progress|Rating|Switch|Toggle|Checkbox|Radio|Slider|Upload|Calendar|Timeline|Accordion|Carousel|Collapse|Tree)\w*)", text)
    refs += extract_heading_items(text, r"^#{1,4}\s+(?:Component:\s*)(\w+)")
    refs += re.findall(r"`(\w+(?:Component|Widget|Card|Table|List|Form|Modal|Panel))`", text)
    return list(dict.fromkeys(r.strip() for r in refs))


def extract_api_endpoints(text: str) -> list[str]:
    """Extract API endpoint references (GET /api/..., POST /api/..., etc.)."""
    return list(dict.fromkeys(
        re.findall(r"(?:GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)\s+(/[\w/:.-]+)", text, re.IGNORECASE)
    ))


def extract_connected_pages(text: str) -> list[str]:
    """Extract 'Connected Pages' references from page specs."""
    section = re.search(r"(?:Connected\s+Pages|Navigation|Links\s+To)[:\s]*\n((?:\s*[-*].*\n)*)", text, re.IGNORECASE)
    if not section:
        return []
    return re.findall(r"[-*]\s+\[?([^\]\n]+)\]?", section.group(1))


def extract_design_tokens(text: str) -> list[str]:
    """Extract design token names from design system spec."""
    tokens = re.findall(r"`--([\w-]+)`", text)
    tokens += re.findall(r"^\s*[-*]\s+`?([\w-]+(?:\.[\w-]+)+)`?", text, re.MULTILINE)
    return list(dict.fromkeys(tokens))


def list_files(directory: Path, suffix: str = ".md") -> list[Path]:
    """List files in a directory matching a suffix."""
    if not directory.is_dir():
        return []
    return sorted(f for f in directory.iterdir() if f.is_file() and f.name.endswith(suffix))


def stem_name(path: Path) -> str:
    """Get the stem of a file, stripping known suffixes like .feature."""
    name = path.stem
    if name.endswith(".feature"):
        name = name[: -len(".feature")]
    return name


# ---------------------------------------------------------------------------
# Validation checks
# ---------------------------------------------------------------------------

def validate(spec_dir: Path, app_name: str) -> dict:
    """Run all validation checks and return structured results."""
    suite = spec_dir / "suite"
    app_dir = spec_dir / "apps" / app_name
    gaps = []          # missing artifacts
    contradictions = []  # inconsistent cross-references
    scores = {"completeness": [], "consistency": [], "coverage": []}

    # --- 1. Entity Consistency ---
    suite_entities = extract_entities(read_file(suite / "domain-model.md"))
    app_entities = extract_entities(read_file(app_dir / "domain-refinement.md"))
    app_entity_text = read_file(app_dir / "domain-refinement.md")

    if not suite_entities:
        gaps.append("No entities found in suite/domain-model.md")
    if not app_entities and (app_dir / "domain-refinement.md").is_file():
        gaps.append(f"No entities found in apps/{app_name}/domain-refinement.md")

    for entity in app_entities:
        if entity not in suite_entities and "app-specific" not in app_entity_text.lower():
            contradictions.append(
                f"Entity '{entity}' in app domain-refinement is not in suite domain-model "
                f"and not marked as app-specific"
            )
    if suite_entities:
        matched = sum(1 for e in app_entities if e in suite_entities)
        scores["consistency"].append(matched / len(app_entities) if app_entities else 1.0)

    # --- 2. Role Consistency ---
    suite_roles = extract_roles(read_file(suite / "role-permission-matrix.md"))
    app_roles = extract_roles(read_file(app_dir / "role-refinement.md"))
    app_role_text = read_file(app_dir / "role-refinement.md")

    if not suite_roles:
        gaps.append("No roles found in suite/role-permission-matrix.md")
    if not app_roles and (app_dir / "role-refinement.md").is_file():
        gaps.append(f"No roles found in apps/{app_name}/role-refinement.md")

    for role in app_roles:
        if role not in suite_roles and "app-specific" not in app_role_text.lower():
            contradictions.append(
                f"Role '{role}' in app role-refinement is not in suite role-permission-matrix "
                f"and not marked as app-specific"
            )
    if suite_roles:
        matched = sum(1 for r in app_roles if r in suite_roles)
        scores["consistency"].append(matched / len(app_roles) if app_roles else 1.0)

    # --- 3. Feature Coverage ---
    feature_files = list_files(app_dir / "features", ".feature.md")
    if not feature_files:
        gaps.append(f"No .feature.md files in apps/{app_name}/features/")
    scores["completeness"].append(1.0 if feature_files else 0.0)
    feature_names = [stem_name(f) for f in feature_files]

    # --- 4. Page Coverage ---
    ia_text = read_file(app_dir / "ia-spec.md")
    ia_routes = extract_routes(ia_text)
    page_files = list_files(app_dir / "pages")
    page_stems = [stem_name(f) for f in page_files]

    if ia_routes and not page_files:
        gaps.append(f"IA spec defines {len(ia_routes)} routes but no page specs exist")
    for route in ia_routes:
        # Derive expected page name from route: /dashboard/settings → dashboard-settings
        slug = route.strip("/").replace("/", "-").replace(":", "")
        if slug and not any(slug in ps or ps in slug for ps in page_stems):
            gaps.append(f"Route '{route}' from ia-spec.md has no matching page spec")
    if ia_routes:
        matched = sum(1 for r in ia_routes if any(
            r.strip("/").replace("/", "-").replace(":", "") in ps or
            ps in r.strip("/").replace("/", "-").replace(":", "")
            for ps in page_stems
        ))
        scores["coverage"].append(matched / len(ia_routes) if ia_routes else 1.0)
    scores["completeness"].append(1.0 if page_files else 0.0)

    # --- 5. Component Coverage ---
    all_page_text = ""
    for pf in page_files:
        all_page_text += read_file(pf) + "\n"
    component_refs = extract_component_refs(all_page_text)
    component_files = list_files(app_dir / "components")
    component_stems = [stem_name(f).lower() for f in component_files]

    for comp in component_refs:
        if comp.lower() not in component_stems and not any(comp.lower() in cs for cs in component_stems):
            gaps.append(f"Component '{comp}' referenced in page specs has no matching component spec")
    if component_refs:
        matched = sum(1 for c in component_refs if c.lower() in component_stems or
                       any(c.lower() in cs for cs in component_stems))
        scores["coverage"].append(matched / len(component_refs))
    scores["completeness"].append(1.0 if component_files else 0.0)

    # --- 6. API Coverage ---
    state_text = read_file(app_dir / "state-interaction.md")
    api_text = read_file(app_dir / "api-contracts.md")
    page_api_refs = extract_api_endpoints(all_page_text + state_text)
    api_defined = extract_api_endpoints(api_text)

    for ep in page_api_refs:
        if ep not in api_defined:
            gaps.append(f"API endpoint '{ep}' referenced in specs but not defined in api-contracts.md")
    if page_api_refs:
        matched = sum(1 for ep in page_api_refs if ep in api_defined)
        scores["consistency"].append(matched / len(page_api_refs))
    scores["completeness"].append(1.0 if (app_dir / "api-contracts.md").is_file() else 0.0)

    # --- 7. Authorization Coverage ---
    auth_text = read_file(app_dir / "authorization.md")
    all_routes = ia_routes + api_defined
    if all_routes and not auth_text:
        gaps.append("Routes and endpoints exist but authorization.md is empty or missing")
    for route in all_routes:
        if route not in auth_text:
            gaps.append(f"Route/endpoint '{route}' not found in authorization.md")
    if all_routes:
        matched = sum(1 for r in all_routes if r in auth_text)
        scores["coverage"].append(matched / len(all_routes))
    scores["completeness"].append(1.0 if (app_dir / "authorization.md").is_file() else 0.0)

    # --- 8. State Coverage ---
    state_keywords = ["loading", "error", "empty"]
    for pf in page_files:
        page_text = read_file(pf).lower()
        missing_states = [s for s in state_keywords if s not in page_text]
        if missing_states:
            gaps.append(
                f"Page spec '{pf.name}' missing state definitions: {', '.join(missing_states)}"
            )
    if page_files:
        total_checks = len(page_files) * len(state_keywords)
        found = sum(
            1 for pf in page_files
            for s in state_keywords
            if s in read_file(pf).lower()
        )
        scores["coverage"].append(found / total_checks if total_checks else 1.0)

    # --- 9. Navigation Consistency ---
    for pf in page_files:
        connected = extract_connected_pages(read_file(pf))
        for target in connected:
            target_slug = target.strip().lower().replace(" ", "-")
            if not any(target_slug in ps.lower() for ps in page_stems):
                contradictions.append(
                    f"Page '{pf.name}' references connected page '{target}' which has no spec file"
                )
    # Count for consistency score
    nav_total = 0
    nav_found = 0
    for pf in page_files:
        connected = extract_connected_pages(read_file(pf))
        nav_total += len(connected)
        nav_found += sum(1 for t in connected if any(
            t.strip().lower().replace(" ", "-") in ps.lower() for ps in page_stems
        ))
    if nav_total:
        scores["consistency"].append(nav_found / nav_total)

    # --- 10. Design System Compliance ---
    design_text = read_file(suite / "design-system.md")
    design_tokens = extract_design_tokens(design_text)
    if design_tokens:
        all_component_text = ""
        for cf in component_files:
            all_component_text += read_file(cf) + "\n"
        comp_token_refs = extract_design_tokens(all_component_text)
        for token in comp_token_refs:
            if token not in design_tokens:
                contradictions.append(
                    f"Component spec references design token '{token}' not found in design-system.md"
                )
        if comp_token_refs:
            matched = sum(1 for t in comp_token_refs if t in design_tokens)
            scores["consistency"].append(matched / len(comp_token_refs))

    # --- Check core file completeness ---
    core_files = [
        "archetype.md", "domain-refinement.md", "role-refinement.md",
        "ia-spec.md", "state-interaction.md", "api-contracts.md", "authorization.md",
    ]
    for fname in core_files:
        if not (app_dir / fname).is_file():
            gaps.append(f"Missing core spec file: apps/{app_name}/{fname}")
        scores["completeness"].append(1.0 if (app_dir / fname).is_file() else 0.0)

    return {"gaps": gaps, "contradictions": contradictions, "scores": scores}


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def compute_scores(raw: dict) -> dict:
    """Compute final 0-100 scores from raw validation results."""
    def avg(lst):
        return (sum(lst) / len(lst) * 100) if lst else 0.0

    completeness = avg(raw["scores"]["completeness"])
    consistency = avg(raw["scores"]["consistency"])
    coverage = avg(raw["scores"]["coverage"])
    overall = 0.40 * completeness + 0.35 * consistency + 0.25 * coverage
    return {
        "completeness": round(completeness, 1),
        "consistency": round(consistency, 1),
        "coverage": round(coverage, 1),
        "overall": round(overall, 1),
    }


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def write_gap_report(path: Path, gaps: list[str], app_name: str):
    """Write the gap report markdown file."""
    lines = [
        f"# Gap Report — {app_name}\n",
        f"Total gaps found: {len(gaps)}\n",
    ]
    if gaps:
        lines.append("## Missing Artifacts & Incomplete Sections\n")
        for i, gap in enumerate(gaps, 1):
            lines.append(f"{i}. {gap}")
    else:
        lines.append("No gaps detected. All expected artifacts are present.\n")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_contradiction_report(path: Path, contradictions: list[str], app_name: str):
    """Write the contradiction report markdown file."""
    lines = [
        f"# Contradiction Report — {app_name}\n",
        f"Total contradictions found: {len(contradictions)}\n",
    ]
    if contradictions:
        lines.append("## Conflicting & Inconsistent Specs\n")
        for i, c in enumerate(contradictions, 1):
            lines.append(f"{i}. {c}")
    else:
        lines.append("No contradictions detected. All cross-references are consistent.\n")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_completeness_report(path: Path, final_scores: dict, gaps: list, contradictions: list, app_name: str):
    """Write the completeness score markdown file."""
    lines = [
        f"# Completeness Score — {app_name}\n",
        "## Scores\n",
        f"| Metric        | Score  |",
        f"|---------------|--------|",
        f"| Completeness  | {final_scores['completeness']:5.1f}% |",
        f"| Consistency   | {final_scores['consistency']:5.1f}% |",
        f"| Coverage      | {final_scores['coverage']:5.1f}% |",
        f"| **Overall**   | **{final_scores['overall']:.1f}%** |",
        "",
        "## Scoring Methodology\n",
        "- **Completeness** (40%): Ratio of existing artifacts to expected artifacts",
        "- **Consistency** (35%): Ratio of valid cross-references to total cross-references",
        "- **Coverage** (25%): Ratio of fully specified items to total items",
        "",
        "## Summary\n",
        f"- Gaps found: {len(gaps)}",
        f"- Contradictions found: {len(contradictions)}",
        f"- Overall score: {final_scores['overall']:.1f}%",
        "",
    ]
    if final_scores["overall"] >= 90:
        lines.append("Specification is ready for code generation.")
    elif final_scores["overall"] >= 70:
        lines.append("Specification is mostly complete. Address remaining gaps before generation.")
    else:
        lines.append("Specification needs significant work. Review gap and contradiction reports.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Validate webapp blueprint specs for an app (Step 16)")
    parser.add_argument("--spec-dir", default="./spec", help="Path to spec directory (default: ./spec)")
    parser.add_argument("--app", required=True, help="App name to validate (must exist under spec/apps/)")
    args = parser.parse_args()

    spec_dir = Path(args.spec_dir).resolve()
    app_dir = spec_dir / "apps" / args.app

    if not spec_dir.is_dir():
        print(f"ERROR: Spec directory not found: {spec_dir}")
        return
    if not app_dir.is_dir():
        print(f"ERROR: App directory not found: {app_dir}")
        return

    # Run validation
    results = validate(spec_dir, args.app)
    final_scores = compute_scores(results)

    # Write reports
    report_dir = spec_dir / "validation" / "reports" / args.app
    report_dir.mkdir(parents=True, exist_ok=True)

    write_gap_report(report_dir / "gap-report.md", results["gaps"], args.app)
    write_contradiction_report(report_dir / "contradiction-report.md", results["contradictions"], args.app)
    write_completeness_report(report_dir / "completeness-score.md", final_scores, results["gaps"], results["contradictions"], args.app)

    # Print summary to stdout
    print(f"=== Validation Report for '{args.app}' ===\n")
    print(f"Completeness : {final_scores['completeness']:5.1f}%")
    print(f"Consistency  : {final_scores['consistency']:5.1f}%")
    print(f"Coverage     : {final_scores['coverage']:5.1f}%")
    print(f"Overall      : {final_scores['overall']:5.1f}%\n")

    if results["gaps"]:
        print(f"Gaps ({len(results['gaps'])}):")
        for g in results["gaps"][:10]:
            print(f"  - {g}")
        if len(results["gaps"]) > 10:
            print(f"  ... and {len(results['gaps']) - 10} more (see gap-report.md)")

    if results["contradictions"]:
        print(f"\nContradictions ({len(results['contradictions'])}):")
        for c in results["contradictions"][:10]:
            print(f"  - {c}")
        if len(results["contradictions"]) > 10:
            print(f"  ... and {len(results['contradictions']) - 10} more (see contradiction-report.md)")

    print(f"\nReports written to: {report_dir}/")


if __name__ == "__main__":
    main()
