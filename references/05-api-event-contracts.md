# Step 5: Suite-Level API Conventions

## Tier
1 — Suite-level (runs once, establishes shared API conventions for the entire suite)

## Purpose
This step defines the suite-wide API style, authentication scheme, request/response conventions, and versioning strategy. It creates the contract that all app-level API definitions (Step 13) must follow. Establishing these conventions early prevents inconsistency across apps and ensures interoperability within the suite.

## Prerequisites
- `./spec/suite/domain-model.md` (Step 1 — needed to understand entities and cross-domain interactions)
- `./spec/suite/role-permission-matrix.md` (Step 2 — needed to understand authentication and authorization requirements)

## Inputs to Read
- `./spec/suite/domain-model.md` — review Entity Glossary to understand what resources the API must support
- `./spec/suite/role-permission-matrix.md` — review Authentication Requirements and Role Hierarchy to inform auth scheme design

## Interrogation Process

### 1. API Style & Philosophy
Determine the foundational API approach:

- What API style will the suite use?
  - **REST**: Resource-oriented, HTTP verbs, widely understood — recommended default
  - **GraphQL**: Flexible queries, single endpoint, client-driven data fetching
  - **Hybrid**: REST for public API, GraphQL for internal frontend use, etc.
- What URL naming convention? (e.g., `/api/v1/orders`, kebab-case vs. camelCase)
- Should the API be designed for external consumption (public API) or internal use only?
- If public: Is an API developer portal needed? OpenAPI/Swagger documentation?

### 2. Authentication & Authorization
Define the security scheme:

- What authentication mechanism? Options:
  - **JWT (JSON Web Tokens)**: Stateless, common for SPAs
  - **OAuth 2.0 / OIDC**: For SSO, third-party integrations
  - **Session-based**: Server-side sessions with cookies
  - **API Keys**: For service-to-service or public API access
- Where are tokens sent? (`Authorization: Bearer` header, cookie, query parameter)
- What is the token lifetime? Refresh token strategy?
- How are permissions encoded? (JWT claims, separate permissions endpoint, policy engine)

### 3. Versioning Strategy
Plan for API evolution:

- What versioning approach?
  - **URL path**: `/api/v1/resource` (most explicit — recommended default)
  - **Header-based**: `Accept: application/vnd.api+json; version=1`
  - **No versioning**: use additive changes only, never break
- What is the deprecation policy? How much notice before removing an endpoint?
- How many versions will be supported simultaneously?

### 4. Request & Response Conventions
Standardize the API envelope:

- What is the standard success response format? Example:
  ```json
  { "data": {...}, "meta": {...} }
  ```
- What is the standard error response format? Example:
  ```json
  { "error": { "code": "VALIDATION_ERROR", "message": "...", "details": [...] } }
  ```
- What pagination pattern?
  - **Offset-based**: `?page=2&limit=20`
  - **Cursor-based**: `?cursor=abc123&limit=20`
  - **Keyset**: `?after=id_123&limit=20`
- What sorting convention? (e.g., `?sort=created_at:desc`)
- What filtering convention? (e.g., `?filter[status]=active&filter[date_gte]=2024-01-01`)
- Should responses include HATEOAS links? (e.g., `_links` for next page, related resources)

### 5. Rate Limiting & Quotas
Define usage constraints:

- Is rate limiting required? What limits? (e.g., 100 requests/minute per user, 1000/minute per API key)
- Are limits different per role or tier? (e.g., free tier vs. enterprise)
- How are rate limits communicated? (standard headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`)
- What happens when limits are exceeded? (HTTP 429, retry-after header, queue)

## Output Specification

### `./spec/suite/api-event-contracts.md`

The output file must contain these sections:

#### API Style & Conventions
- **Style**: REST / GraphQL / Hybrid
- **Base URL Pattern**: template (e.g., `https://api.{domain}/v{version}/{resource}`)
- **Naming Conventions**: URL casing, pluralization rules, verb usage
- **Documentation**: OpenAPI spec requirement, tooling

#### Authentication & Authorization Scheme
- **Mechanism**: chosen auth approach with rationale
- **Token Format**: structure, claims, lifetime
- **Refresh Strategy**: how tokens are renewed
- **Permission Model**: how permissions are checked per request

#### Versioning Strategy
- **Approach**: chosen versioning method
- **Deprecation Policy**: timeline, notification process
- **Compatibility Rules**: what constitutes a breaking change

#### Common Request/Response Envelopes
Provide JSON examples for:
- **Success (single resource)**: response envelope with `data` field
- **Success (collection)**: response envelope with `data` array and `meta` pagination
- **Error**: error envelope with `error` object, code, message, details
- **Validation Error**: error envelope with field-level validation details

#### Pagination & Filtering
- **Pagination Style**: chosen approach with example URL
- **Sorting Convention**: parameter format with example
- **Filtering Convention**: parameter format with example
- **Default Page Size**: value and maximum allowed

#### Rate Limiting Policy
A markdown table with columns:
| Tier/Role | Requests/Minute | Requests/Day | Burst Limit | Retry Policy |
- **Headers**: which rate limit headers are included in responses
- **Exceeded Behavior**: response code, body, retry guidance

## Completion Checklist
- [ ] `./spec/suite/api-event-contracts.md` created
- [ ] API style chosen with naming conventions documented
- [ ] Authentication scheme defined with token format and lifecycle
- [ ] Versioning strategy specified with deprecation policy
- [ ] Request/response envelopes defined with JSON examples
- [ ] Pagination and filtering conventions documented
- [ ] Rate limiting policy defined per tier/role
