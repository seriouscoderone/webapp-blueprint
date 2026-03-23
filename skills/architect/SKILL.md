---
name: webapp-architect
description: Technical specification pipeline for webapp-blueprint suites. Takes the domain spec (Steps 1-9) as input and produces information architecture, page patterns, state management, API contracts, authorization policies, validation reports, generation briefs, and seed data specifications (Steps 10-17).
---

# Webapp Architect — Technical Specification Pipeline

## Overview

This skill implements an **8-step technical specification pipeline** covering **Steps 10-17** of the webapp-blueprint pipeline. It takes the domain spec produced by `webapp-blueprint` (Steps 1-9) as input and produces the complete technical specification for each application.

The pipeline is organized into **2 tiers**:
- **Tier 3** (Steps 10-14): Per-app detailed specification — information architecture, page patterns, state management, API contracts, and authorization policies
- **Tier 4** (Steps 15-17): Validation and generation — spec validation, generation briefs, and seed data

---

## Prerequisites

Before starting, verify that the domain spec (Steps 1-9) is complete:

1. `.blueprint-meta.json` exists at the spec root and shows all 9 steps completed
2. `spec/suite/domain-model.md` exists
3. At least one app in `spec/apps/` with `archetype.md` and at least one `.feature.md`

If prerequisites are not met, print:

> **Error:** Run webapp-blueprint first to complete domain discovery (Steps 1-9).

---

## Tech Stack Declaration

Before beginning Step 10, declare the tech stack for the application. Ask the user:

1. **What frontend framework?** (React, Vue, Svelte, Angular, other)
2. **What styling approach?** (Tailwind, CSS Modules, Styled Components, other)
3. **What state management?** (TanStack Query, Zustand, Redux Toolkit, Pinia, framework defaults)
4. **What API style?** (REST, GraphQL, tRPC)
5. **What routing?** (React Router, Next.js, Vue Router, SvelteKit)

Store answers in `.architect-meta.json` at the spec root (see Architect Metadata section) and inject into all downstream steps. If `.architect-meta.json` already exists with a `tech_stack` field, confirm with the user rather than re-asking.

---

## Pipeline at a Glance

| Step | Name | Tier | Reads From | Writes To | Reference |
|------|------|------|------------|-----------|-----------|
| 10 | Information Architecture | 3 | Steps 6-7, 9 | `apps/{app}/ia-spec.md` | `{SKILL_DIR}/references/10-ia-spec.md` |
| 11 | Page Patterns | 3 | Steps 6, 9-10 | `apps/{app}/pages/*.md` | `{SKILL_DIR}/references/11-page-patterns.md` |
| 12 | State & Interaction | 3 | Steps 9, 11 | `apps/{app}/state-interaction.md` | `{SKILL_DIR}/references/12-state-interaction.md` |
| 13 | API Contracts | 3 | Steps 5, 7, 11, 12 | `apps/{app}/api-contracts.md` | `{SKILL_DIR}/references/13-api-contracts.md` |
| 14 | Authorization Policy | 3 | Steps 8, 10, 13 | `apps/{app}/authorization.md` | `{SKILL_DIR}/references/14-authorization-policy.md` |
| 15 | Spec Validator | 4 | Steps 1-14 | `validation/reports/{app}/*` | `{SKILL_DIR}/references/15-spec-validator.md` |
| 16 | Generation Brief | 4 | Steps 1-15 | `apps/{app}/generation-briefs/*` | `{SKILL_DIR}/references/16-generation-brief.md` |
| 17 | Seed Data | 4 | Steps 1, 9, 13, 16 | `apps/{app}/seed-data.md` | `{SKILL_DIR}/references/17-seed-data.md` |

---

## Spec Folder Structure

All outputs are written under `./spec/` relative to the working directory. Steps 10-17 produce artifacts in the `apps/{app}/` and `validation/` directories:

```
spec/
├── suite/                           ← Tier 1 (produced by webapp-blueprint)
│   ├── domain-model.md
│   ├── role-permission-matrix.md
│   ├── ui-conventions.md
│   ├── navigation-shell.md
│   └── api-event-contracts.md
├── apps/
│   └── {app_name}/
│       ├── archetype.md             ← Tier 2 (produced by webapp-blueprint)
│       ├── domain-refinement.md
│       ├── role-refinement.md
│       ├── features/
│       │   └── *.feature.md
│       ├── ia-spec.md               ← Step 10
│       ├── pages/                   ← Step 11
│       │   └── {page_name}.md
│       ├── state-interaction.md     ← Step 12
│       ├── api-contracts.md         ← Step 13
│       ├── authorization.md         ← Step 14
│       ├── seed-data.md             ← Step 17
│       └── generation-briefs/       ← Step 16
│           ├── _build-order.md
│           └── {page_name}-brief.md
└── validation/
    └── reports/
        └── {app_name}/             ← Step 15
            ├── gap-report.md
            ├── contradiction-report.md
            └── completeness-score.md
```

See [Conventions & Folder Structure]({SKILL_DIR}/references/00-conventions.md) for the full annotated tree, naming conventions, and cross-reference syntax.

---

## How to Use

When this skill is invoked, follow these steps:

### 1. Detect Current State

Run the progress checker to understand where the user is in the pipeline:

```bash
python3 {SKILL_DIR}/scripts/check-progress.py --project-dir {project_root}
```

Where `{SKILL_DIR}` is the directory containing this skill and `{project_root}` is the user's project directory (the parent of `spec/`). If the user's working directory is the project root, `--project-dir .` works.

### 2. Verify Prerequisites

Check that `.blueprint-meta.json` exists and that Steps 1-9 are complete. If not, instruct the user to run `webapp-blueprint` first.

