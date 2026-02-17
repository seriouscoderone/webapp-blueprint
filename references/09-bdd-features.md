# Step 9: BDD Feature Specifications

## Tier
3 — Per-app specification (runs for each app; produces detailed feature-level artifacts)

## Purpose
BDD Feature Specifications translate the app's archetype, domain refinement, and role refinement into concrete, testable behavior definitions using Given/When/Then syntax. Each feature file captures user stories, acceptance criteria, edge cases, and error scenarios in a structured format that serves as both a living specification and a foundation for automated testing.

## Prerequisites
- `./spec/apps/{app_name}/archetype.md` — the app archetype must be defined
- `./spec/apps/{app_name}/domain-refinement.md` — app-level domain model must exist
- `./spec/apps/{app_name}/role-refinement.md` — app-level roles and permissions must exist

## Inputs to Read
- `./spec/apps/{app_name}/archetype.md`
- `./spec/apps/{app_name}/domain-refinement.md`
- `./spec/apps/{app_name}/role-refinement.md`
- `./spec/suite/domain-model.md` (for reference to suite-wide entities and events)

## Interrogation Process

### 1. Feature Inventory
Establish which features this app provides:

- Based on the archetype and domain refinement, what are the primary features of this app?
- Which features map directly to the core workflows identified in the domain model?
- Are there features that span multiple entities or aggregates?
- Which features are must-have for an MVP vs. planned for later phases?
- Are there features that are unique to specific roles?

Present the proposed feature list to the user for confirmation before proceeding. Each feature should have a short name (used as the filename) and a one-sentence description.

### 2. Per-Feature Deep Dive
For each feature, ask:

#### User Stories
- Who is the primary actor for this feature? Are there secondary actors?
- What is the user trying to accomplish? What is the business value?
- Are there different user stories for different roles interacting with the same feature?

#### Acceptance Criteria
- What constitutes a successful outcome for the happy path?
- What data must be present before the feature can be used?
- What are the expected outputs or side effects (e.g., notifications, state changes, audit logs)?

#### Scenarios & Variations
- What are the 3-5 most important happy-path scenarios?
- What happens when the user provides invalid input? List each validation case.
- What happens when the user lacks permission?
- What happens when a dependent system is unavailable (network error, service down)?
- Are there concurrency scenarios (two users editing the same thing)?
- Are there boundary/limit scenarios (max items, character limits, file size limits)?

#### Edge Cases & Error Scenarios
- What should happen if the user navigates away mid-operation?
- What if the user's session expires during this feature?
- Are there race conditions to consider (e.g., item deleted by another user while viewing)?
- What data states are impossible or should be guarded against?

### 3. Cross-Feature Dependencies
After all features are specified:

- Do any features depend on another feature being completed first?
- Do features share scenarios (e.g., both "create order" and "edit order" share validation)?
- Are there features that produce domain events consumed by other features?

## Feature File Format

Each `.feature.md` file uses the following BDD structure:

```markdown
# Feature: {feature_name}

## User Story
As a {role}
I want to {action}
So that {benefit}

## Background
> Preconditions that apply to ALL scenarios in this feature.

Given {common_precondition}
And {another_common_precondition}

## Scenarios

### Scenario: {descriptive_scenario_name}
> Brief description of what this scenario tests.

Given {precondition}
  And {additional_precondition}
When {action_taken_by_user}
  And {additional_action}
Then {expected_outcome}
  And {additional_expected_outcome}

### Scenario Outline: {parameterized_scenario_name}
> Use Scenario Outline when testing the same flow with different data.

Given {precondition_with_<parameter>}
When {action_with_<parameter>}
Then {outcome_with_<parameter>}

Examples:
  | parameter | expected_result |
  | value_1   | result_1        |
  | value_2   | result_2        |
```

## Common Scenario Patterns

Include relevant patterns from this catalog when writing feature files:

