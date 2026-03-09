# Webapp Blueprint

A Claude Code skill that implements a **18-step enterprise web application specification pipeline**. It guides you through systematic design — from domain discovery and role matrices through BDD features, page specs, API definitions, and authorization policies — producing a complete `/spec` folder ready for code generation, plus a machine-readable blackbox test template for the build/test cycle.

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
| 1 | 1–5 | Suite-wide (run once) | Domain model, roles, UI conventions, navigation, API conventions |
| 2 | 6–8 | Per-app (run once each) | App archetype, domain refinement, role refinement |
| 3 | 9–14 | Per-app (detailed) | BDD features, IA, pages, state, APIs, authorization |
| 4 | 15–18 | Per-app (final) | Spec validation, generation briefs, seed data, blackbox test template |

Supports 6 app archetypes: CRUD Manager, Dashboard/Analytics, Workflow Engine, Content Platform, Communication Hub, and Configuration/Admin.

## Output Structure

Spec artifacts are generated under `./spec/` in your working directory. Step 18 writes to a sibling `blackbox/` folder:

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
│   ├── features/*.feature.md
│   ├── ia-spec.md
│   ├── pages/*.md
│   ├── state-interaction.md
│   ├── api-contracts.md
│   ├── authorization.md
│   ├── seed-data.md                # Tier 4 (Step 17)
│   └── generation-briefs/          # Tier 4 (Step 16)
│       ├── _build-order.md
│       └── {page_name}-brief.md
└── validation/reports/{app_name}/  # Tier 4 (Step 15)
    ├── gap-report.md
    ├── contradiction-report.md
    └── completeness-score.md

blackbox/
├── templates/                      # Tier 4 (Step 18) — spec snapshot
│   └── {suite_name}_test.template.json
└── builds/{build_token}/           # Runtime — written by build/test skills
    ├── manifest.json
    ├── test_results.json
    └── final_test_results/
        └── results.json
```

## Scripts

Five helper scripts are included:

- **`scripts/check-progress.py`** — Scans `./spec/` and reports which steps are complete, which are pending, and what to work on next.
- **`scripts/validate-spec.py`** — Cross-references all spec artifacts to find gaps, contradictions, and produces a completeness score.
- **`scripts/generate-blackbox-template.py`** — Step 18: Parses all BDD feature files for a suite and generates a machine-readable JSON test template under `./blackbox/templates/`. Usage: `python3 scripts/generate-blackbox-template.py --suite {suite_name}`
- **`scripts/wait-for-build.py`** — Polls for a new ready build in `blackbox/builds/`. Used by the test skill. Prints `build_token` to stdout on exit 0, exits 1 on timeout.
- **`scripts/wait-for-results.py`** — Polls for `final_test_results/` from the test agent. Used by the build skill. Exits 0 when results arrive, 1 on timeout.
- **`scripts/summarize-results.py`** — Prints PASSED/FAILED/UNTESTED counts per app from a completed test run.

## Companion Skills

This repo contains three installable skills that cover the full spec → build → test lifecycle:

| Skill | Command | Purpose |
|-------|---------|---------|
| `webapp-blueprint` | `/webapp-blueprint` | Design the spec (18 steps) |
| `webapp-blueprint-build` | `/webapp-blueprint-build` | Implement from briefs, fix BDD failures, sync spec gaps |
| `webapp-blueprint-test` | `/webapp-blueprint-test` | Execute BDD scenarios against the running app (separate session) |

One install registers all three skills:
```bash
claude skill add --source gh:seriouscoderone/webapp-blueprint
```

**Typical workflow:** run `webapp-blueprint` to produce the spec → run `webapp-blueprint-build` in your project session to build and deploy → run `webapp-blueprint-test` in a separate session to execute BDD scenarios → build skill reads results and fixes failures → repeat until green.

### Running the test agent as a separate instance

`webapp-blueprint-test` must run in a completely isolated Claude Code session — it needs its own tool permissions (browser automation) and must not share context with the build agent. Use `CLAUDE_CONFIG_DIR` to create a dedicated instance:

```bash
# In ~/.zshrc or ~/.bashrc
alias claude-build="CLAUDE_CONFIG_DIR=~/.claude-build claude"
alias claude-test="CLAUDE_CONFIG_DIR=~/.claude-test claude"
```

Then install `webapp-blueprint-test` once into the test instance:

```bash
claude-test skill add --source gh:seriouscoderone/webapp-blueprint/skills/test
```

In practice:
```bash
# Terminal 1 — build agent (your main project directory)
claude-build

# Terminal 2 — test agent (same project directory, isolated context)
claude-test
```

Both instances operate on the same `blackbox/` folder on disk, but have no shared memory or tool state. The `manifest.json` / `final_test_results/` files are the only communication channel between them.

## License

MIT
