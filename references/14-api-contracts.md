# Step 14: App-Level API Contracts

## Tier
3 — Per-app specification (runs for each app; defines the concrete API surface the app requires)

## Purpose
App-Level API Contracts define the actual HTTP endpoints, request/response schemas, error responses, and real-time channels that the app's frontend will consume. While the suite-level API event contracts define cross-app communication patterns, this step produces the concrete, implementation-ready API specification for a single app, covering every endpoint needed to support its pages, features, and state management requirements.

## Prerequisites
- `./spec/apps/{app_name}/domain-refinement.md` — app-level domain model
- `./spec/apps/{app_name}/features/*.feature.md` — BDD feature specs
- `./spec/apps/{app_name}/pages/*.md` — page specs (to know what data each page needs)
- `./spec/apps/{app_name}/state-interaction.md` — state management and caching requirements
- `./spec/suite/api-event-contracts.md` — suite-wide API patterns and event bus

## Inputs to Read
- `./spec/apps/{app_name}/domain-refinement.md`
- `./spec/apps/{app_name}/features/*.feature.md`
- `./spec/apps/{app_name}/pages/*.md`
- `./spec/apps/{app_name}/state-interaction.md`
- `./spec/apps/{app_name}/role-refinement.md`
- `./spec/suite/api-event-contracts.md`

## Interrogation Process

### 1. API Style & Conventions
Establish the API foundation:

