---
name: webapp-blueprint
description: Comprehensive enterprise web application specification pipeline. Guides users through 19 sequential design steps — from domain discovery, role matrices, and design systems through BDD features, page specs, component contracts, API definitions, authorization policies, seed data, and blackbox test templates. Produces a complete `/spec` folder ready for code generation. Use when designing, specifying, or planning a web application or application suite.
---

# Webapp Blueprint — Enterprise Application Specification Pipeline

## Overview

This skill implements a **19-step specification pipeline** organized into **4 tiers** that produces a comprehensive `./spec/` folder of markdown artifacts plus a machine-readable blackbox test template. Each step's outputs feed into subsequent steps, building from high-level domain concepts down to page-level generation briefs.

The pipeline is designed for **enterprise application suites** — collections of related web applications that share a domain model, design system, and role hierarchy. It works equally well for a single application.

**Tiers at a glance:**
- **Tier 1** (Steps 1–5): Suite-level foundations — run once
- **Tier 2** (Steps 6–8): Per-app classification — run once per app
- **Tier 3** (Steps 9–15): Per-app detailed specification — run per app
- **Tier 4** (Steps 16–19): Validation, generation briefs, seed data, and blackbox test template — run after Tier 3

---

## Pipeline at a Glance

| Step | Name | Tier | Reads From | Writes To | Reference |
|------|------|------|-----------|-----------|-----------|
| 1 | Domain Discovery | 1 | — | `suite/domain-model.md` | `references/01-domain-discovery.md` |
| 2 | Role & Permission Matrix | 1 | Step 1 | `suite/role-permission-matrix.md` | `references/02-role-permission-matrix.md` |
| 3 | Design System | 1 | Step 1 | `suite/design-system.md` | `references/03-design-system.md` |
| 4 | Navigation Shell | 1 | Steps 1–3 | `suite/navigation-shell.md` | `references/04-navigation-shell.md` |
| 5 | API & Event Contracts | 1 | Steps 1–2 | `suite/api-event-contracts.md` | `references/05-api-event-contracts.md` |
| 6 | App Archetype | 2 | Steps 1–5 | `apps/{app}/archetype.md` | `references/06-app-archetype.md` |
| 7 | Domain Refinement | 2 | Steps 1, 6 | `apps/{app}/domain-refinement.md` | `references/07-domain-refinement.md` |
| 8 | Role Refinement | 2 | Steps 2, 6–7 | `apps/{app}/role-refinement.md` | `references/08-role-refinement.md` |
| 9 | BDD Features | 3 | Steps 6–8 | `apps/{app}/features/*.feature.md` | `references/09-bdd-features.md` |
| 10 | Information Architecture | 3 | Steps 6–7, 9 | `apps/{app}/ia-spec.md` | `references/10-ia-spec.md` |
| 11 | Page Patterns | 3 | Steps 6, 9–10 | `apps/{app}/pages/*.md` | `references/11-page-patterns.md` |
| 12 | Component Inventory | 3 | Steps 3, 11 | `apps/{app}/components/*.md` | `references/12-component-inventory.md` |
| 13 | State & Interaction | 3 | Steps 9, 11–12 | `apps/{app}/state-interaction.md` | `references/13-state-interaction.md` |
| 14 | API Contracts | 3 | Steps 5, 7, 11, 13 | `apps/{app}/api-contracts.md` | `references/14-api-contracts.md` |
| 15 | Authorization Policy | 3 | Steps 8, 10, 14 | `apps/{app}/authorization.md` | `references/15-authorization-policy.md` |
| 16 | Spec Validator | 4 | Steps 1–15 | `validation/reports/{app}/*` | `references/16-spec-validator.md` |
| 17 | Generation Brief | 4 | Steps 1–16 | `apps/{app}/generation-briefs/*` | `references/17-generation-brief.md` |
| 18 | Seed Data Specification | 4 | Steps 1, 9, 14, 17 | `apps/{app}/seed-data.md` | `references/18-seed-data.md` |
| 19 | Blackbox Test Template | 4 | Step 9 | `blackbox/templates/{app}_test.template.json` | `references/19-blackbox-template.md` |

---

## Spec Folder Structure

All outputs are written under `./spec/` relative to the working directory:

```
spec/
├── suite/
│   ├── domain-model.md
│   ├── role-permission-matrix.md
│   ├── design-system.md
│   ├── navigation-shell.md
│   └── api-event-contracts.md
├── apps/
│   └── {app_name}/
│       ├── archetype.md
│       ├── domain-refinement.md
│       ├── role-refinement.md
│       ├── features/
│       │   └── {feature_name}.feature.md
│       ├── ia-spec.md
│       ├── pages/
│       │   └── {page_name}.md
│       ├── components/
│       │   └── {component_name}.md
│       ├── state-interaction.md
│       ├── api-contracts.md
│       ├── authorization.md
│       ├── seed-data.md
│       └── generation-briefs/
│           ├── _build-order.md
│           └── {page_name}-brief.md
└── validation/
    └── reports/
        └── {app_name}/
            ├── gap-report.md
            ├── contradiction-report.md
            └── completeness-score.md
```

