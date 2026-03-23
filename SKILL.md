---
name: webapp-blueprint
description: Enterprise web application specification pipeline. Guides users through 9 sequential design steps — from domain discovery, role matrices, and UI conventions through navigation, API conventions, app archetypes, domain refinement, role refinement, and BDD features. Produces a complete `/spec` folder ready for downstream technical specification and code generation.
---

# Webapp Blueprint — Enterprise Application Specification Pipeline

## Overview

This skill implements a **9-step specification pipeline** organized into **3 tiers** that produces a comprehensive `./spec/` folder of markdown artifacts. Each step's outputs feed into subsequent steps, building from high-level domain concepts down to testable BDD feature specifications.

The pipeline is designed for **enterprise application suites** — collections of related web applications that share a domain model, UI conventions, and role hierarchy. It works equally well for a single application.

**Tiers at a glance:**
- **Tier 1** (Steps 1–5): Suite-level foundations — run once
- **Tier 2** (Steps 6–8): Per-app classification — run once per app
- **Tier 3** (Step 9): BDD feature specifications — run per app

---

## Pipeline at a Glance

| Step | Name | Tier | Reads From | Writes To | Reference |
|------|------|------|-----------|-----------|-----------|
| 1 | Domain Discovery | 1 | — | `suite/domain-model.md` | `references/01-domain-discovery.md` |
| 2 | Role & Permission Matrix | 1 | Step 1 | `suite/role-permission-matrix.md` | `references/02-role-permission-matrix.md` |
| 3 | UI Conventions | 1 | Step 1 | `suite/ui-conventions.md` | `references/03-ui-conventions.md` |
| 4 | Navigation Shell | 1 | Steps 1–3 | `suite/navigation-shell.md` | `references/04-navigation-shell.md` |
| 5 | Suite API Conventions | 1 | Steps 1–2 | `suite/api-event-contracts.md` | `references/05-api-event-contracts.md` |
| 6 | App Archetype | 2 | Steps 1–5 | `apps/{app}/archetype.md` | `references/06-app-archetype.md` |
| 7 | Domain Refinement | 2 | Steps 1, 6 | `apps/{app}/domain-refinement.md` | `references/07-domain-refinement.md` |
| 8 | Role Refinement | 2 | Steps 2, 6–7 | `apps/{app}/role-refinement.md` | `references/08-role-refinement.md` |
| 9 | BDD Features | 3 | Steps 6–8 | `apps/{app}/features/*.feature.md` | `references/09-bdd-features.md` |

---

## Spec Folder Structure

All outputs are written under `./spec/` relative to the working directory:

```
spec/
├── suite/
│   ├── domain-model.md
│   ├── role-permission-matrix.md
│   ├── ui-conventions.md
│   ├── navigation-shell.md
│   └── api-event-contracts.md
├── apps/
│   └── {app_name}/
│       ├── archetype.md
│       ├── domain-refinement.md
│       ├── role-refinement.md
│       └── features/
│           └── {feature_name}.feature.md
└── .blueprint-meta.json
```

See [Conventions & Folder Structure](references/00-conventions.md) for the full annotated tree, output formatting rules, variable placeholders, file naming conventions, and cross-reference syntax.

---

## How to Use

When this skill is invoked, follow these steps:

### 1. Detect Current State

Run the progress checker to understand where the user is in the pipeline. The scripts ship with this skill — use `--project-dir` to point them at the user's project without needing to copy anything into the repo:

```bash
python3 {SKILL_DIR}/scripts/check-progress.py --project-dir {project_root}
```

Where `{SKILL_DIR}` is the directory containing this skill and `{project_root}` is the user's project directory (the parent of `spec/`). If the user's working directory is the project root, `--project-dir .` works.

If the `./spec` directory does not exist, the user is starting fresh.

### 2. Present Progress Summary

Show the user a concise summary of:
- Which Tier 1 steps are complete
- Which apps exist and their completion status
- The suggested next step

### 3. Ask What to Work On

Ask the user which step they'd like to work on. Default to the **next incomplete step** (lowest-numbered step whose prerequisites are met but whose outputs are missing).

If the user wants to work on a Tier 2+ step, confirm which app they're working on.

### 4. Load the Reference File

Read the appropriate `references/NN-*.md` file for the selected step. This file contains:
- The interrogation process (questions to ask)
- Output specification (what files to produce)
- Completion checklist

### 5. Execute the Step

