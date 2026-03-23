# Phase 1 — Test Harness Generation

This reference covers the complete scaffolding of the test infrastructure from spec artifacts. Everything in this phase is generated — no manual coding required.

---

## 1. Feature Conversion (.feature.md to .feature)

The spec pipeline produces features in `.feature.md` format (Gherkin wrapped in markdown). The test harness needs pure `.feature` files.

### Conversion Rules

1. **Strip the YAML front-matter** — Remove everything between the opening and closing `---` markers (inclusive)
2. **Strip markdown headings** — Remove any lines starting with `#`
3. **Extract the Gherkin block** — If the Gherkin is inside a fenced code block (` ```gherkin ... ``` `), extract only the content between the fences
4. **Preserve Gherkin structure** — Keep `Feature:`, `Background:`, `Scenario:`, `Scenario Outline:`, `Examples:`, `Given`, `When`, `Then`, `And`, `But` lines exactly as-is
5. **Preserve tags** — Keep any `@tag` lines above Feature or Scenario declarations
6. **Preserve data tables** — Keep `| column | column |` table rows with their indentation
7. **Preserve doc strings** — Keep `"""` delimited blocks
8. **Trim trailing whitespace** — Remove trailing spaces from each line
9. **Single trailing newline** — Ensure the file ends with exactly one newline

### Source and Destination

- **Source:** `spec/apps/{app}/features/{feature_name}.feature.md`
- **Destination:** `tests/features/{app}/{feature_name}.feature`

### Example

Source (`spec/apps/portal/features/order-management.feature.md`):
```markdown
---
app: portal
feature: Order Management
---

# Order Management

```gherkin
Feature: Order Management
  As a store manager
  I want to view and manage orders
  So that I can fulfill customer requests

  Background:
    Given I am logged in as a "store_manager"
    And I am on the "Orders" page

  Scenario: View order list
    Then I should see the orders table
    And the table should have at least 1 row
```
```

Destination (`tests/features/portal/order-management.feature`):
```gherkin
Feature: Order Management
  As a store manager
  I want to view and manage orders
  So that I can fulfill customer requests

  Background:
    Given I am logged in as a "store_manager"
    And I am on the "Orders" page

  Scenario: View order list
    Then I should see the orders table
    And the table should have at least 1 row
```

---

## 2. Playwright Configuration

Generate `playwright.config.ts` at the project root (or in the `tests/` directory depending on project layout).

### Template

```typescript
import { defineConfig, devices } from '@playwright/test';
import { defineBddConfig } from 'playwright-bdd';

const testDir = defineBddConfig({
  features: 'tests/features/**/*.feature',
  steps: 'tests/steps/**/*.ts',
});

export default defineConfig({
  testDir,
  timeout: 30_000,
  expect: { timeout: 5_000 },
  fullyParallel: false,
  retries: 0,
  workers: 1,
  reporter: [
    ['json', { outputFile: 'test-results/results.json' }],
    ['html', { open: 'never' }],
    ['list'],
  ],
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
});
```

### Key Settings

- **`fullyParallel: false`** — Tests run sequentially for determinism
- **`retries: 0`** — No retries; failures are real
- **`workers: 1`** — Single worker for determinism
- **`trace: 'retain-on-failure'`** — Traces saved only for failures (useful for debugging)
- **JSON reporter** — Machine-readable output for `parse-playwright-results.py`

---

## 3. Base Fixtures

Generate `tests/fixtures/base.fixture.ts`. This extends Playwright's `test` object with common fixtures shared across all step definitions.

### Template

```typescript
import { test as base } from 'playwright-bdd';

export type TestFixtures = {
  authenticatedPage: import('@playwright/test').Page;
};

export const test = base.extend<TestFixtures>({
  authenticatedPage: async ({ page }, use) => {
    // Override in app-specific fixtures or auth.steps.ts
    await use(page);
  },
});
```

