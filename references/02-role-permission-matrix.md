# Step 2: Role & Permission Matrix

## Tier
1 — Suite-level (runs once, establishes global access control model for the entire application suite)

## Purpose
The Role & Permission Matrix defines who can do what across the entire suite. It maps user roles to entity-level operations and data visibility rules. This step produces the authorization foundation that every app-level step will reference when defining feature access, UI visibility, and API guards.

## Prerequisites
- `./spec/suite/domain-model.md` (Step 1 — needed to understand entities, operations, and workflows)

## Inputs to Read
- `./spec/suite/domain-model.md` — review the Entity Glossary, Domain Event Catalog, and Key Business Rules to understand what operations exist and what constraints apply

## Interrogation Process

### 1. User Types & Roles
Identify who uses the system:

- What are the distinct types of users who will interact with this system?
- For each user type: What is their primary goal when using the system?
- Are there internal users (employees, admins) and external users (customers, partners, vendors)?
- Is there a super-admin or system administrator role? What can they do that no one else can?
- Are there roles that exist only temporarily (e.g., an auditor during compliance review)?
- Can a single person hold multiple roles simultaneously?

### 2. Organizational Hierarchy
Understand how roles relate structurally:

- Is there a hierarchy among roles (e.g., manager can see everything their reports can see)?
- Does permission inheritance follow the org chart, or is it independent?
- Are there team or group-level permissions (e.g., a user can see only their team's data)?
- Do any roles have tenant-level or organization-level scoping?

### 3. Permission Granularity
Define what operations each role can perform:

- For each entity in the domain model: Which roles can Create, Read, Update, Delete it?
- Are there operations beyond CRUD? (e.g., approve, publish, archive, export, assign, escalate)
- Are there field-level permissions? (e.g., a user can see an order but not the profit margin)
- Can permissions be conditional? (e.g., "can edit only their own records", "can approve only if amount < $10k")
- Are there time-based permissions? (e.g., "can edit within 24 hours of creation")

### 4. Data Visibility & Scope
Define what data each role can see:

- Can all users see all records, or is data scoped? (e.g., by team, region, department, tenant)
- Are there records that should be completely hidden from certain roles (not just read-only, but invisible)?
- Are there aggregate/summary views that show data without exposing individual records?
- Can users see historical data, or only current state?
- Are there data export restrictions by role?

### 5. Authentication & Session Requirements
Capture security requirements:

- What authentication methods are supported? (password, SSO, OAuth, magic link, MFA)
- Which roles require MFA?
- What are the session duration requirements? (e.g., admin sessions expire after 15 minutes of inactivity)
- Are there IP-based or device-based access restrictions?
- Is there a password policy? (length, complexity, rotation)
- Are there requirements for audit logging of access?

## Output Specification

### `./spec/suite/role-permission-matrix.md`

The output file must contain these sections:

#### Role Definitions
A markdown table with columns:
| Role | Description | Typical User | Access Level | Notes |
Access Level should indicate broad scope (e.g., "Global", "Organization", "Team", "Self").

#### Permission Matrix
A markdown table with entity-operation combinations as rows and roles as columns. Use these symbols:
- `C` = Create, `R` = Read, `U` = Update, `D` = Delete
- `*` = All operations
- `-` = No access
- Custom operations listed explicitly (e.g., `Approve`, `Export`)

| Entity / Operation | Admin | Manager | Member | Viewer |
Include conditional permissions as footnotes (e.g., "U^1" where footnote 1 = "own records only").

#### Data Visibility Rules
For each role, describe:
- **Scope**: What data boundary applies (global, org, team, self)
- **Filters**: Any automatic filters applied (e.g., "sees only active records")
- **Hidden Fields**: Fields excluded from this role's view
- **Export**: Whether the role can export data and in what formats

#### Role Hierarchy
Describe the inheritance chain. Use a simple text tree or list format:
- Which roles inherit permissions from other roles
- Where inheritance is overridden or restricted
- Whether custom roles are supported

#### Authentication Requirements
A markdown table with columns:
| Role | Auth Method | MFA Required | Session Timeout | IP Restrictions | Audit Level |

## Completion Checklist
- [ ] `./spec/suite/role-permission-matrix.md` created
- [ ] All user roles identified with clear descriptions
- [ ] Permission matrix covers every entity from the domain model
- [ ] Conditional permissions documented with footnotes
- [ ] Data visibility scope defined for each role
- [ ] Authentication and session requirements specified per role
