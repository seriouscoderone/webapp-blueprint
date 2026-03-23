# Phase 2 — Step Definition Implementation

This reference covers filling in the TODO bodies of step definition skeletons generated in Phase 1. This is a coding task — the agent reads spec files and writes Playwright automation code.

---

## Inputs

Read these spec files to inform implementation:

1. **Page pattern specs** (`spec/apps/{app}/pages/*.md`) — Layout patterns, UI elements, user actions, state variations
2. **State-interaction spec** (`spec/apps/{app}/state-interaction.md` or `spec/suite/state-interaction.md`) — How state flows between components, API calls, and UI updates
3. **API contracts** (`spec/apps/{app}/api-contracts.md`) — Endpoint signatures, request/response shapes, auth patterns
4. **Domain refinement** (`spec/apps/{app}/domain-refinement.md`) — Entity relationships, field names, validation rules
5. **Role refinement** (`spec/apps/{app}/role-refinement.md`) — Which roles can do what
6. **Seed data** (`spec/apps/{app}/seed-data.md` or `spec/suite/seed-data.md`) — Test data available at startup

---

## Locator Strategy

Use this hierarchy — prefer the most accessible option:

### 1. `page.getByRole()` (Preferred)

Most resilient to implementation changes. Maps to ARIA roles.

```typescript
// Buttons
page.getByRole('button', { name: 'Submit' })
page.getByRole('button', { name: /save/i })

// Links
page.getByRole('link', { name: 'Dashboard' })

// Text inputs
page.getByRole('textbox', { name: 'Email' })

// Dropdowns
page.getByRole('combobox', { name: 'Status' })

// Checkboxes
page.getByRole('checkbox', { name: 'Active' })

// Tables
page.getByRole('table', { name: 'Orders' })
page.getByRole('row').nth(0)
page.getByRole('cell', { name: 'Pending' })

// Headings
page.getByRole('heading', { name: 'Dashboard', level: 1 })

// Navigation
page.getByRole('navigation')
page.getByRole('main')
```

### 2. `page.getByText()` (Good)

For visible text content that is not associated with a clear role.

```typescript
page.getByText('No orders found')
page.getByText(/total: \$[\d.]+/i)
```

### 3. `page.getByLabel()` (Good for Forms)

For form fields associated with labels.

```typescript
page.getByLabel('Email address')
page.getByLabel('Password')
```

### 4. `page.getByPlaceholder()` (Acceptable)

When labels are not present but placeholders are.

```typescript
page.getByPlaceholder('Search orders...')
```

### 5. `page.getByTestId()` (Fallback)

Use when no semantic locator is possible. Requires `data-testid` attributes in the app.

```typescript
page.getByTestId('order-total')
page.getByTestId('notification-badge')
```

### 6. `page.locator()` (Last Resort)

CSS or XPath selectors. Avoid unless nothing else works.

```typescript
page.locator('.order-card:first-child')
page.locator('[data-status="pending"]')
```

---

## Step Implementation Patterns

### Given Steps — Precondition Setup

Given steps set up the state needed for the scenario. **Prefer API-based setup over UI navigation** — it is faster and more reliable.

#### Authentication (via API)

```typescript
Given('I am logged in as a {string}', async ({ page, request }, role: string) => {
  // Look up credentials for role from seed data or a role map
  const credentials = getRoleCredentials(role);

  // Login via API
  const response = await request.post('/api/auth/login', {
    data: { username: credentials.username, password: credentials.password },
  });
  const { token } = await response.json();

  // Inject auth into browser context
  await page.context().addCookies([{
    name: 'auth-token',
    value: token,
    domain: 'localhost',
    path: '/',
  }]);
});
```

Alternatively, if the app uses localStorage:

