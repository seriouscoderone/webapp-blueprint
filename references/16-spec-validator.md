# Step 16: Spec Consistency Validator

## Tier
4 — Validation and generation (runs after all Tier 1-3 steps for an app are complete)

## Purpose
The Spec Consistency Validator performs comprehensive cross-referencing checks across the entire specification for a given app. It identifies gaps (missing artifacts), contradictions (conflicting definitions), and coverage holes (entities, roles, or features that are incompletely specified). This step ensures the specification is internally consistent and complete before code generation begins.

## Prerequisites
All specification files for the target app must exist before validation:

**Suite-level (Tier 1):**
- `./spec/suite/domain-model.md` (Step 1)
- `./spec/suite/role-permission-matrix.md` (Step 2)
- `./spec/suite/design-system.md` (Step 3)
- `./spec/suite/navigation-shell.md` (Step 4)
- `./spec/suite/api-event-contracts.md` (Step 5)

**App-level (Tier 2):**
- `./spec/apps/{app_name}/archetype.md` (Step 6)
- `./spec/apps/{app_name}/domain-refinement.md` (Step 7)
- `./spec/apps/{app_name}/role-refinement.md` (Step 8)

**App-level (Tier 3):**
- `./spec/apps/{app_name}/features/*.feature.md` (Step 9)
- `./spec/apps/{app_name}/ia-spec.md` (Step 10)
- `./spec/apps/{app_name}/pages/*.md` (Step 11)
- `./spec/apps/{app_name}/components/*.md` (Step 12)
- `./spec/apps/{app_name}/state-interaction.md` (Step 13)
- `./spec/apps/{app_name}/api-contracts.md` (Step 14)
- `./spec/apps/{app_name}/authorization.md` (Step 15)

## Inputs to Read
- Every file listed in Prerequisites above for the target `{app_name}`
- The validation script at `scripts/validate-spec.py`

## App Selection Process
Before running validation, determine which app to validate:
1. List all apps found in `./spec/apps/` subdirectories.
2. Ask: "Which app do you want to validate?"
3. Confirm that all prerequisite files exist for the selected app before proceeding.
4. If any prerequisites are missing, report which steps need to be completed first and stop.

## Interrogation Process

This step is primarily automated. The interrogation is minimal and focused on confirming scope and reviewing results.

### 1. Pre-Validation Confirmation
- "Which app do you want to validate?" (select from existing apps)
- "Do you want to run a full validation or focus on specific check categories?" (Entity, Role, Feature, Page, Component, API, Authorization, State, Navigation, Design System)
- "Are there any known gaps or in-progress items I should flag but not count as failures?"

### 2. Post-Validation Review
After the script runs, walk through results with the user:
- "Here are the results. Let's start with the highest-severity issues."
- For each gap: "This artifact is missing — should we create it now, defer it, or mark it as intentionally omitted?"
- For each contradiction: "These two specs disagree — which definition is correct?"
- For each coverage hole: "This [entity/role/feature] is only partially specified — what's missing?"

### 3. Remediation Planning
- "Would you like to fix these issues now or generate a remediation checklist?"
- "Are any of these gaps acceptable? For example, features planned for a future release that don't need specs yet?"
- "After fixing, do you want to re-run validation to confirm everything passes?"

## Cross-Reference Checks

The validator performs the following ten categories of checks:

### 1. Entity Consistency
Verify that every entity referenced in `apps/{app_name}/domain-refinement.md` traces back to an entity defined in `suite/domain-model.md`.
- Every app-level entity must have a parent entry in the suite domain model
- App-level attributes must not contradict suite-level attribute definitions
- Lifecycle states in the refinement must be a subset of or extension of suite-level states
- Relationships defined at the app level must be compatible with suite-level relationship definitions

### 2. Role Consistency
Verify that every role in `apps/{app_name}/role-refinement.md` derives from a role defined in `suite/role-permission-matrix.md`.
- Every app-level role must map to a suite-level role
- App-level permissions must not exceed the permissions granted at the suite level
- App-level data visibility rules must be consistent with suite-level scope definitions
- Any role referenced in authorization.md must appear in the role refinement

### 3. Feature Coverage
Verify that every feature defined in `apps/{app_name}/features/` has substantive BDD scenarios.
- Each `.feature.md` file must contain at least one `Scenario:` or `Scenario Outline:` block
- Every `Given/When/Then` step must reference entities and roles that exist in the spec
- Features referenced in page specs must have corresponding `.feature.md` files
- No orphan features — every feature must be referenced by at least one page

