# Step 3: Design System Foundation

## Tier
1 — Suite-level (runs once, establishes visual language for the entire application suite)

## Purpose
The Design System Foundation defines the visual identity and component styling conventions for all applications in the suite. It ensures consistency across apps by establishing a shared palette, typography scale, spacing system, and accessibility standards. Every app-level UI decision will reference this foundation.

## Prerequisites
- `./spec/suite/domain-model.md` (Step 1 — needed to understand the domain context, which influences brand tone and terminology)

## Inputs to Read
- `./spec/suite/domain-model.md` — review Business Context to understand industry norms and user expectations that inform design choices

## Interrogation Process

### 1. Brand Identity & Tone
Establish the personality of the product:

- What is the product or suite name?
- Does the product have a tagline or mission statement?
- How should the product feel to users? Pick 3-5 personality traits (e.g., professional, playful, minimal, bold, trustworthy, innovative).
- Are there existing brand guidelines or a style guide to follow?
- Are there competitor products whose visual style you admire or want to differentiate from?
- What industry conventions should the design respect? (e.g., healthcare apps tend toward clean/clinical, fintech toward trust/security)

### 2. Color Palette
Define the color system:

- Do you have existing brand colors? If so, what are they (hex values)?
- If not: What mood should the primary color convey? (e.g., blue for trust, green for growth, purple for creativity)
- How many accent colors do you need? Are there distinct sections or apps that need their own accent?
- What semantic colors should the system use? (confirm defaults: success=green, warning=amber, error=red, info=blue)
- Do you need a dark mode? If so, should it be a full inversion or a separate palette?
- Are there colors to avoid? (e.g., red may conflict with cultural norms in some markets)

### 3. Typography
Define the type system:

- Do you have a preferred font family? (e.g., Inter, SF Pro, Roboto, a custom brand font)
- Should the system use a different font for headings vs. body text?
- Do you prefer a compact or spacious type scale? (compact suits data-dense apps; spacious suits consumer products)
- What is the base font size? (typical: 14px for enterprise, 16px for consumer)
- Are there monospace font needs (code display, data tables)?
- What languages must the typography support? (Latin only, CJK, RTL?)

### 4. Spacing & Layout
Define the spatial system:

- Do you prefer a 4px or 8px base spacing unit?
- Is the layout grid-based? If so, how many columns? (typical: 12-column)
- What is the maximum content width? (e.g., 1280px, 1440px, fluid)
- How dense should the UI be? (compact for power users, relaxed for casual users)
- Are there sidebar or panel width conventions to establish?

### 5. Component Style Preferences
Define visual treatment for common elements:

- Button style: Rounded, pill-shaped, or sharp corners?
- Card style: Bordered, elevated (shadow), or flat?
- Form inputs: Outlined, underlined, or filled?
- Table style: Striped rows, hover highlights, bordered cells?
- What border radius scale do you prefer? (e.g., subtle 4px, moderate 8px, rounded 12px+)
- What elevation/shadow system? (e.g., flat design with borders, or layered with shadows)

### 6. Responsive Design
Define breakpoint strategy:

- What are the target device categories? (desktop only, desktop + tablet, full responsive including mobile)
- Should the experience be equivalent across devices, or is mobile a reduced/different experience?
- What are the breakpoint values? (confirm or adjust defaults: sm=640px, md=768px, lg=1024px, xl=1280px, 2xl=1536px)
- Are there specific mobile interaction patterns preferred? (bottom navigation, swipe gestures, pull-to-refresh)

### 7. Accessibility & Motion
Define inclusive design standards:

- What WCAG conformance level is required? (A, AA, or AAA)
- Are there specific accessibility requirements beyond WCAG? (e.g., screen reader optimization, keyboard-only navigation)
- What contrast ratio targets? (WCAG AA minimum: 4.5:1 for text, 3:1 for large text)
- Should focus indicators be highly visible or subtle?
- What is the motion/animation philosophy? (no motion, subtle transitions, expressive animations)
- Should the system respect `prefers-reduced-motion`?
- What icon style? (outlined, filled, duotone) Any specific icon library preferred?

## Output Specification

### `./spec/suite/design-system.md`

The output file must contain these sections:

#### Brand Identity
- **Product Name**
- **Tagline** (if applicable)
- **Personality Traits**: 3-5 adjectives with brief explanation of how each manifests in the UI

#### Color Palette
Tables for each color group:
- **Primary**: name, hex, usage context
- **Secondary**: name, hex, usage context
- **Accent**: name, hex, usage context
- **Semantic**: success, warning, error, info — each with hex and usage
- **Neutrals**: gray scale from 50 to 950 with hex values
- **Dark Mode** (if applicable): mapping of light mode colors to dark mode equivalents

#### Typography Scale
- **Font Families**: heading, body, mono — with fallback stacks
- **Size Scale**: named sizes (xs through 4xl) with px/rem values and intended use
- **Weight Scale**: named weights with numeric values
- **Line Heights**: default, tight, relaxed values
- **Letter Spacing**: adjustments for headings, body, uppercase text

#### Spacing System
- **Base Unit**: value in px
- **Scale**: named spacing values (xs through 4xl) with computed px values
- **Layout Grid**: column count, gutter width, margin width

#### Elevation System
- **Shadow Scale**: named levels (sm, md, lg, xl) with CSS shadow values
- **Usage Guidelines**: when to use each level

#### Border Radius Scale
- **Scale**: named values (sm, md, lg, full) with px values
- **Usage Guidelines**: which components use which radius

#### Responsive Breakpoints
A markdown table with columns:
| Name | Min Width | Typical Device | Layout Notes |

#### Accessibility Standards
- **WCAG Level**: target conformance
- **Contrast Ratios**: minimum ratios for text, interactive elements, decorative elements
- **Focus Indicators**: style description (color, width, offset)
- **Keyboard Navigation**: tab order conventions, skip links
- **Screen Reader**: ARIA usage guidelines

#### Motion & Animation
- **Philosophy**: one-sentence approach statement
- **Transition Defaults**: duration, easing function
- **Reduced Motion**: behavior when `prefers-reduced-motion` is active
- **Loading Animations**: skeleton screen vs spinner preference

#### Iconography
- **Style**: outlined/filled/duotone
- **Library**: preferred icon set
- **Size Scale**: standard icon sizes
- **Usage Guidelines**: when to use icons, labeling requirements

## Completion Checklist
- [ ] `./spec/suite/design-system.md` created
- [ ] Color palette defined with hex values for all categories
- [ ] Typography scale defined with font families and size scale
- [ ] Spacing system defined with base unit and scale
- [ ] Responsive breakpoints specified
- [ ] Accessibility standards documented with WCAG level
- [ ] Motion principles established
