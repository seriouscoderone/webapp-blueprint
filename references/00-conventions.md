# Conventions & Folder Structure

## Spec Folder Structure

Spec artifacts are written under `./spec/` relative to the working directory. Runtime artifacts (Step 19 and beyond) are written to sibling folders:

```
spec/                               ← specification artifacts (blueprint skill)
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

blackbox/                           ← runtime artifact folder (build/test cycle)
└── templates/
    └── {app_name}_test.template.json   ← Step 19 output
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
- `{component_name}` — PascalCase component identifier (e.g., `DataTable`)

### File Naming
- Suite files: descriptive kebab-case (e.g., `domain-model.md`)
- App files: descriptive kebab-case in app directory
- Feature files: `{feature_name}.feature.md`
- Page files: `{page_name}.md`
- Component files: `{component_name}.md`

### Cross-References
When referencing another spec file, use relative paths from `./spec/`:
- `See [Domain Model](../suite/domain-model.md)`
- `Derived from [Global Roles](../../suite/role-permission-matrix.md)`
