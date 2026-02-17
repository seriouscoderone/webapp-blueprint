# Step 17: Frontend Generation Brief

## Tier
4 — Validation and generation (runs after all Tier 1-3 steps and Step 16 validation are complete)

## Purpose
The Frontend Generation Brief produces per-page build instructions optimized for feeding into an AI code generation pipeline. Each brief is a self-contained document that gives a code generator everything it needs to build one page — design tokens, data requirements, component manifest, state shape, interaction flows, authorization rules, and acceptance criteria. The build order ensures pages are generated in dependency order so shared components and simpler pages are built first.

## Prerequisites
All specification files for the target app plus passing validation:

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

**Validation (Tier 4):**
- `./spec/validation/reports/{app_name}/completeness-score.md` (Step 16) — overall score must be 75 or above

## Inputs to Read
- Every file listed in Prerequisites above for the target `{app_name}`
- All three validation reports from Step 16 (to understand known gaps and their status)

## App Selection Process
Before generating briefs, determine scope:
1. List all apps found in `./spec/apps/` subdirectories.
2. Ask: "Which app do you want to generate briefs for?"
3. Check that Step 16 validation reports exist and the overall score is 75 or above.
4. If the score is below 75, warn the user and recommend re-running Step 16 after fixing gaps. Allow them to proceed if they explicitly choose to.

## Interrogation Process

### 1. Target App & Scope
- "Which app do you want to generate briefs for?" (select from existing apps)
- "Do you want to generate briefs for all pages, or start with a subset?" If subset: "Which pages should I prioritize?"
- "Are there any pages that are blocked or deferred? I'll exclude them from the build order."

### 2. Target Framework & Conventions
- "What frontend framework will be used?" (React, Vue, Svelte, SolidJS, Angular, or other)
- "What styling approach?" (Tailwind CSS, CSS Modules, Styled Components, vanilla CSS, or other)
- "What state management library, if any?" (React Query / TanStack Query, Zustand, Redux Toolkit, Pinia, Jotai, or framework defaults)
- "What routing library?" (React Router, Next.js App Router, Vue Router, SvelteKit, or other)
- "Are there any code generation tools or templates already in use that the briefs should align with?"

### 3. Generation Preferences
- "Should briefs include mock data examples for each page?" (useful for visual development)
- "Should briefs include test scaffolding hints?" (describe which tests to write alongside the page)
- "What level of component granularity do you want?" (one brief per page with inline component details, or separate component briefs)
- "Are there any project conventions the generated code should follow?" (naming, file structure, import patterns)

### 4. Dependency Confirmation
- "I've computed the build order based on component and data dependencies. Let me walk you through it for confirmation."
- Present the proposed build order and ask: "Does this order make sense? Should any pages be re-prioritized?"

## Build Order Logic

Pages are ordered into tiers based on their dependencies. Within each tier, pages are ordered by complexity (simpler first). The build order ensures that every page's dependencies are built before it.

### Tier A: Shared / Primitive Components
Build order position: 1-N (built first)
- Components with no dependencies on other app components
- Design system primitives (buttons, inputs, badges, icons)
- Utility components (loading spinners, error boundaries, empty states)
- These are referenced by the component manifest but generated as standalone units

### Tier B: Composite Components
Build order position: N+1 onward
- Components that compose primitive components
- Data display components (data tables, card lists, detail panels)
- Form components (filter bars, search inputs, multi-field forms)
- Each composite component brief references its primitive dependencies

### Tier C: Feature Components
Build order position: after Tier B
- Components implementing specific business logic
- Workflow steppers, approval panels, rich editors
- Components tied to specific domain entities or features
- These depend on composites and primitives

### Tier D: Layout / Shell Pages
Build order position: after Tier C
- App shell, navigation layout, sidebar
- Pages that establish the visual frame other pages live within
- Depend on the suite-level navigation shell spec

### Tier E: List / Index Pages
Build order position: after Tier D
- Entity list views, search results, table pages
- Simpler data-fetching patterns, establish query conventions
- These pages set patterns that detail pages build upon

### Tier F: Detail / Form Pages
Build order position: after Tier E
- Entity detail views, create/edit forms, profile pages
- More complex state management (form state, validation, mutations)
- Build on patterns established by list pages