### CRUD Pattern
```
Scenario: Create a new {entity}
  Given I am logged in as a {role}
    And I am on the {entity} list page
  When I click "Create New {Entity}"
    And I fill in the required fields
    And I submit the form
  Then a new {entity} is created
    And I see a success confirmation
    And the {entity} appears in the list

Scenario: View {entity} details
  Given a {entity} exists with ID {id}
    And I have permission to view it
  When I navigate to the {entity} detail page
  Then I see all {entity} fields displayed

Scenario: Update an existing {entity}
  Given I am viewing {entity} with ID {id}
    And I have edit permission
  When I modify the {field} field
    And I save changes
  Then the {entity} is updated
    And I see a success confirmation

Scenario: Delete a {entity}
  Given I am viewing {entity} with ID {id}
    And I have delete permission
  When I click "Delete"
    And I confirm the deletion
  Then the {entity} is removed
    And I am redirected to the list page
```

### Search & Filter Pattern
```
Scenario: Search {entities} by keyword
  Given I am on the {entity} list page
    And multiple {entities} exist
  When I enter "{search_term}" in the search field
  Then the list shows only {entities} matching "{search_term}"
    And the result count is updated

Scenario: Filter {entities} by {attribute}
  Given I am on the {entity} list page
  When I select "{value}" from the {attribute} filter
  Then only {entities} with {attribute} = "{value}" are displayed

Scenario: Clear all filters
  Given I have active filters applied
  When I click "Clear Filters"
  Then all {entities} are displayed
    And all filter controls are reset
```

### Form Submission Pattern
```
Scenario: Submit form with valid data
  Given I am on the {form_name} form
  When I fill in all required fields with valid data
    And I click "Submit"
  Then the form is submitted successfully
    And I see a confirmation message

Scenario: Submit form with missing required fields
  Given I am on the {form_name} form
  When I leave the {required_field} empty
    And I click "Submit"
  Then the form is not submitted
    And I see a validation error on {required_field}

Scenario: Submit form with invalid data
  Given I am on the {form_name} form
  When I enter "{invalid_value}" in the {field} field
    And I click "Submit"
  Then the form is not submitted
    And I see the error "{error_message}"
```

### Approval Workflow Pattern
```
Scenario: Submit {entity} for approval
  Given I am the owner of {entity}
    And the {entity} status is "Draft"
  When I click "Submit for Approval"
  Then the {entity} status changes to "Pending Approval"
    And the assigned approver is notified

Scenario: Approve a {entity}
  Given I am an approver
    And a {entity} is pending my approval
  When I review the {entity}
    And I click "Approve"
  Then the {entity} status changes to "Approved"
    And the submitter is notified

Scenario: Reject a {entity} with reason
  Given I am an approver
    And a {entity} is pending my approval
  When I click "Reject"
    And I enter a rejection reason
  Then the {entity} status changes to "Rejected"
    And the submitter is notified with the reason
```

## Output Specification

### `./spec/apps/{app_name}/features/{feature_name}.feature.md`

One file per feature. Each file must contain:

#### Feature Header
- Feature name and one-line description
- User story in As a / I want / So that format
- If multiple roles use this feature, include a user story for each

#### Background
- Preconditions common to all scenarios (e.g., "Given I am logged in")

#### Happy Path Scenarios
- At least 2-3 scenarios covering the primary success flows

#### Validation & Error Scenarios
- At least 2 scenarios covering input validation failures
- At least 1 scenario for permission denied
- At least 1 scenario for system/network error handling

#### Edge Case Scenarios
- Boundary conditions (empty lists, max values, concurrent edits)
- State transition edge cases

#### Scenario Outlines (where applicable)
- Parameterized scenarios for repetitive validation patterns

## Completion Checklist
- [ ] Feature inventory confirmed with user
- [ ] One `.feature.md` file created per feature in `./spec/apps/{app_name}/features/`
- [ ] Every feature file contains at least one user story
- [ ] Every feature file has happy-path and error scenarios
- [ ] Given/When/Then syntax is consistently applied
- [ ] Cross-feature dependencies are noted in feature headers where relevant
- [ ] Edge cases and boundary conditions are covered
- [ ] All roles from `role-refinement.md` are represented across the feature set
