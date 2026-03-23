# Step 10: Information Architecture

## Tier
3 — Per-app specification (runs for each app; defines the structural blueprint for content and navigation)

## Purpose
Information Architecture defines how the app's content is organized, how pages relate to each other, and how users navigate through the application. It bridges the gap between abstract features and concrete page-level specifications by establishing the page hierarchy, URL schema, navigation model, and content zones that all subsequent page and component specs will reference.

## Prerequisites
- `./spec/apps/{app_name}/archetype.md` — app archetype must be defined
- `./spec/apps/{app_name}/domain-refinement.md` — app-level domain model must exist
- `./spec/apps/{app_name}/features/*.feature.md` — BDD feature specs must be complete

## Inputs to Read
- `./spec/apps/{app_name}/archetype.md`
- `./spec/apps/{app_name}/domain-refinement.md`
- `./spec/apps/{app_name}/role-refinement.md`
- `./spec/apps/{app_name}/features/*.feature.md` (all feature files)
- `./spec/suite/navigation-shell.md` (for suite-level nav context)

## Interrogation Process

### 1. Page Inventory
Derive the list of pages from features and ask:

- Based on the features defined, here is a proposed list of pages. Does this look right? Are any missing?
- Are there pages that are not tied to a specific feature (e.g., settings, profile, help)?
- Which page is the landing/home page for this app?
- Are there pages that should only be visible to certain roles?
- Are there any full-screen modal or overlay pages (e.g., onboarding wizard, media viewer)?

### 2. Page Hierarchy & Grouping
Establish structure:

- How should pages be grouped? By entity type? By workflow phase? By user goal?
- Is there a natural hierarchy (e.g., Projects > Project Detail > Task Detail)?
- What is the maximum depth of nesting the user is comfortable with?
- Are there pages that serve as "hubs" linking to multiple sub-pages?
- Should any pages be treated as tabs within a parent page rather than standalone pages?

### 3. URL Structure
Define the routing schema:

- Do you prefer descriptive URLs (e.g., `/projects/acme-corp/tasks/42`) or ID-based (e.g., `/projects/123/tasks/42`)?
- Should entity names or slugs appear in URLs?
- Are there URL parameters needed for filtering or view state (e.g., `/orders?status=pending`)?
- Do any routes need to support deep linking (sharing a URL that restores exact state)?
- Are there routes that should redirect based on role (e.g., admin vs. regular user)?

### 4. Navigation Model
Define how users move between pages:

- What items belong in the primary navigation (always visible sidebar or top nav)?
- Is there a secondary navigation level (e.g., tabs within a section)?
- Are there contextual navigation elements (breadcrumbs, back buttons, related links)?
- How does the user return to the previous page — browser back, breadcrumb, or explicit button?
- Are there quick-access elements like a global search, recent items, or favorites?
- Should the navigation reflect the user's role (hide items they cannot access)?

### 5. Content Zones
Define the layout regions:

- Does the app use a consistent layout shell (sidebar + main content, or top nav + main)?
- Which pages need a sidebar? What goes in it (navigation, filters, context panel)?
- Do any pages need a secondary header or toolbar area?
- Are there pages with a split layout (side-by-side panels)?
- Is there a footer with persistent information or actions?

### 6. Information Density
Calibrate density preferences:

- Should list views default to compact (many rows, minimal spacing) or spacious (fewer rows, more whitespace)?
- Should detail views prioritize showing all information at once or organize into tabs/accordions?
- Are there contexts where data density matters most (e.g., dashboards should be dense, forms should be spacious)?
- What is the expected amount of data in typical list views (10s, 100s, 1000s of items)?

### 7. Search & Filter Architecture
Define search and discovery:

- Is there a global search across all entities, or per-section search?
- What entities are searchable? Which fields should be searched?
- What are the standard filter dimensions for each list view?
- Should filters be visible by default or collapsible?
- Do any views need saved/preset filter combinations?
- Is there a need for advanced search (boolean operators, field-specific queries)?

## Output Specification

### `./spec/apps/{app_name}/ia-spec.md`

The output file must contain these sections:

#### Site Map
A hierarchical representation of all pages using indented list format:
```
- Dashboard (/)
- Projects (/projects)
  - Project Detail (/projects/:id)
    - Task Board (/projects/:id/tasks)
    - Settings (/projects/:id/settings)
- Reports (/reports)
  - Custom Report (/reports/custom)
```
Include the page name and its URL path.

#### URL Schema
A table defining route patterns:
| Route Pattern | Page | Parameters | Auth Required | Notes |
|---|---|---|---|---|
| `/` | Dashboard | — | Yes | Redirects based on role |
| `/projects/:projectId` | Project Detail | projectId: UUID | Yes | — |
| `/projects/:projectId/tasks?status=:status` | Task Board | projectId, status | Yes | status is optional filter |

#### Navigation Model
- **Primary Navigation**: Items always visible in the main nav. Table: label, icon, route, badge (if any), role visibility.
- **Secondary Navigation**: Sub-navigation within sections (e.g., tabs on a detail page). Describe per parent page.
- **Contextual Navigation**: Breadcrumbs pattern, back navigation, related links.
- **Quick Access**: Global search behavior, recent items, favorites, keyboard shortcuts.

#### Content Zones
For each distinct layout template used in the app:
- **Template Name** (e.g., "Standard Layout", "Detail Layout", "Full-Width Layout")
- **Zones**: Diagram or description of header, sidebar, main, footer regions
- **Which pages use this template**
- **Responsive behavior**: How zones collapse or reorder on smaller screens

#### Information Density
- **Default density setting**: Compact, comfortable, or spacious
- **Per-context overrides**: Which views use a different density and why
- **Pagination or virtualization**: Strategy for long lists (paginated, infinite scroll, virtual scroll)
- **Data limits**: Maximum items per page, truncation rules

#### Search & Filter Architecture
- **Global search**: Scope, searchable entities, results format
- **Per-list filters**: For each major list view, the available filter dimensions
- **Filter persistence**: Whether filters are remembered across sessions
- **Saved views**: Whether users can save filter/sort combinations

## Completion Checklist
- [ ] `./spec/apps/{app_name}/ia-spec.md` created
- [ ] Site map includes every page derived from feature specs
- [ ] URL schema covers all routes with parameter definitions
- [ ] Navigation model defines primary, secondary, and contextual navigation
- [ ] Content zones are defined with responsive behavior
- [ ] Information density preferences are documented
- [ ] Search and filter architecture is specified for all list views