### Tier G: Dashboard / Analytics Pages
Build order position: last
- Dashboards, reports, analytics views
- Depend on data from multiple entities being available
- Often the most complex pages with the most dependencies

## Per-Page Generation Brief Format

Each page gets its own generation brief file following this structure:

```markdown
# Generation Brief: {Page Display Name}

## Build Order
- **Position**: {N} of {M}
- **Tier**: {A-G} — {tier description}
- **Dependencies**: {list of components/pages that must be built first}
- **Blocks**: {list of components/pages that depend on this one}

## Page Context
- **App**: {app_name}
- **Archetype**: {primary archetype}
- **URL Pattern**: {route pattern from ia-spec, e.g., /apps/{app_name}/orders/:id}
- **Layout Pattern**: {pattern name from page spec, e.g., master-detail, full-width-form}
- **Target Framework**: {framework name}
- **File Path**: {suggested file path in the codebase, e.g., src/pages/orders/OrderDetail.tsx}

## Design Tokens
{Relevant subset of the design system for this page. Include only tokens actually used.}

### Colors
{Color tokens used on this page — backgrounds, text, borders, status indicators}

### Typography
{Font sizes, weights, and line heights used on this page}

### Spacing
{Spacing scale values used in the page layout}

### Breakpoints
{Responsive breakpoints that affect this page's layout}

## Data Requirements

### Entities
| Entity | Source | Fields Used | Relationship |
|--------|--------|-------------|-------------|
{Rows for each entity displayed or manipulated on this page}

### API Endpoints
| Endpoint | Method | Purpose | Request Shape | Response Shape | Caching |
|----------|--------|---------|---------------|----------------|---------|
{Rows for each API call this page makes, pulled from api-contracts.md}

### Query Parameters
{URL query parameters this page reads — filters, search terms, pagination, sort}

## Component Manifest
{Ordered list of every component on this page, from outermost to innermost.}

| # | Component | Source | Props | Notes |
|---|-----------|--------|-------|-------|
{Numbered rows — # indicates render order / nesting depth}

For each component, include:
- Full prop interface from the component contract
- Any page-specific prop values or overrides
- Whether the component is shared (from Tier A/B/C) or page-specific

## State Specification

### Server State
{Queries and mutations from state-interaction.md relevant to this page}
| Key | Type | Source Endpoint | Stale Time | Refetch Strategy |
|-----|------|----------------|------------|-----------------|
{Rows for each server state key}

### Client State
{Local UI state needed for this page}
| Key | Type | Initial Value | Purpose |
|-----|------|---------------|---------|
{Rows for each client state variable — modals, selected items, active tabs, etc.}

### Form State (if applicable)
| Field | Type | Validation Rules | Default Value |
|-------|------|-----------------|---------------|
{Rows for each form field, pulled from page spec and feature scenarios}

### Derived State
{Computed values derived from server or client state}
| Key | Derivation Logic | Dependencies |
|-----|-----------------|--------------|
{Rows for each derived value — filtered lists, computed totals, display flags}

## Interaction Flows
{Sequence of user actions, state changes, API calls, and UI updates. Each flow is a numbered sequence.}

### Flow 1: {Flow Name, e.g., "Load Page"}
1. User navigates to {route}
2. Page renders loading skeleton
3. Fetch {endpoint} with {params}
4. On success: populate {state keys}, render {components}
5. On error: render error state with retry action

### Flow 2: {Flow Name, e.g., "Submit Form"}
1. User fills {form fields}
2. Client-side validation runs on blur / submit
3. On valid: call {mutation endpoint} with {payload}
4. Optimistic update: {describe UI change before server confirms}
5. On success: {redirect / show toast / update list}
6. On error: {revert optimistic update, show error message}

{Additional flows as needed — one per major user interaction on this page}

## Authorization Rules
{Pulled from authorization.md, scoped to this page.}

### Route Guard
- **Allowed Roles**: {roles that can access this page}
- **Redirect**: {where unauthorized users are sent}

### Conditional Rendering
| Element | Condition | Visible To | Hidden From |
|---------|-----------|-----------|-------------|
{Rows for UI elements that are conditionally shown based on role or permissions}

### Data Scoping
{How data is filtered based on the current user's role and scope — e.g., "Managers see their team's records only"}

## BDD Scenarios
{Relevant scenarios from feature files that apply to this page, formatted as Given/When/Then.}

### Scenario: {Scenario Name}
- **Feature**: {source feature file}
- **Given** {precondition}
- **When** {user action}
- **Then** {expected outcome}

{Repeat for each relevant scenario}

## Acceptance Criteria
{Testable criteria derived from the BDD scenarios and page spec. These serve as the definition of done for code generation.}

- [ ] {Criterion 1 — e.g., "Page loads within 2 seconds on 3G connection"}
- [ ] {Criterion 2 — e.g., "Empty state shown when no records match filters"}
- [ ] {Criterion 3 — e.g., "Form validates email format before submission"}
- [ ] {Criterion N}
```

