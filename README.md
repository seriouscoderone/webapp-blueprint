# Webapp Blueprint

A Claude Code skill that implements an **18-step enterprise web application specification pipeline**. It guides you through systematic design — from domain discovery and role matrices through BDD features, page specs, component contracts, API definitions, and authorization policies — producing a complete `/spec` folder ready for code generation.

## Installation

### From within a Claude Code session

```
/skill add gh:seriouscoderone/webapp-blueprint
```

### From the Claude CLI

```bash
claude skill add --source gh:seriouscoderone/webapp-blueprint
```

### From a local clone

```bash
git clone https://github.com/seriouscoderone/webapp-blueprint.git
claude skill add --source ./webapp-blueprint
```

Or from within a Claude Code session:

```
/skill add ./webapp-blueprint
```

## Usage

Once installed, invoke the skill in any Claude Code session:

```
/webapp-blueprint
```

The skill will:

1. Check your `./spec/` directory for existing progress
2. Show which steps are complete and suggest the next one
3. Walk you through the selected step with guided questions
4. Generate structured markdown artifacts in `./spec/`

You can jump to any step directly — the skill will verify prerequisites are met before proceeding.

## What It Does

The pipeline is organized into 4 tiers:

| Tier | Steps | Scope | Purpose |
|------|-------|-------|---------|
| 1 | 1–5 | Suite-wide (run once) | Domain model, roles, design system, navigation, API conventions |
| 2 | 6–8 | Per-app (run once each) | App archetype, domain refinement, role refinement |
| 3 | 9–15 | Per-app (detailed) | BDD features, IA, pages, components, state, APIs, authorization |
| 4 | 16–18 | Per-app (final) | Spec validation, generation briefs, seed data |

Supports 6 app archetypes: CRUD Manager, Dashboard/Analytics, Workflow Engine, Content Platform, Communication Hub, and Configuration/Admin.

## Output Structure

All artifacts are generated under `./spec/` in your working directory:

```
spec/
├── suite/                          # Tier 1 — shared foundations
│   ├── domain-model.md
│   ├── role-permission-matrix.md
│   ├── design-system.md
│   ├── navigation-shell.md
│   └── api-event-contracts.md
├── apps/{app_name}/                # Tier 2–3 — per-app specs
│   ├── archetype.md
│   ├── domain-refinement.md
│   ├── role-refinement.md
│   ├── features/*.feature.md
│   ├── ia-spec.md
│   ├── pages/*.md
│   ├── components/*.md
│   ├── state-interaction.md
│   ├── api-contracts.md
│   ├── authorization.md
│   ├── seed-data.md                # Tier 4 (Step 18)
│   └── generation-briefs/          # Tier 4
│       ├── _build-order.md
│       └── {page_name}-brief.md
└── validation/reports/{app_name}/  # Tier 4
    ├── gap-report.md
    ├── contradiction-report.md
    └── completeness-score.md
```

## Validation Scripts

Two helper scripts are included for pipeline management:

- **`scripts/check-progress.py`** — Scans `./spec/` and reports which steps are complete, which are pending, and what to work on next.
- **`scripts/validate-spec.py`** — Cross-references all spec artifacts to find gaps, contradictions, and produces a completeness score.

## License

MIT