- Is the API RESTful, GraphQL, tRPC, or a combination? (Or do you want a recommendation based on the app's needs?)
- What is the base URL pattern? (e.g., `/api/v1/{resource}`)
- What naming convention should be used for endpoints? (kebab-case, camelCase, snake_case)
- What is the standard response envelope? (e.g., `{ data, meta, errors }` or flat response?)
- What authentication mechanism is used? (Bearer token, session cookie, API key)
- What is the standard date/time format? (ISO 8601, Unix timestamp)
- What is the standard ID format? (UUID v4, CUID, auto-increment integer)

### 2. Endpoint Inventory
Walk through each page and feature to derive endpoints:

- For page {page_name}, what API calls are needed? (Cross-reference with the page spec's data requirements)
- For feature {feature_name}, what mutations (create, update, delete) are needed?
- Are there endpoints that serve multiple pages? (Shared data like current user, notifications)
- Are there endpoints that need to support different representations? (e.g., list view vs. detail view of the same entity)
- Are there batch or bulk endpoints needed? (e.g., bulk delete, bulk status update)

### 3. Per-Endpoint Detail
For each endpoint, clarify:

#### Request
- What are the path parameters? (e.g., `:projectId`, `:taskId`)
- What query parameters are supported? (Filtering, sorting, pagination, field selection)
- What is the request body schema for mutations?
- Are there file upload endpoints? What are the constraints (size, type)?

#### Response
- What fields are returned? What is the TypeScript-style interface?
- Are related entities embedded or returned as IDs (with separate lookup)?
- Is the response paginated? What pagination style? (Offset, cursor, page-based)
- Are there different response shapes for list vs. detail?

#### Errors
- What error status codes can this endpoint return?
- What is the error response body format?
- Are there domain-specific error codes? (e.g., `INSUFFICIENT_BALANCE`, `APPROVAL_REQUIRED`)

### 4. Real-Time Channels
If the state-interaction spec calls for real-time data:

- What WebSocket or SSE channels does this app need?
- What is the message format for each channel?
- How does the client subscribe/unsubscribe?
- Are there per-entity channels (e.g., subscribe to updates for a specific project)?

### 5. Domain Events
Identify events this app produces and consumes:

- What domain events does this app emit when mutations occur? (Cross-reference with suite api-event-contracts.md)
- What domain events from other apps does this app consume?
- What is the event payload schema?

## Output Specification

### `./spec/apps/{app_name}/api-contracts.md`

The output file must contain these sections:

#### API Conventions
- **Style**: REST, GraphQL, tRPC, or hybrid
- **Base URL**: The base path for all endpoints
- **Authentication**: How requests are authenticated
- **Response Envelope**: The standard wrapper format
- **Date Format**: ISO 8601 or other
- **ID Format**: UUID, CUID, etc.
- **Error Format**: Standard error response structure
```typescript
interface ApiError {
  status: number;
  code: string;
  message: string;
  details?: Record<string, string[]>;
}
```

#### Endpoints Overview
A summary table of all endpoints:
| Method | Path | Description | Auth | Rate Limit |
|---|---|---|---|---|
| GET | /projects | List projects | Yes | 100/min |
| POST | /projects | Create project | Yes | 20/min |
| GET | /projects/:id | Get project detail | Yes | 100/min |
| PUT | /projects/:id | Update project | Yes | 30/min |
| DELETE | /projects/:id | Delete project | Yes | 10/min |

#### Endpoint Groups
For each logical group of endpoints (typically per entity), a detailed section:

##### {Entity} Endpoints

**List {Entities}**
```
GET /api/v1/{entities}
```
Query Parameters:
| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `page` | `number` | No | `1` | Page number |
| `limit` | `number` | No | `25` | Items per page (max 100) |
| `sort` | `string` | No | `createdAt` | Sort field |
| `order` | `'asc' \| 'desc'` | No | `desc` | Sort direction |
| `search` | `string` | No | — | Full-text search query |
| `status` | `string` | No | — | Filter by status |

Response: `200 OK`
```typescript
interface ListResponse {
  data: Entity[];
  meta: {
    total: number;
    page: number;
    limit: number;
    totalPages: number;
  };
}
```

**Create {Entity}**
```
POST /api/v1/{entities}
```
Request Body:
```typescript
interface CreateEntityRequest {
  name: string;
  description?: string;
  // ... fields
}
```

Response: `201 Created`
```typescript
interface EntityResponse {
  data: Entity;
}
```

Error Responses:
| Status | Code | Description |
|---|---|---|
| 400 | `VALIDATION_ERROR` | Request body failed validation |
| 401 | `UNAUTHORIZED` | Missing or invalid auth token |
| 403 | `FORBIDDEN` | User lacks permission |
| 409 | `CONFLICT` | Entity with this name already exists |
| 422 | `BUSINESS_RULE_VIOLATION` | Domain rule prevents this action |

*Repeat for Get, Update, Delete, and any custom actions.*

#### Shared Schemas
TypeScript interfaces for entities and common types used across endpoints:
```typescript
interface Entity {
  id: string;
  createdAt: string;
  updatedAt: string;
  createdBy: string;
  // ... entity-specific fields
}

interface PaginationMeta {
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}
```

#### WebSocket / SSE Channels
If real-time communication is needed:
| Channel | Transport | Subscribe | Message Payload | Description |
|---|---|---|---|---|
| `projects:{id}:updates` | WebSocket | On project detail open | `{ field, oldValue, newValue, updatedBy }` | Real-time project field changes |
| `notifications` | SSE | On app load | `{ id, type, title, body, createdAt }` | User notification stream |

For each channel:
- **Subscribe**: When/how the client subscribes
- **Unsubscribe**: When/how the client disconnects
- **Message Format**: TypeScript interface for the message payload
- **Reconnection**: Behavior when the connection drops

#### Domain Events
Events this app produces:
| Event | Trigger | Payload |
|---|---|---|
| `project.created` | POST /projects | `{ projectId, name, createdBy }` |
| `task.status.changed` | PUT /tasks/:id (status field) | `{ taskId, oldStatus, newStatus, changedBy }` |

Events this app consumes:
| Event | Source App | Handler |
|---|---|---|
| `user.deactivated` | Identity app | Remove user from project members |
| `billing.subscription.changed` | Billing app | Update feature flags |

## Completion Checklist
- [ ] `./spec/apps/{app_name}/api-contracts.md` created
- [ ] API conventions (style, auth, response format) are documented
- [ ] Every page's data requirements are covered by at least one endpoint
- [ ] Every feature's mutations are covered by at least one endpoint
- [ ] All endpoints have request and response schemas defined
- [ ] Error responses are documented with status codes and error codes
- [ ] Pagination is specified for all list endpoints
- [ ] Real-time channels are defined if state-interaction spec requires them
- [ ] Domain events (produced and consumed) are documented
