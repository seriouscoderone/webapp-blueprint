# Step 6: App Archetype Classification

## Tier
2 — Per-app specification (run once per app in the suite)

## Purpose
This is the gateway step for Tier 2. The user declares a new app within the suite, selects one or more archetypes that describe its behavior, and establishes the app-level context that every subsequent Tier 2 step will build on. The archetype carries default assumptions about page patterns, component needs, state complexity, and API style, giving later steps a strong starting point.

## Prerequisites
- `./spec/suite/domain-model.md` (Step 1)
- `./spec/suite/role-permission-matrix.md` (Step 2)
- `./spec/suite/design-system.md` (Step 3)
- `./spec/suite/navigation-shell.md` (Step 4)
- `./spec/suite/api-event-contracts.md` (Step 5)

All five Tier 1 files must exist before any Tier 2 work begins.

## Inputs to Read
- `./spec/suite/domain-model.md` — to understand which entities this app might own
- `./spec/suite/role-permission-matrix.md` — to identify which roles will use this app
- `./spec/suite/navigation-shell.md` — to see where this app sits in the suite navigation
- `./spec/suite/api-event-contracts.md` — to understand available integration points

## App Selection Process
Before any interrogation, determine which app the user is working on:
1. List any existing apps found in `./spec/apps/` subdirectories.
2. Ask: "Which app are you specifying? Choose an existing one or name a new app."
3. Use the app name (lowercase, kebab-case) as `{app_name}` for all output paths.
4. If the app directory already exists and `archetype.md` is present, confirm whether the user wants to revise it or start fresh.

## Archetype Reference Table

Use this table when discussing archetypes with the user. Present the options clearly and help them identify which archetype(s) best fit their app.

### 1. CRUD Manager
| Aspect | Default |
|---|---|
| **Description** | Entity-centric data management — users create, read, update, and delete records |
| **Typical Page Patterns** | List page with filters/sort/search, detail/view page, create/edit form, bulk operations page |
| **Typical Components** | Data table, filter bar, form fields, detail card, inline editing, bulk action toolbar |
| **State Complexity** | Low-medium — mainly server state with form state for editing |
| **Typical API Pattern** | RESTful CRUD endpoints, pagination, filtering, sorting query params |

### 2. Dashboard / Analytics
| Aspect | Default |
|---|---|
| **Description** | Read-heavy data visualization — KPIs, charts, reports, and drill-down analysis |
| **Typical Page Patterns** | Overview dashboard, drill-down detail, report builder, comparison view, export page |
| **Typical Components** | KPI cards, chart widgets (bar, line, pie, area), date range picker, filter panel, data table, export controls |
| **State Complexity** | Medium — filter/date state, cached aggregations, real-time or polling updates |
| **Typical API Pattern** | Aggregation endpoints, time-series queries, report generation, WebSocket for live data |

### 3. Workflow Engine
| Aspect | Default |
|---|---|
| **Description** | Multi-step processes with state machines, approvals, routing, and audit trails |
| **Typical Page Patterns** | Inbox/queue, process detail with timeline, step form/wizard, approval dialog, history/audit log |
| **Typical Components** | Status badges, progress stepper, timeline, approval buttons, comment thread, assignment picker, deadline indicators |
| **State Complexity** | High — state machines, optimistic transitions, real-time status updates, conflict resolution |
| **Typical API Pattern** | Command-based (transition, approve, reject), event-sourced history, webhook notifications |

### 4. Content Platform
| Aspect | Default |
|---|---|
| **Description** | Rich content creation, editing, versioning, and publishing workflows |
| **Typical Page Patterns** | Content list/library, editor view, preview, version history, publishing queue, media manager |
| **Typical Components** | Rich text editor, media uploader, version diff viewer, publish controls, tag/category picker, content card |
| **State Complexity** | High — autosave, version tracking, collaborative editing, draft/published state |
| **Typical API Pattern** | CRUD with versioning, presigned upload URLs, publish/unpublish commands, search/filter |

### 5. Communication Hub
| Aspect | Default |
|---|---|
| **Description** | Messaging, notifications, real-time updates, and user-to-user interaction |
| **Typical Page Patterns** | Conversation list, message thread, compose view, notification center, contact/directory, settings |
| **Typical Components** | Message bubble, conversation list item, compose box, notification badge, presence indicator, typing indicator, attachment preview |
| **State Complexity** | High — real-time WebSocket state, optimistic sends, read receipts, presence management |
| **Typical API Pattern** | WebSocket for real-time, REST for history, push notifications, pagination for message history |

### 6. Configuration / Admin
| Aspect | Default |
|---|---|
| **Description** | System settings, user/team management, integrations, and platform administration |
| **Typical Page Patterns** | Settings categories, settings form, user management table, integration marketplace, audit log, billing page |
| **Typical Components** | Settings form, toggle switches, user invitation form, role selector, integration card, API key manager, usage meter |
| **State Complexity** | Low — mostly form state, minimal real-time needs |
| **Typical API Pattern** | RESTful settings CRUD, user management endpoints, integration OAuth flows, audit log queries |

