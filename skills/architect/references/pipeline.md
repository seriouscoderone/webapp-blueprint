# Pipeline Reference — Architect Dependency Graph (Steps 10-17)

## Prerequisites

Steps 1-9 outputs are prerequisites for the architect pipeline. These are produced by `webapp-blueprint` and read from the `spec/` folder:

- **Step 1:** `suite/domain-model.md`
- **Step 2:** `suite/role-permission-matrix.md`
- **Step 3:** `suite/ui-conventions.md`
- **Step 4:** `suite/navigation-shell.md`
- **Step 5:** `suite/api-event-contracts.md`
- **Step 6:** `apps/{app}/archetype.md`
- **Step 7:** `apps/{app}/domain-refinement.md`
- **Step 8:** `apps/{app}/role-refinement.md`
- **Step 9:** `apps/{app}/features/*.feature.md`

The architect requires `.blueprint-meta.json` at the spec root confirming all 9 steps are complete.

---

## Dependency Graph

### Tier 3 — Technical Specification (Steps 10-14)

```
Steps 6-7, 9 ──── Step 10 (IA) ──┬── Step 11 (Pages) ──┬── Step 12 (State)
                                  │                      │
                                  │                      ├── Step 13 (APIs)
                                  │                      │     (also needs 5, 7)
                                  │                      │
                                  └──────────────────────┴── Step 14 (Authorization)
                                                               (also needs 8, 13)
```

- **Step 10** (Information Architecture) reads Steps 6-7, 9
- **Step 11** (Page Patterns) reads Steps 6, 9-10
- **Step 12** (State & Interaction) reads Steps 9, 11
- **Step 13** (API Contracts) reads Steps 5, 7, 11, 12
- **Step 14** (Authorization Policy) reads Steps 8, 10, 13

Steps 12 and 13 both depend on Step 11 but are independent of each other and can be worked in parallel. Step 14 depends on Steps 10 and 13 (and transitively on 12 via 13).

### Tier 4 — Validation & Generation (Steps 15-17)

```
Steps 1-14 ──── Step 15 (Validate) ──── Step 16 (Generation Briefs) ──── Step 17 (Seed Data)
```

- **Step 15** (Spec Validator) reads all Steps 1-14 outputs
- **Step 16** (Generation Brief) reads all Steps 1-15 outputs (requires validation score >= 80)
- **Step 17** (Seed Data) reads Steps 1, 9, 13, 16

---

## Execution Order

The recommended execution order within the architect pipeline:

1. Declare tech stack (stored in `.architect-meta.json`)
2. **Step 10** — Information Architecture
3. **Step 11** — Page Patterns (one file per page)
4. **Step 12** — State & Interaction
5. **Step 13** — API Contracts
6. **Step 14** — Authorization Policy
7. **Step 15** — Spec Validator (fix gaps until score >= 80)
8. **Step 16** — Generation Briefs
9. **Step 17** — Seed Data

---

## Inheritance Principle

The architect inherits all suite-level and app-level constraints from Steps 1-9:

1. **Suite-level** specs (Tier 1) establish global constraints — read-only for the architect
2. **App-level** specs (Tier 2, Step 9) provide domain and feature context — read-only for the architect
3. **Technical specs** (Steps 10-14) must be consistent with all inherited constraints
4. Apps may **not contradict** suite-level constraints — they may only refine or extend them

---

## Visibility Rules

| Artifact Level | Visible To | Mutable By |
|---|---|---|
| Suite specs (`suite/*`) | Architect (read-only) | webapp-blueprint only |
| App classification (`archetype.md`, etc.) | Architect (read-only) | webapp-blueprint only |
| BDD features (`features/*`) | Architect (read-only) | webapp-blueprint only |
| Technical specs (Steps 10-14) | Architect, downstream | Architect (Steps 10-14) |
| Validation reports (`validation/*`) | All (read-only reference) | Architect (Step 15) |
| Generation briefs | Code generation tools | Architect (Step 16) |
| Seed data | Code generation tools | Architect (Step 17) |

---

## Re-Running Steps

Steps can be re-run to update specs. When a step is re-run:
- Its output files are **overwritten** with new content
- Downstream steps may need to be re-validated (Step 15 will catch inconsistencies)
- The user should be warned about downstream impacts before re-running
