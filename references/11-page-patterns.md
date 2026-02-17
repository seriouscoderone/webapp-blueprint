# Step 11: Page Pattern Specifications

## Tier
3 — Per-app specification (runs for each app; produces one spec file per page)

## Purpose
Page Pattern Specifications translate the information architecture into concrete page-level designs. Each page is assigned a layout pattern, its data requirements are defined, user actions are enumerated, and all state variations (loading, empty, error, populated) are documented. These specs serve as the direct input for component inventory and implementation.

## Prerequisites
- `./spec/apps/{app_name}/ia-spec.md` — information architecture must be complete
- `./spec/apps/{app_name}/features/*.feature.md` — BDD features must exist
- `./spec/apps/{app_name}/archetype.md` — app archetype for design context

## Inputs to Read
- `./spec/apps/{app_name}/ia-spec.md`
- `./spec/apps/{app_name}/features/*.feature.md`
- `./spec/apps/{app_name}/archetype.md`
- `./spec/apps/{app_name}/domain-refinement.md`
- `./spec/apps/{app_name}/role-refinement.md`
- `./spec/suite/design-system.md` (for available design primitives)

## Layout Pattern Catalog

Use this catalog to classify each page. Present these options to the user and ask which pattern best fits each page.

### 1. List + Detail
A table or list of items with the ability to navigate to a detail view (separate page).
- **Use when**: The detail view is complex enough to warrant its own page.
- **Typical structure**: Filter bar + data table/list + pagination. Clicking a row navigates to detail.
- **Examples**: Order list, user directory, project list.

### 2. Master-Detail (Split View)
A list panel and a detail panel displayed side by side.
- **Use when**: Users frequently switch between items and need quick context switching.
- **Typical structure**: Left panel with scrollable list, right panel with detail. Detail updates without full navigation.
- **Examples**: Email inbox, chat interface, file browser.

### 3. Form Page
A single-purpose page for creating or editing an entity.
- **Use when**: The form is the primary interaction on the page.
- **Typical structure**: Form header, grouped form fields, action buttons (save, cancel). May be single-step or multi-step.
- **Examples**: Create project form, edit profile, registration.

### 4. Dashboard
A grid of widgets displaying aggregated data, charts, and KPIs.
- **Use when**: Users need an at-a-glance overview of system state.
- **Typical structure**: Grid layout with cards, charts, stat counters, and recent activity. Widgets may be configurable.
- **Examples**: Admin dashboard, analytics overview, home page.

### 5. Detail View
A single-entity page showing comprehensive information organized in sections or tabs.
- **Use when**: An entity has enough data and actions to fill a full page.
- **Typical structure**: Header with entity summary and actions, content organized into tabs or sections.
- **Examples**: Project detail, customer profile, order detail.

### 6. Wizard / Stepper
A multi-step guided process with progress indication.
- **Use when**: The task is complex and benefits from being broken into sequential steps.
- **Typical structure**: Step indicator, one step visible at a time, back/next/submit controls, summary step at the end.
- **Examples**: Onboarding wizard, multi-step checkout, report builder.

### 7. Empty State
The appearance of a page when there is no data yet. Not a standalone pattern but a required variation for every page that displays data.
- **Use when**: First-time use or no results match filters.
- **Typical structure**: Illustration or icon, explanatory text, call-to-action button.

### 8. Settings Page
Grouped configuration options with save/cancel semantics.
- **Use when**: Users need to configure preferences or system settings.
- **Typical structure**: Vertical navigation or tabs for setting groups, form controls, save/cancel per group or globally.
- **Examples**: Account settings, notification preferences, workspace configuration.

## Interrogation Process

### 1. Page-by-Page Pattern Assignment
For each page in the site map:

- Which layout pattern best describes this page? (Show the catalog above.)
- Does this page combine patterns? (e.g., a dashboard with an embedded list)
- What is the primary user goal on this page?

### 2. Data Requirements
For each page:

- What entities/data does this page display?
- What API calls are needed to populate this page?
- Is any data real-time (needs WebSocket/SSE updates)?
- How much data is typical? (e.g., 10 items vs. 10,000 items)
- Are there computed or derived values shown on this page?

### 3. User Actions
For each page:

- What are the primary actions a user can take? (e.g., create, edit, delete, export)
- Are there bulk actions (select multiple items, then act)?
- Which actions are always visible vs. shown in a menu or on hover?
- Are there keyboard shortcuts for common actions?
- Do any actions require confirmation (destructive actions)?

### 4. Responsive Behavior
For each page:

- How should this page adapt to mobile viewports? (Stack columns, hide sidebar, simplify layout)
- Are there breakpoints where the layout changes significantly?
- Should any functionality be hidden or deferred on mobile?
- Is touch-specific behavior needed (swipe actions, pull-to-refresh)?

### 5. State Variations
For each page:

- **Loading**: What does the page look like while data loads? (Skeleton, spinner, progressive loading)
- **Empty**: What does the page look like with no data? (Illustration + CTA, or placeholder text)
- **Error**: What does the page look like if data fails to load? (Error message, retry button)
- **Populated**: The normal state with data.
- **Partial**: Are there cases where some data loads but other sections fail?

### 6. Role-Based Variations
For each page:

- Does the page look different for different roles?
- Are certain sections, actions, or data fields hidden based on role?
- Does the page redirect if the user lacks access?

## Output Specification

### `./spec/apps/{app_name}/pages/{page_name}.md`

One file per page. Each file must contain:

#### Page Identity
- **Page Name**: Human-readable name
- **URL**: Route pattern from ia-spec.md
- **Layout Pattern**: Which pattern from the catalog (or combination)
- **Primary User Goal**: One sentence describing why a user visits this page

#### Data Requirements
A table:
| Data Source | Entity/Endpoint | Fields Used | Real-Time | Pagination |
|---|---|---|---|---|
| API call | GET /projects | name, status, owner, updatedAt | No | Yes, 25/page |

#### Layout Specification
- **Desktop Layout**: Description of zones (header, sidebar, main, footer) with content in each
- **Tablet Layout**: Changes from desktop
- **Mobile Layout**: Changes from tablet
- Optionally include an ASCII wireframe or description of the spatial arrangement

#### User Actions
A table:
| Action | Trigger | Location | Confirmation | Permission |
|---|---|---|---|---|
| Create Project | Button click | Top-right header | No | role:admin, role:manager |
| Delete Project | Menu item | Row action menu | Yes — modal | role:admin |
| Export CSV | Button click | Toolbar | No | role:any |

#### State Variations
For each state (loading, empty, error, populated):
- What is displayed
- What user actions are available (if any)
- Any transition behavior (e.g., skeleton fades into content)

#### Role Variations
A description or table showing what changes per role:
| Element | Admin | Manager | Viewer |
|---|---|---|---|
| Create button | Visible | Visible | Hidden |
| Delete action | Visible | Hidden | Hidden |
| Financial data column | Visible | Visible | Hidden |

#### Connected Pages
- **Navigates From**: Which pages link to this page and how
- **Navigates To**: Which pages this page links to and what triggers navigation
- **Breadcrumb Trail**: The breadcrumb path for this page

## Completion Checklist
- [ ] One `.md` file created per page in `./spec/apps/{app_name}/pages/`
- [ ] Every page in the site map has a corresponding page spec
- [ ] Every page has a layout pattern assigned
- [ ] Data requirements are specified with endpoints and fields
- [ ] All four state variations (loading, empty, error, populated) are defined
- [ ] Role variations are documented for pages with role-dependent content
- [ ] Responsive behavior is described for at least desktop and mobile
- [ ] Connected pages (navigation in/out) are documented
