# Step 3: UI Conventions

## Tier
1 — Suite-level (runs once, establishes structural UI conventions for the entire application suite)

## Purpose
UI Conventions defines the structural and behavioural rules that all applications in the suite share — layout grid, spacing scale, responsive breakpoints, and accessibility standards. It is intentionally agnostic of visual design (colours, typography, brand) to remain compatible with any UI framework or component library the implementor chooses.

## Prerequisites
- `./spec/suite/domain-model.md` (Step 1)

## Inputs to Read
- `./spec/suite/domain-model.md` — review to understand user types and usage contexts (e.g. data-dense enterprise vs. consumer-facing)

## Interrogation Process

### 1. Layout Grid
- How many columns should the layout grid use? (typical: 12-column)
- What is the maximum content width? (e.g. 1280px, 1440px, fluid)
- What is the gutter width between columns?
- Are there standard sidebar or panel widths to establish?

### 2. Spacing Scale
- What base spacing unit should the system use? (4px or 8px)
- How dense should the default UI be? (compact for power users, relaxed for casual users)
- Are there specific spacing conventions for forms, tables, or cards?

### 3. Responsive Breakpoints
- What device categories must the suite support? (desktop only, desktop + tablet, full responsive)
- Is mobile a full experience or a reduced one?
- What are the breakpoint values? (confirm or adjust defaults: sm=640px, md=768px, lg=1024px, xl=1280px, 2xl=1536px)
- Are there mobile-specific interaction patterns? (bottom navigation, swipe gestures)

### 4. Accessibility Standards
- What WCAG conformance level is required? (A, AA, or AAA)
- Are there keyboard navigation conventions to standardise?
- What focus indicator behaviour is expected?
- Are there screen reader or ARIA conventions to establish suite-wide?

## Output Specification

### `./spec/suite/ui-conventions.md`

The output file must contain these sections:

#### Layout Grid
- **Column count**: value
- **Max content width**: value
- **Gutter width**: value
- **Sidebar/panel widths**: named widths if applicable (e.g. nav: 240px, detail panel: 360px)

#### Spacing Scale
- **Base unit**: value in px
- **Scale**: named spacing values (xs through 4xl) with computed px values
- **Density**: default density setting and rationale

#### Responsive Breakpoints
| Name | Min Width | Typical Device | Layout Notes |
|------|-----------|----------------|--------------|
| sm   | 640px     | Large phone    |              |
| md   | 768px     | Tablet         |              |
| lg   | 1024px    | Small laptop   |              |
| xl   | 1280px    | Desktop        |              |
| 2xl  | 1536px    | Wide desktop   |              |

#### Accessibility Standards
- **WCAG Level**: target conformance (A / AA / AAA)
- **Keyboard Navigation**: tab order conventions, skip links, focus trap behaviour for modals
- **Focus Indicators**: visible focus ring required; describe style if known
- **Screen Reader**: ARIA landmark conventions, live region usage
- **Reduced Motion**: behaviour when `prefers-reduced-motion` is active

## Completion Checklist
- [ ] `./spec/suite/ui-conventions.md` created
- [ ] Layout grid defined with column count and max width
- [ ] Spacing scale defined with base unit
- [ ] Responsive breakpoints specified
- [ ] Accessibility standards documented with WCAG level