Follow the reference file's interrogation process:
- Ask questions in the order specified
- Adapt based on user responses
- Read any prerequisite files from `./spec/` as specified
- Generate output files in the correct locations
- Create directories as needed

### 6. Complete and Continue

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
| 1 | `suite/domain-model.md` exists |
| 2 | `suite/role-permission-matrix.md` exists |
| 3 | `suite/ui-conventions.md` exists |
| 4 | `suite/navigation-shell.md` exists |
| 5 | `suite/api-event-contracts.md` exists |
| 6 | `apps/{app}/archetype.md` exists |
| 7 | `apps/{app}/domain-refinement.md` exists |
| 8 | `apps/{app}/role-refinement.md` exists |
| 9 | `apps/{app}/features/` has ≥1 `.feature.md` file |

---

## Step Dispatch Table

| Step | Description | Reference File | Prerequisites |
|------|-------------|---------------|--------------|
| 1 | Discover the business domain: entities, events, rules, boundaries | `references/01-domain-discovery.md` | None |
| 2 | Define global roles, permissions, and data visibility rules | `references/02-role-permission-matrix.md` | Step 1 |
| 3 | Establish UI conventions: design tokens, typography, spacing, accessibility | `references/03-ui-conventions.md` | Step 1 |
| 4 | Design the app shell: navigation, layout, global actions | `references/04-navigation-shell.md` | Steps 1–3 |
| 5 | Define suite-level API style, auth scheme, and conventions | `references/05-api-event-contracts.md` | Steps 1–2 |
| 6 | Classify app archetype and apply default patterns | `references/06-app-archetype.md` | Steps 1–5 |
| 7 | Refine domain model for app scope: owned vs referenced entities | `references/07-domain-refinement.md` | Steps 1, 6 |
| 8 | Refine roles and permissions for app scope | `references/08-role-refinement.md` | Steps 2, 6–7 |
| 9 | Write BDD feature scenarios in Given/When/Then format | `references/09-bdd-features.md` | Steps 6–8 |

---

## Conventions

See [references/00-conventions.md](references/00-conventions.md) for output formatting, file naming, variable placeholders, and cross-reference conventions.

---

## Tier-Specific Guidance

### Tier 1 — Suite Foundations (Steps 1–5)

These steps run **once** and establish global constraints. Every app in the suite inherits from these foundations. When working on Tier 1:
- Focus on breadth over depth — capture the full scope
- Think about what's shared across all apps
- Establish naming conventions and patterns that Tier 2+ will follow
- It's OK to leave some details as "TBD" — Tier 2/3 will refine them

### Tier 2 — App Classification (Steps 6–8)

These steps run **once per app**. They establish the app's identity within the suite. When working on Tier 2:
- Always ask the user for the app name first
- Create the `./spec/apps/{app_name}/` directory
- Read the suite-level files to understand the global context
- Focus on what makes this app unique vs. what it inherits
- The archetype selection (Step 6) drives defaults for all subsequent steps

### Tier 3 — BDD Feature Specifications (Step 9)

This step produces testable behavior definitions for each app. When working on Tier 3:
- Read the app's archetype, domain refinement, and role refinement before starting
- Build a feature inventory first and confirm it with the user before writing scenarios
- Work through features one at a time with the user
- Ensure every role from `role-refinement.md` is represented across the feature set
- Cover happy paths, error scenarios, and edge cases for each feature
- After generating feature files, run the Gherkin compatibility check:
  ```bash
  python3 {SKILL_DIR}/scripts/feature-md-to-gherkin.py --app {app_name} --project-dir {project_root} --validate-only
  ```

---

## Downstream Skills

After completing all 9 steps for all apps in the suite, the specification is ready for downstream processing:

- **webapp-architect** — Takes the blueprint spec and produces technical specification artifacts (information architecture, page patterns, state design, API contracts, authorization policies, generation briefs, and seed data). Run this skill next to complete the technical design.
- **webapp-prover** — Executes BDD scenarios against a deployed application and manages the build/test/fix cycle. Run this after the architect skill has produced generation briefs and the application has been built.

---

## Blueprint Metadata

On completion of all steps for all apps, the skill writes `.blueprint-meta.json` at the spec root:

```json
{
  "version": "1.0",
  "skill": "webapp-blueprint",
  "completed_at": "<ISO-8601>",
  "suite_name": "<suite>",
  "apps": ["<app1>", "<app2>"],
  "steps_completed": [1, 2, 3, 4, 5, 6, 7, 8, 9]
}
```