### 3. Declare Tech Stack

If `.architect-meta.json` does not exist or has no `tech_stack` field, ask the user the tech stack questions (see Tech Stack Declaration section above). Store the answers before proceeding.

### 4. Present Progress Summary

Show the user a concise summary of:
- Whether prerequisites (Steps 1-9) are met
- Which Steps 10-17 are complete for each app
- The suggested next step

### 5. Ask What to Work On

Ask the user which step they'd like to work on. Default to the **next incomplete step** (lowest-numbered step whose prerequisites are met but whose outputs are missing).

Confirm which app they're working on.

### 6. Load the Reference File

Read the appropriate `{SKILL_DIR}/references/NN-*.md` file for the selected step. This file contains:
- The interrogation process (questions to ask)
- Output specification (what files to produce)
- Completion checklist

### 7. Execute the Step

Follow the reference file's interrogation process:
- Ask questions in the order specified
- Adapt based on user responses
- Read any prerequisite files from `./spec/` as specified
- Inject tech stack context where relevant
- Generate output files in the correct locations
- Create directories as needed

### 8. Complete and Continue

After finishing a step:
- Verify all output files were created
- Run through the completion checklist
- Suggest the next step in the pipeline
- Ask if the user wants to continue

---

## Progress Detection

A step is considered **complete** when its primary output file(s) exist in `./spec/`:

| Step | Complete When |
|------|--------------|
| 10 | `apps/{app}/ia-spec.md` exists |
| 11 | `apps/{app}/pages/` has at least 1 `.md` file |
| 12 | `apps/{app}/state-interaction.md` exists |
| 13 | `apps/{app}/api-contracts.md` exists |
| 14 | `apps/{app}/authorization.md` exists |
| 15 | `validation/reports/{app}/completeness-score.md` exists |
| 16 | `apps/{app}/generation-briefs/_build-order.md` exists |
| 17 | `apps/{app}/seed-data.md` exists |

---

## Step Dispatch Table

| Step | Description | Reference File | Prerequisites |
|------|-------------|---------------|--------------|
| 10 | Define information architecture: sitemap, URLs, navigation | `{SKILL_DIR}/references/10-ia-spec.md` | Steps 6-7, 9 |
| 11 | Specify page layouts, data needs, states, and actions | `{SKILL_DIR}/references/11-page-patterns.md` | Steps 6, 9-10 |
| 12 | Design state management, data flow, and interaction patterns | `{SKILL_DIR}/references/12-state-interaction.md` | Steps 9, 11 |
| 13 | Define app-level API endpoints, schemas, and events | `{SKILL_DIR}/references/13-api-contracts.md` | Steps 5, 7, 11, 12 |
| 14 | Specify authorization policies: routes, APIs, data, UI elements | `{SKILL_DIR}/references/14-authorization-policy.md` | Steps 8, 10, 13 |
| 15 | Validate spec consistency and completeness with scoring | `{SKILL_DIR}/references/15-spec-validator.md` | Steps 1-14 |
| 16 | Generate per-page briefs with build order for code generation | `{SKILL_DIR}/references/16-generation-brief.md` | Steps 1-15 |
| 17 | Define realistic seed data covering all BDD scenarios and roles | `{SKILL_DIR}/references/17-seed-data.md` | Steps 1, 9, 13, 16 |

---

## Conventions

See [{SKILL_DIR}/references/00-conventions.md]({SKILL_DIR}/references/00-conventions.md) for output formatting, file naming, variable placeholders, and cross-reference conventions.

---

## Tier-Specific Guidance

### Tier 3 — App Specification (Steps 10-14)

These steps produce the detailed technical artifacts for each app. When working on Tier 3:
- Work iteratively — it's normal to revisit earlier steps as details emerge
- Steps 10-11 (IA, pages) inform each other — the information architecture defines the page structure, and page specs may reveal missing routes
- Steps 12-13 (state, APIs) build on the page specs — data needs from page specs drive state design and API contracts
- Step 14 (authorization) ties everything together — it must cover all routes from Step 10 and all endpoints from Step 13
- For steps that produce multiple files (Step 11), work through them one at a time with the user
- Inject tech stack context: framework-specific patterns for state management, API calls, and routing

### Tier 4 — Validation & Generation (Steps 15-17)

These steps run **after Tier 3 is complete** for an app. When working on Tier 4:
- Step 15 uses `{SKILL_DIR}/scripts/validate-spec.py --app {app} --project-dir {project_root}` to automate cross-reference checks
- Review validation results with the user and fix gaps; a score of 80 or higher is required to proceed
- Step 16 produces the final generation briefs — these drive the code generation sequence
- Step 17 produces the seed data specification — ensures generated code can be tested immediately
- The build order in Step 16 also determines the correct seed insertion order for Step 17

---

## Architect Metadata

On completion of all steps for an app, write `.architect-meta.json` at the spec root:

```json
{
  "version": "1.0",
  "skill": "webapp-architect",
  "completed_at": "<ISO-8601>",
  "app": "<app_name>",
  "tech_stack": {
    "framework": "...",
    "styling": "...",
    "api": "...",
    "state": "...",
    "routing": "..."
  },
  "steps_completed": [10, 11, 12, 13, 14, 15, 16, 17]
}
```

Update `.architect-meta.json` incrementally as each step completes — add the step number to `steps_completed` after each step finishes. Write the `completed_at` timestamp when all 8 steps are done.

---

## Downstream Skills

After completing Steps 10-17, the specification is ready for the build-test-fix cycle:
- Run **webapp-prover** for deterministic BDD testing and the build-test-fix cycle
