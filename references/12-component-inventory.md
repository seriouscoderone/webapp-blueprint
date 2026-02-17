# Step 12: Component Inventory

## Tier
3 — Per-app specification (runs for each app; catalogs and specifies all UI components)

## Purpose
The Component Inventory extracts every UI component referenced across all page specs, deduplicates them, classifies them by complexity level, and defines a complete contract for each. This produces a shared component vocabulary that ensures consistency across pages, enables parallel development, and feeds directly into the design system and implementation plan.

## Prerequisites
- `./spec/apps/{app_name}/pages/*.md` — all page specs must be complete
- `./spec/suite/design-system.md` — suite-wide design system for base primitives

## Inputs to Read
- `./spec/apps/{app_name}/pages/*.md` (all page specs)
- `./spec/suite/design-system.md`
- `./spec/apps/{app_name}/archetype.md` (for design context)
- `./spec/apps/{app_name}/domain-refinement.md` (for entity-specific components)
- `./spec/apps/{app_name}/role-refinement.md` (for permission-aware components)

## Component Classification

Components are classified into three tiers based on complexity and specificity:

### Primitive
Atomic, highly reusable elements with no domain knowledge. These typically come from or extend the design system.
- Examples: Button, Input, Textarea, Select, Checkbox, Radio, Badge, Avatar, Icon, Tooltip, Spinner, Divider
- **Characteristics**: No business logic, fully controlled via props, no API calls, no internal state beyond UI state

### Composite
Combinations of primitives that form reusable UI patterns. May have light interaction logic but remain domain-agnostic.
- Examples: SearchBar (Input + Button + Icon), DataTable (Table + Pagination + SortHeaders), FormField (Label + Input + ErrorMessage), Card (Container + Header + Body + Footer), Modal (Overlay + Container + Header + Actions), Tabs (TabList + TabPanel)
- **Characteristics**: Composed of primitives, may manage internal UI state (open/closed, selected tab), still no domain-specific knowledge

### Feature
Domain-specific components tied to a particular entity or workflow. These are unique to the application.
- Examples: UserProfileCard, OrderTimeline, InvoiceLineItemEditor, ApprovalWorkflowStepper, ProjectStatusBadge, NotificationFeed
- **Characteristics**: Contain domain logic, may fetch their own data, are tied to specific entities, may enforce business rules in the UI

## Interrogation Process

### 1. Component Extraction
Walk through each page spec and extract components:

- Looking at page {page_name}, I see these likely components: {list}. Does this match your expectation?
- Are there components on this page that should be shared with other pages?
- Are there components that look similar across pages but have slight differences — should they be unified or kept separate?

### 2. Deduplication & Naming
After extracting from all pages:

- Here is the consolidated component list with {N} components. I have merged duplicates. Does this look right?
- Are there components with overlapping purposes that should be combined?
- Do the component names clearly convey their purpose? Any naming preferences?

### 3. Classification Review
Present the classified list:

- I have classified components into Primitive ({N}), Composite ({N}), and Feature ({N}) categories. Does this classification seem right?
- Should any Composite components be promoted to Feature (they need domain knowledge)?
- Are there Primitives that the design system already provides and do not need a custom spec?

### 4. Per-Component Contract
For each Feature and Composite component, ask:

#### Props & Configuration
- What data does this component receive from its parent?
- Which props are required vs. optional? What are the defaults for optional props?
- Are there variant props (size, color scheme, style)?

#### States & Interactions
- What are the visual states (default, hover, active, focus, disabled, loading, error)?
- Does the component have an expanded/collapsed state?
- Does the component manage any internal state, or is it fully controlled by its parent?

#### Events & Communication
- What events does this component emit to its parent? (e.g., onChange, onSubmit, onSelect, onDelete)
- What is the payload of each event?
- Does the component need to communicate with sibling components?

#### Slots & Composition
- Does this component accept child content or named slots?
- Can its internal structure be customized by the consumer?

#### Accessibility
- What ARIA role does this component use?
- What keyboard interactions must it support?
- What does a screen reader announce for this component?
- Are there contrast or motion considerations?