See [Conventions & Folder Structure](references/00-conventions.md) for the full annotated tree, output formatting rules, variable placeholders, file naming conventions, and cross-reference syntax.

---

## How to Use

When this skill is invoked, follow these steps:

### 1. Detect Current State

Run the progress checker to understand where the user is in the pipeline:

```bash
python3 scripts/check-progress.py --spec-dir ./spec
```

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
| 3 | `suite/design-system.md` exists |
| 4 | `suite/navigation-shell.md` exists |
| 5 | `suite/api-event-contracts.md` exists |
| 6 | `apps/{app}/archetype.md` exists |
| 7 | `apps/{app}/domain-refinement.md` exists |
| 8 | `apps/{app}/role-refinement.md` exists |
| 9 | `apps/{app}/features/` has ≥1 `.feature.md` file |
| 10 | `apps/{app}/ia-spec.md` exists |
| 11 | `apps/{app}/pages/` has ≥1 `.md` file |
| 12 | `apps/{app}/components/` has ≥1 `.md` file |
| 13 | `apps/{app}/state-interaction.md` exists |
| 14 | `apps/{app}/api-contracts.md` exists |
| 15 | `apps/{app}/authorization.md` exists |
| 16 | `validation/reports/{app}/completeness-score.md` exists |
| 17 | `apps/{app}/generation-briefs/_build-order.md` exists |
| 18 | `apps/{app}/seed-data.md` exists |
| 19 | `blackbox/templates/{app}_test.template.json` exists |

---

## Step Dispatch Table

| Step | Description | Reference File | Prerequisites |
|------|-------------|---------------|--------------|
| 1 | Discover the business domain: entities, events, rules, boundaries | `references/01-domain-discovery.md` | None |
| 2 | Define global roles, permissions, and data visibility rules | `references/02-role-permission-matrix.md` | Step 1 |
| 3 | Establish design tokens: colors, typography, spacing, accessibility | `references/03-design-system.md` | Step 1 |
| 4 | Design the app shell: navigation, layout, global actions | `references/04-navigation-shell.md` | Steps 1–3 |
| 5 | Define suite-level API style, auth scheme, and event bus | `references/05-api-event-contracts.md` | Steps 1–2 |
| 6 | Classify app archetype and apply default patterns | `references/06-app-archetype.md` | Steps 1–5 |
| 7 | Refine domain model for app scope: owned vs referenced entities | `references/07-domain-refinement.md` | Steps 1, 6 |
| 8 | Refine roles and permissions for app scope | `references/08-role-refinement.md` | Steps 2, 6–7 |
| 9 | Write BDD feature scenarios in Given/When/Then format | `references/09-bdd-features.md` | Steps 6–8 |
| 10 | Define information architecture: sitemap, URLs, navigation | `references/10-ia-spec.md` | Steps 6–7, 9 |
| 11 | Specify page layouts, data needs, states, and actions | `references/11-page-patterns.md` | Steps 6, 9–10 |
| 12 | Inventory components: contracts, props, variants, accessibility | `references/12-component-inventory.md` | Steps 3, 11 |
| 13 | Design state management, data flow, and interaction patterns | `references/13-state-interaction.md` | Steps 9, 11–12 |
| 14 | Define app-level API endpoints, schemas, and events | `references/14-api-contracts.md` | Steps 5, 7, 11, 13 |
| 15 | Specify authorization policies: routes, APIs, data, UI elements | `references/15-authorization-policy.md` | Steps 8, 10, 14 |
| 16 | Validate spec consistency and completeness with scoring | `references/16-spec-validator.md` | Steps 1–15 |
| 17 | Generate per-page briefs with build order for code generation | `references/17-generation-brief.md` | Steps 1–16 |
| 18 | Define realistic seed data covering all BDD scenarios and roles | `references/18-seed-data.md` | Steps 1, 9, 14, 17 |
| 19 | Generate machine-readable JSON test template from BDD features | `references/19-blackbox-template.md` | Step 9 |

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

### Tier 3 — App Specification (Steps 9–15)

These steps produce the detailed artifacts for each app. When working on Tier 3:
- Work iteratively — it's normal to revisit earlier steps as details emerge
- Steps 9–11 (features, IA, pages) often inform each other
- Steps 12–14 (components, state, APIs) build on the page specs
- Step 15 (authorization) ties everything together
- For steps that produce multiple files (9, 11, 12), work through them one at a time with the user

### Tier 4 — Validation & Generation (Steps 16–19)

These steps run **after Tier 3 is complete** for an app. When working on Tier 4:
- Step 16 uses `scripts/validate-spec.py` to automate cross-reference checks
- Review validation results with the user and fix gaps; a score ≥ 80 is required to proceed
- Step 17 produces the final generation briefs — these drive the code generation sequence
- Step 18 produces the seed data specification — ensures generated code can be tested immediately
- The build order in Step 17 also determines the correct seed insertion order for Step 18
- Step 19 uses `scripts/generate-blackbox-template.py` to produce a machine-readable JSON test template — the handoff artifact for the build/test cycle skill