### 4. Page Coverage
Verify that every page listed in `apps/{app_name}/ia-spec.md` has a corresponding page pattern spec in `apps/{app_name}/pages/`.
- Each route defined in the IA spec must have a matching `pages/{page_name}.md` file
- Page file names must match the kebab-case version of the page name in the IA spec
- Every page must define its layout pattern, which must exist in the design system or archetype defaults

### 5. Component Coverage
Verify that every component referenced in page specs has a corresponding component contract.
- Each component named in any `pages/*.md` file must have a matching `components/{component_name}.md` file
- Component prop interfaces must be fully defined (no TBD or placeholder props)
- Components referenced in multiple pages must have consistent prop interfaces across all references

### 6. API Coverage
Verify that every data requirement in page specs, state specs, and component contracts has a corresponding API endpoint.
- Every data-fetching hook or query in `state-interaction.md` must map to an endpoint in `api-contracts.md`
- Every mutation action in state specs must map to a mutation endpoint
- Every endpoint in `api-contracts.md` must be referenced by at least one page, component, or state spec
- App-level endpoints must not conflict with suite-level API contracts in `suite/api-event-contracts.md`

### 7. Authorization Coverage
Verify that every route and API endpoint has an authorization policy defined.
- Every route in `ia-spec.md` must have a corresponding entry in `authorization.md`
- Every endpoint in `api-contracts.md` must have a corresponding authorization rule
- Authorization roles must match roles defined in `role-refinement.md`
- Conditional access rules must reference valid entity attributes and states

### 8. State Coverage
Verify that every page has loading, error, and empty states defined.
- Each page in `pages/*.md` must define at minimum: loading state, error state, empty state
- State transitions referenced in `state-interaction.md` must match the states defined in page specs
- Optimistic update strategies must be defined for mutation-heavy pages
- Form validation states must be defined for pages containing forms

### 9. Navigation Consistency
Verify that all page cross-references (connected pages, breadcrumbs, navigation links) resolve to valid pages.
- Every "connected page" reference in a page spec must match a valid page in `ia-spec.md`
- Breadcrumb paths must follow the IA hierarchy
- Navigation links defined in `suite/navigation-shell.md` must resolve to pages defined in this app or other suite apps
- Deep link URLs must match route patterns defined in `ia-spec.md`

### 10. Design System Compliance
Verify that component variants and styling tokens align with the design system.
- Component variants referenced in page specs must exist in the design system or the component contract
- Color, spacing, and typography tokens used in component contracts must exist in `suite/design-system.md`
- Responsive breakpoints referenced in page specs must match design system breakpoints
- Icon names referenced in components must exist in the design system icon set

## Scoring Rubric

### Completeness Score (0-100)
Measures the percentage of expected artifacts that exist. Each artifact category has equal weight within the score.

| Check | What Counts as "Complete" |
|-------|--------------------------|
| Suite files | All 5 Tier 1 files exist |
| App archetype | `archetype.md` exists |
| Domain refinement | `domain-refinement.md` exists |
| Role refinement | `role-refinement.md` exists |
| Feature files | At least one `.feature.md` per feature area identified in archetype |
| IA spec | `ia-spec.md` exists |
| Page specs | One `pages/*.md` file per page listed in IA spec |
| Component specs | One `components/*.md` file per component referenced in page specs |
| State interaction | `state-interaction.md` exists |
| API contracts | `api-contracts.md` exists |
| Authorization | `authorization.md` exists |

Formula: `(existing artifacts / expected artifacts) * 100`

### Consistency Score (0-100)
Measures the percentage of cross-references that resolve correctly without contradictions.

| Check | What Counts as "Consistent" |
|-------|----------------------------|
| Entity references | App entities map to suite entities without attribute conflicts |
| Role references | App roles map to suite roles without permission escalation |
| Page references | Navigation cross-references resolve to valid pages |
| Component references | Components in page specs match component contracts |
| API references | Data requirements map to defined endpoints |
| Authorization references | Routes and endpoints have matching auth policies |
| Design token references | Tokens used in components exist in the design system |

Formula: `(valid cross-references / total cross-references) * 100`

### Coverage Score (0-100)
Measures the percentage of entities, roles, and features that are fully specified end-to-end (from domain model through to authorization and state).

| Check | What Counts as "Covered" |
|-------|-------------------------|
| Entity coverage | Entity appears in domain model, refinement, at least one feature, at least one page, API contracts, and authorization |
| Role coverage | Role appears in permission matrix, refinement, authorization, and at least one feature scenario |
| Feature coverage | Feature has BDD scenarios, is referenced by a page, and has supporting API endpoints |
| State coverage | Page has loading, error, and empty states defined |