### 5. Shared Component Identification
After specifying all components:

- Are there components used across multiple apps in the suite that should be promoted to the suite design system?
- Are there third-party component library components that can be used instead of building custom?

## Output Specification

### `./spec/apps/{app_name}/components/{component_name}.md`

One file per Feature and Composite component. Primitives are documented in a single summary table unless they require custom behavior beyond the design system.

Each component file must contain:

#### Component Identity
- **Name**: PascalCase component name
- **Classification**: Primitive | Composite | Feature
- **Description**: One sentence explaining what this component does
- **Used In**: List of pages where this component appears

#### Props Interface
A table defining the component's API:
| Prop | Type | Required | Default | Description |
|---|---|---|---|---|
| `title` | `string` | Yes | — | The card's heading text |
| `size` | `'sm' \| 'md' \| 'lg'` | No | `'md'` | Controls overall dimensions |
| `onClose` | `() => void` | No | — | Called when the close button is clicked |
| `isLoading` | `boolean` | No | `false` | Shows a loading skeleton when true |
| `items` | `Item[]` | Yes | — | Array of items to display |

#### Visual Variants
Describe the visual variations:
- **Size variants**: sm, md, lg — describe the differences
- **Color / style variants**: primary, secondary, danger, ghost — when to use each
- **Density variants**: compact, comfortable — if applicable

#### States
Define every visual state the component can be in:
| State | Description | Visual Treatment |
|---|---|---|
| Default | Normal resting state | Standard styling |
| Hover | Mouse is over the component | Subtle background change, cursor pointer |
| Active | Being clicked/pressed | Slight scale-down or color darken |
| Focus | Keyboard-focused | Focus ring, high-contrast outline |
| Disabled | Cannot be interacted with | Reduced opacity, no pointer events |
| Loading | Data is being fetched | Skeleton placeholder or spinner overlay |
| Error | Something went wrong | Red border or inline error message |

#### Events
A table of events the component emits:
| Event | Payload | Description |
|---|---|---|
| `onChange` | `{ value: string }` | Fired when the input value changes |
| `onSelect` | `{ item: Item }` | Fired when an item is selected from the list |
| `onDelete` | `{ id: string }` | Fired when the delete action is confirmed |

#### Slots / Children
Describe how the component accepts nested content:
- **Default slot**: What goes inside the component by default
- **Named slots**: Header, footer, actions, icon — describe each
- **Render props**: If the component delegates rendering to the consumer

#### Accessibility
- **ARIA Role**: The semantic role (e.g., `role="dialog"`, `role="listbox"`)
- **Keyboard Behavior**: Tab order, arrow key navigation, Enter/Space to activate, Escape to close
- **Screen Reader Text**: What is announced, including state changes
- **Focus Management**: Where focus moves on open/close/navigation

#### Usage Examples
Brief description of how this component is used in context:
- "In the Project List page, this component renders each project row with name, status badge, owner avatar, and action menu."
- "In the Dashboard, this component displays the KPI value with trend arrow and sparkline chart."

## Primitives Summary

If there are Primitives that extend the design system, include a summary file:

### `./spec/apps/{app_name}/components/_primitives.md`

A single file with a table:
| Component | Extends Design System | Custom Behavior | Used In |
|---|---|---|---|
| Button | Yes | Added "danger" variant | All pages |
| Badge | Yes | Added "expired" status color | Orders list, Order detail |
| Avatar | Yes | None — use as-is | User list, Profile |

## Completion Checklist
- [ ] All components extracted from page specs
- [ ] Duplicates merged and naming finalized
- [ ] Components classified as Primitive, Composite, or Feature
- [ ] One `.md` file created per Feature/Composite component in `./spec/apps/{app_name}/components/`
- [ ] Every component file includes: props interface, visual variants, states, events, accessibility
- [ ] Primitives summary table created if custom primitives exist
- [ ] Cross-page component reuse is documented in "Used In" fields
- [ ] Suite-level shared component candidates are identified