Extend this fixture file based on what the spec requires. Common additions:
- **`apiContext`** — Pre-configured API request context for Given steps
- **`testData`** — Seed data references loaded from `spec/suite/seed-data.md` or seed scripts
- **`storageState`** — Authenticated browser state for bypassing login UI

---

## 4. Step Definition Skeletons

Generate one step definition file per feature, plus shared step files for cross-cutting concerns.

### Skeleton Format

```typescript
import { createBdd } from 'playwright-bdd';
import { test } from '../fixtures/base.fixture';
import { expect } from '@playwright/test';

const { Given, When, Then } = createBdd(test);

// --- Background steps (if not in common/) ---

Given('I am logged in as a {string}', async ({ page }, role: string) => {
  // TODO: Implement login for role
});

// --- Scenario: View order list ---

Then('I should see the orders table', async ({ page }) => {
  // TODO: Assert orders table is visible
});

Then('the table should have at least {int} row(s)', async ({ page }, count: number) => {
  // TODO: Assert row count
});
```

### Skeleton Rules

1. **Import `createBdd` from `playwright-bdd`** — Always destructure `Given`, `When`, `Then` from `createBdd(test)`
2. **Import `test` from the base fixture** — Not from `@playwright/test` directly
3. **Import `expect` from `@playwright/test`** — For assertions
4. **One file per feature** — `tests/steps/{app}/{feature}.steps.ts`
5. **Common steps in `tests/steps/common/`** — `auth.steps.ts`, `navigation.steps.ts`
6. **TODO placeholder in every body** — Phase 2 fills these in
7. **Parameter types match Gherkin** — `{string}` maps to `string`, `{int}` maps to `number`, `{float}` maps to `number`
8. **Dedup step patterns** — If the same step text appears in multiple scenarios, define it once

### Common Step Files

**`tests/steps/common/auth.steps.ts`** — Login/logout/role steps shared across all features:
```typescript
import { createBdd } from 'playwright-bdd';
import { test } from '../../fixtures/base.fixture';

const { Given } = createBdd(test);

Given('I am logged in as a {string}', async ({ page }, role: string) => {
  // TODO: Login via API, set auth cookies/tokens
});

Given('I am not logged in', async ({ page }) => {
  // TODO: Clear auth state
});
```

**`tests/steps/common/navigation.steps.ts`** — Page navigation steps:
```typescript
import { createBdd } from 'playwright-bdd';
import { test } from '../../fixtures/base.fixture';

const { Given, When } = createBdd(test);

Given('I am on the {string} page', async ({ page }, pageName: string) => {
  // TODO: Navigate to page by name using route map
});

When('I navigate to {string}', async ({ page }, path: string) => {
  // TODO: Navigate to path
});
```

---

## 5. Page Objects

Generate page object classes from the page pattern specs (`spec/apps/{app}/pages/*.md`).

### Derivation Rules

Read each page spec and extract:

1. **Layout pattern** → Base class structure (e.g., `ListDetailPage`, `FormPage`, `DashboardPage`)
2. **Key UI elements** → Locator properties on the page object
3. **User actions** → Methods that perform interactions (click, fill, select)
4. **State variations** → Methods or getters for different page states (empty, loading, error, populated)

### Template

```typescript
import { type Page, type Locator } from '@playwright/test';

export class OrdersPage {
  readonly page: Page;

  // --- Locators (derived from page spec UI elements) ---
  readonly ordersTable: Locator;
  readonly searchInput: Locator;
  readonly createOrderButton: Locator;
  readonly statusFilter: Locator;

  constructor(page: Page) {
    this.page = page;
    // Prefer accessible locators
    this.ordersTable = page.getByRole('table', { name: /orders/i });
    this.searchInput = page.getByRole('searchbox', { name: /search orders/i });
    this.createOrderButton = page.getByRole('button', { name: /create order/i });
    this.statusFilter = page.getByRole('combobox', { name: /status/i });
  }

  // --- Actions (derived from page spec user actions) ---

  async searchOrders(query: string): Promise<void> {
    await this.searchInput.fill(query);
    await this.searchInput.press('Enter');
  }

  async filterByStatus(status: string): Promise<void> {
    await this.statusFilter.selectOption(status);
  }

  async clickCreateOrder(): Promise<void> {
    await this.createOrderButton.click();
  }

  // --- State queries (derived from page spec state variations) ---

  async getRowCount(): Promise<number> {
    return this.ordersTable.getByRole('row').count();
  }

  async isEmptyState(): Promise<boolean> {
    return this.page.getByText(/no orders found/i).isVisible();
  }
}
```

