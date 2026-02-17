# Step 5: Suite-Level API & Event Contracts

## Tier
1 — Suite-level (runs once, establishes shared API conventions and event infrastructure for the entire suite)

## Purpose
This step defines the suite-wide API style, authentication scheme, error handling conventions, and event bus architecture. It creates the contract that all app-level API definitions (Step 14) must follow. Establishing these conventions early prevents inconsistency across apps and ensures interoperability within the suite.

## Prerequisites
- `./spec/suite/domain-model.md` (Step 1 — needed to understand entities, events, and cross-domain interactions)
- `./spec/suite/role-permission-matrix.md` (Step 2 — needed to understand authentication and authorization requirements)

## Inputs to Read
- `./spec/suite/domain-model.md` — review Entity Glossary and Domain Event Catalog to understand what resources and events the API must support
- `./spec/suite/role-permission-matrix.md` — review Authentication Requirements and Role Hierarchy to inform auth scheme design

## Interrogation Process

### 1. API Style & Philosophy
Determine the foundational API approach:

- What API style will the suite use?
  - **REST**: Resource-oriented, HTTP verbs, widely understood
  - **GraphQL**: Flexible queries, single endpoint, client-driven data fetching
  - **gRPC**: High-performance, strongly typed, binary protocol
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
- Is there service-to-service authentication? (e.g., mutual TLS, shared secrets, service tokens)

### 3. Versioning Strategy
Plan for API evolution:

- What versioning approach?
  - **URL path**: `/api/v1/resource` (most explicit)
  - **Header-based**: `Accept: application/vnd.api+json; version=1`
  - **Query parameter**: `/api/resource?version=1`
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

### 6. Event Bus & Async Communication
Define event-driven architecture:

- Does the suite need an event bus for cross-app communication?
- What event transport? (e.g., message queue like RabbitMQ/SQS, streaming like Kafka, webhooks, server-sent events)
- What is the event naming convention? (e.g., `domain.entity.action` like `orders.order.placed`)
- What is the event envelope format?
  ```json
  { "eventId": "...", "eventType": "...", "timestamp": "...", "source": "...", "data": {...} }
  ```
- What delivery guarantees are needed? (at-most-once, at-least-once, exactly-once)
- Is event ordering important? Within an entity? Globally?
- Is there a schema registry for event validation?
- Are there dead-letter queue / retry policies for failed event processing?

### 7. Cross-App Communication
Define how apps within the suite interact:

- Do apps call each other's APIs directly, or only through events?
- Is there an API gateway? What does it handle? (routing, auth, rate limiting, transformation)
- Is there a service mesh or service discovery mechanism?
- How are cross-app transactions handled? (saga pattern, two-phase commit, eventual consistency)
- Are there shared data stores, or does each app own its data exclusively?

### 8. Operational Conventions
Define health and observability standards:

- What health check convention? (e.g., `GET /health` returning `{ "status": "healthy", "checks": {...} }`)
- What status endpoint convention? (e.g., `GET /status` with version, uptime, dependency health)
- What request tracing convention? (e.g., `X-Request-Id` header, correlation IDs across services)
- What logging format? (structured JSON, log levels)
- Are there SLA/SLO requirements for API response times?

## Output Specification

### `./spec/suite/api-event-contracts.md`

The output file must contain these sections:

#### API Style & Conventions
- **Style**: REST / GraphQL / gRPC / Hybrid
- **Base URL Pattern**: template (e.g., `https://api.{domain}/v{version}/{resource}`)
- **Naming Conventions**: URL casing, pluralization rules, verb usage
- **Documentation**: OpenAPI spec requirement, tooling

#### Authentication & Authorization Scheme
- **Mechanism**: chosen auth approach with rationale
- **Token Format**: structure, claims, lifetime
- **Refresh Strategy**: how tokens are renewed
- **Permission Model**: how permissions are checked per request
- **Service-to-Service Auth**: mechanism for internal communication

#### Versioning Strategy
- **Approach**: chosen versioning method
- **Deprecation Policy**: timeline, notification process
- **Compatibility Rules**: what constitutes a breaking change

#### Rate Limiting Policy
A markdown table with columns:
| Tier/Role | Requests/Minute | Requests/Day | Burst Limit | Retry Policy |
- **Headers**: which rate limit headers are included in responses
- **Exceeded Behavior**: response code, body, retry guidance

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

#### Shared Event Bus
- **Transport**: chosen technology
- **Event Naming Convention**: pattern with examples
- **Event Envelope**: JSON structure with required fields
- **Delivery Guarantees**: chosen guarantee level
- **Schema Registry**: approach to event schema validation
- **Dead Letter Policy**: handling of failed events
- **Retry Strategy**: backoff and max retry configuration

#### Cross-App Communication Patterns
- **Synchronous**: how apps call each other (direct, via gateway)
- **Asynchronous**: how apps communicate via events
- **Data Ownership**: which app owns which entities
- **Transaction Strategy**: how cross-app operations maintain consistency

#### Health Check & Status Conventions
- **Health Endpoint**: path, response format, status codes
- **Status Endpoint**: path, response format (version, uptime, dependencies)
- **Tracing**: request ID header, correlation ID propagation
- **Logging**: format, required fields, log levels

## Completion Checklist
- [ ] `./spec/suite/api-event-contracts.md` created
- [ ] API style chosen with naming conventions documented
- [ ] Authentication scheme defined with token format and lifecycle
- [ ] Versioning strategy specified with deprecation policy
- [ ] Request/response envelopes defined with JSON examples
- [ ] Rate limiting policy defined per tier/role
- [ ] Event bus architecture defined with naming convention and delivery guarantees
- [ ] Health check and status endpoint conventions documented