```typescript
Given('I am logged in as a {string}', async ({ page, request }, role: string) => {
  const credentials = getRoleCredentials(role);
  const response = await request.post('/api/auth/login', {
    data: { username: credentials.username, password: credentials.password },
  });
  const { token } = await response.json();

  await page.goto('/');
  await page.evaluate((t) => localStorage.setItem('auth-token', t), token);
});
```

#### Data Setup (via API)

```typescript
Given('there are {int} orders in the system', async ({ request }, count: number) => {
  for (let i = 0; i < count; i++) {
    await request.post('/api/orders', {
      data: { title: `Test Order ${i + 1}`, status: 'pending' },
    });
  }
});

Given('an order exists with status {string}', async ({ request }, status: string) => {
  await request.post('/api/orders', {
    data: { title: 'Test Order', status },
  });
});
```

#### Navigation

```typescript
Given('I am on the {string} page', async ({ page }, pageName: string) => {
  const routes: Record<string, string> = {
    'Dashboard': '/',
    'Orders': '/orders',
    'Settings': '/settings',
    'Users': '/admin/users',
  };
  const path = routes[pageName];
  if (!path) throw new Error(`Unknown page: ${pageName}`);
  await page.goto(path);
  await page.waitForLoadState('networkidle');
});
```

### When Steps — User Actions

When steps perform the actions being tested. These should mirror what a user actually does.

#### Click Actions

```typescript
When('I click the {string} button', async ({ page }, buttonName: string) => {
  await page.getByRole('button', { name: buttonName }).click();
});

When('I click on the order {string}', async ({ page }, orderTitle: string) => {
  await page.getByRole('link', { name: orderTitle }).click();
});
```

#### Form Interactions

```typescript
When('I fill in {string} with {string}', async ({ page }, field: string, value: string) => {
  await page.getByLabel(field).fill(value);
});

When('I select {string} from the {string} dropdown', async ({ page }, option: string, dropdown: string) => {
  await page.getByRole('combobox', { name: dropdown }).selectOption(option);
});

When('I check the {string} checkbox', async ({ page }, label: string) => {
  await page.getByRole('checkbox', { name: label }).check();
});

When('I submit the form', async ({ page }) => {
  await page.getByRole('button', { name: /submit|save|create/i }).click();
});
```

#### Search and Filter

```typescript
When('I search for {string}', async ({ page }, query: string) => {
  const searchBox = page.getByRole('searchbox').or(page.getByPlaceholder(/search/i));
  await searchBox.fill(query);
  await searchBox.press('Enter');
});

When('I filter by status {string}', async ({ page }, status: string) => {
  await page.getByRole('combobox', { name: /status/i }).selectOption(status);
});
```

#### Navigation Actions

```typescript
When('I navigate to {string}', async ({ page }, path: string) => {
  await page.goto(path);
});

When('I click the {string} link in the sidebar', async ({ page }, linkText: string) => {
  await page.getByRole('navigation').getByRole('link', { name: linkText }).click();
});

When('I go back', async ({ page }) => {
  await page.goBack();
});
```

### Then Steps — Assertions

Then steps verify outcomes. Use `expect()` from `@playwright/test`.

#### Visibility

```typescript
Then('I should see the {string} heading', async ({ page }, text: string) => {
  await expect(page.getByRole('heading', { name: text })).toBeVisible();
});

Then('I should see {string}', async ({ page }, text: string) => {
  await expect(page.getByText(text)).toBeVisible();
});

Then('I should not see {string}', async ({ page }, text: string) => {
  await expect(page.getByText(text)).not.toBeVisible();
});
```

#### Text Content

```typescript
Then('the page title should be {string}', async ({ page }, title: string) => {
  await expect(page).toHaveTitle(title);
});

Then('the {string} field should contain {string}', async ({ page }, field: string, value: string) => {
  await expect(page.getByLabel(field)).toHaveValue(value);
});
```

#### Table and List Assertions