## Interrogation Process

### App Identity
- "What is the name of this app?" (use for `{app_name}`, convert to kebab-case)
- "In one or two sentences, what does this app do?"
- "What is the primary purpose — what problem does it solve for users?"

### Archetype Selection
Present the six archetypes with brief descriptions (use the reference table above).
- "Which archetype best describes this app?"
- "Does it have a secondary archetype? For example, a CRUD Manager that also has a Dashboard view, or a Workflow Engine with a Configuration section."
- If hybrid: "Which archetype is primary (drives the core experience) and which is secondary (supplements it)?"

### Target Users
Reference the roles from `role-permission-matrix.md`:
- "Which of the suite's roles will use this app?" (list the global roles)
- "Is there a primary role — the user who spends the most time in this app?"
- "Are any roles restricted to read-only access in this app?"

### Differentiation
If other apps already exist in the suite:
- "How does this app differ from [existing app names]?"
- "Are there any entities or features that might overlap with another app? How should ownership be divided?"

### Archetype Defaults Review
After selecting archetype(s), present the default page patterns, components, and API style from the reference table.
- "Here are the defaults for [archetype]. Do any of these not apply to your app?"
- "Are there additional patterns or components you already know you'll need beyond these defaults?"

### Tech Stack Declaration
Ask the following questions to lock in the implementation technology. This declaration is stored in `archetype.md` and read by Steps 3, 11, 12, and 17 to produce framework-appropriate output.

- **Language**: TypeScript or JavaScript?
- **Framework**: React / Vue / Angular / SvelteKit / Next.js / Nuxt / other (specify)
- **Styling**: Tailwind CSS / CSS Modules / Styled Components / Material UI / Shadcn/ui / Chakra UI / other (specify)
- **State management**: TanStack Query + Context / Zustand / Redux Toolkit / Jotai / Pinia / other (specify)
- **Routing**: Next.js App Router / React Router / TanStack Router / Vue Router / other (specify)
- **Test runner**: Vitest (unit) + Playwright (E2E) / Jest (unit) + Cypress (E2E) / other (specify)
- **Package manager**: npm / yarn / pnpm / bun

If the user is unsure about any choice, offer the most common option for their framework as a default (e.g., Next.js App Router for Next.js, TanStack Query for React, Vitest + Playwright for Vite-based stacks).

### Success Criteria
- "What does success look like for this app? What are 2-3 key outcomes users should achieve?"

## Output Specification

### `./spec/apps/{app_name}/archetype.md`

```markdown
# {App Display Name} — Archetype

## App Identity
- **Name**: {display name}
- **Slug**: {app_name} (kebab-case)
- **Description**: {1-2 sentence description}
- **Primary Purpose**: {what problem it solves}

## Selected Archetype(s)
- **Primary**: {archetype name} — {why it fits}
- **Secondary**: {archetype name, if hybrid} — {why it supplements the primary}

## Archetype Defaults Applied
### Page Patterns
{List of page patterns inherited from the selected archetype(s), noting which are confirmed vs. tentative}

### Component Patterns
{List of component types inherited from the archetype(s)}

### State Complexity
{Expected state management approach based on archetype}

### API Style
{Expected API patterns based on archetype}

## Target User Roles
| Role | Access Level | Primary? | Notes |
|------|-------------|----------|-------|
{One row per role that uses this app}

## App-Specific Goals
1. {Goal 1 — measurable outcome}
2. {Goal 2}
3. {Goal 3}

## Tech Stack
- **Language**: {TypeScript / JavaScript}
- **Framework**: {framework name and version if known}
- **Styling**: {styling approach}
- **State Management**: {state management library/approach}
- **Routing**: {routing library/approach}
- **Test Runner**: {unit test runner} (unit) + {E2E test runner} (E2E)
- **Package Manager**: {npm / yarn / pnpm / bun}

## Overrides & Customizations
{Any archetype defaults the user wants to change, add, or remove}

## Relationship to Other Apps
{How this app relates to other apps in the suite — shared entities, navigation links, cross-app workflows}
```

## Completion Checklist
- [ ] App name established and directory created at `./spec/apps/{app_name}/`
- [ ] Primary archetype selected with rationale
- [ ] Secondary archetype identified (if hybrid) or explicitly marked as single-archetype
- [ ] Archetype defaults reviewed and customized
- [ ] Target user roles identified from global role list
- [ ] App-specific goals defined (at least 2)
- [ ] Relationship to other suite apps documented (if other apps exist)
- [ ] Tech stack declared: language, framework, styling, state management, routing, test runner, package manager
- [ ] Output file written to `./spec/apps/{app_name}/archetype.md`
