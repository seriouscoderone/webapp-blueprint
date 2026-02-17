# Step 8: Role & Permission Refinement (Per-App)

## Tier
2 — Per-app specification (run once per app in the suite)

## Purpose
Takes the suite-wide role and permission matrix and narrows it to this app's scope. Determines which global roles have access, whether any app-specific roles are needed, and defines granular permissions at the feature, entity, and data level. This step also captures how the UI varies by role, which directly feeds into page and component specs later.

## Prerequisites
- `./spec/suite/role-permission-matrix.md` (Step 2)
- `./spec/apps/{app_name}/archetype.md` (Step 6)
- `./spec/apps/{app_name}/domain-refinement.md` (Step 7)

## Inputs to Read
- `./spec/suite/role-permission-matrix.md` — global roles, their descriptions, and suite-level permissions
- `./spec/apps/{app_name}/archetype.md` — target user roles and app identity
- `./spec/apps/{app_name}/domain-refinement.md` — owned entities, referenced entities, and business rules

## App Selection Process
Before starting, confirm which app the user is working on:
1. List existing apps in `./spec/apps/` that already have `domain-refinement.md`.
2. Ask: "Which app are you refining roles and permissions for?"
3. Verify that both `archetype.md` and `domain-refinement.md` exist for the selected app.

## Interrogation Process

### Active Roles
Present the target roles from `archetype.md` alongside the full global role list:
- "The archetype step identified these roles for {app_name}: [list]. Does that still look correct?"
- "Are there any global roles that should be explicitly excluded from this app?"
- "Does every listed role need access, or are some roles only relevant for specific features?"

### App-Specific Roles
- "Are there any roles needed within this app that don't exist in the suite-wide matrix?"
- "If so, is this a true new role, or a specialization of an existing global role (e.g., 'Approver' as a specialization of 'Manager')?"
- "Does this app need a concept of 'owner' — where the user who created a record has elevated permissions on it?"

### Entity-Level Permissions
For each owned entity from `domain-refinement.md`, walk through CRUD:
- "For **{entity}**, which roles can create new records?"
- "Which roles can view records? Can all roles see all records, or only their own?"
- "Which roles can edit records? Are there restrictions by record status?"
- "Which roles can delete or archive records?"
- If the archetype is Workflow Engine: "Which roles can transition records between statuses (e.g., submit, approve, reject)?"

### Feature-Level Permissions
- "Are there features or pages in this app that are restricted to certain roles?"
- "Are there any admin-only features (e.g., configuration, bulk operations, reporting)?"
- "Are there actions that require elevated confirmation (e.g., approval from a second role)?"

### Data-Level Access (Row-Level Security)
- "Can all users of a given role see all records, or only records they own / are assigned to?"
- "Is there team or department scoping — users only see data for their team?"
- "Are there any records that should be visible to everyone but editable only by owners?"
- "Does data visibility change based on record status (e.g., draft only visible to author, published visible to all)?"

### UI Variations by Role
- "How does the interface change depending on the user's role?"
- "Are there actions, buttons, or menu items that should be hidden (not just disabled) for certain roles?"
- "Does the navigation within this app change by role (e.g., admins see a settings tab)?"
- "Are there dashboard or summary views that differ by role?"

## Output Specification

### `./spec/apps/{app_name}/role-refinement.md`

```markdown
# {App Display Name} — Role & Permission Refinement

## Active Roles
Global roles that have access to this app.

| Role | Access Level | Description (in this app's context) |
|------|-------------|-------------------------------------|
{One row per active role}

## App-Specific Roles
{Roles unique to this app, if any. Omit section if none.}

| Role | Based On | Purpose | Scope |
|------|----------|---------|-------|
{One row per app-specific role}

## Permission Matrix
Permissions per role for each owned and app-specific entity.

### {Entity Name}
| Operation | {Role 1} | {Role 2} | {Role 3} | Conditions |
|-----------|----------|----------|----------|------------|
| Create    |          |          |          |            |
| Read      |          |          |          |            |
| Update    |          |          |          |            |
| Delete    |          |          |          |            |
{Use: ✅ allowed, ❌ denied, 🔒 own records only, ⚙️ conditional (explain in Conditions)}

{Repeat for each entity}

## Feature-Level Permissions
| Feature / Page | {Role 1} | {Role 2} | {Role 3} | Notes |
|---------------|----------|----------|----------|-------|
{One row per feature or restricted page}

## Data-Level Access
### Ownership Rules
{Define what "ownership" means — creator, assignee, team member, etc.}

### Row-Level Security Rules
| Rule | Applies To | Logic |
|------|-----------|-------|
{e.g., "Users see only their own drafts", "Managers see all team records"}

### Status-Based Visibility
| Entity | Status | Visibility Rule |
|--------|--------|----------------|
{e.g., "Post in Draft status visible only to author", "Published visible to all"}

## Role-Based UI Variations
### Navigation Changes
| UI Element | Visible To | Hidden From | Notes |
|-----------|-----------|-------------|-------|
{e.g., "Settings tab visible to Admin only"}

### Action Visibility
| Action | Visible To | Behavior for Others |
|--------|-----------|-------------------|
{e.g., "Delete button visible to Admin and Owner, hidden for Viewer"}

### Dashboard / Layout Variations
{Describe how the default view or layout changes per role, if applicable}
```

## Completion Checklist
- [ ] All active global roles identified for this app
- [ ] App-specific roles defined (if any) or explicitly noted as not needed
- [ ] Permission matrix covers every owned and app-specific entity from domain-refinement.md
- [ ] Feature-level permissions documented for restricted features
- [ ] Row-level security rules defined (ownership, team scoping, status-based visibility)
- [ ] UI variations per role documented (navigation, action visibility, layout changes)
- [ ] No contradictions with suite-wide role-permission-matrix.md
- [ ] Output file written to `./spec/apps/{app_name}/role-refinement.md`