```typescript
Then('the table should have {int} row(s)', async ({ page }, count: number) => {
  // Subtract 1 for header row if using <th> in <thead>
  await expect(page.getByRole('row')).toHaveCount(count + 1);
});

Then('the table should have at least {int} row(s)', async ({ page }, minCount: number) => {
  const rows = page.getByRole('row');
  const count = await rows.count();
  expect(count).toBeGreaterThanOrEqual(minCount + 1); // +1 for header
});

Then('the list should contain {string}', async ({ page }, itemText: string) => {
  await expect(page.getByRole('listitem').filter({ hasText: itemText })).toBeVisible();
});
```

#### Navigation Assertions

```typescript
Then('I should be on the {string} page', async ({ page }, pageName: string) => {
  const routes: Record<string, string | RegExp> = {
    'Dashboard': '/',
    'Orders': /\/orders/,
    'Order Detail': /\/orders\/\d+/,
  };
  const expected = routes[pageName];
  if (typeof expected === 'string') {
    await expect(page).toHaveURL(expected);
  } else {
    await expect(page).toHaveURL(expected);
  }
});

Then('I should be redirected to {string}', async ({ page }, path: string) => {
  await expect(page).toHaveURL(new RegExp(path));
});
```

#### Notification/Message Assertions

```typescript
Then('I should see a success message {string}', async ({ page }, message: string) => {
  await expect(page.getByRole('alert').or(page.getByText(message))).toBeVisible();
});

Then('I should see an error message {string}', async ({ page }, message: string) => {
  await expect(page.getByRole('alert').filter({ hasText: message })).toBeVisible();
});
```

#### Form Validation

```typescript
Then('the {string} field should show a validation error', async ({ page }, field: string) => {
  const input = page.getByLabel(field);
  await expect(input).toHaveAttribute('aria-invalid', 'true');
});

Then('the submit button should be disabled', async ({ page }) => {
  await expect(page.getByRole('button', { name: /submit|save|create/i })).toBeDisabled();
});
```

---

## Error Handling Patterns

### Waiting for Responses

When a step triggers an API call, wait for the response before asserting:

```typescript
When('I submit the order form', async ({ page }) => {
  const responsePromise = page.waitForResponse(resp =>
    resp.url().includes('/api/orders') && resp.request().method() === 'POST'
  );
  await page.getByRole('button', { name: 'Create Order' }).click();
  await responsePromise;
});
```

### Handling Loading States

```typescript
Then('the data should be loaded', async ({ page }) => {
  // Wait for loading indicator to disappear
  await expect(page.getByText(/loading/i)).not.toBeVisible({ timeout: 10_000 });
});
```

### Retry-safe Assertions

Playwright's `expect()` auto-retries by default (up to `expect.timeout`). Do not add manual waits unless strictly necessary.

```typescript
// GOOD — auto-retries until visible or timeout
await expect(page.getByText('Order created')).toBeVisible();

// BAD — unnecessary manual wait
await page.waitForTimeout(2000);
expect(await page.getByText('Order created').isVisible()).toBe(true);
```

---

## Page Object Integration

Step definitions should use page objects where available:

```typescript
import { OrdersPage } from '../../page-objects/portal/orders.page';

When('I search for order {string}', async ({ page }, query: string) => {
  const ordersPage = new OrdersPage(page);
  await ordersPage.searchOrders(query);
});

Then('I should see the orders table', async ({ page }) => {
  const ordersPage = new OrdersPage(page);
  await expect(ordersPage.ordersTable).toBeVisible();
});
```

---

## Completion Criteria

Phase 2 is complete when ALL of the following are true:

- [ ] No step definition file contains TODO placeholders
- [ ] All step implementations use page objects where available
- [ ] Given steps use API-based setup (not UI navigation) where possible
- [ ] All locators follow the accessibility hierarchy (role > text > testId > css)
- [ ] `npx bddgen` compiles all features without errors
- [ ] All step patterns in `.feature` files bind to implemented functions (no undefined steps)

Proceed to Phase 3 once all criteria are met.
