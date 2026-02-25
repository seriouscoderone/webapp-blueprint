# Step 18: Seed Data Specification

## Tier
4 — Per-app (final, runs after Steps 16–17 are complete for an app)

## Purpose
Define a complete, realistic dataset that exercises every BDD scenario, covers all user roles, and populates all entity relationships — ready to feed fixtures, factories, or a seed script. Seed data ensures the generated application can be immediately tested with meaningful, representative data rather than empty states or arbitrary values.

## Prerequisites
- `./spec/apps/{app_name}/features/*.feature.md` (Step 9) — BDD scenarios to cover
- `./spec/apps/{app_name}/api-contracts.md` (Step 14) — entity schemas and field types
- `./spec/apps/{app_name}/generation-briefs/` (Step 17) — build order and page context

## Inputs to Read
- `./spec/apps/{app_name}/features/*.feature.md` — to enumerate all scenarios requiring data
- `./spec/apps/{app_name}/domain-refinement.md` — entity list, attributes, and relationships
- `./spec/apps/{app_name}/role-refinement.md` — roles and permission boundaries
- `./spec/apps/{app_name}/api-contracts.md` — field types, constraints, and enums
- `./spec/apps/{app_name}/authorization.md` — role-based data visibility rules

## App Selection Process
Before any interrogation, determine which app the user is working on:
1. List any existing apps found in `./spec/apps/` subdirectories.
2. Ask: "Which app are you creating seed data for?"
3. Confirm that all prerequisite files exist for the selected app before proceeding.
4. Load and summarize the BDD features and domain entities to inform the interrogation.

## Interrogation Process

### 1. Volume Strategy
- "How many representative records do you need per entity? A common starting point is 5–10 unless an entity needs specific counts to trigger edge cases."
- "Are there any entities that need a specific number of records to cover all scenarios? (e.g., 'we need at least 3 orders per user to test pagination')"

### 2. Per-Entity Data Needs
For each entity found in `domain-refinement.md`:
- "For `{EntityName}`: what are the distinct states or variants you need to see in seed data?" (e.g., active/inactive user, pending/approved/rejected order)
- "Are there any field values that must be realistic rather than random? (e.g., valid email formats, realistic product names, plausible prices)"
- "Are there any fields with constraints that seed data must respect? (e.g., unique slugs, max-length strings, valid enum values)"

### 3. BDD Scenario Coverage
Review each `.feature.md` file:
- "Scenario `{SC-NN}: {scenario title}` — does it require data that's not covered by the entity defaults above?"
- "Are there scenarios that test 'not found' or 'empty' states? How should those be triggered?"
- "Are there scenarios that test permission boundaries? Which specific records should be owned by which roles?"

### 4. Role-Specific Data
For each role in `role-refinement.md`:
- "What data should exist specifically for the `{Role}` to exercise their permissions? (e.g., an admin user, a set of records they own, records they can only read)"
- "Should any role start in a specific app state? (e.g., a new user with no history, a power user with lots of activity)"

### 5. Edge and Boundary Cases
- "Do you need an 'empty state' trigger — a user or context with zero records to test empty list views?"
- "Do you need boundary data — records with max-length strings, zero-quantity values, or extreme numeric values?"
- "Do you need error triggers — invalid, expired, or locked records that should produce error states?"

### 6. Relational Integrity
Walk through entity relationships from `domain-refinement.md`:
- "For `{EntityB}` which depends on `{EntityA}`: how many `{EntityA}` records should each `{EntityB}` reference?"
- "Are there any circular or self-referential relationships? (e.g., a user who manages other users, a category with subcategories)"
- "What is the dependency creation order? Which entities must be seeded before others?"

### 7. Format and Tooling
- "What format do you want for the seed data output?"
  - JSON fixtures (import directly into test runner)
  - Factory function stubs (TypeScript/JavaScript factory pattern)
  - SQL seed script
  - Markdown tables (human-readable reference)
- "Where will the seed script or fixtures live in the project? (e.g., `src/db/seeds/`, `test/fixtures/`)"
- "Do you use a specific seeding library or ORM? (e.g., Prisma seed, Drizzle, Knex, Sequelize, custom)"

## Output Specification

### `./spec/apps/{app_name}/seed-data.md`

```markdown
# Seed Data Specification: {App Display Name}

## Format & Tooling
- **Output format**: [JSON fixtures / factory stubs / SQL / markdown tables]
- **Seed script location**: [e.g., `src/db/seeds/`]
- **Seeding library/ORM**: [e.g., Prisma seed script, custom]
- **Volume strategy**: [e.g., 10 records per entity unless noted below]

---

## Entities

### {EntityName}
| Field | Value Strategy | Notes |
|-------|---------------|-------|
| id | Sequential UUID (e.g., `{entity}-001`) | |
| {field} | {strategy: realistic/enum/range/fixed} | {any constraint notes} |
| ... | ... | ... |

**Records**:
- **{entity}-001**: {description, e.g., "Active admin user with 2FA enabled"}
- **{entity}-002**: {description}
- ...

{Repeat for each entity}

---

## Role Coverage Matrix

| Role | Seeded Records | Covers Scenarios |
|------|---------------|-----------------|
| {Role} | {entity-id list} | SC-01, SC-04, SC-09 |
| ... | ... | ... |

---

## BDD Scenario Coverage

| Scenario ID | Scenario Title | Data Required | Seed Record IDs |
|-------------|---------------|--------------|-----------------|
| SC-01 | {title} | {description of required data} | {entity}-001 |
| ... | ... | ... | ... |

**Uncovered Scenarios**: {List any scenarios that require runtime-generated data rather than static seed data, and why}

---

## Edge Case Data

### Empty State Triggers
- **{EntityName} empty list**: {which user/context has zero records and how to invoke it}
- ...

### Error State Triggers
- **{Condition}**: {which record ID and what makes it invalid/expired/locked}
- ...

### Boundary Data
- **Max-length {field}**: {record ID and the max-length value used}
- **Zero/null {field}**: {record ID and the boundary value}
- ...

---

## Relational Dependency Order

Seed entities in this order to satisfy foreign key and relationship constraints:

1. **{EntityA}** — no dependencies
2. **{EntityB}** — depends on EntityA (`{EntityB}.{fk_field}` → `{EntityA}.id`)
3. ...

---

## Seed Script Notes

{Any implementation notes for the developer writing the actual seed script:
- Special handling for hashed passwords
- Environment-specific values (dev vs. staging)
- How to reset/re-run the seed
- Known limitations or manual steps required}
```

## Completion Checklist
- [ ] Target app selected and all prerequisite files confirmed present
- [ ] BDD features loaded and all scenario data requirements mapped
- [ ] Volume strategy agreed upon for each entity
- [ ] Per-entity records described with distinct states and variants
- [ ] Role coverage matrix completed — every role has at least one seeded record
- [ ] BDD scenario coverage table completed — every scenario mapped to seed records
- [ ] Edge case data defined: empty, error, and boundary cases
- [ ] Relational dependency order documented
- [ ] Seed format and tooling confirmed
- [ ] Output file written to `./spec/apps/{app_name}/seed-data.md`
