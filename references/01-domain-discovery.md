# Step 1: Domain Discovery

## Tier
1 — Suite-level (runs once, establishes global context for the entire application suite)

## Purpose
Domain Discovery is the foundational step of the specification pipeline. It captures the business domain, core entities, relationships, workflows, and domain events that will inform every subsequent step. A thorough domain model prevents misalignment between business reality and technical design.

## Prerequisites
- None (this is the first step in the pipeline)

## Inputs to Read
- None

## Interrogation Process

### 1. Business Overview
Ask these questions to establish the high-level context:

- What industry or sector does this application serve?
- What is the core problem this application solves? Who experiences this problem today?
- What is the value proposition — why would someone choose this over alternatives?
- Is this a greenfield product or a replacement/modernization of an existing system?
- If replacing an existing system, what are its biggest shortcomings?
- Who are the primary stakeholders (not end-users, but people who care about the product's success)?
- Are there regulatory or compliance requirements specific to this domain (e.g., HIPAA, PCI-DSS, GDPR, SOX)?

### 2. Core Entity Discovery
Identify the nouns of the domain:

- What are the main "things" the system manages? (e.g., orders, patients, projects, invoices)
- For each entity: What are its key attributes? Which attributes are required vs. optional?
- Are there entities with distinct lifecycle states? What are those states and what triggers transitions?
- Which entities are created by users vs. derived/computed by the system?
- Are there entities that represent real-world physical objects vs. abstract concepts?
- Which entity would you consider the most central — the one everything else relates to?
- Are there entities that are shared across multiple contexts or apps? (e.g., a "User" entity used everywhere)
- Do any entities have versioning or audit history requirements?

### 3. Relationship Mapping
Understand how entities connect:

- For each pair of related entities: Is the relationship one-to-one, one-to-many, or many-to-many?
- Are any relationships optional (an entity can exist without the related entity)?
- Are there hierarchical relationships (parent-child, folder-file, org-team-member)?
- Do any entities "belong to" or "are owned by" another entity?
- Are there relationships that change over time (e.g., a task can be reassigned)?

### 4. Workflow / Process Discovery
Map the key business processes:

- Walk me through the most common workflow from start to finish. What triggers it? What steps occur? How does it end?
- Are there approval or review steps in any workflow? Who approves, and what are the possible outcomes?
- What are the 3-5 most frequent actions users perform daily?
- Are there time-sensitive processes (deadlines, SLAs, escalations)?
- Do any workflows span multiple user roles? If so, what are the handoff points?
- Are there batch or scheduled processes (e.g., end-of-day reconciliation, weekly reports)?
- Are there workflows that involve external parties (customers, vendors, partners)?
- What happens when a workflow is interrupted or abandoned midway?

### 5. Domain Event Identification
Capture the things that "happen" in the system:

- What are the most important state changes in the system? (e.g., "order placed", "payment received", "user deactivated")
- Which state changes should trigger notifications to users?
- Are there events that should trigger automated actions (e.g., sending an email, updating a dashboard)?
- Do any events need to be communicated to external systems?
- Are there events that multiple parts of the system care about?

### 6. Business Rules & Constraints
Identify invariants and edge cases:

- What are the hard constraints the system must enforce? (e.g., "an invoice cannot be edited after it is sent")
- Are there validation rules that are domain-specific rather than generic? (e.g., "a prescription requires a licensed provider")
- Are there limits or quotas? (e.g., max team size, storage limits, rate limits)
- What are the most common edge cases or exceptions in the current process?
- Are there rules that vary by customer tier, region, or configuration?

## Output Specification

### `./spec/suite/domain-model.md`

The output file must contain these sections:

#### Business Context
- **Industry**: The sector or vertical
- **Problem Statement**: 2-3 sentences describing the core problem
- **Value Proposition**: What makes this solution compelling
- **Target Users**: Brief description of who uses this system day-to-day
- **Compliance Requirements**: Any regulatory constraints (or "None identified")
- **Existing Systems**: Systems being replaced or integrated with (or "Greenfield")

#### Entity Glossary
A markdown table with columns:
| Entity | Description | Key Attributes | Lifecycle States | Relationships |
Each entity should have a concise but complete entry. Include at least 3-5 key attributes per entity. For lifecycle states, list the possible states in order (e.g., Draft -> Active -> Archived). For relationships, use the format: "has many [Entity]", "belongs to [Entity]", "references [Entity]".

#### Domain Event Catalog
A markdown table with columns:
| Event Name | Trigger | Producer Entity | Consumer(s) | Payload Summary |
Use past-tense verb phrases for event names (e.g., `OrderPlaced`, `UserDeactivated`).
Include both user-initiated events (e.g., "user clicks submit") and system-initiated events (e.g., "scheduled job runs"). Payload summary should list the 3-5 most important fields carried by the event.

#### Aggregate Boundaries
Group entities into aggregates — clusters of entities that change together and enforce consistency boundaries. For each aggregate:
- **Aggregate root**: The entity that controls access to the aggregate
- **Members**: Other entities in the aggregate
- **Invariants**: Rules enforced within the aggregate boundary
- **Concurrency Notes**: How concurrent modifications are handled (optimistic locking, last-write-wins, etc.)

Aggregates should be drawn around transactional consistency boundaries. If two entities must always be updated together atomically, they belong in the same aggregate.

#### Key Business Rules
A numbered list of business rules, each with:
- **Rule**: Plain-language statement of the constraint
- **Enforcement**: Where/how the system enforces it (e.g., "API validation", "database constraint", "workflow gate")
- **Severity**: What happens if this rule is violated (e.g., "block action", "warn user", "log for audit")

Distinguish between hard constraints (must never be violated) and soft constraints (can be overridden with appropriate authority).

#### Glossary of Domain Terms
A brief glossary of domain-specific terminology that may be unfamiliar or ambiguous. This ensures all subsequent steps use consistent language. Format as a definition list:
- **Term**: Definition as understood in this domain

#### Open Questions
A bulleted list of unresolved items discovered during the conversation. Each item should include:
- The question itself
- Why it matters (which downstream decisions depend on it)
- Who might be able to answer it (role or person)

## Completion Checklist
- [ ] `./spec/suite/domain-model.md` created
- [ ] At least 5 entities identified with attributes and relationships
- [ ] At least 3 domain events cataloged
- [ ] Aggregate boundaries defined for all entities
- [ ] Business rules documented with enforcement strategy
- [ ] Open questions captured for follow-up
