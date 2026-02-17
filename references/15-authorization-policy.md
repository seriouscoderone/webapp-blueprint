# Step 15: Authorization Policy

## Tier
3 — Per-app specification (runs for each app; defines enforcement rules for access control)

## Purpose
The Authorization Policy translates the app's role refinement into concrete enforcement rules at every layer: routes, API endpoints, UI elements, and data. It specifies exactly who can access what, under what conditions, and what happens when access is denied. This spec ensures that authorization is consistently applied rather than implemented ad-hoc across features.

## Prerequisites
- `./spec/apps/{app_name}/role-refinement.md` — app-level roles and permissions
- `./spec/apps/{app_name}/api-contracts.md` — API endpoints to protect
- `./spec/apps/{app_name}/pages/*.md` — pages with role-based variations

## Inputs to Read
- `./spec/apps/{app_name}/role-refinement.md`
- `./spec/apps/{app_name}/api-contracts.md`
- `./spec/apps/{app_name}/pages/*.md` (all page specs, especially role variations)
- `./spec/apps/{app_name}/features/*.feature.md` (for permission-related scenarios)
- `./spec/suite/role-permission-matrix.md` (for suite-wide role definitions)

## Interrogation Process

### 1. Authorization Model
Establish the overall approach:

- What authorization model fits this app? Options:
  - **RBAC** (Role-Based Access Control): Permissions are assigned to roles, users are assigned roles. Simple and common.
  - **ABAC** (Attribute-Based Access Control): Access depends on attributes of the user, resource, and context. More flexible.
  - **Hybrid**: RBAC as the foundation with attribute-based conditions for specific rules (e.g., "Managers can edit, but only within their department").
- Are roles hierarchical? (e.g., Admin inherits all Manager permissions, Manager inherits all Viewer permissions)
- Can a user hold multiple roles simultaneously?
- Are there organization-level or team-level role scoping? (e.g., Admin of Project A but Viewer of Project B)

### 2. Route-Level Policies
For each page/route in the app:

- Which roles can access this route?
- What happens when an unauthorized user tries to navigate to this route? (Redirect to login, redirect to home, show 403 page?)
- Are there routes that are public (no auth required)?
- Are there routes that require a specific role AND a specific condition? (e.g., "Admin OR the project owner")

### 3. API-Level Policies
For each API endpoint:

- Which roles are allowed to call this endpoint?
- Are there additional conditions beyond role? (e.g., "Can only update resources they own", "Can only access resources in their department")
- Are there field-level restrictions? (e.g., "Viewers cannot see salary field in the API response")
- Are there rate limit differences by role?

### 4. UI Element Visibility
For interactive elements across pages:

- Which buttons, actions, or menu items should be hidden (not just disabled) for certain roles?
- Should unauthorized actions be hidden entirely or shown as disabled with a tooltip explaining why?
- Are there sections of a page that are visible only to certain roles?
- Should the navigation menu reflect role-based access (hide links to pages the user cannot access)?

### 5. Data-Level Policies
Define row-level and field-level security:

- Can users see all records or only records they are related to? (e.g., "Sales reps see only their own leads")
- Are there tenant/organization boundaries? (Multi-tenant isolation)
- Are there fields that should be redacted or hidden based on role? (e.g., mask SSN for non-admin users)
- Are there soft-delete policies? (Who can see deleted records?)
- Is there audit-log access control? (Who can view audit trails?)

### 6. Ownership Rules
Define resource ownership:

- When a user creates a resource, are they the "owner"?
- What can an owner do that others in the same role cannot? (e.g., "Only the creator can delete a draft")
- Can ownership be transferred?
- Are there resources with shared ownership (multiple owners)?
- Do ownership rules override role-based rules or work alongside them?

### 7. Escalation & Overrides
Define escape hatches:

- Can admins override normal authorization rules? (e.g., edit any record, impersonate any user)
- Is there an impersonation or "act as" feature for support/admin use?
- Are there emergency access patterns? (e.g., break-glass access with audit logging)
- Can authorization be temporarily elevated? (e.g., a manager grants a team member temporary edit access)

## Output Specification

### `./spec/apps/{app_name}/authorization.md`

The output file must contain these sections:

#### Policy Overview
- **Model**: RBAC, ABAC, or Hybrid
- **Role Hierarchy**: Whether roles inherit permissions and the inheritance chain
- **Multi-Role**: Whether users can hold multiple roles
- **Scope**: Whether roles are global, per-organization, per-project, etc.
- **Default Deny**: Confirm that the default policy is deny-all unless explicitly allowed

