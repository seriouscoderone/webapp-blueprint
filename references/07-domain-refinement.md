# Step 7: Domain Model Refinement (Per-App)

## Tier
2 — Per-app specification (run once per app in the suite)

## Purpose
Narrows the suite-wide domain model down to this app's scope. Determines which entities this app owns (is the source of truth for), which it merely references from other apps, and whether any new app-specific entities are needed. Establishes the data lifecycle and business rules that apply within this app's boundary.

## Prerequisites
- `./spec/suite/domain-model.md` (Step 1)
- `./spec/apps/{app_name}/archetype.md` (Step 6)

## Inputs to Read
- `./spec/suite/domain-model.md` — full list of suite entities, their attributes, and relationships
- `./spec/apps/{app_name}/archetype.md` — app identity, selected archetype(s), target roles, and goals

## App Selection Process
Before starting, confirm which app the user is working on:
1. List existing apps in `./spec/apps/` that already have `archetype.md`.
2. Ask: "Which app are you refining the domain model for?"
3. Verify that `archetype.md` exists for the selected app before proceeding.

## Interrogation Process

### Entity Ownership
Present the full entity list from `domain-model.md`:
- "Looking at the suite entities, which ones does **{app_name}** own — meaning this app is where those records are created and managed?"
- "Which entities does this app need to display or reference but does NOT create or modify?"
- For each owned entity: "Does this app manage the full lifecycle (create, update, archive/delete), or only part of it?"

### App-Specific Entities
- "Are there any entities unique to this app that aren't in the suite domain model?"
- "Do any of the suite entities need app-specific extensions — extra fields or statuses that only matter inside this app?"
- If the archetype is Workflow Engine: "What are the workflow-specific entities (e.g., process instances, steps, approvals)?"
- If the archetype is Content Platform: "What content types exist? Do they need versioning or drafts?"

### Business Rules
- "What are the key business rules that govern data in this app?"
- "Are there validation rules specific to this app beyond what the suite model defines?"
- "Are there any computed or derived fields this app needs?"
- "Are there constraints between entities (e.g., an order can't be approved without at least one line item)?"

### Read vs. Write Patterns
- "For each owned entity, what's the typical ratio of reads to writes?"
- "Are there any entities that are write-heavy (frequent updates, real-time changes)?"
- "Does the app need optimistic updates for any operations?"
- "Are there bulk operations (batch create, mass update, import)?"

### Data Lifecycle
- "What happens when a record is 'deleted' in this app — soft delete, archive, or hard delete?"
- "Are there status transitions that records go through (e.g., draft → active → closed)?"
- "Is there a retention policy — how long does data live before archiving?"
- "Does any data need to be synchronized with other apps in the suite?"

## Output Specification

### `./spec/apps/{app_name}/domain-refinement.md`

```markdown
# {App Display Name} — Domain Refinement

## Owned Entities
Entities this app is the source of truth for.

| Entity | Operations | Lifecycle | Notes |
|--------|-----------|-----------|-------|
{One row per owned entity — include create/read/update/delete/archive as applicable}

### Entity Details
{For each owned entity, list key attributes, required fields, and any app-specific extensions beyond the suite model}

## Referenced Entities
Entities owned by other apps, used here as read-only or via ID reference.

| Entity | Source App | Usage in This App | Notes |
|--------|-----------|-------------------|-------|
{One row per referenced entity}

## App-Specific Entities
Entities that exist only within this app's scope.

| Entity | Purpose | Key Attributes | Relationships |
|--------|---------|---------------|---------------|
{One row per app-specific entity — omit section if none}

## Entity Relationship Diagram
{Text-based diagram showing relationships between owned, referenced, and app-specific entities within this app's scope. Use simple notation:}
{Entity A ──1:N──▶ Entity B}
{Entity C ──M:N──▶ Entity D (via JoinEntity)}
{[External] Entity E ◇──▶ Entity A (referenced)}

## App-Specific Business Rules
1. {Rule — e.g., "An invoice cannot be finalized without at least one line item"}
2. {Rule}
{Number each rule for easy reference in later steps}

## Data Lifecycle
### Creation
{How records enter the system — user input, import, system-generated}

### Active State
{Normal operations — editing, status transitions, relationships}

### Archival / Deletion
{What happens at end-of-life — soft delete, archive, hard delete, retention period}

### Cross-App Sync
{If data changes here, what other apps need to know? Reference events from api-event-contracts.md}
```

## Completion Checklist
- [ ] Every suite entity classified as owned, referenced, or not applicable to this app
- [ ] App-specific entities identified (if any) with attributes and relationships
- [ ] Entity relationship diagram covers all entities in this app's scope
- [ ] Business rules documented and numbered
- [ ] Read/write patterns noted for owned entities
- [ ] Data lifecycle defined (creation, active use, archival/deletion)
- [ ] Cross-app sync needs identified (if applicable)
- [ ] Output file written to `./spec/apps/{app_name}/domain-refinement.md`
