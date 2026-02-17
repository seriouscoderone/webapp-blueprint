# Step 13: State & Interaction Design

## Tier
3 — Per-app specification (runs for each app; defines how data flows and interactions behave)

## Purpose
State & Interaction Design documents how the app manages client-side state, synchronizes with the server, handles form interactions, and recovers from errors. It answers the "how does data flow" question at every layer: what state lives where, how it stays in sync, and what happens when things go wrong. This spec ensures consistent behavior patterns across all features.

## Prerequisites
- `./spec/apps/{app_name}/pages/*.md` — all page specs must be complete
- `./spec/apps/{app_name}/components/*.md` — component inventory must be complete
- `./spec/apps/{app_name}/features/*.feature.md` — BDD features for interaction context

## Inputs to Read
- `./spec/apps/{app_name}/pages/*.md` (all page specs)
- `./spec/apps/{app_name}/components/*.md` (all component specs)
- `./spec/apps/{app_name}/features/*.feature.md`
- `./spec/apps/{app_name}/domain-refinement.md`
- `./spec/apps/{app_name}/archetype.md`
- `./spec/suite/api-event-contracts.md` (for event-driven patterns)

## Interrogation Process

### 1. State Architecture
Establish the overall approach:

- What state management approach do you prefer? (e.g., React Query + Zustand, Redux Toolkit, Jotai, Pinia, NgRx — or do you want a recommendation based on the archetype?)
- What is the shape of global client state? (e.g., auth/session, UI preferences, active selections)
- Is there state that should persist across browser sessions (localStorage/sessionStorage)?
- Should URL state be used for filters, pagination, or view modes so they are shareable/bookmarkable?
- Is there ephemeral UI state that components manage internally (open/closed menus, hover states)?

### 2. Server State Management
Define how server data is managed on the client:

- Should the app use a server-state cache (e.g., React Query, SWR, Apollo Cache, TanStack Query)?
- What is the default cache duration for fetched data? Should it vary by entity type?
- When should cached data be automatically refetched? (On window focus, on reconnect, on interval?)
- How should cache invalidation work after mutations? (Refetch queries, optimistic update, or manual cache update?)
- Are there queries that should be prefetched (e.g., prefetch the next page of a list)?

### 3. Form State Patterns
Define how forms behave:

- When should validation run? (On blur, on change, on submit, or a combination?)
- Should forms track dirty state (warn users about unsaved changes)?
- Is autosave needed for any forms? If so, what is the debounce interval?
- How should multi-step forms preserve state across steps?
- Should form state survive page navigation (e.g., going back to a partially filled form)?
- How should server-side validation errors be displayed?

### 4. Optimistic Updates
Determine where to use optimistic UI:

- Which mutations should update the UI immediately before the server responds? (e.g., toggling a favorite, marking a notification as read, updating inline text)
- What is the rollback strategy if an optimistic update fails? (Revert UI, show error toast, retry?)
- Are there mutations that should NEVER be optimistic? (e.g., financial transactions, deletion of critical data)

### 5. Real-Time Sync
Define real-time behavior:

- Which data should update in real-time without user refresh? (e.g., notifications, chat messages, live dashboards, collaborative editing)
- What transport is preferred? (WebSocket, Server-Sent Events, polling as fallback)
- How should the UI indicate live updates? (Subtle refresh, highlight new items, toast notification?)
- What happens when the real-time connection drops? (Show banner, attempt reconnect, fall back to polling?)
- Are there collaborative scenarios where multiple users edit the same data simultaneously?

### 6. Loading Orchestration
Define data fetching strategy:

- Should page data load in parallel or in a waterfall (sequential dependencies)?
- Which data is critical (blocks render) vs. non-critical (can load progressively)?
- Should the app use suspense boundaries or manual loading state management?
- Are there data dependencies between sections of a page (e.g., load project first, then load tasks for that project)?
- What is the timeout before showing a loading indicator? (Instant spinner vs. delayed skeleton)

### 7. Error Recovery
Define error handling patterns:

