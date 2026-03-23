# Webapp Blueprint

A Claude Code skill that implements a **9-step enterprise web application specification pipeline**. It guides you through systematic design — from domain discovery and role matrices through UI conventions, navigation, API conventions, app archetypes, domain refinement, role refinement, and BDD features — producing a complete `/spec` folder ready for downstream technical specification and code generation.

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

The pipeline is organized into 3 tiers:

| Tier | Steps | Scope | Purpose |
|------|-------|-------|---------|
| 1 | 1–5 | Suite-wide (run once) | Domain model, roles, UI conventions, navigation, API conventions |
| 2 | 6–8 | Per-app (run once each) | App archetype, domain refinement, role refinement |
| 3 | 9 | Per-app (detailed) | BDD feature specifications |

Supports 6 app archetypes: CRUD Manager, Dashboard/Analytics, Workflow Engine, Content Platform, Communication Hub, and Configuration/Admin.

## Output Structure

Spec artifacts are generated under `./spec/` in your working directory:

```
spec/
├── suite/                          # Tier 1 — shared foundations
│   ├── domain-model.md
│   ├── role-permission-matrix.md
│   ├── ui-conventions.md
│   ├── navigation-shell.md
│   └── api-event-contracts.md
├── apps/{app_name}/                # Tier 2–3 — per-app specs
│   ├── archetype.md
│   ├── domain-refinement.md
│   ├── role-refinement.md
│   └── features/*.feature.md
└── .blueprint-meta.json            # Written on pipeline completion
```

## Scripts

Two helper scripts are included:

- **`scripts/check-progress.py`** — Scans `./spec/` and reports which steps are complete, which are pending, and what to work on next.
- **`scripts/feature-md-to-gherkin.py`** — Converts `.feature.md` files to standard Gherkin `.feature` files. Also supports `--validate-only` mode to check for Gherkin compatibility issues without writing output.

## Downstream Skills

After completing the 9-step blueprint, two downstream skills continue the lifecycle:

| Skill | Purpose |
|-------|---------|
| **webapp-architect** | Technical specification — information architecture, page patterns, state design, API contracts, authorization, generation briefs, seed data |
| **webapp-prover** | BDD test execution and build/test/fix cycle against the deployed application |

**Typical workflow:** run `webapp-blueprint` to produce the behavioral spec, then run `webapp-architect` to produce the technical spec, then build the application, then run `webapp-prover` to validate it against the BDD scenarios.

## License

MIT
