# Step 4: Navigation & App Shell

## Tier
1 — Suite-level (runs once, establishes the shared navigation structure and app shell for the entire suite)

## Purpose
The Navigation & App Shell step defines the persistent UI frame that wraps every application in the suite. It covers the shell layout, primary navigation structure, global actions, and how navigation adapts by role and device. This ensures users experience consistent wayfinding regardless of which app they are in.

## Prerequisites
- `./spec/suite/domain-model.md` (Step 1 — needed to understand what content areas exist)
- `./spec/suite/role-permission-matrix.md` (Step 2 — needed to determine role-based nav visibility)
- `./spec/suite/design-system.md` (Step 3 — needed for layout conventions, breakpoints, and component styles)

## Inputs to Read
- `./spec/suite/domain-model.md` — review entities and workflows to identify top-level navigation areas
- `./spec/suite/role-permission-matrix.md` — review roles and data visibility to determine which nav items each role sees
- `./spec/suite/design-system.md` — review responsive breakpoints, spacing system, and component style preferences

## Interrogation Process

### 1. Shell Layout Pattern
Determine the overall page structure:

- What shell layout pattern fits best? Options:
  - **Sidebar + top bar**: Fixed sidebar for primary nav, top bar for global actions (common in enterprise dashboards)
  - **Top nav only**: Horizontal navigation bar, content below (common in marketing/consumer apps)
  - **Hybrid**: Collapsible sidebar with a top bar
- Should the sidebar (if used) be persistent, collapsible, or auto-hiding?
- What is the default sidebar width? (e.g., expanded=240px, collapsed=64px icon-only)
- Is there a secondary sidebar or detail panel pattern? (e.g., a right-side inspector panel)

### 2. Primary Navigation Structure
Define the main navigation items:

- What are the top-level navigation sections? (derive from domain model entities and workflows)
- How should nav items be grouped? (e.g., by workflow stage, by entity type, by user goal)
- What is the ordering principle? (most-used first, workflow order, alphabetical)
- Does each nav item need an icon? If so, describe the icon concept for each item.
- Are there nested/sub-navigation items? How deep does nesting go? (recommend max 2 levels)
- Should nav items show counts or badges? (e.g., "Orders (12)", "Alerts" with a red dot)

### 3. Multi-App Navigation
If the suite contains multiple apps:

- Is there an app switcher? Where does it live? (top-left, top bar dropdown, sidebar header)
- Do all apps share the same shell, or does each app have a distinct shell variation?
- Is there a home/dashboard that spans apps?
- How does the user know which app they are currently in? (visual indicator, color accent, breadcrumb)

### 4. Global Actions & Utilities
Define persistent actions available from any screen:

- **Search**: Is there a global search? Where is it placed? Does it search across apps or within the current app?
- **Notifications**: Is there a notification center? Bell icon with dropdown? Real-time or polling? What events generate notifications?
- **User Menu**: What items appear in the user/profile menu? (profile, settings, preferences, logout, switch org/tenant)
- **Help**: Is there contextual help? A help center link? An in-app chat widget?
- **Quick Actions**: Are there create/action buttons that persist globally? (e.g., "+ New" button)
- **Theme Toggle**: Is dark/light mode switching available to users?

### 5. Breadcrumbs & Wayfinding
Define how users understand where they are:

- Should the app use breadcrumbs? If so, what is the format? (e.g., "Home > Projects > Project Alpha > Tasks")
- Are breadcrumbs clickable for navigation?
- Is there a page title area? Does it include actions (e.g., "Edit" button next to the title)?
- How are nested views handled? (e.g., detail views replace the page, open in a modal, or open in a side panel)

### 6. Mobile Navigation
Define how navigation adapts on small screens:

- What is the mobile navigation pattern?
  - **Bottom tab bar**: persistent tabs at the bottom (max 5 items)
  - **Hamburger menu**: slide-out drawer from the left
  - **Combination**: bottom tabs for primary, hamburger for secondary
- Which nav items appear in the mobile primary navigation vs. the overflow menu?
- Are there mobile-specific gestures? (swipe to go back, pull down to refresh)

### 7. Role-Based Visibility
Define what each role sees in the navigation:

- For each navigation item: Which roles see it? (derive from the permission matrix)
- When a user lacks access to a nav item, is it hidden entirely or shown as disabled/locked?
- Are there nav items that appear only conditionally? (e.g., "Admin" section appears only for admins)
- Does the nav order or grouping change per role?

### 8. Loading & Transition States
Define how the shell behaves during loading:

- What is the loading strategy when navigating between sections? (full page reload, skeleton screen, spinner, content shimmer)
- Is there a global progress indicator? (top bar progress line, e.g., NProgress style)
- How are errors handled in the shell? (inline error, toast notification, error page)
- Is there an offline state? What does the shell show when connectivity is lost?

## Output Specification

### `./spec/suite/navigation-shell.md`

The output file must contain these sections:

#### Shell Layout
- **Pattern**: chosen layout pattern with rationale
- **Sidebar** (if applicable): width, collapse behavior, pinning
- **Top Bar**: height, contents, fixed vs. scrolling
- **Content Area**: max width, padding, scroll behavior
- ASCII or text-based wireframe sketch of the layout

#### Primary Navigation
A markdown table with columns:
| Order | Label | Icon | Route/Path | Group | Badge/Count |
Include grouping separators where applicable.

#### App Switcher
- **Mechanism**: dropdown, grid, sidebar section
- **Current App Indicator**: how the active app is highlighted
- **App List**: name, icon, description for each app in the suite

#### Global Actions
For each global action:
- **Placement**: where in the shell it lives
- **Behavior**: what happens on interaction (dropdown, modal, navigation, panel)
- **Content**: what the action reveals or triggers

#### Breadcrumb Strategy
- **Format**: template pattern (e.g., `App > Section > Entity > Detail`)
- **Depth**: maximum breadcrumb depth
- **Behavior**: clickable, truncation rules for long paths
- **Mobile**: whether breadcrumbs appear on mobile

#### Mobile Navigation
- **Pattern**: chosen mobile nav pattern
- **Primary Items**: which items appear in the persistent mobile nav (max 5)
- **Overflow**: where remaining items go
- **Transitions**: how mobile navigation animates

#### Role-Based Nav Visibility
A markdown table with columns:
| Nav Item | Admin | Manager | Member | Viewer | Notes |
Use checkmarks or dashes to indicate visibility.

#### Loading & Transition States
- **Page Transition**: strategy and animation
- **Global Indicator**: progress bar style
- **Error Handling**: shell-level error display approach
- **Offline State**: behavior description

## Completion Checklist
- [ ] `./spec/suite/navigation-shell.md` created
- [ ] Shell layout pattern selected with wireframe sketch
- [ ] All primary navigation items defined with icons and routes
- [ ] Global actions (search, notifications, user menu) specified
- [ ] Mobile navigation pattern defined with primary items selected
- [ ] Role-based visibility mapped for every nav item
- [ ] Loading and error states documented