- What is the default error behavior for failed API calls? (Toast, inline error, error page?)
- Should failed requests be automatically retried? How many times? With what backoff?
- Are there operations where a full-page error state is appropriate vs. a section-level error?
- How should network disconnection be handled? (Offline banner, queue operations for retry, read-only mode?)
- Is there a global error boundary that catches unhandled errors?

### 8. Undo / Redo
Determine if undo/redo is needed:

- Are there operations where the user should be able to undo? (e.g., "Undo delete" toast with timer)
- Should undo be time-limited (e.g., 10-second window) or persist until page navigation?
- Is full undo/redo history needed (e.g., for a content editor or form builder)?
- How many levels of undo should be supported?

## Output Specification

### `./spec/apps/{app_name}/state-interaction.md`

The output file must contain these sections:

#### State Architecture
- **Approach**: The chosen state management stack and rationale
- **Global State Shape**: A TypeScript-style interface or description of the top-level client state
- **URL State**: Which state is encoded in the URL and the serialization format
- **Persistent State**: What is stored in localStorage/sessionStorage and why
- **Per-Component State**: Categories of state managed internally by components

#### Server State Management
- **Library/Approach**: Which server-state solution is used
- **Cache Configuration**: Default stale time, cache time, refetch triggers
- **Invalidation Rules**: Table mapping mutations to the queries they invalidate
| Mutation | Invalidates | Strategy |
|---|---|---|
| createProject | projectList | Refetch |
| updateTask | taskDetail, taskList | Optimistic + refetch |
| deleteComment | commentList | Remove from cache |
- **Prefetching**: Which queries are prefetched and when

#### Form State Patterns
- **Validation Timing**: When validation runs for each form type
- **Dirty Tracking**: How unsaved changes are detected and communicated to the user
- **Autosave**: Which forms autosave, debounce interval, indicator behavior
- **Multi-Step Forms**: State persistence strategy, step validation, back/forward behavior
- **Server Validation**: How server-side errors are mapped to form fields

#### Optimistic Updates
- **Optimistic Operations**: List of operations that use optimistic UI
- **Rollback Behavior**: What happens on failure for each optimistic operation
- **Non-Optimistic Operations**: Operations that must wait for server confirmation and why

#### Real-Time Sync
- **Real-Time Data**: Which entities/events are synced in real-time
- **Transport**: WebSocket, SSE, or polling — and the fallback chain
- **UI Treatment**: How real-time updates manifest in the UI
- **Reconnection**: Strategy for connection drops (backoff, max retries, fallback)
- **Conflict Resolution**: How simultaneous edits are handled (if applicable)

#### Loading Orchestration
- **Page Load Strategy**: For each major page, which data loads in parallel vs. sequentially
- **Critical vs. Deferred**: Which data blocks render vs. loads progressively
- **Loading UI**: Skeleton, spinner, or progressive disclosure — per context
- **Timeout Behavior**: When to show loading indicators, when to show error states

#### Error Recovery Patterns
- **Default Error Handling**: The standard behavior for failed requests
- **Retry Policy**: Automatic retry count, backoff strategy, which errors trigger retry
- **Error Hierarchy**: Toast vs. inline vs. section-level vs. page-level errors
- **Offline Behavior**: How the app behaves when the network is unavailable
- **Global Error Boundary**: What the fallback UI shows for unhandled errors

#### Undo / Redo
- **Supported Operations**: Which actions can be undone
- **Mechanism**: Time-limited toast, persistent history, or keyboard shortcut
- **Scope**: How many levels, what triggers history to be cleared

## Completion Checklist
- [ ] `./spec/apps/{app_name}/state-interaction.md` created
- [ ] State management approach is chosen and justified
- [ ] Server state caching and invalidation rules are defined
- [ ] Form state patterns cover validation, dirty tracking, and autosave
- [ ] Optimistic update operations are identified with rollback strategies
- [ ] Real-time sync requirements are specified with transport and fallback
- [ ] Loading orchestration is defined for all major pages
- [ ] Error recovery patterns cover retry, offline, and error boundary scenarios
