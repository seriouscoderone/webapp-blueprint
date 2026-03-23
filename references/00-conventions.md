# Conventions & Folder Structure

## Spec Folder Structure

Spec artifacts are written under `./spec/` relative to the working directory:

```
spec/                               ← specification artifacts (blueprint skill)
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
└── .blueprint-meta.json            ← written on pipeline completion
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

### File Naming
- Suite files: descriptive kebab-case (e.g., `domain-model.md`)
- App files: descriptive kebab-case in app directory
- Feature files: `{feature_name}.feature.md`

### Cross-References
When referencing another spec file, use relative paths from `./spec/`:
- `See [Domain Model](../suite/domain-model.md)`
- `Derived from [Global Roles](../../suite/role-permission-matrix.md)`