Formula: `(fully covered items / total items) * 100`

### Overall Score
Weighted average of the three scores:
- **40% Completeness** — do the artifacts exist?
- **35% Consistency** — do they agree with each other?
- **25% Coverage** — do they fully specify the domain end-to-end?

Formula: `(completeness * 0.40) + (consistency * 0.35) + (coverage * 0.25)`

**Thresholds:**
- **≥ 80**: Ready — proceed to Step 17 (Generation Briefs) and Step 18 (Seed Data)
- **65–79**: Conditional — user may proceed with acknowledged gaps; list all gaps explicitly
- **< 65**: Blocked — do not proceed; surface the top 5 gaps and require remediation first

---

## Gate: Proceeding to Steps 17 and 18

The overall score determines whether the spec is ready to proceed:

- **Score ≥ 80: PASS** — proceed to Step 17 (Generation Briefs) and/or Step 18 (Seed Data Specification)
- **Score 65–79: CONDITIONAL** — user may proceed but Claude must explicitly list every known gap and confirm the user accepts the risk of incomplete generation output
- **Score < 65: BLOCK** — do not proceed to Step 17 or Step 18; surface the top 5 highest-impact gaps and require the user to remediate them before re-running validation

## Output Specification

### `./spec/validation/reports/{app_name}/gap-report.md`

```markdown
# Gap Report: {App Display Name}

## Summary
- **Total expected artifacts**: {N}
- **Missing artifacts**: {N}
- **Severity**: {Critical / Warning / Info}

## Missing Artifacts
### Critical (blocks generation)
| # | Expected Artifact | Relevant Step | Impact |
|---|-------------------|---------------|--------|
{Rows for each missing artifact that would block code generation}

### Warning (degrades generation quality)
| # | Expected Artifact | Relevant Step | Impact |
|---|-------------------|---------------|--------|
{Rows for each missing artifact that would reduce output quality}

### Info (optional / nice-to-have)
| # | Expected Artifact | Relevant Step | Impact |
|---|-------------------|---------------|--------|
{Rows for each missing but non-essential artifact}

## Remediation Steps
{Ordered list of steps to close the gaps, referencing specific pipeline steps to re-run}
```

### `./spec/validation/reports/{app_name}/contradiction-report.md`

```markdown
# Contradiction Report: {App Display Name}

## Summary
- **Total cross-references checked**: {N}
- **Contradictions found**: {N}
- **Severity**: {Critical / Warning / Info}

## Contradictions
### {Check Category Name} (e.g., Entity Consistency)
| # | Source A | Source B | Conflict Description | Suggested Resolution |
|---|---------|---------|---------------------|---------------------|
{Rows for each contradiction found in this category}

{Repeat for each check category that found contradictions}

## Resolution Plan
{Ordered list of contradictions to resolve, starting with the highest severity}
```

### `./spec/validation/reports/{app_name}/completeness-score.md`

```markdown
# Completeness Score: {App Display Name}

## Overall Score: {N}/100
**Verdict**: {Ready for generation / Minor gaps / Significant gaps / Incomplete}

## Score Breakdown
| Category | Score | Weight | Weighted |
|----------|-------|--------|----------|
| Completeness | {N}/100 | 40% | {N} |
| Consistency | {N}/100 | 35% | {N} |
| Coverage | {N}/100 | 25% | {N} |
| **Overall** | | | **{N}/100** |

## Completeness Details
| Artifact Category | Expected | Found | Score |
|-------------------|----------|-------|-------|
{One row per artifact category}

## Consistency Details
| Check Category | References | Valid | Issues | Score |
|----------------|-----------|-------|--------|-------|
{One row per cross-reference check}

## Coverage Details
| Item Type | Total | Fully Covered | Partially Covered | Not Covered | Score |
|-----------|-------|---------------|-------------------|-------------|-------|
{Rows for entities, roles, features, states}

## Recommendations
{Prioritized list of actions to improve the score, ordered by impact}
```

## Completion Checklist
- [ ] Target app selected and all prerequisites confirmed present
- [ ] Validation script executed against the app's specification files
- [ ] All 10 cross-reference check categories evaluated
- [ ] `./spec/validation/reports/{app_name}/gap-report.md` created with all missing artifacts
- [ ] `./spec/validation/reports/{app_name}/contradiction-report.md` created with all conflicts
- [ ] `./spec/validation/reports/{app_name}/completeness-score.md` created with scores and breakdown
- [ ] Overall score computed with correct weighting (40/35/25)
- [ ] Results reviewed with the user and remediation plan agreed upon
- [ ] Any critical gaps or contradictions resolved (or explicitly deferred with rationale)