#### Roles Summary
A quick reference of all roles relevant to this app:
| Role | Description | Inherits From |
|---|---|---|
| Admin | Full access to all features | Manager |
| Manager | Can manage team and resources | Member |
| Member | Standard user with CRUD on own resources | Viewer |
| Viewer | Read-only access | — |

#### Route-Level Policies
A table covering every route:
| Route | Allowed Roles | Additional Conditions | Denied Redirect |
|---|---|---|---|
| `/dashboard` | Admin, Manager, Member, Viewer | — | `/login` |
| `/settings` | Admin | — | `/dashboard` |
| `/projects/:id/edit` | Admin, Manager | Must be project member | `/projects/:id` |
| `/admin/users` | Admin | — | `/dashboard` |

#### API-Level Policies
A table covering every endpoint:
| Method | Endpoint | Allowed Roles | Conditions | Denied Status |
|---|---|---|---|---|
| GET | /projects | All authenticated | Returns only projects user is a member of | 401 |
| POST | /projects | Admin, Manager | — | 403 |
| PUT | /projects/:id | Admin, Manager | Must be project member | 403 |
| DELETE | /projects/:id | Admin | — | 403 |
| GET | /admin/users | Admin | — | 403 |

For endpoints with complex conditions, add a detail block:
```
PUT /projects/:id
  Roles: Admin, Manager
  Conditions:
    - User must be a member of the project
    - If Manager: can only update projects in their department
    - If Admin: no additional conditions
  Field restrictions:
    - Manager cannot modify: budget, priority
    - Member: read-only access (GET only)
```

#### UI Element Visibility
A table for each page with role-dependent elements:
| Page | Element | Admin | Manager | Member | Viewer |
|---|---|---|---|---|---|
| Project List | "Create" button | Visible | Visible | Hidden | Hidden |
| Project Detail | "Delete" action | Visible | Hidden | Hidden | Hidden |
| Project Detail | "Edit" button | Visible | Visible | Hidden | Hidden |
| Project Detail | Budget section | Visible | Visible | Hidden | Hidden |
| Settings | User Management tab | Visible | Hidden | Hidden | Hidden |

Note the strategy for each:
- **Hidden**: Element is not rendered in the DOM
- **Disabled**: Element is rendered but grayed out with tooltip
- **Conditional**: Element visibility depends on additional attributes

#### Data-Level Policies
Define row-level and field-level security:

**Row-Level Security:**
| Entity | Rule | Description |
|---|---|---|
| Project | Membership | Users can only see projects they are members of |
| Task | Project scope | Users can see tasks within their accessible projects |
| User | Organization | Users can only see users within their organization |

**Field-Level Security:**
| Entity | Field | Admin | Manager | Member | Viewer |
|---|---|---|---|---|---|
| User | email | Read/Write | Read | Read | Hidden |
| User | salary | Read/Write | Read | Hidden | Hidden |
| Project | budget | Read/Write | Read | Hidden | Hidden |

#### Ownership Rules
- **Default Ownership**: Who becomes the owner when a resource is created
- **Owner Privileges**: What actions are exclusive to the owner (beyond their role permissions)
| Entity | Owner Can | Non-Owner Same Role Can |
|---|---|---|
| Draft Document | Edit, Delete, Submit | View only |
| Comment | Edit, Delete | View, Reply |
| Project | Transfer ownership, Archive | Cannot |
- **Ownership Transfer**: How and when ownership can be changed
- **Shared Ownership**: Whether resources can have multiple owners

#### Escalation & Override Paths
- **Admin Override**: What admins can do that bypasses normal rules (with audit logging)
- **Impersonation**: If supported, how it works (with audit trail requirements)
- **Temporary Elevation**: How temporary access grants work (duration, approval, revocation)
- **Break-Glass Access**: Emergency access patterns with mandatory audit
- **Audit Requirements**: Which authorization overrides must be logged and what the log entry contains

## Completion Checklist
- [ ] `./spec/apps/{app_name}/authorization.md` created
- [ ] Authorization model (RBAC/ABAC/Hybrid) is chosen and documented
- [ ] Every route has a policy defined with allowed roles and redirect behavior
- [ ] Every API endpoint has a policy with allowed roles and conditions
- [ ] UI element visibility rules cover all role-dependent interface elements
- [ ] Data-level policies define row-level and field-level security
- [ ] Ownership rules are documented for entities with creator-specific permissions
- [ ] Escalation and override paths are defined with audit requirements
- [ ] The default-deny principle is explicitly stated
