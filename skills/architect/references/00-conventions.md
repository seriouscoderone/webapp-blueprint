# Conventions & Folder Structure

## Spec Folder Structure

Spec artifacts are written under `./spec/` relative to the working directory. The architect skill (Steps 10-17) reads from the existing suite and app-level artifacts produced by webapp-blueprint (Steps 1-9) and writes new technical specification artifacts.

```
spec/
├── .blueprint-meta.json                ← prerequisite: written by webapp-blueprint
├── .architect-meta.json                ← written by webapp-architect on completion
│
├── suite/                              ← Tier 1 — Suite-level foundations (Steps 1-5, read-only)
│   ├── domain-model.md                 # Step 1: Domain Discovery
│   ├── role-permission-matrix.md       # Step 2: Role & Permission Matrix
│   ├── ui-conventions.md               # Step 3: UI Conventions
│   ├── navigation-shell.md             # Step 4: Navigation & App Shell
│   └── api-event-contracts.md          # Step 5: Suite-Level API Conventions
│
├── apps/                               ← Tier 2-4 — Per-app specifications
│   └── {app_name}/
│       │
│       │  # Tier 2 — App Classification (Steps 6-8, read-only for architect)
│       ├── archetype.md                # Step 6: App Archetype Classification
│       ├── domain-refinement.md        # Step 7: Domain Model Refinement
│       ├── role-refinement.md          # Step 8: Role & Permission Refinement
│       │
│       │  # Tier 3 — BDD Features (Step 9, read-only for architect)
│       ├── features/                   # Step 9: BDD Feature Specifications
│       │   └── {feature_name}.feature.md
│       │
│       │  # Tier 3 — Technical Specification (Steps 10-14, written by architect)
│       ├── ia-spec.md                  # Step 10: Information Architecture
│       ├── pages/                      # Step 11: Page Pattern Specifications
│       │   └── {page_name}.md          #   One file per page
│       ├── state-interaction.md        # Step 12: State & Interaction Design
│       ├── api-contracts.md            # Step 13: App-Level API Contracts
│       ├── authorization.md            # Step 14: Authorization Policy
│       │
│       │  # Tier 4 — Generation (Steps 16-17, written by architect)
│       ├── seed-data.md                # Step 17: Seed Data Specification
│       └── generation-briefs/          # Step 16: Frontend Generation Briefs
│           ├── _build-order.md         #   Ordered build plan
│           └── {page_name}-brief.md    #   One brief per page
│
└── validation/                         ← Tier 4 — Validation reports
    └── reports/
        └── {app_name}/                 # Step 15: Spec Validation
            ├── gap-report.md           #   Missing artifacts
            ├── contradiction-report.md #   Conflicting specs
            └── completeness-score.md   #   Scores & summary
```

---

## Conventions

### Output Formatting
- All output files are **Markdown** (`.md`)
- Use ATX headings (`#`, `##`, `###`)
- Use tables for structured data (roles, permissions, entities, endpoints)
- Use fenced code blocks for schemas and examples
- Use bullet lists for enumerations
- Keep line lengths reasonable (soft-wrap friendly)

### Variable Placeholders
- `{app_name}` — Lowercase, kebab-case app identifier (e.g., `admin-portal`)
- `{feature_name}` — Lowercase, kebab-case feature identifier (e.g., `user-registration`)
- `{page_name}` — Lowercase, kebab-case page identifier (e.g., `order-list`)

### File Naming
- Suite files: descriptive kebab-case (e.g., `domain-model.md`)
- App files: descriptive kebab-case in app directory
- Feature files: `{feature_name}.feature.md`
- Page files: `{page_name}.md`
- Generation briefs: `{page_name}-brief.md`

### Cross-References
When referencing another spec file, use relative paths from `./spec/`:
- `See [Domain Model](../suite/domain-model.md)`
- `Derived from [Global Roles](../../suite/role-permission-matrix.md)`
- `See [IA Spec](ia-spec.md)` (within same app directory)
- `See [Page Spec](pages/{page_name}.md)` (within same app directory)