## Build Order Document Format

In addition to per-page briefs, generate a build order document:

```markdown
# Build Order: {App Display Name}

## Overview
- **App**: {app_name}
- **Total Pages**: {M}
- **Total Components**: {N}
- **Target Framework**: {framework}
- **Estimated Build Tiers**: {number of tiers A-G used}
- **Validation Score**: {overall score from Step 16}

## Dependency Graph
{Text-based representation of page and component dependencies}

## Build Sequence

### Tier A: Shared / Primitive Components ({count} items)
| # | Component | Contract File | Dependencies | Est. Complexity |
|---|-----------|---------------|--------------|-----------------|
{Rows ordered by build position}

### Tier B: Composite Components ({count} items)
| # | Component | Contract File | Dependencies | Est. Complexity |
|---|-----------|---------------|--------------|-----------------|

### Tier C: Feature Components ({count} items)
| # | Component | Contract File | Dependencies | Est. Complexity |
|---|-----------|---------------|--------------|-----------------|

### Tier D: Layout / Shell Pages ({count} items)
| # | Page | Brief File | Dependencies | Est. Complexity |
|---|------|------------|--------------|-----------------|

### Tier E: List / Index Pages ({count} items)
| # | Page | Brief File | Dependencies | Est. Complexity |
|---|------|------------|--------------|-----------------|

### Tier F: Detail / Form Pages ({count} items)
| # | Page | Brief File | Dependencies | Est. Complexity |
|---|------|------------|--------------|-----------------|

### Tier G: Dashboard / Analytics Pages ({count} items)
| # | Page | Brief File | Dependencies | Est. Complexity |
|---|------|------------|--------------|-----------------|

## Critical Path
{The longest dependency chain — this determines the minimum sequential build time}

## Parallel Build Opportunities
{Groups of pages/components at the same tier with no mutual dependencies that can be built concurrently}

## Generation Notes
{Any framework-specific or project-specific notes that apply across all briefs}
```

## Output Specification

### `./spec/apps/{app_name}/generation-briefs/{page_name}-brief.md`
One file per page, following the per-page generation brief format above. File names use kebab-case matching the page name (e.g., `order-detail-brief.md`, `user-list-brief.md`).

### `./spec/apps/{app_name}/generation-briefs/_build-order.md`
The build order document covering all pages and components, following the build order format above. Prefixed with underscore to sort it first in directory listings.

## Completion Checklist
- [ ] Target app selected and validation score confirmed at 75 or above
- [ ] Target framework, styling, state management, and routing preferences captured
- [ ] Build order computed based on component and page dependencies
- [ ] Build order reviewed and confirmed with the user
- [ ] `./spec/apps/{app_name}/generation-briefs/_build-order.md` created with dependency graph and sequenced tiers
- [ ] One `{page_name}-brief.md` created per page in the app
- [ ] Each brief contains all sections: context, design tokens, data, components, state, flows, auth, BDD, acceptance criteria
- [ ] Component manifests reference actual component contracts from Step 12
- [ ] API endpoints reference actual contracts from Step 14
- [ ] Authorization rules reference actual policies from Step 15
- [ ] BDD scenarios reference actual feature files from Step 9
- [ ] Acceptance criteria are testable and complete
- [ ] All briefs cross-checked against each other for consistency
