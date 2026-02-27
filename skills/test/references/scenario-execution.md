# Scenario Execution Reference

## Overview

Each BDD scenario is a `### Scenario:` or `### Scenario Outline:` block in a `.feature.md` file. Translate each Given/When/Then step into browser actions, then assert the Then conditions.

---

## Reading a Scenario

Scenario format in `.feature.md`:
```markdown
### Scenario: User can view order history

**Given** the user is logged in as a customer
**When** they navigate to `/orders`
**Then** they see a list of their past orders
**And** each order shows order number, date, and status
```

---

## Step Translation

| BDD Keyword | Browser Action |
|-------------|---------------|
| `Given ... is logged in as {role}` | Navigate to login page, authenticate as a seed user with that role |
| `Given ... navigates to {path}` | `navigate(base_url + path)` |
| `When ... clicks {element}` | `find(element description)`, `left_click(ref)` |
| `When ... fills in {field} with {value}` | `find(field)`, `form_input(ref, value)` |
| `When ... submits the form` | Find and click the submit button |
| `Then ... sees {text}` | `find(text on page)` — assert element exists |
| `Then ... is redirected to {path}` | Assert current URL contains path |
| `Then ... {element} is not visible` | Assert element not present in accessible tree |

For steps not covered by this table, interpret the Given/When/Then semantically and translate to the most natural browser action.

---

## Authentication

Seed user credentials come from `spec/apps/{app}/seed-data.md`. For each role (e.g., `customer`, `admin`, `viewer`), the seed data spec defines test credentials. Use these exactly.

Before executing any scenario that requires authentication, navigate to the login page and sign in as the appropriate user. Do not reuse authentication state across scenarios — start fresh for each.

---

## Assertions

For `Then` steps:
- Use `find()` or `read_page()` to check for expected content
- If the expected content is not found: `FAILED`
- If the expected content is found: continue to next step
- If all Then steps pass: `PASSED`

Be lenient on exact text matching — prefer semantic matching (e.g., "an error message about invalid email" matches any visible text indicating an email validation error).

---

## Recording Results

### PASSED scenario
```json
{
  "_type": "scenario",
  "status": "PASSED",
  "message": "All steps completed successfully",
  "error_detail": null,
  "steps_to_reproduce": [],
  "last_run": "2026-01-01T12:00:00Z",
  "build_id": "12345678"
}
```

### FAILED scenario
```json
{
  "_type": "scenario",
  "status": "FAILED",
  "message": "Then step failed: expected order list, got empty state",
  "error_detail": "Expected element 'order list' to be present. Page content: [empty state message: 'No orders yet']. Console errors: none.",
  "steps_to_reproduce": [
    "Navigate to https://portal.example.com/login",
    "Enter email: customer@example.com, password: test1234",
    "Click 'Sign In'",
    "Navigate to https://portal.example.com/orders",
    "Expected: list of orders. Actual: empty state shown."
  ],
  "last_run": "2026-01-01T12:01:30Z",
  "build_id": "12345678"
}
```

Always fill in `steps_to_reproduce` for FAILED scenarios — this is what the build agent reads to reproduce and fix the failure.

---

## Scenario Outlines

A `### Scenario Outline:` block has an `Examples:` table with multiple parameter rows. Run each row as a separate execution. If **any** row fails, mark the overall entry as `FAILED` and combine error details:

```json
{
  "_type": "scenario_outline",
  "status": "FAILED",
  "message": "2 of 3 example rows failed",
  "error_detail": "Row 2 (role=viewer): Cannot access /admin — got 403. Row 3 (role=guest): Redirected to login instead of /dashboard.",
  "steps_to_reproduce": [
    "Row 2: Navigate as viewer to /admin — expected access denied message, got 403 page",
    "Row 3: Navigate as guest to /dashboard — expected dashboard, got login redirect"
  ],
  "last_run": "2026-01-01T12:05:00Z",
  "build_id": "12345678"
}
```

If all rows pass, mark as `PASSED`.

---

## Error Capture Guidelines

**error_detail** should include:
- The specific assertion that failed and the actual vs. expected values
- Any browser console errors observed during the scenario
- HTTP errors (404, 500, etc.) if relevant
- The exact page URL at the time of failure

**steps_to_reproduce** should be:
- Numbered or bulleted ordered list
- Each step is a single concrete browser action
- Include the full URL at the start
- End with "Expected: X. Actual: Y."

Keep `error_detail` focused on the failure, not a full browser log dump. The build agent needs to understand what went wrong, not debug the entire page.