### Naming Convention

- **File:** `tests/page-objects/{app}/{page-name}.page.ts`
- **Class:** `{PageName}Page` (PascalCase)
- **Locators:** camelCase properties, initialized in constructor
- **Actions:** async methods returning `Promise<void>`

---

## 6. API Helpers

Generate API helper modules from `spec/apps/{app}/api-contracts.md`.

### Purpose

API helpers are used in **Given** steps to set up test preconditions without going through the UI. This is faster and more reliable than UI-based setup.

### Template

```typescript
import { type APIRequestContext } from '@playwright/test';

export class PortalApi {
  private readonly request: APIRequestContext;
  private readonly baseURL: string;

  constructor(request: APIRequestContext, baseURL: string) {
    this.request = request;
    this.baseURL = baseURL;
  }

  // --- Auth ---

  async login(username: string, password: string): Promise<string> {
    const response = await this.request.post(`${this.baseURL}/api/auth/login`, {
      data: { username, password },
    });
    const body = await response.json();
    return body.token;
  }

  // --- CRUD operations (derived from api-contracts.md) ---

  async createOrder(data: Record<string, unknown>): Promise<Record<string, unknown>> {
    const response = await this.request.post(`${this.baseURL}/api/orders`, {
      data,
    });
    return response.json();
  }

  async getOrders(params?: Record<string, string>): Promise<Record<string, unknown>> {
    const query = params ? '?' + new URLSearchParams(params).toString() : '';
    const response = await this.request.get(`${this.baseURL}/api/orders${query}`);
    return response.json();
  }

  async deleteOrder(id: string): Promise<void> {
    await this.request.delete(`${this.baseURL}/api/orders/${id}`);
  }
}
```

### Derivation Rules

1. Read each endpoint in `api-contracts.md`
2. Create a method for each endpoint: `{verb}{Resource}` (e.g., `createOrder`, `getOrders`, `updateOrder`, `deleteOrder`)
3. Include request body types based on the contract's request schema
4. Include auth header injection based on the auth pattern from the spec

### File Convention

- **File:** `tests/api-helpers/{app}.api.ts`
- **Class:** `{AppName}Api` (PascalCase)

---

## Package Dependencies

Ensure these are installed before proceeding:

```bash
npm install -D @playwright/test playwright-bdd
npx playwright install chromium
```

If the project does not yet have a `package.json`, create one:

```bash
npm init -y
npm install -D @playwright/test playwright-bdd
npx playwright install chromium
```

---

## Completion Criteria

Phase 1 is complete when ALL of the following are true:

- [ ] All `.feature.md` files converted to `.feature` in `tests/features/{app}/`
- [ ] `playwright.config.ts` exists with `defineBddConfig()` integration
- [ ] `tests/fixtures/base.fixture.ts` exists
- [ ] Step definition skeletons exist for every feature (with TODO bodies)
- [ ] Common step files exist (`auth.steps.ts`, `navigation.steps.ts`)
- [ ] Page objects exist for all pages referenced in features
- [ ] API helpers exist for all apps with API contracts
- [ ] `npm install` succeeds
- [ ] `npx bddgen` compiles without import/syntax errors (steps may be unimplemented)

Proceed to Phase 2 once all criteria are met.
