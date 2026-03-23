# Pipeline Reference — Canonical Structure & Execution Rules

## Spec Folder Structure

This is the complete canonical folder structure for the `./spec/` output directory. Every pipeline step writes to a specific location within this tree.

```
spec/
│
├── suite/                                  # Tier 1 — Suite-level foundations (run once)
│   ├── domain-model.md                     # Step 1: Domain Discovery
│   ├── role-permission-matrix.md           # Step 2: Role & Permission Matrix
│   ├── ui-conventions.md                   # Step 3: UI Conventions
│   ├── navigation-shell.md                 # Step 4: Navigation & App Shell
│   └── api-event-contracts.md              # Step 5: Suite-Level API Conventions
│
├── apps/                                   # Tier 2–3 — Per-app specifications
│   └── {app_name}/                         # One directory per application
│       ├── archetype.md                    # Step 6: App Archetype Classification
│       ├── domain-refinement.md            # Step 7: Domain Model Refinement
│       ├── role-refinement.md              # Step 8: Role & Permission Refinement
│       └── features/                       # Step 9: BDD Feature Specifications
│           └── {feature_name}.feature.md   #   One file per feature
│
└── .blueprint-meta.json                    # Written on pipeline completion
```

---

## Execution Order

Steps must be executed respecting their dependency chain. Within a tier, the numbered order is the recommended sequence, though some steps can be done in parallel where noted.

### Tier 1 — Suite Foundations

```
Step 1 ──┬── Step 2 ──── Step 5
         │
         ├── Step 3
         │
         └── Step 4 (requires 1, 2, 3)
```

Steps 2, 3, and 5 all depend on Step 1 but are independent of each other. Step 4 depends on Steps 1–3.

### Tier 2 — App Classification

```
Steps 1–5 ──── Step 6 ──── Step 7 ──── Step 8
```

Strictly sequential within Tier 2. All Tier 1 must complete before any Tier 2 step.

### Tier 3 — BDD Feature Specifications

```
Steps 6–8 ──── Step 9
```

Step 9 depends on all Tier 2 steps. It produces one `.feature.md` file per feature.

---

## Inheritance Principle

Specifications follow a top-down inheritance model:

1. **Suite-level** specs (Tier 1) establish global constraints
2. **App-level** specs (Tier 2–3) inherit from and refine suite-level specs
3. Apps may **not contradict** suite-level constraints — they may only refine or extend them

Examples:
- An app's roles must be a subset of (or derive from) the global role matrix
- An app's entities must trace back to the suite domain model (or be explicitly app-specific)
- An app's API contracts must follow the suite-level API conventions

---

## Visibility Rules

| Artifact Level | Visible To | Mutable By |
|---|---|---|
| Suite specs (`suite/*`) | All apps | Tier 1 steps only |
| App specs (`apps/{app}/*`) | That app only | Tier 2–3 steps for that app |

---

## Multi-App Workflow

For suites with multiple applications:

1. Complete **all Tier 1** steps first (once)
2. For each app:
   a. Complete **Tier 2** (Steps 6–8)
   b. Complete **Tier 3** (Step 9)
3. Apps can be specified in any order, but each app should complete its full Tier 2–3 pipeline before heavy investment in the next app (to surface suite-level issues early)

---

## Re-Running Steps

Steps can be re-run to update specs. When a step is re-run:
- Its output files are **overwritten** with new content
- Downstream steps may need to be re-validated
- The user should be warned about downstream impacts before re-running

---

## Downstream Processing

After all 9 steps are complete for all apps, the specification is ready for:

- **webapp-architect** — Technical specification (information architecture, page patterns, state design, API contracts, authorization, generation briefs, seed data)
- **webapp-prover** — BDD test execution and build/test/fix cycle
